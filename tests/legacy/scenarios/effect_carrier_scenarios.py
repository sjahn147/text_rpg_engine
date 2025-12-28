"""
Effect Carrier 시나리오 테스트
Effect Carrier 생성, 적용, 제거, 상호작용 테스트
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

class TestEffectCarrierScenarios:
    """Effect Carrier 시나리오 테스트"""
    
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
            'cell_manager': cell_manager,
            'game_data_repo': game_data_repo,
            'runtime_data_repo': runtime_data_repo,
            'reference_layer_repo': reference_layer_repo
        }
    
    @pytest.mark.asyncio
    async def test_skill_effect_carrier_scenario(self, managers):
        """스킬 Effect Carrier 시나리오"""
        logger.info("🎮 시나리오 7: 스킬 Effect Carrier 적용")
        
        # 1. 플레이어 엔티티 생성
        player_result = await managers['entity_manager'].create_entity(
            name="전사 플레이어",
            entity_type="player",
            properties={"level": 5, "hp": 150, "mp": 30, "gold": 500, "strength": 15}
        )
        
        assert player_result.success, f"플레이어 생성 실패: {player_result.message}"
        player_id = player_result.entity.entity_id
        logger.info(f"✅ 전사 플레이어 생성 완료: {player_id}")
        
        # 2. 스킬 Effect Carrier 조회 (기존 데이터베이스에서)
        # TODO: Effect Carrier Manager 구현 후 실제 스킬 적용
        logger.info("⚠️ 스킬 Effect Carrier 적용은 Manager 구현 후 테스트 예정")
        
        # 3. 정리
        await managers['entity_manager'].delete_entity(player_id)
        logger.info("✅ 정리 완료")
    
    @pytest.mark.asyncio
    async def test_buff_effect_carrier_scenario(self, managers):
        """버프 Effect Carrier 시나리오"""
        logger.info("🎮 시나리오 8: 버프 Effect Carrier 적용")
        
        # 1. 플레이어 엔티티 생성
        player_result = await managers['entity_manager'].create_entity(
            name="마법사 플레이어",
            entity_type="player",
            properties={"level": 3, "hp": 80, "mp": 120, "gold": 300, "intelligence": 18}
        )
        
        assert player_result.success, f"플레이어 생성 실패: {player_result.message}"
        player_id = player_result.entity.entity_id
        logger.info(f"✅ 마법사 플레이어 생성 완료: {player_id}")
        
        # 2. 버프 Effect Carrier 조회 (기존 데이터베이스에서)
        # TODO: Effect Carrier Manager 구현 후 실제 버프 적용
        logger.info("⚠️ 버프 Effect Carrier 적용은 Manager 구현 후 테스트 예정")
        
        # 3. 정리
        await managers['entity_manager'].delete_entity(player_id)
        logger.info("✅ 정리 완료")
    
    @pytest.mark.asyncio
    async def test_item_effect_carrier_scenario(self, managers):
        """아이템 Effect Carrier 시나리오"""
        logger.info("🎮 시나리오 9: 아이템 Effect Carrier 적용")
        
        # 1. 플레이어 엔티티 생성
        player_result = await managers['entity_manager'].create_entity(
            name="탐험가 플레이어",
            entity_type="player",
            properties={"level": 2, "hp": 100, "mp": 50, "gold": 200, "inventory": []}
        )
        
        assert player_result.success, f"플레이어 생성 실패: {player_result.message}"
        player_id = player_result.entity.entity_id
        logger.info(f"✅ 탐험가 플레이어 생성 완료: {player_id}")
        
        # 2. 아이템 Effect Carrier 조회 (기존 데이터베이스에서)
        # TODO: Effect Carrier Manager 구현 후 실제 아이템 사용
        logger.info("⚠️ 아이템 Effect Carrier 적용은 Manager 구현 후 테스트 예정")
        
        # 3. 정리
        await managers['entity_manager'].delete_entity(player_id)
        logger.info("✅ 정리 완료")
    
    @pytest.mark.asyncio
    async def test_multiple_effect_carriers_scenario(self, managers):
        """여러 Effect Carrier 동시 적용 시나리오"""
        logger.info("🎮 시나리오 10: 여러 Effect Carrier 동시 적용")
        
        # 1. 플레이어 엔티티 생성
        player_result = await managers['entity_manager'].create_entity(
            name="하이브리드 플레이어",
            entity_type="player",
            properties={"level": 7, "hp": 200, "mp": 100, "gold": 1000, "strength": 20, "intelligence": 15}
        )
        
        assert player_result.success, f"플레이어 생성 실패: {player_result.message}"
        player_id = player_result.entity.entity_id
        logger.info(f"✅ 하이브리드 플레이어 생성 완료: {player_id}")
        
        # 2. 여러 Effect Carrier 조회 및 적용
        # TODO: Effect Carrier Manager 구현 후 실제 다중 적용 테스트
        logger.info("⚠️ 다중 Effect Carrier 적용은 Manager 구현 후 테스트 예정")
        
        # 3. 정리
        await managers['entity_manager'].delete_entity(player_id)
        logger.info("✅ 정리 완료")
    
    @pytest.mark.asyncio
    async def test_effect_carrier_interaction_scenario(self, managers):
        """Effect Carrier 간 상호작용 시나리오"""
        logger.info("🎮 시나리오 11: Effect Carrier 간 상호작용")
        
        # 1. 플레이어와 NPC 생성
        player_result = await managers['entity_manager'].create_entity(
            name="영웅 플레이어",
            entity_type="player",
            properties={"level": 8, "hp": 250, "mp": 150, "gold": 2000}
        )
        
        npc_result = await managers['entity_manager'].create_entity(
            name="마법사 NPC",
            entity_type="npc",
            properties={"level": 10, "hp": 300, "mp": 200, "gold": 500}
        )
        
        assert player_result.success and npc_result.success, "엔티티 생성 실패"
        player_id = player_result.entity.entity_id
        npc_id = npc_result.entity.entity_id
        
        logger.info(f"✅ 플레이어와 NPC 생성 완료: {player_id}, {npc_id}")
        
        # 2. Effect Carrier 간 상호작용 테스트
        # TODO: Effect Carrier Manager 구현 후 실제 상호작용 테스트
        logger.info("⚠️ Effect Carrier 상호작용은 Manager 구현 후 테스트 예정")
        
        # 3. 정리
        await managers['entity_manager'].delete_entity(player_id)
        await managers['entity_manager'].delete_entity(npc_id)
        logger.info("✅ 정리 완료")

class TestEffectCarrierLifecycle:
    """Effect Carrier 생명주기 시나리오 테스트"""
    
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
    async def test_effect_carrier_lifecycle_complete(self, managers):
        """Effect Carrier 완전한 생명주기 시나리오"""
        logger.info("🎮 시나리오 12: Effect Carrier 완전한 생명주기")
        
        # 1. 엔티티 생성
        entity_result = await managers['entity_manager'].create_entity(
            name="Effect Carrier 테스트 엔티티",
            entity_type="player",
            properties={"level": 5, "hp": 120, "mp": 80, "gold": 800}
        )
        
        assert entity_result.success, f"엔티티 생성 실패: {entity_result.message}"
        entity_id = entity_result.entity.entity_id
        logger.info(f"✅ 테스트 엔티티 생성 완료: {entity_id}")
        
        # 2. Effect Carrier 생성 및 적용
        # TODO: Effect Carrier Manager 구현 후 실제 생명주기 테스트
        logger.info("⚠️ Effect Carrier 생명주기는 Manager 구현 후 테스트 예정")
        
        # 3. 정리
        await managers['entity_manager'].delete_entity(entity_id)
        logger.info("✅ 정리 완료")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
