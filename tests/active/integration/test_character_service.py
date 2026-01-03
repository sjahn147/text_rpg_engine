"""
CharacterService 통합 테스트

목적:
- 캐릭터 관련 API 기능 검증
- 캐릭터 능력치, 인벤토리, 장착 아이템, Effect Carrier, 스킬/주문 조회 테스트
"""
import pytest
import pytest_asyncio
import uuid
from typing import Dict, Any
from common.utils.logger import logger

from database.connection import DatabaseConnection
from app.services.gameplay.character_service import CharacterService
from app.core.game_manager import GameManager
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from database.factories.game_data_factory import GameDataFactory
from database.factories.instance_factory import InstanceFactory


@pytest.mark.asyncio
class TestCharacterService:
    """CharacterService 통합 테스트"""
    
    @pytest.mark.integration
    async def test_get_character_stats(self, db_connection):
        """캐릭터 능력치 조회 테스트"""
        logger.info("[통합 테스트] 캐릭터 능력치 조회 테스트 시작")
        
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
        
        # CharacterService 생성
        character_service = CharacterService(db_connection)
        
        # 캐릭터 능력치 조회
        result = await character_service.get_character_stats(session_id)
        
        # 검증
        assert result.get('success') is True, "캐릭터 능력치 조회 실패"
        assert 'entity_id' in result, "entity_id가 없음"
        assert 'entity_name' in result, "entity_name이 없음"
        assert 'stats' in result, "stats가 없음"
        assert 'base_stats' in result, "base_stats가 없음"
        assert 'current_stats' in result, "current_stats가 없음"
        
        logger.info(f"[OK] 캐릭터 능력치 조회 성공: {result.get('entity_name')}")
        logger.info(f"[OK] Stats: {result.get('stats')}")
    
    @pytest.mark.integration
    async def test_get_character_inventory(self, db_connection):
        """인벤토리 및 장착 아이템 조회 테스트"""
        logger.info("[통합 테스트] 인벤토리 조회 테스트 시작")
        
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
        
        # CharacterService 생성
        character_service = CharacterService(db_connection)
        
        # 인벤토리 조회
        result = await character_service.get_character_inventory(session_id)
        
        # 검증
        assert result.get('success') is True, "인벤토리 조회 실패"
        assert 'entity_id' in result, "entity_id가 없음"
        assert 'inventory' in result, "inventory가 없음"
        assert 'equipped' in result, "equipped가 없음"
        assert 'items' in result['inventory'], "inventory.items가 없음"
        
        logger.info(f"[OK] 인벤토리 조회 성공: {len(result['inventory']['items'])}개 아이템")
    
    @pytest.mark.integration
    async def test_get_character_equipped(self, db_connection):
        """장착 아이템 조회 테스트"""
        logger.info("[통합 테스트] 장착 아이템 조회 테스트 시작")
        
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
        
        # CharacterService 생성
        character_service = CharacterService(db_connection)
        
        # 장착 아이템 조회
        result = await character_service.get_character_equipped(session_id)
        
        # 검증
        assert result.get('success') is True, "장착 아이템 조회 실패"
        assert 'entity_id' in result, "entity_id가 없음"
        assert 'equipped' in result, "equipped가 없음"
        assert isinstance(result['equipped'], list), "equipped가 리스트가 아님"
        
        logger.info(f"[OK] 장착 아이템 조회 성공: {len(result['equipped'])}개 장착")
    
    @pytest.mark.integration
    async def test_get_character_applied_effects(self, db_connection):
        """적용 중인 Effect Carrier 조회 테스트"""
        logger.info("[통합 테스트] 적용 중인 Effect Carrier 조회 테스트 시작")
        
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
        
        # CharacterService 생성
        character_service = CharacterService(db_connection)
        
        # 적용 중인 Effect Carrier 조회
        result = await character_service.get_character_applied_effects(session_id)
        
        # 검증
        assert result.get('success') is True, "적용 중인 Effect Carrier 조회 실패"
        assert 'entity_id' in result, "entity_id가 없음"
        assert 'applied_effects' in result, "applied_effects가 없음"
        assert isinstance(result['applied_effects'], list), "applied_effects가 리스트가 아님"
        
        logger.info(f"[OK] 적용 중인 Effect Carrier 조회 성공: {len(result['applied_effects'])}개 효과")
    
    @pytest.mark.integration
    async def test_get_character_abilities(self, db_connection):
        """스킬/주문 목록 조회 테스트"""
        logger.info("[통합 테스트] 스킬/주문 목록 조회 테스트 시작")
        
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
        
        # CharacterService 생성
        character_service = CharacterService(db_connection)
        
        # 스킬/주문 목록 조회
        result = await character_service.get_character_abilities(session_id)
        
        # 검증
        assert result.get('success') is True, "스킬/주문 목록 조회 실패"
        assert 'entity_id' in result, "entity_id가 없음"
        assert 'abilities' in result, "abilities가 없음"
        assert 'skills' in result['abilities'], "abilities.skills가 없음"
        assert 'magic' in result['abilities'], "abilities.magic가 없음"
        assert isinstance(result['abilities']['skills'], list), "skills가 리스트가 아님"
        assert isinstance(result['abilities']['magic'], list), "magic가 리스트가 아님"
        
        logger.info(f"[OK] 스킬/주문 목록 조회 성공: {len(result['abilities']['skills'])}개 스킬, {len(result['abilities']['magic'])}개 주문")
    
    @pytest.mark.integration
    async def test_get_character_spells(self, db_connection):
        """주문 목록 조회 테스트"""
        logger.info("[통합 테스트] 주문 목록 조회 테스트 시작")
        
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
        
        # CharacterService 생성
        character_service = CharacterService(db_connection)
        
        # 주문 목록 조회
        result = await character_service.get_character_spells(session_id)
        
        # 검증
        assert result.get('success') is True, "주문 목록 조회 실패"
        assert 'entity_id' in result, "entity_id가 없음"
        assert 'spells' in result, "spells가 없음"
        assert isinstance(result['spells'], list), "spells가 리스트가 아님"
        
        logger.info(f"[OK] 주문 목록 조회 성공: {len(result['spells'])}개 주문")

