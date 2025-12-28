"""
GameManager 테스트
"""
import pytest
from unittest.mock import AsyncMock, Mock
from app.core.game_manager import GameManager
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from database.factories.game_data_factory import GameDataFactory
from database.factories.instance_factory import InstanceFactory


class TestGameManager:
    """GameManager 테스트 클래스"""
    
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
    
    def test_initialization(self, game_manager, mock_dependencies):
        """초기화 테스트"""
        # Given & When
        # GameManager 인스턴스 생성
        
        # Then
        assert game_manager.db == mock_dependencies['db_connection']
        assert game_manager.game_data == mock_dependencies['game_data_repo']
        assert game_manager.runtime_data == mock_dependencies['runtime_data_repo']
        assert game_manager.reference_layer == mock_dependencies['reference_layer_repo']
        assert game_manager.game_data_factory == mock_dependencies['game_data_factory']
        assert game_manager.instance_factory == mock_dependencies['instance_factory']
        assert game_manager.current_session_id is None
        assert game_manager.current_player_id is None
    
    @pytest.mark.asyncio
    async def test_start_new_game_success(self, game_manager):
        """새 게임 시작 성공 테스트"""
        # Given
        player_template_id = "PLAYER_TEMPLATE_001"
        start_cell_id = "CELL_VILLAGE_CENTER_001"
        
        # Mock 설정
        game_manager._create_game_session = AsyncMock(return_value="SESSION_001")
        game_manager._get_default_start_cell = AsyncMock(return_value=start_cell_id)
        game_manager._create_cell_instance = AsyncMock(return_value="CELL_INSTANCE_001")
        game_manager._create_player_instance = AsyncMock(return_value="PLAYER_INSTANCE_001")
        game_manager._link_player_to_session = AsyncMock()
        
        # When
        result = await game_manager.start_new_game(player_template_id, start_cell_id)
        
        # Then
        assert result == "SESSION_001"
        assert game_manager.current_session_id == "SESSION_001"
        assert game_manager.current_player_id == "PLAYER_INSTANCE_001"
    
    @pytest.mark.asyncio
    async def test_start_new_game_without_start_cell(self, game_manager):
        """기본 시작 셀 사용 테스트"""
        # Given
        player_template_id = "PLAYER_TEMPLATE_001"
        
        # Mock 설정
        game_manager._create_game_session = AsyncMock(return_value="SESSION_001")
        game_manager._get_default_start_cell = AsyncMock(return_value="DEFAULT_CELL_001")
        game_manager._create_cell_instance = AsyncMock(return_value="CELL_INSTANCE_001")
        game_manager._create_player_instance = AsyncMock(return_value="PLAYER_INSTANCE_001")
        game_manager._link_player_to_session = AsyncMock()
        
        # When
        result = await game_manager.start_new_game(player_template_id)
        
        # Then
        assert result == "SESSION_001"
        game_manager._get_default_start_cell.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_start_new_game_failure(self, game_manager):
        """새 게임 시작 실패 테스트"""
        # Given
        player_template_id = "INVALID_TEMPLATE"
        
        # Mock 설정 - 실패 시나리오
        game_manager._create_game_session = AsyncMock(side_effect=Exception("Database error"))
        
        # When & Then
        with pytest.raises(Exception, match="Database error"):
            await game_manager.start_new_game(player_template_id)
    
    def test_dependency_injection(self, mock_dependencies):
        """의존성 주입 테스트"""
        # Given
        db_connection = mock_dependencies['db_connection']
        game_data_repo = mock_dependencies['game_data_repo']
        runtime_data_repo = mock_dependencies['runtime_data_repo']
        reference_layer_repo = mock_dependencies['reference_layer_repo']
        game_data_factory = mock_dependencies['game_data_factory']
        instance_factory = mock_dependencies['instance_factory']
        
        # When
        game_manager = GameManager(
            db_connection=db_connection,
            game_data_repo=game_data_repo,
            runtime_data_repo=runtime_data_repo,
            reference_layer_repo=reference_layer_repo,
            game_data_factory=game_data_factory,
            instance_factory=instance_factory
        )
        
        # Then
        assert game_manager.db == db_connection
        assert game_manager.game_data == game_data_repo
        assert game_manager.runtime_data == runtime_data_repo
        assert game_manager.reference_layer == reference_layer_repo
        assert game_manager.game_data_factory == game_data_factory
        assert game_manager.instance_factory == instance_factory
