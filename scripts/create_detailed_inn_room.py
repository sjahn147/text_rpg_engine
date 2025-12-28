"""
여관 내 방 데이터를 상세하게 생성하는 스크립트

DB가 지원하는 모든 엔티티를 사용하여 내 방을 자세하게 구성합니다.
- 상세한 description
- 다양한 오브젝트들 (침대, 책상, 창문, 가방, 책장 등)
- 상호작용 가능한 오브젝트들
"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from database.factories.world_data_factory import WorldDataFactory


async def create_detailed_inn_room():
    """여관 내 방을 상세하게 생성"""
    factory = WorldDataFactory()
    
    # 레크로스타 지역이 이미 있는지 확인하고, 없으면 생성
    # 기존 데이터와 충돌하지 않도록 새로운 ID 사용
    region_config = {
        "region_id": "REG_RECROSTAR_01",
        "region_name": "레크로스타",
        "region_type": "resort",
        "description": "한적한 휴양지 레크로스타. 따뜻한 해안가의 작은 마을입니다.",
        "properties": {
            "climate": "temperate",
            "season": "spring",
            "atmosphere": "peaceful"
        },
        "locations": [
            {
                "location_id": "LOC_RECROSTAR_INN_01",
                "location_name": "여관",
                "description": "레크로스타의 중심가에 위치한 아늑한 여관. 여행자들에게 따뜻한 휴식처를 제공합니다.",
                "properties": {
                    "type": "inn",
                    "owner": "여관주인 마리아",
                    "atmosphere": "cozy"
                },
                "cells": [
                    {
                        "cell_id": "CELL_INN_ROOM_001",
                        "cell_name": "내 방",
                        "description": """여관 2층에 있는 당신의 방입니다. 

창문을 통해 레크로스타의 아름다운 해안가 풍경이 보입니다. 따뜻한 햇살이 방 안을 환하게 비추고, 바다 소리가 멀리서 들려옵니다.

방은 작지만 깔끔하게 정리되어 있습니다. 나무로 만든 침대가 한쪽 벽에 놓여 있고, 그 옆에는 작은 책상이 있습니다. 책상 위에는 여행 가방이 놓여 있고, 벽에는 작은 책장이 달려 있습니다.

