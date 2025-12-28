"""
Cell Manager 실제 DB 통합 테스트
"""

import pytest
import pytest_asyncio
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from app.world.cell_manager import CellManager, CellData, CellType, CellStatus, CellResult, CellContent
from app.entity.entity_manager import EntityManager, EntityData, EntityType, EntityStatus, EntityResult
from app.effect_carrier.effect_carrier_manager import EffectCarrierManager, EffectCarrierData, EffectCarrierType, EffectCarrierResult
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from common.utils.logger import logger

class TestCellManagerDBIntegration:
    """Cell Manager 실제 DB 통합 테스트"""
    
    @pytest_asyncio.fixture
    async def db_connection(self):
        """실제 DB 연결"""
        db = DatabaseConnection()
        try:
            await db.pool
            logger.info("실제 DB 연결 성공")
            return db
        except Exception as e:
            logger.error(f"실제 DB 연결 실패: {str(e)}")
            pytest.skip("DB 연결 실패")
    
    @pytest_asyncio.fixture
    async def repositories(self, db_connection):
        """리포지토리 인스턴스들"""
        return {
            'game_data_repo': GameDataRepository(db_connection),
            'runtime_data_repo': RuntimeDataRepository(db_connection),
            'reference_layer_repo': ReferenceLayerRepository(db_connection)
        }
    
    @pytest_asyncio.fixture
    async def effect_carrier_manager(self, db_connection, repositories):
        """Effect Carrier Manager 인스턴스"""
        return EffectCarrierManager(
            db_connection,
            repositories['game_data_repo'],
            repositories['runtime_data_repo'],
            repositories['reference_layer_repo']
        )
    
    @pytest_asyncio.fixture
    async def entity_manager(self, db_connection, repositories, effect_carrier_manager):
        """Entity Manager 인스턴스"""
        return EntityManager(
            db_connection,
            repositories['game_data_repo'],
            repositories['runtime_data_repo'],
            repositories['reference_layer_repo'],
            effect_carrier_manager
        )
    
    @pytest_asyncio.fixture
    async def cell_manager(self, db_connection, repositories, entity_manager, effect_carrier_manager):
        """Cell Manager 인스턴스"""
        return CellManager(
            db_connection,
            repositories['game_data_repo'],
            repositories['runtime_data_repo'],
            repositories['reference_layer_repo'],
            entity_manager,
            effect_carrier_manager
        )
    
    @pytest.mark.asyncio
    async def test_cell_creation_with_db(self, cell_manager):
        """실제 DB를 통한 셀 생성 테스트"""
        # Given
        name = "Test Cell DB"
        cell_type = CellType.INDOOR
        location_id = "test-location-001"
        description = "A test cell for database integration"
        properties = {"lighting": "bright", "temperature": "comfortable"}
        size = {"width": 25, "height": 30}
        
        # When
        result = await cell_manager.create_cell(
            name=name,
            cell_type=cell_type,
            location_id=location_id,
            description=description,
            properties=properties,
            size=size
        )
        
        # Then
        assert result.success, f"셀 생성 실패: {result.message}"
        assert result.cell is not None
        assert result.cell.name == name
        assert result.cell.cell_type == cell_type
        assert result.cell.location_id == location_id
        assert result.cell.description == description
        assert result.cell.properties == properties
        assert result.cell.size == size
        
        # 생성된 셀 ID 저장
        cell_id = result.cell.cell_id
        logger.info(f"셀 생성 성공: {cell_id}")
        
        return cell_id
    
    @pytest.mark.asyncio
    async def test_cell_retrieval_with_db(self, cell_manager):
        """실제 DB를 통한 셀 조회 테스트"""
        # Given - 셀 생성
        cell_id = await self.test_cell_creation_with_db(cell_manager)
        
        # When
        result = await cell_manager.get_cell(cell_id)
        
        # Then
        assert result.success, f"셀 조회 실패: {result.message}"
        assert result.cell is not None
        assert result.cell.cell_id == cell_id
        assert result.cell.name == "Test Cell DB"
        
        logger.info(f"셀 조회 성공: {cell_id}")
    
    @pytest.mark.asyncio
    async def test_cell_update_with_db(self, cell_manager):
        """실제 DB를 통한 셀 업데이트 테스트"""
        # Given - 셀 생성
        cell_id = await self.test_cell_creation_with_db(cell_manager)
        
        # When - 셀 업데이트
        updates = {
            "properties": {"lighting": "dim", "temperature": "cold", "atmosphere": "mysterious"},
            "description": "Updated test cell description"
        }
        result = await cell_manager.update_cell(cell_id, updates)
        
        # Then
        assert result.success, f"셀 업데이트 실패: {result.message}"
        assert result.cell is not None
        assert result.cell.properties["lighting"] == "dim"
        assert result.cell.properties["temperature"] == "cold"
        assert result.cell.description == "Updated test cell description"
        
        logger.info(f"셀 업데이트 성공: {cell_id}")
    
    @pytest.mark.asyncio
    async def test_cell_deletion_with_db(self, cell_manager):
        """실제 DB를 통한 셀 삭제 테스트"""
        # Given - 셀 생성
        cell_id = await self.test_cell_creation_with_db(cell_manager)
        
        # When
        result = await cell_manager.delete_cell(cell_id)
        
        # Then
        assert result.success, f"셀 삭제 실패: {result.message}"
        
        # 삭제된 셀 조회 시 실패해야 함
        get_result = await cell_manager.get_cell(cell_id)
        assert not get_result.success, "삭제된 셀이 여전히 존재함"
        
        logger.info(f"셀 삭제 성공: {cell_id}")
    
    @pytest.mark.asyncio
    async def test_cell_content_loading_with_db(self, cell_manager, entity_manager):
        """실제 DB를 통한 셀 컨텐츠 로딩 테스트"""
        # Given - 셀 생성
        cell_id = await self.test_cell_creation_with_db(cell_manager)
        
        # 엔티티 생성 및 셀에 배치
        entity_result = await entity_manager.create_entity(
            name="Test NPC",
            entity_type=EntityType.NPC,
            properties={"health": 100, "level": 5},
            position={"x": 10.0, "y": 15.0}
        )
        assert entity_result.success
        entity_id = entity_result.entity.entity_id
        
        # When - 셀 컨텐츠 로딩
        content_result = await cell_manager.load_cell_content(cell_id)
        
        # Then
        assert content_result.success, f"셀 컨텐츠 로딩 실패: {content_result.message}"
        assert content_result.data is not None
        assert isinstance(content_result.data, CellContent)
        
        logger.info(f"셀 컨텐츠 로딩 성공: {cell_id}")
    
    @pytest.mark.asyncio
    async def test_cell_enter_leave_with_db(self, cell_manager, entity_manager):
        """실제 DB를 통한 셀 진입/떠나기 테스트"""
        # Given - 셀과 엔티티 생성
        cell_id = await self.test_cell_creation_with_db(cell_manager)
        
        entity_result = await entity_manager.create_entity(
            name="Test Player",
            entity_type=EntityType.PLAYER,
            properties={"health": 100, "level": 1},
            position={"x": 5.0, "y": 5.0}
        )
        assert entity_result.success
        entity_id = entity_result.entity.entity_id
        
        # When - 셀 진입
        enter_result = await cell_manager.enter_cell(cell_id, entity_id)
        
        # Then
        assert enter_result.success, f"셀 진입 실패: {enter_result.message}"
        assert enter_result.cell is not None
        assert enter_result.cell.cell_id == cell_id
        
        # 셀 떠나기
        leave_result = await cell_manager.leave_cell(cell_id, entity_id)
        assert leave_result.success, f"셀 떠나기 실패: {leave_result.message}"
        
        logger.info(f"셀 진입/떠나기 성공: {cell_id} -> {entity_id}")
    
    @pytest.mark.asyncio
    async def test_cell_list_with_db(self, cell_manager):
        """실제 DB를 통한 셀 목록 조회 테스트"""
        # Given - 여러 셀 생성
        cell_ids = []
        for i in range(3):
            cell_id = await self.test_cell_creation_with_db(cell_manager)
            cell_ids.append(cell_id)
        
        # When
        result = await cell_manager.list_cells()
        
        # Then
        assert result.success, f"셀 목록 조회 실패: {result.message}"
        assert result.data is not None
        assert len(result.data) >= 3
        
        # 생성된 셀들이 목록에 있는지 확인
        cell_names = [cell.name for cell in result.data]
        assert "Test Cell DB" in cell_names
        
        logger.info(f"셀 목록 조회 성공: {len(result.data)}개 셀")
    
    @pytest.mark.asyncio
    async def test_cell_list_with_filters_with_db(self, cell_manager):
        """실제 DB를 통한 필터링된 셀 목록 조회 테스트"""
        # Given - 여러 셀 생성
        cell_ids = []
        for i in range(3):
            cell_id = await self.test_cell_creation_with_db(cell_manager)
            cell_ids.append(cell_id)
        
        # When - INDOOR 타입으로 필터링
        result = await cell_manager.list_cells(cell_type=CellType.INDOOR)
        
        # Then
        assert result.success, f"필터링된 셀 목록 조회 실패: {result.message}"
        assert result.data is not None
        
        # 모든 셀이 INDOOR 타입인지 확인
        for cell in result.data:
            assert cell.cell_type == CellType.INDOOR
        
        logger.info(f"필터링된 셀 목록 조회 성공: {len(result.data)}개 INDOOR 셀")
    
    @pytest.mark.asyncio
    async def test_cell_cache_consistency_with_db(self, cell_manager):
        """실제 DB를 통한 셀 캐시 일관성 테스트"""
        # Given - 셀 생성
        cell_id = await self.test_cell_creation_with_db(cell_manager)
        
        # When - 캐시에서 조회
        result1 = await cell_manager.get_cell(cell_id)
        result2 = await cell_manager.get_cell(cell_id)
        
        # Then
        assert result1.success and result2.success
        assert result1.cell.cell_id == result2.cell.cell_id
        assert result1.cell.name == result2.cell.name
        
        # 캐시 초기화 후 다시 조회
        await cell_manager.clear_cache()
        result3 = await cell_manager.get_cell(cell_id)
        
        assert result3.success
        assert result3.cell.cell_id == cell_id
        
        logger.info(f"셀 캐시 일관성 테스트 성공: {cell_id}")
    
    @pytest.mark.asyncio
    async def test_cell_error_handling_with_db(self, cell_manager):
        """실제 DB를 통한 셀 에러 처리 테스트"""
        # Given - 존재하지 않는 셀 ID
        non_existent_id = "non-existent-cell-id"
        
        # When
        result = await cell_manager.get_cell(non_existent_id)
        
        # Then
        assert not result.success, "존재하지 않는 셀 조회가 성공함"
        assert "찾을 수 없습니다" in result.message
        
        logger.info(f"셀 에러 처리 테스트 성공: {non_existent_id}")
    
    @pytest.mark.asyncio
    async def test_cell_entity_placement_with_db(self, cell_manager, entity_manager):
        """실제 DB를 통한 셀-엔티티 배치 테스트"""
        # Given - 셀과 엔티티 생성
        cell_id = await self.test_cell_creation_with_db(cell_manager)
        
        entity_result = await entity_manager.create_entity(
            name="Test NPC",
            entity_type=EntityType.NPC,
            properties={"health": 100, "level": 5},
            position={"x": 10.0, "y": 15.0}
        )
        assert entity_result.success
        entity_id = entity_result.entity.entity_id
        
        # When - 엔티티를 셀에 배치
        placement_result = await cell_manager.place_entity_in_cell(cell_id, entity_id, {"x": 10.0, "y": 15.0})
        
        # Then
        assert placement_result.success, f"엔티티 배치 실패: {placement_result.message}"
        
        # 셀 컨텐츠에서 엔티티 확인
        content_result = await cell_manager.load_cell_content(cell_id)
        assert content_result.success
        assert len(content_result.data.entities) >= 1
        
        logger.info(f"셀-엔티티 배치 성공: {cell_id} -> {entity_id}")
    
    @pytest.mark.asyncio
    async def test_cell_size_management_with_db(self, cell_manager):
        """실제 DB를 통한 셀 크기 관리 테스트"""
        # Given - 셀 생성
        cell_id = await self.test_cell_creation_with_db(cell_manager)
        
        # When - 셀 크기 업데이트
        new_size = {"width": 50, "height": 40}
        result = await cell_manager.update_cell(cell_id, {"size": new_size})
        
        # Then
        assert result.success, f"셀 크기 업데이트 실패: {result.message}"
        assert result.cell.size == new_size
        
        logger.info(f"셀 크기 관리 성공: {cell_id} -> {new_size}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
