"""
테스트용 샘플 데이터 삽입 스크립트
- NPC 행동 스케줄 데이터
- 시간 이벤트 데이터
- 엔티티 및 셀 데이터
"""
import asyncio
import uuid
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.connection import DatabaseConnection

async def insert_test_data():
    """테스트용 샘플 데이터 삽입"""
    db = DatabaseConnection()
    await db.initialize()
    
    try:
        # 1. 샘플 엔티티 데이터 삽입
        await insert_sample_entities(db)
        
        # 2. 샘플 셀 데이터 삽입
        await insert_sample_cells(db)
        
        # 3. NPC 행동 스케줄 데이터 삽입
        await insert_npc_behavior_schedules(db)
        
        # 4. 시간 이벤트 데이터 삽입
        await insert_time_events(db)
        
        print("✅ 테스트 데이터 삽입 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 데이터 삽입 실패: {str(e)}")
        raise
    finally:
        await db.close()

async def insert_sample_entities(db):
    """샘플 엔티티 데이터 삽입"""
    entities = [
        {
            "entity_id": "MERCHANT_THOMAS_001",
            "entity_type": "npc",
            "entity_name": "상인 토마스",
            "entity_description": "친근한 상인",
            "base_stats": {"hp": 100, "mp": 50, "strength": 10, "intelligence": 15, "charisma": 18},
            "default_equipment": {"weapon": "WEAPON_STAFF_001", "armor": "ARMOR_ROBE_001"},
            "default_abilities": {"skills": ["SKILL_TRADE_001"], "magic": ["MAGIC_HEAL_001"]},
            "default_inventory": {"items": ["ITEM_POTION_HEAL_001"], "quantities": {"ITEM_POTION_HEAL_001": 10}},
            "entity_properties": {"personality": "friendly", "gold": 1000, "interaction_flags": ["can_trade", "can_talk"], "is_hostile": False}
        },
        {
            "entity_id": "FARMER_JOHN_001",
            "entity_type": "npc",
            "entity_name": "농부 존",
            "entity_description": "성실한 농부",
            "base_stats": {"hp": 120, "mp": 30, "strength": 15, "intelligence": 10, "charisma": 12},
            "default_equipment": {"weapon": "WEAPON_PITCHFORK_001", "armor": "ARMOR_CLOTH_001"},
            "default_abilities": {"skills": ["SKILL_FARM_001"]},
            "default_inventory": {"items": ["ITEM_BREAD_001"], "quantities": {"ITEM_BREAD_001": 5}},
            "entity_properties": {"personality": "hardworking", "gold": 500, "interaction_flags": ["can_talk"], "is_hostile": False}
        },
        {
            "entity_id": "INNKEEPER_MARIA_001",
            "entity_type": "npc",
            "entity_name": "여관주인 마리아",
            "entity_description": "따뜻한 여관주인",
            "base_stats": {"hp": 90, "mp": 40, "strength": 8, "intelligence": 14, "charisma": 20},
            "default_equipment": {"weapon": "WEAPON_NONE", "armor": "ARMOR_DRESS_001"},
            "default_abilities": {"skills": ["SKILL_SERVICE_001"]},
            "default_inventory": {"items": ["ITEM_FOOD_001"], "quantities": {"ITEM_FOOD_001": 20}},
            "entity_properties": {"personality": "caring", "gold": 800, "interaction_flags": ["can_talk", "can_rest"], "is_hostile": False}
        },
        {
            "entity_id": "GUARD_ALEX_001",
            "entity_type": "npc",
            "entity_name": "수호병 알렉스",
            "entity_description": "성실한 수호병",
            "base_stats": {"hp": 150, "mp": 20, "strength": 18, "intelligence": 12, "charisma": 14},
            "default_equipment": {"weapon": "WEAPON_SWORD_001", "armor": "ARMOR_PLATE_001"},
            "default_abilities": {"skills": ["SKILL_PATROL_001", "SKILL_COMBAT_001"]},
            "default_inventory": {"items": ["ITEM_POTION_HEAL_001"], "quantities": {"ITEM_POTION_HEAL_001": 3}},
            "entity_properties": {"personality": "dutiful", "gold": 600, "interaction_flags": ["can_talk"], "is_hostile": False}
        },
        {
            "entity_id": "TRAVELER_ELLA_001",
            "entity_type": "npc",
            "entity_name": "여행자 엘라",
            "entity_description": "호기심 많은 여행자",
            "base_stats": {"hp": 80, "mp": 60, "strength": 10, "intelligence": 16, "charisma": 16},
            "default_equipment": {"weapon": "WEAPON_DAGGER_001", "armor": "ARMOR_LEATHER_001"},
            "default_abilities": {"skills": ["SKILL_EXPLORE_001"]},
            "default_inventory": {"items": ["ITEM_MAP_001"], "quantities": {"ITEM_MAP_001": 1}},
            "entity_properties": {"personality": "curious", "gold": 300, "interaction_flags": ["can_talk"], "is_hostile": False}
        }
    ]
    
    for entity in entities:
        query = """
            INSERT INTO game_data.entities (
                entity_id, entity_type, entity_name, entity_description,
                base_stats, default_equipment, default_abilities, default_inventory, entity_properties
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ON CONFLICT (entity_id) DO UPDATE SET
                entity_name = EXCLUDED.entity_name,
                entity_description = EXCLUDED.entity_description,
                base_stats = EXCLUDED.base_stats,
                default_equipment = EXCLUDED.default_equipment,
                default_abilities = EXCLUDED.default_abilities,
                default_inventory = EXCLUDED.default_inventory,
                entity_properties = EXCLUDED.entity_properties,
                updated_at = CURRENT_TIMESTAMP
        """
        
        await db.execute_query(
            query,
            entity["entity_id"],
            entity["entity_type"],
            entity["entity_name"],
            entity["entity_description"],
            json.dumps(entity["base_stats"]),
            json.dumps(entity["default_equipment"]),
            json.dumps(entity["default_abilities"]),
            json.dumps(entity["default_inventory"]),
            json.dumps(entity["entity_properties"])
        )
    
    print("✅ 샘플 엔티티 데이터 삽입 완료")

