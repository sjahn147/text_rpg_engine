"""
기본 엔티티 생성 시나리오 테스트
플레이어 엔티티 생성, Effect Carrier 적용, 기본 행동 테스트
"""

import pytest
import pytest_asyncio
import asyncio
from typing import Dict, Any
from database.connection import DatabaseConnection
from app.entity.entity_manager import EntityManager
from app.world.cell_manager import CellManager
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from common.utils.logger import logger

class TestBasicEntityCreation:
    """기본 엔티티 생성 시나리오 테스트"""
    
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
    async def test_player_entity_creation(self, managers):
        """플레이어 엔티티 생성 시나리오"""
        logger.info("🎮 시나리오 1: 플레이어 엔티티 생성")
        
        # 1. 플레이어 엔티티 생성
        player_result = await managers['entity_manager'].create_entity(
            name="테스트 플레이어",
            entity_type="player",
            properties={"level": 1, "hp": 100, "mp": 50, "gold": 100}
        )
        
        assert player_result.success, f"플레이어 생성 실패: {player_result.message}"
        player_id = player_result.entity.entity_id
        logger.info(f"✅ 플레이어 생성 완료: {player_id}")
        
        # 2. 플레이어 정보 조회
        get_result = await managers['entity_manager'].get_entity(player_id)
        assert get_result.success, f"플레이어 조회 실패: {get_result.message}"
        assert get_result.entity.name == "테스트 플레이어"
        assert get_result.entity.properties["level"] == 1
        logger.info(f"✅ 플레이어 정보 조회 완료: {get_result.entity.name}")
        
        # 3. 정리
        delete_result = await managers['entity_manager'].delete_entity(player_id)
        assert delete_result.success, f"플레이어 삭제 실패: {delete_result.message}"
        logger.info("✅ 플레이어 삭제 완료")
    
    @pytest.mark.asyncio
    async def test_npc_entity_creation(self, managers):
        """NPC 엔티티 생성 시나리오"""
        logger.info("🎮 시나리오 2: NPC 엔티티 생성")
        
        # 1. NPC 엔티티 생성
        npc_result = await managers['entity_manager'].create_entity(
            name="상인 토마스",
            entity_type="npc",
            properties={"level": 5, "hp": 80, "mp": 30, "gold": 500, "shop_items": ["sword", "potion"]}
        )
        
        assert npc_result.success, f"NPC 생성 실패: {npc_result.message}"
        npc_id = npc_result.entity.entity_id
        logger.info(f"✅ NPC 생성 완료: {npc_id}")
        
        # 2. NPC 정보 조회
        get_result = await managers['entity_manager'].get_entity(npc_id)
        assert get_result.success, f"NPC 조회 실패: {get_result.message}"
        assert get_result.entity.name == "상인 토마스"
        assert get_result.entity.properties["shop_items"] == ["sword", "potion"]
        logger.info(f"✅ NPC 정보 조회 완료: {get_result.entity.name}")
        
        # 3. 정리
        delete_result = await managers['entity_manager'].delete_entity(npc_id)
        assert delete_result.success, f"NPC 삭제 실패: {delete_result.message}"
        logger.info("✅ NPC 삭제 완료")
    
    @pytest.mark.asyncio
    async def test_entity_with_effect_carrier(self, managers):
        """Effect Carrier가 적용된 엔티티 생성 시나리오"""
        logger.info("🎮 시나리오 3: Effect Carrier 적용 엔티티 생성")
        
        # 1. 플레이어 엔티티 생성
        player_result = await managers['entity_manager'].create_entity(
            name="마법사 플레이어",
            entity_type="player",
            properties={"level": 3, "hp": 80, "mp": 100, "gold": 200}
        )
        
        assert player_result.success, f"플레이어 생성 실패: {player_result.message}"
        player_id = player_result.entity.entity_id
        logger.info(f"✅ 마법사 플레이어 생성 완료: {player_id}")
        
        # 2. Effect Carrier 조회 (기존 데이터베이스에서)
        # TODO: Effect Carrier Manager 구현 후 실제 Effect Carrier 적용
        logger.info("⚠️ Effect Carrier 적용은 Manager 구현 후 테스트 예정")
        
        # 3. 정리
        delete_result = await managers['entity_manager'].delete_entity(player_id)
        assert delete_result.success, f"플레이어 삭제 실패: {delete_result.message}"
        logger.info("✅ 마법사 플레이어 삭제 완료")
    
    @pytest.mark.asyncio
    async def test_entity_cell_placement(self, managers):
        """엔티티를 셀에 배치하는 시나리오"""
        logger.info("🎮 시나리오 4: 엔티티 셀 배치")
        
        # 1. 플레이어 엔티티 생성
        player_result = await managers['entity_manager'].create_entity(
            name="탐험가 플레이어",
            entity_type="player",
            properties={"level": 2, "hp": 90, "mp": 60, "gold": 150}
        )
        
        assert player_result.success, f"플레이어 생성 실패: {player_result.message}"
        player_id = player_result.entity.entity_id
        logger.info(f"✅ 탐험가 플레이어 생성 완료: {player_id}")
        
        # 2. 셀 생성
        cell_result = await managers['cell_manager'].create_cell(
            name="마을 광장",
            cell_type="indoor",
            location_id="LOC_FOREST_VILLAGE_001",
            description="평화로운 마을의 중심 광장"
        )
        
        assert cell_result.success, f"셀 생성 실패: {cell_result.message}"
        cell_id = cell_result.cell.cell_id
        logger.info(f"✅ 마을 광장 셀 생성 완료: {cell_id}")
        
        # 3. 플레이어를 셀에 배치
        # TODO: Cell Manager의 place_entity_in_cell 메서드 구현 후 테스트
        logger.info("⚠️ 엔티티 셀 배치는 Cell Manager 구현 후 테스트 예정")
        
        # 4. 정리
        await managers['entity_manager'].delete_entity(player_id)
        # TODO: Cell Manager의 delete_cell 메서드 구현 후 테스트
        logger.info("⚠️ 셀 삭제는 Cell Manager 구현 후 테스트 예정")
        logger.info("✅ 정리 완료")
    
    @pytest.mark.asyncio
    async def test_entity_interaction(self, managers):
        """엔티티 간 상호작용 시나리오"""
        logger.info("🎮 시나리오 5: 엔티티 간 상호작용")
        
        # 1. 플레이어와 NPC 생성
        player_result = await managers['entity_manager'].create_entity(
            name="영웅 플레이어",
            entity_type="player",
            properties={"level": 4, "hp": 120, "mp": 80, "gold": 300}
        )
        
        npc_result = await managers['entity_manager'].create_entity(
            name="마을 수호자",
            entity_type="npc",
            properties={"level": 6, "hp": 150, "mp": 40, "gold": 200}
        )
        
        assert player_result.success and npc_result.success, "엔티티 생성 실패"
        player_id = player_result.entity.entity_id
        npc_id = npc_result.entity.entity_id
        
        logger.info(f"✅ 플레이어와 NPC 생성 완료: {player_id}, {npc_id}")
        
        # 2. 상호작용 시뮬레이션
        # TODO: Dialogue Manager 구현 후 실제 대화 테스트
        logger.info("⚠️ 엔티티 상호작용은 Dialogue Manager 구현 후 테스트 예정")
        
        # 3. 정리
        await managers['entity_manager'].delete_entity(player_id)
        await managers['entity_manager'].delete_entity(npc_id)
        logger.info("✅ 정리 완료")

