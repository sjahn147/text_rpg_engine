"""
통합 게임플레이 시나리오 테스트
여러 시스템이 연동된 복합적인 게임 시나리오 테스트
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

class TestIntegratedGameplayScenarios:
    """통합 게임플레이 시나리오 테스트"""
    
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
    async def test_complete_adventure_scenario(self, managers):
        """완전한 모험 시나리오"""
        logger.info("🎮 시나리오 18: 완전한 모험 시나리오")
        
        # 1. 플레이어 생성
        player_result = await managers['entity_manager'].create_entity(
            name="영웅 플레이어",
            entity_type="player",
            properties={"level": 5, "hp": 200, "mp": 100, "gold": 1000, "experience": 0}
        )
        
        assert player_result.success, f"플레이어 생성 실패: {player_result.message}"
        player_id = player_result.entity.entity_id
        logger.info(f"✅ 영웅 플레이어 생성 완료: {player_id}")
        
        # 2. 여러 NPC 생성
        npcs = []
        npc_data = [
            {"name": "마을 촌장", "type": "npc", "level": 3, "hp": 80, "gold": 200},
            {"name": "상인", "type": "npc", "level": 2, "hp": 60, "gold": 500},
            {"name": "수호자", "type": "npc", "level": 8, "hp": 300, "gold": 100}
        ]
        
        for npc_info in npc_data:
            npc_result = await managers['entity_manager'].create_entity(
                name=npc_info["name"],
                entity_type=npc_info["type"],
                properties={"level": npc_info["level"], "hp": npc_info["hp"], "gold": npc_info["gold"]}
            )
            assert npc_result.success, f"NPC {npc_info['name']} 생성 실패"
            npcs.append(npc_result.entity.entity_id)
            logger.info(f"✅ {npc_info['name']} NPC 생성 완료")
        
        # 3. 여러 셀 생성 (모험 경로)
        cells = []
        cell_data = [
            {"name": "마을 입구", "description": "모험의 시작점"},
            {"name": "마을 광장", "description": "주민들이 모이는 곳"},
            {"name": "상점가", "description": "다양한 물건을 판매하는 곳"},
            {"name": "신전", "description": "신성한 힘이 느껴지는 곳"},
            {"name": "숲의 입구", "description": "위험한 모험이 기다리는 곳"}
        ]
        
        for cell_info in cell_data:
            cell_result = await managers['cell_manager'].create_cell(
                name=cell_info["name"],
                description=cell_info["description"],
                location_id="LOC_FOREST_VILLAGE_001"
            )
            assert cell_result.success, f"셀 {cell_info['name']} 생성 실패"
            cells.append(cell_result.cell.cell_id)
            logger.info(f"✅ {cell_info['name']} 셀 생성 완료")
        
        # 4. 통합 게임플레이 시뮬레이션
        # TODO: 모든 Manager 구현 후 실제 통합 게임플레이 테스트
        logger.info("⚠️ 통합 게임플레이는 모든 Manager 구현 후 테스트 예정")
        
        # 5. 정리
        await managers['entity_manager'].delete_entity(player_id)
        for npc_id in npcs:
            await managers['entity_manager'].delete_entity(npc_id)
        for cell_id in cells:
            await managers['cell_manager'].delete_cell(cell_id)
        logger.info("✅ 정리 완료")
    
    @pytest.mark.asyncio
    async def test_combat_scenario(self, managers):
        """전투 시나리오"""
        logger.info("🎮 시나리오 19: 전투 시나리오")
        
        # 1. 플레이어와 적 생성
        player_result = await managers['entity_manager'].create_entity(
            name="전사 플레이어",
            entity_type="player",
            properties={"level": 6, "hp": 250, "mp": 80, "gold": 800, "attack": 25, "defense": 15}
        )
        
        enemy_result = await managers['entity_manager'].create_entity(
            name="고블린",
            entity_type="monster",
            properties={"level": 4, "hp": 120, "mp": 20, "gold": 50, "attack": 18, "defense": 8}
        )
        
        assert player_result.success and enemy_result.success, "엔티티 생성 실패"
        player_id = player_result.entity.entity_id
        enemy_id = enemy_result.entity.entity_id
        
        logger.info(f"✅ 전사 플레이어와 고블린 생성 완료: {player_id}, {enemy_id}")
        
        # 2. 전투 셀 생성
        cell_result = await managers['cell_manager'].create_cell(
            name="전투 지역",
            description="위험한 전투가 벌어지는 곳",
            location_id="LOC_FOREST_VILLAGE_001"
        )
        
        assert cell_result.success, f"전투 셀 생성 실패: {cell_result.message}"
        cell_id = cell_result.cell.cell_id
        logger.info(f"✅ 전투 지역 셀 생성 완료: {cell_id}")
        
        # 3. 전투 시뮬레이션
        # TODO: 전투 시스템 구현 후 실제 전투 테스트
        logger.info("⚠️ 전투 시뮬레이션은 전투 시스템 구현 후 테스트 예정")
        
        # 4. 정리
        await managers['entity_manager'].delete_entity(player_id)
        await managers['entity_manager'].delete_entity(enemy_id)
        await managers['cell_manager'].delete_cell(cell_id)
        logger.info("✅ 정리 완료")
    
    @pytest.mark.asyncio
    async def test_trading_scenario(self, managers):
        """거래 시나리오"""
        logger.info("🎮 시나리오 20: 거래 시나리오")
        
        # 1. 플레이어와 상인 생성
        player_result = await managers['entity_manager'].create_entity(
            name="상인 플레이어",
            entity_type="player",
            properties={"level": 4, "hp": 150, "mp": 70, "gold": 500, "inventory": ["sword", "potion"]}
        )
        
        merchant_result = await managers['entity_manager'].create_entity(
            name="상점 주인",
            entity_type="npc",
            properties={"level": 3, "hp": 100, "mp": 50, "gold": 2000, "shop_items": ["armor", "shield", "potion"]}
        )
        
        assert player_result.success and merchant_result.success, "엔티티 생성 실패"
        player_id = player_result.entity.entity_id
        merchant_id = merchant_result.entity.entity_id
        
        logger.info(f"✅ 상인 플레이어와 상점 주인 생성 완료: {player_id}, {merchant_id}")
        
        # 2. 상점 셀 생성
        cell_result = await managers['cell_manager'].create_cell(
            name="상점 내부",
            description="다양한 물건들이 진열된 상점",
            location_id="LOC_FOREST_VILLAGE_001"
        )
        
        assert cell_result.success, f"상점 셀 생성 실패: {cell_result.message}"
        cell_id = cell_result.cell.cell_id
        logger.info(f"✅ 상점 내부 셀 생성 완료: {cell_id}")
        
        # 3. 거래 시뮬레이션
        # TODO: 거래 시스템 구현 후 실제 거래 테스트
        logger.info("⚠️ 거래 시뮬레이션은 거래 시스템 구현 후 테스트 예정")
        
        # 4. 정리
        await managers['entity_manager'].delete_entity(player_id)
        await managers['entity_manager'].delete_entity(merchant_id)
        await managers['cell_manager'].delete_cell(cell_id)
        logger.info("✅ 정리 완료")

class TestSessionManagementScenarios:
    """세션 관리 시나리오 테스트"""
    
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
    async def test_session_save_load_scenario(self, managers):
        """세션 저장/로드 시나리오"""
        logger.info("🎮 시나리오 21: 세션 저장/로드")
        
        # 1. 플레이어 생성
        player_result = await managers['entity_manager'].create_entity(
            name="세션 테스트 플레이어",
            entity_type="player",
            properties={"level": 3, "hp": 120, "mp": 80, "gold": 400, "experience": 150}
        )
        
        assert player_result.success, f"플레이어 생성 실패: {player_result.message}"
        player_id = player_result.entity.entity_id
        logger.info(f"✅ 세션 테스트 플레이어 생성 완료: {player_id}")
        
        # 2. 세션 저장 시뮬레이션
        # TODO: 세션 관리 시스템 구현 후 실제 저장/로드 테스트
        logger.info("⚠️ 세션 저장/로드는 세션 관리 시스템 구현 후 테스트 예정")
        
        # 3. 정리
        await managers['entity_manager'].delete_entity(player_id)
        logger.info("✅ 정리 완료")
    
    @pytest.mark.asyncio
    async def test_multi_session_scenario(self, managers):
        """다중 세션 시나리오"""
        logger.info("🎮 시나리오 22: 다중 세션")
        
        # 1. 여러 플레이어 생성 (다른 세션)
        players = []
        for i in range(3):
            player_result = await managers['entity_manager'].create_entity(
                name=f"플레이어 {i+1}",
                entity_type="player",
                properties={"level": 2+i, "hp": 100+i*20, "mp": 50+i*10, "gold": 200+i*100}
            )
            
            assert player_result.success, f"플레이어 {i+1} 생성 실패"
            players.append(player_result.entity.entity_id)
            logger.info(f"✅ 플레이어 {i+1} 생성 완료")
        
        # 2. 다중 세션 시뮬레이션
        # TODO: 다중 세션 관리 시스템 구현 후 테스트
        logger.info("⚠️ 다중 세션은 세션 관리 시스템 구현 후 테스트 예정")
        
        # 3. 정리
        for player_id in players:
            await managers['entity_manager'].delete_entity(player_id)
        logger.info("✅ 정리 완료")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
