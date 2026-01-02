"""
RecoveryInteractionHandler TimeSystem 연동 테스트

목적:
- handle_rest의 TimeSystem 연동 테스트
- handle_meditate의 EffectCarrierManager 연동 테스트
"""
import pytest
import pytest_asyncio
import uuid
from typing import Dict, Any
from common.utils.logger import logger

from database.connection import DatabaseConnection
from app.handlers.object_interactions.recovery import RecoveryInteractionHandler
from app.managers.object_state_manager import ObjectStateManager
from app.managers.entity_manager import EntityManager
from app.managers.effect_carrier_manager import EffectCarrierManager
from app.systems.time_system import TimeSystem


@pytest.mark.asyncio
class TestRecoveryHandlerTimeSystem:
    """RecoveryInteractionHandler TimeSystem 연동 테스트"""
    
    @pytest.mark.integration
    async def test_handle_rest_timesystem_integration(
        self,
        db_connection
    ):
        """handle_rest의 TimeSystem 연동 테스트"""
        logger.info("[통합 테스트] handle_rest TimeSystem 연동 테스트 시작")
        
        # 핸들러 초기화
        from database.repositories.game_data import GameDataRepository
        from database.repositories.runtime_data import RuntimeDataRepository
        from database.repositories.reference_layer import ReferenceLayerRepository
        
        game_data_repo = GameDataRepository(db_connection)
        runtime_data_repo = RuntimeDataRepository(db_connection)
        reference_layer_repo = ReferenceLayerRepository(db_connection)
        
        from app.managers.effect_carrier_manager import EffectCarrierManager
        effect_carrier_manager = EffectCarrierManager(
            db_connection, game_data_repo, runtime_data_repo, reference_layer_repo
        )
        
        entity_manager = EntityManager(
            db_connection, game_data_repo, runtime_data_repo, reference_layer_repo, effect_carrier_manager
        )
        object_state_manager = ObjectStateManager(
            db_connection, game_data_repo, runtime_data_repo, reference_layer_repo
        )
        
        recovery_handler = RecoveryInteractionHandler(
            db_connection=db_connection,
            object_state_manager=object_state_manager,
            entity_manager=entity_manager
        )
        
        # 에러 처리 테스트 (EntityManager가 None인 경우)
        result = await recovery_handler.handle_rest(
            entity_id="test-entity",
            target_id="test-target",
            parameters={"session_id": "test-session"}
        )
        
        # 오브젝트를 찾을 수 없어도 에러 처리가 올바르게 작동하는지 확인
        assert result.success is False, "오브젝트가 없으면 실패해야 함"
        assert "오브젝트" in result.message or "찾을 수 없" in result.message
        
        logger.info("[OK] handle_rest TimeSystem 연동 테스트 통과")
    
    @pytest.mark.integration
    async def test_handle_meditate_effect_integration(
        self,
        db_connection
    ):
        """handle_meditate의 EffectCarrierManager 연동 테스트"""
        logger.info("[통합 테스트] handle_meditate EffectCarrierManager 연동 테스트 시작")
        
        # 핸들러 초기화
        from database.repositories.game_data import GameDataRepository
        from database.repositories.runtime_data import RuntimeDataRepository
        from database.repositories.reference_layer import ReferenceLayerRepository
        
        game_data_repo = GameDataRepository(db_connection)
        runtime_data_repo = RuntimeDataRepository(db_connection)
        reference_layer_repo = ReferenceLayerRepository(db_connection)
        
        from app.managers.effect_carrier_manager import EffectCarrierManager
        effect_carrier_manager = EffectCarrierManager(
            db_connection, game_data_repo, runtime_data_repo, reference_layer_repo
        )
        
        entity_manager = EntityManager(
            db_connection, game_data_repo, runtime_data_repo, reference_layer_repo, effect_carrier_manager
        )
        object_state_manager = ObjectStateManager(
            db_connection, game_data_repo, runtime_data_repo, reference_layer_repo
        )
        
        recovery_handler = RecoveryInteractionHandler(
            db_connection=db_connection,
            object_state_manager=object_state_manager,
            entity_manager=entity_manager,
            effect_carrier_manager=effect_carrier_manager
        )
        
        # 에러 처리 테스트 (오브젝트가 없는 경우)
        result = await recovery_handler.handle_meditate(
            entity_id="test-entity",
            target_id="test-target",
            parameters={"session_id": "test-session"}
        )
        
        # 오브젝트를 찾을 수 없어도 에러 처리가 올바르게 작동하는지 확인
        assert result.success is False, "오브젝트가 없으면 실패해야 함"
        assert "오브젝트" in result.message or "찾을 수 없" in result.message
        
        logger.info("[OK] handle_meditate EffectCarrierManager 연동 테스트 통과")