async def insert_sample_cells(db):
    """샘플 셀 데이터 삽입"""
    # 먼저 지역과 위치 데이터 삽입
    await db.execute_query("""
        INSERT INTO game_data.world_regions (region_id, region_name, region_description, region_type, region_properties)
        VALUES ('REG_VILLAGE_001', '평화로운 마을', '작고 평화로운 마을', 'village', 
                '{"climate": "temperate", "danger_level": 1, "recommended_level": {"min": 1, "max": 5}}')
        ON CONFLICT (region_id) DO NOTHING
    """)
    
    await db.execute_query("""
        INSERT INTO game_data.world_locations (location_id, region_id, location_name, location_description, location_type, location_properties)
        VALUES ('LOC_VILLAGE_CENTER_001', 'REG_VILLAGE_001', '마을 중심가', '마을의 중심 지역', 'village_center',
                '{"background_music": "peaceful_village", "ambient_effects": ["birds", "wind"]}')
        ON CONFLICT (location_id) DO NOTHING
    """)
    
    cells = [
        {
            "cell_id": "CELL_SQUARE_CENTER_001",
            "location_id": "LOC_VILLAGE_CENTER_001",
            "cell_name": "마을 광장",
            "matrix_width": 20,
            "matrix_height": 20,
            "cell_description": "마을의 중심 광장",
            "cell_properties": {"terrain": "stone", "weather": "clear"}
        },
        {
            "cell_id": "CELL_SQUARE_FOUNTAIN_001",
            "location_id": "LOC_VILLAGE_CENTER_001",
            "cell_name": "분수대",
            "matrix_width": 10,
            "matrix_height": 10,
            "cell_description": "아름다운 분수대",
            "cell_properties": {"terrain": "stone", "water": "fountain"}
        },
        {
            "cell_id": "CELL_WEAPON_SHOP_001",
            "location_id": "LOC_VILLAGE_CENTER_001",
            "cell_name": "무기 상점",
            "matrix_width": 15,
            "matrix_height": 12,
            "cell_description": "무기와 방어구를 판매하는 상점",
            "cell_properties": {"terrain": "wooden_floor", "lighting": "bright"}
        },
        {
            "cell_id": "CELL_GENERAL_SHOP_001",
            "location_id": "LOC_VILLAGE_CENTER_001",
            "cell_name": "잡화점",
            "matrix_width": 12,
            "matrix_height": 10,
            "cell_description": "일상용품을 판매하는 잡화점",
            "cell_properties": {"terrain": "wooden_floor", "lighting": "moderate"}
        },
        {
            "cell_id": "CELL_MERCHANT_HOUSE_001",
            "location_id": "LOC_VILLAGE_CENTER_001",
            "cell_name": "상인 집",
            "matrix_width": 18,
            "matrix_height": 15,
            "cell_description": "상인 토마스의 집",
            "cell_properties": {"terrain": "wooden_floor", "lighting": "warm"}
        },
        {
            "cell_id": "CELL_FARMER_HOUSE_001",
            "location_id": "LOC_VILLAGE_CENTER_001",
            "cell_name": "농부 집",
            "matrix_width": 16,
            "matrix_height": 14,
            "cell_description": "농부 존의 집",
            "cell_properties": {"terrain": "wooden_floor", "lighting": "cozy"}
        }
    ]
    
    for cell in cells:
        query = """
            INSERT INTO game_data.world_cells (
                cell_id, location_id, cell_name, matrix_width, matrix_height,
                cell_description, cell_properties
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (cell_id) DO UPDATE SET
                cell_name = EXCLUDED.cell_name,
                cell_description = EXCLUDED.cell_description,
                cell_properties = EXCLUDED.cell_properties,
                updated_at = CURRENT_TIMESTAMP
        """
        
        await db.execute_query(
            query,
            cell["cell_id"],
            cell["location_id"],
            cell["cell_name"],
            cell["matrix_width"],
            cell["matrix_height"],
            cell["cell_description"],
            json.dumps(cell["cell_properties"])
        )
    
    print("✅ 샘플 셀 데이터 삽입 완료")

