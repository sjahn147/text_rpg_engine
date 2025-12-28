from typing import Dict, List, Optional, Any, Tuple
import uuid
import json
import asyncio
from datetime import datetime
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from database.factories.game_data_factory import GameDataFactory
from database.factories.instance_factory import InstanceFactory

class GameManager:
    """게임 전체를 관리하는 핵심 클래스"""
    
    def __init__(self, 
                 db_connection: DatabaseConnection,
                 game_data_repo: GameDataRepository,
                 runtime_data_repo: RuntimeDataRepository,
                 reference_layer_repo: ReferenceLayerRepository,
                 game_data_factory: GameDataFactory,
                 instance_factory: InstanceFactory):
        """
        의존성 주입을 통한 GameManager 초기화
        
        Args:
            db_connection: 데이터베이스 연결
            game_data_repo: 게임 데이터 저장소
            runtime_data_repo: 런타임 데이터 저장소
            reference_layer_repo: 참조 레이어 저장소
            game_data_factory: 게임 데이터 팩토리
            instance_factory: 인스턴스 팩토리
        """
        self.db = db_connection
        
        # Repository 클래스들 (의존성 주입)
        self.game_data = game_data_repo
        self.runtime_data = runtime_data_repo
        self.reference_layer = reference_layer_repo
        
        # Factory 클래스들 (의존성 주입)
        self.game_data_factory = game_data_factory
        self.instance_factory = instance_factory
        
        # 현재 세션 정보
        self.current_session_id: Optional[str] = None
        self.current_player_id: Optional[str] = None
        
    async def start_new_game(self, player_template_id: str, start_cell_id: str = None) -> str:
        """새로운 게임 세션을 시작합니다."""
        try:
            # 1. 게임 세션 생성
            session_id = await self._create_game_session()
            
            # 2. 시작 셀 결정 및 인스턴스 생성
            if not start_cell_id:
                start_cell_id = await self._get_default_start_cell()
            
            cell_runtime_id = await self._create_cell_instance(start_cell_id, session_id)
            
            # 3. 플레이어 인스턴스 생성
            player_runtime_id = await self._create_player_instance(
                player_template_id, session_id, cell_runtime_id
            )
            
            # 4. 세션에 플레이어 참조 추가
            await self._link_player_to_session(session_id, player_runtime_id)
            
            # 5. 초기 NPC들 생성 (상점, 퀘스트 NPC 등)
            await self._spawn_initial_npcs(session_id, cell_runtime_id)
            
            # 6. 세션 정보 저장
            self.current_session_id = session_id
            self.current_player_id = player_runtime_id
            
            return session_id
            
        except Exception as e:
            raise Exception(f"게임 시작 실패: {str(e)}")
    
    async def _create_game_session(self) -> str:
        """게임 세션을 생성합니다."""
        session_id = str(uuid.uuid4())
        
        await self.runtime_data.create_session({
            "session_id": session_id,
            "session_state": "active",
            "created_at": datetime.now(),
            "metadata": json.dumps({
                "game_version": "1.0.0",
                "created_at": datetime.now().isoformat(),
                "session_type": "single_player"
            })
        })
        
        return session_id
    
    async def _get_default_start_cell(self) -> str:
        """기본 시작 셀을 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # 레크로스타 여관 내 방 우선 검색
            cell_id = await conn.fetchval(
                """
                SELECT cell_id 
                FROM game_data.world_cells 
                WHERE cell_id = 'CELL_INN_ROOM_001'
                LIMIT 1
                """
            )
            
            if not cell_id:
                # 내 방이 없으면 이름으로 검색
                cell_id = await conn.fetchval(
                    """
                    SELECT cell_id 
                    FROM game_data.world_cells 
                    WHERE cell_name LIKE '%내 방%' OR cell_name LIKE '%room%' OR cell_name LIKE '%inn%'
                    LIMIT 1
                    """
                )
            
            if not cell_id:
                # 기본 셀 중 하나 선택
                cell_id = await conn.fetchval(
                    """
                    SELECT cell_id 
                    FROM game_data.world_cells 
                    LIMIT 1
                    """
                )
            
            if not cell_id:
                raise Exception("시작할 수 있는 셀이 없습니다. 먼저 셀을 생성해주세요.")
            
            return cell_id
    
    async def _create_cell_instance(self, game_cell_id: str, session_id: str) -> str:
        """셀 인스턴스를 생성합니다."""
        return await self.instance_factory.create_cell_instance(
            game_cell_id=game_cell_id,
            session_id=session_id
        )
    
    async def _create_player_instance(self, player_template_id: str, session_id: str, cell_runtime_id: str) -> str:
        """플레이어 인스턴스를 생성합니다."""
        return await self.instance_factory.create_player_instance(
            game_entity_id=player_template_id,
            session_id=session_id,
            runtime_cell_id=cell_runtime_id,
            position={"x": 50, "y": 0, "z": 50}  # 기본 시작 위치
        )
    
    async def _link_player_to_session(self, session_id: str, player_runtime_id: str):
        """세션에 플레이어를 연결합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE runtime_data.active_sessions
                SET player_runtime_entity_id = $1
                WHERE session_id = $2
                """,
                player_runtime_id, session_id
            )
    
    async def _spawn_initial_npcs(self, session_id: str, cell_runtime_id: str):
        """초기 NPC들을 생성합니다."""
        # NPC 생성은 선택적 (실패해도 게임 시작은 계속)
        try:
            # 상점 NPC 생성
            await self._spawn_merchant_npc(session_id, cell_runtime_id)
        except Exception as e:
            print(f"상점 NPC 생성 실패 (무시): {e}")
        
        try:
            # 퀘스트 NPC 생성
            await self._spawn_quest_npc(session_id, cell_runtime_id)
        except Exception as e:
            print(f"퀘스트 NPC 생성 실패 (무시): {e}")
    
    async def _spawn_merchant_npc(self, session_id: str, cell_runtime_id: str):
        """상점 NPC를 생성합니다."""
        try:
            # 상점 NPC 템플릿 찾기
            pool = await self.db.pool
            async with pool.acquire() as conn:
                merchant_template = await conn.fetchrow(
                    """
                    SELECT entity_id FROM game_data.entities 
                    WHERE entity_type = 'npc' AND entity_properties->>'shop_type' IS NOT NULL
                    LIMIT 1
                    """
                )
                
                if merchant_template:
                    await self.instance_factory.create_npc_instance(
                        game_entity_id=merchant_template['entity_id'],
                        session_id=session_id,
                        runtime_cell_id=cell_runtime_id,
                        position={"x": 100, "y": 0, "z": 100}
                    )
        except Exception as e:
            print(f"상점 NPC 생성 실패: {e}")
    
    async def _spawn_quest_npc(self, session_id: str, cell_runtime_id: str):
        """퀘스트 NPC를 생성합니다."""
        try:
            # 퀘스트 NPC 템플릿 찾기
            pool = await self.db.pool
            async with pool.acquire() as conn:
                quest_npc_template = await conn.fetchrow(
                    """
                    SELECT entity_id FROM game_data.entities 
                    WHERE entity_type = 'npc' AND entity_properties->>'quest_giver' = 'true'
                    LIMIT 1
                    """
                )
                
                if quest_npc_template:
                    await self.instance_factory.create_npc_instance(
                        game_entity_id=quest_npc_template['entity_id'],
                        session_id=session_id,
                        runtime_cell_id=cell_runtime_id,
                        position={"x": 150, "y": 0, "z": 150}
                    )
        except Exception as e:
            print(f"퀘스트 NPC 생성 실패: {e}")
    
    async def get_current_session_info(self) -> Dict[str, Any]:
        """현재 세션 정보를 조회합니다."""
        if not self.current_session_id:
            return {}
        
        return await self.runtime_data.get_session(self.current_session_id)
    
    async def get_player_info(self) -> Dict[str, Any]:
        """현재 플레이어 정보를 조회합니다."""
        if not self.current_player_id:
            return {}
        
        return await self.runtime_data.get_entity_state(self.current_player_id)
    
    async def move_player(self, target_cell_id: str, position: Dict[str, float]) -> bool:
        """플레이어를 이동시킵니다."""
        if not self.current_player_id:
            return False
        
        try:
            await self.runtime_data.update_entity_cell(
                runtime_entity_id=self.current_player_id,
                runtime_cell_id=target_cell_id,
                position=position
            )
            return True
        except Exception as e:
            print(f"플레이어 이동 실패: {e}")
            return False
    
    async def get_cell_contents(self, cell_runtime_id: str) -> Dict[str, Any]:
        """셀의 내용을 조회합니다."""
        return await self.runtime_data.get_cell_data(cell_runtime_id)
    
    async def start_dialogue(self, npc_runtime_id: str) -> Optional[str]:
        """NPC와의 대화를 시작합니다."""
        try:
            # NPC 정보 조회
            npc_info = await self.reference_layer.get_entity_reference(npc_runtime_id)
            if not npc_info:
                return None
            
            # 대화 컨텍스트 조회
            dialogue_contexts = await self.game_data.get_dialogue_contexts(npc_info['game_entity_id'])
            
            if not dialogue_contexts:
                return None
            
            # 기본 인사말 컨텍스트 반환
            greeting_context = next(
                (dc for dc in dialogue_contexts if '인사' in dc.get('title', '')), 
                dialogue_contexts[0]
            )
            
            return greeting_context.get('dialogue_id')
            
        except Exception as e:
            print(f"대화 시작 실패: {e}")
            return None
    
    async def process_dialogue_choice(self, dialogue_id: str, choice: str) -> str:
        """대화 선택을 처리합니다."""
        try:
            # 대화 컨텍스트 조회
            context = await self.game_data.get_dialogue_context(dialogue_id)
            if not context:
                return "대화를 찾을 수 없습니다."
            
            # 간단한 응답 생성 (실제로는 더 복잡한 로직 필요)
            if "상점" in choice or "물건" in choice:
                return "어서오세요! 오늘은 어떤 물건을 찾고 계신가요?"
            elif "퀘스트" in choice or "임무" in choice:
                return "퀘스트에 대해 궁금하시군요. 어떤 도움이 필요하신가요?"
            else:
                return "흥미로운 이야기네요. 더 자세히 들려주세요."
                
        except Exception as e:
            return f"대화 처리 중 오류가 발생했습니다: {e}"
    
    async def end_game_session(self):
        """게임 세션을 종료합니다."""
        if not self.current_session_id:
            return
        
        try:
            # 세션 정리 - 외래키 제약조건을 고려한 순서로 정리
            pool = await self.db.pool
            async with pool.acquire() as conn:
                async with conn.transaction():
                    # 1. 먼저 active_sessions에서 플레이어 참조 제거
                    await conn.execute(
                        """
                        UPDATE runtime_data.active_sessions
                        SET player_runtime_entity_id = NULL
                        WHERE session_id = $1
                        """,
                        self.current_session_id
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
                        self.current_session_id
                    )
                    
                    # 3. 엔티티 참조 삭제
                    await conn.execute(
                        """
                        DELETE FROM reference_layer.entity_references
                        WHERE session_id = $1
                        """,
                        self.current_session_id
                    )
                    
                    # 4. 셀 참조 삭제
                    await conn.execute(
                        """
                        DELETE FROM reference_layer.cell_references
                        WHERE session_id = $1
                        """,
                        self.current_session_id
                    )
                    
                    # 5. 세션 삭제
                    await conn.execute(
                        """
                        DELETE FROM runtime_data.active_sessions
                        WHERE session_id = $1
                        """,
                        self.current_session_id
                    )
            
            # 상태 초기화
            self.current_session_id = None
            self.current_player_id = None
            
        except Exception as e:
            print(f"세션 종료 실패: {e}")
    
    async def save_game_state(self) -> bool:
        """게임 상태를 저장합니다."""
        if not self.current_session_id:
            return False
        
        try:
            # 세션 메타데이터에 저장 시간 추가
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
                    self.current_session_id
                )
            
            return True
            
        except Exception as e:
            print(f"게임 저장 실패: {e}")
            return False
    
    async def load_game_state(self, session_id: str) -> bool:
        """저장된 게임 상태를 불러옵니다."""
        try:
            # 세션 존재 확인
            session_info = await self.runtime_data.get_session(session_id)
            if not session_info:
                return False
            
            # 플레이어 정보 조회
            player_runtime_id = session_info.get('player_runtime_entity_id')
            if not player_runtime_id:
                return False
            
            # 상태 복원
            self.current_session_id = session_id
            self.current_player_id = player_runtime_id
            
            return True
            
        except Exception as e:
            print(f"게임 로드 실패: {e}")
            return False

    async def load_cell_contents(self, cell_id: str) -> Dict[str, Any]:
        """특정 셀의 컨텐츠 로드"""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # 1. Game Data에서 셀 정보 조회
            cell_data = await self.game_data.get_cell(cell_id)
            if not cell_data:
                raise ValueError(f"Cell {cell_id} not found")

            # 2. 셀에 있는 엔티티들 조회
            entities = await conn.fetch(
                """
                SELECT er.runtime_entity_id, er.game_entity_id, er.entity_type, er.is_player,
                       es.current_stats, es.current_position
                FROM reference_layer.entity_references er
                JOIN runtime_data.entity_states es ON er.runtime_entity_id = es.runtime_entity_id
                JOIN reference_layer.cell_references cr ON es.current_position->>'runtime_cell_id' = cr.runtime_cell_id
                WHERE cr.game_cell_id = $1 AND er.session_id = $2
                """,
                cell_id, self.current_session_id
            )

            # 3. 셀에 있는 오브젝트들 조회
            objects = await conn.fetch(
                """
                SELECT or_ref.runtime_object_id, or_ref.game_object_id, or_ref.object_type,
                       os.current_state, os.current_position
                FROM reference_layer.object_references or_ref
                JOIN runtime_data.object_states os ON or_ref.runtime_object_id = os.runtime_object_id
                WHERE or_ref.session_id = $1
                """,
                self.current_session_id
            )

        return {
            'cell_data': cell_data,
            'entities': [dict(entity) for entity in entities],
            'objects': [dict(obj) for obj in objects]
        }

    async def handle_interaction(self, source_entity_id: str, target_entity_id: str,
                         interaction_type: str, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """엔티티 간 상호작용 처리"""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                # 1. 이벤트 생성
                event_id = str(uuid.uuid4())
                await conn.execute(
                    """
                    INSERT INTO runtime_data.triggered_events
                    (event_id, session_id, event_type, event_data, source_entity_ref, target_entity_ref)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    event_id, self.current_session_id, interaction_type,
                    json.dumps(interaction_data), source_entity_id, target_entity_id
                )

                # 2. 상호작용 타입에 따른 처리
                if interaction_type == 'DIALOGUE':
                    # 대화 컨텍스트 조회
                    context = await self.game_data.get_dialogue_context(interaction_data.get('context_id'))
                    if context:
                        return {
                            'event_id': event_id,
                            'context': context,
                            'choices': context.get('available_topics', [])
                        }

                elif interaction_type == 'TRADE':
                    return {
                        'event_id': event_id,
                        'available_items': interaction_data.get('items', []),
                        'prices': interaction_data.get('prices', {})
                    }

                return {'event_id': event_id}

    async def process_player_choice(self, event_id: str, choice_type: str,
                            choice_data: Dict[str, Any]) -> Dict[str, Any]:
        """플레이어의 선택 처리"""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                # 1. 선택 기록
                choice_id = str(uuid.uuid4())
                await conn.execute(
                    """
                    INSERT INTO runtime_data.player_choices
                    (choice_id, event_id, choice_type, choice_data)
                    VALUES ($1, $2, $3, $4)
                    """,
                    choice_id, event_id, choice_type, json.dumps(choice_data)
                )

                # 2. 선택에 따른 결과 처리
                affected_entities = []
                affected_objects = []
                consequence_data = {}

                if choice_type == 'DIALOGUE_RESPONSE':
                    consequence_data = {
                        'response': choice_data.get('response'),
                        'next_context': choice_data.get('next_context')
                    }

                elif choice_type == 'TRADE_ACCEPT':
                    buyer_id = choice_data.get('buyer_id')
                    seller_id = choice_data.get('seller_id')
                    items = choice_data.get('items', [])
                    
                    affected_entities.extend([buyer_id, seller_id])
                    affected_objects.extend(items)
                    
                    consequence_data = {
                        'transaction': 'success',
                        'items': items,
                        'price': choice_data.get('price')
                    }

                # 3. 결과 기록
                consequence_id = str(uuid.uuid4())
                await conn.execute(
                    """
                    INSERT INTO runtime_data.event_consequences
                    (consequence_id, choice_id, consequence_type, consequence_data, affected_entities, affected_objects)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    consequence_id, choice_id, f"{choice_type}_RESULT",
                    json.dumps(consequence_data),
                    json.dumps(affected_entities),
                    json.dumps(affected_objects)
                )

        return {
            'choice_id': choice_id,
            'consequence_id': consequence_id,
            'consequence_data': consequence_data
        } 