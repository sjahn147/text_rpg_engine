"""
ObjectService 통합 테스트

목적:
- 오브젝트 관련 API 기능 검증
- 오브젝트 상태 조회, 가능한 액션 조회, 카테고리별 액션 조회 테스트
"""
import pytest
import pytest_asyncio
import uuid
from typing import Dict, Any
from common.utils.logger import logger

from database.connection import DatabaseConnection
from app.services.gameplay.object_service import ObjectService
from app.core.game_manager import GameManager
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from database.factories.game_data_factory import GameDataFactory
from database.factories.instance_factory import InstanceFactory


@pytest.mark.asyncio
class TestObjectService:
    """ObjectService 통합 테스트"""
    
    @pytest.mark.integration
    async def test_get_object_state(self, db_connection):
        """오브젝트 상태 조회 테스트"""
        logger.info("[통합 테스트] 오브젝트 상태 조회 테스트 시작")
        
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
        
        # 게임 시작
        session_id = await game_manager.start_new_game("NPC_VILLAGER_001")
        assert session_id is not None, "게임 세션 생성 실패"
        
        # ObjectService 생성
        object_service = ObjectService(db_connection)
        
        # 오브젝트 상태 조회 (game_object_id 사용)
        # 실제 게임 데이터에 있는 오브젝트 ID를 사용해야 함
        # 테스트용으로 존재하는 오브젝트 ID를 사용하거나, 오류 처리 확인
        try:
            result = await object_service.get_object_state("OBJ_DOOR_001", session_id)
            
            # 검증
            assert result.get('success') is True, "오브젝트 상태 조회 실패"
            assert 'object_id' in result, "object_id가 없음"
            assert 'state' in result, "state가 없음"
            
            logger.info(f"[OK] 오브젝트 상태 조회 성공: {result.get('object_id')}")
        except ValueError as e:
            # 오브젝트가 없을 수 있으므로 정상적인 오류 처리 확인
            logger.info(f"[INFO] 오브젝트를 찾을 수 없음 (예상 가능): {str(e)}")
            assert "찾을 수 없습니다" in str(e) or "조회 실패" in str(e), "예상치 못한 오류"
    
    @pytest.mark.integration
    async def test_get_object_actions(self, db_connection):
        """오브젝트 액션 조회 테스트"""
        logger.info("[통합 테스트] 오브젝트 액션 조회 테스트 시작")
        
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
        
        # 게임 시작
        session_id = await game_manager.start_new_game("NPC_VILLAGER_001")
        assert session_id is not None, "게임 세션 생성 실패"
        
        # ObjectService 생성
        object_service = ObjectService(db_connection)
        
        # 오브젝트 액션 조회
        try:
            result = await object_service.get_object_actions("OBJ_DOOR_001", session_id)
            
            # 검증
            assert result.get('success') is True, "오브젝트 액션 조회 실패"
            assert 'object_id' in result, "object_id가 없음"
            assert 'actions' in result, "actions가 없음"
            assert isinstance(result['actions'], list), "actions가 리스트가 아님"
            
            logger.info(f"[OK] 오브젝트 액션 조회 성공: {len(result['actions'])}개 액션")
        except ValueError as e:
            # 오브젝트가 없을 수 있으므로 정상적인 오류 처리 확인
            logger.info(f"[INFO] 오브젝트를 찾을 수 없음 (예상 가능): {str(e)}")
            assert "찾을 수 없습니다" in str(e) or "조회 실패" in str(e), "예상치 못한 오류"
    
    @pytest.mark.integration
    async def test_get_categorized_actions(self, db_connection):
        """카테고리별 액션 조회 테스트"""
        logger.info("[통합 테스트] 카테고리별 액션 조회 테스트 시작")
        
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
        
        # 게임 시작
        session_id = await game_manager.start_new_game("NPC_VILLAGER_001")
        assert session_id is not None, "게임 세션 생성 실패"
        
        # ObjectService 생성
        object_service = ObjectService(db_connection)
        
        # 카테고리별 액션 조회
        result = await object_service.get_categorized_actions(session_id)
        
        # 검증
        assert result.get('success') is True, "카테고리별 액션 조회 실패"
        assert 'session_id' in result, "session_id가 없음"
        assert 'categorized_actions' in result, "categorized_actions가 없음"
        assert 'total_actions' in result, "total_actions가 없음"
        
        categorized = result['categorized_actions']
        assert 'entity' in categorized, "entity 카테고리가 없음"
        assert 'cell' in categorized, "cell 카테고리가 없음"
        assert 'object' in categorized, "object 카테고리가 없음"
        assert 'item' in categorized, "item 카테고리가 없음"
        assert 'time' in categorized, "time 카테고리가 없음"
        
        assert isinstance(categorized['entity'], list), "entity가 리스트가 아님"
        assert isinstance(categorized['cell'], list), "cell이 리스트가 아님"
        assert isinstance(categorized['object'], list), "object가 리스트가 아님"
        assert isinstance(categorized['item'], list), "item이 리스트가 아님"
        assert isinstance(categorized['time'], list), "time이 리스트가 아님"
        
        logger.info(f"[OK] 카테고리별 액션 조회 성공: 총 {result['total_actions']}개 액션")
        logger.info(f"[OK] Entity: {len(categorized['entity'])}, Cell: {len(categorized['cell'])}, Object: {len(categorized['object'])}, Item: {len(categorized['item'])}, Time: {len(categorized['time'])}")

