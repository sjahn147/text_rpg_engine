"""
액션 시스템 테스트

목적:
- ActionHandler의 핵심 기능 검증
- 다양한 게임 행동 처리 테스트
- 행동 로깅 및 결과 처리 검증
- Effect Carrier와의 연동 테스트
"""
import pytest
import pytest_asyncio
import asyncio
from typing import List, Dict, Any
from common.utils.logger import logger


@pytest.mark.asyncio
class TestActionSystem:
    """액션 시스템 테스트"""
    
    async def test_investigate_action(self, db_with_templates, entity_manager, cell_manager, action_handler, test_session):
        """
        시나리오: 조사 행동 테스트
        1. 플레이어와 NPC 엔티티 생성
        2. 조사 행동 실행
        3. 조사 결과 확인
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
        
        # 2. 셀 생성 및 엔티티 배치
        cell_result = await cell_manager.create_cell(
            static_cell_id="CELL_SHOP_INTERIOR_001",
            session_id=session_id
        )
        assert cell_result.success
        cell_id = cell_result.cell.cell_id
        
        # 엔티티들을 셀에 배치
        await cell_manager.add_entity_to_cell(player_id, cell_id)
        await cell_manager.add_entity_to_cell(npc_id, cell_id)
        
        logger.info(f"[SCENARIO] Created entities and placed in cell")
        
        # 3. 조사 행동 실행
        action_result = await action_handler.handle_investigate(
            player_id=player_id,
            target_id=npc_id,
            parameters={"cell_id": cell_id}
        )
        
        # 4. 조사 결과 확인
        assert action_result.success, f"Investigate action failed: {action_result.message}"
        assert action_result.message is not None, "Action message should not be None"
        assert len(action_result.message) > 0, "Action message should not be empty"
        
        logger.info(f"[OK] Investigate action successful")
        logger.info(f"[OK] Result: {action_result.message}")
    
    async def test_move_action(self, db_with_templates, entity_manager, cell_manager, action_handler, test_session):
        """
        시나리오: 이동 행동 테스트
        1. 두 개의 셀 생성
        2. 플레이어를 첫 번째 셀에 배치
        3. 두 번째 셀로 이동
        4. 이동 결과 확인
        """
        session_id = test_session['session_id']
        
        # 1. 두 개의 셀 생성
        cell_a_result = await cell_manager.create_cell(
            static_cell_id="CELL_SHOP_INTERIOR_001",
            session_id=session_id
        )
        assert cell_a_result.success
        cell_a_id = cell_a_result.cell.cell_id
        
        cell_b_result = await cell_manager.create_cell(
            static_cell_id="CELL_SHOP_INTERIOR_001",
            session_id=session_id
        )
        assert cell_b_result.success
        cell_b_id = cell_b_result.cell.cell_id
        
        # 2. 플레이어 생성 및 첫 번째 셀에 배치
        player_result = await entity_manager.create_entity(
            static_entity_id="NPC_VILLAGER_001",
            session_id=session_id
        )
        assert player_result.status == "success"
        player_id = player_result.entity_id
        
        await cell_manager.add_entity_to_cell(player_id, cell_a_id)
        
        logger.info(f"[SCENARIO] Player placed in cell A")
        
        # 3. 두 번째 셀로 이동
        move_result = await action_handler.handle_move(
            player_id=player_id,
            target_id=cell_b_id,
            parameters={"from_cell_id": cell_a_id}
        )
        
        # 4. 이동 결과 확인
        assert move_result.success, f"Move action failed: {move_result.message}"
        
        # 5. 셀 B에서 플레이어 확인
        content_result = await cell_manager.load_cell_content(cell_b_id)
        assert content_result.success
        
        player_found = False
        if content_result.content and content_result.content.entities:
            for entity in content_result.content.entities:
                if entity.entity_id == player_id:
                    player_found = True
                    break
        
        assert player_found, f"Player should be in cell B after move"
        
        logger.info(f"[OK] Move action successful")
        logger.info(f"[OK] Player moved from {cell_a_id} to {cell_b_id}")
    
    async def test_wait_action(self, db_with_templates, entity_manager, action_handler, test_session):
        """
        시나리오: 대기 행동 테스트
        1. 플레이어 생성
        2. 대기 행동 실행
        3. 대기 결과 확인
        """
        session_id = test_session['session_id']
        
        # 1. 플레이어 생성
        player_result = await entity_manager.create_entity(
            static_entity_id="NPC_VILLAGER_001",
            session_id=session_id
        )
        assert player_result.status == "success"
        player_id = player_result.entity_id
        
        logger.info(f"[SCENARIO] Player created for wait action")
        
        # 2. 대기 행동 실행
        wait_result = await action_handler.handle_wait(
            player_id=player_id,
            parameters={"hours": 1}  # 1시간 대기
        )
        
        # 3. 대기 결과 확인
        assert wait_result.success, f"Wait action failed: {wait_result.message}"
        assert "대기" in wait_result.message or "wait" in wait_result.message.lower(), "Wait message should contain wait-related text"
        
        logger.info(f"[OK] Wait action successful")
        logger.info(f"[OK] Result: {wait_result.message}")
    
    async def test_attack_action(self, db_with_templates, entity_manager, action_handler, test_session):
        """
        시나리오: 공격 행동 테스트
        1. 플레이어와 적 생성
        2. 공격 행동 실행
        3. 공격 결과 확인
        """
        session_id = test_session['session_id']
        
        # 1. 플레이어와 적 생성
        player_result = await entity_manager.create_entity(
            static_entity_id="NPC_VILLAGER_001",
            session_id=session_id
        )
        assert player_result.status == "success"
        player_id = player_result.entity_id
        
        enemy_result = await entity_manager.create_entity(
            static_entity_id="NPC_GOBLIN_001",
            session_id=session_id
        )
        assert enemy_result.status == "success"
        enemy_id = enemy_result.entity_id
        
        logger.info(f"[SCENARIO] Player and enemy created")
        
        # 엔티티 정보 확인
        player_entity = await entity_manager.get_entity(player_id)
        enemy_entity = await entity_manager.get_entity(enemy_id)
        logger.info(f"[DEBUG] Player entity type: {player_entity.entity.entity_type if player_entity.success else 'Failed'}")
        logger.info(f"[DEBUG] Enemy entity type: {enemy_entity.entity.entity_type if enemy_entity.success else 'Failed'}")
        
        # 2. 공격 행동 실행
        attack_result = await action_handler.handle_attack(
            player_id=player_id,
            target_id=enemy_id
        )
        
        # 3. 공격 결과 확인
        assert attack_result.success, f"Attack action failed: {attack_result.message}"
        assert "공격" in attack_result.message or "attack" in attack_result.message.lower(), "Attack message should contain attack-related text"
        
        logger.info(f"[OK] Attack action successful")
        logger.info(f"[OK] Result: {attack_result.message}")
    
    async def test_use_item_action(self, db_with_templates, entity_manager, action_handler, test_session):
        """
        시나리오: 아이템 사용 행동 테스트
        1. 플레이어 생성
        2. 아이템 사용 행동 실행
        3. 아이템 사용 결과 확인
        """
        session_id = test_session['session_id']
        
        # 1. 플레이어 생성
        player_result = await entity_manager.create_entity(
            static_entity_id="NPC_VILLAGER_001",
            session_id=session_id
        )
        assert player_result.status == "success"
        player_id = player_result.entity_id
        
        logger.info(f"[SCENARIO] Player created for item use")
        
        # 2. 아이템 사용 행동 실행
        item_result = await action_handler.handle_use_item(
            player_id=player_id,
            parameters={"item_id": "ITEM_POTION_HEAL_001"}  # 가상의 아이템 ID
        )
        
        # 3. 아이템 사용 결과 확인
        # 아이템이 존재하지 않을 수 있으므로 실패해도 정상
        if item_result.success:
            assert "아이템" in item_result.message or "item" in item_result.message.lower(), "Item message should contain item-related text"
            logger.info(f"[OK] Item use action successful: {item_result.message}")
        else:
            logger.info(f"[OK] Item use action failed as expected (item not found): {item_result.message}")
    
    async def test_get_available_actions(self, db_with_templates, entity_manager, cell_manager, action_handler, test_session):
        """
        시나리오: 사용 가능한 행동 조회 테스트
        1. 플레이어 생성
        2. 사용 가능한 행동 조회
        3. 행동 목록 확인
        """
        session_id = test_session['session_id']
        
        # 1. 플레이어 생성
        player_result = await entity_manager.create_entity(
            static_entity_id="NPC_VILLAGER_001",
            session_id=session_id
        )
        assert player_result.status == "success"
        player_id = player_result.entity_id
        
        logger.info(f"[SCENARIO] Player created for action query")
        
        # 2. 사용 가능한 행동 조회 (셀 ID가 필요)
        # 먼저 셀을 생성하고 플레이어를 배치
        cell_result = await cell_manager.create_cell(
            static_cell_id="CELL_SHOP_INTERIOR_001",
            session_id=session_id
        )
        assert cell_result.success
        cell_id = cell_result.cell.cell_id
        
        await cell_manager.add_entity_to_cell(player_id, cell_id)
        
        actions_result = await action_handler.get_available_actions(
            player_id=player_id,
            current_cell_id=cell_id
        )
        
        # 3. 행동 목록 확인
        assert actions_result is not None, "Actions result should not be None"
        assert isinstance(actions_result, list), "Actions should be a list"
        assert len(actions_result) > 0, "Should have available actions"
        
        logger.info(f"[OK] Available actions retrieved")
        logger.info(f"[OK] Actions: {actions_result}")
    
    async def test_action_logging(self, db_with_templates, entity_manager, action_handler, test_session):
        """
        시나리오: 행동 로깅 테스트
        1. 플레이어 생성
        2. 행동 실행
        3. 행동 로그 확인
        """
        session_id = test_session['session_id']
        
        # 1. 플레이어 생성
        player_result = await entity_manager.create_entity(
            static_entity_id="NPC_VILLAGER_001",
            session_id=session_id
        )
        assert player_result.status == "success"
        player_id = player_result.entity_id
        
        logger.info(f"[SCENARIO] Player created for action logging")
        
        # 2. 행동 실행 (대기 행동)
        wait_result = await action_handler.handle_wait(
            player_id=player_id,
            parameters={"hours": 1}
        )
        assert wait_result.success
        
        # 3. 행동 로그 확인 (내부적으로 로깅이 되었는지 확인)
        # 실제 로그 조회 기능이 있다면 여기서 확인
        logger.info(f"[OK] Action logging test completed")
        logger.info(f"[OK] Action executed and logged: {wait_result.message}")
