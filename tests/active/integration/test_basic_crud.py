"""
기본 CRUD 작업 테스트
엔티티와 셀의 생성, 조회, 수정, 삭제를 검증
"""
import pytest
import pytest_asyncio
from common.utils.logger import logger


class TestBasicCRUD:
    """기본 CRUD 작업 테스트 클래스"""
    
    @pytest.mark.asyncio
    async def test_entity_lifecycle(self, db_with_templates, entity_manager, test_session):
        """엔티티 생명주기 테스트: 생성 → 조회 → 수정 → 삭제"""
        session_id = test_session['session_id']
        
        # 1. 생성 (Create)
        create_result = await entity_manager.create_entity(
            static_entity_id="NPC_VILLAGER_001",
            session_id=session_id
        )
        assert create_result.status == "success"
        entity_id = create_result.entity_id
        logger.info(f"[OK] Entity created: {entity_id}")
        
        # 2. 조회 (Read)
        entity_result = await entity_manager.get_entity(entity_id)
        assert entity_result.success
        assert entity_result.entity is not None
        assert entity_result.entity.entity_id == entity_id
        logger.info(f"[OK] Entity retrieved: {entity_result.entity.name}")
        
        # 3. 수정 (Update)
        update_result = await entity_manager.update_entity(
            entity_id=entity_id,
            updates={"custom_properties": {"mood": "very_happy"}}
        )
        assert update_result is not None
        logger.info(f"[OK] Entity updated")
        
        # 4. 삭제 (Delete)
        delete_result = await entity_manager.delete_entity(entity_id)
        assert delete_result.success
        logger.info(f"[OK] Entity deleted")
        
        # 5. 삭제 확인 (상태가 INACTIVE로 변경됨)
        get_result = await entity_manager.get_entity(entity_id)
        assert not get_result.success or get_result.entity.status == "inactive"
        logger.info(f"[OK] Entity deletion confirmed")
    
    @pytest.mark.asyncio
    async def test_cell_lifecycle(self, db_with_templates, cell_manager, test_session):
        """셀 생명주기 테스트: 생성 → 로딩 → 수정 → 삭제"""
        session_id = test_session['session_id']
        
        # 1. 생성 (Create)
        create_result = await cell_manager.create_cell(
            static_cell_id="CELL_SHOP_INTERIOR_001",
            session_id=session_id
        )
        assert create_result.cell is not None
        cell_id = create_result.cell.cell_id
        logger.info(f"[OK] Cell created: {cell_id}")
        
        # 2. 로딩 (Read)
        cell_result = await cell_manager.get_cell(cell_id)
        assert cell_result.success
        assert cell_result.cell is not None
        assert cell_result.cell.cell_id == cell_id
        logger.info(f"[OK] Cell loaded: {cell_result.cell.name}")
        
        # 3. 수정 (Update) - 셀 속성 변경
        update_result = await cell_manager.update_cell(
            cell_id=cell_id,
            updates={"weather": "rainy"}
        )
        assert update_result.success
        logger.info(f"[OK] Cell updated")
        
        # 4. 삭제 (Delete)
        delete_result = await cell_manager.delete_cell(cell_id)
        assert delete_result.success
        logger.info(f"[OK] Cell deleted")
    
    @pytest.mark.asyncio
    async def test_multiple_entities_crud(self, db_with_templates, entity_manager, test_session):
        """여러 엔티티 동시 CRUD 테스트"""
        session_id = test_session['session_id']
        entity_ids = []
        
        # 여러 엔티티 생성
        for template in ["NPC_VILLAGER_001", "NPC_MERCHANT_001"]:
            result = await entity_manager.create_entity(
                static_entity_id=template,
                session_id=session_id
            )
            assert result.status == "success"
            entity_ids.append(result.entity_id)
            logger.info(f"[OK] Created entity from template {template}")
        
        # 모든 엔티티 조회
        for entity_id in entity_ids:
            entity = await entity_manager.get_entity(entity_id)
            assert entity is not None
        
        logger.info(f"[OK] All {len(entity_ids)} entities retrieved successfully")
    
    @pytest.mark.asyncio
    async def test_entity_custom_properties(self, db_with_templates, entity_manager, test_session):
        """커스텀 속성을 가진 엔티티 생성 테스트"""
        session_id = test_session['session_id']
        
        # 커스텀 속성으로 엔티티 생성
        result = await entity_manager.create_entity(
            static_entity_id="NPC_VILLAGER_001",
            session_id=session_id,
            custom_properties={"special_skill": "farming", "mood": "excited"}
        )
        
        assert result.status == "success"
        entity_result = await entity_manager.get_entity(result.entity_id)
        assert entity_result.success
        assert entity_result.entity.properties.get("special_skill") == "farming"
        logger.info(f"[OK] Entity with custom properties created")

