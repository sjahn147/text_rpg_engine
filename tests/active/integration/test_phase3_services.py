"""
Phase 3 Service Layer 통합 테스트

목적:
- JournalService, MapService, ExplorationService 기능 검증
"""
import pytest
import pytest_asyncio
from common.utils.logger import logger

from database.connection import DatabaseConnection
from app.services.gameplay.journal_service import JournalService
from app.services.gameplay.map_service import MapService
from app.services.gameplay.exploration_service import ExplorationService
from app.core.game_manager import GameManager
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from database.factories.game_data_factory import GameDataFactory
from database.factories.instance_factory import InstanceFactory


@pytest.mark.asyncio
class TestPhase3Services:
    """Phase 3 Service Layer 통합 테스트"""
    
    @pytest.mark.integration
    async def test_journal_service(self, db_connection):
        """JournalService 테스트"""
        logger.info("[통합 테스트] JournalService 테스트 시작")
        
        # 게임 시작
        game_data_repo = GameDataRepository(db_connection)
        runtime_data_repo = RuntimeDataRepository(db_connection)
        reference_layer_repo = ReferenceLayerRepository(db_connection)
        game_data_factory = GameDataFactory(db_connection)
        instance_factory = InstanceFactory(db_connection)
        
        game_manager = GameManager(
            db_connection=db_connection,
            game_data_repo=game_data_repo,
            runtime_data_repo=runtime_data_repo,
            reference_layer_repo=reference_layer_repo,
            game_data_factory=game_data_factory,
            instance_factory=instance_factory
        )
        
        session_id = await game_manager.start_new_game("NPC_VILLAGER_001")
        assert session_id is not None, "게임 세션 생성 실패"
        
        # JournalService 생성
        journal_service = JournalService(db_connection)
        
        # 저널 데이터 조회
        result = await journal_service.get_journal(session_id)
        assert result.get('success') is True, "저널 데이터 조회 실패"
        assert 'journal' in result, "journal이 없음"
        
        logger.info(f"[OK] JournalService 테스트 성공")
    
    @pytest.mark.integration
    async def test_map_service(self, db_connection):
        """MapService 테스트"""
        logger.info("[통합 테스트] MapService 테스트 시작")
        
        # 게임 시작
        game_data_repo = GameDataRepository(db_connection)
        runtime_data_repo = RuntimeDataRepository(db_connection)
        reference_layer_repo = ReferenceLayerRepository(db_connection)
        game_data_factory = GameDataFactory(db_connection)
        instance_factory = InstanceFactory(db_connection)
        
        game_manager = GameManager(
            db_connection=db_connection,
            game_data_repo=game_data_repo,
            runtime_data_repo=runtime_data_repo,
            reference_layer_repo=reference_layer_repo,
            game_data_factory=game_data_factory,
            instance_factory=instance_factory
        )
        
        session_id = await game_manager.start_new_game("NPC_VILLAGER_001")
        assert session_id is not None, "게임 세션 생성 실패"
        
        # MapService 생성
        map_service = MapService(db_connection)
        
        # 맵 데이터 조회
        result = await map_service.get_map_data(session_id)
        assert result.get('success') is True, "맵 데이터 조회 실패"
        assert 'map_data' in result, "map_data가 없음"
        
        # 발견한 셀 목록 조회
        discovered_result = await map_service.get_discovered_cells(session_id)
        assert discovered_result.get('success') is True, "발견한 셀 목록 조회 실패"
        assert 'discovered_cells' in discovered_result, "discovered_cells가 없음"
        
        logger.info(f"[OK] MapService 테스트 성공")
    
    @pytest.mark.integration
    async def test_exploration_service(self, db_connection):
        """ExplorationService 테스트"""
        logger.info("[통합 테스트] ExplorationService 테스트 시작")
        
        # 게임 시작
        game_data_repo = GameDataRepository(db_connection)
        runtime_data_repo = RuntimeDataRepository(db_connection)
        reference_layer_repo = ReferenceLayerRepository(db_connection)
        game_data_factory = GameDataFactory(db_connection)
        instance_factory = InstanceFactory(db_connection)
        
        game_manager = GameManager(
            db_connection=db_connection,
            game_data_repo=game_data_repo,
            runtime_data_repo=runtime_data_repo,
            reference_layer_repo=reference_layer_repo,
            game_data_factory=game_data_factory,
            instance_factory=instance_factory
        )
        
        session_id = await game_manager.start_new_game("NPC_VILLAGER_001")
        assert session_id is not None, "게임 세션 생성 실패"
        
        # ExplorationService 생성
        exploration_service = ExplorationService(db_connection)
        
        # 탐험 진행도 조회
        result = await exploration_service.get_exploration_progress(session_id)
        assert result.get('success') is True, "탐험 진행도 조회 실패"
        assert 'exploration_progress' in result, "exploration_progress가 없음"
        
        progress = result['exploration_progress']
        assert 'discovered_cells' in progress, "discovered_cells가 없음"
        assert 'total_cells' in progress, "total_cells가 없음"
        assert 'progress_percentage' in progress, "progress_percentage가 없음"
        
        logger.info(f"[OK] ExplorationService 테스트 성공: {progress['progress_percentage']}%")

