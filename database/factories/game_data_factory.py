from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime
import json

from ..connection import DatabaseConnection

class GameDataFactory:
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        self.db = db_connection or DatabaseConnection()

    async def create_npc_template(
        self,
        template_id: str,  # "NPC_MERCHANT_001", "NPC_MONSTER_WOLF_001" 등
        name: str,
        template_type: str,  # "merchant", "monster", "quest_giver" 등
        base_stats: Dict[str, Any],
        base_properties: Dict[str, Any],
        behavior_properties: Dict[str, Any] = None,
        additional_properties: Dict[str, Any] = None  # 추가 속성 (cell_id, occupation 등)
    ) -> str:
        """NPC 템플릿을 생성합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                # 1. 기본 속성 설정
                entity_properties = {
                    "template_type": template_type,
                    "base_properties": base_properties,
                }

                # 2. 타입별 특수 속성 추가
                if template_type == "merchant":
                    entity_properties.update({
                        "shop_inventory": additional_properties.get("shop_inventory", []) if additional_properties else [],
                        "bargain_skill": base_properties.get("bargain_skill", 5),
                        "ai_type": "merchant",
                        "behavior": behavior_properties or {
                            "daily_routine": [
                                {"time": "08:00", "action": "open_shop"},
                                {"time": "20:00", "action": "close_shop"}
                            ],
                            "interaction_type": "shop"
                        }
                    })
                elif template_type == "monster":
                    entity_properties.update({
                        "aggro_range": base_properties.get("aggro_range", 10),
                        "patrol_pattern": base_properties.get("patrol_pattern", "random"),
                        "ai_type": "aggressive",
                        "behavior": behavior_properties or {
                            "combat_style": "melee",
                            "aggro_condition": "on_sight",
                            "retreat_threshold": 0.2  # 20% HP에서 도망
                        }
                    })
                elif template_type == "quest_giver":
                    entity_properties.update({
                        "available_quests": additional_properties.get("available_quests", []) if additional_properties else [],
                        "ai_type": "stationary",
                        "behavior": behavior_properties or {
                            "daily_routine": [
                                {"time": "all", "action": "stand"}
                            ],
                            "interaction_type": "dialogue"
                        }
                    })
                elif template_type == "npc":
                    # 일반 NPC 타입
                    entity_properties.update({
                        "ai_type": "stationary",
                        "behavior": behavior_properties or {
                            "daily_routine": [
                                {"time": "all", "action": "stand"}
                            ],
                            "interaction_type": "dialogue"
                        }
                    })
                
                # 3. 추가 속성 병합 (cell_id, occupation, personality, dialogue 등) - 타입별 속성 이후에 병합
                if additional_properties:
                    # shop_inventory, available_quests 등은 이미 설정되었으므로 덮어쓰지 않음
                    for key, value in additional_properties.items():
                        if key not in ["shop_inventory", "available_quests"] or key not in entity_properties:
                            entity_properties[key] = value

                # 3. game_data.entities 테이블에 저장 (실제 스키마에 맞게 수정)
                # default_position_3d와 entity_size 추가
                default_position_3d = base_properties.get("default_position_3d")
                entity_size = base_properties.get("entity_size", "medium")
                
                await conn.execute(
                    """
                    INSERT INTO game_data.entities
                    (entity_id, entity_type, entity_name, entity_description, base_stats, 
                     default_equipment, default_abilities, default_inventory, entity_properties,
                     default_position_3d, entity_size,
                     created_at, updated_at)
                    VALUES ($1, 'npc', $2, $3, $4, $5, $6, $7, $8, $9, $10, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """,
                    template_id, 
                    name, 
                    f"{template_type} NPC template",
                    json.dumps(base_stats),
                    json.dumps({}),  # default_equipment
                    json.dumps({}),  # default_abilities
                    json.dumps({"items": [], "quantities": {}}),  # default_inventory
                    json.dumps(entity_properties),
                    json.dumps(default_position_3d) if default_position_3d else None,  # default_position_3d
                    entity_size  # entity_size
                )

                return template_id

    async def create_player_template(
        self,
        template_id: str,  # "PLAYER_TEMPLATE_001" 등
        name: str,
        base_stats: Dict[str, Any],
        base_properties: Dict[str, Any]
    ) -> str:
        """플레이어 템플릿을 생성합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                # 1. 기본 속성 설정
                entity_properties = {
                    "template_type": "player",
                    "base_properties": base_properties,
                    "ai_type": "player_controlled",
                    "behavior": {
                        "interaction_type": "player",
                        "movement_type": "free"
                    }
                }

                # 2. game_data.entities 테이블에 저장
                # default_position_3d와 entity_size 추가
                default_position_3d = base_properties.get("default_position_3d")
                entity_size = base_properties.get("entity_size", "medium")
                
                await conn.execute(
                    """
                    INSERT INTO game_data.entities
                    (entity_id, entity_type, entity_name, entity_description, base_stats, 
                     default_equipment, default_abilities, default_inventory, entity_properties,
                     default_position_3d, entity_size,
                     created_at, updated_at)
                    VALUES ($1, 'player', $2, $3, $4, $5, $6, $7, $8, $9, $10, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """,
                    template_id, 
                    name, 
                    "Player template",
                    json.dumps(base_stats),
                    json.dumps({}),  # default_equipment
                    json.dumps({}),  # default_abilities
                    json.dumps({"items": [], "quantities": {}}),  # default_inventory
                    json.dumps(entity_properties),
                    json.dumps(default_position_3d) if default_position_3d else None,  # default_position_3d
                    entity_size  # entity_size
                )

                return template_id

    async def create_item_template(
        self,
        template_id: str,  # "ITEM_WEAPON_SWORD_001", "ITEM_POTION_HEAL_001" 등
        name: str,
        item_type: str,  # "weapon", "armor", "consumable" 등
        base_properties: Dict[str, Any],
        usage_properties: Dict[str, Any] = None
    ) -> str:
        """아이템 템플릿을 생성합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                # 1. 기본 속성 설정
                item_properties = {
                    "item_type": item_type,
                    "base_properties": base_properties,
                }

                # 2. 타입별 특수 속성 추가
                if item_type == "weapon":
                    item_properties.update({
                        "damage": base_properties.get("damage", 0),
                        "attack_speed": base_properties.get("attack_speed", 1.0),
                        "range": base_properties.get("range", 1),
                        "usage": usage_properties or {
                            "equip_slot": "weapon",
                            "required_level": 1,
                            "durability": 100
                        }
                    })
                elif item_type == "armor":
                    item_properties.update({
                        "defense": base_properties.get("defense", 0),
                        "magic_defense": base_properties.get("magic_defense", 0),
                        "usage": usage_properties or {
                            "equip_slot": "body",
                            "required_level": 1,
                            "durability": 100
                        }
                    })
                elif item_type == "consumable":
                    item_properties.update({
                        "effect_type": base_properties.get("effect_type", "heal"),
                        "effect_power": base_properties.get("effect_power", 0),
                        "usage": usage_properties or {
                            "use_time": 1.0,
                            "cooldown": 0,
                            "stack_size": 99
                        }
                    })

                # 3. game_data.inventory_items 테이블에 저장 (실제 스키마에 맞게 수정)
                await conn.execute(
                    """
                    INSERT INTO game_data.inventory_items
                    (item_id, base_property_id, item_type, stack_limit, item_properties, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """,
                    template_id, 
                    f"BASE_{template_id}",  # 임시 base_property_id
                    item_type, 
                    99,  # stack_limit
                    json.dumps(item_properties)
                )

                return template_id

    async def create_effect_template(
        self,
        template_id: str,  # "EFFECT_BUFF_STRENGTH_001", "EFFECT_DOT_POISON_001" 등
        name: str,
        effect_type: str,  # "buff", "debuff", "dot", "hot" 등
        base_properties: Dict[str, Any],
        trigger_conditions: Dict[str, Any] = None
    ) -> str:
        """효과 템플릿을 생성합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                # 1. 기본 속성 설정
                effect_properties = {
                    "effect_type": effect_type,
                    "base_properties": base_properties,
                }

                # 2. 타입별 특수 속성 추가
                if effect_type in ["buff", "debuff"]:
                    effect_properties.update({
                        "stat_modifiers": base_properties.get("stat_modifiers", {}),
                        "duration": base_properties.get("duration", 0),
                        "trigger": trigger_conditions or {
                            "on_apply": ["modify_stats"],
                            "on_remove": ["revert_stats"]
                        }
                    })
                elif effect_type in ["dot", "hot"]:
                    effect_properties.update({
                        "tick_damage": base_properties.get("tick_damage", 0),
                        "tick_interval": base_properties.get("tick_interval", 1.0),
                        "duration": base_properties.get("duration", 0),
                        "trigger": trigger_conditions or {
                            "on_tick": ["apply_damage"],
                            "on_apply": ["init_tick"],
                            "on_remove": ["cleanup_tick"]
                        }
                    })

                # 3. game_data.effects 테이블에 저장 (실제 스키마에 맞게 수정)
                await conn.execute(
                    """
                    INSERT INTO game_data.effects
                    (effect_id, base_property_id, effect_type, duration, effect_properties, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """,
                    template_id, 
                    f"BASE_{template_id}",  # 임시 base_property_id
                    effect_type, 
                    base_properties.get("duration", 0),
                    json.dumps(effect_properties)
                )

                return template_id

    async def create_dialogue_context(
        self,
        entity_id: str,
        title: str,
        content: str,
        priority: int = 1,
        conditions: Dict[str, Any] = None
    ) -> str:
        """대화 컨텍스트를 생성합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                context_id = f"DIALOGUE_{entity_id}_{uuid.uuid4().hex[:8]}"
                
                await conn.execute(
                    """
                    INSERT INTO game_data.dialogue_contexts
                    (dialogue_id, title, content, entity_id, priority, constraints, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """,
                    context_id,
                    title,
                    content,
                    entity_id,
                    priority,
                    json.dumps(conditions or {})
                )

                return context_id

    async def create_world_region(
        self,
        region_id: str,
        region_name: str,
        region_type: str = "continent",
        description: str = "",
        properties: Dict[str, Any] = None
    ) -> str:
        """월드 지역을 생성합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    """
                    INSERT INTO game_data.world_regions
                    (region_id, region_name, region_type, region_description, region_properties, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """,
                    region_id,
                    region_name,
                    region_type,
                    description,
                    json.dumps(properties or {})
                )

                return region_id

    async def create_world_location(
        self,
        location_id: str,
        region_id: str,
        location_name: str,
        description: str = "",
        properties: Dict[str, Any] = None
    ) -> str:
        """월드 위치를 생성합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    """
                    INSERT INTO game_data.world_locations
                    (location_id, region_id, location_name, location_description, location_properties, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """,
                    location_id,
                    region_id,
                    location_name,
                    description,
                    json.dumps(properties or {})
                )

                return location_id

    async def create_world_cell(
        self,
        cell_id: str,
        location_id: str,
        cell_name: str,
        matrix_width: int = 100,
        matrix_height: int = 100,
        cell_description: str = "",
        cell_properties: Dict[str, Any] = None
    ) -> str:
        """월드 셀을 생성합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    """
                    INSERT INTO game_data.world_cells
                    (cell_id, location_id, cell_name, matrix_width, matrix_height, cell_description, cell_properties)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """,
                    cell_id,
                    location_id,
                    cell_name,
                    matrix_width,
                    matrix_height,
                    cell_description,
                    json.dumps(cell_properties or {})
                )

                return cell_id

    async def create_world_object(
        self,
        object_id: str,
        object_type: str,  # "static", "interactive", "trigger"
        object_name: str,
        default_cell_id: str = None,
        default_position: Dict[str, Any] = None,
        interaction_type: str = None,
        possible_states: Dict[str, Any] = None,
        properties: Dict[str, Any] = None,
        wall_mounted: bool = False,
        passable: bool = False,
        movable: bool = False,
        object_height: float = 1.0,
        object_width: float = 1.0,
        object_depth: float = 1.0,
        object_weight: float = 0.0,
        object_description: str = ""
    ) -> str:
        """월드 오브젝트를 생성합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    """
                    INSERT INTO game_data.world_objects
                    (object_id, object_type, object_name, object_description, default_cell_id,
                     default_position, interaction_type, possible_states, properties,
                     wall_mounted, passable, movable,
                     object_height, object_width, object_depth, object_weight,
                     created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16,
                            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """,
                    object_id,
                    object_type,
                    object_name,
                    object_description,
                    default_cell_id,
                    json.dumps(default_position) if default_position else None,
                    interaction_type,
                    json.dumps(possible_states) if possible_states else None,
                    json.dumps(properties) if properties else None,
                    wall_mounted,
                    passable,
                    movable,
                    object_height,
                    object_width,
                    object_depth,
                    object_weight
                )

                return object_id