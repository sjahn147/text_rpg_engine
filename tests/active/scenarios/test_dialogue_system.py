"""
대화 시스템 테스트

목적:
- DialogueManager의 핵심 기능 검증
- 대화 시작, 진행, 종료 시나리오 테스트
- NPC와의 대화 상호작용 검증
- 대화 기록 및 상태 관리 검증
"""
import pytest
import pytest_asyncio
import asyncio
from typing import List, Dict, Any
from common.utils.logger import logger


@pytest.mark.asyncio
class TestDialogueSystem:
    """대화 시스템 테스트"""
    
    async def test_start_dialogue(self, db_with_templates, entity_manager, dialogue_manager, test_session):
        """
        시나리오: 대화 시작
        1. 플레이어와 NPC 엔티티 생성
        2. 대화 시작
        3. 대화 상태 확인
        """
        session_id = test_session['session_id']
        
        # 1. 플레이어와 NPC 엔티티 생성 (사용 가능한 템플릿 사용)
        player_result = await entity_manager.create_entity(
            static_entity_id="NPC_VILLAGER_001",  # 플레이어 역할로 사용
            session_id=session_id
        )
        assert player_result.status == "success"
        player_id = player_result.entity_id
        
        npc_result = await entity_manager.create_entity(
            static_entity_id="NPC_VILLAGER_001",
            session_id=session_id
        )
        assert npc_result.status == "success"
        npc_id = npc_result.entity_id
        
        logger.info(f"[SCENARIO] Created player: {player_id}, NPC: {npc_id}")
        
        # 2. 대화 시작
        dialogue_result = await dialogue_manager.start_dialogue(
            player_id=player_id,
            npc_id=npc_id,
            session_id=session_id
        )
        
        # 3. 대화 시작 결과 확인
        assert dialogue_result.success, f"Dialogue start failed: {dialogue_result.message}"
        assert dialogue_result.npc_response is not None, "NPC response should not be None"
        assert len(dialogue_result.npc_response) > 0, "NPC response should not be empty"
        
        logger.info(f"[OK] Dialogue started successfully")
        logger.info(f"[OK] NPC Response: {dialogue_result.npc_response}")
    
    async def test_continue_dialogue(self, db_with_templates, entity_manager, dialogue_manager, test_session):
        """
        시나리오: 대화 진행
        1. 대화 시작
        2. 대화 주제 선택
        3. 대화 진행
        4. NPC 응답 확인
        """
        session_id = test_session['session_id']
        
        # 1. 엔티티 생성
        player_result = await entity_manager.create_entity(
            static_entity_id="NPC_VILLAGER_001",
            session_id=session_id
        )
        assert player_result.status == "success"
        player_id = player_result.entity_id
        
        npc_result = await entity_manager.create_entity(
            static_entity_id="NPC_MERCHANT_001",
            session_id=session_id
        )
        assert npc_result.status == "success"
        npc_id = npc_result.entity_id
        
        # 2. 대화 시작
        start_result = await dialogue_manager.start_dialogue(
            player_id=player_id,
            npc_id=npc_id,
            session_id=session_id
        )
        assert start_result.success, f"Failed to start dialogue: {start_result.message}"
        
        # 3. 대화 주제 선택 (trade)
        continue_result = await dialogue_manager.continue_dialogue(
            player_id=player_id,
            npc_id=npc_id,
            session_id=session_id,
            topic="trade"
        )
        
        # 4. 대화 진행 결과 확인
        assert continue_result.success, f"Dialogue continue failed: {continue_result.message}"
        assert continue_result.npc_response is not None, "NPC response should not be None"
        assert len(continue_result.npc_response) > 0, "NPC response should not be empty"
        
        logger.info(f"[OK] Dialogue continued successfully")
        logger.info(f"[OK] NPC Response: {continue_result.npc_response[:100]}...")
    
    async def test_end_dialogue(self, db_with_templates, entity_manager, dialogue_manager, test_session):
        """
        시나리오: 대화 종료
        1. 대화 시작 및 진행
        2. 대화 종료
        3. 대화 기록 확인
        """
        session_id = test_session['session_id']
        
        # 1. 엔티티 생성
        player_result = await entity_manager.create_entity(
            static_entity_id="NPC_VILLAGER_001",
            session_id=session_id
        )
        assert player_result.status == "success"
        player_id = player_result.entity_id
        
        npc_result = await entity_manager.create_entity(
            static_entity_id="NPC_VILLAGER_001",
            session_id=session_id
        )
        assert npc_result.status == "success"
        npc_id = npc_result.entity_id
        
        # 2. 대화 시작 및 진행
        start_result = await dialogue_manager.start_dialogue(
            player_id=player_id,
            npc_id=npc_id,
            session_id=session_id
        )
        assert start_result.success
        
        continue_result = await dialogue_manager.continue_dialogue(
            player_id=player_id,
            npc_id=npc_id,
            session_id=session_id,
            topic="greeting"
        )
        assert continue_result.success
        
        # 3. 대화 종료
        end_result = await dialogue_manager.end_dialogue(
            player_id=player_id,
            npc_id=npc_id
        )
        
        # 4. 대화 종료 결과 확인
        assert end_result.success, f"Dialogue end failed: {end_result.message}"
        
        # 5. 대화 기록 확인
        history = await dialogue_manager.get_dialogue_history(
            session_id=session_id,
            player_id=player_id,
            npc_id=npc_id
        )
        
        assert history is not None, "Dialogue history should not be None"
        assert len(history) > 0, "Dialogue history should not be empty"
        
        logger.info(f"[OK] Dialogue ended successfully")
        logger.info(f"[OK] History entries: {len(history)}")
    
    async def test_dialogue_topics(self, db_with_templates, entity_manager, dialogue_manager, test_session):
        """
        시나리오: 대화 주제 관리
        1. NPC와 대화 시작
        2. 사용 가능한 주제 조회
        3. 각 주제별 대화 테스트
        """
        session_id = test_session['session_id']
        
        # 1. 엔티티 생성
        player_result = await entity_manager.create_entity(
            static_entity_id="NPC_VILLAGER_001",
            session_id=session_id
        )
        assert player_result.status == "success"
        player_id = player_result.entity_id
        
        npc_result = await entity_manager.create_entity(
            static_entity_id="NPC_MERCHANT_001",
            session_id=session_id
        )
        assert npc_result.status == "success"
        npc_id = npc_result.entity_id
        
        # 2. 대화 시작
        start_result = await dialogue_manager.start_dialogue(
            player_id=player_id,
            npc_id=npc_id,
            session_id=session_id
        )
        assert start_result.success
        
        # 3. 사용 가능한 주제 조회
        topics = await dialogue_manager.get_available_topics(npc_id=npc_id)
        assert topics is not None, "Topics should not be None"
        assert len(topics) > 0, "Should have available topics"
        
        logger.info(f"[OK] Available topics: {topics}")
        
        # 4. 각 주제별 대화 테스트
        for topic in topics[:3]:  # 처음 3개 주제만 테스트
            continue_result = await dialogue_manager.continue_dialogue(
                player_id=player_id,
                npc_id=npc_id,
                session_id=session_id,
                topic=topic
            )
            
            if continue_result.success:
                logger.info(f"[OK] Topic '{topic}' dialogue successful")
            else:
                logger.warning(f"[WARNING] Topic '{topic}' dialogue failed: {continue_result.message}")
    
    async def test_dialogue_context_loading(self, db_with_templates, dialogue_manager):
        """
        시나리오: 대화 컨텍스트 로딩
        1. NPC별 대화 컨텍스트 조회
        2. 대화 템플릿 로딩 확인
        3. 대화 주제 로딩 확인
        """
        # 1. 대화 템플릿 로딩
        await dialogue_manager._load_dialogue_templates()
        assert dialogue_manager.response_templates is not None, "Dialogue templates should be loaded"
        
        # 2. 대화 주제 로딩
        await dialogue_manager._load_dialogue_topics()
        assert dialogue_manager.available_topics is not None, "Dialogue topics should be loaded"
        
        # 3. 기본 우선순위 확인
        priority_result = await dialogue_manager.get_default_priority()
        assert priority_result is not None, "Default priority should be available"
        
        logger.info(f"[OK] Dialogue system initialization successful")
        logger.info(f"[OK] Templates loaded: {len(dialogue_manager.response_templates) if dialogue_manager.response_templates else 0}")
        logger.info(f"[OK] Topics loaded: {len(dialogue_manager.available_topics) if dialogue_manager.available_topics else 0}")
        logger.info(f"[OK] Default priority: {priority_result}")
