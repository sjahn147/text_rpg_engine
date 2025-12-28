"""
엔티티-셀 상호작용 시나리오 테스트

목적:
- 엔티티가 셀에 진입/이탈하는 시나리오 검증
- 셀 내 엔티티 목록 조회 검증
- 엔티티 이동 시 DB 트랜잭션 무결성 검증
"""
import pytest
import pytest_asyncio
from typing import List
from common.utils.logger import logger


@pytest.mark.asyncio
class TestEntityCellInteraction:
    """엔티티-셀 상호작용 시나리오 테스트"""
    
    async def test_entity_enters_cell(self, db_with_templates, entity_manager, cell_manager, test_session):
        """
        시나리오: 엔티티가 셀에 진입
        1. 셀 생성
        2. 엔티티 생성
        3. 엔티티를 셀에 배치
        4. 셀 내 엔티티 목록에서 확인
        """
        session_id = test_session['session_id']
        
        # 1. 셀 생성
        cell_result = await cell_manager.create_cell(
            static_cell_id="CELL_SHOP_INTERIOR_001",
            session_id=session_id
        )
        assert cell_result.success
        cell_id = cell_result.cell.cell_id
        logger.info(f"[SCENARIO] Cell created: {cell_id}")
        
        # 2. 엔티티 생성
        entity_result = await entity_manager.create_entity(
            static_entity_id="NPC_VILLAGER_001",
            session_id=session_id,
            custom_position={"x": 5.0, "y": 5.0}
        )
        assert entity_result.status == "success"
        entity_id = entity_result.entity_id
        logger.info(f"[SCENARIO] Entity created: {entity_id}")
        
        # 3. 엔티티를 셀에 배치 (add_entity_to_cell)
        enter_result = await cell_manager.add_entity_to_cell(
            entity_id=entity_id,
            cell_id=cell_id
        )
        assert enter_result.success
        logger.info(f"[SCENARIO] Entity entered cell")
        
        # 4. 셀 컨텐츠 로드하여 엔티티 확인
        content_result = await cell_manager.load_cell_content(cell_id)
        assert content_result.success
        assert content_result.content is not None
        assert len(content_result.content.entities) > 0
        
        # 엔티티가 목록에 있는지 확인
        entity_found = False
        for entity in content_result.content.entities:
            if entity.entity_id == entity_id:
                entity_found = True
                break
        
        assert entity_found, f"Entity {entity_id} not found in cell {cell_id}"
        logger.info(f"[OK] Entity found in cell content")
    
    async def test_entity_moves_between_cells(self, db_with_templates, entity_manager, cell_manager, test_session):
        """
        시나리오: 엔티티가 셀 간 이동
        1. 두 개의 셀 생성 (A, B)
        2. 엔티티 생성 및 셀 A에 배치
        3. 엔티티를 셀 B로 이동
        4. 셀 A에서 엔티티가 제거되었는지 확인
        5. 셀 B에서 엔티티가 추가되었는지 확인
        """
        session_id = test_session['session_id']
        
        # 1. 두 개의 셀 생성
        cell_a_result = await cell_manager.create_cell(
            static_cell_id="CELL_SHOP_INTERIOR_001",
            session_id=session_id
        )
        assert cell_a_result.success
        cell_a_id = cell_a_result.cell.cell_id
        
        cell_b_result = await cell_manager.create_cell(
            static_cell_id="CELL_SHOP_INTERIOR_001",
            session_id=session_id
        )
        assert cell_b_result.success
        cell_b_id = cell_b_result.cell.cell_id
        logger.info(f"[SCENARIO] Two cells created: A={cell_a_id}, B={cell_b_id}")
        
        # 2. 엔티티 생성 및 셀 A에 배치
        entity_result = await entity_manager.create_entity(
            static_entity_id="NPC_VILLAGER_001",
            session_id=session_id
        )
        assert entity_result.status == "success"
        entity_id = entity_result.entity_id
        
        enter_a_result = await cell_manager.add_entity_to_cell(
            entity_id=entity_id,
            cell_id=cell_a_id
        )
        assert enter_a_result.success
        logger.info(f"[SCENARIO] Entity entered cell A")
        
        # 3. 엔티티를 셀 B로 이동
        move_result = await cell_manager.move_entity_between_cells(
            entity_id=entity_id,
            from_cell_id=cell_a_id,
            to_cell_id=cell_b_id,
            new_position={"x": 3.0, "y": 3.0}
        )
        assert move_result.success
        logger.info(f"[SCENARIO] Entity moved to cell B")
        
        # 4. 셀 A 확인 (엔티티 없어야 함)
        content_a = await cell_manager.load_cell_content(cell_a_id)
        assert content_a.success
        
        entity_in_a = False
        if content_a.content and content_a.content.entities:
            for entity in content_a.content.entities:
                if entity.entity_id == entity_id:
                    entity_in_a = True
                    break
        
        assert not entity_in_a, f"Entity should not be in cell A"
        logger.info(f"[OK] Entity not found in cell A")
        
        # 5. 셀 B 확인 (엔티티 있어야 함)
        content_b = await cell_manager.load_cell_content(cell_b_id)
        assert content_b.success
        
        entity_in_b = False
        if content_b.content and content_b.content.entities:
            for entity in content_b.content.entities:
                if entity.entity_id == entity_id:
                    entity_in_b = True
                    break
        
        assert entity_in_b, f"Entity should be in cell B"
        logger.info(f"[OK] Entity found in cell B")
    
    async def test_multiple_entities_in_cell(self, db_with_templates, entity_manager, cell_manager, test_session):
        """
        시나리오: 한 셀에 여러 엔티티 배치
        1. 셀 생성
        2. 3개 엔티티 생성 및 셀에 배치
        3. 셀 컨텐츠에서 모든 엔티티 확인
        """
        session_id = test_session['session_id']
        
        # 1. 셀 생성
        cell_result = await cell_manager.create_cell(
            static_cell_id="CELL_SHOP_INTERIOR_001",
            session_id=session_id
        )
        assert cell_result.success
        cell_id = cell_result.cell.cell_id
        logger.info(f"[SCENARIO] Cell created")
        
        # 2. 3개 엔티티 생성 및 배치
        entity_ids = []
        templates = ["NPC_VILLAGER_001", "NPC_MERCHANT_001", "NPC_GOBLIN_001"]
        
        for idx, template in enumerate(templates):
            entity_result = await entity_manager.create_entity(
                static_entity_id=template,
                session_id=session_id,
                custom_position={"x": float(idx * 2), "y": float(idx * 2)}
            )
            assert entity_result.status == "success"
            entity_id = entity_result.entity_id
            entity_ids.append(entity_id)
            
            enter_result = await cell_manager.add_entity_to_cell(
                entity_id=entity_id,
                cell_id=cell_id
            )
            assert enter_result.success
            logger.info(f"[SCENARIO] Entity {idx+1} entered cell")
        
        # 3. 셀 컨텐츠 확인
        content_result = await cell_manager.load_cell_content(cell_id)
        assert content_result.success
        assert content_result.content is not None
        
        # 모든 엔티티가 셀에 있는지 확인
        found_entities = []
        if content_result.content.entities:
            for entity in content_result.content.entities:
                if entity.entity_id in entity_ids:
                    found_entities.append(entity.entity_id)
        
        assert len(found_entities) == len(entity_ids), \
            f"Expected {len(entity_ids)} entities, found {len(found_entities)}"
        logger.info(f"[OK] All {len(entity_ids)} entities found in cell")
    
    async def test_entity_leaves_cell(self, db_with_templates, entity_manager, cell_manager, test_session):
        """
        시나리오: 엔티티가 셀에서 나감
        1. 셀 생성 및 엔티티 배치
        2. 엔티티가 셀을 떠남 (leave_cell)
        3. 셀 컨텐츠에서 엔티티가 없는지 확인
        """
        session_id = test_session['session_id']
        
        # 1. 셀 생성 및 엔티티 배치
        cell_result = await cell_manager.create_cell(
            static_cell_id="CELL_SHOP_INTERIOR_001",
            session_id=session_id
        )
        assert cell_result.success
        cell_id = cell_result.cell.cell_id
        
        entity_result = await entity_manager.create_entity(
            static_entity_id="NPC_VILLAGER_001",
            session_id=session_id
        )
        assert entity_result.status == "success"
        entity_id = entity_result.entity_id
        
        enter_result = await cell_manager.add_entity_to_cell(
            entity_id=entity_id,
            cell_id=cell_id
        )
        assert enter_result.success
        logger.info(f"[SCENARIO] Entity entered cell")
        
        # 2. 엔티티가 셀을 떠남
        leave_result = await cell_manager.remove_entity_from_cell(
            entity_id=entity_id,
            cell_id=cell_id
        )
        assert leave_result.success
        logger.info(f"[SCENARIO] Entity left cell")
        
        # 3. 셀 컨텐츠 확인
        content_result = await cell_manager.load_cell_content(cell_id)
        assert content_result.success
        
        entity_found = False
        if content_result.content and content_result.content.entities:
            for entity in content_result.content.entities:
                if entity.entity_id == entity_id:
                    entity_found = True
                    break
        
        assert not entity_found, f"Entity should not be in cell after leaving"
        logger.info(f"[OK] Entity not found in cell after leaving")

