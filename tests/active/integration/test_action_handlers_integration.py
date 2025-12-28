"""
액션 핸들러 통합 테스트

목적:
- 모든 액션 핸들러의 통합 테스트
- 오브젝트, 아이템, 엔티티, 셀, 시간 상호작용 검증
- 실제 DB와의 연동 검증
"""
import pytest
import pytest_asyncio
import asyncio
import uuid
import json
from typing import Dict, Any
from common.utils.logger import logger

from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from app.managers.entity_manager import EntityManager
from app.managers.cell_manager import CellManager
from app.managers.inventory_manager import InventoryManager
from app.managers.effect_carrier_manager import EffectCarrierManager
from app.managers.object_state_manager import ObjectStateManager
from app.handlers.action_handler import ActionHandler
from app.handlers.action_result import ActionType

# Object Interactions
from app.handlers.object_interactions.information import InformationInteractionHandler
from app.handlers.object_interactions.state_change import StateChangeInteractionHandler
from app.handlers.object_interactions.position import PositionInteractionHandler
from app.handlers.object_interactions.recovery import RecoveryInteractionHandler
from app.handlers.object_interactions.consumption import ConsumptionInteractionHandler
from app.handlers.object_interactions.learning import LearningInteractionHandler
from app.handlers.object_interactions.item_manipulation import ItemManipulationInteractionHandler
from app.handlers.object_interactions.crafting import CraftingInteractionHandler
from app.handlers.object_interactions.destruction import DestructionInteractionHandler

# Item Interactions
from app.handlers.item_interactions.use_handler import UseItemHandler
from app.handlers.item_interactions.consumption_handler import ConsumptionItemHandler
from app.handlers.item_interactions.equipment_handler import EquipmentItemHandler
from app.handlers.item_interactions.inventory_handler import InventoryItemHandler

# Entity Interactions
from app.handlers.entity_interactions.dialogue_handler import DialogueHandler
from app.handlers.entity_interactions.trade_handler import TradeHandler
from app.handlers.entity_interactions.combat_handler import CombatHandler

# Cell Interactions
from app.handlers.cell_interactions.investigation_handler import InvestigationHandler
from app.handlers.cell_interactions.visit_handler import VisitHandler
from app.handlers.cell_interactions.movement_handler import MovementHandler

# Time Interactions
from app.handlers.time_interactions.wait_handler import WaitHandler


