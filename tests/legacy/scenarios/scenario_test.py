from typing import Dict, Any, Optional
import asyncio
import uuid
from datetime import datetime, timezone
import sys
import os
import json

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.connection import DatabaseConnection
from database.factories.game_data_factory import GameDataFactory
from database.factories.instance_factory import InstanceFactory
from database.repositories.game_data import GameDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from database.repositories.runtime_data import RuntimeDataRepository

class GameScenarioTest:
    def __init__(self):
        self.db = DatabaseConnection()
        self.game_data_factory = GameDataFactory()
        self.instance_factory = InstanceFactory()
        self.game_data = GameDataRepository(db_connection)
        self.reference_layer = ReferenceLayerRepository(db_connection)
        self.runtime_data = RuntimeDataRepository(db_connection)
        
        # 테스트 세션 정보 저장
        self.session_id: Optional[str] = None
        self.player_runtime_id: Optional[str] = None
        self.merchant_runtime_id: Optional[str] = None
        self.test_cell_id: Optional[str] = None
        
        # 고유한 테스트 ID 생성
        self.test_id = uuid.uuid4().hex[:8]
        
    async def setup_test_data(self):
        """테스트에 필요한 기본 게임 데이터를 생성합니다."""
        # 1. events 테이블이 없으면 생성
        await self.create_events_table_if_not_exists()
        
        # 2. 테스트 NPC(상인) 템플릿 생성
        self.merchant_template_id = f"TEST_MERCHANT_{self.test_id}"
        await self.game_data_factory.create_npc_template(
            template_id=self.merchant_template_id,
            name="테스트 상인",
            template_type="merchant",
            base_stats={"hp": 100, "level": 1},
            base_properties={
                "bargain_skill": 5,
                "dialogue": {
                    "greeting": "어서오세요!",
                    "farewell": "안녕히 가세요!",
                    "quest_complete": "퀘스트를 완료하셨군요!"
                }
            }
        )
        
        # 3. 테스트 플레이어 템플릿 생성
        self.player_template_id = f"TEST_PLAYER_{self.test_id}"
        await self.game_data_factory.create_npc_template(
            template_id=self.player_template_id,
            name="테스트 플레이어",
            template_type="player",
            base_stats={
                "hp": 100,
                "mp": 100,
                "level": 1,
                "exp": 0
            },
            base_properties={
                "inventory_size": 20,
                "equipment_slots": ["weapon", "armor", "accessory"]
            }
        )
        
        # 4. 테스트 이벤트 생성
        self.test_event_id = f"TEST_EVENT_{self.test_id}"
        await self.game_data.create_event({
            "event_id": self.test_event_id,
            "name": "테스트 퀘스트",
            "type": "quest",
            "properties": json.dumps({
                "description": "상인과 대화하기",
                "rewards": {
                    "exp": 100,
                    "gold": 50
                }
            })
        })
        
    async def create_events_table_if_not_exists(self):
        """events 테이블이 없으면 생성합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # 테이블 존재 여부 확인
            result = await conn.fetchval(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'game_data' 
                    AND table_name = 'events'
                );
                """
            )
            
            if not result:
                # events 테이블 생성
                await conn.execute(
                    """
                    CREATE TABLE game_data.events (
                        event_id VARCHAR(50) PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        type VARCHAR(50) NOT NULL,
                        properties JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    """
                )
                print("events 테이블이 생성되었습니다.")
        
    async def run_scenario(self):
        """테스트 시나리오를 실행합니다."""
        try:
            print("테스트 시나리오 시작...")
            
            # 1. 테스트 세션 생성 (새로운 세션 중심 설계)
            self.session_id = await self.create_test_session()
            print(f"테스트 세션 생성됨: {self.session_id}")
            
            # 2. 테스트 셀 생성
            self.test_cell_id = await self.create_test_cell()
            print(f"테스트 셀 생성됨: {self.test_cell_id}")
            
            # 3. 테스트 플레이어 캐릭터 생성
            self.player_runtime_id = await self.create_test_player()
            print(f"테스트 플레이어 생성됨: {self.player_runtime_id}")
            
            # 4. 테스트 상인 NPC 생성
            self.merchant_runtime_id = await self.create_test_merchant()
            print(f"테스트 상인 생성됨: {self.merchant_runtime_id}")
            
            # 5. 플레이어를 테스트 셀에 입장
            await self.enter_test_cell()
            print("플레이어가 테스트 셀에 입장함")
            
            # 6. 셀의 엔티티 및 오브젝트 로드
            cell_data = await self.load_cell_data()
            print("셀 데이터 로드됨:", cell_data)
            
            # 7. 상인과 상호작용
            await self.interact_with_merchant()
            print("상인과 상호작용 완료")
            
            # 8. 이벤트 상태 업데이트
            await self.complete_test_event()
            print("테스트 이벤트 완료")
            
            print("시나리오 테스트 성공!")
            return True
            
        except Exception as e:
            print(f"시나리오 테스트 실패: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
    async def create_test_session(self) -> str:
        """테스트 세션을 생성합니다. (새로운 세션 중심 설계)"""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                # 1. 플레이어 엔티티를 game_data.entities에 먼저 등록 (실제 컬럼명에 맞게 수정)
                player_entity_id = f"PLAYER_{self.test_id}"
                await conn.execute(
                    '''
                    INSERT INTO game_data.entities (
                        entity_id, entity_type, entity_name, entity_description,
                        base_stats, default_equipment, default_abilities, default_inventory, entity_properties
                    )
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    ON CONFLICT (entity_id) DO NOTHING
                    ''',
                    player_entity_id,
                    "player",
                    "테스트 플레이어",
                    "테스트용 플레이어 엔티티",
                    json.dumps({"hp": 100, "mp": 100, "level": 1, "exp": 0}),
                    json.dumps({}),  # default_equipment
                    json.dumps({}),  # default_abilities
                    json.dumps({}),  # default_inventory
                    json.dumps({"inventory_size": 20, "equipment_slots": ["weapon", "armor", "accessory"]})
                )

                # 2. 세션 먼저 생성 (session_id만으로 가능)
                session_id = str(uuid.uuid4())
                await conn.execute(
                    """
                    INSERT INTO runtime_data.active_sessions 
                    (session_id, session_state, metadata)
                    VALUES ($1, 'active', $2)
                    """,
                    session_id,
                    json.dumps({
                        "type": "test",
                        "max_players": 1,
                        "test_id": self.test_id
                    })
                )
                
                # 3. 플레이어 엔티티 참조 생성 (session_id 참조)
                player_runtime_id = str(uuid.uuid4())
                await conn.execute(
                    """
                    INSERT INTO reference_layer.entity_references
                    (runtime_entity_id, game_entity_id, session_id, entity_type, is_player)
                    VALUES ($1, $2, $3, 'player', TRUE)
                    """,
                    player_runtime_id, player_entity_id, session_id
                )
                
                # 4. runtime_entities 테이블에 엔티티 등록
                await conn.execute(
                    """
                    INSERT INTO runtime_data.runtime_entities
                    (runtime_entity_id, game_entity_id, session_id)
                    VALUES ($1, $2, $3)
                    """,
                    player_runtime_id, player_entity_id, session_id
                )
                
                # 5. 세션에 플레이어 정보 추가 (선택적)
                await conn.execute(
                    """
                    UPDATE runtime_data.active_sessions 
                    SET player_runtime_entity_id = $1 
                    WHERE session_id = $2
                    """,
                    player_runtime_id, session_id
                )
                
                self.player_runtime_entity_id = player_runtime_id
                return session_id
        
    async def create_test_cell(self) -> str:
        """테스트 셀을 생성합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                game_cell_id = f"TEST_CELL_{self.test_id}"
                test_location_id = f"TEST_LOC_{self.test_id}"
                test_region_id = f"TEST_REGION_{self.test_id}"

                # 1. world_regions에 임시 region 등록 (존재하지 않으면)
                await conn.execute(
                    '''
                    INSERT INTO game_data.world_regions (region_id, region_name)
                    VALUES ($1, $2)
                    ON CONFLICT (region_id) DO NOTHING
                    ''',
                    test_region_id, "테스트 지역"
                )

                # 2. world_locations에 임시 location 등록 (존재하지 않으면)
                await conn.execute(
                    '''
                    INSERT INTO game_data.world_locations (location_id, region_id, location_name)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (location_id) DO NOTHING
                    ''',
                    test_location_id, test_region_id, "테스트 로케이션"
                )

                # 3. world_cells에 셀 등록 (존재하지 않으면)
                await conn.execute(
                    '''
                    INSERT INTO game_data.world_cells (
                        cell_id, location_id, cell_name, matrix_width, matrix_height, cell_description, cell_properties
                    )
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (cell_id) DO NOTHING
                    ''',
                    game_cell_id, test_location_id, "테스트 셀", 100, 100, "테스트용 셀",
                    json.dumps({"spawn_point": {"x": 50, "y": 0, "z": 50}})
                )

                # 4. 셀 참조 생성
                runtime_cell_id = str(uuid.uuid4())
                await conn.execute(
                    """
                    INSERT INTO reference_layer.cell_references
                    (runtime_cell_id, game_cell_id, session_id, cell_type)
                    VALUES ($1, $2, $3, $4)
                    """,
                    runtime_cell_id, game_cell_id, self.session_id, "indoor"
                )
                
                return runtime_cell_id
        
    async def create_test_player(self) -> str:
        """테스트 플레이어 캐릭터를 생성합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                # 플레이어 엔티티 상태 생성
                await conn.execute(
                    """
                    INSERT INTO runtime_data.entity_states
                    (runtime_entity_id, current_stats, current_position, active_effects, inventory, equipped_items)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    self.player_runtime_entity_id,
                    json.dumps({
                        "hp": 100,
                        "mp": 100,
                        "level": 1,
                        "exp": 0
                    }),
                    json.dumps({"x": 50, "y": 0, "z": 50}),
                    json.dumps([]),
                    json.dumps([]),
                    json.dumps([])
                )
                
                return self.player_runtime_entity_id
        
    async def create_test_merchant(self) -> str:
        """테스트 상인 NPC를 생성합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                # 1. 상인 엔티티 참조 생성
                merchant_runtime_id = str(uuid.uuid4())
                await conn.execute(
                    """
                    INSERT INTO reference_layer.entity_references
                    (runtime_entity_id, game_entity_id, session_id, entity_type, is_player)
                    VALUES ($1, $2, $3, 'npc', FALSE)
                    """,
                    merchant_runtime_id, self.merchant_template_id, self.session_id
                )
                
                # 2. runtime_entities 테이블에 엔티티 등록
                await conn.execute(
                    """
                    INSERT INTO runtime_data.runtime_entities
                    (runtime_entity_id, game_entity_id, session_id)
                    VALUES ($1, $2, $3)
                    """,
                    merchant_runtime_id, self.merchant_template_id, self.session_id
                )
                
                # 3. 상인 엔티티 상태 생성
                await conn.execute(
                    """
                    INSERT INTO runtime_data.entity_states
                    (runtime_entity_id, current_stats, current_position, active_effects, inventory, equipped_items)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    merchant_runtime_id,
                    json.dumps({
                        "hp": 100,
                        "level": 1
                    }),
                    json.dumps({"x": 55, "y": 0, "z": 55}),
                    json.dumps([]),
                    json.dumps([]),
                    json.dumps([])
                )
                
                return merchant_runtime_id
        
    async def enter_test_cell(self):
        """플레이어를 테스트 셀에 입장시킵니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE runtime_data.entity_states
                SET current_position = $1
                WHERE runtime_entity_id = $2
                """,
                json.dumps({"x": 50, "y": 0, "z": 50}),
                self.player_runtime_id
            )
        
    async def load_cell_data(self) -> Dict[str, Any]:
        """셀의 엔티티와 오브젝트 정보를 로드합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # 셀의 엔티티들 조회
            entities = await conn.fetch(
                """
                SELECT er.runtime_entity_id, er.game_entity_id, er.entity_type, er.is_player,
                       es.current_stats, es.current_position
                FROM reference_layer.entity_references er
                JOIN runtime_data.entity_states es ON er.runtime_entity_id = es.runtime_entity_id
                WHERE er.session_id = $1
                """,
                self.session_id
            )
            
            return {
                "cell_id": self.test_cell_id,
                "entities": [dict(entity) for entity in entities]
            }
        
    async def interact_with_merchant(self):
        """상인과 상호작용합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # 상인 엔티티 정보 조회
            merchant_entity = await conn.fetchrow(
                """
                SELECT e.entity_id, e.dialogue_context_id
                FROM game_data.entities e
                JOIN reference_layer.entity_references er ON e.entity_id = er.game_entity_id
                WHERE er.runtime_entity_id = $1
                """,
                self.merchant_runtime_id
            )
            
            # 대화 컨텍스트 조회
            dialogue_contexts = await conn.fetch(
                """
                SELECT title, content, priority
                FROM game_data.dialogue_contexts
                WHERE entity_id = $1
                ORDER BY priority DESC
                """,
                merchant_entity['entity_id']
            )
            
            # 인사말 찾기
            greeting_context = next((dc for dc in dialogue_contexts if '인사' in dc['title']), None)
            farewell_context = next((dc for dc in dialogue_contexts if '작별' in dc['title']), None)
            
            greeting = greeting_context['content'] if greeting_context else '어서오세요!'
            farewell = farewell_context['content'] if farewell_context else '안녕히 가세요!'
            
            print(f"상인: {greeting}")
            await asyncio.sleep(1)
            print(f"상인: {farewell}")
        
    async def complete_test_event(self):
        """테스트 이벤트를 완료 상태로 변경합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                # 1. 이벤트 데이터 조회
                event_data = await conn.fetchrow(
                    """
                    SELECT properties FROM game_data.events
                    WHERE event_id = $1
                    """,
                    self.test_event_id
                )
                
                rewards = json.loads(event_data['properties'])['rewards']
                
                # 2. 플레이어 경험치 업데이트
                current_stats = await conn.fetchval(
                    """
                    SELECT current_stats FROM runtime_data.entity_states
                    WHERE runtime_entity_id = $1
                    """,
                    self.player_runtime_id
                )
                
                stats = json.loads(current_stats)
                stats['exp'] += rewards['exp']
                
                await conn.execute(
                    """
                    UPDATE runtime_data.entity_states
                    SET current_stats = $1
                    WHERE runtime_entity_id = $2
                    """,
                    json.dumps(stats),
                    self.player_runtime_id
                )
                
                # 3. 완료 메시지 (대화 컨텍스트에서 조회)
                merchant_entity = await conn.fetchrow(
                    """
                    SELECT e.entity_id
                    FROM game_data.entities e
                    JOIN reference_layer.entity_references er ON e.entity_id = er.game_entity_id
                    WHERE er.runtime_entity_id = $1
                    """,
                    self.merchant_runtime_id
                )
                
                quest_complete_context = await conn.fetchrow(
                    """
                    SELECT content
                    FROM game_data.dialogue_contexts
                    WHERE entity_id = $1 AND title LIKE '%완료%'
                    ORDER BY priority DESC
                    LIMIT 1
                    """,
                    merchant_entity['entity_id']
                )
                
                quest_complete_msg = quest_complete_context['content'] if quest_complete_context else '퀘스트를 완료하셨군요!'
                
                print(f"상인: {quest_complete_msg}")
                print(f"경험치 {rewards['exp']} 획득!")

async def run_test():
    """테스트 실행 함수"""
    scenario = GameScenarioTest()
    await scenario.setup_test_data()
    success = await scenario.run_scenario()
    if success:
        print("모든 테스트가 성공적으로 완료되었습니다.")
    else:
        print("테스트 중 오류가 발생했습니다.")

if __name__ == "__main__":
    asyncio.run(run_test()) 