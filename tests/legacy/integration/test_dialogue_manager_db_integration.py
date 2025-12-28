"""
Dialogue Manager 실제 DB 통합 테스트
"""

import pytest
import pytest_asyncio
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from app.interaction.dialogue_manager import DialogueManager, DialogueResult, DialogueContext, DialogueTopic, DialogueKnowledge
from app.entity.entity_manager import EntityManager, EntityData, EntityType, EntityStatus, EntityResult
from app.effect_carrier.effect_carrier_manager import EffectCarrierManager, EffectCarrierData, EffectCarrierType, EffectCarrierResult
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from common.utils.logger import logger

class TestDialogueManagerDBIntegration:
    """Dialogue Manager 실제 DB 통합 테스트"""
    
    @pytest_asyncio.fixture
    async def db_connection(self):
        """실제 DB 연결"""
        db = DatabaseConnection()
        try:
            await db.pool
            logger.info("실제 DB 연결 성공")
            return db
        except Exception as e:
            logger.error(f"실제 DB 연결 실패: {str(e)}")
            pytest.skip("DB 연결 실패")
    
    @pytest_asyncio.fixture
    async def repositories(self, db_connection):
        """리포지토리 인스턴스들"""
        return {
            'game_data_repo': GameDataRepository(db_connection),
            'runtime_data_repo': RuntimeDataRepository(db_connection),
            'reference_layer_repo': ReferenceLayerRepository(db_connection)
        }
    
    @pytest_asyncio.fixture
    async def effect_carrier_manager(self, db_connection, repositories):
        """Effect Carrier Manager 인스턴스"""
        return EffectCarrierManager(
            db_connection,
            repositories['game_data_repo'],
            repositories['runtime_data_repo'],
            repositories['reference_layer_repo']
        )
    
    @pytest_asyncio.fixture
    async def entity_manager(self, db_connection, repositories, effect_carrier_manager):
        """Entity Manager 인스턴스"""
        return EntityManager(
            db_connection,
            repositories['game_data_repo'],
            repositories['runtime_data_repo'],
            repositories['reference_layer_repo'],
            effect_carrier_manager
        )
    
    @pytest_asyncio.fixture
    async def dialogue_manager(self, db_connection, repositories, entity_manager, effect_carrier_manager):
        """Dialogue Manager 인스턴스"""
        return DialogueManager(
            db_connection,
            repositories['game_data_repo'],
            repositories['runtime_data_repo'],
            repositories['reference_layer_repo'],
            entity_manager,
            effect_carrier_manager
        )
    
    @pytest.mark.asyncio
    async def test_dialogue_start_with_db(self, dialogue_manager, entity_manager):
        """실제 DB를 통한 대화 시작 테스트"""
        # Given - 플레이어와 NPC 생성
        player_result = await entity_manager.create_entity(
            name="Test Player",
            entity_type=EntityType.PLAYER,
            properties={"health": 100, "level": 1},
            position={"x": 5.0, "y": 5.0}
        )
        assert player_result.success
        player_id = player_result.entity.entity_id
        
        npc_result = await entity_manager.create_entity(
            name="Test NPC",
            entity_type=EntityType.NPC,
            properties={"health": 100, "level": 5, "personality": "friendly"},
            position={"x": 10.0, "y": 10.0}
        )
        assert npc_result.success
        npc_id = npc_result.entity.entity_id
        
        # When - 대화 시작
        result = await dialogue_manager.start_dialogue(player_id, npc_id, "greeting")
        
        # Then
        assert result.success, f"대화 시작 실패: {result.message}"
        assert result.npc_response is not None
        assert len(result.npc_response) > 0
        assert "Test NPC" in result.npc_response
        
        logger.info(f"대화 시작 성공: {player_id} -> {npc_id}")
    
    @pytest.mark.asyncio
    async def test_dialogue_continue_with_db(self, dialogue_manager, entity_manager):
        """실제 DB를 통한 대화 계속 테스트"""
        # Given - 플레이어와 NPC 생성
        player_result = await entity_manager.create_entity(
            name="Test Player",
            entity_type=EntityType.PLAYER,
            properties={"health": 100, "level": 1},
            position={"x": 5.0, "y": 5.0}
        )
        assert player_result.success
        player_id = player_result.entity.entity_id
        
        npc_result = await entity_manager.create_entity(
            name="Test NPC",
            entity_type=EntityType.NPC,
            properties={"health": 100, "level": 5, "personality": "friendly"},
            position={"x": 10.0, "y": 10.0}
        )
        assert npc_result.success
        npc_id = npc_result.entity.entity_id
        
        # When - 대화 계속
        result = await dialogue_manager.continue_dialogue(
            player_id, npc_id, "greeting", "안녕하세요!"
        )
        
        # Then
        assert result.success, f"대화 계속 실패: {result.message}"
        assert result.npc_response is not None
        assert len(result.npc_response) > 0
        assert "Test NPC" in result.npc_response
        
        logger.info(f"대화 계속 성공: {player_id} -> {npc_id}")
    
    @pytest.mark.asyncio
    async def test_dialogue_history_with_db(self, dialogue_manager, entity_manager):
        """실제 DB를 통한 대화 기록 테스트"""
        # Given - 플레이어와 NPC 생성
        player_result = await entity_manager.create_entity(
            name="Test Player",
            entity_type=EntityType.PLAYER,
            properties={"health": 100, "level": 1},
            position={"x": 5.0, "y": 5.0}
        )
        assert player_result.success
        player_id = player_result.entity.entity_id
        
        npc_result = await entity_manager.create_entity(
            name="Test NPC",
            entity_type=EntityType.NPC,
            properties={"health": 100, "level": 5, "personality": "friendly"},
            position={"x": 10.0, "y": 10.0}
        )
        assert npc_result.success
        npc_id = npc_result.entity.entity_id
        
        # When - 대화 시작 및 계속
        await dialogue_manager.start_dialogue(player_id, npc_id, "greeting")
        await dialogue_manager.continue_dialogue(player_id, npc_id, "greeting", "안녕하세요!")
        
        # 대화 기록 조회
        session_id = "550e8400-e29b-41d4-a716-446655440000"
        history = await dialogue_manager.get_dialogue_history(session_id, player_id, npc_id)
        
        # Then
        assert len(history) >= 1
        assert history[0]["player_id"] == player_id
        assert history[0]["npc_id"] == npc_id
        assert "안녕하세요!" in history[0]["player_message"]
        
        logger.info(f"대화 기록 조회 성공: {len(history)}개 기록")
    
    @pytest.mark.asyncio
    async def test_dialogue_topics_with_db(self, dialogue_manager, entity_manager):
        """실제 DB를 통한 대화 주제 테스트"""
        # Given - 플레이어와 NPC 생성
        player_result = await entity_manager.create_entity(
            name="Test Player",
            entity_type=EntityType.PLAYER,
            properties={"health": 100, "level": 1},
            position={"x": 5.0, "y": 5.0}
        )
        assert player_result.success
        player_id = player_result.entity.entity_id
        
        npc_result = await entity_manager.create_entity(
            name="Test NPC",
            entity_type=EntityType.NPC,
            properties={"health": 100, "level": 5, "personality": "friendly"},
            position={"x": 10.0, "y": 10.0}
        )
        assert npc_result.success
        npc_id = npc_result.entity.entity_id
        
        # When - 다양한 주제로 대화
        topics = ["greeting", "trade", "lore", "quest", "farewell"]
        results = []
        
        for topic in topics:
            result = await dialogue_manager.continue_dialogue(
                player_id, npc_id, topic, f"{topic}에 대해 이야기해주세요"
            )
            results.append(result)
        
        # Then
        for i, result in enumerate(results):
            assert result.success, f"주제 {topics[i]} 대화 실패: {result.message}"
            assert result.npc_response is not None
            assert len(result.npc_response) > 0
        
        logger.info(f"대화 주제 테스트 성공: {len(topics)}개 주제")
    
    @pytest.mark.asyncio
    async def test_dialogue_npc_info_with_db(self, dialogue_manager, entity_manager):
        """실제 DB를 통한 NPC 대화 정보 테스트"""
        # Given - NPC 생성
        npc_result = await entity_manager.create_entity(
            name="Test NPC",
            entity_type=EntityType.NPC,
            properties={"health": 100, "level": 5, "personality": "friendly", "profession": "merchant"},
            position={"x": 10.0, "y": 10.0}
        )
        assert npc_result.success
        npc_id = npc_result.entity.entity_id
        
        # When - NPC 대화 정보 조회
        info = await dialogue_manager.get_npc_dialogue_info(npc_id)
        
        # Then
        assert info is not None
        assert "npc_name" in info
        assert "personality" in info
        assert info["npc_name"] == "Test NPC"
        assert info["personality"] == "friendly"
        
        logger.info(f"NPC 대화 정보 조회 성공: {npc_id}")
    
    @pytest.mark.asyncio
    async def test_dialogue_error_handling_with_db(self, dialogue_manager):
        """실제 DB를 통한 대화 에러 처리 테스트"""
        # Given - 존재하지 않는 엔티티 ID
        non_existent_player = "non-existent-player-id"
        non_existent_npc = "non-existent-npc-id"
        
        # When - 대화 시작 시도
        result = await dialogue_manager.start_dialogue(non_existent_player, non_existent_npc, "greeting")
        
        # Then
        assert not result.success, "존재하지 않는 엔티티와 대화가 성공함"
        assert "찾을 수 없습니다" in result.message
        
        logger.info(f"대화 에러 처리 테스트 성공: {non_existent_player} -> {non_existent_npc}")
    
    @pytest.mark.asyncio
    async def test_dialogue_context_management_with_db(self, dialogue_manager, entity_manager):
        """실제 DB를 통한 대화 컨텍스트 관리 테스트"""
        # Given - 플레이어와 NPC 생성
        player_result = await entity_manager.create_entity(
            name="Test Player",
            entity_type=EntityType.PLAYER,
            properties={"health": 100, "level": 1},
            position={"x": 5.0, "y": 5.0}
        )
        assert player_result.success
        player_id = player_result.entity.entity_id
        
        npc_result = await entity_manager.create_entity(
            name="Test NPC",
            entity_type=EntityType.NPC,
            properties={"health": 100, "level": 5, "personality": "friendly"},
            position={"x": 10.0, "y": 10.0}
        )
        assert npc_result.success
        npc_id = npc_result.entity.entity_id
        
        # When - 대화 컨텍스트 생성 및 관리
        context = DialogueContext(
            context_id=f"ctx_{npc_id}_greeting",
            title="인사 대화",
            content="안녕하세요! 무엇을 도와드릴까요?",
            priority=1,
            entity_personality="friendly",
            available_topics=["greeting", "trade", "farewell"],
            constraints={"max_response_length": 200, "tone": "friendly"}
        )
        
        # 대화 시작
        result = await dialogue_manager.start_dialogue(player_id, npc_id, "greeting")
        
        # Then
        assert result.success, f"대화 컨텍스트 관리 실패: {result.message}"
        assert result.npc_response is not None
        assert "Test NPC" in result.npc_response
        
        logger.info(f"대화 컨텍스트 관리 성공: {npc_id}")
    
    @pytest.mark.asyncio
    async def test_dialogue_knowledge_integration_with_db(self, dialogue_manager, entity_manager):
        """실제 DB를 통한 대화 지식 통합 테스트"""
        # Given - 플레이어와 NPC 생성
        player_result = await entity_manager.create_entity(
            name="Test Player",
            entity_type=EntityType.PLAYER,
            properties={"health": 100, "level": 1},
            position={"x": 5.0, "y": 5.0}
        )
        assert player_result.success
        player_id = player_result.entity.entity_id
        
        npc_result = await entity_manager.create_entity(
            name="Test NPC",
            entity_type=EntityType.NPC,
            properties={"health": 100, "level": 5, "personality": "friendly", "knowledge": "lore"},
            position={"x": 10.0, "y": 10.0}
        )
        assert npc_result.success
        npc_id = npc_result.entity.entity_id
        
        # When - 지식 기반 대화
        result = await dialogue_manager.continue_dialogue(
            player_id, npc_id, "lore", "이곳의 전설에 대해 이야기해주세요"
        )
        
        # Then
        assert result.success, f"지식 기반 대화 실패: {result.message}"
        assert result.npc_response is not None
        assert len(result.npc_response) > 0
        
        logger.info(f"대화 지식 통합 성공: {npc_id}")
    
    @pytest.mark.asyncio
    async def test_dialogue_effect_carrier_integration_with_db(self, dialogue_manager, entity_manager, effect_carrier_manager):
        """실제 DB를 통한 대화-Effect Carrier 통합 테스트"""
        # Given - 플레이어와 NPC 생성
        player_result = await entity_manager.create_entity(
            name="Test Player",
            entity_type=EntityType.PLAYER,
            properties={"health": 100, "level": 1},
            position={"x": 5.0, "y": 5.0}
        )
        assert player_result.success
        player_id = player_result.entity.entity_id
        
        npc_result = await entity_manager.create_entity(
            name="Test NPC",
            entity_type=EntityType.NPC,
            properties={"health": 100, "level": 5, "personality": "friendly"},
            position={"x": 10.0, "y": 10.0}
        )
        assert npc_result.success
        npc_id = npc_result.entity.entity_id
        
        # Effect Carrier 생성
        effect_result = await effect_carrier_manager.create_effect_carrier(
            name="Blessing of Wisdom",
            carrier_type=EffectCarrierType.BLESSING,
            effect_json={"intelligence": 5, "wisdom": 3},
            constraints_json={"min_level": 1},
            tags=["blessing", "wisdom"]
        )
        assert effect_result.success
        effect_id = effect_result.data.effect_id
        
        # When - Effect Carrier 적용 후 대화
        session_id = "550e8400-e29b-41d4-a716-446655440000"
        apply_result = await entity_manager.apply_effect_carrier(player_id, effect_id, session_id)
        assert apply_result.success
        
        # 대화 시작
        result = await dialogue_manager.start_dialogue(player_id, npc_id, "greeting")
        
        # Then
        assert result.success, f"Effect Carrier 통합 대화 실패: {result.message}"
        assert result.npc_response is not None
        assert "Test NPC" in result.npc_response
        
        logger.info(f"대화-Effect Carrier 통합 성공: {player_id} -> {npc_id}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
