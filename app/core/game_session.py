from typing import Dict, List, Any, Optional
import json
import uuid
from datetime import datetime
from database.connection import DatabaseConnection
from app.managers.cell_manager import CellManager
from app.core.game_manager import GameManager

class GameSession:
    """게임 세션을 관리하는 클래스"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.db = DatabaseConnection()
        # CellManager와 GameManager는 필요할 때만 초기화 (의존성 주입 복잡도 때문에)
        self._cell_manager: Optional[CellManager] = None
        self._game_manager: Optional[GameManager] = None
        
        # 세션 정보 캐시
        self._session_info: Optional[Dict[str, Any]] = None
        self._player_entities: Optional[List[Dict[str, Any]]] = None
    
    @property
    def cell_manager(self) -> CellManager:
        """CellManager 지연 초기화"""
        if self._cell_manager is None:
            from database.repositories.game_data import GameDataRepository
            from database.repositories.runtime_data import RuntimeDataRepository
            from database.repositories.reference_layer import ReferenceLayerRepository
            from app.managers.entity_manager import EntityManager
            
            game_data_repo = GameDataRepository(self.db)
            runtime_data_repo = RuntimeDataRepository(self.db)
            reference_layer_repo = ReferenceLayerRepository(self.db)
            entity_manager = EntityManager(self.db, game_data_repo, runtime_data_repo, reference_layer_repo)
            
            self._cell_manager = CellManager(
                db_connection=self.db,
                game_data_repo=game_data_repo,
                runtime_data_repo=runtime_data_repo,
                reference_layer_repo=reference_layer_repo,
                entity_manager=entity_manager
            )
        return self._cell_manager

    async def initialize_session(self) -> None:
        """새로운 게임 세션을 초기화합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE runtime_data.active_sessions
                SET session_state = 'active',
                    last_active_at = CURRENT_TIMESTAMP,
                    metadata = jsonb_set(
                        COALESCE(metadata, '{}'::jsonb),
                        '{initialized_at}',
                        $1::jsonb
                    )
                WHERE session_id = $2
                """,
                json.dumps(datetime.now().isoformat()),
                self.session_id
            )

    async def enter_cell(self, runtime_cell_id: str) -> Dict[str, Any]:
        """플레이어가 새로운 셀에 진입할 때 호출됩니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                # 1. 셀의 모든 컨텐츠 로드
                cell_contents = await self.cell_manager.get_cell_contents(runtime_cell_id)
                
                # 2. 셀 진입 이벤트 기록
                event_id = str(uuid.uuid4())
                event_data = {
                    'cell_id': runtime_cell_id,
                    'timestamp': datetime.now().isoformat(),
                    'discovered_entities': [e['runtime_entity_id'] for e in cell_contents['entities']],
                    'discovered_objects': [o['runtime_object_id'] for o in cell_contents['objects']]
                }
                
                await conn.execute(
                    """
                    INSERT INTO runtime_data.triggered_events
                    (event_id, session_id, event_type, event_data)
                    VALUES ($1, $2, 'CELL_ENTER', $3)
                    """,
                    event_id, self.session_id, json.dumps(event_data)
                )
        
        return cell_contents

    async def move_player(self, player_id: str, target_cell_id: str, new_position: Dict[str, float]) -> bool:
        """플레이어를 이동시킵니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            try:
                await conn.execute(
                    """
                    UPDATE runtime_data.entity_states
                    SET runtime_cell_id = $1,
                        current_position = $2,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE runtime_entity_id = $3
                    """,
                    target_cell_id,
                    json.dumps(new_position),
                    player_id
                )
                
                # 캐시 무효화
                self._player_entities = None
                return True
            except Exception as e:
                print(f"플레이어 이동 오류: {e}")
                return False

    async def start_npc_dialogue(self, player_id: str, npc_id: str) -> Optional[str]:
        """NPC와의 대화를 시작합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            try:
                # NPC의 대화 컨텍스트 조회
                npc_info = await conn.fetchrow(
                    """
                    SELECT er.runtime_entity_id, e.dialogue_context_id
                    FROM reference_layer.entity_references er
                    JOIN game_data.entities e ON er.game_entity_id = e.entity_id
                    WHERE er.runtime_entity_id = $1 AND er.session_id = $2
                    """,
                    npc_id, self.session_id
                )
                
                if not npc_info or not npc_info['dialogue_context_id']:
                    return None
                
                # 대화 상태 초기화
                dialogue_state_id = str(uuid.uuid4())
                await conn.execute(
                    """
                    INSERT INTO runtime_data.dialogue_states
                    (state_id, session_id, runtime_entity_id, current_context_id, conversation_state, active_topics)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (session_id, runtime_entity_id) 
                    DO UPDATE SET
                        current_context_id = $4,
                        conversation_state = $5,
                        active_topics = $6,
                        last_updated = CURRENT_TIMESTAMP
                    """,
                    dialogue_state_id,
                    self.session_id,
                    npc_id,
                    npc_info['dialogue_context_id'],
                    json.dumps({"current_topic": "greeting", "emotion": "neutral"}),
                    json.dumps({"current_topics": ["greeting"], "available_topics": ["shop_items", "local_news"]})
                )
                
                return npc_info['dialogue_context_id']
                
            except Exception as e:
                print(f"대화 시작 오류: {e}")
                return None

    async def handle_dialogue_input(self, player_input: str, npc_id: str) -> str:
        """대화 입력을 처리합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            try:
                # 현재 대화 상태 조회
                dialogue_state = await conn.fetchrow(
                    """
                    SELECT current_context_id, conversation_state, active_topics
                    FROM runtime_data.dialogue_states
                    WHERE session_id = $1 AND runtime_entity_id = $2
                    """,
                    self.session_id, npc_id
                )
                
                if not dialogue_state:
                    return "대화를 시작할 수 없습니다."
                
                # 대화 컨텍스트 조회
                context = await conn.fetchrow(
                    """
                    SELECT title, content, available_topics
                    FROM game_data.dialogue_contexts
                    WHERE dialogue_id = $1
                    """,
                    dialogue_state['current_context_id']
                )
                
                if not context:
                    return "대화 컨텍스트를 찾을 수 없습니다."
                
                # 대화 히스토리 기록
                await conn.execute(
                    """
                    INSERT INTO runtime_data.dialogue_history
                    (session_id, runtime_entity_id, context_id, speaker_type, message)
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    self.session_id, npc_id, dialogue_state['current_context_id'], "player", player_input
                )
                
                # 간단한 응답 생성 (실제로는 더 복잡한 로직 필요)
                if "상점" in player_input or "물건" in player_input:
                    response = "어서오세요! 오늘은 어떤 물건을 찾고 계신가요?"
                elif "뉴스" in player_input or "소식" in player_input:
                    response = "최근 숲에서 이상한 몬스터들이 목격되고 있습니다. 조심하세요."
                else:
                    response = "흥미로운 이야기네요. 더 자세히 들려주세요."
                
                # NPC 응답 기록
                await conn.execute(
                    """
                    INSERT INTO runtime_data.dialogue_history
                    (session_id, runtime_entity_id, context_id, speaker_type, message)
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    self.session_id, npc_id, dialogue_state['current_context_id'], "npc", response
                )
                
                return response
                
            except Exception as e:
                print(f"대화 처리 오류: {e}")
                return "대화 처리 중 오류가 발생했습니다."

    async def get_session_info(self) -> Dict[str, Any]:
        """세션 정보를 조회합니다."""
        if self._session_info is None:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT session_id, session_state, created_at, last_active_at, metadata
                    FROM runtime_data.active_sessions
                    WHERE session_id = $1
                    """,
                    self.session_id
                )
                
                if row:
                    self._session_info = dict(row)
                else:
                    self._session_info = {}
        
        return self._session_info

    async def get_player_entities(self) -> List[Dict[str, Any]]:
        """플레이어 엔티티들을 조회합니다."""
        if self._player_entities is None:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT 
                        er.runtime_entity_id,
                        er.game_entity_id,
                        er.entity_type,
                        er.is_player,
                        es.current_stats,
                        es.current_position,
                        es.current_position->>'runtime_cell_id' as runtime_cell_id,
                        es.active_effects,
                        es.inventory,
                        es.equipped_items
                    FROM reference_layer.entity_references er
                    LEFT JOIN runtime_data.entity_states es ON er.runtime_entity_id = es.runtime_entity_id
                    WHERE er.session_id = $1 AND er.is_player = TRUE
                    """,
                    self.session_id
                )
                
                self._player_entities = [dict(row) for row in rows]
        
        return self._player_entities

    async def get_npc_entities(self) -> List[Dict[str, Any]]:
        """NPC 엔티티들을 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT 
                    er.runtime_entity_id,
                    er.game_entity_id,
                    er.entity_type,
                    er.is_player,
                    es.current_stats,
                    es.current_position,
                    es.runtime_cell_id,
                    es.active_effects
                FROM reference_layer.entity_references er
                LEFT JOIN runtime_data.entity_states es ON er.runtime_entity_id = es.runtime_entity_id
                WHERE er.session_id = $1 AND er.is_player = FALSE
                """,
                self.session_id
            )
            
            return [dict(row) for row in rows]

    async def get_cell_contents(self, cell_id: str) -> Dict[str, Any]:
        """셀의 내용을 조회합니다."""
        return await self.cell_manager.get_cell_contents(cell_id)

    async def get_player_inventory(self, player_id: str) -> Dict[str, Any]:
        """플레이어의 인벤토리를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT inventory, equipped_items
                FROM runtime_data.entity_states
                WHERE runtime_entity_id = $1
                """,
                player_id
            )
            
            if row:
                return {
                    'inventory': row['inventory'],
                    'equipment': row['equipped_items']
                }
            return {'inventory': {}, 'equipment': {}}

    async def update_player_stats(self, player_id: str, new_stats: Dict[str, Any]) -> bool:
        """플레이어 스탯을 업데이트합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            try:
                await conn.execute(
                    """
                    UPDATE runtime_data.entity_states
                    SET current_stats = $1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE runtime_entity_id = $2
                    """,
                    json.dumps(new_stats),
                    player_id
                )
                
                # 캐시 무효화
                self._player_entities = None
                return True
            except Exception as e:
                print(f"스탯 업데이트 오류: {e}")
                return False

    async def end_session(self) -> None:
        """게임 세션을 종료합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            try:
                async with conn.transaction():
                    # 1. 먼저 active_sessions에서 플레이어 참조 제거
                    await conn.execute(
                        """
                        UPDATE runtime_data.active_sessions
                        SET player_runtime_entity_id = NULL
                        WHERE session_id = $1
                        """,
                        self.session_id
                    )
                    
                    # 2. 엔티티 상태 삭제
                    await conn.execute(
                        """
                        DELETE FROM runtime_data.entity_states
                        WHERE runtime_entity_id IN (
                            SELECT runtime_entity_id FROM reference_layer.entity_references
                            WHERE session_id = $1
                        )
                        """,
                        self.session_id
                    )
                    
                    # 3. 엔티티 참조 삭제
                    await conn.execute(
                        """
                        DELETE FROM reference_layer.entity_references
                        WHERE session_id = $1
                        """,
                        self.session_id
                    )
                    
                    # 4. 셀 참조 삭제
                    await conn.execute(
                        """
                        DELETE FROM reference_layer.cell_references
                        WHERE session_id = $1
                        """,
                        self.session_id
                    )
                    
                    # 5. 세션 삭제
                    await conn.execute(
                        """
                        DELETE FROM runtime_data.active_sessions
                        WHERE session_id = $1
                        """,
                        self.session_id
                    )
                
                # 캐시 초기화
                self._session_info = None
                self._player_entities = None
                
            except Exception as e:
                print(f"세션 종료 오류: {e}")

    async def save_session_state(self) -> bool:
        """세션 상태를 저장합니다."""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                await conn.execute(
                    """
            UPDATE runtime_data.active_sessions
                    SET metadata = jsonb_set(
                        COALESCE(metadata, '{}'::jsonb),
                        '{last_save}',
                        $1::jsonb
                    )
                    WHERE session_id = $2
                    """,
                    json.dumps(datetime.now().isoformat()),
                    self.session_id
                )
            
            return True
            
        except Exception as e:
            print(f"세션 저장 오류: {e}")
            return False

    async def get_dialogue_history(self, npc_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """NPC와의 대화 히스토리를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT speaker_type, message, timestamp
                FROM runtime_data.dialogue_history
                WHERE session_id = $1 AND runtime_entity_id = $2
                ORDER BY timestamp DESC
                LIMIT $3
                """,
                self.session_id, npc_id, limit
            )
            
            return [dict(row) for row in rows]

    async def get_available_actions(self, player_id: str, target_id: str) -> List[str]:
        """플레이어가 대상에 대해 수행할 수 있는 액션들을 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # 대상 엔티티 정보 조회
            target_info = await conn.fetchrow(
                """
                SELECT er.entity_type, er.is_player, e.entity_properties
                FROM reference_layer.entity_references er
                LEFT JOIN game_data.entities e ON er.game_entity_id = e.entity_id
                WHERE er.runtime_entity_id = $1 AND er.session_id = $2
                """,
                target_id, self.session_id
            )
            
            if not target_info:
                return []
            
            actions = []
            
            # NPC인 경우
            if target_info['entity_type'] == 'npc' and not target_info['is_player']:
                actions.append("대화")
                
                # 상점 NPC인 경우
                if target_info['entity_properties'] and 'shop_type' in target_info['entity_properties']:
                    actions.append("거래")
                
                # 퀘스트 NPC인 경우
                if target_info['entity_properties'] and target_info['entity_properties'].get('quest_giver'):
                    actions.append("퀘스트")
            
            # 플레이어인 경우
            elif target_info['is_player']:
                actions.append("파티 초대")
                actions.append("거래")
            
            return actions 