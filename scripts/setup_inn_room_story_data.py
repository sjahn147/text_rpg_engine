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
                # 6. Player Entity Template
                # ============================================================
                logger.info("\n[6/7] Player Entity Template 생성 중...")
                
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
                    'NPC_VILLAGER_001',
                    'player',
                    '당신',
                    '거울을 보는 것처럼 자신의 모습을 관찰할 수 있습니다. 평범해 보이지만 모험을 시작하려는 의지가 느껴집니다.',
                    json.dumps({
                        'hp': 100,
                        'mp': 50,
                        'strength': 10,
                        'agility': 10,
                        'intelligence': 10
                    }),
                    json.dumps([]),
                    json.dumps([]),
                    json.dumps({
                        'items': [],
                        'quantities': {}
                    }),
                    json.dumps({
                        'level': 1,
                        'experience': 0,
                        'personality': 'neutral',
                        'occupation': '모험가',
                        'mood': '차분함'
                    })
                )
                
                logger.info("  ✓ Player Entity Template 생성 완료")
                
                # ============================================================
                # 7. 완료 메시지
                # ============================================================
                logger.info("\n[7/7] 데이터 생성 완료!")
                logger.info("=" * 60)
                logger.info("생성된 데이터:")
                logger.info("  • Region: 레크로스타 (REG_RECROSTAR_001)")
                logger.info("  • Location: 레크로스타 여관 (LOC_RECROSTAR_INN_001)")
                logger.info("  • Cells: 내 방, 복도, 로비")
                logger.info(f"  • Effect Carriers: {len(effect_carriers)}개")
                logger.info(f"  • Items: {len(items)}개")
                logger.info(f"  • World Objects: {len(objects)}개")
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

