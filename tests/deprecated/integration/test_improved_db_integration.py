"""
개선된 DB 통합 테스트
- 새로운 DB 연결 관리 시스템 사용
- 테스트 격리 및 안정성 확보
"""
import pytest
import asyncio
from app.entity.entity_manager import EntityManager
from app.world.cell_manager import CellManager
from app.interaction.dialogue_manager import DialogueManager
from app.interaction.action_handler import ActionHandler
from app.effect_carrier.effect_carrier_manager import EffectCarrierManager
from app.entity.entity_manager import EntityType, EntityStatus
from app.world.cell_manager import CellType, CellStatus


class TestImprovedDBIntegration:
    """개선된 DB 통합 테스트"""
    
    @pytest.mark.asyncio
    async def test_entity_creation_with_improved_db(self, db_connection, managers, clean_database):
        """개선된 DB 연결로 엔티티 생성 테스트"""
        entity_manager = managers['entity_manager']
        
        # 엔티티 생성
        result = await entity_manager.create_entity(
            name="Test Player",
            entity_type=EntityType.PLAYER,
            properties={"health": 100, "level": 1}
        )
        
        assert result.success
        assert result.entity is not None
        assert result.entity.name == "Test Player"
        assert result.entity.entity_type == EntityType.PLAYER
    
    @pytest.mark.asyncio
    async def test_cell_creation_with_improved_db(self, db_connection, managers, clean_database):
        """개선된 DB 연결로 셀 생성 테스트"""
        cell_manager = managers['cell_manager']
        
        # 셀 생성
        result = await cell_manager.create_cell(
            name="Test Room",
            cell_type=CellType.INDOOR,
            location_id="test-location-1",
            description="A test room"
        )
        
        assert result.success
        assert result.cell is not None
        assert result.cell.name == "Test Room"
        assert result.cell.cell_type == CellType.INDOOR
    
    @pytest.mark.asyncio
    async def test_dialogue_with_improved_db(self, db_connection, managers, clean_database):
        """개선된 DB 연결로 대화 테스트"""
        entity_manager = managers['entity_manager']
        dialogue_manager = managers['dialogue_manager']
        
        # 플레이어 생성
        player_result = await entity_manager.create_entity(
            name="Test Player",
            entity_type=EntityType.PLAYER
        )
        assert player_result.success
        
        # NPC 생성
        npc_result = await entity_manager.create_entity(
            name="Test NPC",
            entity_type=EntityType.NPC
        )
        assert npc_result.success
        
        # 대화 시작
        dialogue_result = await dialogue_manager.start_dialogue(
            player_id=player_result.entity.entity_id,
            npc_id=npc_result.entity.entity_id
        )
        
        assert dialogue_result.success
        assert dialogue_result.session_id is not None
    
    @pytest.mark.asyncio
    async def test_action_with_improved_db(self, db_connection, managers, clean_database):
        """개선된 DB 연결로 액션 테스트"""
        entity_manager = managers['entity_manager']
        cell_manager = managers['cell_manager']
        action_handler = managers['action_handler']
        
        # 플레이어 생성
        player_result = await entity_manager.create_entity(
            name="Test Player",
            entity_type=EntityType.PLAYER
        )
        assert player_result.success
        
        # 셀 생성
        cell_result = await cell_manager.create_cell(
            name="Test Room",
            cell_type=CellType.INDOOR,
            location_id="test-location-1"
        )
        assert cell_result.success
        
        # 조사 액션 실행
        action_result = await action_handler.execute_action(
            action_type="investigate",
            entity_id=player_result.entity.entity_id,
            target_id=cell_result.cell.cell_id
        )
        
        assert action_result.success
        assert "조사" in action_result.message
    
    @pytest.mark.asyncio
    async def test_effect_carrier_with_improved_db(self, db_connection, managers, clean_database):
        """개선된 DB 연결로 Effect Carrier 테스트"""
        effect_carrier_manager = managers['effect_carrier_manager']
        
        # Effect Carrier 생성
        result = await effect_carrier_manager.create_effect_carrier(
            name="Test Buff",
            effect_type="buff",
            effect_json={"stat": "strength", "value": 10},
            constraints_json={"duration": 300}
        )
        
        assert result.success
        assert result.data is not None
        assert result.data.name == "Test Buff"
    
    @pytest.mark.asyncio
    async def test_full_workflow_with_improved_db(self, db_connection, managers, clean_database):
        """개선된 DB 연결로 전체 워크플로우 테스트"""
        entity_manager = managers['entity_manager']
        cell_manager = managers['cell_manager']
        dialogue_manager = managers['dialogue_manager']
        action_handler = managers['action_handler']
        
        # 1. 플레이어 생성
        player_result = await entity_manager.create_entity(
            name="Adventurer",
            entity_type=EntityType.PLAYER,
            properties={"health": 100, "level": 1}
        )
        assert player_result.success
        
        # 2. NPC 생성
        npc_result = await entity_manager.create_entity(
            name="Village Elder",
            entity_type=EntityType.NPC,
            properties={"health": 80, "level": 5}
        )
        assert npc_result.success
        
        # 3. 셀 생성
        cell_result = await cell_manager.create_cell(
            name="Village Square",
            cell_type=CellType.OUTDOOR,
            location_id="village-1",
            description="A peaceful village square"
        )
        assert cell_result.success
        
        # 4. 플레이어를 셀에 배치
        enter_result = await cell_manager.enter_cell(
            cell_id=cell_result.cell.cell_id,
            player_id=player_result.entity.entity_id
        )
        assert enter_result.success
        
        # 5. 대화 시작
        dialogue_result = await dialogue_manager.start_dialogue(
            player_id=player_result.entity.entity_id,
            npc_id=npc_result.entity.entity_id
        )
        assert dialogue_result.success
        
        # 6. 액션 실행
        action_result = await action_handler.execute_action(
            action_type="investigate",
            entity_id=player_result.entity.entity_id,
            target_id=cell_result.cell.cell_id
        )
        assert action_result.success
        
        print(f"✅ 전체 워크플로우 테스트 성공!")
        print(f"   - 플레이어: {player_result.entity.name}")
        print(f"   - NPC: {npc_result.entity.name}")
        print(f"   - 셀: {cell_result.cell.name}")
        print(f"   - 대화 세션: {dialogue_result.session_id}")
        print(f"   - 액션 결과: {action_result.message}")


