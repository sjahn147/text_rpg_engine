"""
게임 플로우 통합 테스트
"""
import pytest
from unittest.mock import Mock, AsyncMock
from app.core.game_manager import GameManager
from app.entity.entity_manager import EntityManager, EntityType, EntityStatus
from app.world.cell_manager import CellManager, CellType, CellStatus
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from database.factories.game_data_factory import GameDataFactory
from database.factories.instance_factory import InstanceFactory


class TestGameFlow:
    """게임 플로우 통합 테스트 클래스"""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Mock 의존성들"""
        return {
            'db_connection': Mock(spec=DatabaseConnection),
            'game_data_repo': Mock(spec=GameDataRepository),
            'runtime_data_repo': Mock(spec=RuntimeDataRepository),
            'reference_layer_repo': Mock(spec=ReferenceLayerRepository),
            'game_data_factory': Mock(spec=GameDataFactory),
            'instance_factory': Mock(spec=InstanceFactory)
        }
    
    @pytest.fixture
    def entity_manager(self, mock_dependencies):
        """EntityManager 인스턴스"""
        return EntityManager(
            db_connection=mock_dependencies['db_connection'],
            game_data_repo=mock_dependencies['game_data_repo'],
            runtime_data_repo=mock_dependencies['runtime_data_repo'],
            reference_layer_repo=mock_dependencies['reference_layer_repo']
        )
    
    @pytest.fixture
    def cell_manager(self, mock_dependencies, entity_manager):
        """CellManager 인스턴스"""
        return CellManager(
            db_connection=mock_dependencies['db_connection'],
            game_data_repo=mock_dependencies['game_data_repo'],
            runtime_data_repo=mock_dependencies['runtime_data_repo'],
            reference_layer_repo=mock_dependencies['reference_layer_repo'],
            entity_manager=entity_manager
        )
    
    @pytest.fixture
    def game_manager(self, mock_dependencies):
        """GameManager 인스턴스"""
        return GameManager(
            db_connection=mock_dependencies['db_connection'],
            game_data_repo=mock_dependencies['game_data_repo'],
            runtime_data_repo=mock_dependencies['runtime_data_repo'],
            reference_layer_repo=mock_dependencies['reference_layer_repo'],
            game_data_factory=mock_dependencies['game_data_factory'],
            instance_factory=mock_dependencies['instance_factory']
        )
    
    @pytest.mark.asyncio
    async def test_complete_game_flow(self, entity_manager, cell_manager, game_manager):
        """완전한 게임 플로우 테스트"""
        # Given
        player_name = "Test Player"
        cell_name = "Village Square"
        
        # 1. 플레이어 생성
        player_result = await entity_manager.create_entity(
            name=player_name,
            entity_type=EntityType.PLAYER,
            properties={"health": 100, "level": 1}
        )
        
        assert player_result.success is True
        assert player_result.entity is not None
        player_id = player_result.entity.entity_id
        
        # 2. 셀 생성
        cell_result = await cell_manager.create_cell(
            name=cell_name,
            cell_type=CellType.OUTDOOR,
            description="A peaceful village square",
            properties={"lighting": "bright", "weather": "sunny"}
        )
        
        assert cell_result.success is True
        assert cell_result.cell is not None
        cell_id = cell_result.cell.cell_id
        
        # 3. NPC 생성
        npc_result = await entity_manager.create_entity(
            name="Village Elder",
            entity_type=EntityType.NPC,
            properties={"health": 80, "level": 5, "role": "elder"}
        )
        
        assert npc_result.success is True
        assert npc_result.entity is not None
        npc_id = npc_result.entity.entity_id
        
        # 4. 플레이어가 셀에 진입
        enter_result = await cell_manager.enter_cell(cell_id, player_id)
        
        assert enter_result.success is True
        assert enter_result.cell is not None
        assert enter_result.content is not None
        
        # 5. NPC가 셀에 진입
        npc_enter_result = await cell_manager.enter_cell(cell_id, npc_id)
        
        assert npc_enter_result.success is True
        
        # 6. 플레이어 상태 업데이트
        update_result = await entity_manager.update_entity(
            player_id, 
            {"health": 95, "experience": 50}
        )
        
        assert update_result.success is True
        assert update_result.entity.properties["health"] == 95
        assert update_result.entity.properties["experience"] == 50
        
        # 7. 셀 상태 업데이트
        cell_update_result = await cell_manager.update_cell(
            cell_id,
            {"weather": "cloudy", "atmosphere": "tense"}
        )
        
        assert cell_update_result.success is True
        assert cell_update_result.cell.properties["weather"] == "cloudy"
        assert cell_update_result.cell.properties["atmosphere"] == "tense"
        
        # 8. 플레이어가 셀에서 떠남
        leave_result = await cell_manager.leave_cell(cell_id, player_id)
        
        assert leave_result.success is True
        
        # 9. 엔티티 목록 조회
        entities = await entity_manager.list_entities()
        assert isinstance(entities, list)
        
        # 10. 셀 목록 조회
        cells = await cell_manager.list_cells()
        assert isinstance(cells, list)
    
    @pytest.mark.asyncio
    async def test_entity_cell_interaction(self, entity_manager, cell_manager):
        """엔티티-셀 상호작용 테스트"""
        # Given
        # 플레이어 생성
        player_result = await entity_manager.create_entity(
            name="Adventurer",
            entity_type=EntityType.PLAYER,
            properties={"health": 100, "mana": 50}
        )
        assert player_result.success is True
        player_id = player_result.entity.entity_id
        
        # 상점 셀 생성
        shop_result = await cell_manager.create_cell(
            name="Weapon Shop",
            cell_type=CellType.SHOP,
            description="A well-stocked weapon shop",
            properties={"merchant": "Gorak", "items": ["sword", "shield"]}
        )
        assert shop_result.success is True
        shop_id = shop_result.cell.cell_id
        
        # 상인 NPC 생성
        merchant_result = await entity_manager.create_entity(
            name="Gorak",
            entity_type=EntityType.NPC,
            properties={"health": 60, "role": "merchant", "gold": 1000}
        )
        assert merchant_result.success is True
        merchant_id = merchant_result.entity.entity_id
        
        # When
        # 플레이어가 상점에 진입
        enter_result = await cell_manager.enter_cell(shop_id, player_id)
        assert enter_result.success is True
        
        # 상인이 상점에 진입
        merchant_enter_result = await cell_manager.enter_cell(shop_id, merchant_id)
        assert merchant_enter_result.success is True
        
        # 플레이어가 아이템 구매 (시뮬레이션)
        player_update_result = await entity_manager.update_entity(
            player_id,
            {"gold": 50, "inventory": ["iron_sword"]}
        )
        assert player_update_result.success is True
        
        # 상인이 금화 받음
        merchant_update_result = await entity_manager.update_entity(
            merchant_id,
            {"gold": 1050, "inventory": ["iron_sword"]}
        )
        assert merchant_update_result.success is True
        
        # Then
        # 최종 상태 확인
        final_player = await entity_manager.get_entity(player_id)
        assert final_player.success is True
        assert final_player.entity.properties["gold"] == 50
        assert "iron_sword" in final_player.entity.properties["inventory"]
        
        final_merchant = await entity_manager.get_entity(merchant_id)
        assert final_merchant.success is True
        assert final_merchant.entity.properties["gold"] == 1050
    
    @pytest.mark.asyncio
    async def test_error_handling_flow(self, entity_manager, cell_manager):
        """에러 처리 플로우 테스트"""
        # Given
        invalid_entity_id = "non-existent-entity"
        invalid_cell_id = "non-existent-cell"
        
        # When & Then
        # 존재하지 않는 엔티티 조회
        entity_result = await entity_manager.get_entity(invalid_entity_id)
        assert entity_result.success is False
        assert "찾을 수 없습니다" in entity_result.message
        
        # 존재하지 않는 셀 조회
        cell_result = await cell_manager.get_cell(invalid_cell_id)
        assert cell_result.success is False
        assert "찾을 수 없습니다" in cell_result.message
        
        # 존재하지 않는 셀에 진입
        enter_result = await cell_manager.enter_cell(invalid_cell_id, "player-id")
        assert enter_result.success is False
        
        # 존재하지 않는 엔티티 업데이트
        update_result = await entity_manager.update_entity(invalid_entity_id, {"health": 50})
        assert update_result.success is False
        
        # 존재하지 않는 셀 업데이트
        cell_update_result = await cell_manager.update_cell(invalid_cell_id, {"lighting": "dim"})
        assert cell_update_result.success is False
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, entity_manager, cell_manager):
        """동시 작업 테스트"""
        import asyncio
        
        # Given
        # 여러 엔티티와 셀 생성
        entities = []
        cells = []
        
        # 5개 엔티티 생성
        for i in range(5):
            result = await entity_manager.create_entity(
                name=f"Entity {i}",
                entity_type=EntityType.NPC,
                properties={"id": i}
            )
            assert result.success is True
            entities.append(result.entity)
        
        # 3개 셀 생성
        for i in range(3):
            result = await cell_manager.create_cell(
                name=f"Cell {i}",
                cell_type=CellType.INDOOR,
                properties={"id": i}
            )
            assert result.success is True
            cells.append(result.cell)
        
        # When
        # 동시에 여러 작업 실행
        async def update_entity(entity_id, updates):
            return await entity_manager.update_entity(entity_id, updates)
        
        async def update_cell(cell_id, updates):
            return await cell_manager.update_cell(cell_id, updates)
        
        # 동시 업데이트 작업들
        tasks = []
        for i, entity in enumerate(entities):
            tasks.append(update_entity(entity.entity_id, {"updated": True, "index": i}))
        
        for i, cell in enumerate(cells):
            tasks.append(update_cell(cell.cell_id, {"updated": True, "index": i}))
        
        # 모든 작업 동시 실행
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Then
        # 모든 작업이 성공했는지 확인
        for result in results:
            if isinstance(result, Exception):
                pytest.fail(f"동시 작업 중 예외 발생: {result}")
            assert result.success is True
    
    @pytest.mark.asyncio
    async def test_cache_consistency(self, entity_manager, cell_manager):
        """캐시 일관성 테스트"""
        # Given
        # 엔티티 생성
        entity_result = await entity_manager.create_entity(
            name="Cache Test Entity",
            entity_type=EntityType.PLAYER,
            properties={"test": "cache"}
        )
        assert entity_result.success is True
        entity_id = entity_result.entity.entity_id
        
        # 셀 생성
        cell_result = await cell_manager.create_cell(
            name="Cache Test Cell",
            cell_type=CellType.INDOOR,
            properties={"test": "cache"}
        )
        assert cell_result.success is True
        cell_id = cell_result.cell.cell_id
        
        # When
        # 캐시에서 조회
        cached_entity = await entity_manager.get_entity(entity_id)
        cached_cell = await cell_manager.get_cell(cell_id)
        
        # Then
        assert cached_entity.success is True
        assert cached_entity.message == "캐시에서 조회"
        assert cached_entity.entity.entity_id == entity_id
        
        assert cached_cell.success is True
        assert cached_cell.message == "캐시에서 조회"
        assert cached_cell.cell.cell_id == cell_id
        
        # 캐시 초기화
        await entity_manager.clear_cache()
        await cell_manager.clear_cache()
        
        # 캐시 초기화 후 조회 (데이터베이스에서 조회해야 함)
        after_clear_entity = await entity_manager.get_entity(entity_id)
        after_clear_cell = await cell_manager.get_cell(cell_id)
        
        # 캐시가 비어있으므로 데이터베이스에서 조회 시도 (Mock이므로 실패)
        assert after_clear_entity.success is False
        assert after_clear_cell.success is False