async def insert_npc_behavior_schedules(db):
    """NPC 행동 스케줄 데이터 삽입"""
    schedules = [
        # 상인 토마스 스케줄
        ("MERCHANT_THOMAS_001", "dawn", "wait", 1, {"min_energy": 20}, {"location": "CELL_MERCHANT_HOUSE_001", "duration": 2}),
        ("MERCHANT_THOMAS_001", "morning", "trade", 1, {"min_energy": 30}, {"location": "CELL_WEAPON_SHOP_001", "duration": 4}),
        ("MERCHANT_THOMAS_001", "lunch", "dialogue", 1, {"min_energy": 20}, {"location": "CELL_SQUARE_CENTER_001", "duration": 2}),
        ("MERCHANT_THOMAS_001", "afternoon", "trade", 1, {"min_energy": 30}, {"location": "CELL_WEAPON_SHOP_001", "duration": 4}),
        ("MERCHANT_THOMAS_001", "evening", "dialogue", 1, {"min_energy": 20}, {"location": "CELL_SQUARE_CENTER_001", "duration": 2}),
        ("MERCHANT_THOMAS_001", "night", "wait", 1, {}, {"location": "CELL_MERCHANT_HOUSE_001", "duration": 2}),
        ("MERCHANT_THOMAS_001", "late_night", "wait", 1, {}, {"location": "CELL_MERCHANT_HOUSE_001", "duration": 8}),
        
        # 농부 존 스케줄
        ("FARMER_JOHN_001", "dawn", "wait", 1, {"min_energy": 20}, {"location": "CELL_FARMER_HOUSE_001", "duration": 2}),
        ("FARMER_JOHN_001", "morning", "investigate", 1, {"min_energy": 40}, {"location": "CELL_FARMER_HOUSE_001", "duration": 4}),
        ("FARMER_JOHN_001", "lunch", "dialogue", 1, {"min_energy": 20}, {"location": "CELL_SQUARE_CENTER_001", "duration": 2}),
        ("FARMER_JOHN_001", "afternoon", "investigate", 1, {"min_energy": 30}, {"location": "CELL_FARMER_HOUSE_001", "duration": 4}),
        ("FARMER_JOHN_001", "evening", "dialogue", 1, {"min_energy": 20}, {"location": "CELL_SQUARE_CENTER_001", "duration": 2}),
        ("FARMER_JOHN_001", "night", "wait", 1, {}, {"location": "CELL_FARMER_HOUSE_001", "duration": 2}),
        ("FARMER_JOHN_001", "late_night", "wait", 1, {}, {"location": "CELL_FARMER_HOUSE_001", "duration": 8}),
        
        # 여관주인 마리아 스케줄
        ("INNKEEPER_MARIA_001", "dawn", "wait", 1, {"min_energy": 20}, {"location": "CELL_SQUARE_CENTER_001", "duration": 2}),
        ("INNKEEPER_MARIA_001", "morning", "dialogue", 1, {"min_energy": 30}, {"location": "CELL_SQUARE_CENTER_001", "duration": 4}),
        ("INNKEEPER_MARIA_001", "lunch", "dialogue", 1, {"min_energy": 20}, {"location": "CELL_SQUARE_CENTER_001", "duration": 2}),
        ("INNKEEPER_MARIA_001", "afternoon", "dialogue", 1, {"min_energy": 30}, {"location": "CELL_SQUARE_CENTER_001", "duration": 4}),
        ("INNKEEPER_MARIA_001", "evening", "dialogue", 1, {"min_energy": 20}, {"location": "CELL_SQUARE_CENTER_001", "duration": 2}),
        ("INNKEEPER_MARIA_001", "night", "investigate", 1, {"min_energy": 10}, {"location": "CELL_SQUARE_CENTER_001", "duration": 2}),
        ("INNKEEPER_MARIA_001", "late_night", "wait", 1, {}, {"location": "CELL_SQUARE_CENTER_001", "duration": 8}),
        
        # 수호병 알렉스 스케줄
        ("GUARD_ALEX_001", "dawn", "investigate", 1, {"min_energy": 30}, {"location": "CELL_SQUARE_CENTER_001", "duration": 2}),
        ("GUARD_ALEX_001", "morning", "investigate", 1, {"min_energy": 40}, {"location": "CELL_SQUARE_CENTER_001", "duration": 4}),
        ("GUARD_ALEX_001", "lunch", "dialogue", 1, {"min_energy": 20}, {"location": "CELL_SQUARE_CENTER_001", "duration": 2}),
        ("GUARD_ALEX_001", "afternoon", "investigate", 1, {"min_energy": 30}, {"location": "CELL_SQUARE_CENTER_001", "duration": 4}),
        ("GUARD_ALEX_001", "evening", "dialogue", 1, {"min_energy": 20}, {"location": "CELL_SQUARE_CENTER_001", "duration": 2}),
        ("GUARD_ALEX_001", "night", "investigate", 1, {"min_energy": 30}, {"location": "CELL_SQUARE_CENTER_001", "duration": 2}),
        ("GUARD_ALEX_001", "late_night", "wait", 1, {}, {"location": "CELL_SQUARE_CENTER_001", "duration": 8}),
        
        # 여행자 엘라 스케줄
        ("TRAVELER_ELLA_001", "dawn", "wait", 1, {"min_energy": 10}, {"location": "CELL_SQUARE_FOUNTAIN_001", "duration": 2}),
        ("TRAVELER_ELLA_001", "morning", "investigate", 1, {"min_energy": 30}, {"location": "CELL_SQUARE_FOUNTAIN_001", "duration": 4}),
        ("TRAVELER_ELLA_001", "lunch", "dialogue", 1, {"min_energy": 20}, {"location": "CELL_SQUARE_CENTER_001", "duration": 2}),
        ("TRAVELER_ELLA_001", "afternoon", "investigate", 1, {"min_energy": 30}, {"location": "CELL_SQUARE_CENTER_001", "duration": 4}),
        ("TRAVELER_ELLA_001", "evening", "dialogue", 1, {"min_energy": 20}, {"location": "CELL_SQUARE_CENTER_001", "duration": 2}),
        ("TRAVELER_ELLA_001", "night", "wait", 1, {}, {"location": "CELL_SQUARE_FOUNTAIN_001", "duration": 2}),
        ("TRAVELER_ELLA_001", "late_night", "wait", 1, {}, {"location": "CELL_SQUARE_FOUNTAIN_001", "duration": 8})
    ]
    
    for schedule in schedules:
        query = """
            INSERT INTO game_data.entity_behavior_schedules (
                entity_id, time_period, action_type, action_priority, conditions, action_data
            ) VALUES ($1, $2, $3, $4, $5, $6)
        """
        
        await db.execute_query(
            query,
            schedule[0],  # entity_id
            schedule[1],  # time_period
            schedule[2],  # action_type
            schedule[3],  # action_priority
            json.dumps(schedule[4]),  # conditions
            json.dumps(schedule[5])   # action_data
        )
    
    print("✅ NPC 행동 스케줄 데이터 삽입 완료")

