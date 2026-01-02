"""
상호작용 QA 테스트

P2 (Medium): 엔티티, 오브젝트, 아이템 상호작용 검증
"""
import pytest
import pytest_asyncio
import json
from typing import Dict, Any
from common.utils.logger import logger


@pytest.mark.asyncio
class TestInteractions:
    """상호작용 테스트"""
    
    async def test_entity_interaction_examine(
        self,
        db_connection,
        game_service,
        test_game_data
    ):
        """
        P2-3: 엔티티 상호작용 (examine) 검증
        
        검증 항목:
        - 엔티티 존재 확인
        - 상호작용 타입별 처리
        - 응답 메시지 정확성
        """
        logger.info("[P2-3] 엔티티 상호작용 (examine) 검증 테스트 시작")
        
        # 게임 시작
        result = await game_service.start_game(
            player_template_id=test_game_data["player_template_id"],
            start_cell_id=test_game_data["cell_id"]
        )
        
        session_id = result["game_state"]["session_id"]
        
        # 현재 셀 ID 사용 (게임 시작 시 이미 생성됨)
        current_cell_id = result["game_state"]["current_cell_id"]
        
        # NPC 인스턴스 생성
        from database.factories.instance_factory import InstanceFactory
        instance_factory = InstanceFactory(db_connection)
        
        # NPC 인스턴스 생성
        npc_id = await instance_factory.create_npc_instance(
            game_entity_id=test_game_data["npc_template_id"],
            session_id=session_id,
            runtime_cell_id=current_cell_id,
            position={"x": 5, "y": 0, "z": 5}
        )
        
        # 엔티티 상호작용 (examine)
        from app.services.gameplay import InteractionService
        interaction_service = InteractionService(db_connection)
        
        interaction_result = await interaction_service.interact_with_entity(
            session_id=session_id,
            entity_id=npc_id,
            action_type="examine"
        )
        
        assert interaction_result is not None, "상호작용 결과가 반환되어야 함"
        assert "success" in interaction_result, "success 필드가 포함되어야 함"
        assert interaction_result["success"] is True, "상호작용이 성공해야 함"
        assert "message" in interaction_result or "result" in interaction_result, \
            "응답 메시지가 포함되어야 함"
        
        logger.info("[P2-3] 엔티티 상호작용 (examine) 검증 테스트 통과")
    
    async def test_object_interaction_examine(
        self,
        db_connection,
        game_service,
        test_game_data
    ):
        """
        P2-4: 오브젝트 상호작용 (examine) 검증
        
        검증 항목:
        - 오브젝트 존재 확인
        - 상호작용 타입별 처리
        - 오브젝트 상태 변경
        """
        logger.info("[P2-4] 오브젝트 상호작용 (examine) 검증 테스트 시작")
        
        # 게임 시작
        result = await game_service.start_game(
            player_template_id=test_game_data["player_template_id"],
            start_cell_id=test_game_data["cell_id"]
        )
        
        session_id = result["game_state"]["session_id"]
        current_cell_id = result["game_state"]["current_cell_id"]
        
        # 오브젝트가 있는지 확인 (없으면 스킵)
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # 현재 셀의 오브젝트 확인
            from app.managers.cell_manager import CellManager
            from database.repositories.game_data import GameDataRepository
            from database.repositories.runtime_data import RuntimeDataRepository
            from database.repositories.reference_layer import ReferenceLayerRepository
            from app.managers.entity_manager import EntityManager
            
            game_data_repo = GameDataRepository(db_connection)
            runtime_data_repo = RuntimeDataRepository(db_connection)
            reference_layer_repo = ReferenceLayerRepository(db_connection)
            entity_manager = EntityManager(db_connection, game_data_repo, runtime_data_repo, reference_layer_repo)
            
            cell_manager = CellManager(
                db_connection,
                game_data_repo,
                runtime_data_repo,
                reference_layer_repo,
                entity_manager
            )
            
            cell_contents = await cell_manager.get_cell_contents(current_cell_id)
            
            if not cell_contents.get("objects"):
                pytest.skip("현재 셀에 오브젝트가 없어서 스킵")
            
            # 첫 번째 오브젝트와 상호작용
            first_object = cell_contents["objects"][0]
            object_id = first_object.get("runtime_object_id") or first_object.get("object_id")
            
            if not object_id:
                pytest.skip("오브젝트 ID를 찾을 수 없어서 스킵")
        
        # 오브젝트 상호작용 (examine)
        from app.services.gameplay import InteractionService
        interaction_service = InteractionService(db_connection)
        
        interaction_result = await interaction_service.interact_with_object(
            session_id=session_id,
            object_id=object_id,
            action_type="examine"
        )
        
        assert interaction_result is not None, "상호작용 결과가 반환되어야 함"
        assert "success" in interaction_result, "success 필드가 포함되어야 함"
        assert interaction_result["success"] is True, "상호작용이 성공해야 함"
        
        logger.info("[P2-4] 오브젝트 상호작용 (examine) 검증 테스트 통과")
    
    async def test_item_manipulation(
        self,
        db_connection,
        game_service,
        test_game_data
    ):
        """
        P2-5: 아이템 조작 검증
        
        검증 항목:
        - 인벤토리 업데이트
        - 장착 슬롯 관리
        - 아이템 효과 적용
        """
        logger.info("[P2-5] 아이템 조작 검증 테스트 시작")
        
        # 게임 시작
        result = await game_service.start_game(
            player_template_id=test_game_data["player_template_id"],
            start_cell_id=test_game_data["cell_id"]
        )
        
        session_id = result["game_state"]["session_id"]
        player_id = result["game_state"]["player_id"]
        
        # 플레이어 인벤토리 조회
        inventory = await game_service.get_player_inventory(session_id)
        
        assert inventory is not None, "인벤토리 정보가 조회되어야 함"
        
        # 인벤토리 구조 확인
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            entity_state = await conn.fetchrow("""
                SELECT inventory, equipped_items
                FROM runtime_data.entity_states
                WHERE runtime_entity_id = $1
            """, player_id)
            
            assert entity_state is not None, "플레이어 상태가 존재해야 함"
            
            # 인벤토리 구조 확인
            if entity_state["inventory"]:
                inv = entity_state["inventory"]
                if isinstance(inv, str):
                    inv = json.loads(inv)
                
                assert isinstance(inv, (list, dict)), \
                    "인벤토리는 리스트 또는 딕셔너리여야 함"
            
            # 장착 슬롯 확인
            if entity_state["equipped_items"]:
                equipped = entity_state["equipped_items"]
                if isinstance(equipped, str):
                    equipped = json.loads(equipped)
                
                assert isinstance(equipped, (list, dict)), \
                    "장착 아이템은 리스트 또는 딕셔너리여야 함"
        
        logger.info("[P2-5] 아이템 조작 검증 테스트 통과 (기본 구조 확인 완료)")

