"""
아이템 조합 시스템 테스트

목적:
- 조합 시스템의 핵심 기능 검증
- 성공률 계산 로직 테스트
- Effect Carrier 수집 및 동시 작용 테스트
- 조합된 아이템 생성 및 사용 테스트
"""
import pytest
import pytest_asyncio
import asyncio
import uuid
from typing import List, Dict, Any
from common.utils.logger import logger

from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from app.managers.entity_manager import EntityManager
from app.managers.inventory_manager import InventoryManager
from app.managers.effect_carrier_manager import EffectCarrierManager
from app.handlers.object_interactions.crafting import CraftingInteractionHandler
from app.managers.object_state_manager import ObjectStateManager


@pytest.mark.asyncio
class TestItemCombination:
    """아이템 조합 시스템 테스트"""
    
    async def test_success_rate_calculation(self, db_connection, test_session):
        """성공률 계산 로직 테스트"""
        session_id = test_session['session_id']
        
        # 핸들러 생성
        game_data_repo = GameDataRepository(db_connection)
        runtime_data_repo = RuntimeDataRepository(db_connection)
        reference_layer_repo = ReferenceLayerRepository(db_connection)
        effect_carrier_manager = EffectCarrierManager(
            db_connection, game_data_repo, runtime_data_repo, reference_layer_repo
        )
        object_state_manager = ObjectStateManager(
            db_connection, game_data_repo, runtime_data_repo, reference_layer_repo
        )
        inventory_manager = InventoryManager(db_connection)
        
        handler = CraftingInteractionHandler(
            db_connection,
            object_state_manager,
            inventory_manager=inventory_manager,
            effect_carrier_manager=effect_carrier_manager
        )
        
        # 테스트 케이스 1: 2개 아이템, Effect Carrier 없음
        input_items = ["ITEM_1", "ITEM_2"]
        item_carriers = []
        success_rate = handler._calculate_combination_success_rate(input_items, item_carriers)
        assert 0.1 <= success_rate <= 0.9, f"Success rate should be between 10% and 90%, got {success_rate:.2%}"
        # 2개 아이템: 50% - 16% = 34%
        assert abs(success_rate - 0.34) < 0.01, f"Expected ~34%, got {success_rate:.2%}"
        
        # 테스트 케이스 2: 3개 아이템, Effect Carrier 없음
        input_items = ["ITEM_1", "ITEM_2", "ITEM_3"]
        success_rate = handler._calculate_combination_success_rate(input_items, item_carriers)
        # 3개 아이템: 50% - 24% = 26%
        assert abs(success_rate - 0.26) < 0.01, f"Expected ~26%, got {success_rate:.2%}"
        
        # 테스트 케이스 3: 2개 아이템, Effect Carrier 2개
        item_carriers = [
            {"item_id": "ITEM_1", "carrier": type('obj', (object,), {'effect_id': 'EC_1'})()},
            {"item_id": "ITEM_2", "carrier": type('obj', (object,), {'effect_id': 'EC_2'})()}
        ]
        success_rate = handler._calculate_combination_success_rate(input_items[:2], item_carriers)
        # 2개 아이템, 2개 Effect Carrier: 50% - 16% + 6% = 40%
        assert abs(success_rate - 0.40) < 0.01, f"Expected ~40%, got {success_rate:.2%}"
        
        logger.info("✅ Success rate calculation test passed")
    
    async def test_consumed_items_on_failure(self, db_connection, test_session):
        """실패 시 재료 소모 결정 로직 테스트"""
        session_id = test_session['session_id']
        
        # 핸들러 생성
        game_data_repo = GameDataRepository(db_connection)
        runtime_data_repo = RuntimeDataRepository(db_connection)
        reference_layer_repo = ReferenceLayerRepository(db_connection)
        effect_carrier_manager = EffectCarrierManager(
            db_connection, game_data_repo, runtime_data_repo, reference_layer_repo
        )
        object_state_manager = ObjectStateManager(
            db_connection, game_data_repo, runtime_data_repo, reference_layer_repo
        )
        inventory_manager = InventoryManager(db_connection)
        
        handler = CraftingInteractionHandler(
            db_connection,
            object_state_manager,
            inventory_manager=inventory_manager,
            effect_carrier_manager=effect_carrier_manager
        )
        
        # 테스트 케이스 1: Effect Carrier 없는 아이템 우선 소모
        input_items = ["ITEM_NO_CARRIER", "ITEM_WITH_CARRIER"]
        item_carriers = [
            {"item_id": "ITEM_WITH_CARRIER", "carrier": type('obj', (object,), {'effect_id': 'EC_1'})()}
        ]
        consumed = handler._determine_consumed_items_on_failure(input_items, item_carriers)
        assert len(consumed) == 1, "Should consume 1 item on failure"
        assert consumed[0] == "ITEM_NO_CARRIER", "Should consume item without Effect Carrier first"
        
        # 테스트 케이스 2: 모두 Effect Carrier가 있으면 랜덤 선택
        input_items = ["ITEM_1", "ITEM_2", "ITEM_3"]
        item_carriers = [
            {"item_id": "ITEM_1", "carrier": type('obj', (object,), {'effect_id': 'EC_1'})()},
            {"item_id": "ITEM_2", "carrier": type('obj', (object,), {'effect_id': 'EC_2'})()},
            {"item_id": "ITEM_3", "carrier": type('obj', (object,), {'effect_id': 'EC_3'})()}
        ]
        consumed = handler._determine_consumed_items_on_failure(input_items, item_carriers)
        assert len(consumed) >= 1, "Should consume at least 1 item"
        assert len(consumed) <= len(input_items) // 2, "Should consume at most 50% of items"
        
        logger.info("✅ Consumed items on failure test passed")
    
    async def test_collect_effect_carriers(self, db_connection, test_session):
        """Effect Carrier 수집 로직 테스트"""
        session_id = test_session['session_id']
        
        # 테스트 아이템 생성
        pool = await db_connection.pool
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
                base_prop_id, "Test Item Base", "Test", "item", "{}", "{}"
            )
            
            # Effect Carrier 생성
            effect_carrier_id = str(uuid.uuid4())
            await conn.execute(
                """
                INSERT INTO game_data.effect_carriers
                (effect_id, name, carrier_type, effect_json, constraints_json, tags)
                VALUES ($1, $2, $3, $4::jsonb, $5::jsonb, $6)
                ON CONFLICT (effect_id) DO NOTHING
                """,
                effect_carrier_id, "Test Effect", "buff", '{"hp_bonus": 10}', '{}', []
            )
            
            # 아이템 생성 (Effect Carrier 포함)
            item_id = f"ITEM_TEST_{uuid.uuid4().hex[:8]}"
            await conn.execute(
                """
                INSERT INTO game_data.items
                (item_id, base_property_id, item_type, stack_size, consumable, effect_carrier_id, item_properties)
                VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb)
                """,
                item_id, base_prop_id, "consumable", 1, True, effect_carrier_id, "{}"
            )
        
        # 핸들러 생성
        game_data_repo = GameDataRepository(db_connection)
        runtime_data_repo = RuntimeDataRepository(db_connection)
        reference_layer_repo = ReferenceLayerRepository(db_connection)
        effect_carrier_manager = EffectCarrierManager(
            db_connection, game_data_repo, runtime_data_repo, reference_layer_repo
        )
        object_state_manager = ObjectStateManager(
            db_connection, game_data_repo, runtime_data_repo, reference_layer_repo
        )
        inventory_manager = InventoryManager(db_connection)
        
        handler = CraftingInteractionHandler(
            db_connection,
            object_state_manager,
            inventory_manager=inventory_manager,
            effect_carrier_manager=effect_carrier_manager
        )
        
        # Effect Carrier 수집
        item_carriers = await handler._collect_item_effect_carriers([item_id])
        
        # Effect Carrier가 수집되었는지 확인
        assert len(item_carriers) >= 1, f"Should collect at least 1 Effect Carrier, got {len(item_carriers)}"
        # item_id가 일치하는 Effect Carrier 찾기
        matching_carrier = next((ic for ic in item_carriers if ic["item_id"] == item_id), None)
        assert matching_carrier is not None, f"Should find Effect Carrier for item {item_id}"
        assert matching_carrier["carrier"].effect_id == effect_carrier_id, f"Effect Carrier ID should match, got {matching_carrier['carrier'].effect_id}, expected {effect_carrier_id}"
        
        logger.info("✅ Collect Effect Carriers test passed")
        
        # 정리
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM game_data.items WHERE item_id = $1", item_id)
            await conn.execute("DELETE FROM game_data.effect_carriers WHERE effect_id = $1", effect_carrier_id)
            await conn.execute("DELETE FROM game_data.base_properties WHERE property_id = $1", base_prop_id)

