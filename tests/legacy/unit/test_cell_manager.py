"""
CellManager 테스트
"""
import pytest
import uuid
from unittest.mock import Mock, AsyncMock
from app.world.cell_manager import (
    CellManager, CellData, CellContent, CellResult, CellType, CellStatus
)
from app.entity.entity_manager import EntityManager
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository


class TestCellManager:
    """CellManager 테스트 클래스"""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Mock 의존성들"""
        mock_db = Mock(spec=DatabaseConnection)
        
        # Mock pool을 await 가능하게 설정
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()
        mock_conn.fetchrow = AsyncMock()
        mock_conn.fetch = AsyncMock()
        
        # acquire()가 매번 새로운 context manager를 반환하도록 설정
        def acquire():
            new_context_manager = AsyncMock()
            new_context_manager.__aenter__ = AsyncMock(return_value=mock_conn)
            new_context_manager.__aexit__ = AsyncMock(return_value=None)
            return new_context_manager
        mock_pool.acquire = acquire
        
        # Mock pool을 await 가능하게 설정
        async def get_pool():
            return mock_pool
        mock_db.pool = get_pool()
        
        return {
            'db_connection': mock_db,
            'game_data_repo': Mock(spec=GameDataRepository),
            'runtime_data_repo': Mock(spec=RuntimeDataRepository),
            'reference_layer_repo': Mock(spec=ReferenceLayerRepository),
            'entity_manager': Mock(spec=EntityManager)
        }
    
    @pytest.fixture
    def cell_manager(self, mock_dependencies):
        """CellManager 인스턴스"""
        return CellManager(
            db_connection=mock_dependencies['db_connection'],
            game_data_repo=mock_dependencies['game_data_repo'],
            runtime_data_repo=mock_dependencies['runtime_data_repo'],
            reference_layer_repo=mock_dependencies['reference_layer_repo'],
            entity_manager=mock_dependencies['entity_manager']
        )
    
    def test_initialization(self, cell_manager, mock_dependencies):
        """초기화 테스트"""
        # Given & When
        # CellManager 인스턴스 생성
        
        # Then
        assert cell_manager.db == mock_dependencies['db_connection']
        assert cell_manager.game_data == mock_dependencies['game_data_repo']
        assert cell_manager.runtime_data == mock_dependencies['runtime_data_repo']
        assert cell_manager.reference_layer == mock_dependencies['reference_layer_repo']
        assert cell_manager.entity_manager == mock_dependencies['entity_manager']
        assert cell_manager._cell_cache == {}
        assert cell_manager._content_cache == {}
    
    @pytest.mark.asyncio
    async def test_create_cell_success(self, cell_manager):
        """셀 생성 성공 테스트"""
        # Given
        static_cell_id = "CELL_VILLAGE_CENTER_001"  # 정적 셀 템플릿 ID
        session_id = str(uuid.uuid4())

        # When
        result = await cell_manager.create_cell(
            static_cell_id=static_cell_id,
            session_id=session_id
        )
        
        # Then
        assert result.success is True
        assert result.cell is not None
        assert result.cell.cell_id is not None
        assert result.cell.cell_type == CellType.INDOOR
    
    @pytest.mark.asyncio
    async def test_create_cell_invalid_static_id(self, cell_manager):
        """잘못된 정적 셀 ID로 셀 생성 실패 테스트"""
        # Given
        static_cell_id = "INVALID_ID"
        session_id = str(uuid.uuid4())

        # When
        result = await cell_manager.create_cell(
            static_cell_id=static_cell_id,
            session_id=session_id
        )
        
        # Then
        assert result.success is False
        assert result.cell is None
        assert "정적 셀 템플릿을 찾을 수 없습니다" in result.message
    
    @pytest.mark.asyncio
    async def test_create_cell_missing_session(self, cell_manager):
        """세션이 없는 경우 셀 생성 실패 테스트"""
        # Given
        static_cell_id = "CELL_VILLAGE_CENTER_001"
        session_id = "INVALID_SESSION"

        # When
        result = await cell_manager.create_cell(
            static_cell_id=static_cell_id,
            session_id=session_id
        )
        
        # Then
        assert result.success is False
        assert result.cell is None
        assert "세션을 찾을 수 없습니다" in result.message
    
    @pytest.mark.asyncio
    async def test_get_cell_from_cache(self, cell_manager):
        """캐시에서 셀 조회 테스트"""
        # Given
        cell_data = CellData(
            cell_id="test-id",
            name="Test Cell",
            cell_type=CellType.INDOOR,
            location_id="test-location-id"
        )
        
        # 캐시에 셀 추가
        cell_manager._cell_cache["test-id"] = cell_data
        
        # When
        result = await cell_manager.get_cell("test-id")
        
        # Then
        assert result.success is True
        assert result.cell == cell_data
        assert result.message == "캐시에서 조회"
    
    @pytest.mark.asyncio
    async def test_get_cell_not_found(self, cell_manager):
        """존재하지 않는 셀 조회 테스트"""
        # Given
        cell_id = "non-existent-id"
        
        # When
        result = await cell_manager.get_cell(cell_id)
        
        # Then
        assert result.success is False
        assert result.cell is None
        assert f"셀 '{cell_id}'를 찾을 수 없습니다." in result.message
    
    @pytest.mark.asyncio
    async def test_load_cell_content_success(self, cell_manager):
        """셀 컨텐츠 로딩 성공 테스트"""
        # Given
        cell_data = CellData(
            cell_id="test-id",
            name="Test Cell",
            cell_type=CellType.INDOOR,
            location_id="test-location-id"
        )
        
        # 캐시에 셀 추가
        cell_manager._cell_cache["test-id"] = cell_data
        
        # When
        result = await cell_manager.load_cell_content("test-id")
        
        # Then
        assert result.success is True
        assert result.cell == cell_data
        assert result.content is not None
        assert result.message == "데이터베이스에서 컨텐츠 로딩"
    
    @pytest.mark.asyncio
    async def test_load_cell_content_not_found(self, cell_manager):
        """존재하지 않는 셀 컨텐츠 로딩 테스트"""
        # Given
        cell_id = "non-existent-id"
        
        # When
        result = await cell_manager.load_cell_content(cell_id)
        
        # Then
        assert result.success is False
        assert result.cell is None
        assert result.content is None
        assert f"셀 '{cell_id}'를 찾을 수 없습니다." in result.message
    
    @pytest.mark.asyncio
    async def test_enter_cell_success(self, cell_manager):
        """셀 진입 성공 테스트"""
        # Given
        cell_data = CellData(
            cell_id="test-id",
            name="Test Cell",
            cell_type=CellType.INDOOR,
            status=CellStatus.ACTIVE,
            location_id="test-location-id"
        )
        
        # 캐시에 셀 추가
        cell_manager._cell_cache["test-id"] = cell_data
        
        # Mock DB 호출을 우회하기 위해 _add_player_to_cell을 Mock
        cell_manager._add_player_to_cell = AsyncMock()
        
        player_id = "player-123"
        
        # When
        result = await cell_manager.enter_cell("test-id", player_id)
        
        # Then
        assert result.success is True
        assert result.cell == cell_data
        assert result.content is not None
        assert f"셀 '{cell_data.name}'에 진입했습니다." in result.message
    
    @pytest.mark.asyncio
    async def test_enter_cell_locked(self, cell_manager):
        """잠긴 셀 진입 실패 테스트"""
        # Given
        cell_data = CellData(
            cell_id="test-id",
            name="Test Cell",
            cell_type=CellType.INDOOR,
            status=CellStatus.LOCKED,
            location_id="test-location-id"
        )
        
        # 캐시에 셀 추가
        cell_manager._cell_cache["test-id"] = cell_data
        
        player_id = "player-123"
        
        # When
        result = await cell_manager.enter_cell("test-id", player_id)
        
        # Then
        assert result.success is False
        assert result.cell is None
        assert result.message == "잠긴 셀입니다."
    
    @pytest.mark.asyncio
    async def test_enter_cell_not_found(self, cell_manager):
        """존재하지 않는 셀 진입 테스트"""
        # Given
        cell_id = "non-existent-id"
        player_id = "player-123"
        
        # When
        result = await cell_manager.enter_cell(cell_id, player_id)
        
        # Then
        assert result.success is False
        assert result.cell is None
        assert f"셀 '{cell_id}'를 찾을 수 없습니다." in result.message
    
    @pytest.mark.asyncio
    async def test_leave_cell_success(self, cell_manager):
        """셀 떠나기 성공 테스트"""
        # Given
        cell_data = CellData(
            cell_id="test-id",
            name="Test Cell",
            cell_type=CellType.INDOOR,
            location_id="test-location-id"
        )
        
        # 캐시에 셀 추가
        cell_manager._cell_cache["test-id"] = cell_data
        
        player_id = "player-123"
        
        # When
        result = await cell_manager.leave_cell("test-id", player_id)
        
        # Then
        assert result.success is True
        assert result.cell == cell_data
        assert f"셀 '{cell_data.name}'에서 떠났습니다." in result.message
    
    @pytest.mark.asyncio
    async def test_leave_cell_not_found(self, cell_manager):
        """존재하지 않는 셀 떠나기 테스트"""
        # Given
        cell_id = "non-existent-id"
        player_id = "player-123"
        
        # When
        result = await cell_manager.leave_cell(cell_id, player_id)
        
        # Then
        assert result.success is False
        assert result.cell is None
        assert f"셀 '{cell_id}'를 찾을 수 없습니다." in result.message
    
    @pytest.mark.asyncio
    async def test_update_cell_success(self, cell_manager):
        """셀 업데이트 성공 테스트"""
        # Given
        cell_data = CellData(
            cell_id="test-id",
            name="Test Cell",
            cell_type=CellType.INDOOR,
            properties={"lighting": "dim"},
            location_id="test-location-id"
        )
        
        # 캐시에 셀 추가
        cell_manager._cell_cache["test-id"] = cell_data
        
        updates = {"lighting": "bright", "temperature": 25}
        
        # When
        result = await cell_manager.update_cell("test-id", updates)
        
        # Then
        assert result.success is True
        assert result.cell is not None
        assert result.cell.properties["lighting"] == "bright"
        assert result.cell.properties["temperature"] == 25
        assert result.message == f"셀 '{cell_data.name}' 업데이트 완료"
    
    @pytest.mark.asyncio
    async def test_update_cell_not_found(self, cell_manager):
        """존재하지 않는 셀 업데이트 테스트"""
        # Given
        cell_id = "non-existent-id"
        updates = {"lighting": "bright"}
        
        # When
        result = await cell_manager.update_cell(cell_id, updates)
        
        # Then
        assert result.success is False
        assert result.cell is None
        assert f"셀 '{cell_id}'를 찾을 수 없습니다." in result.message
    
    @pytest.mark.asyncio
    async def test_list_cells(self, cell_manager):
        """셀 목록 조회 테스트"""
        # Given & When
        cells = await cell_manager.list_cells()
        
        # Then
        assert isinstance(cells, list)
    
    @pytest.mark.asyncio
    async def test_list_cells_with_filters(self, cell_manager):
        """필터링된 셀 목록 조회 테스트"""
        # Given
        cell_type = CellType.INDOOR
        status = CellStatus.ACTIVE
        
        # When
        cells = await cell_manager.list_cells(
            cell_type=cell_type,
            status=status
        )
        
        # Then
        assert isinstance(cells, list)
    
    @pytest.mark.asyncio
    async def test_clear_cache(self, cell_manager):
        """캐시 초기화 테스트"""
        # Given
        cell_data = CellData(
            cell_id="test-id",
            name="Test Cell",
            cell_type=CellType.INDOOR,
            location_id="test-location-id"
        )
        
        content_data = CellContent()
        
        # 캐시에 데이터 추가
        cell_manager._cell_cache["test-id"] = cell_data
        cell_manager._content_cache["test-id"] = content_data
        
        assert len(cell_manager._cell_cache) == 1
        assert len(cell_manager._content_cache) == 1
        
        # When
        await cell_manager.clear_cache()
        
        # Then
        assert len(cell_manager._cell_cache) == 0
        assert len(cell_manager._content_cache) == 0
    
    def test_cell_data_validation(self):
        """CellData 모델 검증 테스트"""
        # Given
        cell_data = CellData(
            cell_id="test-id",
            name="Test Cell",
            cell_type=CellType.INDOOR,
            status=CellStatus.ACTIVE,
            description="A test cell",
            properties={"lighting": "bright"},
            location_id="test-location-id"
        )
        
        # When & Then
        assert cell_data.cell_id == "test-id"
        assert cell_data.name == "Test Cell"
        assert cell_data.cell_type == CellType.INDOOR
        assert cell_data.status == CellStatus.ACTIVE
        assert cell_data.description == "A test cell"
        assert cell_data.properties == {"lighting": "bright"}
    
    def test_cell_content_validation(self):
        """CellContent 모델 검증 테스트"""
        # Given
        content = CellContent(
            entities=[],
            objects=[],
            events=[],
            atmosphere={"mood": "peaceful"}
        )
        
        # When & Then
        assert isinstance(content.entities, list)
        assert isinstance(content.objects, list)
        assert isinstance(content.events, list)
        assert content.atmosphere == {"mood": "peaceful"}
    
    def test_cell_result_success(self):
        """CellResult 성공 결과 테스트"""
        # Given
        cell_data = CellData(
            cell_id="test-id",
            name="Test Cell",
            cell_type=CellType.INDOOR,
            location_id="test-location-id"
        )
        
        content_data = CellContent()
        
        # When
        result = CellResult.success_result(cell_data, content_data, "Test message")
        
        # Then
        assert result.success is True
        assert result.cell == cell_data
        assert result.content == content_data
        assert result.message == "Test message"
        assert result.error is None
    
    def test_cell_result_error(self):
        """CellResult 에러 결과 테스트"""
        # When
        result = CellResult.error_result("Test error", "Detailed error")
        
        # Then
        assert result.success is False
        assert result.cell is None
        assert result.content is None
        assert result.message == "Test error"
        assert result.error == "Detailed error"