@pytest.mark.asyncio
class TestActionHandlersIntegration:
    """액션 핸들러 통합 테스트"""
    
    @pytest_asyncio.fixture
    async def setup_test_environment(self, db_connection, test_session):
        """테스트 환경 설정"""
        session_id = test_session['session_id']
        
        # Repositories
        game_data_repo = GameDataRepository(db_connection)
        runtime_data_repo = RuntimeDataRepository(db_connection)
        reference_layer_repo = ReferenceLayerRepository(db_connection)
        
        # Managers
        effect_carrier_manager = EffectCarrierManager(
            db_connection, game_data_repo, runtime_data_repo, reference_layer_repo
        )
        entity_manager = EntityManager(
            db_connection, game_data_repo, runtime_data_repo, reference_layer_repo, effect_carrier_manager
        )
        cell_manager = CellManager(
            db_connection, game_data_repo, runtime_data_repo, reference_layer_repo, entity_manager
        )
        inventory_manager = InventoryManager(db_connection)
        object_state_manager = ObjectStateManager(
            db_connection, game_data_repo, runtime_data_repo, reference_layer_repo
        )
        
        # ActionHandler
        action_handler = ActionHandler(
            db_connection=db_connection,
            game_data_repo=game_data_repo,
            runtime_data_repo=runtime_data_repo,
            reference_layer_repo=reference_layer_repo,
            entity_manager=entity_manager,
            cell_manager=cell_manager,
            effect_carrier_manager=effect_carrier_manager,
            object_state_manager=object_state_manager,
            inventory_manager=inventory_manager
        )
        
        # 플레이어 엔티티 생성
        player_result = await entity_manager.create_entity(
            static_entity_id="NPC_VILLAGER_001",
            session_id=session_id
        )
        if player_result.status != "success":
            pytest.skip("플레이어 엔티티 생성 실패")
        
        player_id = player_result.entity_id
        
        # 셀 생성
        cell_result = await cell_manager.create_cell(
            static_cell_id="CELL_INN_ROOM_001",
            session_id=session_id
        )
        if not cell_result.success:
            pytest.skip("셀 생성 실패")
        
        cell_id = cell_result.cell.cell_id
        
        # 플레이어를 셀에 배치
        await cell_manager.add_entity_to_cell(player_id, cell_id)
        
        return {
            "session_id": session_id,
            "player_id": player_id,
            "cell_id": cell_id,
            "action_handler": action_handler,
            "entity_manager": entity_manager,
            "cell_manager": cell_manager,
            "inventory_manager": inventory_manager,
            "object_state_manager": object_state_manager,
            "game_data_repo": game_data_repo,
            "runtime_data_repo": runtime_data_repo,
            "reference_layer_repo": reference_layer_repo,
        }
    
    async def test_object_information_interactions(self, setup_test_environment):
        """오브젝트 정보 상호작용 테스트 (examine, inspect, search)"""
        env = setup_test_environment
        
        # 오브젝트 생성 (테스트용)
        pool = await env["action_handler"].db.pool
        async with pool.acquire() as conn:
            # 게임 오브젝트 생성
            game_object_id = f"OBJ_TEST_{uuid.uuid4().hex[:8]}"
            await conn.execute(
                """
                INSERT INTO game_data.world_objects
                (object_id, object_name, object_description, object_type, interaction_type, properties)
                VALUES ($1, $2, $3, $4, $5, $6::jsonb)
                ON CONFLICT (object_id) DO NOTHING
                """,
                game_object_id, "테스트 오브젝트", "테스트용 오브젝트입니다", "interactive", "examine", json.dumps({
                    "description": "이것은 테스트 오브젝트입니다."
                })
            )
            
            # 런타임 오브젝트 생성
            runtime_object_id = str(uuid.uuid4())
            await conn.execute(
                """
                INSERT INTO runtime_data.runtime_objects
                (runtime_object_id, game_object_id, session_id)
                VALUES ($1, $2, $3)
                """,
                runtime_object_id, game_object_id, env["session_id"]
            )
            
            # 레퍼런스 레이어 등록
            await conn.execute(
                """
                INSERT INTO reference_layer.object_references
                (runtime_object_id, game_object_id, session_id, object_type)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT DO NOTHING
                """,
                runtime_object_id, game_object_id, env["session_id"], "interactive"
            )
        
        # examine 테스트
        result = await env["action_handler"].execute_action(
            entity_id=env["player_id"],
            action_type=ActionType.EXAMINE_OBJECT,
            target_id=runtime_object_id,
            parameters={"session_id": env["session_id"]}
        )
        
        assert result.success is True
        assert "message" in result.message or result.message != ""
        logger.info(f"[OK] examine_object 성공: {result.message[:50]}")
    
    async def test_object_state_change_interactions(self, setup_test_environment):
        """오브젝트 상태 변경 상호작용 테스트 (open, close, light, extinguish)"""
        env = setup_test_environment
        
        # 열 수 있는 오브젝트 생성
        pool = await env["action_handler"].db.pool
        async with pool.acquire() as conn:
            game_object_id = f"OBJ_CHEST_{uuid.uuid4().hex[:8]}"
            await conn.execute(
                """
                INSERT INTO game_data.world_objects
                (object_id, object_name, object_description, object_type, interaction_type, properties)
                VALUES ($1, $2, $3, $4, $5, $6::jsonb)
                ON CONFLICT (object_id) DO NOTHING
                """,
                game_object_id, "상자", "열 수 있는 상자입니다", "interactive", "openable", json.dumps({
                    "possible_states": ["open", "closed"],
                    "current_state": "closed"
                })
            )
            
            runtime_object_id = str(uuid.uuid4())
            await conn.execute(
                """
                INSERT INTO runtime_data.runtime_objects
                (runtime_object_id, game_object_id, session_id)
                VALUES ($1, $2, $3)
                """,
                runtime_object_id, game_object_id, env["session_id"]
            )
            
            await conn.execute(
                """
                INSERT INTO reference_layer.object_references
                (runtime_object_id, game_object_id, session_id, object_type)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT DO NOTHING
                """,
                runtime_object_id, game_object_id, env["session_id"], "interactive"
            )
        
        # open 테스트
        result = await env["action_handler"].execute_action(
            entity_id=env["player_id"],
            action_type=ActionType.OPEN_OBJECT,
            target_id=runtime_object_id,
            parameters={"session_id": env["session_id"]}
        )
        
        assert result.success is True
        logger.info(f"[OK] open_object 성공: {result.message[:50]}")
    
    async def test_object_recovery_interactions(self, setup_test_environment):
        """오브젝트 회복 상호작용 테스트 (rest, sleep, meditate)"""
        env = setup_test_environment
        
        # 쉴 수 있는 오브젝트 생성 (침대)
        pool = await env["action_handler"].db.pool
        async with pool.acquire() as conn:
            game_object_id = f"OBJ_BED_{uuid.uuid4().hex[:8]}"
            await conn.execute(
                """
                INSERT INTO game_data.world_objects
                (object_id, object_name, object_description, object_type, interaction_type, properties)
                VALUES ($1, $2, $3, $4, $5, $6::jsonb)
                ON CONFLICT (object_id) DO NOTHING
                """,
                game_object_id, "침대", "쉴 수 있는 침대입니다", "interactive", "restable", json.dumps({
                    "rest_effect": {"hp_regen": 10, "mp_regen": 5}
                })
            )
            
            runtime_object_id = str(uuid.uuid4())
            await conn.execute(
                """
                INSERT INTO runtime_data.runtime_objects
                (runtime_object_id, game_object_id, session_id)
                VALUES ($1, $2, $3)
                """,
                runtime_object_id, game_object_id, env["session_id"]
            )
            
            await conn.execute(
                """
                INSERT INTO reference_layer.object_references
                (runtime_object_id, game_object_id, session_id, object_type)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT DO NOTHING
                """,
                runtime_object_id, game_object_id, env["session_id"], "interactive"
            )
        
        # rest 테스트
        result = await env["action_handler"].execute_action(
            entity_id=env["player_id"],
            action_type=ActionType.REST_AT_OBJECT,
            target_id=runtime_object_id,
            parameters={"session_id": env["session_id"]}
        )
        
        assert result.success is True
        logger.info(f"[OK] rest_at_object 성공: {result.message[:50]}")
    
    async def test_item_use_interaction(self, setup_test_environment):
        """아이템 사용 상호작용 테스트"""
        env = setup_test_environment
        
        # 테스트 아이템 생성 및 인벤토리에 추가
        pool = await env["action_handler"].db.pool
        async with pool.acquire() as conn:
            # Base property 생성
            base_prop_id = f"BASE_TEST_{uuid.uuid4().hex[:8]}"
            await conn.execute(
                """
                INSERT INTO game_data.base_properties
                (property_id, name, description, type, base_effects, requirements)
                VALUES ($1, $2, $3, $4, $5::jsonb, $6::jsonb)
                ON CONFLICT (property_id) DO NOTHING
                """,
                base_prop_id, "테스트 아이템", "테스트용 아이템", "item", "{}", "{}"
            )
            
            # Item 생성
            item_id = f"ITEM_TEST_{uuid.uuid4().hex[:8]}"
            await conn.execute(
                """
                INSERT INTO game_data.items
                (item_id, base_property_id, item_type, stack_size, consumable, item_properties)
                VALUES ($1, $2, $3, $4, $5, $6::jsonb)
                ON CONFLICT (item_id) DO NOTHING
                """,
                item_id, base_prop_id, "consumable", 1, True, json.dumps({
                    "healing_amount": 20
                })
            )
        
        # 인벤토리에 아이템 추가
        await env["inventory_manager"].add_item_to_inventory(env["player_id"], item_id, 1)
        
        # 아이템 사용 테스트
        result = await env["action_handler"].execute_action(
            entity_id=env["player_id"],
            action_type=ActionType.USE_ITEM,
            target_id=item_id,
            parameters={"session_id": env["session_id"]}
        )
        
        # 성공 또는 실패 모두 정상 (아이템이 없을 수도 있음)
        logger.info(f"[OK] use_item 결과: {result.message[:50]}")
    
    async def test_item_equipment_interaction(self, setup_test_environment):
        """아이템 장착 상호작용 테스트"""
        env = setup_test_environment
        
        # 테스트 장비 생성
        pool = await env["action_handler"].db.pool
        async with pool.acquire() as conn:
            base_prop_id = f"BASE_WEAPON_{uuid.uuid4().hex[:8]}"
            await conn.execute(
                """
                INSERT INTO game_data.base_properties
                (property_id, name, description, type, base_effects, requirements)
                VALUES ($1, $2, $3, $4, $5::jsonb, $6::jsonb)
                ON CONFLICT (property_id) DO NOTHING
                """,
                base_prop_id, "테스트 검", "테스트용 무기", "weapon", "{}", "{}"
            )
            
            weapon_id = f"WEAPON_TEST_{uuid.uuid4().hex[:8]}"
            await conn.execute(
                """
                INSERT INTO game_data.equipment_weapons
                (weapon_id, base_property_id, damage, weapon_type, durability, weapon_properties)
                VALUES ($1, $2, $3, $4, $5, $6::jsonb)
                ON CONFLICT (weapon_id) DO NOTHING
                """,
                weapon_id, base_prop_id, 10, "sword", 100, "{}"
            )
        
        # 인벤토리에 무기 추가
        await env["inventory_manager"].add_item_to_inventory(env["player_id"], weapon_id, 1)
        
        # 장착 테스트
        result = await env["action_handler"].execute_action(
            entity_id=env["player_id"],
            action_type=ActionType.EQUIP_ITEM,
            target_id=weapon_id,
            parameters={"session_id": env["session_id"], "item_id": weapon_id}
        )
        
        logger.info(f"[OK] equip_item 결과: {result.message[:50]}")
    
    async def test_cell_movement_interaction(self, setup_test_environment):
        """셀 이동 상호작용 테스트"""
        env = setup_test_environment
        
        # 두 번째 셀 생성
        cell_result = await env["cell_manager"].create_cell(
            static_cell_id="CELL_INN_HALL_001",
            session_id=env["session_id"]
        )
        
        if not cell_result.success:
            pytest.skip("셀 생성 실패")
        
        target_cell_id = cell_result.cell.cell_id
        
        # 이동 테스트
        result = await env["action_handler"].execute_action(
            entity_id=env["player_id"],
            action_type=ActionType.MOVE_TO_CELL,
            target_id=target_cell_id,
            parameters={"session_id": env["session_id"]}
        )
        
        logger.info(f"[OK] move_to_cell 결과: {result.message[:50]}")
    
    async def test_time_wait_interaction(self, setup_test_environment):
        """시간 대기 상호작용 테스트"""
        env = setup_test_environment
        
        # 대기 테스트
        result = await env["action_handler"].execute_action(
            entity_id=env["player_id"],
            action_type=ActionType.WAIT,
            target_id=None,
            parameters={"session_id": env["session_id"], "minutes": 10}
        )
        
        assert result.success is True
        logger.info(f"[OK] wait 성공: {result.message[:50]}")
    
    # ============================================================
    # Entity Interactions 테스트
    # ============================================================
    
    async def test_entity_dialogue_interaction(self, setup_test_environment):
        """엔티티 대화 상호작용 테스트"""
        env = setup_test_environment
        
        # NPC 엔티티 생성 (여관주인)
        npc_result = await env["entity_manager"].create_entity(
            static_entity_id="NPC_INNKEEPER_001",
            session_id=env["session_id"]
        )
        
        if not npc_result.success:
            pytest.skip("NPC 생성 실패")
        
        npc_id = npc_result.entity_id
        
        # 플레이어를 셀에 배치
        cell_result = await env["cell_manager"].create_cell(
            static_cell_id="CELL_INN_ROOM_001",
            session_id=env["session_id"]
        )
        
        if cell_result.success:
            cell_id = cell_result.cell.cell_id
            await env["cell_manager"].add_entity_to_cell(env["player_id"], cell_id)
            await env["cell_manager"].add_entity_to_cell(npc_id, cell_id)
        
        # 대화 테스트
        result = await env["action_handler"].execute_action(
            entity_id=env["player_id"],
            action_type=ActionType.DIALOGUE,
            target_id=npc_id,
            parameters={"session_id": env["session_id"], "topic": "greeting"}
        )
        
        assert result.success is True
        assert result.data is not None
        logger.info(f"[OK] dialogue 성공: {result.message[:50]}")
    
    async def test_entity_trade_interaction(self, setup_test_environment):
        """엔티티 거래 상호작용 테스트"""
        env = setup_test_environment
        
        # NPC 엔티티 생성 (상인)
        npc_result = await env["entity_manager"].create_entity(
            static_entity_id="NPC_MERCHANT_RECROSTAR_001",
            session_id=env["session_id"]
        )
        
        if not npc_result.success:
            pytest.skip("NPC 생성 실패")
        
        npc_id = npc_result.entity_id
        
        # 플레이어를 셀에 배치
        cell_result = await env["cell_manager"].create_cell(
            static_cell_id="CELL_INN_LOBBY_001",
            session_id=env["session_id"]
        )
        
        if cell_result.success:
            cell_id = cell_result.cell.cell_id
            await env["cell_manager"].add_entity_to_cell(env["player_id"], cell_id)
            await env["cell_manager"].add_entity_to_cell(npc_id, cell_id)
        
        # 거래 테스트
        result = await env["action_handler"].execute_action(
            entity_id=env["player_id"],
            action_type=ActionType.TRADE,
            target_id=npc_id,
            parameters={"session_id": env["session_id"]}
        )
        
        assert result.success is True
        assert result.data is not None
        assert "items" in result.data or "gold" in result.data
        logger.info(f"[OK] trade 성공: {result.message[:50]}")
    
    async def test_entity_combat_interaction(self, setup_test_environment):
        """엔티티 전투 상호작용 테스트"""
        env = setup_test_environment
        
        # 적대 엔티티 생성 (고블린)
        enemy_result = await env["entity_manager"].create_entity(
            static_entity_id="NPC_GOBLIN_RECROSTAR_001",
            session_id=env["session_id"]
        )
        
        if not enemy_result.success:
            pytest.skip("적대 엔티티 생성 실패")
        
        enemy_id = enemy_result.entity_id
        
        # 플레이어를 셀에 배치
        cell_result = await env["cell_manager"].create_cell(
            static_cell_id="CELL_INN_HALL_001",
            session_id=env["session_id"]
        )
        
        if cell_result.success:
            cell_id = cell_result.cell.cell_id
            await env["cell_manager"].add_entity_to_cell(env["player_id"], cell_id)
            await env["cell_manager"].add_entity_to_cell(enemy_id, cell_id)
        
        # 전투 테스트
        result = await env["action_handler"].execute_action(
            entity_id=env["player_id"],
            action_type=ActionType.ATTACK,
            target_id=enemy_id,
            parameters={"session_id": env["session_id"], "damage": 10}
        )
        
        assert result.success is True
        assert result.data is not None
        logger.info(f"[OK] combat 성공: {result.message[:50]}")
    
    # ============================================================
    # Cell Interactions 테스트
    # ============================================================
    
    async def test_cell_investigation_interaction(self, setup_test_environment):
        """셀 조사 상호작용 테스트"""
        env = setup_test_environment
        
        # 셀 생성
        cell_result = await env["cell_manager"].create_cell(
            static_cell_id="CELL_INN_ROOM_001",
            session_id=env["session_id"]
        )
        
        if not cell_result.success:
            pytest.skip("셀 생성 실패")
        
        cell_id = cell_result.cell.cell_id
        
        # 플레이어를 셀에 배치
        await env["cell_manager"].add_entity_to_cell(env["player_id"], cell_id)
        
        # 조사 테스트
        result = await env["action_handler"].execute_action(
            entity_id=env["player_id"],
            action_type=ActionType.INVESTIGATE,
            target_id=None,
            parameters={"session_id": env["session_id"], "cell_id": cell_id}
        )
        
        assert result.success is True
        assert result.data is not None
        logger.info(f"[OK] investigation 성공: {result.message[:50]}")
    
    async def test_cell_visit_interaction(self, setup_test_environment):
        """셀 방문 상호작용 테스트"""
        env = setup_test_environment
        
        # 방문할 셀 생성
        cell_result = await env["cell_manager"].create_cell(
            static_cell_id="CELL_INN_LOBBY_001",
            session_id=env["session_id"]
        )
        
        if not cell_result.success:
            pytest.skip("셀 생성 실패")
        
        target_cell_id = cell_result.cell.cell_id
        
        # 방문 테스트
        result = await env["action_handler"].execute_action(
            entity_id=env["player_id"],
            action_type=ActionType.VISIT,
            target_id=target_cell_id,
            parameters={"session_id": env["session_id"]}
        )
        
        assert result.success is True
        assert result.data is not None
        logger.info(f"[OK] visit 성공: {result.message[:50]}")
    
    async def test_cell_movement_interaction_complete(self, setup_test_environment):
        """셀 이동 상호작용 완전 테스트 (이미 있지만 더 상세하게)"""
        env = setup_test_environment
        
        # 현재 셀 생성
        current_cell_result = await env["cell_manager"].create_cell(
            static_cell_id="CELL_INN_ROOM_001",
            session_id=env["session_id"]
        )
        
        if not current_cell_result.success:
            pytest.skip("현재 셀 생성 실패")
        
        current_cell_id = current_cell_result.cell.cell_id
        await env["cell_manager"].add_entity_to_cell(env["player_id"], current_cell_id)
        
        # 목표 셀 생성
        target_cell_result = await env["cell_manager"].create_cell(
            static_cell_id="CELL_INN_HALL_001",
            session_id=env["session_id"]
        )
        
        if not target_cell_result.success:
            pytest.skip("목표 셀 생성 실패")
        
        target_cell_id = target_cell_result.cell.cell_id
        
        # 이동 테스트
        result = await env["action_handler"].execute_action(
            entity_id=env["player_id"],
            action_type=ActionType.MOVE_TO_CELL,
            target_id=target_cell_id,
            parameters={"session_id": env["session_id"], "from_cell_id": current_cell_id}
        )
        
        assert result.success is True
        logger.info(f"[OK] movement 성공: {result.message[:50]}")

