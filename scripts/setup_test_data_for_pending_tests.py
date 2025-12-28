"""
남은 테스트를 위한 추가 데이터 생성 스크립트

목적:
- Entity Interactions 테스트 (Dialogue, Trade, Combat)를 위한 데이터
- Cell Interactions 테스트 (Investigation, Visit, Movement)를 위한 데이터
"""
import asyncio
import json
import uuid
from database.connection import DatabaseConnection
from common.utils.logger import logger


async def setup_test_data_for_pending_tests():
    """남은 테스트를 위한 데이터 생성"""
    db = DatabaseConnection()
    await db.initialize()
    
    try:
        pool = await db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                logger.info("=" * 60)
                logger.info("남은 테스트를 위한 데이터 생성 시작")
                logger.info("=" * 60)
                
                # ============================================================
                # 1. NPC 엔티티 (대화/거래용)
                # ============================================================
                logger.info("\n[1/5] NPC 엔티티 생성 중...")
                
                npcs = [
                    {
                        'entity_id': 'NPC_INNKEEPER_001',
                        'entity_name': '여관주인',
                        'entity_description': '레크로스타 여관의 주인입니다. 따뜻하고 친근한 성격입니다.',
                        'entity_type': 'npc',
                        'base_stats': json.dumps({
                            'hp': 100,
                            'mp': 50,
                            'strength': 8,
                            'agility': 10,
                            'intelligence': 15,
                            'charisma': 18
                        }),
                        'entity_properties': json.dumps({
                            'personality': 'friendly',
                            'occupation': 'innkeeper',
                            'mood': 'happy',
                            'dialogue_id': 'DIALOGUE_INNKEEPER_001',
                            'can_trade': True,
                            'can_talk': True,
                            'gold': 500
                        }),
                        'default_inventory': json.dumps({
                            'items': ['ITEM_HEAL_POTION_001', 'ITEM_MANA_POTION_001'],
                            'quantities': {'ITEM_HEAL_POTION_001': 5, 'ITEM_MANA_POTION_001': 3}
                        })
                    },
                    {
                        'entity_id': 'NPC_MERCHANT_RECROSTAR_001',
                        'entity_name': '레크로스타 상인',
                        'entity_description': '레크로스타 마을의 상인입니다. 다양한 물건을 판매합니다.',
                        'entity_type': 'npc',
                        'base_stats': json.dumps({
                            'hp': 80,
                            'mp': 40,
                            'strength': 6,
                            'agility': 8,
                            'intelligence': 14,
                            'charisma': 16
                        }),
                        'entity_properties': json.dumps({
                            'personality': 'greedy',
                            'occupation': 'merchant',
                            'mood': 'neutral',
                            'dialogue_id': 'DIALOGUE_MERCHANT_001',
                            'can_trade': True,
                            'can_talk': True,
                            'gold': 1000
                        }),
                        'default_inventory': json.dumps({
                            'items': ['ITEM_HEAL_POTION_001', 'ITEM_MANA_POTION_001', 'ITEM_ENERGY_BAR_001'],
                            'quantities': {'ITEM_HEAL_POTION_001': 10, 'ITEM_MANA_POTION_001': 8, 'ITEM_ENERGY_BAR_001': 15}
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
                            entity_properties = EXCLUDED.entity_properties,
                            default_inventory = EXCLUDED.default_inventory
                    """,
                        npc['entity_id'],
                        npc['entity_type'],
                        npc['entity_name'],
                        npc['entity_description'],
                        npc['base_stats'],
                        json.dumps([]),  # default_equipment
                        json.dumps([]),  # default_abilities
                        npc['default_inventory'],
                        npc['entity_properties']
                    )
                
                logger.info(f"  ✓ {len(npcs)}개의 NPC 생성 완료")
                
                # ============================================================
                # 2. 적대 엔티티 (전투용)
                # ============================================================
                logger.info("\n[2/5] 적대 엔티티 생성 중...")
                
                enemies = [
                    {
                        'entity_id': 'NPC_GOBLIN_RECROSTAR_001',
                        'entity_name': '고블린',
                        'entity_description': '레크로스타 근처에 나타난 작은 고블린입니다. 공격적입니다.',
                        'entity_type': 'enemy',
                        'base_stats': json.dumps({
                            'hp': 50,
                            'mp': 10,
                            'strength': 8,
                            'agility': 12,
                            'intelligence': 3
                        }),
                        'entity_properties': json.dumps({
                            'personality': 'aggressive',
                            'faction': 'monster',
                            'ai_behavior': 'hostile',
                            'is_hostile': True
                        }),
                        'default_inventory': json.dumps({
                            'items': [],
                            'quantities': {}
                        })
                    }
                ]
                
                for enemy in enemies:
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
                        enemy['entity_id'],
                        enemy['entity_type'],
                        enemy['entity_name'],
                        enemy['entity_description'],
                        enemy['base_stats'],
                        json.dumps([]),  # default_equipment
                        json.dumps([]),  # default_abilities
                        enemy['default_inventory'],
                        enemy['entity_properties']
                    )
                
                logger.info(f"  ✓ {len(enemies)}개의 적대 엔티티 생성 완료")
                
                # ============================================================
                # 3. Dialogue Contexts & Topics
                # ============================================================
                logger.info("\n[3/5] Dialogue 데이터 생성 중...")
                
                # 여관주인 대화
                await conn.execute("""
                    INSERT INTO game_data.dialogue_contexts
                    (dialogue_id, title, content, priority, entity_id, entity_personality, available_topics, constraints)
                    VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb, $8::jsonb)
                    ON CONFLICT (dialogue_id) DO UPDATE SET
                        content = EXCLUDED.content,
                        available_topics = EXCLUDED.available_topics
                """,
                    'DIALOGUE_INNKEEPER_001',
                    '여관주인 인사',
                    '어서오세요! 레크로스타 여관에 오신 것을 환영합니다. 편안한 하루 보내시길 바랍니다.',
                    1,
                    'NPC_INNKEEPER_001',
                    '따뜻하고 친근한 여관주인. 손님을 환대하는 것을 좋아합니다.',
                    json.dumps({
                        'topics': ['greeting', 'room_info', 'local_news', 'farewell'],
                        'default_topic': 'greeting'
                    }),
                    json.dumps({
                        'max_response_length': 200,
                        'tone': 'friendly'
                    })
                )
                
                # 여관주인 대화 주제
                await conn.execute("""
                    INSERT INTO game_data.dialogue_topics
                    (topic_id, dialogue_id, topic_type, content, conditions)
                    VALUES ($1, $2, $3, $4, $5::jsonb)
                    ON CONFLICT (topic_id) DO UPDATE SET
                        content = EXCLUDED.content
                """,
                    'TOPIC_INNKEEPER_GREETING_001',
                    'DIALOGUE_INNKEEPER_001',
                    'greeting',
                    '레크로스타는 아름다운 해안가 마을입니다. 바다 소리를 들으며 휴식을 취하실 수 있습니다.',
                    json.dumps({})
                )
                
                await conn.execute("""
                    INSERT INTO game_data.dialogue_topics
                    (topic_id, dialogue_id, topic_type, content, conditions)
                    VALUES ($1, $2, $3, $4, $5::jsonb)
                    ON CONFLICT (topic_id) DO UPDATE SET
                        content = EXCLUDED.content
                """,
                    'TOPIC_INNKEEPER_ROOM_001',
                    'DIALOGUE_INNKEEPER_001',
                    'room_info',
                    '2층에 있는 방은 모두 깨끗하게 정리되어 있습니다. 창문에서 바다를 보실 수 있어요.',
                    json.dumps({})
                )
                
                # 상인 대화
                await conn.execute("""
                    INSERT INTO game_data.dialogue_contexts
                    (dialogue_id, title, content, priority, entity_id, entity_personality, available_topics, constraints)
                    VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb, $8::jsonb)
                    ON CONFLICT (dialogue_id) DO UPDATE SET
                        content = EXCLUDED.content,
                        available_topics = EXCLUDED.available_topics
                """,
                    'DIALOGUE_MERCHANT_001',
                    '상인 인사',
                    '안녕하세요! 레크로스타 상점입니다. 무엇을 찾고 계신가요?',
                    1,
                    'NPC_MERCHANT_RECROSTAR_001',
                    '상업적이고 친근한 상인. 좋은 거래를 중시합니다.',
                    json.dumps({
                        'topics': ['greeting', 'trade', 'local_news', 'farewell'],
                        'default_topic': 'greeting'
                    }),
                    json.dumps({
                        'max_response_length': 200,
                        'tone': 'friendly'
                    })
                )
                
                # 상인 대화 주제
                await conn.execute("""
                    INSERT INTO game_data.dialogue_topics
                    (topic_id, dialogue_id, topic_type, content, conditions)
                    VALUES ($1, $2, $3, $4, $5::jsonb)
                    ON CONFLICT (topic_id) DO UPDATE SET
                        content = EXCLUDED.content
                """,
                    'TOPIC_MERCHANT_GREETING_001',
                    'DIALOGUE_MERCHANT_001',
                    'greeting',
                    '레크로스타는 휴양지라서 여행자들이 많이 오시죠. 다양한 물건을 준비해두었습니다.',
                    json.dumps({})
                )
                
                await conn.execute("""
                    INSERT INTO game_data.dialogue_topics
                    (topic_id, dialogue_id, topic_type, content, conditions)
                    VALUES ($1, $2, $3, $4, $5::jsonb)
                    ON CONFLICT (topic_id) DO UPDATE SET
                        content = EXCLUDED.content
                """,
                    'TOPIC_MERCHANT_TRADE_001',
                    'DIALOGUE_MERCHANT_001',
                    'trade',
                    '치유 물약, 마나 물약, 에너지 바를 판매하고 있습니다. 필요하시면 언제든 말씀해주세요.',
                    json.dumps({})
                )
                
                logger.info("  ✓ Dialogue Contexts & Topics 생성 완료")
                
                # ============================================================
                # 4. 셀에 NPC 배치용 데이터 (셀-엔티티 연결)
                # ============================================================
                logger.info("\n[4/5] 셀-엔티티 연결 정보 확인 중...")
                
                # 이미 생성된 셀들에 NPC를 배치할 수 있도록 정보 확인
                # (실제 배치는 런타임에 InstanceFactory가 처리)
                logger.info("  ✓ 셀-엔티티 연결은 런타임에 처리됩니다")
                
                # ============================================================
                # 5. 완료 메시지
                # ============================================================
                logger.info("\n[5/5] 데이터 생성 완료!")
                logger.info("=" * 60)
                logger.info("생성된 데이터:")
                logger.info(f"  • NPC 엔티티: {len(npcs)}개")
                logger.info(f"    - NPC_INNKEEPER_001 (여관주인, 대화/거래 가능)")
                logger.info(f"    - NPC_MERCHANT_RECROSTAR_001 (상인, 대화/거래 가능)")
                logger.info(f"  • 적대 엔티티: {len(enemies)}개")
                logger.info(f"    - NPC_GOBLIN_RECROSTAR_001 (고블린, 전투용)")
                logger.info("  • Dialogue Contexts: 2개")
                logger.info("    - DIALOGUE_INNKEEPER_001")
                logger.info("    - DIALOGUE_MERCHANT_001")
                logger.info("  • Dialogue Topics: 4개")
                logger.info("=" * 60)
                logger.info("\n✅ 모든 테스트 데이터 생성 완료!")
                logger.info("\n📋 테스트 가능한 기능:")
                logger.info("  1. Entity Interactions:")
                logger.info("     - Dialogue: NPC_INNKEEPER_001, NPC_MERCHANT_RECROSTAR_001")
                logger.info("     - Trade: NPC_INNKEEPER_001, NPC_MERCHANT_RECROSTAR_001")
                logger.info("     - Combat: NPC_GOBLIN_RECROSTAR_001")
                logger.info("  2. Cell Interactions:")
                logger.info("     - Investigation: CELL_INN_ROOM_001, CELL_INN_HALL_001, CELL_INN_LOBBY_001")
                logger.info("     - Visit: 연결된 셀들 (cell_properties.connected_cells)")
                logger.info("     - Movement: CELL_INN_ROOM_001 ↔ CELL_INN_HALL_001 ↔ CELL_INN_LOBBY_001")
                
    except Exception as e:
        logger.error(f"데이터 생성 실패: {str(e)}")
        raise
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(setup_test_data_for_pending_tests())