class TestDatabaseConnectionStability:
    """DB 연결 안정성 테스트"""
    
    @pytest.mark.asyncio
    async def test_multiple_connections(self, db_connection, managers, clean_database):
        """여러 연결 동시 사용 테스트"""
        entity_manager = managers['entity_manager']
        
        # 여러 엔티티 동시 생성
        tasks = []
        for i in range(5):
            task = entity_manager.create_entity(
                name=f"Player {i}",
                entity_type=EntityType.PLAYER
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # 모든 생성이 성공했는지 확인
        for result in results:
            assert result.success
            assert result.entity is not None
    
    @pytest.mark.asyncio
    async def test_connection_reuse(self, db_connection, managers, clean_database):
        """연결 재사용 테스트"""
        entity_manager = managers['entity_manager']
        
        # 첫 번째 엔티티 생성
        result1 = await entity_manager.create_entity(
            name="Player 1",
            entity_type=EntityType.PLAYER
        )
        assert result1.success
        
        # 두 번째 엔티티 생성 (같은 연결 사용)
        result2 = await entity_manager.create_entity(
            name="Player 2",
            entity_type=EntityType.PLAYER
        )
        assert result2.success
        
        # 두 엔티티가 다른 ID를 가지는지 확인
        assert result1.entity.entity_id != result2.entity.entity_id
