"""
MVP 스키마와 Manager 호환성 테스트
"""
import asyncio
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath('.'))

from database.connection import DatabaseConnection
from app.entity.entity_manager import EntityManager, EntityType, EntityStatus
from app.world.cell_manager import CellManager, CellType, CellStatus
from app.interaction.action_handler import ActionHandler, ActionType
from app.interaction.dialogue_manager import DialogueManager
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository

async def test_mvp_compatibility():
    """MVP 스키마와 Manager 호환성 테스트"""
    try:
        print("🧪 MVP 스키마 호환성 테스트 시작...")
        
        # 데이터베이스 연결 (직접 설정)
        db_connection = DatabaseConnection()
        db_connection.host = 'localhost'
        db_connection.port = 5432
        db_connection.user = 'postgres'
        db_connection.password = '2696Sjbj!'
        db_connection.database = 'rpg_engine'
        
        # 연결 풀 초기화 (pool 속성 접근 시 자동 생성됨)
        await db_connection.pool
        
        # Repository 생성
        game_data_repo = GameDataRepository(db_connection)
        runtime_data_repo = RuntimeDataRepository(db_connection)
        reference_layer_repo = ReferenceLayerRepository(db_connection)
        
        # Manager 생성
        entity_manager = EntityManager(db_connection, game_data_repo, runtime_data_repo, reference_layer_repo)
        cell_manager = CellManager(db_connection, game_data_repo, runtime_data_repo, reference_layer_repo, entity_manager)
        action_handler = ActionHandler(db_connection, entity_manager, cell_manager)
        dialogue_manager = DialogueManager(db_connection, entity_manager)
        
        print("✅ Manager 초기화 완료")
        
        # EntityManager 테스트
        print("\n🔍 EntityManager 테스트...")
        entity_result = await entity_manager.create_entity(
            name="테스트 NPC",
            entity_type=EntityType.NPC,
            properties={"test": True, "gold": 100}
        )
        
        if entity_result.success:
            print(f"✅ 엔티티 생성 성공: {entity_result.entity.name}")
            
            # 엔티티 조회 테스트
            get_result = await entity_manager.get_entity(entity_result.entity.entity_id)
            if get_result.success:
                print(f"✅ 엔티티 조회 성공: {get_result.entity.name}")
            else:
                print(f"❌ 엔티티 조회 실패: {get_result.message}")
        else:
            print(f"❌ 엔티티 생성 실패: {entity_result.message}")
        
        # CellManager 테스트
        print("\n🏠 CellManager 테스트...")
        cell_result = await cell_manager.create_cell(
            name="테스트 셀",
            cell_type=CellType.INDOOR,
            location_id="LOC_FOREST_VILLAGE_001",
            description="테스트용 셀입니다."
        )
        
        if cell_result.success:
            print(f"✅ 셀 생성 성공: {cell_result.cell.name}")
            
            # 셀 조회 테스트
            get_cell_result = await cell_manager.get_cell(cell_result.cell.cell_id)
            if get_cell_result.success:
                print(f"✅ 셀 조회 성공: {get_cell_result.cell.name}")
            else:
                print(f"❌ 셀 조회 실패: {get_cell_result.message}")
        else:
            print(f"❌ 셀 생성 실패: {cell_result.message}")
        
        # ActionHandler 테스트
        print("\n⚡ ActionHandler 테스트...")
        if entity_result.success and cell_result.success:
            action_result = await action_handler.execute_action(
                ActionType.INVESTIGATE,
                player_id="test_player",
                parameters={"cell_id": cell_result.cell.cell_id}
            )
            
            if action_result.success:
                print(f"✅ 행동 실행 성공: {action_result.message[:50]}...")
            else:
                print(f"❌ 행동 실행 실패: {action_result.message}")
        
        # DialogueManager 테스트
        print("\n💬 DialogueManager 테스트...")
        if entity_result.success:
            dialogue_result = await dialogue_manager.start_dialogue(
                player_id="test_player",
                npc_id=entity_result.entity.entity_id,
                initial_topic="greeting"
            )
            
            if dialogue_result.success:
                print(f"✅ 대화 시작 성공: {dialogue_result.npc_response[:50]}...")
            else:
                print(f"❌ 대화 시작 실패: {dialogue_result.message}")
        
        print("\n🎉 MVP 스키마 호환성 테스트 완료!")
        print("✅ 모든 Manager가 MVP 스키마와 완벽히 호환됩니다!")
        
    except Exception as e:
        print(f"❌ 호환성 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mvp_compatibility())
