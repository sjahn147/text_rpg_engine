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

class ModularGameScenarioTest:
    def __init__(self):
        # 데이터베이스 연결
        self.db = DatabaseConnection()
        
        # Repository 클래스들
        self.game_data = GameDataRepository(db_connection)
        self.reference_layer = ReferenceLayerRepository(db_connection)
        self.runtime_data = RuntimeDataRepository(db_connection)
        
        # Factory 클래스들
        self.game_data_factory = GameDataFactory()
        self.instance_factory = InstanceFactory()
        
        # 테스트 세션 정보 저장
        self.session_id: Optional[str] = None
        self.player_runtime_id: Optional[str] = None
        self.merchant_runtime_id: Optional[str] = None
        self.test_cell_id: Optional[str] = None
        
        # 고유한 테스트 ID 생성
        self.test_id = uuid.uuid4().hex[:8]
        
    async def setup_test_data(self):
        """테스트에 필요한 기본 게임 데이터를 생성합니다."""
        print("테스트 데이터 설정 시작...")
        
        # 1. events 테이블이 없으면 생성
        await self.create_events_table_if_not_exists()
        
        # 2. 테스트 월드 구조 생성
        await self.create_test_world_structure()
        
        # 3. 테스트 NPC(상인) 템플릿 생성
        await self.create_test_merchant_template()
        
        # 4. 테스트 플레이어 템플릿 생성
        await self.create_test_player_template()
        
        # 5. 테스트 이벤트 생성
        await self.create_test_event()
        
        # 6. 대화 컨텍스트 생성
        await self.create_dialogue_contexts()
        
        print("테스트 데이터 설정 완료!")
        
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
        
    async def create_test_world_structure(self):
        """테스트용 월드 구조를 생성합니다."""
        # 1. 테스트 지역 생성
        test_region_id = f"TEST_REGION_{self.test_id}"
        await self.game_data_factory.create_world_region(
            region_id=test_region_id,
            region_name="테스트 지역",
            region_type="continent",
            description="테스트용 지역"
        )
        
        # 2. 테스트 위치 생성
        test_location_id = f"TEST_LOC_{self.test_id}"
        await self.game_data_factory.create_world_location(
            location_id=test_location_id,
            region_id=test_region_id,
            location_name="테스트 로케이션",
            description="테스트용 위치"
        )
        
        # 3. 테스트 셀 생성
        self.test_game_cell_id = f"TEST_CELL_{self.test_id}"
        await self.game_data_factory.create_world_cell(
            cell_id=self.test_game_cell_id,
            location_id=test_location_id,
            cell_name="테스트 셀",
            matrix_width=100,
            matrix_height=100,
            cell_description="테스트용 셀",
            cell_properties={"spawn_point": {"x": 50, "y": 0, "z": 50}}
        )
        
    async def create_test_merchant_template(self):
        """테스트용 상인 NPC 템플릿을 생성합니다."""
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
        
    async def create_test_player_template(self):
        """테스트용 플레이어 템플릿을 생성합니다."""
        self.player_template_id = f"TEST_PLAYER_{self.test_id}"
        await self.game_data_factory.create_player_template(
            template_id=self.player_template_id,
            name="테스트 플레이어",
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
        
    async def create_test_event(self):
        """테스트 이벤트를 생성합니다."""
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
        
    async def create_dialogue_contexts(self):
        """대화 컨텍스트를 생성합니다."""
        # 인사말 컨텍스트
        await self.game_data_factory.create_dialogue_context(
            entity_id=self.merchant_template_id,
            title="인사",
            content="어서오세요! 무엇을 도와드릴까요?",
            priority=1
        )
        
        # 작별인사 컨텍스트
        await self.game_data_factory.create_dialogue_context(
            entity_id=self.merchant_template_id,
            title="작별인사",
            content="안녕히 가세요! 또 들러주세요!",
            priority=2
        )
        
        # 퀘스트 완료 컨텍스트
        await self.game_data_factory.create_dialogue_context(
            entity_id=self.merchant_template_id,
            title="퀘스트 완료",
            content="퀘스트를 완료하셨군요! 축하합니다!",
            priority=3
        )
        
    async def run_scenario(self):
        """테스트 시나리오를 실행합니다."""
        try:
            print("모듈러 시나리오 테스트 시작...")
            
            # 1. 테스트 세션 생성
            self.session_id = await self.create_test_session()
            print(f"테스트 세션 생성됨: {self.session_id}")
            
            # 2. 테스트 셀 인스턴스 생성
            self.test_cell_id = await self.create_test_cell_instance()
            print(f"테스트 셀 인스턴스 생성됨: {self.test_cell_id}")
            
            # 3. 테스트 플레이어 인스턴스 생성
            self.player_runtime_id = await self.create_test_player_instance()
            print(f"테스트 플레이어 인스턴스 생성됨: {self.player_runtime_id}")
            
            # 4. 테스트 상인 인스턴스 생성
            self.merchant_runtime_id = await self.create_test_merchant_instance()
            print(f"테스트 상인 인스턴스 생성됨: {self.merchant_runtime_id}")
            
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
            
            print("모듈러 시나리오 테스트 성공!")
            return True
            
        except Exception as e:
            print(f"모듈러 시나리오 테스트 실패: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
    async def create_test_session(self) -> str:
        """테스트 세션을 생성합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                # 1. 세션 생성
                session_id = str(uuid.uuid4())
                await self.runtime_data.create_session({
                    "session_id": session_id,
                    "session_state": "active",
                    "created_at": datetime.now(),
                    "metadata": json.dumps({
                        "type": "test",
                        "max_players": 1,
                        "test_id": self.test_id
                    })
                })
                
                return session_id
        
    async def create_test_cell_instance(self) -> str:
        """테스트 셀 인스턴스를 생성합니다."""
        return await self.instance_factory.create_cell_instance(
            game_cell_id=self.test_game_cell_id,
            session_id=self.session_id
        )
        
    async def create_test_player_instance(self) -> str:
        """테스트 플레이어 인스턴스를 생성합니다."""
        return await self.instance_factory.create_player_instance(
            game_entity_id=self.player_template_id,
            session_id=self.session_id,
            runtime_cell_id=self.test_cell_id,
            position={"x": 50, "y": 0, "z": 50}
        )
        
    async def create_test_merchant_instance(self) -> str:
        """테스트 상인 인스턴스를 생성합니다."""
        return await self.instance_factory.create_npc_instance(
            game_entity_id=self.merchant_template_id,
            session_id=self.session_id,
            runtime_cell_id=self.test_cell_id,
            position={"x": 55, "y": 0, "z": 55}
        )
        
    async def enter_test_cell(self):
        """플레이어를 테스트 셀에 입장시킵니다."""
        await self.runtime_data.update_entity_cell(
            runtime_entity_id=self.player_runtime_id,
            runtime_cell_id=self.test_cell_id,
            position={"x": 50, "y": 0, "z": 50}
        )
        
    async def load_cell_data(self) -> Dict[str, Any]:
        """셀의 엔티티와 오브젝트 정보를 로드합니다."""
        return await self.runtime_data.get_cell_data(self.test_cell_id)
        
    async def interact_with_merchant(self):
        """상인과 상호작용합니다."""
        # 상인 엔티티 정보 조회
        merchant_entity = await self.game_data.get_entity(self.merchant_template_id)
        
        # 대화 컨텍스트 조회
        dialogue_contexts = await self.game_data.get_dialogue_contexts(self.merchant_template_id)
        
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
                event_data = await self.game_data.get_event(self.test_event_id)
                rewards = json.loads(event_data['properties'])['rewards']
                
                # 2. 플레이어 경험치 업데이트
                current_stats = await self.runtime_data.get_entity_state(self.player_runtime_id)
                stats = json.loads(current_stats['current_stats'])
                stats['exp'] += rewards['exp']
                
                await self.runtime_data.update_entity_stats(
                    runtime_entity_id=self.player_runtime_id,
                    stats={"exp": rewards['exp']}
                )
                
                # 3. 완료 메시지 (대화 컨텍스트에서 조회)
                quest_complete_context = await self.game_data.get_dialogue_context_by_title(
                    entity_id=self.merchant_template_id,
                    title="완료"
                )
                
                quest_complete_msg = quest_complete_context['content'] if quest_complete_context else '퀘스트를 완료하셨군요!'
                
                print(f"상인: {quest_complete_msg}")
                print(f"경험치 {rewards['exp']} 획득!")

async def run_modular_test():
    """모듈러 테스트 실행 함수"""
    scenario = ModularGameScenarioTest()
    await scenario.setup_test_data()
    success = await scenario.run_scenario()
    if success:
        print("모든 모듈러 테스트가 성공적으로 완료되었습니다.")
    else:
        print("모듈러 테스트 중 오류가 발생했습니다.")

if __name__ == "__main__":
    asyncio.run(run_modular_test()) 