async def insert_time_events(db):
    """시간 이벤트 데이터 삽입"""
    events = [
        ("새벽 시작", "daily", None, 6, 0, {"description": "새벽이 시작됩니다", "affected_entities": [], "world_changes": {"time_period": "dawn"}}, True),
        ("점심 시간", "daily", None, 12, 0, {"description": "점심 시간입니다", "affected_entities": [], "world_changes": {"time_period": "lunch"}}, True),
        ("저녁 시간", "daily", None, 18, 0, {"description": "저녁 시간입니다", "affected_entities": [], "world_changes": {"time_period": "evening"}}, True),
        ("밤 시간", "daily", None, 22, 0, {"description": "밤 시간입니다", "affected_entities": [], "world_changes": {"time_period": "night"}}, True)
    ]
    
    for event in events:
        query = """
            INSERT INTO game_data.time_events (
                event_name, event_type, trigger_day, trigger_hour, trigger_minute, event_data, is_active
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        """
        
        await db.execute_query(
            query,
            event[0],  # event_name
            event[1],  # event_type
            event[2],  # trigger_day
            event[3],  # trigger_hour
            event[4],  # trigger_minute
            json.dumps(event[5]),  # event_data
            event[6]   # is_active
        )
    
    print("✅ 시간 이벤트 데이터 삽입 완료")

if __name__ == "__main__":
    asyncio.run(insert_test_data())
