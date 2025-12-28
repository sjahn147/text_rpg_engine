"""
Action Handler 실제 DB 통합 테스트
"""

import pytest
import pytest_asyncio
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from app.interaction.action_handler import ActionHandler, ActionResult, ActionType
from app.entity.entity_manager import EntityManager, EntityData, EntityType, EntityStatus, EntityResult
from app.world.cell_manager import CellManager, CellData, CellType, CellStatus, CellResult
from app.effect_carrier.effect_carrier_manager import EffectCarrierManager, EffectCarrierData, EffectCarrierType, EffectCarrierResult
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from common.utils.logger import logger

class TestActionHandlerDBIntegration:
    """Action Handler 실제 DB 통합 테스트"""
    
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
    async def cell_manager(self, db_connection, repositories, entity_manager, effect_carrier_manager):
        """Cell Manager 인스턴스"""
        return CellManager(
            db_connection,
            repositories['game_data_repo'],
            repositories['runtime_data_repo'],
            repositories['reference_layer_repo'],
            entity_manager,
            effect_carrier_manager
        )
    
    @pytest_asyncio.fixture
    async def action_handler(self, db_connection, repositories, entity_manager, cell_manager, effect_carrier_manager):
        """Action Handler 인스턴스"""
        return ActionHandler(
            db_connection,
            repositories['game_data_repo'],
            repositories['runtime_data_repo'],
            repositories['reference_layer_repo'],
            entity_manager,
            cell_manager,
            effect_carrier_manager
        )
    
    @pytest.mark.asyncio
    async def test_investigate_action_with_db(self, action_handler, entity_manager, cell_manager):
        """실제 DB를 통한 조사 행동 테스트"""
        # Given - 플레이어와 셀 생성
        player_result = await entity_manager.create_entity(
            name="Test Player",
            entity_type=EntityType.PLAYER,
            properties={"health": 100, "level": 1},
            position={"x": 5.0, "y": 5.0}
        )
        assert player_result.success
        player_id = player_result.entity.entity_id
        
        cell_result = await cell_manager.create_cell(
            name="Test Cell",
            cell_type=CellType.INDOOR,
            location_id="test-location-001",
            description="A test cell for investigation",
            properties={"lighting": "bright", "temperature": "comfortable"},
            size={"width": 20, "height": 20}
        )
        assert cell_result.success
        cell_id = cell_result.cell.cell_id
        
        # When - 조사 행동 실행
        result = await action_handler.execute_action(
            player_id=player_id,
            action_type=ActionType.INVESTIGATE,
            target_id=None,
            parameters={"cell_id": cell_id}
        )
        
        # Then
        assert result.success, f"조사 행동 실패: {result.message}"
        assert result.data is not None
        assert "cell_name" in result.data
        assert result.data["cell_name"] == "Test Cell"
        
        logger.info(f"조사 행동 성공: {player_id} -> {cell_id}")
    
    @pytest.mark.asyncio
    async def test_dialogue_action_with_db(self, action_handler, entity_manager):
        """실제 DB를 통한 대화 행동 테스트"""
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
        
        # When - 대화 행동 실행
        result = await action_handler.execute_action(
            player_id=player_id,
            action_type=ActionType.DIALOGUE,
            target_id=npc_id,
            parameters={"topic": "greeting", "message": "안녕하세요!"}
        )
        
        # Then
        assert result.success, f"대화 행동 실패: {result.message}"
        assert result.data is not None
        assert "target_name" in result.data
        assert result.data["target_name"] == "Test NPC"
        
        logger.info(f"대화 행동 성공: {player_id} -> {npc_id}")
    
    @pytest.mark.asyncio
    async def test_trade_action_with_db(self, action_handler, entity_manager):
        """실제 DB를 통한 거래 행동 테스트"""
        # Given - 플레이어와 상인 NPC 생성
        player_result = await entity_manager.create_entity(
            name="Test Player",
            entity_type=EntityType.PLAYER,
            properties={"health": 100, "level": 1, "gold": 100},
            position={"x": 5.0, "y": 5.0}
        )
        assert player_result.success
        player_id = player_result.entity.entity_id
        
        merchant_result = await entity_manager.create_entity(
            name="Test Merchant",
            entity_type=EntityType.NPC,
            properties={"health": 100, "level": 5, "profession": "merchant", "gold": 1000},
            position={"x": 10.0, "y": 10.0}
        )
        assert merchant_result.success
        merchant_id = merchant_result.entity.entity_id
        
        # When - 거래 행동 실행
        result = await action_handler.execute_action(
            player_id=player_id,
            action_type=ActionType.TRADE,
            target_id=merchant_id,
            parameters={"item_id": "test_item", "price": 50}
        )
        
        # Then
        assert result.success, f"거래 행동 실패: {result.message}"
        assert result.data is not None
        assert "merchant_name" in result.data
        assert result.data["merchant_name"] == "Test Merchant"
        
        logger.info(f"거래 행동 성공: {player_id} -> {merchant_id}")
    
    @pytest.mark.asyncio
    async def test_wait_action_with_db(self, action_handler, entity_manager):
        """실제 DB를 통한 대기 행동 테스트"""
        # Given - 플레이어 생성
        player_result = await entity_manager.create_entity(
            name="Test Player",
            entity_type=EntityType.PLAYER,
            properties={"health": 100, "level": 1},
            position={"x": 5.0, "y": 5.0}
        )
        assert player_result.success
        player_id = player_result.entity.entity_id
        
        # When - 대기 행동 실행
        result = await action_handler.execute_action(
            player_id=player_id,
            action_type=ActionType.WAIT,
            target_id=None,
            parameters={"duration": 1}
        )
        
        # Then
        assert result.success, f"대기 행동 실패: {result.message}"
        assert result.data is not None
        assert "duration" in result.data
        assert result.data["duration"] == 1
        
        logger.info(f"대기 행동 성공: {player_id}")
    
    @pytest.mark.asyncio
    async def test_move_action_with_db(self, action_handler, entity_manager, cell_manager):
        """실제 DB를 통한 이동 행동 테스트"""
        # Given - 플레이어와 셀들 생성
        player_result = await entity_manager.create_entity(
            name="Test Player",
            entity_type=EntityType.PLAYER,
            properties={"health": 100, "level": 1},
            position={"x": 5.0, "y": 5.0}
        )
        assert player_result.success
        player_id = player_result.entity.entity_id
        
        # 현재 셀 생성
        current_cell_result = await cell_manager.create_cell(
            name="Current Cell",
            cell_type=CellType.INDOOR,
            location_id="test-location-001",
            description="Current location",
            properties={"lighting": "bright"},
            size={"width": 20, "height": 20}
        )
        assert current_cell_result.success
        current_cell_id = current_cell_result.cell.cell_id
        
        # 목표 셀 생성
        target_cell_result = await cell_manager.create_cell(
            name="Target Cell",
            cell_type=CellType.INDOOR,
            location_id="test-location-002",
            description="Target location",
            properties={"lighting": "dim"},
            size={"width": 25, "height": 25}
        )
        assert target_cell_result.success
        target_cell_id = target_cell_result.cell.cell_id
        
        # When - 이동 행동 실행
        result = await action_handler.execute_action(
            player_id=player_id,
            action_type=ActionType.MOVE,
            target_id=target_cell_id,
            parameters={"from_cell_id": current_cell_id, "to_cell_id": target_cell_id}
        )
        
        # Then
        assert result.success, f"이동 행동 실패: {result.message}"
        assert result.data is not None
        assert "from_cell_id" in result.data
        assert "to_cell_id" in result.data
        assert result.data["to_cell_id"] == target_cell_id
        
        logger.info(f"이동 행동 성공: {player_id} -> {target_cell_id}")
    
    @pytest.mark.asyncio
    async def test_attack_action_with_db(self, action_handler, entity_manager):
        """실제 DB를 통한 공격 행동 테스트"""
        # Given - 플레이어와 몬스터 생성
        player_result = await entity_manager.create_entity(
            name="Test Player",
            entity_type=EntityType.PLAYER,
            properties={"health": 100, "level": 1, "attack": 15},
            position={"x": 5.0, "y": 5.0}
        )
        assert player_result.success
        player_id = player_result.entity.entity_id
        
        monster_result = await entity_manager.create_entity(
            name="Test Monster",
            entity_type=EntityType.MONSTER,
            properties={"health": 50, "level": 3, "defense": 5},
            position={"x": 10.0, "y": 10.0}
        )
        assert monster_result.success
        monster_id = monster_result.entity.entity_id
        
        # When - 공격 행동 실행
        result = await action_handler.execute_action(
            player_id=player_id,
            action_type=ActionType.ATTACK,
            target_id=monster_id,
            parameters={"damage": 20}
        )
        
        # Then
        assert result.success, f"공격 행동 실패: {result.message}"
        assert result.data is not None
        assert "target_name" in result.data
        assert result.data["target_name"] == "Test Monster"
        assert result.data["damage"] == 20
        
        logger.info(f"공격 행동 성공: {player_id} -> {monster_id}")
    
    @pytest.mark.asyncio
    async def test_use_item_action_with_db(self, action_handler, entity_manager):
        """실제 DB를 통한 아이템 사용 행동 테스트"""
        # Given - 플레이어 생성
        player_result = await entity_manager.create_entity(
            name="Test Player",
            entity_type=EntityType.PLAYER,
            properties={"health": 100, "level": 1},
            position={"x": 5.0, "y": 5.0}
        )
        assert player_result.success
        player_id = player_result.entity.entity_id
        
        # When - 아이템 사용 행동 실행
        result = await action_handler.execute_action(
            player_id=player_id,
            action_type=ActionType.USE_ITEM,
            target_id=None,
            parameters={"item_id": "health_potion", "target_id": player_id}
        )
        
        # Then
        assert result.success, f"아이템 사용 행동 실패: {result.message}"
        assert result.data is not None
        assert "item_id" in result.data
        assert result.data["item_id"] == "health_potion"
        
        logger.info(f"아이템 사용 행동 성공: {player_id} -> health_potion")
    
    @pytest.mark.asyncio
    async def test_available_actions_with_db(self, action_handler, entity_manager, cell_manager):
        """실제 DB를 통한 사용 가능한 행동 목록 테스트"""
        # Given - 플레이어와 셀 생성
        player_result = await entity_manager.create_entity(
            name="Test Player",
            entity_type=EntityType.PLAYER,
            properties={"health": 100, "level": 1},
            position={"x": 5.0, "y": 5.0}
        )
        assert player_result.success
        player_id = player_result.entity.entity_id
        
        cell_result = await cell_manager.create_cell(
            name="Test Cell",
            cell_type=CellType.INDOOR,
            location_id="test-location-001",
            description="A test cell",
            properties={"lighting": "bright"},
            size={"width": 20, "height": 20}
        )
        assert cell_result.success
        cell_id = cell_result.cell.cell_id
        
        # When - 사용 가능한 행동 목록 조회
        actions = await action_handler.get_available_actions(player_id, cell_id)
        
        # Then
        assert len(actions) > 0
        assert any(action["type"] == ActionType.INVESTIGATE.value for action in actions)
        assert any(action["type"] == ActionType.WAIT.value for action in actions)
        
        logger.info(f"사용 가능한 행동 목록 조회 성공: {len(actions)}개 행동")
    
    @pytest.mark.asyncio
    async def test_action_error_handling_with_db(self, action_handler):
        """실제 DB를 통한 행동 에러 처리 테스트"""
        # Given - 존재하지 않는 플레이어 ID
        non_existent_player = "non-existent-player-id"
        
        # When - 행동 실행 시도
        result = await action_handler.execute_action(
            player_id=non_existent_player,
            action_type=ActionType.INVESTIGATE,
            target_id=None,
            parameters={"cell_id": "test-cell"}
        )
        
        # Then
        assert not result.success, "존재하지 않는 플레이어의 행동이 성공함"
        assert "찾을 수 없습니다" in result.message
        
        logger.info(f"행동 에러 처리 테스트 성공: {non_existent_player}")
    
    @pytest.mark.asyncio
    async def test_action_effect_carrier_integration_with_db(self, action_handler, entity_manager, effect_carrier_manager):
        """실제 DB를 통한 행동-Effect Carrier 통합 테스트"""
        # Given - 플레이어 생성
        player_result = await entity_manager.create_entity(
            name="Test Player",
            entity_type=EntityType.PLAYER,
            properties={"health": 100, "level": 1},
            position={"x": 5.0, "y": 5.0}
        )
        assert player_result.success
        player_id = player_result.entity.entity_id
        
        # Effect Carrier 생성
        effect_result = await effect_carrier_manager.create_effect_carrier(
            name="Strength Boost",
            carrier_type=EffectCarrierType.BUFF,
            effect_json={"strength": 10, "duration": 60},
            constraints_json={"min_level": 1},
            tags=["buff", "strength"]
        )
        assert effect_result.success
        effect_id = effect_result.data.effect_id
        
        # Effect Carrier 적용
        session_id = "550e8400-e29b-41d4-a716-446655440000"
        apply_result = await entity_manager.apply_effect_carrier(player_id, effect_id, session_id)
        assert apply_result.success
        
        # When - 행동 실행 (Effect Carrier가 적용된 상태)
        result = await action_handler.execute_action(
            player_id=player_id,
            action_type=ActionType.WAIT,
            target_id=None,
            parameters={"duration": 1}
        )
        
        # Then
        assert result.success, f"Effect Carrier 통합 행동 실패: {result.message}"
        assert result.data is not None
        
        logger.info(f"행동-Effect Carrier 통합 성공: {player_id}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