class TestEntityLifecycle:
    """엔티티 생명주기 시나리오 테스트"""
    
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
    async def test_entity_lifecycle_complete(self, managers):
        """엔티티 완전한 생명주기 시나리오"""
        logger.info("[SCENARIO] 시나리오 6: 엔티티 완전한 생명주기")
        
        # 1. 엔티티 생성
        entity_result = await managers['entity_manager'].create_entity(
            name="생명주기 테스트 엔티티",
            entity_type="npc",
            properties={"level": 1, "hp": 50, "mp": 20, "gold": 50}
        )
        
        assert entity_result.success, f"엔티티 생성 실패: {entity_result.message}"
        entity_id = entity_result.entity.entity_id
        logger.info(f"[SUCCESS] 엔티티 생성 완료: {entity_id}")
        
        # 2. 엔티티 정보 수정 (Entity Manager의 update_entity_stats 메서드 사용)
        logger.info("엔티티 정보 수정 시작")
        update_result = await managers['entity_manager'].update_entity_stats(
            entity_id, 
            {"level": 2, "hp": 60, "mp": 30}
        )
        
        assert update_result.success, f"엔티티 수정 실패: {update_result.message}"
        logger.info("엔티티 정보 수정 완료")
        
        # 3. 수정된 정보 확인
        get_result = await managers['entity_manager'].get_entity(entity_id)
        assert get_result.success, f"엔티티 조회 실패: {get_result.message}"
        assert get_result.entity.properties["level"] == 2
        assert get_result.entity.properties["hp"] == 60
        logger.info("[SUCCESS] 수정된 정보 확인 완료")
        
        # 4. 엔티티 삭제
        delete_result = await managers['entity_manager'].delete_entity(entity_id)
        assert delete_result.success, f"엔티티 삭제 실패: {delete_result.message}"
        logger.info("[SUCCESS] 엔티티 삭제 완료")
        
        # 5. 삭제 확인
        get_result = await managers['entity_manager'].get_entity(entity_id)
        assert not get_result.success, "엔티티가 삭제되지 않았습니다"
        logger.info("[SUCCESS] 엔티티 삭제 확인 완료")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
