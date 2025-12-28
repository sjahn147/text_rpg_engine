"""
내 방 스토리 데이터 생성 스크립트

목적:
- "내 방" 스토리에 맞는 완전한 게임 데이터 생성
- Effect Carrier, 연결된 셀, 오브젝트, 아이템 등 모든 필요한 데이터 포함
"""
import asyncio
import json
import uuid
from database.connection import DatabaseConnection
from common.utils.logger import logger


async def setup_inn_room_story_data():
    """내 방 스토리 데이터 생성"""
    db = DatabaseConnection()
    await db.initialize()
    
    try:
        pool = await db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                logger.info("=" * 60)
                logger.info("내 방 스토리 데이터 생성 시작")
                logger.info("=" * 60)
                
                # ============================================================
                # 1. Region & Location (레크로스타 리조트)
                # ============================================================
                logger.info("\n[1/7] Region & Location 생성 중...")
                
                await conn.execute("""
                    INSERT INTO game_data.world_regions
                    (region_id, region_name, region_description, region_type, region_properties)
                    VALUES ($1, $2, $3, $4, $5::jsonb)
                    ON CONFLICT (region_id) DO UPDATE SET
                        region_name = EXCLUDED.region_name,
                        region_description = EXCLUDED.region_description,
                        region_properties = EXCLUDED.region_properties
                """,
                    'REG_RECROSTAR_001',
                    '레크로스타',
                    '아름다운 해안가 리조트 마을. 따뜻한 햇살과 바다 소리가 있는 평화로운 곳입니다.',
                    'resort',
                    json.dumps({
                        'climate': 'mild',
                        'danger_level': 1,
                        'recommended_level': {'min': 1, 'max': 5},
                        'theme': 'peaceful_coastal'
                    })
                )
                
                await conn.execute("""
                    INSERT INTO game_data.world_locations
                    (location_id, region_id, location_name, location_description, location_type, location_properties)
                    VALUES ($1, $2, $3, $4, $5, $6::jsonb)
                    ON CONFLICT (location_id) DO UPDATE SET
                        location_name = EXCLUDED.location_name,
                        location_description = EXCLUDED.location_description,
                        location_properties = EXCLUDED.location_properties
                """,
                    'LOC_RECROSTAR_INN_001',
                    'REG_RECROSTAR_001',
                    '레크로스타 여관',
                    '해안가에 위치한 아늑한 여관입니다. 2층에 있는 당신의 방에서 아름다운 바다 풍경을 감상할 수 있습니다.',
                    'inn',
                    json.dumps({
                        'background_music': 'peaceful_inn',
                        'ambient_effects': ['ocean_waves', 'seagulls', 'wind'],
                        'services': ['lodging', 'meals']
                    })
                )
                
                # ============================================================
                # 2. Cells (내 방 + 연결된 셀들)
                # ============================================================
                logger.info("\n[2/7] Cells 생성 중...")
                
                # 내 방
                cell_description_room = """여관 2층에 있는 당신의 방입니다. 

창문을 통해 레크로스타의 아름다운 해안가 풍경이 보입니다. 따뜻한 햇살이 방 안을 환하게 비추고, 바다 소리가 멀리서 들려옵니다.

방은 작지만 깔끔하게 정리되어 있습니다. 나무로 만든 침대가 한쪽 벽에 놓여 있고, 그 옆에는 작은 책상이 있습니다. 책상 위에는 여행 가방이 놓여 있고, 벽에는 작은 책장이 달려 있습니다.

문은 복도로 이어지고, 창문은 바다를 향해 열려 있습니다. 이곳에서 하루를 시작하는 것이 기대됩니다."""
                
                await conn.execute("""
                    INSERT INTO game_data.world_cells
                    (cell_id, location_id, cell_name, matrix_width, matrix_height, cell_description, cell_properties)
                    VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb)
                    ON CONFLICT (cell_id) DO UPDATE SET
                        cell_name = EXCLUDED.cell_name,
                        cell_description = EXCLUDED.cell_description,
                        cell_properties = EXCLUDED.cell_properties
                """,
                    'CELL_INN_ROOM_001',
                    'LOC_RECROSTAR_INN_001',
                    '내 방',
                    20,
                    20,
                    cell_description_room,
                    json.dumps({
                        'terrain': 'indoor',
                        'weather': 'clear',
                        'lighting': 'bright',
                        'atmosphere': 'peaceful',
                        'connected_cells': [
                            {
                                'cell_id': 'CELL_INN_HALL_001',
                                'direction': 'south',
                                'description': '복도로 나가는 문'
                            }
                        ]
                    })
                )
                
                # 복도
                cell_description_hall = """여관 2층의 복도입니다. 

양쪽으로 여러 방들이 늘어서 있고, 끝에는 계단이 보입니다. 바닥은 나무로 만들어져 있어 발소리가 살짝 울립니다. 벽에는 작은 등불들이 걸려 있어 따뜻한 빛을 냅니다.

복도 끝의 계단을 내려가면 1층 로비로 갈 수 있습니다."""
                
                await conn.execute("""
                    INSERT INTO game_data.world_cells
                    (cell_id, location_id, cell_name, matrix_width, matrix_height, cell_description, cell_properties)
                    VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb)
                    ON CONFLICT (cell_id) DO UPDATE SET
                        cell_name = EXCLUDED.cell_name,
                        cell_description = EXCLUDED.cell_description,
                        cell_properties = EXCLUDED.cell_properties
                """,
                    'CELL_INN_HALL_001',
                    'LOC_RECROSTAR_INN_001',
                    '여관 복도',
                    15,
                    10,
                    cell_description_hall,
                    json.dumps({
                        'terrain': 'indoor',
                        'lighting': 'dim',
                        'connected_cells': [
                            {
                                'cell_id': 'CELL_INN_ROOM_001',
                                'direction': 'north',
                                'description': '당신의 방'
                            },
                            {
                                'cell_id': 'CELL_INN_LOBBY_001',
                                'direction': 'down',
                                'description': '1층 로비로 내려가는 계단'
                            }
                        ]
                    })
                )
                
                # 로비
                cell_description_lobby = """여관 1층의 로비입니다.

넓은 공간에 편안한 의자들이 놓여 있고, 벽난로가 따뜻한 불을 피우고 있습니다. 카운터 뒤에는 여관주인이 서 있습니다. 

앞문을 통해 밖으로 나갈 수 있습니다."""
                
                await conn.execute("""
                    INSERT INTO game_data.world_cells
                    (cell_id, location_id, cell_name, matrix_width, matrix_height, cell_description, cell_properties)
                    VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb)
                    ON CONFLICT (cell_id) DO UPDATE SET
                        cell_name = EXCLUDED.cell_name,
                        cell_description = EXCLUDED.cell_description,
                        cell_properties = EXCLUDED.cell_properties
                """,
                    'CELL_INN_LOBBY_001',
                    'LOC_RECROSTAR_INN_001',
                    '여관 로비',
                    20,
                    15,
                    cell_description_lobby,
                    json.dumps({
                        'terrain': 'indoor',
                        'lighting': 'warm',
                        'connected_cells': [
                            {
                                'cell_id': 'CELL_INN_HALL_001',
                                'direction': 'up',
                                'description': '2층 복도로 올라가는 계단'
                            }
                        ]
                    })
                )
                
                # ============================================================
                # 3. Effect Carriers (효과 부여 아이템용)
                # ============================================================
                logger.info("\n[3/7] Effect Carriers 생성 중...")
                
                effect_carriers = [
                    {
                        'effect_id': str(uuid.uuid4()),
                        'name': '치유의 빛',
                        'carrier_type': 'item',
                        'effect_json': json.dumps({
                            'type': 'heal',
                            'amount': 20,
                            'duration': 0
                        }),
                        'constraints_json': json.dumps({
                            'target': 'self',
                            'cooldown': 60
                        }),
                        'tags': ['healing', 'light'],
                        'description': '따뜻한 빛이 몸을 감싸며 상처를 치유합니다.'
                    },
                    {
                        'effect_id': str(uuid.uuid4()),
                        'name': '정신력 회복',
                        'carrier_type': 'item',
                        'effect_json': json.dumps({
                            'type': 'restore_mp',
                            'amount': 15,
                            'duration': 0
                        }),
                        'constraints_json': json.dumps({
                            'target': 'self'
                        }),
                        'tags': ['mana', 'restoration'],
                        'description': '정신력을 빠르게 회복시킵니다.'
                    },
                    {
                        'effect_id': str(uuid.uuid4()),
                        'name': '활력 증가',
                        'carrier_type': 'item',
                        'effect_json': json.dumps({
                            'type': 'buff',
                            'stat': 'strength',
                            'amount': 5,
                            'duration': 300
                        }),
                        'constraints_json': json.dumps({
                            'target': 'self'
                        }),
                        'tags': ['buff', 'strength'],
                        'description': '일시적으로 힘을 증가시킵니다.'
                    }
                ]
                
                for ec in effect_carriers:
                    await conn.execute("""
                        INSERT INTO game_data.effect_carriers
                        (effect_id, name, carrier_type, effect_json, constraints_json, tags, created_at, updated_at)
                        VALUES ($1, $2, $3, $4::jsonb, $5::jsonb, $6, NOW(), NOW())
                        ON CONFLICT (effect_id) DO UPDATE SET
                            name = EXCLUDED.name,
                            effect_json = EXCLUDED.effect_json,
                            constraints_json = EXCLUDED.constraints_json,
                            tags = EXCLUDED.tags,
                            updated_at = NOW()
                    """,
                        ec['effect_id'],
                        ec['name'],
                        ec['carrier_type'],
                        ec['effect_json'],
                        ec['constraints_json'],
                        ec['tags']
                    )
                
                logger.info(f"  ✓ {len(effect_carriers)}개의 Effect Carrier 생성 완료")
                
                # ============================================================
                # 4. Base Properties & Items
                # ============================================================
                logger.info("\n[4/7] Items 생성 중...")
                
                # Base Properties
                base_props = [
                    ('BASE_HEAL_POTION', '치유 물약', '상처를 치료하는 물약입니다.', 'item'),
                    ('BASE_MANA_POTION', '마나 물약', '정신력을 회복하는 물약입니다.', 'item'),
                    ('BASE_ENERGY_BAR', '에너지 바', '빠르게 체력을 회복하는 간식입니다.', 'item'),
                    ('BASE_TRAVEL_BAG', '여행 가방', '여행에 필요한 물건들을 담는 가방입니다.', 'item'),
                    ('BASE_TRAVELER_SWORD', '여행자의 검', '간단하지만 튼튼한 검입니다.', 'item'),
                    ('BASE_TRAVELER_CLOAK', '여행자의 망토', '바람과 비를 막아주는 실용적인 망토입니다.', 'item'),
                    ('BASE_TRAVELER_MAP', '여행 지도', '레크로스타 지역의 간단한 지도입니다.', 'item'),
                ]
                
                for prop_id, name, desc, prop_type in base_props:
                    await conn.execute("""
                        INSERT INTO game_data.base_properties
                        (property_id, name, description, type, base_effects, requirements)
                        VALUES ($1, $2, $3, $4, $5::jsonb, $6::jsonb)
                        ON CONFLICT (property_id) DO UPDATE SET
                            name = EXCLUDED.name,
                            description = EXCLUDED.description
                    """,
                        prop_id, name, desc, prop_type, '{}', '{}'
                    )
                
                # Items (Effect Carrier 포함)
                items = [
                    {
                        'item_id': 'ITEM_TRAVELER_SWORD_001',
                        'base_property_id': 'BASE_TRAVELER_SWORD',
                        'item_type': 'weapon',
                        'stack_size': 1,
                        'consumable': False,
                        'effect_carrier_id': None,
                        'item_properties': json.dumps({
                            'attack': 8,
                            'durability': 100,
                            'weight': 2.5,
                            'material': 'iron',
                            'quality': 'common'
                        })
                    },
                    {
                        'item_id': 'ITEM_TRAVELER_CLOAK_001',
                        'base_property_id': 'BASE_TRAVELER_CLOAK',
                        'item_type': 'armor',
                        'stack_size': 1,
                        'consumable': False,
                        'effect_carrier_id': None,
                        'item_properties': json.dumps({
                            'defense': 3,
                            'magic_defense': 2,
                            'durability': 80,
                            'weight': 1.0,
                            'material': 'cloth',
                            'quality': 'common'
                        })
                    },
                    {
                        'item_id': 'ITEM_TRAVELER_MAP_001',
                        'base_property_id': 'BASE_TRAVELER_MAP',
                        'item_type': 'tool',
                        'stack_size': 1,
                        'consumable': False,
                        'effect_carrier_id': None,
                        'item_properties': json.dumps({
                            'region': '레크로스타',
                            'quality': 'common'
                        })
                    },
                    {
                        'item_id': 'ITEM_HEAL_POTION_001',
                        'base_property_id': 'BASE_HEAL_POTION',
                        'item_type': 'consumable',
                        'stack_size': 10,
                        'consumable': True,
                        'effect_carrier_id': effect_carriers[0]['effect_id'],
                        'item_properties': json.dumps({
                            'healing_amount': 20,
                            'color': 'red'
                        })
                    },
                    {
                        'item_id': 'ITEM_MANA_POTION_001',
                        'base_property_id': 'BASE_MANA_POTION',
                        'item_type': 'consumable',
                        'stack_size': 10,
                        'consumable': True,
                        'effect_carrier_id': effect_carriers[1]['effect_id'],
                        'item_properties': json.dumps({
                            'mana_amount': 15,
                            'color': 'blue'
                        })
                    },
                    {
                        'item_id': 'ITEM_ENERGY_BAR_001',
                        'base_property_id': 'BASE_ENERGY_BAR',
                        'item_type': 'consumable',
                        'stack_size': 5,
                        'consumable': True,
                        'effect_carrier_id': None,
                        'item_properties': json.dumps({
                            'healing_amount': 10,
                            'satiety': 5
                        })
                    }
                ]
                
                for item in items:
                    await conn.execute("""
                        INSERT INTO game_data.items
                        (item_id, base_property_id, item_type, stack_size, consumable, effect_carrier_id, item_properties)
                        VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb)
                        ON CONFLICT (item_id) DO UPDATE SET
                            item_properties = EXCLUDED.item_properties,
                            effect_carrier_id = EXCLUDED.effect_carrier_id
                    """,
                        item['item_id'],
                        item['base_property_id'],
                        item['item_type'],
                        item['stack_size'],
                        item['consumable'],
                        item['effect_carrier_id'],
                        item['item_properties']
                    )
                
                logger.info(f"  ✓ {len(items)}개의 Item 생성 완료")
                
                # ============================================================
                # 5. World Objects (방 안의 오브젝트들)
                # ============================================================
                logger.info("\n[5/7] World Objects 생성 중...")
                
                objects = [
                    {
                        'object_id': 'OBJ_INN_BED_001',
                        'object_name': '침대',
                        'object_description': '편안해 보이는 나무 침대입니다. 깔끔하게 정리된 이불이 보입니다.',
                        'object_type': 'interactive',
                        'default_cell_id': 'CELL_INN_ROOM_001',
                        'default_position': json.dumps({'x': 5.0, 'y': 0.0, 'z': 8.0}),
                        'interaction_type': 'rest',
                        'possible_states': json.dumps(['made', 'unmade', 'slept_in']),
                        'properties': json.dumps({
                            'rest_quality': 'high',
                            'hp_regen': 10,
                            'mp_regen': 5,
                            'contents': []
                        }),
                        'movable': False,
                        'passable': False
                    },
                    {
                        'object_id': 'OBJ_INN_WINDOW_001',
                        'object_name': '창문',
                        'object_description': '바다를 향해 열린 큰 창문입니다. 따뜻한 햇살과 바다 소리가 들어옵니다.',
                        'object_type': 'interactive',
                        'default_cell_id': 'CELL_INN_ROOM_001',
                        'default_position': json.dumps({'x': 10.0, 'y': 1.0, 'z': 0.0}),
                        'interaction_type': 'examine',
                        'possible_states': json.dumps(['open', 'closed']),
                        'properties': json.dumps({
                            'view': 'ocean',
                            'light_level': 'bright'
                        }),
                        'movable': False,
                        'passable': False,
                        'wall_mounted': True
                    },
                    {
                        'object_id': 'OBJ_INN_DESK_001',
                        'object_name': '책상',
                        'object_description': '작은 나무 책상입니다. 위에는 여행 가방이 놓여 있습니다.',
                        'object_type': 'interactive',
                        'default_cell_id': 'CELL_INN_ROOM_001',
                        'default_position': json.dumps({'x': 8.0, 'y': 0.0, 'z': 5.0}),
                        'interaction_type': 'examine',
                        'possible_states': json.dumps(['normal']),
                        'properties': json.dumps({
                            'contents': ['OBJ_INN_BAG_001']
                        }),
                        'movable': True,
                        'passable': False
                    },
                    {
                        'object_id': 'OBJ_INN_BAG_001',
                        'object_name': '여행 가방',
                        'object_description': '당신의 여행 가방입니다. 안에는 몇 가지 물건들이 들어있습니다.',
                        'object_type': 'interactive',
                        'default_cell_id': 'CELL_INN_ROOM_001',
                        'default_position': json.dumps({'x': 8.5, 'y': 0.5, 'z': 5.5}),
                        'interaction_type': 'openable',
                        'possible_states': json.dumps(['closed', 'open']),
                        'properties': json.dumps({
                            'contents': ['ITEM_HEAL_POTION_001', 'ITEM_MANA_POTION_001', 'ITEM_ENERGY_BAR_001'],
                            'current_state': 'closed'
                        }),
                        'movable': True,
                        'passable': False
                    },
                    {
                        'object_id': 'OBJ_INN_BOOKSHELF_001',
                        'object_name': '책장',
                        'object_description': '벽에 달린 작은 책장입니다. 몇 권의 책이 꽂혀 있습니다.',
                        'object_type': 'interactive',
                        'default_cell_id': 'CELL_INN_ROOM_001',
                        'default_position': json.dumps({'x': 0.0, 'y': 1.5, 'z': 5.0}),
                        'interaction_type': 'examine',
                        'possible_states': json.dumps(['normal']),
                        'properties': json.dumps({
                            'contents': []
                        }),
                        'movable': False,
                        'passable': False,
                        'wall_mounted': True
                    },
                    {
                        'object_id': 'OBJ_INN_DOOR_001',
                        'object_name': '문',
                        'object_description': '복도로 나가는 문입니다.',
                        'object_type': 'interactive',
                        'default_cell_id': 'CELL_INN_ROOM_001',
                        'default_position': json.dumps({'x': 10.0, 'y': 0.0, 'z': 10.0}),
                        'interaction_type': 'openable',
                        'possible_states': json.dumps(['closed', 'open']),
                        'properties': json.dumps({
                            'leads_to': 'CELL_INN_HALL_001',
                            'current_state': 'closed'
                        }),
                        'movable': False,
                        'passable': True
                    },
                    {
                        'object_id': 'OBJ_INN_CHAIR_001',
                        'object_name': '의자',
                        'object_description': '책상 앞에 놓인 편안한 의자입니다.',
                        'object_type': 'interactive',
                        'default_cell_id': 'CELL_INN_ROOM_001',
                        'default_position': json.dumps({'x': 8.0, 'y': 0.0, 'z': 7.0}),
                        'interaction_type': 'sit',
                        'possible_states': json.dumps(['normal']),
                        'properties': json.dumps({}),
                        'movable': True,
                        'passable': False
                    },
                    {
                        'object_id': 'OBJ_INN_CANDLE_001',
                        'object_name': '촛불',
                        'object_description': '책상 위에 놓인 작은 촛불입니다. 따뜻한 불꽃이 흔들리고 있습니다.',
                        'object_type': 'interactive',
                        'default_cell_id': 'CELL_INN_ROOM_001',
                        'default_position': json.dumps({'x': 8.5, 'y': 0.8, 'z': 5.5}),
                        'interaction_type': 'lightable',
                        'possible_states': json.dumps(['lit', 'unlit']),
                        'properties': json.dumps({
                            'light_level': 'dim',
                            'current_state': 'lit'
                        }),
                        'movable': True,
                        'passable': False
                    },
                    # ============================================================
                    # 복도 (CELL_INN_HALL_001) 오브젝트
                    # ============================================================
                    {
                        'object_id': 'OBJ_INN_HALL_DOOR_ROOM_001',
                        'object_name': '방 문',
                        'object_description': '당신의 방으로 들어가는 문입니다.',
                        'object_type': 'interactive',
                        'default_cell_id': 'CELL_INN_HALL_001',
                        'default_position': json.dumps({'x': 7.5, 'y': 0.0, 'z': 0.0}),
                        'interaction_type': 'openable',
                        'possible_states': json.dumps(['closed', 'open']),
                        'properties': json.dumps({
                            'connected_cell': 'CELL_INN_ROOM_001',
                            'leads_to': 'CELL_INN_ROOM_001',
                            'current_state': 'closed'
                        }),
                        'movable': False,
                        'passable': True
                    },
                    {
                        'object_id': 'OBJ_INN_HALL_STAIRS_001',
                        'object_name': '계단',
                        'object_description': '1층 로비로 내려가는 나무 계단입니다. 발소리가 울립니다.',
                        'object_type': 'interactive',
                        'default_cell_id': 'CELL_INN_HALL_001',
                        'default_position': json.dumps({'x': 14.0, 'y': 0.0, 'z': 5.0}),
                        'interaction_type': 'openable',
                        'possible_states': json.dumps(['open']),
                        'properties': json.dumps({
                            'connected_cell': 'CELL_INN_LOBBY_001',
                            'leads_to': 'CELL_INN_LOBBY_001',
                            'current_state': 'open'
                        }),
                        'movable': False,
                        'passable': True
                    },
                    {
                        'object_id': 'OBJ_INN_HALL_WALL_LAMP_001',
                        'object_name': '벽 등불',
                        'object_description': '벽에 걸린 작은 등불입니다. 따뜻한 빛을 내고 있습니다.',
                        'object_type': 'interactive',
                        'default_cell_id': 'CELL_INN_HALL_001',
                        'default_position': json.dumps({'x': 2.0, 'y': 1.8, 'z': 2.0}),
                        'interaction_type': 'lightable',
                        'possible_states': json.dumps(['lit', 'unlit']),
                        'properties': json.dumps({
                            'light_level': 'dim',
                            'current_state': 'lit'
                        }),
                        'movable': False,
                        'passable': False,
                        'wall_mounted': True
                    },
                    {
                        'object_id': 'OBJ_INN_HALL_WALL_LAMP_002',
                        'object_name': '벽 등불',
                        'object_description': '벽에 걸린 작은 등불입니다. 따뜻한 빛을 내고 있습니다.',
                        'object_type': 'interactive',
                        'default_cell_id': 'CELL_INN_HALL_001',
                        'default_position': json.dumps({'x': 8.0, 'y': 1.8, 'z': 2.0}),
                        'interaction_type': 'lightable',
                        'possible_states': json.dumps(['lit', 'unlit']),
                        'properties': json.dumps({
                            'light_level': 'dim',
                            'current_state': 'lit'
                        }),
                        'movable': False,
                        'passable': False,
                        'wall_mounted': True
                    },
                    {
                        'object_id': 'OBJ_INN_HALL_WALL_LAMP_003',
                        'object_name': '벽 등불',
                        'object_description': '벽에 걸린 작은 등불입니다. 따뜻한 빛을 내고 있습니다.',
                        'object_type': 'interactive',
                        'default_cell_id': 'CELL_INN_HALL_001',
                        'default_position': json.dumps({'x': 12.0, 'y': 1.8, 'z': 2.0}),
                        'interaction_type': 'lightable',
                        'possible_states': json.dumps(['lit', 'unlit']),
                        'properties': json.dumps({
                            'light_level': 'dim',
                            'current_state': 'lit'
                        }),
                        'movable': False,
                        'passable': False,
                        'wall_mounted': True
                    },
                    {
                        'object_id': 'OBJ_INN_HALL_WALL_DECOR_001',
                        'object_name': '벽 장식',
                        'object_description': '벽에 걸린 작은 그림입니다. 바다 풍경을 그리고 있습니다.',
                        'object_type': 'static',
                        'default_cell_id': 'CELL_INN_HALL_001',
                        'default_position': json.dumps({'x': 5.0, 'y': 1.5, 'z': 1.0}),
                        'interaction_type': 'examine',
                        'possible_states': json.dumps(['normal']),
                        'properties': json.dumps({}),
                        'movable': False,
                        'passable': False,
                        'wall_mounted': True
                    },
                    # ============================================================
                    # 로비 (CELL_INN_LOBBY_001) 오브젝트
                    # ============================================================
                    {
                        'object_id': 'OBJ_INN_LOBBY_STAIRS_001',
                        'object_name': '계단',
                        'object_description': '2층 복도로 올라가는 나무 계단입니다.',
                        'object_type': 'interactive',
                        'default_cell_id': 'CELL_INN_LOBBY_001',
                        'default_position': json.dumps({'x': 18.0, 'y': 0.0, 'z': 7.0}),
                        'interaction_type': 'openable',
                        'possible_states': json.dumps(['open']),
                        'properties': json.dumps({
                            'connected_cell': 'CELL_INN_HALL_001',
                            'leads_to': 'CELL_INN_HALL_001',
                            'current_state': 'open'
                        }),
                        'movable': False,
                        'passable': True
                    },
                    {
                        'object_id': 'OBJ_INN_LOBBY_FIREPLACE_001',
                        'object_name': '벽난로',
                        'object_description': '따뜻한 불을 피우고 있는 벽난로입니다. 불꽃이 부드럽게 타오르고 있습니다.',
                        'object_type': 'interactive',
                        'default_cell_id': 'CELL_INN_LOBBY_001',
                        'default_position': json.dumps({'x': 0.0, 'y': 0.0, 'z': 7.0}),
                        'interaction_type': 'lightable',
                        'possible_states': json.dumps(['lit', 'unlit']),
                        'properties': json.dumps({
                            'light_level': 'warm',
                            'heat_level': 'moderate',
                            'current_state': 'lit'
                        }),
                        'movable': False,
                        'passable': False,
                        'wall_mounted': True
                    },
                    {
                        'object_id': 'OBJ_INN_LOBBY_COUNTER_001',
                        'object_name': '카운터',
                        'object_description': '여관주인이 서 있는 나무 카운터입니다. 위에는 등록부와 열쇠들이 놓여 있습니다.',
                        'object_type': 'interactive',
                        'default_cell_id': 'CELL_INN_LOBBY_001',
                        'default_position': json.dumps({'x': 10.0, 'y': 0.0, 'z': 0.0}),
                        'interaction_type': 'examine',
                        'possible_states': json.dumps(['normal']),
                        'properties': json.dumps({
                            'contents': []
                        }),
                        'movable': False,
                        'passable': False
                    },
                    {
                        'object_id': 'OBJ_INN_LOBBY_CHAIR_001',
                        'object_name': '편안한 의자',
                        'object_description': '로비에 놓인 편안한 의자입니다. 푹신한 쿠션이 달려 있습니다.',
                        'object_type': 'interactive',
                        'default_cell_id': 'CELL_INN_LOBBY_001',
                        'default_position': json.dumps({'x': 5.0, 'y': 0.0, 'z': 5.0}),
                        'interaction_type': 'sit',
                        'possible_states': json.dumps(['normal']),
                        'properties': json.dumps({
                            'comfort_level': 'high'
                        }),
                        'movable': True,
                        'passable': False
                    },
                    {
                        'object_id': 'OBJ_INN_LOBBY_CHAIR_002',
                        'object_name': '편안한 의자',
                        'object_description': '로비에 놓인 편안한 의자입니다. 푹신한 쿠션이 달려 있습니다.',
                        'object_type': 'interactive',
                        'default_cell_id': 'CELL_INN_LOBBY_001',
                        'default_position': json.dumps({'x': 8.0, 'y': 0.0, 'z': 5.0}),
                        'interaction_type': 'sit',
                        'possible_states': json.dumps(['normal']),
                        'properties': json.dumps({
                            'comfort_level': 'high'
                        }),
                        'movable': True,
                        'passable': False
                    },
                    {
                        'object_id': 'OBJ_INN_LOBBY_CHAIR_003',
                        'object_name': '편안한 의자',
                        'object_description': '로비에 놓인 편안한 의자입니다. 푹신한 쿠션이 달려 있습니다.',
                        'object_type': 'interactive',
                        'default_cell_id': 'CELL_INN_LOBBY_001',
                        'default_position': json.dumps({'x': 5.0, 'y': 0.0, 'z': 10.0}),
                        'interaction_type': 'sit',
                        'possible_states': json.dumps(['normal']),
                        'properties': json.dumps({
                            'comfort_level': 'high'
                        }),
                        'movable': True,
                        'passable': False
                    },
                    {
                        'object_id': 'OBJ_INN_LOBBY_FRONT_DOOR_001',
                        'object_name': '앞문',
                        'object_description': '여관 밖으로 나가는 큰 문입니다.',
                        'object_type': 'interactive',
                        'default_cell_id': 'CELL_INN_LOBBY_001',
                        'default_position': json.dumps({'x': 10.0, 'y': 0.0, 'z': 14.0}),
                        'interaction_type': 'openable',
                        'possible_states': json.dumps(['closed', 'open']),
                        'properties': json.dumps({
                            'current_state': 'closed',
                            'leads_to': 'outside'
                        }),
                        'movable': False,
                        'passable': True
                    },
                    {
                        'object_id': 'OBJ_INN_LOBBY_TABLE_001',
                        'object_name': '작은 탁자',
                        'object_description': '의자들 사이에 놓인 작은 나무 탁자입니다. 위에는 신문과 잡지가 놓여 있습니다.',
                        'object_type': 'interactive',
                        'default_cell_id': 'CELL_INN_LOBBY_001',
                        'default_position': json.dumps({'x': 6.5, 'y': 0.5, 'z': 7.5}),
                        'interaction_type': 'examine',
                        'possible_states': json.dumps(['normal']),
                        'properties': json.dumps({
                            'contents': []
                        }),
                        'movable': True,
                        'passable': False
                    },
                    {
                        'object_id': 'OBJ_INN_LOBBY_BOOKSHELF_001',
                        'object_name': '책장',
                        'object_description': '로비 벽에 놓인 책장입니다. 여행 가이드와 소설들이 꽂혀 있습니다.',
                        'object_type': 'interactive',
                        'default_cell_id': 'CELL_INN_LOBBY_001',
                        'default_position': json.dumps({'x': 15.0, 'y': 1.5, 'z': 2.0}),
                        'interaction_type': 'examine',
                        'possible_states': json.dumps(['normal']),
                        'properties': json.dumps({
                            'contents': []
                        }),
                        'movable': False,
                        'passable': False,
                        'wall_mounted': True
                    },
                    {
                        'object_id': 'OBJ_INN_LOBBY_PLANT_001',
                        'object_name': '화분',
                        'object_description': '로비 구석에 놓인 초록 식물입니다. 잘 가꾸어진 것 같습니다.',
                        'object_type': 'static',
                        'default_cell_id': 'CELL_INN_LOBBY_001',
                        'default_position': json.dumps({'x': 2.0, 'y': 0.0, 'z': 12.0}),
                        'interaction_type': 'examine',
                        'possible_states': json.dumps(['normal']),
                        'properties': json.dumps({}),
                        'movable': True,
                        'passable': False
                    },
                    {
                        'object_id': 'OBJ_INN_ROOM_RUG_001',
                        'object_name': '양탄자',
                        'object_description': '침대 앞에 깔린 부드러운 양탄자입니다.',
                        'object_type': 'static',
                        'default_cell_id': 'CELL_INN_ROOM_001',
                        'default_position': json.dumps({'x': 5.0, 'y': 0.0, 'z': 8.0}),
                        'interaction_type': 'examine',
                        'possible_states': json.dumps(['normal']),
                        'properties': json.dumps({}),
                        'movable': False,
                        'passable': True
                    },
                    {
                        'object_id': 'OBJ_INN_ROOM_MIRROR_001',
                        'object_name': '거울',
                        'object_description': '벽에 걸린 작은 거울입니다. 자신의 모습을 볼 수 있습니다.',
                        'object_type': 'interactive',
                        'default_cell_id': 'CELL_INN_ROOM_001',
                        'default_position': json.dumps({'x': 0.0, 'y': 1.5, 'z': 8.0}),
                        'interaction_type': 'examine',
                        'possible_states': json.dumps(['normal']),
                        'properties': json.dumps({}),
                        'movable': False,
                        'passable': False,
                        'wall_mounted': True
                    },
                    {
                        'object_id': 'OBJ_INN_HALL_RUG_001',
                        'object_name': '복도 양탄자',
                        'object_description': '복도 바닥에 깔린 긴 양탄자입니다. 발소리를 줄여줍니다.',
                        'object_type': 'static',
                        'default_cell_id': 'CELL_INN_HALL_001',
                        'default_position': json.dumps({'x': 7.5, 'y': 0.0, 'z': 5.0}),
                        'interaction_type': 'examine',
                        'possible_states': json.dumps(['normal']),
                        'properties': json.dumps({}),
                        'movable': False,
                        'passable': True
                    }
                ]
                
                for obj in objects:
                    await conn.execute("""
                        INSERT INTO game_data.world_objects
                        (object_id, object_type, object_name, object_description, default_cell_id,
                         default_position, interaction_type, possible_states, properties,
                         wall_mounted, passable, movable,
                         object_height, object_width, object_depth, object_weight)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb, $9::jsonb,
                                $10, $11, $12, $13, $14, $15, $16)
                        ON CONFLICT (object_id) DO UPDATE SET
                            object_name = EXCLUDED.object_name,
                            object_description = EXCLUDED.object_description,
                            properties = EXCLUDED.properties
                    """,
                        obj['object_id'],
                        obj['object_type'],
                        obj['object_name'],
                        obj['object_description'],
                        obj['default_cell_id'],
                        obj['default_position'],
                        obj['interaction_type'],
                        obj['possible_states'],
                        obj['properties'],
                        obj.get('wall_mounted', False),
                        obj.get('passable', False),
                        obj.get('movable', False),
                        1.0,  # object_height
                        1.0,  # object_width
                        1.0,  # object_depth
                        0.0   # object_weight
                    )
                
                logger.info(f"  ✓ {len(objects)}개의 World Object 생성 완료")
                
                # ============================================================
                # 6. NPC Entities (인물)
                # ============================================================
                logger.info("\n[6/8] NPC Entities 생성 중...")
                
                npcs = [
                    {
                        'entity_id': 'NPC_INNKEEPER_001',
                        'entity_type': 'npc',
                        'entity_name': '여관주인 마리아',
                        'entity_description': '따뜻한 미소를 띤 여관주인입니다. 손님을 환대하는 것이 즐거운 것 같습니다.',
                        'base_stats': json.dumps({
                            'hp': 80,
                            'mp': 30,
                            'strength': 8,
                            'agility': 6,
                            'intelligence': 12,
                            'charisma': 15
                        }),
                        'default_equipment': json.dumps({}),
                        'default_abilities': json.dumps([]),
                        'default_inventory': json.dumps({
                            'items': [],
                            'quantities': {}
                        }),
                        'entity_properties': json.dumps({
                            'personality': 'friendly',
                            'occupation': '여관주인',
                            'mood': 'happy',
                            'dialogue_id': 'DIALOGUE_INNKEEPER_001',
                            'default_cell_id': 'CELL_INN_LOBBY_001',
                            'default_position': json.dumps({'x': 10.0, 'y': 0.0, 'z': 2.0}),
                            'can_interact': True
                        })
                    },
                    {
                        'entity_id': 'NPC_TRAVELER_001',
                        'entity_type': 'npc',
                        'entity_name': '여행자 엘라',
                        'entity_description': '로비에서 휴식을 취하고 있는 여행자입니다. 먼 곳에서 온 것 같습니다.',
                        'base_stats': json.dumps({
                            'hp': 60,
                            'mp': 40,
                            'strength': 7,
                            'agility': 10,
                            'intelligence': 11,
                            'charisma': 9
                        }),
                        'default_equipment': json.dumps({}),
                        'default_abilities': json.dumps([]),
                        'default_inventory': json.dumps({
                            'items': [],
                            'quantities': {}
                        }),
                        'entity_properties': json.dumps({
                            'personality': 'curious',
                            'occupation': '여행자',
                            'mood': 'relaxed',
                            'dialogue_id': 'DIALOGUE_TRAVELER_001',
                            'default_cell_id': 'CELL_INN_LOBBY_001',
                            'default_position': json.dumps({'x': 5.0, 'y': 0.0, 'z': 5.0}),
                            'can_interact': True,
                            'examine_text': '로비에서 휴식을 취하고 있는 여행자 엘라입니다. 먼 곳에서 온 것 같으며, 편안하게 의자에 앉아 있습니다. 여행 가방이 옆에 놓여 있습니다.'
                        })
                    },
                    {
                        'entity_id': 'NPC_MERCHANT_001',
                        'entity_type': 'npc',
                        'entity_name': '상인 토마스',
                        'entity_description': '로비에서 물건을 파는 상인입니다. 다양한 물건을 가지고 있는 것 같습니다.',
                        'base_stats': json.dumps({
                            'hp': 70,
                            'mp': 25,
                            'strength': 6,
                            'agility': 8,
                            'intelligence': 13,
                            'charisma': 14
                        }),
                        'default_equipment': json.dumps({}),
                        'default_abilities': json.dumps([]),
                        'default_inventory': json.dumps({
                            'items': ['ITEM_HEAL_POTION_001', 'ITEM_MANA_POTION_001'],
                            'quantities': {'ITEM_HEAL_POTION_001': 5, 'ITEM_MANA_POTION_001': 3}
                        }),
                        'entity_properties': json.dumps({
                            'personality': 'merchant',
                            'occupation': '상인',
                            'mood': 'business',
                            'dialogue_id': 'DIALOGUE_MERCHANT_001',
                            'default_cell_id': 'CELL_INN_LOBBY_001',
                            'default_position': json.dumps({'x': 12.0, 'y': 0.0, 'z': 8.0}),
                            'can_interact': True,
                            'can_trade': True,
                            'examine_text': '로비에서 물건을 파는 상인 토마스입니다. 다양한 물건을 가지고 있는 것 같습니다. 상인다운 차림새에 물건들이 가득 담긴 가방을 메고 있습니다.'
                        })
                    }
                ]
                
                for npc in npcs:
                    await conn.execute("""
                        INSERT INTO game_data.entities
                        (entity_id, entity_type, entity_name, entity_description,
                         base_stats, default_equipment, default_abilities,
                         default_inventory, entity_properties)
                        VALUES ($1, $2, $3, $4, $5::jsonb, $6::jsonb, $7::jsonb, $8::jsonb, $9::jsonb)
                        ON CONFLICT (entity_id) DO UPDATE SET
                            entity_description = EXCLUDED.entity_description,
                            entity_properties = EXCLUDED.entity_properties
                    """,
                        npc['entity_id'],
                        npc['entity_type'],
                        npc['entity_name'],
                        npc['entity_description'],
                        npc['base_stats'],
                        npc['default_equipment'],
                        npc['default_abilities'],
                        npc['default_inventory'],
                        npc['entity_properties']
                    )
                
                logger.info(f"  ✓ {len(npcs)}개의 NPC 생성 완료")
                
                # ============================================================
                # 7. Dialogue Contexts & Topics
                # ============================================================
                logger.info("\n[7/9] Dialogue Contexts & Topics 생성 중...")
                
                # 여관주인 다이얼로그
                await conn.execute("""
                    INSERT INTO game_data.dialogue_contexts
                    (dialogue_id, title, content, priority, entity_personality, available_topics, constraints)
                    VALUES ($1, $2, $3, $4, $5, $6::jsonb, $7::jsonb)
                    ON CONFLICT (dialogue_id) DO UPDATE SET
                        content = EXCLUDED.content,
                        available_topics = EXCLUDED.available_topics
                """,
                    'DIALOGUE_INNKEEPER_001',
                    '여관주인 마리아와의 대화',
                    '안녕하세요! 레크로스타 여관에 오신 것을 환영합니다. 편안하게 쉬시길 바랍니다.',
                    1,
                    'friendly',
                    json.dumps({
                        'topics': ['greeting', 'room_info', 'local_info', 'farewell'],
                        'default_topic': 'greeting'
                    }),
                    json.dumps({
                        'max_response_length': 200,
                        'tone': 'friendly'
                    })
                )
                
                # 여관주인 다이얼로그 토픽
                topics_innkeeper = [
                    {
                        'topic_id': 'TOPIC_INNKEEPER_GREETING',
                        'dialogue_id': 'DIALOGUE_INNKEEPER_001',
                        'topic_type': 'greeting',
                        'content': '안녕하세요! 오늘도 좋은 하루 되세요. 방은 편안하신가요?',
                        'conditions': json.dumps({})
                    },
                    {
                        'topic_id': 'TOPIC_INNKEEPER_ROOM',
                        'dialogue_id': 'DIALOGUE_INNKEEPER_001',
                        'topic_type': 'room_info',
                        'content': '2층에 있는 방은 모두 바다를 향해 있어서 아침에 일어나면 멋진 풍경을 볼 수 있어요. 특히 당신의 방은 조용하고 편안합니다.',
                        'conditions': json.dumps({})
                    },
                    {
                        'topic_id': 'TOPIC_INNKEEPER_LOCAL',
                        'dialogue_id': 'DIALOGUE_INNKEEPER_001',
                        'topic_type': 'local_info',
                        'content': '레크로스타는 정말 평화로운 곳이에요. 바다 소리와 따뜻한 햇살이 일상입니다. 근처에는 작은 시장도 있어요.',
                        'conditions': json.dumps({})
                    },
                    {
                        'topic_id': 'TOPIC_INNKEEPER_FAREWELL',
                        'dialogue_id': 'DIALOGUE_INNKEEPER_001',
                        'topic_type': 'farewell',
                        'content': '편안한 하루 되세요! 필요하시면 언제든지 말씀해 주세요.',
                        'conditions': json.dumps({})
                    }
                ]
                
                for topic in topics_innkeeper:
                    await conn.execute("""
                        INSERT INTO game_data.dialogue_topics
                        (topic_id, dialogue_id, topic_type, content, conditions)
                        VALUES ($1, $2, $3, $4, $5::jsonb)
                        ON CONFLICT (topic_id) DO UPDATE SET
                            content = EXCLUDED.content
                    """,
                        topic['topic_id'],
                        topic['dialogue_id'],
                        topic['topic_type'],
                        topic['content'],
                        topic['conditions']
                    )
                
                # 여행자 다이얼로그
                await conn.execute("""
                    INSERT INTO game_data.dialogue_contexts
                    (dialogue_id, title, content, priority, entity_personality, available_topics, constraints)
                    VALUES ($1, $2, $3, $4, $5, $6::jsonb, $7::jsonb)
                    ON CONFLICT (dialogue_id) DO UPDATE SET
                        content = EXCLUDED.content,
                        available_topics = EXCLUDED.available_topics
                """,
                    'DIALOGUE_TRAVELER_001',
                    '여행자 엘라와의 대화',
                    '안녕하세요! 여기 정말 좋은 곳이네요. 바다 소리가 들려서 마음이 편안해집니다.',
                    1,
                    'curious',
                    json.dumps({
                        'topics': ['greeting', 'travel', 'local_info', 'farewell'],
                        'default_topic': 'greeting'
                    }),
                    json.dumps({
                        'max_response_length': 200,
                        'tone': 'friendly'
                    })
                )
                
                topics_traveler = [
                    {
                        'topic_id': 'TOPIC_TRAVELER_GREETING',
                        'dialogue_id': 'DIALOGUE_TRAVELER_001',
                        'topic_type': 'greeting',
                        'content': '안녕하세요! 저는 엘라라고 해요. 먼 곳에서 여행을 하고 있습니다.',
                        'conditions': json.dumps({})
                    },
                    {
                        'topic_id': 'TOPIC_TRAVELER_TRAVEL',
                        'dialogue_id': 'DIALOGUE_TRAVELER_001',
                        'topic_type': 'travel',
                        'content': '동쪽의 큰 도시에서 왔어요. 레크로스타는 정말 평화롭고 아름다운 곳이네요. 바다를 보면서 휴식을 취하기에 완벽해요.',
                        'conditions': json.dumps({})
                    },
                    {
                        'topic_id': 'TOPIC_TRAVELER_LOCAL',
                        'dialogue_id': 'DIALOGUE_TRAVELER_001',
                        'topic_type': 'local_info',
                        'content': '이곳 사람들은 모두 친절하시고, 음식도 맛있어요. 특히 해산물이 신선하다고 들었어요.',
                        'conditions': json.dumps({})
                    },
                    {
                        'topic_id': 'TOPIC_TRAVELER_FAREWELL',
                        'dialogue_id': 'DIALOGUE_TRAVELER_001',
                        'topic_type': 'farewell',
                        'content': '좋은 여행 되세요! 언제든지 이야기하고 싶으시면 말씀해 주세요.',
                        'conditions': json.dumps({})
                    }
                ]
                
                for topic in topics_traveler:
                    await conn.execute("""
                        INSERT INTO game_data.dialogue_topics
                        (topic_id, dialogue_id, topic_type, content, conditions)
                        VALUES ($1, $2, $3, $4, $5::jsonb)
                        ON CONFLICT (topic_id) DO UPDATE SET
                            content = EXCLUDED.content
                    """,
                        topic['topic_id'],
                        topic['dialogue_id'],
                        topic['topic_type'],
                        topic['content'],
                        topic['conditions']
                    )
                
                # 상인 다이얼로그
                await conn.execute("""
                    INSERT INTO game_data.dialogue_contexts
                    (dialogue_id, title, content, priority, entity_personality, available_topics, constraints)
                    VALUES ($1, $2, $3, $4, $5, $6::jsonb, $7::jsonb)
                    ON CONFLICT (dialogue_id) DO UPDATE SET
                        content = EXCLUDED.content,
                        available_topics = EXCLUDED.available_topics
                """,
                    'DIALOGUE_MERCHANT_001',
                    '상인 토마스와의 대화',
                    '안녕하세요! 저는 토마스라고 합니다. 여행에 필요한 물건들을 판매하고 있어요.',
                    1,
                    'merchant',
                    json.dumps({
                        'topics': ['greeting', 'shop', 'items', 'farewell'],
                        'default_topic': 'greeting'
                    }),
                    json.dumps({
                        'max_response_length': 200,
                        'tone': 'business'
                    })
                )
                
                topics_merchant = [
                    {
                        'topic_id': 'TOPIC_MERCHANT_GREETING',
                        'dialogue_id': 'DIALOGUE_MERCHANT_001',
                        'topic_type': 'greeting',
                        'content': '안녕하세요! 여행에 필요한 물건이 있으시면 언제든지 말씀해 주세요. 치유 물약이나 마나 물약을 가지고 있어요.',
                        'conditions': json.dumps({})
                    },
                    {
                        'topic_id': 'TOPIC_MERCHANT_SHOP',
                        'dialogue_id': 'DIALOGUE_MERCHANT_001',
                        'topic_type': 'shop',
                        'content': '저는 주로 여행자들을 위해 물약을 판매해요. 치유 물약은 50골드, 마나 물약은 40골드입니다.',
                        'conditions': json.dumps({})
                    },
                    {
                        'topic_id': 'TOPIC_MERCHANT_ITEMS',
                        'dialogue_id': 'DIALOGUE_MERCHANT_001',
                        'topic_type': 'items',
                        'content': '현재 치유 물약 5개와 마나 물약 3개를 가지고 있어요. 필요하시면 구매하실 수 있습니다.',
                        'conditions': json.dumps({})
                    },
                    {
                        'topic_id': 'TOPIC_MERCHANT_FAREWELL',
                        'dialogue_id': 'DIALOGUE_MERCHANT_001',
                        'topic_type': 'farewell',
                        'content': '좋은 하루 되세요! 물건이 필요하시면 언제든지 말씀해 주세요.',
                        'conditions': json.dumps({})
                    }
                ]
                
                for topic in topics_merchant:
                    await conn.execute("""
                        INSERT INTO game_data.dialogue_topics
                        (topic_id, dialogue_id, topic_type, content, conditions)
                        VALUES ($1, $2, $3, $4, $5::jsonb)
                        ON CONFLICT (topic_id) DO UPDATE SET
                            content = EXCLUDED.content
                    """,
                        topic['topic_id'],
                        topic['dialogue_id'],
                        topic['topic_type'],
                        topic['content'],
                        topic['conditions']
                    )
                
                logger.info(f"  ✓ 3개의 Dialogue Context와 {len(topics_innkeeper) + len(topics_traveler) + len(topics_merchant)}개의 Topics 생성 완료")
                
                # ============================================================
                # 8. Player Entity Template
                # ============================================================
                logger.info("\n[8/9] Player Entity Template 생성 중...")
                
                await conn.execute("""
                    INSERT INTO game_data.entities
                    (entity_id, entity_type, entity_name, entity_description,
                     base_stats, default_equipment, default_abilities,
                     default_inventory, entity_properties)
                    VALUES ($1, $2, $3, $4, $5::jsonb, $6::jsonb, $7::jsonb, $8::jsonb, $9::jsonb)
                    ON CONFLICT (entity_id) DO UPDATE SET
                        entity_description = EXCLUDED.entity_description,
                        entity_properties = EXCLUDED.entity_properties,
                        base_stats = EXCLUDED.base_stats,
                        default_equipment = EXCLUDED.default_equipment,
                        default_inventory = EXCLUDED.default_inventory
                """,
                    'NPC_VILLAGER_001',
                    'player',
                    '당신',
                    '거울을 보는 것처럼 자신의 모습을 관찰할 수 있습니다. 평범해 보이지만 모험을 시작하려는 의지가 느껴집니다. 여행 가방을 메고 있고, 간단한 여행자 복장을 입고 있습니다.',
                    json.dumps({
                        'hp': 100,
                        'max_hp': 100,
                        'mp': 50,
                        'max_mp': 50,
                        'strength': 12,
                        'agility': 11,
                        'intelligence': 10,
                        'charisma': 9,
                        'defense': 5,
                        'magic_defense': 3
                    }),
                    json.dumps({
                        'weapon': 'ITEM_TRAVELER_SWORD_001',
                        'armor': 'ITEM_TRAVELER_CLOAK_001',
                        'accessory': None
                    }),
                    json.dumps([
                        'ABILITY_BASIC_ATTACK',
                        'ABILITY_DODGE'
                    ]),
                    json.dumps({
                        'items': [
                            'ITEM_HEAL_POTION_001',
                            'ITEM_MANA_POTION_001',
                            'ITEM_ENERGY_BAR_001',
                            'ITEM_TRAVELER_MAP_001'
                        ],
                        'quantities': {
                            'ITEM_HEAL_POTION_001': 2,
                            'ITEM_MANA_POTION_001': 1,
                            'ITEM_ENERGY_BAR_001': 3,
                            'ITEM_TRAVELER_MAP_001': 1
                        }
                    }),
                    json.dumps({
                        'level': 1,
                        'experience': 0,
                        'experience_to_next': 100,
                        'personality': 'neutral',
                        'occupation': '모험가',
                        'mood': '차분함',
                        'background': '레크로스타에 도착한 여행자입니다. 먼 곳에서 온 것 같으며, 모험을 시작하려는 의지가 느껴집니다.',
                        'examine_text': '당신은 거울에 비친 자신의 모습을 봅니다. 평범한 여행자 복장에 간단한 장비를 갖추고 있습니다. 여행 가방에는 몇 가지 물약과 지도가 들어있고, 허리에 찬 검은 아직 사용한 적이 없는 것 같습니다. 눈에는 호기심과 모험에 대한 열망이 보입니다.',
                        'can_interact': True
                    })
                )
                
                logger.info("  ✓ Player Entity Template 생성 완료")
                
                # ============================================================
                # 9. 완료 메시지
                # ============================================================
                logger.info("\n[9/9] 데이터 생성 완료!")
                logger.info("=" * 60)
                logger.info("생성된 데이터:")
                logger.info("  • Region: 레크로스타 (REG_RECROSTAR_001)")
                logger.info("  • Location: 레크로스타 여관 (LOC_RECROSTAR_INN_001)")
                logger.info("  • Cells: 내 방, 복도, 로비")
                logger.info(f"  • Effect Carriers: {len(effect_carriers)}개")
                logger.info(f"  • Items: {len(items)}개")
                logger.info(f"  • World Objects: {len(objects)}개")
                logger.info(f"  • NPCs: {len(npcs)}개")
                logger.info("  • Player Entity: NPC_VILLAGER_001")
                logger.info("=" * 60)
                logger.info("\n✅ 모든 데이터 생성 완료!")
                
    except Exception as e:
        logger.error(f"데이터 생성 실패: {str(e)}")
        raise
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(setup_inn_room_story_data())

