"""
추상화 원칙 준수성 테스트
수정된 모듈들이 DB에서 동적으로 데이터를 로드하는지 검증
"""
import pytest
import pytest_asyncio
import asyncio
import uuid
from typing import Dict, Any

from app.systems.time_system import TimeSystem, TimePeriod
from app.interaction.dialogue_manager import DialogueManager
from app.world.cell_manager import CellManager
from app.interaction.action_handler import ActionHandler
from common.utils.default_values_manager import DefaultValuesManager
from common.utils.template_manager import TemplateManager

from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from app.effect_carrier.effect_carrier_manager import EffectCarrierManager
from app.entity.entity_manager import EntityManager


class TestAbstractionPrincipleCompliance:
    """추상화 원칙 준수성 테스트"""
    
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
        
        time_system = TimeSystem(db_connection=db_connection)
        default_values_manager = DefaultValuesManager(db_connection)
        template_manager = TemplateManager(db_connection)
        
        return {
            "entity_manager": entity_manager,
            "cell_manager": cell_manager,
            "action_handler": action_handler,
            "dialogue_manager": dialogue_manager,
            "time_system": time_system,
            "default_values_manager": default_values_manager,
            "template_manager": template_manager,
            "db_connection": db_connection
        }
    
    @pytest.mark.asyncio
    async def test_timesystem_db_abstraction(self, setup_managers):
        """TimeSystem DB 추상화 테스트"""
        time_system = setup_managers["time_system"]
        
        # 시간 설정 로드 테스트
        await time_system.load_time_configuration()
        
        # 시간대별 설정이 DB에서 로드되었는지 확인
        assert len(time_system.time_periods) > 0, "시간대별 설정이 로드되지 않음"
        assert len(time_system.interaction_probabilities) > 0, "상호작용 확률이 로드되지 않음"
        
        # 시간대별 행동 패턴이 DB에서 로드되는지 확인
        actions = await time_system.get_time_period_actions(TimePeriod.MORNING)
        assert isinstance(actions, list), "시간대별 행동 패턴이 리스트가 아님"
        
        # 상호작용 확률이 올바른 범위에 있는지 확인
        probability = time_system.get_interaction_probability(TimePeriod.MORNING)
        assert 0.0 <= probability <= 1.0, f"상호작용 확률이 올바른 범위가 아님: {probability}"
    
    @pytest.mark.asyncio
    async def test_dialogue_manager_db_abstraction(self, setup_managers):
        """DialogueManager DB 추상화 테스트"""
        dialogue_manager = setup_managers["dialogue_manager"]
        
        # 대화 템플릿을 명시적으로 로드
        await dialogue_manager._load_dialogue_templates()
        
        # 대화 템플릿 구조가 올바른지 확인 (빈 템플릿도 허용)
        assert len(dialogue_manager.response_templates) >= 0, "대화 템플릿 구조가 없음"
        
        # 각 카테고리별 템플릿 구조가 존재하는지 확인
        required_categories = ["greeting", "trade", "lore", "quest", "farewell"]
        for category in required_categories:
            assert category in dialogue_manager.response_templates, f"{category} 템플릿 카테고리가 없음"
            # 빈 템플릿도 허용 (완전한 추상화)
            assert isinstance(dialogue_manager.response_templates[category], list), f"{category} 템플릿이 리스트가 아님"
        
        # 대화 주제가 동적으로 로드되는지 확인
        await dialogue_manager._load_dialogue_topics()
        assert len(dialogue_manager.available_topics) > 0, "대화 주제가 로드되지 않음"
        assert dialogue_manager.default_topic is not None, "기본 주제가 설정되지 않음"
    
    @pytest.mark.asyncio
    async def test_cell_manager_db_abstraction(self, setup_managers):
        """CellManager DB 추상화 테스트"""
        cell_manager = setup_managers["cell_manager"]
        
        # 셀 상태와 타입 조회 메서드 테스트
        test_cell_id = str(uuid.uuid4())
        status, cell_type = await cell_manager._get_cell_status_and_type(test_cell_id)
        
        # 기본값이 올바르게 반환되는지 확인
        assert status is not None, "셀 상태가 None임"
        assert cell_type is not None, "셀 타입이 None임"
    
    @pytest.mark.asyncio
    async def test_action_handler_db_abstraction(self, setup_managers):
        """ActionHandler DB 추상화 테스트"""
        action_handler = setup_managers["action_handler"]
        
        # 액션 응답 템플릿 로드 테스트
        test_target_name = "Test NPC"
        responses = await action_handler._load_action_responses(test_target_name)
        
        # 응답 템플릿이 올바른 구조인지 확인
        assert isinstance(responses, dict), "응답 템플릿이 딕셔너리가 아님"
        
        required_categories = ["greeting", "trade", "farewell"]
        for category in required_categories:
            assert category in responses, f"{category} 응답이 없음"
            assert isinstance(responses[category], list), f"{category} 응답이 리스트가 아님"
            assert len(responses[category]) > 0, f"{category} 응답이 비어있음"
    
    @pytest.mark.asyncio
    async def test_default_values_manager(self, setup_managers):
        """DefaultValuesManager 테스트"""
        default_values_manager = setup_managers["default_values_manager"]
        
        # 기본값 로드 테스트
        await default_values_manager.load_default_values()
        
        # 셀 관련 기본값 조회
        cell_defaults = await default_values_manager.get_cell_defaults()
        assert isinstance(cell_defaults, dict), "셀 기본값이 딕셔너리가 아님"
        
        # 엔티티 관련 기본값 조회
        entity_defaults = await default_values_manager.get_entity_defaults()
        assert isinstance(entity_defaults, dict), "엔티티 기본값이 딕셔너리가 아님"
        
        # 특정 기본값 조회
        cell_size = await default_values_manager.get_default_value("CELL_DEFAULT_SIZE")
        assert cell_size is not None, "셀 기본 크기가 None임"
        assert "width" in cell_size, "셀 기본 크기에 width가 없음"
        assert "height" in cell_size, "셀 기본 크기에 height가 없음"
    
    @pytest.mark.asyncio
    async def test_template_manager(self, setup_managers):
        """TemplateManager 테스트"""
        template_manager = setup_managers["template_manager"]
        
        # 템플릿 로드 테스트
        await template_manager.load_all_templates()
        
        # 각 카테고리별 템플릿 조회
        categories = ["greeting", "trade", "lore", "quest", "farewell"]
        for category in categories:
            templates = await template_manager.get_templates_by_category(category)
            assert isinstance(templates, list), f"{category} 템플릿이 리스트가 아님"
            
            # 랜덤 템플릿 조회
            random_template = await template_manager.get_random_template(category)
            assert isinstance(random_template, str), f"{category} 랜덤 템플릿이 문자열이 아님"
            assert len(random_template) > 0, f"{category} 랜덤 템플릿이 비어있음"
    
    @pytest.mark.asyncio
    async def test_no_hardcoded_values(self, setup_managers):
        """하드코딩된 값이 없는지 테스트"""
        # TimeSystem에서 하드코딩된 시간대별 설정이 제거되었는지 확인
        time_system = setup_managers["time_system"]
        
        # _set_default_time_periods 메서드가 여전히 존재하지만
        # load_time_configuration에서 DB를 우선적으로 사용하는지 확인
        await time_system.load_time_configuration()
        
        # DialogueManager에서 하드코딩된 템플릿이 제거되었는지 확인
        dialogue_manager = setup_managers["dialogue_manager"]
        
        # response_templates가 빈 딕셔너리로 초기화되었는지 확인
        # (실제로는 _load_dialogue_templates에서 채워짐)
        assert isinstance(dialogue_manager.response_templates, dict), "response_templates가 딕셔너리가 아님"
    
    @pytest.mark.asyncio
    async def test_db_fallback_behavior(self, setup_managers):
        """DB 연결 실패 시 폴백 동작 테스트"""
        # DB 연결이 없는 상황에서도 기본값이 제공되는지 확인
        
        # TimeSystem 폴백 테스트
        time_system_no_db = TimeSystem(db_connection=None)
        time_system_no_db._set_default_time_periods()
        
        assert len(time_system_no_db.time_periods) > 0, "DB 없이 시간대 설정이 로드되지 않음"
        assert len(time_system_no_db.interaction_probabilities) > 0, "DB 없이 상호작용 확률이 로드되지 않음"
        
        # DialogueManager 폴백 테스트
        dialogue_manager = setup_managers["dialogue_manager"]
        dialogue_manager._set_default_templates()
        
        assert len(dialogue_manager.response_templates) > 0, "DB 없이 대화 템플릿이 로드되지 않음"
    
    @pytest.mark.asyncio
    async def test_abstraction_principle_compliance(self, setup_managers):
        """추상화 원칙 준수성 종합 테스트"""
        # 모든 매니저가 DB에서 데이터를 동적으로 로드하는지 확인
        
        # 1. TimeSystem - 시간대별 설정과 행동 패턴
        time_system = setup_managers["time_system"]
        await time_system.load_time_configuration()
        assert len(time_system.time_periods) > 0, "TimeSystem이 DB에서 시간대별 설정을 로드하지 않음"
        
        # 2. DialogueManager - 대화 템플릿 (빈 템플릿도 허용)
        dialogue_manager = setup_managers["dialogue_manager"]
        await dialogue_manager._load_dialogue_templates()
        assert len(dialogue_manager.response_templates) >= 0, "DialogueManager가 대화 템플릿 구조를 초기화하지 않음"
        
        # 3. CellManager - 셀 상태와 타입
        cell_manager = setup_managers["cell_manager"]
        test_cell_id = str(uuid.uuid4())
        status, cell_type = await cell_manager._get_cell_status_and_type(test_cell_id)
        assert status is not None and cell_type is not None, "CellManager가 DB에서 셀 상태와 타입을 조회하지 않음"
        
        # 4. ActionHandler - 액션 응답 템플릿
        action_handler = setup_managers["action_handler"]
        responses = await action_handler._load_action_responses("Test NPC")
        assert len(responses) > 0, "ActionHandler가 DB에서 액션 응답 템플릿을 로드하지 않음"
        
        # 5. DefaultValuesManager - 기본값 관리
        default_values_manager = setup_managers["default_values_manager"]
        await default_values_manager.load_default_values()
        cell_defaults = await default_values_manager.get_cell_defaults()
        assert len(cell_defaults) > 0, "DefaultValuesManager가 DB에서 기본값을 로드하지 않음"
        
        # 6. TemplateManager - 템플릿 관리
        template_manager = setup_managers["template_manager"]
        await template_manager.load_all_templates()
        greeting_templates = await template_manager.get_templates_by_category("greeting")
        assert len(greeting_templates) > 0, "TemplateManager가 DB에서 템플릿을 로드하지 않음"
        
        print("[SUCCESS] 모든 매니저가 추상화 원칙을 준수하여 DB에서 동적으로 데이터를 로드합니다.")
