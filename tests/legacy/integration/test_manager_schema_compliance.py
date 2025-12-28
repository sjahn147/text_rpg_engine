"""
매니저 클래스 스키마 준수성 통합 테스트
"""
import pytest
import pytest_asyncio
import asyncio
import uuid
from typing import Dict, Any

from app.entity.entity_manager import EntityManager, EntityType
from app.world.cell_manager import CellManager
from app.interaction.action_handler import ActionHandler, ActionType
from app.interaction.dialogue_manager import DialogueManager
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from app.effect_carrier.effect_carrier_manager import EffectCarrierManager


class TestManagerSchemaCompliance:
    """매니저 클래스 스키마 준수성 테스트"""
    
    @pytest.fixture
    def setup_managers(self):
        """매니저 클래스들 초기화"""
        db_connection = DatabaseConnection()
        game_data_repo = GameDataRepository(db_connection)
        runtime_data_repo = RuntimeDataRepository(db_connection)
        reference_layer_repo = ReferenceLayerRepository(db_connection)
        effect_carrier_manager = EffectCarrierManager(db_connection, game_data_repo, runtime_data_repo, reference_layer_repo)
        
        entity_manager = EntityManager(
            db_connection, game_data_repo, runtime_data_repo, 
            reference_layer_repo, effect_carrier_manager
        )
        
        cell_manager = CellManager(
            db_connection, game_data_repo, runtime_data_repo,
            reference_layer_repo, entity_manager, effect_carrier_manager
        )
        
        action_handler = ActionHandler(
            db_connection, game_data_repo, runtime_data_repo,
            reference_layer_repo, entity_manager, cell_manager, effect_carrier_manager
        )
        
        dialogue_manager = DialogueManager(
            db_connection, game_data_repo, runtime_data_repo,
            reference_layer_repo, entity_manager, effect_carrier_manager
        )
        
        return {
            "entity_manager": entity_manager,
            "cell_manager": cell_manager,
            "action_handler": action_handler,
            "dialogue_manager": dialogue_manager,
            "db_connection": db_connection
        }
    
    @pytest.mark.asyncio
    async def test_entity_manager_schema_compliance(self, setup_managers):
        """EntityManager 스키마 준수성 테스트"""
        managers = setup_managers
        entity_manager = managers["entity_manager"]
        
        # 스키마 검증
        schema_result = await entity_manager.validate_schema()
        assert schema_result["valid"], f"EntityManager schema validation failed: {schema_result['errors']}"
        
        # 정적 엔티티 템플릿에서 런타임 인스턴스 생성 테스트
        session_id = str(uuid.uuid4())
        static_entity_id = "NPC_MERCHANT_001"  # 정적 템플릿 ID
        
        result = await entity_manager.create_entity(
            static_entity_id=static_entity_id,
            session_id=session_id,
            custom_properties={"test": "value"}
        )
        
        assert result.success, f"Entity creation failed: {result.message}"
        assert result.entity is not None
        assert result.entity.entity_id != static_entity_id  # UUID가 생성되어야 함
        assert result.entity.name == "상인 토마스"  # 정적 템플릿의 이름
    
    @pytest.mark.asyncio
    async def test_cell_manager_schema_compliance(self, setup_managers):
        """CellManager 스키마 준수성 테스트"""
        managers = setup_managers
        cell_manager = managers["cell_manager"]
        
        # 정적 셀 템플릿에서 런타임 인스턴스 생성 테스트
        session_id = str(uuid.uuid4())
        static_cell_id = "CELL_VILLAGE_CENTER_001"  # 정적 템플릿 ID
        
        result = await cell_manager.create_cell(
            static_cell_id=static_cell_id,
            session_id=session_id
        )
        
        assert result.success, f"Cell creation failed: {result.message}"
        assert result.cell is not None
        assert result.cell.cell_id != static_cell_id  # UUID가 생성되어야 함
        assert result.cell.name == "마을 광장"  # 정적 템플릿의 이름
    
    @pytest.mark.asyncio
    async def test_action_handler_schema_compliance(self, setup_managers):
        """ActionHandler 스키마 준수성 테스트"""
        managers = setup_managers
        action_handler = managers["action_handler"]
        
        # 세션 ID가 필요한지 테스트
        session_id = str(uuid.uuid4())
        player_id = "test_player"
        
        # wait 액션 테스트 (가장 간단한 액션)
        result = await action_handler.execute_action(
            action_type=ActionType.WAIT,
            player_id=player_id,
            session_id=session_id,
            parameters={"hours": 1}
        )
        
        assert result.success, f"Wait action failed: {result.message}"
        assert "대기했습니다" in result.message
    
    @pytest.mark.asyncio
    async def test_dialogue_manager_schema_compliance(self, setup_managers):
        """DialogueManager 스키마 준수성 테스트"""
        managers = setup_managers
        dialogue_manager = managers["dialogue_manager"]
        
        # 세션 ID가 필요한지 테스트
        session_id = str(uuid.uuid4())
        player_id = str(uuid.uuid4())  # UUID 형식으로 변경
        npc_id = str(uuid.uuid4())     # UUID 형식으로 변경
        
        # 대화 시작 테스트
        result = await dialogue_manager.start_dialogue(
            player_id=player_id,
            npc_id=npc_id,
            session_id=session_id,
            initial_topic="greeting"
        )
        
        # 엔티티가 존재하지 않으므로 실패해야 함 (정상적인 동작)
        assert not result.success, "Dialogue should fail with non-existent entities"
        # 플레이어나 NPC 중 하나라도 찾을 수 없으면 실패
        assert "찾을 수 없습니다" in result.message
    
    @pytest.mark.asyncio
    async def test_jsonb_handling_consistency(self, setup_managers):
        """JSONB 데이터 처리 일관성 테스트"""
        managers = setup_managers
        entity_manager = managers["entity_manager"]
        
        # JSONB 데이터가 올바르게 처리되는지 테스트
        session_id = str(uuid.uuid4())
        static_entity_id = "NPC_MERCHANT_001"
        
        custom_properties = {
            "test_jsonb": {"nested": {"value": 123}},
            "array_data": [1, 2, 3],
            "string_data": "test"
        }
        
        result = await entity_manager.create_entity(
            static_entity_id=static_entity_id,
            session_id=session_id,
            custom_properties=custom_properties
        )
        
        assert result.success, f"Entity creation with JSONB failed: {result.message}"
        assert result.entity.properties["test_jsonb"]["nested"]["value"] == 123
        assert result.entity.properties["array_data"] == [1, 2, 3]
        assert result.entity.properties["string_data"] == "test"
    
    @pytest.mark.asyncio
    async def test_session_centric_design(self, setup_managers):
        """세션 중심 설계 준수 테스트"""
        managers = setup_managers
        entity_manager = managers["entity_manager"]
        
        # 세션 ID 없이 엔티티 생성 시도 (실패해야 함)
        result = await entity_manager.create_entity(
            static_entity_id="NPC_MERCHANT_001",
            session_id="",  # 빈 세션 ID
            custom_properties={}
        )
        
        assert not result.success, "Entity creation should fail without valid session ID"
        assert "유효하지 않은 세션 ID" in result.message
    
    @pytest.mark.asyncio
    async def test_static_vs_runtime_separation(self, setup_managers):
        """정적 데이터와 런타임 데이터 분리 테스트"""
        managers = setup_managers
        entity_manager = managers["entity_manager"]
        
        # 정적 템플릿 ID와 런타임 인스턴스 ID가 다른지 확인
        session_id = str(uuid.uuid4())
        static_entity_id = "NPC_MERCHANT_001"
        
        result = await entity_manager.create_entity(
            static_entity_id=static_entity_id,
            session_id=session_id,
            custom_properties={}
        )
        
        assert result.success, f"Entity creation failed: {result.message}"
        
        # 정적 ID와 런타임 ID가 달라야 함
        assert result.entity.entity_id != static_entity_id
        assert result.entity.entity_id.startswith(static_entity_id) == False  # UUID 형식이어야 함
        
        # 정적 템플릿의 이름이 유지되는지 확인
        assert result.entity.name == "상인 토마스"  # 정적 템플릿의 이름
    
    @pytest.mark.asyncio
    async def test_error_handling_improvements(self, setup_managers):
        """에러 처리 개선 테스트"""
        managers = setup_managers
        entity_manager = managers["entity_manager"]
        
        # 잘못된 엔티티 ID로 생성 시도 (정적 ID 형식이지만 존재하지 않는 ID)
        result = await entity_manager.create_entity(
            static_entity_id="NPC_NONEXISTENT_001",  # 정적 ID 형식이지만 존재하지 않음
            session_id=str(uuid.uuid4()),
            custom_properties={}
        )
        
        assert not result.success, "Entity creation should fail with invalid ID"
        assert "정적 엔티티 템플릿을 찾을 수 없습니다" in result.message
    
    @pytest.mark.asyncio
    async def test_schema_validation_integration(self, setup_managers):
        """스키마 검증 통합 테스트"""
        managers = setup_managers
        entity_manager = managers["entity_manager"]
        
        # 스키마 검증 실행
        validation_result = await entity_manager.validate_schema()
        
        assert "manager" in validation_result
        assert validation_result["manager"] == "EntityManager"
        assert "valid" in validation_result
        assert "errors" in validation_result
        assert "warnings" in validation_result
        
        # 스키마가 유효한지 확인
        if not validation_result["valid"]:
            print(f"Schema validation errors: {validation_result['errors']}")
            print(f"Schema validation warnings: {validation_result['warnings']}")
        
        # 최소한 에러가 없어야 함
        assert len(validation_result["errors"]) == 0, f"Schema validation errors: {validation_result['errors']}"
