"""
Manager 통합 테스트
"""

import pytest
import pytest_asyncio
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from app.entity.entity_manager import EntityManager, EntityData, EntityType, EntityStatus, EntityResult
from app.world.cell_manager import CellManager, CellData, CellType, CellStatus, CellResult
from app.interaction.dialogue_manager import DialogueManager, DialogueResult
from app.interaction.action_handler import ActionHandler, ActionResult, ActionType
from app.effect_carrier.effect_carrier_manager import EffectCarrierManager, EffectCarrierData, EffectCarrierType, EffectCarrierResult
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from common.utils.logger import logger

class TestManagerIntegration:
    """Manager 통합 테스트"""
    
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
    async def test_entity_cell_integration(self, entity_manager, cell_manager):
        """Entity Manager와 Cell Manager 통합 테스트"""
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
            description="A test cell for integration",
            properties={"lighting": "bright", "temperature": "comfortable"},
            size={"width": 20, "height": 20}
        )
        assert cell_result.success
        cell_id = cell_result.cell.cell_id
        
        # When - 플레이어가 셀에 진입
        enter_result = await cell_manager.enter_cell(cell_id, player_id)
        
        # Then
        assert enter_result.success, f"셀 진입 실패: {enter_result.message}"
        assert enter_result.cell is not None
        assert enter_result.cell.cell_id == cell_id
        
        logger.info(f"Entity-Cell 통합 성공: {player_id} -> {cell_id}")
    
    @pytest.mark.asyncio
    async def test_entity_dialogue_integration(self, entity_manager, dialogue_manager):
        """Entity Manager와 Dialogue Manager 통합 테스트"""
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
        dialogue_result = await dialogue_manager.start_dialogue(player_id, npc_id, "greeting")
        
        # Then
        assert dialogue_result.success, f"대화 시작 실패: {dialogue_result.message}"
        assert dialogue_result.npc_response is not None
        assert "Test NPC" in dialogue_result.npc_response
        
        logger.info(f"Entity-Dialogue 통합 성공: {player_id} -> {npc_id}")
    
    @pytest.mark.asyncio
    async def test_entity_action_integration(self, entity_manager, action_handler):
        """Entity Manager와 Action Handler 통합 테스트"""
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
        action_result = await action_handler.execute_action(
            player_id=player_id,
            action_type=ActionType.WAIT,
            target_id=None,
            parameters={"duration": 1}
        )
        
        # Then
        assert action_result.success, f"행동 실행 실패: {action_result.message}"
        assert action_result.data is not None
        assert "duration" in action_result.data
        
        logger.info(f"Entity-Action 통합 성공: {player_id}")
    
    @pytest.mark.asyncio
    async def test_cell_dialogue_integration(self, cell_manager, dialogue_manager, entity_manager):
        """Cell Manager와 Dialogue Manager 통합 테스트"""
        # Given - 플레이어, NPC, 셀 생성
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
        
        cell_result = await cell_manager.create_cell(
            name="Test Cell",
            cell_type=CellType.INDOOR,
            location_id="test-location-001",
            description="A test cell for dialogue",
            properties={"lighting": "bright"},
            size={"width": 20, "height": 20}
        )
        assert cell_result.success
        cell_id = cell_result.cell.cell_id
        
        # When - 플레이어가 셀에 진입 후 대화
        enter_result = await cell_manager.enter_cell(cell_id, player_id)
        assert enter_result.success
        
        dialogue_result = await dialogue_manager.start_dialogue(player_id, npc_id, "greeting")
        
        # Then
        assert dialogue_result.success, f"셀-대화 통합 실패: {dialogue_result.message}"
        assert dialogue_result.npc_response is not None
        
        logger.info(f"Cell-Dialogue 통합 성공: {cell_id} -> {player_id} -> {npc_id}")
    
    @pytest.mark.asyncio
    async def test_cell_action_integration(self, cell_manager, action_handler, entity_manager):
        """Cell Manager와 Action Handler 통합 테스트"""
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
            description="A test cell for action",
            properties={"lighting": "bright"},
            size={"width": 20, "height": 20}
        )
        assert cell_result.success
        cell_id = cell_result.cell.cell_id
        
        # When - 플레이어가 셀에 진입 후 조사 행동
        enter_result = await cell_manager.enter_cell(cell_id, player_id)
        assert enter_result.success
        
        action_result = await action_handler.execute_action(
            player_id=player_id,
            action_type=ActionType.INVESTIGATE,
            target_id=None,
            parameters={"cell_id": cell_id}
        )
        
        # Then
        assert action_result.success, f"셀-행동 통합 실패: {action_result.message}"
        assert action_result.data is not None
        assert "cell_name" in action_result.data
        
        logger.info(f"Cell-Action 통합 성공: {cell_id} -> {player_id}")
    
    @pytest.mark.asyncio
    async def test_dialogue_action_integration(self, dialogue_manager, action_handler, entity_manager):
        """Dialogue Manager와 Action Handler 통합 테스트"""
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
        action_result = await action_handler.execute_action(
            player_id=player_id,
            action_type=ActionType.DIALOGUE,
            target_id=npc_id,
            parameters={"topic": "greeting", "message": "안녕하세요!"}
        )
        
        # Then
        assert action_result.success, f"대화-행동 통합 실패: {action_result.message}"
        assert action_result.data is not None
        assert "target_name" in action_result.data
        
        logger.info(f"Dialogue-Action 통합 성공: {player_id} -> {npc_id}")
    
    @pytest.mark.asyncio
    async def test_effect_carrier_entity_integration(self, effect_carrier_manager, entity_manager):
        """Effect Carrier Manager와 Entity Manager 통합 테스트"""
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
        
        # When - Effect Carrier 적용
        session_id = "550e8400-e29b-41d4-a716-446655440000"
        apply_result = await entity_manager.apply_effect_carrier(player_id, effect_id, session_id)
        
        # Then
        assert apply_result.success, f"Effect Carrier 적용 실패: {apply_result.message}"
        
        # Effect Carrier 조회
        effects_result = await entity_manager.get_entity_effects(player_id, session_id)
        assert effects_result.success, f"Effect Carrier 조회 실패: {effects_result.message}"
        
        logger.info(f"Effect Carrier-Entity 통합 성공: {player_id} -> {effect_id}")
    
    @pytest.mark.asyncio
    async def test_full_game_flow_integration(self, entity_manager, cell_manager, dialogue_manager, action_handler, effect_carrier_manager):
        """전체 게임 플로우 통합 테스트"""
        # Given - 플레이어, NPC, 셀 생성
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
        
        cell_result = await cell_manager.create_cell(
            name="Test Cell",
            cell_type=CellType.INDOOR,
            location_id="test-location-001",
            description="A test cell for full flow",
            properties={"lighting": "bright"},
            size={"width": 20, "height": 20}
        )
        assert cell_result.success
        cell_id = cell_result.cell.cell_id
        
        # Effect Carrier 생성 및 적용 (선택사항)
        try:
            effect_result = await effect_carrier_manager.create_effect_carrier(
                name="Wisdom Blessing",
                carrier_type=EffectCarrierType.BLESSING,
                effect_json={"wisdom": 5, "intelligence": 3},
                constraints_json={"min_level": 1},
                tags=["blessing", "wisdom"]
            )
            if effect_result.success:
                effect_id = effect_result.data.effect_id
                session_id = "550e8400-e29b-41d4-a716-446655440000"
                apply_result = await entity_manager.apply_effect_carrier(player_id, effect_id, session_id)
                # Effect Carrier 적용 실패해도 테스트 계속 진행
        except Exception as e:
            logger.warning(f"Effect Carrier 생성/적용 실패, 테스트 계속 진행: {str(e)}")
        
        # When - 전체 게임 플로우 실행
        # 1. 플레이어가 셀에 진입
        enter_result = await cell_manager.enter_cell(cell_id, player_id)
        assert enter_result.success
        
        # 2. 셀 조사
        investigate_result = await action_handler.execute_action(
            player_id=player_id,
            action_type=ActionType.INVESTIGATE,
            target_id=None,
            parameters={"cell_id": cell_id}
        )
        assert investigate_result.success
        
        # 3. NPC와 대화
        dialogue_result = await dialogue_manager.start_dialogue(player_id, npc_id, "greeting")
        assert dialogue_result.success
        
        # 4. 대화 계속
        continue_result = await dialogue_manager.continue_dialogue(
            player_id, npc_id, "greeting", "안녕하세요!"
        )
        assert continue_result.success
        
        # 5. 대기 행동
        wait_result = await action_handler.execute_action(
            player_id=player_id,
            action_type=ActionType.WAIT,
            target_id=None,
            parameters={"duration": 1}
        )
        assert wait_result.success
        
        # Then
        logger.info(f"전체 게임 플로우 통합 성공: {player_id} -> {cell_id} -> {npc_id}")
    
    @pytest.mark.asyncio
    async def test_manager_error_handling_integration(self, entity_manager, cell_manager, dialogue_manager, action_handler):
        """Manager 에러 처리 통합 테스트"""
        # Given - 존재하지 않는 엔티티 ID
        non_existent_player = "non-existent-player-id"
        non_existent_npc = "non-existent-npc-id"
        non_existent_cell = "non-existent-cell-id"
        
        # When & Then - 각 Manager의 에러 처리 테스트
        
        # Entity Manager 에러 처리
        entity_result = await entity_manager.get_entity(non_existent_player)
        assert not entity_result.success
        
        # Cell Manager 에러 처리
        cell_result = await cell_manager.get_cell(non_existent_cell)
        assert not cell_result.success
        
        # Dialogue Manager 에러 처리
        dialogue_result = await dialogue_manager.start_dialogue(non_existent_player, non_existent_npc, "greeting")
        assert not dialogue_result.success
        
        # Action Handler 에러 처리
        action_result = await action_handler.execute_action(
            player_id=non_existent_player,
            action_type=ActionType.INVESTIGATE,
            target_id=None,
            parameters={"cell_id": non_existent_cell}
        )
        assert not action_result.success
        
        logger.info(f"Manager 에러 처리 통합 성공")
    
    @pytest.mark.asyncio
    async def test_manager_performance_integration(self, entity_manager, cell_manager, dialogue_manager, action_handler):
        """Manager 성능 통합 테스트"""
        # Given - 다수의 엔티티와 셀 생성
        entities = []
        cells = []
        
        # 10개의 엔티티 생성
        for i in range(10):
            entity_result = await entity_manager.create_entity(
                name=f"Test Entity {i}",
                entity_type=EntityType.NPC,
                properties={"health": 100, "level": i + 1},
                position={"x": float(i), "y": float(i)}
            )
            assert entity_result.success
            entities.append(entity_result.entity.entity_id)
        
        # 5개의 셀 생성
        for i in range(5):
            cell_result = await cell_manager.create_cell(
                name=f"Test Cell {i}",
                cell_type=CellType.INDOOR,
                location_id=f"test-location-{i:03d}",
                description=f"A test cell {i}",
                properties={"lighting": "bright"},
                size={"width": 20, "height": 20}
            )
            assert cell_result.success
            cells.append(cell_result.cell.cell_id)
        
        # When - 성능 테스트 실행
        start_time = datetime.now()
        
        # 병렬 엔티티 조회
        entity_tasks = [entity_manager.get_entity(entity_id) for entity_id in entities]
        entity_results = await asyncio.gather(*entity_tasks)
        
        # 병렬 셀 조회
        cell_tasks = [cell_manager.get_cell(cell_id) for cell_id in cells]
        cell_results = await asyncio.gather(*cell_tasks)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Then
        assert all(result.success for result in entity_results), "일부 엔티티 조회 실패"
        assert all(result.success for result in cell_results), "일부 셀 조회 실패"
        assert execution_time < 5.0, f"성능 테스트 실패: {execution_time}초"
        
        logger.info(f"Manager 성능 통합 성공: {execution_time:.2f}초")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
