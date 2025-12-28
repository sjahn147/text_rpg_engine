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

# 새로 구현된 클래스들 import
from app.core.game_manager import GameManager
from app.game_session import GameSession
from app.entity.entity_manager import EntityManager
from app.entity.instance_manager import InstanceManager
from app.world.cell_manager import CellManager
from app.interaction import InteractionManager

class ClassBasedGameScenarioTest:
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
        
        # 새로 구현된 매니저 클래스들
        self.game_manager = GameManager()
        self.cell_manager = CellManager()
        self.entity_manager = EntityStateManager()
        self.instance_manager = InstanceManager()
        self.interaction_manager = InteractionManager()
        
        # 테스트 세션 정보 저장
        self.session_id: Optional[str] = None
        self.player_runtime_id: Optional[str] = None
        self.merchant_runtime_id: Optional[str] = None
        self.test_cell_id: Optional[str] = None
        self.game_session: Optional[GameSession] = None
        
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
                "shop_type": "general",
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
            print("클래스 기반 시나리오 테스트 시작...")
            
            # 1. GameManager를 사용하여 새 게임 시작
            self.session_id = await self.game_manager.start_new_game(
                player_template_id=self.player_template_id,
                start_cell_id=self.test_game_cell_id
            )
            print(f"게임 세션 생성됨: {self.session_id}")
            
            # 2. GameSession 객체 생성
            self.game_session = GameSession(self.session_id)
            await self.game_session.initialize_session()
            
            # 3. 플레이어 정보 조회
            player_entities = await self.game_session.get_player_entities()
            if player_entities:
                self.player_runtime_id = player_entities[0]['runtime_entity_id']
                print(f"플레이어 인스턴스 조회됨: {self.player_runtime_id}")
            
            # 4. 현재 셀 정보 조회
            player_info = await self.game_manager.get_player_info()
            if player_info:
                self.test_cell_id = player_info.get('runtime_cell_id')
                print(f"현재 셀 ID: {self.test_cell_id}")
            
            # 5. 셀 내용 조회 (CellManager 사용)
            cell_contents = await self.cell_manager.get_cell_contents(self.test_cell_id)
            print("셀 데이터 로드됨:", cell_contents)
            
            # 6. NPC들과 상호작용 (InteractionManager 사용)
            await self.interact_with_npcs()
            print("NPC들과 상호작용 완료")
            
            # 7. 플레이어 이동 테스트 (EntityStateManager 사용)
            await self.test_player_movement()
            print("플레이어 이동 테스트 완료")
            
            # 8. 게임 상태 저장
            await self.game_manager.save_game_state()
            print("게임 상태 저장 완료")
            
            print("클래스 기반 시나리오 테스트 성공!")
            return True
            
        except Exception as e:
            print(f"클래스 기반 시나리오 테스트 실패: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
    async def interact_with_npcs(self):
        """NPC들과 상호작용합니다."""
        # 1. 셀에 있는 NPC들 조회
        npc_entities = await self.game_session.get_npc_entities()
        
        for npc in npc_entities:
            npc_id = npc['runtime_entity_id']
            npc_name = npc.get('entity_name', '알 수 없는 NPC')
            
            print(f"\n{npc_name}와 상호작용 시작...")
            
            # 2. 상호작용 가능 여부 확인
            can_interact = await self.interaction_manager.can_interact(
                self.player_runtime_id, npc_id, self.session_id
            )
            
            if not can_interact:
                print(f"{npc_name}와 상호작용할 수 없습니다. (거리가 멀어요)")
                continue
            
            # 3. 사용 가능한 액션 조회
            available_actions = await self.interaction_manager.get_available_actions(
                self.player_runtime_id, npc_id, self.session_id
            )
            
            print(f"사용 가능한 액션: {available_actions}")
            
            # 4. 대화 시작
            if "대화" in available_actions:
                dialogue_context_id = await self.interaction_manager.start_dialogue(
                    self.player_runtime_id, npc_id, self.session_id
                )
                
                if dialogue_context_id:
                    print(f"대화 시작됨: {dialogue_context_id}")
                    
                    # 5. 대화 입력 처리
                    player_input = "안녕하세요! 상점에 대해 궁금해요."
                    npc_response = await self.interaction_manager.process_dialogue_input(
                        player_input, npc_id, self.session_id
                    )
                    
                    print(f"플레이어: {player_input}")
                    print(f"{npc_name}: {npc_response}")
                    
                    # 6. 대화 히스토리 조회
                    dialogue_history = await self.interaction_manager.get_dialogue_history(
                        npc_id, self.session_id, limit=5
                    )
                    
                    print(f"대화 히스토리 ({len(dialogue_history)}개 메시지)")
                    
    async def test_player_movement(self):
        """플레이어 이동을 테스트합니다."""
        print("\n플레이어 이동 테스트 시작...")
        
        # 1. 현재 위치 조회
        player_state = await self.entity_manager.get_entity_state(self.player_runtime_id)
        if player_state:
            current_position = player_state.get('current_position')
            print(f"현재 위치: {current_position}")
        
        # 2. 새로운 위치로 이동
        new_position = {"x": 60, "y": 0, "z": 60}
        success = await self.game_manager.move_player(self.test_cell_id, new_position)
        
        if success:
            print(f"플레이어 이동 성공: {new_position}")
            
            # 3. 업데이트된 위치 확인
            updated_state = await self.entity_manager.get_entity_state(self.player_runtime_id)
            if updated_state:
                updated_position = updated_state.get('current_position')
                print(f"업데이트된 위치: {updated_position}")
        else:
            print("플레이어 이동 실패")
        
        # 4. 범위 내 엔티티 검색 테스트
        entities_in_range = await self.cell_manager.find_entities_in_range(
            self.test_cell_id, new_position, range_distance=10.0
        )
        
        print(f"범위 내 엔티티 수: {len(entities_in_range)}")
        for entity in entities_in_range:
            print(f"  - {entity.get('entity_name', '알 수 없는 엔티티')} (거리: {entity.get('distance', 0):.2f})")
    
    async def cleanup_test(self):
        """테스트 정리"""
        if self.game_session:
            await self.game_session.end_session()
        
        if self.game_manager:
            await self.game_manager.end_game_session()
        
        print("테스트 정리 완료")

async def run_class_based_test():
    """클래스 기반 테스트 실행 함수"""
    scenario = ClassBasedGameScenarioTest()
    
    try:
        await scenario.setup_test_data()
        success = await scenario.run_scenario()
        
        if success:
            print("모든 클래스 기반 테스트가 성공적으로 완료되었습니다.")
        else:
            print("클래스 기반 테스트 중 오류가 발생했습니다.")
    
    finally:
        await scenario.cleanup_test()

if __name__ == "__main__":
    asyncio.run(run_class_based_test()) 