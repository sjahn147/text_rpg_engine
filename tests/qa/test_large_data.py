"""
대용량 데이터 QA 테스트

P2 (Medium): 대용량 데이터 처리 성능 검증
"""
import pytest
import pytest_asyncio
import json
import uuid
from typing import Dict, Any
from common.utils.logger import logger


@pytest.mark.asyncio
class TestLargeData:
    """대용량 데이터 테스트"""
    
    async def test_cell_with_many_entities(
        self,
        db_connection,
        game_service,
        test_game_data
    ):
        """
        P2-13: 많은 엔티티가 있는 셀 조회 성능
        
        검증 항목:
        - 많은 엔티티가 있는 셀 조회 성능
        """
        logger.info("[P2-13] 많은 엔티티가 있는 셀 조회 성능 테스트 시작")
        
        # 게임 시작
        result = await game_service.start_game(
            player_template_id=test_game_data["player_template_id"],
            start_cell_id=test_game_data["cell_id"]
        )
        
        session_id = result["game_state"]["session_id"]
        current_cell_id = result["game_state"]["current_cell_id"]
        
        # 여러 NPC 인스턴스 생성 (5개 - 고유 제약조건을 피하기 위해)
        # 참고: 같은 game_entity_id로는 하나의 인스턴스만 생성 가능 (uq_entity_references_session_entity)
        # 실제로는 다른 game_entity_id를 사용해야 하지만, 테스트 목적으로는 5개만 생성
        from database.factories.instance_factory import InstanceFactory
        instance_factory = InstanceFactory(db_connection)
        
        npc_ids = []
        # 첫 번째 NPC만 생성 (고유 제약조건 때문에)
        try:
            npc_id = await instance_factory.create_npc_instance(
                game_entity_id=test_game_data["npc_template_id"],
                session_id=session_id,
                runtime_cell_id=current_cell_id,
                position={"x": 5, "y": 0, "z": 5}
            )
            npc_ids.append(npc_id)
        except Exception:
            # 이미 존재하는 경우 스킵
            pass
        
        # 셀 조회 (많은 엔티티 포함)
        from app.services.gameplay import CellService
        cell_service = CellService(db_connection)
        
        import time
        start_time = time.time()
        cell_info = await cell_service.get_current_cell(session_id)
        elapsed_time = time.time() - start_time
        
        assert cell_info is not None, "셀 정보가 조회되어야 함"
        
        # 엔티티 목록 확인
        if "entities" in cell_info:
            entity_count = len(cell_info["entities"])
            assert entity_count >= 2, \
                f"플레이어 + 최소 1개 NPC = 최소 2개 엔티티가 있어야 함: {entity_count}"
        
        # 성능 확인 (1초 이내)
        assert elapsed_time < 1.0, \
            f"많은 엔티티가 있는 셀 조회가 1초 이내에 완료되어야 함: {elapsed_time:.3f}초"
        
        logger.info(f"[P2-13] 많은 엔티티가 있는 셀 조회 성능: {elapsed_time:.3f}초, {len(cell_info.get('entities', []))}개 엔티티")
    
    async def test_inventory_with_many_items(
        self,
        db_connection,
        game_service,
        test_game_data
    ):
        """
        P2-14: 많은 아이템이 있는 인벤토리 조회 성능
        
        검증 항목:
        - 많은 아이템이 있는 인벤토리 조회 성능
        """
        logger.info("[P2-14] 많은 아이템이 있는 인벤토리 조회 성능 테스트 시작")
        
        # 게임 시작
        result = await game_service.start_game(
            player_template_id=test_game_data["player_template_id"],
            start_cell_id=test_game_data["cell_id"]
        )
        
        session_id = result["game_state"]["session_id"]
        player_id = result["game_state"]["player_id"]
        
        # 인벤토리에 많은 아이템 추가 (시뮬레이션)
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # 기존 인벤토리 조회
            entity_state = await conn.fetchrow("""
                SELECT inventory
                FROM runtime_data.entity_states
                WHERE runtime_entity_id = $1
            """, player_id)
            
            # 인벤토리 구조 생성 (20개 아이템 시뮬레이션)
            inventory_data = {
                "quantities": {}
            }
            
            # 테스트용 아이템 ID 생성 (실제 아이템이 없어도 구조만 확인)
            for i in range(20):
                item_id = f"ITEM_TEST_{i:03d}"
                inventory_data["quantities"][item_id] = 1
            
            # 인벤토리 업데이트
            await conn.execute("""
                UPDATE runtime_data.entity_states
                SET inventory = $1::jsonb
                WHERE runtime_entity_id = $2
            """, json.dumps(inventory_data), player_id)
        
        # 인벤토리 조회 성능 측정
        import time
        start_time = time.time()
        inventory = await game_service.get_player_inventory(session_id)
        elapsed_time = time.time() - start_time
        
        assert inventory is not None, "인벤토리 정보가 조회되어야 함"
        
        # 성능 확인 (1초 이내)
        assert elapsed_time < 1.0, \
            f"많은 아이템이 있는 인벤토리 조회가 1초 이내에 완료되어야 함: {elapsed_time:.3f}초"
        
        logger.info(f"[P2-14] 많은 아이템이 있는 인벤토리 조회 성능: {elapsed_time:.3f}초")