문은 복도로 이어지고, 창문은 바다를 향해 열려 있습니다. 이곳에서 하루를 시작하는 것이 기대됩니다.""",
                        "matrix_width": 20,
                        "matrix_height": 20,
                        "properties": {
                            "terrain": "indoor",
                            "lighting": "bright",
                            "temperature": "comfortable",
                            "atmosphere": "peaceful",
                            "background_music": "inn_room_peaceful",
                            "ambient_effects": ["sea_waves", "seagulls"],
                            "detail_sections": [
                                {
                                    "section": "침대",
                                    "description": "편안해 보이는 나무 침대입니다. 깨끗한 침구가 정돈되어 있습니다."
                                },
                                {
                                    "section": "책상",
                                    "description": "작은 나무 책상입니다. 위에는 여행 가방이 놓여 있습니다."
                                },
                                {
                                    "section": "창문",
                                    "description": "큰 창문이 바다를 향해 열려 있습니다. 따뜻한 햇살이 들어옵니다."
                                },
                                {
                                    "section": "책장",
                                    "description": "벽에 달린 작은 책장입니다. 몇 권의 책이 꽂혀 있습니다."
                                }
                            ]
                        },
                        "characters": [
                            # 내 방에는 NPC가 없지만, 필요하면 추가 가능
                        ],
                        "world_objects": [
                            {
                                "object_id": "OBJ_INN_BED_001",
                                "object_type": "interactive",
                                "object_name": "침대",
                                "description": "편안해 보이는 나무 침대입니다. 깨끗한 침구가 정돈되어 있습니다. 잠을 자거나 휴식을 취할 수 있습니다.",
                                "default_position": {"x": 3.0, "y": 2.0, "z": 0.0},
                                "interaction_type": "rest",
                                "possible_states": ["made", "unmade", "slept_in"],
                                "properties": {
                                    "material": "wood",
                                    "comfort_level": 8,
                                    "can_sleep": True,
                                    "can_rest": True,
                                    "interaction_text": "침대에 누워 휴식을 취합니다.",
                                    "restore_hp": 50,
                                    "restore_mp": 30
                                },
                                "wall_mounted": False,
                                "passable": False,
                                "movable": False,
                                "object_height": 0.8,
                                "object_width": 2.0,
                                "object_depth": 1.5,
                                "object_weight": 50.0
                            },
                            {
                                "object_id": "OBJ_INN_DESK_001",
                                "object_type": "interactive",
                                "object_name": "책상",
                                "description": "작은 나무 책상입니다. 위에는 여행 가방이 놓여 있습니다. 물건을 정리하거나 읽을 수 있습니다.",
                                "default_position": {"x": 6.0, "y": 3.0, "z": 0.0},
                                "interaction_type": "examine",
                                "possible_states": ["clean", "cluttered"],
                                "properties": {
                                    "material": "wood",
                                    "has_drawer": True,
                                    "can_write": True,
                                    "can_read": True,
                                    "interaction_text": "책상을 살펴봅니다.",
                                    "contents": ["ITEM_PAPER_BLANK_001", "ITEM_PEN_BASIC_001"]
                                },
                                "wall_mounted": False,
                                "passable": False,
                                "movable": False,
                                "object_height": 0.75,
                                "object_width": 1.2,
                                "object_depth": 0.6,
                                "object_weight": 15.0
                            },
                            {
                                "object_id": "OBJ_INN_WINDOW_001",
                                "object_type": "interactive",
                                "object_name": "창문",
                                "description": "큰 창문이 바다를 향해 열려 있습니다. 따뜻한 햇살이 들어오고, 멀리서 바다 소리가 들려옵니다. 밖의 풍경을 감상할 수 있습니다.",
                                "default_position": {"x": 10.0, "y": 5.0, "z": 0.0},
                                "interaction_type": "examine",
                                "possible_states": ["open", "closed"],
                                "properties": {
                                    "material": "glass",
                                    "view": "ocean",
                                    "can_open": True,
                                    "can_close": True,
                                    "interaction_text": "창문 밖을 내다봅니다.",
                                    "view_description": "레크로스타의 아름다운 해안가가 보입니다. 파란 바다와 하얀 모래사장, 그리고 멀리서 날아오는 갈매기들이 보입니다."
                                },
                                "wall_mounted": True,
                                "passable": False,
                                "movable": False,
                                "object_height": 1.5,
                                "object_width": 2.0,
                                "object_depth": 0.1,
                                "object_weight": 5.0
                            },
                            {
                                "object_id": "OBJ_INN_BOOKSHELF_001",
                                "object_type": "interactive",
                                "object_name": "책장",
                                "description": "벽에 달린 작은 책장입니다. 몇 권의 책이 꽂혀 있습니다. 책을 읽을 수 있습니다.",
                                "default_position": {"x": 1.0, "y": 4.0, "z": 0.0},
                                "interaction_type": "examine",
                                "possible_states": ["organized", "messy"],
                                "properties": {
                                    "material": "wood",
                                    "book_count": 5,
                                    "can_read": True,
                                    "interaction_text": "책장을 살펴봅니다.",
                                    "books": [
                                        "레크로스타 여행 가이드",
                                        "바다의 전설",
                                        "해양 생물 도감",
                                        "요리 레시피 모음",
                                        "고대 지도"
                                    ]
                                },
                                "wall_mounted": True,
                                "passable": False,
                                "movable": False,
                                "object_height": 1.2,
                                "object_width": 1.0,
                                "object_depth": 0.3,
                                "object_weight": 10.0
                            },
                            {
                                "object_id": "OBJ_INN_BAG_001",
                                "object_type": "interactive",
                                "object_name": "여행 가방",
                                "description": "책상 위에 놓인 여행 가방입니다. 당신의 소지품들이 들어 있습니다. 가방을 열어 내용물을 확인할 수 있습니다.",
                                "default_position": {"x": 6.0, "y": 3.0, "z": 0.3},
                                "interaction_type": "openable",
                                "possible_states": ["closed", "open"],
                                "properties": {
                                    "material": "leather",
                                    "can_open": True,
                                    "can_close": True,
                                    "interaction_text": "가방을 엽니다.",
                                    "contents": ["ITEM_CLOTHING_BASIC_001", "ITEM_TOOL_TRAVEL_001", "ITEM_COIN_GOLD_001", "ITEM_MAP_RECROSTAR_001"],
                                    "inventory_slots": 20
                                },
                                "wall_mounted": False,
                                "passable": False,
                                "movable": True,
                                "object_height": 0.4,
                                "object_width": 0.5,
                                "object_depth": 0.3,
                                "object_weight": 2.0
                            },
                            {
                                "object_id": "OBJ_INN_DOOR_001",
                                "object_type": "interactive",
                                "object_name": "문",
                                "description": "복도로 이어지는 문입니다. 문을 열어 밖으로 나갈 수 있습니다.",
                                "default_position": {"x": 0.0, "y": 5.0, "z": 0.0},
                                "interaction_type": "openable",
                                "possible_states": ["closed", "open"],
                                "properties": {
                                    "material": "wood",
                                    "can_open": True,
                                    "can_close": True,
                                    "leads_to": "복도",
                                    "interaction_text": "문을 엽니다.",
                                    "connected_cell": "CELL_INN_HALLWAY_001"
                                },
                                "wall_mounted": True,
                                "passable": False,
                                "movable": False,
                                "object_height": 2.0,
                                "object_width": 0.9,
                                "object_depth": 0.1,
                                "object_weight": 20.0
                            },
                            {
                                "object_id": "OBJ_INN_CHAIR_001",
                                "object_type": "interactive",
                                "object_name": "의자",
                                "description": "책상 앞에 놓인 나무 의자입니다. 앉아서 휴식을 취하거나 책을 읽을 수 있습니다.",
                                "default_position": {"x": 5.5, "y": 3.0, "z": 0.0},
                                "interaction_type": "sit",
                                "possible_states": ["empty", "occupied"],
                                "properties": {
                                    "material": "wood",
                                    "can_sit": True,
                                    "comfort_level": 6,
                                    "interaction_text": "의자에 앉습니다.",
                                    "restore_mp": 10
                                },
                                "wall_mounted": False,
                                "passable": False,
                                "movable": True,
                                "object_height": 0.9,
                                "object_width": 0.5,
                                "object_depth": 0.5,
                                "object_weight": 5.0
                            },
                            {
                                "object_id": "OBJ_INN_CANDLE_001",
                                "object_type": "interactive",
                                "object_name": "양초",
                                "description": "책상 위에 놓인 양초입니다. 밤에 불을 켜서 방을 밝힐 수 있습니다.",
                                "default_position": {"x": 6.2, "y": 3.0, "z": 0.3},
                                "interaction_type": "lightable",
                                "possible_states": ["unlit", "lit"],
                                "properties": {
                                    "material": "wax",
                                    "can_light": True,
                                    "can_extinguish": True,
                                    "light_radius": 3,
                                    "burn_time": 3600,
                                    "interaction_text": "양초에 불을 켭니다.",
                                    "current_burn_time": 3600
                                },
                                "wall_mounted": False,
                                "passable": True,
                                "movable": True,
                                "object_height": 0.15,
                                "object_width": 0.05,
                                "object_depth": 0.05,
                                "object_weight": 0.1
                            },
                            {
                                "object_id": "OBJ_INN_MIRROR_001",
                                "object_type": "static",
                                "object_name": "거울",
                                "description": "벽에 걸린 작은 거울입니다. 자신의 모습을 확인할 수 있습니다.",
                                "default_position": {"x": 8.0, "y": 4.0, "z": 0.0},
                                "interaction_type": "examine",
                                "possible_states": ["clean", "dirty"],
                                "properties": {
                                    "material": "glass",
                                    "can_examine": True,
                                    "interaction_text": "거울을 봅니다.",
                                    "reflection_description": "당신의 모습이 거울에 비춰집니다."
                                },
                                "wall_mounted": True,
                                "passable": False,
                                "movable": False,
                                "object_height": 0.5,
                                "object_width": 0.4,
                                "object_depth": 0.05,
                                "object_weight": 2.0
                            },
                            {
                                "object_id": "OBJ_INN_RUG_001",
                                "object_type": "static",
                                "object_name": "양탄자",
                                "description": "바닥에 깔린 작은 양탄자입니다. 방을 더욱 아늑하게 만들어줍니다.",
                                "default_position": {"x": 5.0, "y": 4.0, "z": 0.0},
                                "interaction_type": "none",
                                "possible_states": ["clean", "dirty"],
                                "properties": {
                                    "material": "fabric",
                                    "color": "red",
                                    "pattern": "geometric",
                                    "interaction_text": "양탄자를 살펴봅니다."
                                },
                                "wall_mounted": False,
                                "passable": True,
                                "movable": True,
                                "object_height": 0.02,
                                "object_width": 2.0,
                                "object_depth": 1.5,
                                "object_weight": 3.0
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    try:
        print("=" * 60)
        print("여관 내 방 데이터 생성 시작")
        print("=" * 60)
        
        # Region과 하위 엔티티 생성
        result = await factory.create_region_with_children(region_config)
        
        print("\n✅ 생성 완료!")
        print(f"  - Region ID: {result['region_id']}")
        print(f"  - Location IDs: {result['location_ids']}")
        print(f"  - Cell IDs: {result['cell_ids']}")
        print(f"  - Entity IDs: {result['entity_ids']}")
        print(f"  - Object IDs: {len(result['object_ids'])}개")
        print(f"    {', '.join(result['object_ids'])}")
        
        print("\n📋 생성된 오브젝트 목록:")
        for obj_id in result['object_ids']:
            print(f"  - {obj_id}")
        
        print("\n" + "=" * 60)
        print("내 방 데이터가 성공적으로 생성되었습니다!")
        print("=" * 60)
        
        return result
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(create_detailed_inn_room())

