"""
셀 이동 시나리오 테스트
엔티티 셀 배치, 셀 간 이동, 셀 내 상호작용 테스트
"""

import pytest
import pytest_asyncio
import asyncio
from typing import Dict, Any, List
from database.connection import DatabaseConnection
from app.entity.entity_manager import EntityManager
from app.world.cell_manager import CellManager
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from common.utils.logger import logger

class TestCellMovementScenarios:
    """셀 이동 시나리오 테스트"""
    
    @pytest_asyncio.fixture
    async def db_connection(self):
        """데이터베이스 연결 픽스처"""
        db = DatabaseConnection()
        await db.pool
        yield db
        await db.close()
    
    @pytest_asyncio.fixture
    async def managers(self, db_connection):
        """Manager 클래스들 픽스처"""
        game_data_repo = GameDataRepository(db_connection)
        runtime_data_repo = RuntimeDataRepository(db_connection)
        reference_layer_repo = ReferenceLayerRepository(db_connection)
        
        entity_manager = EntityManager(db_connection, game_data_repo, runtime_data_repo, reference_layer_repo)
        cell_manager = CellManager(db_connection, game_data_repo, runtime_data_repo, reference_layer_repo, entity_manager)
        
        return {
            'entity_manager': entity_manager,
            'cell_manager': cell_manager
        }
    
    @pytest.mark.asyncio
    async def test_entity_cell_placement_scenario(self, managers):
        """엔티티 셀 배치 시나리오"""
        logger.info("🎮 시나리오 13: 엔티티 셀 배치")
        
        # 1. 플레이어 엔티티 생성
        player_result = await managers['entity_manager'].create_entity(
            name="탐험가 플레이어",
            entity_type="player",
            properties={"level": 3, "hp": 100, "mp": 60, "gold": 300}
        )
        
        assert player_result.success, f"플레이어 생성 실패: {player_result.message}"
        player_id = player_result.entity.entity_id
        logger.info(f"✅ 탐험가 플레이어 생성 완료: {player_id}")
        
        # 2. 셀 생성
        cell_result = await managers['cell_manager'].create_cell(
            name="숲의 입구",
            cell_type="outdoor",
            location_id="LOC_FOREST_VILLAGE_001",
            description="신비로운 숲으로 들어가는 입구"
        )
        
        assert cell_result.success, f"셀 생성 실패: {cell_result.message}"
        cell_id = cell_result.cell.cell_id
        logger.info(f"✅ 숲의 입구 셀 생성 완료: {cell_id}")
        
        # 3. 플레이어를 셀에 배치
        # TODO: Cell Manager의 place_entity_in_cell 메서드 구현 후 테스트
        logger.info("⚠️ 엔티티 셀 배치는 Cell Manager 구현 후 테스트 예정")
        
        # 4. 정리
        await managers['entity_manager'].delete_entity(player_id)
        await managers['cell_manager'].delete_cell(cell_id)
        logger.info("✅ 정리 완료")
    
    @pytest.mark.asyncio
    async def test_cell_to_cell_movement_scenario(self, managers):
        """셀 간 이동 시나리오"""
        logger.info("🎮 시나리오 14: 셀 간 이동")
        
        # 1. 플레이어 엔티티 생성
        player_result = await managers['entity_manager'].create_entity(
            name="모험가 플레이어",
            entity_type="player",
            properties={"level": 4, "hp": 120, "mp": 80, "gold": 500}
        )
        
        assert player_result.success, f"플레이어 생성 실패: {player_result.message}"
        player_id = player_result.entity.entity_id
        logger.info(f"✅ 모험가 플레이어 생성 완료: {player_id}")
        
        # 2. 두 개의 셀 생성
        cell1_result = await managers['cell_manager'].create_cell(
            name="마을 광장",
            cell_type="outdoor",
            location_id="LOC_FOREST_VILLAGE_001",
            description="평화로운 마을의 중심 광장"
        )
        
        cell2_result = await managers['cell_manager'].create_cell(
            name="상점 내부",
            cell_type="indoor",
            location_id="LOC_FOREST_VILLAGE_001",
            description="다양한 물건들이 진열된 상점"
        )
        
        assert cell1_result.success and cell2_result.success, "셀 생성 실패"
        cell1_id = cell1_result.cell.cell_id
        cell2_id = cell2_result.cell.cell_id
        
        logger.info(f"✅ 두 셀 생성 완료: {cell1_id}, {cell2_id}")
        
        # 3. 셀 간 이동 테스트
        # TODO: Cell Manager의 move_entity_to_cell 메서드 구현 후 테스트
        logger.info("⚠️ 셀 간 이동은 Cell Manager 구현 후 테스트 예정")
        
        # 4. 정리
        await managers['entity_manager'].delete_entity(player_id)
        await managers['cell_manager'].delete_cell(cell1_id)
        await managers['cell_manager'].delete_cell(cell2_id)
        logger.info("✅ 정리 완료")
    
    @pytest.mark.asyncio
    async def test_multiple_entities_in_cell_scenario(self, managers):
        """셀 내 다중 엔티티 시나리오"""
        logger.info("🎮 시나리오 15: 셀 내 다중 엔티티")
        
        # 1. 여러 엔티티 생성
        player_result = await managers['entity_manager'].create_entity(
            name="플레이어",
            entity_type="player",
            properties={"level": 5, "hp": 150, "mp": 100, "gold": 800}
        )
        
        npc1_result = await managers['entity_manager'].create_entity(
            name="상인",
            entity_type="npc",
            properties={"level": 3, "hp": 80, "mp": 40, "gold": 1000}
        )
        
        npc2_result = await managers['entity_manager'].create_entity(
            name="수호자",
            entity_type="npc",
            properties={"level": 7, "hp": 200, "mp": 60, "gold": 200}
        )
        
        assert all([player_result.success, npc1_result.success, npc2_result.success]), "엔티티 생성 실패"
        
        player_id = player_result.entity.entity_id
        npc1_id = npc1_result.entity.entity_id
        npc2_id = npc2_result.entity.entity_id
        
        logger.info(f"✅ 세 엔티티 생성 완료: {player_id}, {npc1_id}, {npc2_id}")
        
        # 2. 셀 생성
        cell_result = await managers['cell_manager'].create_cell(
            name="마을 광장",
            cell_type="outdoor",
            location_id="LOC_FOREST_VILLAGE_001",
            description="여러 사람들이 모이는 광장"
        )
        
        assert cell_result.success, f"셀 생성 실패: {cell_result.message}"
        cell_id = cell_result.cell.cell_id
        logger.info(f"✅ 마을 광장 셀 생성 완료: {cell_id}")
        
        # 3. 모든 엔티티를 셀에 배치
        # TODO: Cell Manager의 다중 엔티티 배치 기능 구현 후 테스트
        logger.info("⚠️ 다중 엔티티 셀 배치는 Cell Manager 구현 후 테스트 예정")
        
        # 4. 정리
        await managers['entity_manager'].delete_entity(player_id)
        await managers['entity_manager'].delete_entity(npc1_id)
        await managers['entity_manager'].delete_entity(npc2_id)
        await managers['cell_manager'].delete_cell(cell_id)
        logger.info("✅ 정리 완료")
    
    @pytest.mark.asyncio
    async def test_cell_exploration_scenario(self, managers):
        """셀 탐험 시나리오"""
        logger.info("🎮 시나리오 16: 셀 탐험")
        
        # 1. 플레이어 엔티티 생성
        player_result = await managers['entity_manager'].create_entity(
            name="탐험가",
            entity_type="player",
            properties={"level": 6, "hp": 180, "mp": 120, "gold": 1200}
        )
        
        assert player_result.success, f"플레이어 생성 실패: {player_result.message}"
        player_id = player_result.entity.entity_id
        logger.info(f"✅ 탐험가 플레이어 생성 완료: {player_id}")
        
        # 2. 여러 셀 생성 (탐험 경로)
        cells = []
        cell_names = ["마을 입구", "마을 광장", "상점가", "신전", "숲의 입구"]
        
        for i, name in enumerate(cell_names):
            cell_result = await managers['cell_manager'].create_cell(
                name=name,
                cell_type="outdoor",
                location_id="LOC_FOREST_VILLAGE_001",
                description=f"{name}의 상세한 설명"
            )
            
            assert cell_result.success, f"셀 {name} 생성 실패"
            cells.append(cell_result.cell.cell_id)
            logger.info(f"✅ {name} 셀 생성 완료: {cell_result.cell.cell_id}")
        
        # 3. 순차적 셀 탐험
        # TODO: Cell Manager의 탐험 기능 구현 후 테스트
        logger.info("⚠️ 셀 탐험은 Cell Manager 구현 후 테스트 예정")
        
        # 4. 정리
        await managers['entity_manager'].delete_entity(player_id)
        for cell_id in cells:
            await managers['cell_manager'].delete_cell(cell_id)
        logger.info("✅ 정리 완료")
    
    @pytest.mark.asyncio
    async def test_cell_interaction_scenario(self, managers):
        """셀 내 상호작용 시나리오"""
        logger.info("🎮 시나리오 17: 셀 내 상호작용")
        
        # 1. 플레이어와 NPC 생성
        player_result = await managers['entity_manager'].create_entity(
            name="플레이어",
            entity_type="player",
            properties={"level": 4, "hp": 130, "mp": 90, "gold": 600}
        )
        
        npc_result = await managers['entity_manager'].create_entity(
            name="마을 주민",
            entity_type="npc",
            properties={"level": 2, "hp": 60, "mp": 30, "gold": 100}
        )
        
        assert player_result.success and npc_result.success, "엔티티 생성 실패"
        player_id = player_result.entity.entity_id
        npc_id = npc_result.entity.entity_id
        
        logger.info(f"✅ 플레이어와 NPC 생성 완료: {player_id}, {npc_id}")
        
        # 2. 셀 생성
        cell_result = await managers['cell_manager'].create_cell(
            name="마을 광장",
            cell_type="outdoor",
            location_id="LOC_FOREST_VILLAGE_001",
            description="플레이어와 NPC가 만나는 광장"
        )
        
        assert cell_result.success, f"셀 생성 실패: {cell_result.message}"
        cell_id = cell_result.cell.cell_id
        logger.info(f"✅ 마을 광장 셀 생성 완료: {cell_id}")
        
        # 3. 셀 내 상호작용 테스트
        # TODO: Dialogue Manager와 Action Handler 구현 후 테스트
        logger.info("⚠️ 셀 내 상호작용은 Dialogue Manager와 Action Handler 구현 후 테스트 예정")
        
        # 4. 정리
        await managers['entity_manager'].delete_entity(player_id)
        await managers['entity_manager'].delete_entity(npc_id)
        await managers['cell_manager'].delete_cell(cell_id)
        logger.info("✅ 정리 완료")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
