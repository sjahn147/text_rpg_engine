"""
EntityManager 테스트
"""
import pytest
import uuid
from unittest.mock import Mock, AsyncMock
from app.entity.entity_manager import (
    EntityManager, EntityData, EntityResult, EntityType, EntityStatus
)
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository


class TestEntityManager:
    """EntityManager 테스트 클래스"""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Mock 의존성들"""
        mock_db = Mock(spec=DatabaseConnection)
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()
        mock_conn.fetchrow = AsyncMock()
        mock_conn.fetch = AsyncMock()
        
        # Mock pool acquire를 올바르게 설정
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_context_manager.__aexit__ = AsyncMock(return_value=None)
        
        # acquire()가 매번 새로운 context manager를 반환하도록 설정
        def acquire():
            new_context_manager = AsyncMock()
            new_conn = AsyncMock()
            new_conn.execute = AsyncMock()
            new_conn.fetchrow = AsyncMock()
            new_conn.fetch = AsyncMock()
            new_context_manager.__aenter__ = AsyncMock(return_value=new_conn)
            new_context_manager.__aexit__ = AsyncMock(return_value=None)
            return new_context_manager
        mock_pool.acquire = acquire
        
        # Mock pool을 await 가능하게 설정
        async def get_pool():
            return mock_pool
        mock_db.pool = get_pool()
        
        # Mock repositories with proper return values
        mock_game_data_repo = Mock(spec=GameDataRepository)
        mock_runtime_data_repo = Mock(spec=RuntimeDataRepository)
        mock_reference_layer_repo = Mock(spec=ReferenceLayerRepository)
        
        # Mock static entity template data
        mock_static_entity = {
            'entity_id': 'NPC_MERCHANT_001',
            'name': '상인 토마스',
            'entity_type': 'npc',
            'status': 'active',
            'properties': {'health': 100, 'level': 1},
            'position': {'x': 0.0, 'y': 0.0}
        }
        
        # Mock session data
        mock_session = {
            'session_id': 'test-session',
            'player_id': 'test-player',
            'started_at': '2025-10-19T00:00:00Z',
            'status': 'active'
        }
        
        # Configure mock responses
        mock_conn.fetchrow.return_value = mock_static_entity
        mock_conn.fetch.return_value = [mock_session]
        mock_conn.execute.return_value = "INSERT 0 1"
        
        return {
            'db_connection': mock_db,
            'game_data_repo': mock_game_data_repo,
            'runtime_data_repo': mock_runtime_data_repo,
            'reference_layer_repo': mock_reference_layer_repo
        }
    
    @pytest.fixture
    def entity_manager(self, mock_dependencies):
        """EntityManager 인스턴스"""
        return EntityManager(
            db_connection=mock_dependencies['db_connection'],
            game_data_repo=mock_dependencies['game_data_repo'],
            runtime_data_repo=mock_dependencies['runtime_data_repo'],
            reference_layer_repo=mock_dependencies['reference_layer_repo'],
            effect_carrier_manager=None  # Effect Carrier Manager는 선택사항
        )
    
    def test_initialization(self, entity_manager, mock_dependencies):
        """초기화 테스트"""
        # Given & When
        # EntityManager 인스턴스 생성
        
        # Then
        assert entity_manager.db == mock_dependencies['db_connection']
        assert entity_manager.game_data == mock_dependencies['game_data_repo']
        assert entity_manager.runtime_data == mock_dependencies['runtime_data_repo']
        assert entity_manager.reference_layer == mock_dependencies['reference_layer_repo']
        assert entity_manager._entity_cache == {}
    
    @pytest.mark.asyncio
    async def test_create_entity_success(self, entity_manager):
        """엔티티 생성 성공 테스트"""
        # Given
        static_entity_id = "NPC_MERCHANT_001"  # 정적 엔티티 템플릿 ID
        session_id = str(uuid.uuid4())
        custom_properties = {"health": 100, "level": 5}
        custom_position = {"x": 10.0, "y": 20.0}
        
        # When
        result = await entity_manager.create_entity(
            static_entity_id=static_entity_id,
            session_id=session_id,
            custom_properties=custom_properties,
            custom_position=custom_position
        )
        
        # Then
        assert result.success is True
        assert result.entity is not None
        assert result.entity.entity_id is not None
        assert result.entity.entity_type == EntityType.NPC
        assert result.entity.properties == custom_properties
        assert result.entity.position == custom_position
    
    @pytest.mark.asyncio
    async def test_create_entity_invalid_static_id(self, entity_manager):
        """잘못된 정적 엔티티 ID로 엔티티 생성 실패 테스트"""
        # Given
        static_entity_id = "INVALID_ID"
        session_id = str(uuid.uuid4())
        
        # When
        result = await entity_manager.create_entity(
            static_entity_id=static_entity_id,
            session_id=session_id
        )
        
        # Then
        assert result.success is False
        assert result.entity is None
        assert "정적 엔티티 템플릿을 찾을 수 없습니다" in result.message
    
    @pytest.mark.asyncio
    async def test_create_entity_missing_session(self, entity_manager):
        """세션이 없는 경우 엔티티 생성 실패 테스트"""
        # Given
        static_entity_id = "NPC_MERCHANT_001"
        session_id = "INVALID_SESSION"
        
        # When
        result = await entity_manager.create_entity(
            static_entity_id=static_entity_id,
            session_id=session_id
        )
        
        # Then
        assert result.success is False
        assert result.entity is None
        assert "세션을 찾을 수 없습니다" in result.message
    
    @pytest.mark.asyncio
    async def test_get_entity_from_cache(self, entity_manager):
        """캐시에서 엔티티 조회 테스트"""
        # Given
        entity_data = EntityData(
            entity_id="test-id",
            name="Test Entity",
            entity_type=EntityType.NPC
        )
        
        # 캐시에 엔티티 추가
        entity_manager._entity_cache["test-id"] = entity_data
        
        # When
        result = await entity_manager.get_entity("test-id")
        
        # Then
        assert result.success is True
        assert result.entity == entity_data
        assert result.message == "캐시에서 조회"
    
    @pytest.mark.asyncio
    async def test_get_entity_not_found(self, entity_manager):
        """존재하지 않는 엔티티 조회 테스트"""
        # Given
        entity_id = "non-existent-id"
        
        # When
        result = await entity_manager.get_entity(entity_id)
        
        # Then
        assert result.success is False
        assert result.entity is None
        assert f"엔티티 '{entity_id}'를 찾을 수 없습니다." in result.message
    
    @pytest.mark.asyncio
    async def test_update_entity_success(self, entity_manager):
        """엔티티 업데이트 성공 테스트"""
        # Given
        entity_data = EntityData(
            entity_id="test-id",
            name="Test Entity",
            entity_type=EntityType.NPC,
            properties={"health": 100}
        )
        
        # 캐시에 엔티티 추가
        entity_manager._entity_cache["test-id"] = entity_data
        
        updates = {"health": 80, "mana": 50}
        
        # When
        result = await entity_manager.update_entity("test-id", updates)
        
        # Then
        assert result.success is True
        assert result.entity is not None
        assert result.entity.properties["health"] == 80
        assert result.entity.properties["mana"] == 50
        assert result.message == f"엔티티 '{entity_data.name}' 업데이트 완료"
    
    @pytest.mark.asyncio
    async def test_update_entity_not_found(self, entity_manager):
        """존재하지 않는 엔티티 업데이트 테스트"""
        # Given
        entity_id = "non-existent-id"
        updates = {"health": 80}
        
        # When
        result = await entity_manager.update_entity(entity_id, updates)
        
        # Then
        assert result.success is False
        assert result.entity is None
        assert f"엔티티 '{entity_id}'를 찾을 수 없습니다." in result.message
    
    @pytest.mark.asyncio
    async def test_delete_entity_success(self, entity_manager):
        """엔티티 삭제 성공 테스트"""
        # Given
        entity_data = EntityData(
            entity_id="test-id",
            name="Test Entity",
            entity_type=EntityType.NPC
        )
        
        # 캐시에 엔티티 추가
        entity_manager._entity_cache["test-id"] = entity_data
        
        # When
        result = await entity_manager.delete_entity("test-id")
        
        # Then
        assert result.success is True
        assert result.entity is not None
        assert result.entity.status == EntityStatus.INACTIVE
        assert result.message == f"엔티티 '{entity_data.name}' 삭제 완료"
        
        # 캐시에서 제거되었는지 확인
        assert "test-id" not in entity_manager._entity_cache
    
    @pytest.mark.asyncio
    async def test_delete_entity_not_found(self, entity_manager):
        """존재하지 않는 엔티티 삭제 테스트"""
        # Given
        entity_id = "non-existent-id"
        
        # When
        result = await entity_manager.delete_entity(entity_id)
        
        # Then
        assert result.success is False
        assert result.entity is None
        assert f"엔티티 '{entity_id}'를 찾을 수 없습니다." in result.message
    
    @pytest.mark.asyncio
    async def test_list_entities(self, entity_manager):
        """엔티티 목록 조회 테스트"""
        # Given & When
        entities = await entity_manager.list_entities()
        
        # Then
        assert isinstance(entities, list)
    
    @pytest.mark.asyncio
    async def test_list_entities_with_filters(self, entity_manager):
        """필터링된 엔티티 목록 조회 테스트"""
        # Given
        entity_type = EntityType.NPC
        status = EntityStatus.ACTIVE
        
        # When
        entities = await entity_manager.list_entities(
            entity_type=entity_type,
            status=status
        )
        
        # Then
        assert isinstance(entities, list)
    
    @pytest.mark.asyncio
    async def test_clear_cache(self, entity_manager):
        """캐시 초기화 테스트"""
        # Given
        entity_data = EntityData(
            entity_id="test-id",
            name="Test Entity",
            entity_type=EntityType.NPC
        )
        
        # 캐시에 엔티티 추가
        entity_manager._entity_cache["test-id"] = entity_data
        assert len(entity_manager._entity_cache) == 1
        
        # When
        await entity_manager.clear_cache()
        
        # Then
        assert len(entity_manager._entity_cache) == 0
    
    def test_entity_data_validation(self):
        """EntityData 모델 검증 테스트"""
        # Given
        entity_data = EntityData(
            entity_id="test-id",
            name="Test Entity",
            entity_type=EntityType.NPC,
            status=EntityStatus.ACTIVE,
            properties={"health": 100}
        )
        
        # When & Then
        assert entity_data.entity_id == "test-id"
        assert entity_data.name == "Test Entity"
        assert entity_data.entity_type == EntityType.NPC
        assert entity_data.status == EntityStatus.ACTIVE
        assert entity_data.properties == {"health": 100}
    
    def test_entity_result_success(self):
        """EntityResult 성공 결과 테스트"""
        # Given
        entity_data = EntityData(
            entity_id="test-id",
            name="Test Entity",
            entity_type=EntityType.NPC
        )
        
        # When
        result = EntityResult.success_result(entity_data, "Test message")
        
        # Then
        assert result.success is True
        assert result.entity == entity_data
        assert result.message == "Test message"
        assert result.error is None
    
    def test_entity_result_error(self):
        """EntityResult 에러 결과 테스트"""
        # When
        result = EntityResult.error_result("Test error", "Detailed error")
        
        # Then
        assert result.success is False
        assert result.entity is None
        assert result.message == "Test error"
        assert result.error == "Detailed error"
