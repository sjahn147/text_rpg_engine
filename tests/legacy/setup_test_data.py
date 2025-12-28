#!/usr/bin/env python3
"""
GUI 테스트를 위한 테스트 데이터 설정 스크립트
"""

import asyncio
import json
import uuid
from datetime import datetime
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository

async def setup_test_data():
    """테스트 데이터 설정"""
    print("GUI 테스트를 위한 데이터를 설정합니다...")
    
    db = DatabaseConnection()
    game_data = GameDataRepository(db_connection)
    runtime_data = RuntimeDataRepository(db_connection)
    reference_layer = ReferenceLayerRepository(db_connection)
    
    try:
        pool = await db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                print("1. 테스트 플레이어 엔티티 생성...")
                
                # 플레이어 엔티티 생성
                await conn.execute(
                    """
                    INSERT INTO game_data.entities 
                    (entity_id, entity_type, entity_name, entity_description, base_stats, entity_properties)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (entity_id) DO NOTHING
                    """,
                    "TEST_PLAYER_001",
                    "player",
                    "테스트 플레이어",
                    "GUI 테스트용 플레이어 캐릭터",
                    json.dumps({
                        "hp": 100,
                        "hp_max": 100,
                        "mp": 50,
                        "mp_max": 50,
                        "strength": 15,
                        "defense": 10,
                        "level": 1
                    }),
                    json.dumps({
                        "is_hostile": False,
                        "interaction_flags": ["can_move", "can_talk"],
                        "player_class": "warrior"
                    })
                )
                
                print("2. 테스트 NPC 엔티티 생성...")
                
                # NPC 엔티티 생성
                await conn.execute(
                    """
                    INSERT INTO game_data.entities 
                    (entity_id, entity_type, entity_name, entity_description, base_stats, entity_properties, dialogue_context_id)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (entity_id) DO NOTHING
                    """,
                    "TEST_NPC_001",
                    "npc",
                    "상인 토마스",
                    "무기 상점을 운영하는 상인",
                    json.dumps({
                        "hp": 100,
                        "mp": 30,
                        "level": 15
                    }),
                    json.dumps({
                        "is_hostile": False,
                        "interaction_flags": ["can_trade", "can_talk"],
                        "shop_type": "weapons"
                    }),
                    "MERCHANT_GREETING"
                )
                
                print("3. 테스트 세션 생성...")
                
                # 테스트 세션 생성
                session_id = str(uuid.uuid4())
                await conn.execute(
                    """
                    INSERT INTO runtime_data.active_sessions 
                    (session_id, session_state, metadata)
                    VALUES ($1, $2, $3)
                    """,
                    session_id,
                    "active",
                    json.dumps({
                        "test_session": True,
                        "created_for": "gui_test",
                        "created_at": datetime.now().isoformat()
                    })
                )
                
                print("4. 엔티티 참조 생성...")
                
                # 플레이어 엔티티 참조
                player_runtime_id = str(uuid.uuid4())
                await conn.execute(
                    """
                    INSERT INTO reference_layer.entity_references 
                    (runtime_entity_id, game_entity_id, session_id, entity_type, is_player)
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    player_runtime_id,
                    "TEST_PLAYER_001",
                    session_id,
                    "player",
                    True
                )
                
                # NPC 엔티티 참조
                npc_runtime_id = str(uuid.uuid4())
                await conn.execute(
                    """
                    INSERT INTO reference_layer.entity_references 
                    (runtime_entity_id, game_entity_id, session_id, entity_type, is_player)
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    npc_runtime_id,
                    "TEST_NPC_001",
                    session_id,
                    "npc",
                    False
                )
                
                print("5. 셀 참조 생성...")
                
                # 실제 존재하는 셀 ID 사용
                cell_id = "CELL_VILLAGE_CENTER_001"  # 실제 존재하는 셀 ID
                
                # 테스트 셀 참조
                cell_runtime_id = str(uuid.uuid4())
                await conn.execute(
                    """
                    INSERT INTO reference_layer.cell_references 
                    (runtime_cell_id, game_cell_id, session_id)
                    VALUES ($1, $2, $3)
                    """,
                    cell_runtime_id,
                    cell_id,
                    session_id
                )
                
                print("6. 엔티티 상태 생성...")
                
                # 플레이어 상태
                await conn.execute(
                    """
                    INSERT INTO runtime_data.entity_states 
                    (runtime_entity_id, runtime_cell_id, current_stats, current_position, inventory, equipped_items)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    player_runtime_id,
                    cell_runtime_id,
                    json.dumps({
                        "hp": 100,
                        "hp_max": 100,
                        "mp": 50,
                        "mp_max": 50,
                        "strength": 15,
                        "defense": 10,
                        "level": 1
                    }),
                    json.dumps({"x": 50, "y": 0, "z": 50}),
                    json.dumps({
                        "items": ["ITEM_POTION_HEAL_001", "ITEM_SWORD_BASIC_001"],
                        "quantities": {
                            "ITEM_POTION_HEAL_001": 5,
                            "ITEM_SWORD_BASIC_001": 1
                        }
                    }),
                    json.dumps({
                        "weapon": "WEAPON_SWORD_NORMAL_001",
                        "armor": "ARMOR_LEATHER_001"
                    })
                )
                
                # NPC 상태
                await conn.execute(
                    """
                    INSERT INTO runtime_data.entity_states 
                    (runtime_entity_id, runtime_cell_id, current_stats, current_position)
                    VALUES ($1, $2, $3, $4)
                    """,
                    npc_runtime_id,
                    cell_runtime_id,
                    json.dumps({
                        "hp": 100,
                        "mp": 30,
                        "level": 15
                    }),
                    json.dumps({"x": 100, "y": 0, "z": 100})
                )
                
                print("7. 세션에 플레이어 참조 추가...")
                
                await conn.execute(
                    """
                    UPDATE runtime_data.active_sessions
                    SET player_runtime_entity_id = $1
                    WHERE session_id = $2
                    """,
                    player_runtime_id,
                    session_id
                )
                
                print(f"✅ 테스트 데이터 설정 완료!")
                print(f"세션 ID: {session_id}")
                print(f"플레이어 런타임 ID: {player_runtime_id}")
                print(f"NPC 런타임 ID: {npc_runtime_id}")
                print(f"셀 런타임 ID: {cell_runtime_id}")
                print(f"사용된 셀 ID: {cell_id}")
                print("\n이제 GUI에서 '새 게임'을 선택하면 테스트 데이터가 로드됩니다.")
                
    except Exception as e:
        print(f"❌ 테스트 데이터 설정 중 오류 발생: {e}")
        raise

async def cleanup_test_data():
    """테스트 데이터 정리"""
    print("테스트 데이터를 정리합니다...")
    
    db = DatabaseConnection()
    
    try:
        pool = await db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                # 테스트 세션들 정리
                await conn.execute(
                    """
                    CALL runtime_data.cleanup_session(session_id)
                    FROM runtime_data.active_sessions
                    WHERE metadata->>'test_session' = 'true'
                    """
                )
                
                print("✅ 테스트 데이터 정리 완료!")
                
    except Exception as e:
        print(f"❌ 테스트 데이터 정리 중 오류 발생: {e}")

def main():
    """메인 함수"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "cleanup":
        asyncio.run(cleanup_test_data())
    else:
        asyncio.run(setup_test_data())

if __name__ == "__main__":
    main() 