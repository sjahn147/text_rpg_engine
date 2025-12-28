"""
레크레스타 상세 구현 Factory

시스템이 지원하는 모든 엔티티 요소를 사용하여 레크레스타를 매우 세밀하게 구현합니다.
- Region: 레크레스타
- Locations: 호텔, 저택, 카페 거리, 해수욕장, 해식 동굴, 별장, 뒷골목, 마사지샵, 항구, 리조트, 주거지역, 시장, 요새 유적
- Cells: 각 Location의 세부 방들
- Entities: 다양한 NPC들 (호텔 주인, 상점 주인, 모험가, 군인, 갱단 등)
- World Objects: 가구, 상품, 장식품 등
- Cell Properties: 온도, 조명, 분위기 등
"""
import asyncio
import json
from pathlib import Path
import sys

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from database.factories.world_data_factory import WorldDataFactory


async def create_rekresta():
    """레크레스타를 매우 세밀하게 생성"""
    factory = WorldDataFactory()
    
    # 기존 레크레스타 데이터 삭제 (있는 경우)
    pool = await factory.db.pool
    async with pool.acquire() as conn:
        async with conn.transaction():
            # Region ID로 관련 데이터 찾기
            region_row = await conn.fetchrow(
                "SELECT region_id FROM game_data.world_regions WHERE region_id = $1",
                "REG_REKRESTA"
            )
            
            if region_row:
                print("기존 레크레스타 데이터 발견. 삭제 중...")
                # 역순으로 삭제 (외래키 제약조건 고려)
                # 1. Entity References 삭제 (레크레스타 관련 Entity ID 패턴)
                rekresta_entity_patterns = [
                    'NPC_HOTEL_%',
                    'NPC_MANSION_%',
                    'NPC_CAFE_%',
                    'NPC_RETIRED_%',
                    'NPC_BEACH_%',
                    'NPC_GANG_%',
                    'NPC_INFORMANT',
                    'NPC_MARKET_%',
                    'NPC_SOLDIER_%',
                    'NPC_BARMAID',
                    'NPC_MASSAGE_%',
                    'NPC_HARBOR_%',
                    'NPC_SHIP_%',
                    'NPC_RUINS_%',
                    'NPC_NOBLE_%'
                ]
                for pattern in rekresta_entity_patterns:
                    await conn.execute("""
                        DELETE FROM reference_layer.entity_references 
                        WHERE game_entity_id LIKE $1
                    """, pattern)
                
                # 2. Entities 삭제 (레크레스타 관련 모든 Entity ID 패턴)
                for pattern in rekresta_entity_patterns:
                    await conn.execute("""
                        DELETE FROM game_data.entities 
                        WHERE entity_id LIKE $1
                    """, pattern)
                
                # 3. Cell References 삭제
                rekresta_cell_patterns = [
                    'CELL_HOTEL_%',
                    'CELL_MANSION_%',
                    'CELL_CAFE_%',
                    'CELL_BEACH_%',
                    'CELL_BACK_ALLEY_%',
                    'CELL_MARKET_%',
                    'CELL_RESORT_%',
                    'CELL_CAVE_%',
                    'CELL_MASSAGE_%',
                    'CELL_HARBOR_%',
                    'CELL_RUINS_%',
                    'CELL_PRIVATE_BEACH_%',
                    'CELL_VILLA_%',
                    'CELL_RESIDENTIAL_%'
                ]
                for pattern in rekresta_cell_patterns:
                    await conn.execute("""
                        DELETE FROM reference_layer.cell_references 
                        WHERE game_cell_id LIKE $1
                    """, pattern)
                
                # 4. World Objects 삭제
                for pattern in rekresta_cell_patterns:
                    await conn.execute("""
                        DELETE FROM game_data.world_objects 
                        WHERE default_cell_id LIKE $1
                    """, pattern)
                
                # 5. Cells 삭제 (레크레스타 관련 모든 Cell ID 패턴)
                rekresta_cell_patterns = [
                    'CELL_HOTEL_%',
                    'CELL_MANSION_%',
                    'CELL_CAFE_%',
                    'CELL_BEACH_%',
                    'CELL_BACK_ALLEY_%',
                    'CELL_MARKET_%',
                    'CELL_RESORT_%',
                    'CELL_CAVE_%',
                    'CELL_MASSAGE_%',
                    'CELL_HARBOR_%',
                    'CELL_RUINS_%',
                    'CELL_PRIVATE_BEACH_%',
                    'CELL_VILLA_%',
                    'CELL_RESIDENTIAL_%'
                ]
                for pattern in rekresta_cell_patterns:
                    await conn.execute("""
                        DELETE FROM game_data.world_cells 
                        WHERE cell_id LIKE $1
                    """, pattern)
                
                # 6. Locations 삭제
                await conn.execute("""
                    DELETE FROM game_data.world_locations 
                    WHERE region_id = $1
                """, "REG_REKRESTA")
                
                # 7. Region 삭제
                await conn.execute("""
                    DELETE FROM game_data.world_regions 
                    WHERE region_id = $1
                """, "REG_REKRESTA")
                
                print("기존 데이터 삭제 완료.")
    
    # 레크레스타 Region 설정
    rekresta_config = {
        "region_id": "REG_REKRESTA",
        "region_name": "레크레스타",
        "region_type": "city",
        "description": "아발룸의 귀족과 젠트리들이 놀러오는 아름다운 여름 휴양지. 해변을 접하고 있는 관광지로, 전직 모험가들이 은퇴하고 살고 싶어하는 도시이다.",
        "properties": {
            "population": 5000,
            "living_standard": "upper_middle",
            "economy": "tourism",
            "security": "good",
            "ruler": "부르겐 남작",
            "theme": "아름다운 것은 거기에 비밀이 있기 때문",
            "climate": "mediterranean",
            "special_features": [
                "해변 휴양지",
                "밤문화 성행",
                "제국군 주둔지 인접",
                "조르가즈 갱 활동"
            ]
        },
        "locations": [
            # 1. 레크레스타 호텔
            {
                "location_id": "LOC_REKRESTA_HOTEL",
                "location_name": "레크레스타 호텔",
                "location_type": "hotel",
                "description": "최고의 서비스를 제공하는 레크레스타의 대표 호텔. 아발룸의 귀족들이 즐겨 찾는 곳이다.",
                "properties": {
                    "quality": "luxury",
                    "price_level": "very_high",
                    "services": ["room_service", "spa", "restaurant", "bar"]
                },
                "cells": [
                    {
                        "cell_id": "CELL_HOTEL_LOBBY",
                        "cell_name": "호텔 로비",
                        "matrix_width": 30,
                        "matrix_height": 25,
                        "cell_description": "대리석 바닥과 크리스탈 샹들리에가 있는 화려한 로비. 접수 데스크와 편안한 소파가 배치되어 있다.",
                        "cell_properties": {
                            "environment": {
                                "temperature": 22.0,
                                "humidity": 45.0,
                                "air_quality": "fresh",
                                "visibility": 100.0
                            },
                            "terrain": {
                                "type": "stone",
                                "elevation": 0.0,
                                "water_level": 0.0
                            },
                            "lighting": {
                                "level": "bright",
                                "source": "chandelier",
                                "color_temperature": 3000,
                                "flicker": False
                            },
                            "atmosphere": {
                                "ambiance": "luxurious",
                                "music": "hotel_lobby_01",
                                "background_noise": "moderate"
                            }
                        },
                        "characters": [
                            {
                                "entity_id": "NPC_HOTEL_MANAGER",
                                "entity_name": "호텔 지배인 엘리자베스",
                                "entity_type": "npc",
                                "base_stats": {
                                    "strength": 8,
                                    "dexterity": 12,
                                    "constitution": 10,
                                    "intelligence": 16,
                                    "wisdom": 14,
                                    "charisma": 18
                                },
                                "entity_properties": {
                                    "template_type": "merchant",
                                    "occupation": "hotel_manager",
                                    "personality": "professional",
                                    "dialogue": "어서오세요, 레크레스타 호텔입니다. 최고의 서비스를 제공하겠습니다."
                                },
                                "default_position_3d": {"x": 15.0, "y": 5.0, "z": 0.0},
                                "entity_size": "medium"
                            },
                            {
                                "entity_id": "NPC_HOTEL_BELLBOY",
                                "entity_name": "벨보이 토마스",
                                "entity_type": "npc",
                                "base_stats": {
                                    "strength": 12,
                                    "dexterity": 14,
                                    "constitution": 11,
                                    "intelligence": 10,
                                    "wisdom": 10,
                                    "charisma": 13
                                },
                                "entity_properties": {
                                    "template_type": "npc",
                                    "occupation": "bellboy",
                                    "personality": "friendly",
                                    "dialogue": "짐을 들어드릴까요?"
                                },
                                "default_position_3d": {"x": 20.0, "y": 10.0, "z": 0.0},
                                "entity_size": "medium"
                            }
                        ],
                        "world_objects": [
                            {
                                "object_id": "OBJ_HOTEL_RECEPTION_DESK",
                                "object_type": "interactive",
                                "object_name": "접수 데스크",
                                "description": "대리석으로 만든 화려한 접수 데스크",
                                "default_position": {"x": 15.0, "y": 3.0},
                                "interaction_type": "talk",
                                "properties": {"interaction": "check_in"},
                                "wall_mounted": False,
                                "passable": False,
                                "movable": False,
                                "object_height": 1.2,
                                "object_width": 4.0,
                                "object_depth": 0.8,
                                "object_weight": 200.0
                            },
                            {
                                "object_id": "OBJ_HOTEL_SOFA_1",
                                "object_type": "static",
                                "object_name": "고급 소파",
                                "description": "부드러운 가죽 소파",
                                "default_position": {"x": 5.0, "y": 15.0},
                                "interaction_type": "sit",
                                "properties": {"comfort": "high"},
                                "wall_mounted": False,
                                "passable": False,
                                "movable": True,
                                "object_height": 0.8,
                                "object_width": 2.0,
                                "object_depth": 1.0,
                                "object_weight": 50.0
                            },
                            {
                                "object_id": "OBJ_HOTEL_CHANDELIER",
                                "object_type": "static",
                                "object_name": "크리스탈 샹들리에",
                                "description": "천장에 매달린 화려한 샹들리에",
                                "default_position": {"x": 15.0, "y": 12.0},
                                "interaction_type": "none",
                                "properties": {},
                                "wall_mounted": True,
                                "passable": True,
                                "movable": False,
                                "object_height": 1.5,
                                "object_width": 2.0,
                                "object_depth": 2.0,
                                "object_weight": 100.0
                            }
                        ]
                    },
                    {
                        "cell_id": "CELL_HOTEL_RESTAURANT",
                        "cell_name": "호텔 레스토랑",
                        "matrix_width": 25,
                        "matrix_height": 20,
                        "cell_description": "바다를 바라보는 전망이 좋은 레스토랑. 신선한 해산물 요리가 유명하다.",
                        "cell_properties": {
                            "environment": {
                                "temperature": 21.0,
                                "humidity": 50.0,
                                "air_quality": "fresh",
                                "visibility": 100.0
                            },
                            "terrain": {
                                "type": "wooden_floor",
                                "elevation": 0.0
                            },
                            "lighting": {
                                "level": "moderate",
                                "source": "window",
                                "color_temperature": 4000
                            },
                            "atmosphere": {
                                "ambiance": "elegant",
                                "music": "restaurant_01",
                                "background_noise": "moderate"
                            }
                        },
                        "characters": [
                            {
                                "entity_id": "NPC_HOTEL_CHEF",
                                "entity_name": "셰프 마르코",
                                "entity_type": "npc",
                                "base_stats": {
                                    "strength": 14,
                                    "dexterity": 16,
                                    "constitution": 13,
                                    "intelligence": 12,
                                    "wisdom": 15,
                                    "charisma": 11
                                },
                                "entity_properties": {
                                    "template_type": "npc",
                                    "occupation": "chef",
                                    "personality": "passionate",
                                    "dialogue": "오늘의 특선은 신선한 해산물 파스타입니다!"
                                },
                                "default_position_3d": {"x": 20.0, "y": 18.0, "z": 0.0},
                                "entity_size": "medium"
                            },
                            {
                                "entity_id": "NPC_HOTEL_WAITER",
                                "entity_name": "웨이터 안나",
                                "entity_type": "npc",
                                "base_stats": {
                                    "strength": 9,
                                    "dexterity": 14,
                                    "constitution": 10,
                                    "intelligence": 11,
                                    "wisdom": 12,
                                    "charisma": 16
                                },
                                "entity_properties": {
                                    "template_type": "npc",
                                    "occupation": "waiter",
                                    "personality": "cheerful",
                                    "dialogue": "주문하시겠어요?"
                                },
                                "default_position_3d": {"x": 12.0, "y": 10.0, "z": 0.0},
                                "entity_size": "medium"
                            }
                        ],
                        "world_objects": [
                            {
                                "object_id": "OBJ_RESTAURANT_TABLE_1",
                                "object_type": "interactive",
                                "object_name": "식탁",
                                "description": "흰색 테이블보가 깔린 식탁",
                                "default_position": {"x": 8.0, "y": 8.0},
                                "interaction_type": "sit",
                                "properties": {"seats": 4},
                                "wall_mounted": False,
                                "passable": False,
                                "movable": True,
                                "object_height": 0.75,
                                "object_width": 1.2,
                                "object_depth": 1.2,
                                "object_weight": 30.0
                            },
                            {
                                "object_id": "OBJ_RESTAURANT_WINDOW",
                                "object_type": "static",
                                "object_name": "바다 전망 창문",
                                "description": "넓은 바다를 바라보는 큰 창문",
                                "default_position": {"x": 0.0, "y": 10.0},
                                "interaction_type": "view",
                                "properties": {"view": "ocean"},
                                "wall_mounted": True,
                                "passable": True,
                                "movable": False,
                                "object_height": 2.5,
                                "object_width": 8.0,
                                "object_depth": 0.1,
                                "object_weight": 50.0
                            }
                        ]
                    },
                    {
                        "cell_id": "CELL_HOTEL_SUITE_101",
                        "cell_name": "스위트룸 101",
                        "matrix_width": 15,
                        "matrix_height": 12,
                        "cell_description": "호텔 최고급 스위트룸. 넓은 발코니와 바다 전망이 있다.",
                        "cell_properties": {
                            "environment": {
                                "temperature": 23.0,
                                "humidity": 40.0,
                                "air_quality": "fresh",
                                "visibility": 100.0
                            },
                            "terrain": {
                                "type": "wooden_floor",
                                "elevation": 0.0
                            },
                            "lighting": {
                                "level": "moderate",
                                "source": "window",
                                "color_temperature": 3500
                            },
                            "atmosphere": {
                                "ambiance": "luxurious",
                                "music": "hotel_room_01",
                                "background_noise": "quiet"
                            }
                        },
                        "characters": [],
                        "world_objects": [
                            {
                                "object_id": "OBJ_SUITE_BED",
                                "object_type": "interactive",
                                "object_name": "킹사이즈 침대",
                                "description": "부드러운 매트리스와 고급 이불",
                                "default_position": {"x": 7.0, "y": 8.0},
                                "interaction_type": "rest",
                                "properties": {"rest_quality": "excellent"},
                                "wall_mounted": False,
                                "passable": False,
                                "movable": False,
                                "object_height": 0.6,
                                "object_width": 2.0,
                                "object_depth": 2.2,
                                "object_weight": 150.0
                            },
                            {
                                "object_id": "OBJ_SUITE_BALCONY",
                                "object_type": "interactive",
                                "object_name": "발코니",
                                "description": "바다를 바라보는 넓은 발코니",
                                "default_position": {"x": 0.0, "y": 6.0},
                                "interaction_type": "view",
                                "properties": {"view": "ocean", "outdoor": True},
                                "wall_mounted": False,
                                "passable": True,
                                "movable": False,
                                "object_height": 0.1,
                                "object_width": 15.0,
                                "object_depth": 3.0,
                                "object_weight": 0.1
                            }
                        ]
                    }
                ]
            },
            # 2. 남작의 저택
            {
                "location_id": "LOC_BARON_MANSION",
                "location_name": "부르겐 남작의 저택",
                "location_type": "mansion",
                "description": "검은 마차가 많이 오가는 부르겐 남작의 저택. 비밀스러운 분위기가 감돈다.",
                "properties": {
                    "owner": "부르겐 남작",
                    "security": "high",
                    "mystery": "high"
                },
                "cells": [
                    {
                        "cell_id": "CELL_MANSION_ENTRANCE",
                        "cell_name": "저택 현관",
                        "matrix_width": 20,
                        "matrix_height": 15,
                        "cell_description": "어두운 분위기의 현관. 검은 대리석 바닥과 벽에 걸린 초상화들이 있다.",
                        "cell_properties": {
                            "environment": {
                                "temperature": 18.0,
                                "humidity": 50.0,
                                "air_quality": "normal",
                                "visibility": 60.0
                            },
                            "terrain": {
                                "type": "stone",
                                "elevation": 0.0
                            },
                            "lighting": {
                                "level": "dim",
                                "source": "torch",
                                "color_temperature": 2000,
                                "flicker": True
                            },
                            "atmosphere": {
                                "ambiance": "mysterious",
                                "music": "mansion_01",
                                "background_noise": "quiet"
                            }
                        },
                        "characters": [
                            {
                                "entity_id": "NPC_MANSION_BUTLER",
                                "entity_name": "집사 윌리엄",
                                "entity_type": "npc",
                                "base_stats": {
                                    "strength": 12,
                                    "dexterity": 13,
                                    "constitution": 11,
                                    "intelligence": 14,
                                    "wisdom": 15,
                                    "charisma": 12
                                },
                                "entity_properties": {
                                    "template_type": "npc",
                                    "occupation": "butler",
                                    "personality": "formal",
                                    "dialogue": "남작님께서 기다리고 계십니다."
                                },
                                "default_position_3d": {"x": 10.0, "y": 3.0, "z": 0.0},
                                "entity_size": "medium"
                            }
                        ],
                        "world_objects": [
                            {
                                "object_id": "OBJ_MANSION_PORTRAIT_1",
                                "object_type": "interactive",
                                "object_name": "초상화",
                                "description": "부르겐 가문의 선조 초상화",
                                "default_position": {"x": 2.0, "y": 2.0},
                                "interaction_type": "examine",
                                "properties": {"secret": "hidden_compartment"},
                                "wall_mounted": True,
                                "passable": True,
                                "movable": False,
                                "object_height": 1.5,
                                "object_width": 1.0,
                                "object_depth": 0.1,
                                "object_weight": 10.0
                            }
                        ]
                    }
                ]
            },
            # 3. 카페 거리
            {
                "location_id": "LOC_CAFE_STREET",
                "location_name": "카페 거리",
                "location_type": "street",
                "description": "천천히 흐르는 시간이 느껴지는 카페 거리. 작은 카페들이 줄지어 있다.",
                "properties": {
                    "atmosphere": "relaxed",
                    "time_flow": "slow"
                },
                "cells": [
                    {
                        "cell_id": "CELL_CAFE_STREET_MAIN",
                        "cell_name": "카페 거리 본거리",
                        "matrix_width": 40,
                        "matrix_height": 20,
                        "cell_description": "포장된 돌길과 양옆에 늘어선 카페들. 평화로운 분위기가 흐른다.",
                        "cell_properties": {
                            "environment": {
                                "temperature": 25.0,
                                "humidity": 55.0,
                                "air_quality": "fresh",
                                "visibility": 100.0
                            },
                            "terrain": {
                                "type": "stone",
                                "elevation": 0.0
                            },
                            "lighting": {
                                "level": "bright",
                                "source": "sun",
                                "color_temperature": 5500
                            },
                            "weather": {
                                "type": "clear",
                                "intensity": 0.0,
                                "wind_speed": 2.0,
                                "precipitation": "none"
                            },
                            "atmosphere": {
                                "ambiance": "peaceful",
                                "music": "cafe_street_01",
                                "background_noise": "moderate"
                            }
                        },
                        "characters": [
                            {
                                "entity_id": "NPC_CAFE_OWNER_1",
                                "entity_name": "카페 주인 마리아",
                                "entity_type": "npc",
                                "base_stats": {
                                    "strength": 8,
                                    "dexterity": 12,
                                    "constitution": 10,
                                    "intelligence": 13,
                                    "wisdom": 14,
                                    "charisma": 16
                                },
                                "entity_properties": {
                                    "template_type": "merchant",
                                    "occupation": "cafe_owner",
                                    "personality": "warm",
                                    "dialogue": "오늘도 좋은 하루 되세요!",
                                    "shop_inventory": ["coffee", "tea", "pastry"]
                                },
                                "default_position_3d": {"x": 15.0, "y": 10.0, "z": 0.0},
                                "entity_size": "medium"
                            },
                            {
                                "entity_id": "NPC_RETIRED_ADVENTURER",
                                "entity_name": "은퇴한 모험가 잭",
                                "entity_type": "npc",
                                "base_stats": {
                                    "strength": 14,
                                    "dexterity": 13,
                                    "constitution": 15,
                                    "intelligence": 12,
                                    "wisdom": 16,
                                    "charisma": 11
                                },
                                "entity_properties": {
                                    "template_type": "quest_giver",
                                    "occupation": "retired_adventurer",
                                    "personality": "wise",
                                    "dialogue": "레크레스타는 정말 살기 좋은 곳이야. 모험은 그만두고 여기서 평화롭게 살고 있어.",
                                    "available_quests": ["rekresta_secrets"]
                                },
                                "default_position_3d": {"x": 25.0, "y": 12.0, "z": 0.0},
                                "entity_size": "medium"
                            }
                        ],
                        "world_objects": [
                            {
                                "object_id": "OBJ_CAFE_TABLE_1",
                                "object_type": "interactive",
                                "object_name": "야외 테이블",
                                "description": "거리에 놓인 작은 테이블",
                                "default_position": {"x": 18.0, "y": 10.0},
                                "interaction_type": "sit",
                                "properties": {"seats": 2},
                                "wall_mounted": False,
                                "passable": False,
                                "movable": True,
                                "object_height": 0.7,
                                "object_width": 0.8,
                                "object_depth": 0.8,
                                "object_weight": 15.0
                            }
                        ]
                    }
                ]
            },
            # 4. 해수욕장
            {
                "location_id": "LOC_BEACH",
                "location_name": "해수욕장",
                "location_type": "beach",
                "description": "안브레티아의 보석이라 불리는 아름다운 해수욕장. 하얀 모래사장과 푸른 바다가 있다.",
                "properties": {
                    "beauty": "exceptional",
                    "popularity": "high"
                },
                "cells": [
                    {
                        "cell_id": "CELL_BEACH_MAIN",
                        "cell_name": "해수욕장 본해변",
                        "matrix_width": 50,
                        "matrix_height": 30,
                        "cell_description": "넓은 하얀 모래사장과 푸른 바다. 휴양객들이 즐겁게 놀고 있다.",
                        "cell_properties": {
                            "environment": {
                                "temperature": 28.0,
                                "humidity": 70.0,
                                "air_quality": "fresh",
                                "visibility": 100.0
                            },
                            "terrain": {
                                "type": "sand",
                                "elevation": 0.0,
                                "water_level": 0.0
                            },
                            "lighting": {
                                "level": "bright",
                                "source": "sun",
                                "color_temperature": 6000
                            },
                            "weather": {
                                "type": "clear",
                                "intensity": 0.0,
                                "wind_speed": 5.0,
                                "precipitation": "none"
                            },
                            "atmosphere": {
                                "ambiance": "peaceful",
                                "music": "beach_01",
                                "sound_effects": ["waves", "seagulls"],
                                "background_noise": "moderate"
                            },
                            "gameplay": {
                                "spawn_points": [
                                    {"id": "beach_spawn_1", "position": {"x": 25.0, "y": 5.0, "z": 0.0}, "type": "player"}
                                ],
                                "safe_zones": [
                                    {"area": {"x": 0, "y": 0, "width": 50, "height": 30}}
                                ]
                            }
                        },
                        "characters": [
                            {
                                "entity_id": "NPC_BEACH_VENDOR",
                                "entity_name": "해변 상인 페드로",
                                "entity_type": "npc",
                                "base_stats": {
                                    "strength": 10,
                                    "dexterity": 13,
                                    "constitution": 11,
                                    "intelligence": 12,
                                    "wisdom": 11,
                                    "charisma": 15
                                },
                                "entity_properties": {
                                    "template_type": "merchant",
                                    "occupation": "beach_vendor",
                                    "personality": "cheerful",
                                    "dialogue": "신선한 음료와 기념품 팝니다!",
                                    "shop_inventory": ["drink", "souvenir", "snack"]
                                },
                                "default_position_3d": {"x": 10.0, "y": 15.0, "z": 0.0},
                                "entity_size": "medium"
                            },
                            {
                                "entity_id": "NPC_BEACH_GUARD",
                                "entity_name": "해변 경비원 카를로스",
                                "entity_type": "npc",
                                "base_stats": {
                                    "strength": 15,
                                    "dexterity": 12,
                                    "constitution": 14,
                                    "intelligence": 10,
                                    "wisdom": 13,
                                    "charisma": 11
                                },
                                "entity_properties": {
                                    "template_type": "npc",
                                    "occupation": "guard",
                                    "personality": "dutiful",
                                    "dialogue": "안전하게 즐기세요!"
                                },
                                "default_position_3d": {"x": 40.0, "y": 20.0, "z": 0.0},
                                "entity_size": "medium"
                            }
                        ],
                        "world_objects": [
                            {
                                "object_id": "OBJ_BEACH_UMBRELLA",
                                "object_type": "static",
                                "object_name": "파라솔",
                                "description": "해변에 꽂힌 파라솔",
                                "default_position": {"x": 20.0, "y": 10.0},
                                "interaction_type": "shade",
                                "properties": {"shade_area": 3.0},
                                "wall_mounted": False,
                                "passable": True,
                                "movable": False,
                                "object_height": 2.5,
                                "object_width": 3.0,
                                "object_depth": 3.0,
                                "object_weight": 20.0
                            },
                            {
                                "object_id": "OBJ_BEACH_CHAIR",
                                "object_type": "interactive",
                                "object_name": "해변 의자",
                                "description": "편안한 해변 의자",
                                "default_position": {"x": 22.0, "y": 10.0},
                                "interaction_type": "sit",
                                "properties": {"comfort": "medium"},
                                "wall_mounted": False,
                                "passable": False,
                                "movable": True,
                                "object_height": 0.5,
                                "object_width": 0.6,
                                "object_depth": 0.8,
                                "object_weight": 8.0
                            }
                        ]
                    }
                ]
            },
            # 5. 뒷골목
            {
                "location_id": "LOC_BACK_ALLEY",
                "location_name": "뒷골목",
                "location_type": "alley",
                "description": "급한 사람들만 오는 뒷골목. 밤문화가 성행하는 곳으로, 조르가즈 갱의 활동 무대이기도 하다.",
                "properties": {
                    "security": "low",
                    "nightlife": "active",
                    "gang_activity": "present"
                },
                "cells": [
                    {
                        "cell_id": "CELL_BACK_ALLEY_MAIN",
                        "cell_name": "뒷골목 본거리",
                        "matrix_width": 25,
                        "matrix_height": 15,
                        "cell_description": "어둡고 좁은 골목. 벽에 낙서가 있고, 어딘가에서 술취한 목소리가 들린다.",
                        "cell_properties": {
                            "environment": {
                                "temperature": 20.0,
                                "humidity": 60.0,
                                "air_quality": "stale",
                                "visibility": 40.0
                            },
                            "terrain": {
                                "type": "stone",
                                "elevation": 0.0
                            },
                            "lighting": {
                                "level": "dim",
                                "source": "torch",
                                "color_temperature": 2000,
                                "flicker": True
                            },
                            "atmosphere": {
                                "ambiance": "dangerous",
                                "music": "back_alley_01",
                                "sound_effects": ["distant_voices", "footsteps"],
                                "background_noise": "moderate"
                            },
                            "gameplay": {
                                "danger_zones": [
                                    {"area": {"x": 0, "y": 0, "width": 25, "height": 15}, "damage_per_second": 0, "damage_type": "none"}
                                ]
                            }
                        },
                        "characters": [
                            {
                                "entity_id": "NPC_GANG_MEMBER_1",
                                "entity_name": "조르가즈 갱단원",
                                "entity_type": "npc",
                                "base_stats": {
                                    "strength": 14,
                                    "dexterity": 13,
                                    "constitution": 12,
                                    "intelligence": 10,
                                    "wisdom": 9,
                                    "charisma": 11
                                },
                                "entity_properties": {
                                    "template_type": "npc",
                                    "occupation": "gang_member",
                                    "personality": "aggressive",
                                    "dialogue": "여기서 뭐하는 거야?",
                                    "faction": "조르가즈 갱"
                                },
                                "default_position_3d": {"x": 12.0, "y": 8.0, "z": 0.0},
                                "entity_size": "medium"
                            },
                            {
                                "entity_id": "NPC_INFORMANT",
                                "entity_name": "정보상",
                                "entity_type": "npc",
                                "base_stats": {
                                    "strength": 8,
                                    "dexterity": 14,
                                    "constitution": 9,
                                    "intelligence": 16,
                                    "wisdom": 15,
                                    "charisma": 13
                                },
                                "entity_properties": {
                                    "template_type": "quest_giver",
                                    "occupation": "informant",
                                    "personality": "sly",
                                    "dialogue": "정보가 필요하면 말해. 물론 돈이 있어야 해.",
                                    "available_quests": ["gang_info"]
                                },
                                "default_position_3d": {"x": 20.0, "y": 5.0, "z": 0.0},
                                "entity_size": "small"
                            }
                        ],
                        "world_objects": [
                            {
                                "object_id": "OBJ_ALLEY_BARREL",
                                "object_type": "static",
                                "object_name": "나무 통",
                                "description": "쓰레기가 가득한 나무 통",
                                "default_position": {"x": 5.0, "y": 10.0},
                                "interaction_type": "search",
                                "properties": {"loot_chance": 0.3},
                                "wall_mounted": False,
                                "passable": False,
                                "movable": True,
                                "object_height": 1.0,
                                "object_width": 0.8,
                                "object_depth": 0.8,
                                "object_weight": 30.0
                            }
                        ]
                    }
                ]
            },
            # 6. 시장
            {
                "location_id": "LOC_MARKET",
                "location_name": "레크레스타 시장",
                "location_type": "market",
                "description": "없는 것 빼고 다 있는 시장. 관광객과 주민들이 함께 이용하는 활기찬 곳이다.",
                "properties": {
                    "variety": "high",
                    "crowd": "busy"
                },
                "cells": [
                    {
                        "cell_id": "CELL_MARKET_MAIN",
                        "cell_name": "시장 본거리",
                        "matrix_width": 45,
                        "matrix_height": 30,
                        "cell_description": "넓은 시장 광장. 수많은 상점과 노점이 줄지어 있다.",
                        "cell_properties": {
                            "environment": {
                                "temperature": 26.0,
                                "humidity": 55.0,
                                "air_quality": "normal",
                                "visibility": 100.0
                            },
                            "terrain": {
                                "type": "stone",
                                "elevation": 0.0
                            },
                            "lighting": {
                                "level": "bright",
                                "source": "sun",
                                "color_temperature": 5500
                            },
                            "weather": {
                                "type": "clear",
                                "intensity": 0.0,
                                "wind_speed": 3.0,
                                "precipitation": "none"
                            },
                            "atmosphere": {
                                "ambiance": "lively",
                                "music": "market_01",
                                "sound_effects": ["haggling", "crowd"],
                                "background_noise": "loud"
                            }
                        },
                        "characters": [
                            {
                                "entity_id": "NPC_MARKET_MERCHANT_1",
                                "entity_name": "상인 아흐메드",
                                "entity_type": "npc",
                                "base_stats": {
                                    "strength": 10,
                                    "dexterity": 12,
                                    "constitution": 11,
                                    "intelligence": 14,
                                    "wisdom": 13,
                                    "charisma": 16
                                },
                                "entity_properties": {
                                    "template_type": "merchant",
                                    "occupation": "merchant",
                                    "personality": "persuasive",
                                    "dialogue": "좋은 물건 많이 있습니다!",
                                    "shop_inventory": ["weapon", "armor", "potion", "misc"],
                                    "bargain_skill": 8
                                },
                                "default_position_3d": {"x": 15.0, "y": 15.0, "z": 0.0},
                                "entity_size": "medium"
                            },
                            {
                                "entity_id": "NPC_MARKET_FISHER",
                                "entity_name": "어부 할아버지",
                                "entity_type": "npc",
                                "base_stats": {
                                    "strength": 13,
                                    "dexterity": 11,
                                    "constitution": 14,
                                    "intelligence": 12,
                                    "wisdom": 15,
                                    "charisma": 10
                                },
                                "entity_properties": {
                                    "template_type": "merchant",
                                    "occupation": "fisher",
                                    "personality": "friendly",
                                    "dialogue": "오늘 아침에 잡은 신선한 생선입니다!",
                                    "shop_inventory": ["fish", "seafood"]
                                },
                                "default_position_3d": {"x": 30.0, "y": 20.0, "z": 0.0},
                                "entity_size": "medium"
                            }
                        ],
                        "world_objects": [
                            {
                                "object_id": "OBJ_MARKET_STALL_1",
                                "object_type": "interactive",
                                "object_name": "노점",
                                "description": "다양한 상품이 진열된 노점",
                                "default_position": {"x": 15.0, "y": 12.0},
                                "interaction_type": "shop",
                                "properties": {"shop_type": "general"},
                                "wall_mounted": False,
                                "passable": False,
                                "movable": False,
                                "object_height": 1.2,
                                "object_width": 2.0,
                                "object_depth": 1.5,
                                "object_weight": 50.0
                            }
                        ]
                    }
                ]
            },
            # 7. 제국군 장병 리조트
            {
                "location_id": "LOC_SOLDIER_RESORT",
                "location_name": "제국군 장병 리조트",
                "location_type": "resort",
                "description": "마을 최고의 소년들이 모이는 제국군 장병 리조트. 휴가 나온 군인들이 즐기는 곳이다.",
                "properties": {
                    "clientele": "soldiers",
                                    "atmosphere": "energetic"
                },
                "cells": [
                    {
                        "cell_id": "CELL_RESORT_BAR",
                        "cell_name": "리조트 바",
                        "matrix_width": 20,
                        "matrix_height": 18,
                        "cell_description": "시끌벅적한 바. 군인들이 술을 마시며 이야기를 나누고 있다.",
                        "cell_properties": {
                            "environment": {
                                "temperature": 22.0,
                                "humidity": 50.0,
                                "air_quality": "normal",
                                "visibility": 70.0
                            },
                            "terrain": {
                                "type": "wooden_floor",
                                "elevation": 0.0
                            },
                            "lighting": {
                                "level": "dim",
                                "source": "lantern",
                                "color_temperature": 2500,
                                "flicker": False
                            },
                            "atmosphere": {
                                "ambiance": "lively",
                                "music": "tavern_01",
                                "sound_effects": ["cheering", "glasses"],
                                "background_noise": "loud"
                            }
                        },
                        "characters": [
                            {
                                "entity_id": "NPC_SOLDIER_1",
                                "entity_name": "제국군 병사 마르쿠스",
                                "entity_type": "npc",
                                "base_stats": {
                                    "strength": 15,
                                    "dexterity": 12,
                                    "constitution": 14,
                                    "intelligence": 10,
                                    "wisdom": 11,
                                    "charisma": 13
                                },
                                "entity_properties": {
                                    "template_type": "npc",
                                    "occupation": "soldier",
                                    "personality": "cheerful",
                                    "dialogue": "휴가 나와서 정말 좋아!",
                                    "faction": "제국군"
                                },
                                "default_position_3d": {"x": 10.0, "y": 12.0, "z": 0.0},
                                "entity_size": "medium"
                            },
                            {
                                "entity_id": "NPC_BARMAID",
                                "entity_name": "바텐더 소피아",
                                "entity_type": "npc",
                                "base_stats": {
                                    "strength": 9,
                                    "dexterity": 14,
                                    "constitution": 10,
                                    "intelligence": 12,
                                    "wisdom": 13,
                                    "charisma": 17
                                },
                                "entity_properties": {
                                    "template_type": "merchant",
                                    "occupation": "barmaid",
                                    "personality": "flirtatious",
                                    "dialogue": "또 왔구나! 오늘은 뭐 마실래?",
                                    "shop_inventory": ["beer", "wine", "food"]
                                },
                                "default_position_3d": {"x": 18.0, "y": 5.0, "z": 0.0},
                                "entity_size": "medium"
                            }
                        ],
                        "world_objects": [
                            {
                                "object_id": "OBJ_BAR_COUNTER",
                                "object_type": "interactive",
                                "object_name": "바 카운터",
                                "description": "나무로 만든 바 카운터",
                                "default_position": {"x": 18.0, "y": 3.0},
                                "interaction_type": "shop",
                                "properties": {"shop_type": "bar"},
                                "wall_mounted": False,
                                "passable": False,
                                "movable": False,
                                "object_height": 1.1,
                                "object_width": 4.0,
                                "object_depth": 0.8,
                                "object_weight": 100.0
                            }
                        ]
                    }
                ]
            },
            # 8. 해식 동굴
            {
                "location_id": "LOC_SEA_CAVE",
                "location_name": "해식 동굴",
                "location_type": "cave",
                "description": "오래된 슬픔이 서려있는 해식 동굴. 바다의 파도가 만들어낸 자연의 작품이다.",
                "properties": {
                    "mood": "melancholic",
                    "natural": True
                },
                "cells": [
                    {
                        "cell_id": "CELL_CAVE_ENTRANCE",
                        "cell_name": "동굴 입구",
                        "matrix_width": 20,
                        "matrix_height": 15,
                        "cell_description": "바다로 이어지는 동굴 입구. 파도 소리가 메아리친다.",
                        "cell_properties": {
                            "environment": {
                                "temperature": 18.0,
                                "humidity": 85.0,
                                "air_quality": "fresh",
                                "visibility": 60.0
                            },
                            "terrain": {
                                "type": "stone",
                                "elevation": -2.0,
                                "water_level": 20.0
                            },
                            "lighting": {
                                "level": "dim",
                                "source": "natural",
                                "color_temperature": 4000
                            },
                            "atmosphere": {
                                "ambiance": "mysterious",
                                "music": "cave_01",
                                "sound_effects": ["waves", "echo"],
                                "background_noise": "moderate"
                            }
                        },
                        "characters": [],
                        "world_objects": [
                            {
                                "object_id": "OBJ_CAVE_ROCK_FORMATION",
                                "object_type": "static",
                                "object_name": "바위 형성물",
                                "description": "오랜 세월 파도에 의해 만들어진 바위 형성물",
                                "default_position": {"x": 10.0, "y": 8.0},
                                "interaction_type": "examine",
                                "properties": {"formation_type": "stalactite"},
                                "wall_mounted": True,
                                "passable": True,
                                "movable": False,
                                "object_height": 3.0,
                                "object_width": 1.5,
                                "object_depth": 1.5,
                                "object_weight": 500.0
                            }
                        ]
                    }
                ]
            },
            # 9. 마사지샵
            {
                "location_id": "LOC_MASSAGE_SHOP",
                "location_name": "마사지샵",
                "location_type": "shop",
                "description": "깨끗한 하루를 위한 마사지샵. 휴양객들이 즐겨 찾는 곳이다.",
                "properties": {
                    "service": "massage",
                    "cleanliness": "high"
                },
                "cells": [
                    {
                        "cell_id": "CELL_MASSAGE_ROOM",
                        "cell_name": "마사지실",
                        "matrix_width": 12,
                        "matrix_height": 10,
                        "cell_description": "조용하고 편안한 마사지실. 향초가 타고 있다.",
                        "cell_properties": {
                            "environment": {
                                "temperature": 24.0,
                                "humidity": 50.0,
                                "air_quality": "fresh",
                                "visibility": 40.0
                            },
                            "terrain": {
                                "type": "wooden_floor",
                                "elevation": 0.0
                            },
                            "lighting": {
                                "level": "dim",
                                "source": "candle",
                                "color_temperature": 2000,
                                "flicker": True
                            },
                            "atmosphere": {
                                "ambiance": "peaceful",
                                "music": "spa_01",
                                "sound_effects": ["water_fountain"],
                                "background_noise": "quiet"
                            }
                        },
                        "characters": [
                            {
                                "entity_id": "NPC_MASSAGE_THERAPIST",
                                "entity_name": "마사지사 미나",
                                "entity_type": "npc",
                                "base_stats": {
                                    "strength": 12,
                                    "dexterity": 16,
                                    "constitution": 11,
                                    "intelligence": 13,
                                    "wisdom": 14,
                                    "charisma": 15
                                },
                                "entity_properties": {
                                    "template_type": "merchant",
                                    "occupation": "massage_therapist",
                                    "personality": "calm",
                                    "dialogue": "편안하게 쉬세요. 모든 피로를 풀어드리겠습니다.",
                                    "shop_inventory": ["massage_service"]
                                },
                                "default_position_3d": {"x": 6.0, "y": 5.0, "z": 0.0},
                                "entity_size": "medium"
                            }
                        ],
                        "world_objects": [
                            {
                                "object_id": "OBJ_MASSAGE_TABLE",
                                "object_type": "interactive",
                                "object_name": "마사지 테이블",
                                "description": "편안한 마사지 테이블",
                                "default_position": {"x": 6.0, "y": 7.0},
                                "interaction_type": "rest",
                                "properties": {"rest_quality": "excellent", "service": "massage"},
                                "wall_mounted": False,
                                "passable": False,
                                "movable": False,
                                "object_height": 0.8,
                                "object_width": 2.0,
                                "object_depth": 1.0,
                                "object_weight": 80.0
                            }
                        ]
                    }
                ]
            },
            # 10. 항구
            {
                "location_id": "LOC_HARBOR",
                "location_name": "레크레스타 항구",
                "location_type": "harbor",
                "description": "평범한 비즈니스가 이루어지는 항구. 조르가즈 갱의 활동 무대이기도 하다.",
                "properties": {
                    "business": "normal",
                    "gang_activity": "present"
                },
                "cells": [
                    {
                        "cell_id": "CELL_HARBOR_DOCK",
                        "cell_name": "항구 부두",
                        "matrix_width": 40,
                        "matrix_height": 25,
                        "cell_description": "배들이 정박해 있는 부두. 선원들과 상인들이 분주하게 움직인다.",
                        "cell_properties": {
                            "environment": {
                                "temperature": 22.0,
                                "humidity": 70.0,
                                "air_quality": "fresh",
                                "visibility": 100.0
                            },
                            "terrain": {
                                "type": "stone",
                                "elevation": 0.0,
                                "water_level": 0.0
                            },
                            "lighting": {
                                "level": "bright",
                                "source": "sun",
                                "color_temperature": 5500
                            },
                            "weather": {
                                "type": "clear",
                                "intensity": 0.0,
                                "wind_speed": 5.0,
                                "precipitation": "none"
                            },
                            "atmosphere": {
                                "ambiance": "busy",
                                "music": "harbor_01",
                                "sound_effects": ["waves", "seagulls", "ship_bells"],
                                "background_noise": "loud"
                            }
                        },
                        "characters": [
                            {
                                "entity_id": "NPC_HARBOR_MASTER",
                                "entity_name": "항구 관리인 로버트",
                                "entity_type": "npc",
                                "base_stats": {
                                    "strength": 13,
                                    "dexterity": 11,
                                    "constitution": 12,
                                    "intelligence": 14,
                                    "wisdom": 15,
                                    "charisma": 12
                                },
                                "entity_properties": {
                                    "template_type": "npc",
                                    "occupation": "harbor_master",
                                    "personality": "businesslike",
                                    "dialogue": "부두 사용료는 미리 내셔야 합니다."
                                },
                                "default_position_3d": {"x": 20.0, "y": 5.0, "z": 0.0},
                                "entity_size": "medium"
                            },
                            {
                                "entity_id": "NPC_SHIP_CAPTAIN",
                                "entity_name": "선장 제임스",
                                "entity_type": "npc",
                                "base_stats": {
                                    "strength": 14,
                                    "dexterity": 12,
                                    "constitution": 15,
                                    "intelligence": 13,
                                    "wisdom": 14,
                                    "charisma": 11
                                },
                                "entity_properties": {
                                    "template_type": "quest_giver",
                                    "occupation": "ship_captain",
                                    "personality": "adventurous",
                                    "dialogue": "다음 항구로 가실 분 있나요?",
                                    "available_quests": ["ship_passage"]
                                },
                                "default_position_3d": {"x": 30.0, "y": 15.0, "z": 0.0},
                                "entity_size": "medium"
                            }
                        ],
                        "world_objects": [
                            {
                                "object_id": "OBJ_HARBOR_CRANE",
                                "object_type": "static",
                                "object_name": "항구 크레인",
                                "description": "화물을 옮기는 크레인",
                                "default_position": {"x": 15.0, "y": 10.0},
                                "interaction_type": "none",
                                "properties": {},
                                "wall_mounted": False,
                                "passable": True,
                                "movable": False,
                                "object_height": 8.0,
                                "object_width": 2.0,
                                "object_depth": 2.0,
                                "object_weight": 1000.0
                            }
                        ]
                    }
                ]
            },
            # 11. 요새 유적
            {
                "location_id": "LOC_FORTRESS_RUINS",
                "location_name": "요새 유적",
                "location_type": "ruins",
                "description": "지워진 경고가 새겨진 옛 요새 유적. 과거의 전쟁을 상기시킨다.",
                "properties": {
                    "historical": True,
                    "danger_level": "low"
                },
                "cells": [
                    {
                        "cell_id": "CELL_RUINS_MAIN",
                        "cell_name": "요새 유적 본관",
                        "matrix_width": 30,
                        "matrix_height": 25,
                        "cell_description": "무너진 성벽과 기둥들이 남아있는 유적. 바람에 흔들리는 풀만이 옛 영광을 기억하는 듯하다.",
                        "cell_properties": {
                            "environment": {
                                "temperature": 20.0,
                                "humidity": 55.0,
                                "air_quality": "normal",
                                "visibility": 100.0
                            },
                            "terrain": {
                                "type": "stone",
                                "elevation": 5.0,
                                "water_level": 0.0,
                                "obstacles": [
                                    {"type": "ruined_wall", "position": {"x": 10, "y": 10}},
                                    {"type": "broken_column", "position": {"x": 20, "y": 15}}
                                ]
                            },
                            "lighting": {
                                "level": "bright",
                                "source": "sun",
                                "color_temperature": 5500
                            },
                            "weather": {
                                "type": "clear",
                                "intensity": 0.0,
                                "wind_speed": 4.0,
                                "precipitation": "none"
                            },
                            "atmosphere": {
                                "ambiance": "melancholic",
                                "music": "ruins_01",
                                "sound_effects": ["wind", "distant_birds"],
                                "background_noise": "quiet"
                            },
                            "gameplay": {
                                "spawn_points": [
                                    {"id": "ruins_spawn_1", "position": {"x": 15.0, "y": 12.0, "z": 0.0}, "type": "player"}
                                ],
                                "interaction_zones": [
                                    {"area": {"x": 10, "y": 10, "width": 5, "height": 5}, "type": "examine"}
                                ]
                            }
                        },
                        "characters": [
                            {
                                "entity_id": "NPC_RUINS_HISTORIAN",
                                "entity_name": "역사학자 아르놀드",
                                "entity_type": "npc",
                                "base_stats": {
                                    "strength": 8,
                                    "dexterity": 10,
                                    "constitution": 9,
                                    "intelligence": 17,
                                    "wisdom": 16,
                                    "charisma": 12
                                },
                                "entity_properties": {
                                    "template_type": "quest_giver",
                                    "occupation": "historian",
                                    "personality": "scholarly",
                                    "dialogue": "이 요새는 옛 전쟁의 증인입니다. 많은 이야기가 묻혀있죠.",
                                    "available_quests": ["ruins_research"]
                                },
                                "default_position_3d": {"x": 15.0, "y": 12.0, "z": 0.0},
                                "entity_size": "medium"
                            }
                        ],
                        "world_objects": [
                            {
                                "object_id": "OBJ_RUINS_WALL",
                                "object_type": "static",
                                "object_name": "무너진 성벽",
                                "description": "오랜 세월에 무너진 성벽",
                                "default_position": {"x": 10.0, "y": 10.0},
                                "interaction_type": "examine",
                                "properties": {"inscription": "지워진 경고"},
                                "wall_mounted": False,
                                "passable": False,
                                "movable": False,
                                "object_height": 2.5,
                                "object_width": 5.0,
                                "object_depth": 1.0,
                                "object_weight": 2000.0
                            }
                        ]
                    }
                ]
            },
            # 12. 개인 해변
            {
                "location_id": "LOC_PRIVATE_BEACH",
                "location_name": "개인 해변",
                "location_type": "beach",
                "description": "출입금지인 개인 해변. 부르겐 남작의 전용 해변이다.",
                "properties": {
                    "access": "restricted",
                    "owner": "부르겐 남작"
                },
                "cells": [
                    {
                        "cell_id": "CELL_PRIVATE_BEACH_MAIN",
                        "cell_name": "개인 해변 본해변",
                        "matrix_width": 35,
                        "matrix_height": 25,
                        "cell_description": "아무도 없는 조용한 개인 해변. 출입금지 표지판이 서 있다.",
                        "cell_properties": {
                            "environment": {
                                "temperature": 28.0,
                                "humidity": 70.0,
                                "air_quality": "fresh",
                                "visibility": 100.0
                            },
                            "terrain": {
                                "type": "sand",
                                "elevation": 0.0,
                                "water_level": 0.0
                            },
                            "lighting": {
                                "level": "bright",
                                "source": "sun",
                                "color_temperature": 6000
                            },
                            "weather": {
                                "type": "clear",
                                "intensity": 0.0,
                                "wind_speed": 3.0,
                                "precipitation": "none"
                            },
                            "atmosphere": {
                                "ambiance": "peaceful",
                                "music": "private_beach_01",
                                "sound_effects": ["waves"],
                                "background_noise": "quiet"
                            },
                            "gameplay": {
                                "restricted_areas": [
                                    {"area": {"x": 0, "y": 0, "width": 35, "height": 25}, "reason": "private_property"}
                                ]
                            }
                        },
                        "characters": [
                            {
                                "entity_id": "NPC_BEACH_GUARD_PRIVATE",
                                "entity_name": "해변 경비원",
                                "entity_type": "npc",
                                "base_stats": {
                                    "strength": 16,
                                    "dexterity": 13,
                                    "constitution": 15,
                                    "intelligence": 10,
                                    "wisdom": 12,
                                    "charisma": 9
                                },
                                "entity_properties": {
                                    "template_type": "npc",
                                    "occupation": "guard",
                                    "personality": "strict",
                                    "dialogue": "이곳은 출입금지입니다. 돌아가세요."
                                },
                                "default_position_3d": {"x": 5.0, "y": 5.0, "z": 0.0},
                                "entity_size": "medium"
                            }
                        ],
                        "world_objects": [
                            {
                                "object_id": "OBJ_PRIVATE_BEACH_SIGN",
                                "object_type": "static",
                                "object_name": "출입금지 표지판",
                                "description": "개인 소유지 출입금지 표지판",
                                "default_position": {"x": 3.0, "y": 3.0},
                                "interaction_type": "read",
                                "properties": {"message": "출입금지 - 부르겐 남작 소유지"},
                                "wall_mounted": False,
                                "passable": True,
                                "movable": False,
                                "object_height": 1.5,
                                "object_width": 0.5,
                                "object_depth": 0.1,
                                "object_weight": 10.0
                            }
                        ]
                    }
                ]
            },
            # 13. 귀족들의 별장
            {
                "location_id": "LOC_NOBLE_VILLA",
                "location_name": "귀족들의 별장",
                "location_type": "villa",
                "description": "무슨 일이든 가능해요. 아발룸의 귀족들이 휴양을 즐기는 별장 지역이다.",
                "properties": {
                    "clientele": "nobles",
                    "exclusivity": "high"
                },
                "cells": [
                    {
                        "cell_id": "CELL_VILLA_MAIN",
                        "cell_name": "별장 본관",
                        "matrix_width": 25,
                        "matrix_height": 20,
                        "cell_description": "화려하게 꾸며진 별장 본관. 귀족들이 모여 파티를 즐기고 있다.",
                        "cell_properties": {
                            "environment": {
                                "temperature": 23.0,
                                "humidity": 45.0,
                                "air_quality": "fresh",
                                "visibility": 100.0
                            },
                            "terrain": {
                                "type": "wooden_floor",
                                "elevation": 0.0
                            },
                            "lighting": {
                                "level": "bright",
                                "source": "chandelier",
                                "color_temperature": 3000,
                                "flicker": False
                            },
                            "atmosphere": {
                                "ambiance": "luxurious",
                                "music": "noble_party_01",
                                "sound_effects": ["laughter", "glasses"],
                                "background_noise": "moderate"
                            }
                        },
                        "characters": [
                            {
                                "entity_id": "NPC_NOBLE_LORD",
                                "entity_name": "귀족 영주",
                                "entity_type": "npc",
                                "base_stats": {
                                    "strength": 10,
                                    "dexterity": 11,
                                    "constitution": 10,
                                    "intelligence": 15,
                                    "wisdom": 14,
                                    "charisma": 18
                                },
                                "entity_properties": {
                                    "template_type": "npc",
                                    "occupation": "noble",
                                    "personality": "arrogant",
                                    "dialogue": "여기서는 무엇이든 가능합니다. 돈만 있다면요.",
                                    "faction": "아발룸 귀족"
                                },
                                "default_position_3d": {"x": 12.0, "y": 10.0, "z": 0.0},
                                "entity_size": "medium"
                            }
                        ],
                        "world_objects": [
                            {
                                "object_id": "OBJ_VILLA_PIANO",
                                "object_type": "interactive",
                                "object_name": "그랜드 피아노",
                                "description": "화려한 그랜드 피아노",
                                "default_position": {"x": 20.0, "y": 10.0},
                                "interaction_type": "play",
                                "properties": {"instrument": "piano"},
                                "wall_mounted": False,
                                "passable": False,
                                "movable": False,
                                "object_height": 1.0,
                                "object_width": 1.5,
                                "object_depth": 2.5,
                                "object_weight": 300.0
                            }
                        ]
                    }
                ]
            },
            # 14. 주거지역
            {
                "location_id": "LOC_RESIDENTIAL_AREA",
                "location_name": "주거지역",
                "location_type": "residential",
                "description": "숨죽여 웃다. 전직 모험가들이 은퇴하고 살고 싶어하는 조용한 주거지역이다.",
                "properties": {
                    "atmosphere": "quiet",
                    "residents": "retired_adventurers"
                },
                "cells": [
                    {
                        "cell_id": "CELL_RESIDENTIAL_STREET",
                        "cell_name": "주거지 거리",
                        "matrix_width": 30,
                        "matrix_height": 20,
                        "cell_description": "조용하고 평화로운 주거지 거리. 작은 집들이 줄지어 있다.",
                        "cell_properties": {
                            "environment": {
                                "temperature": 24.0,
                                "humidity": 50.0,
                                "air_quality": "fresh",
                                "visibility": 100.0
                            },
                            "terrain": {
                                "type": "stone",
                                "elevation": 0.0
                            },
                            "lighting": {
                                "level": "bright",
                                "source": "sun",
                                "color_temperature": 5500
                            },
                            "weather": {
                                "type": "clear",
                                "intensity": 0.0,
                                "wind_speed": 2.0,
                                "precipitation": "none"
                            },
                            "atmosphere": {
                                "ambiance": "peaceful",
                                "music": "residential_01",
                                "sound_effects": ["birds", "distant_voices"],
                                "background_noise": "quiet"
                            }
                        },
                        "characters": [
                            {
                                "entity_id": "NPC_RETIRED_ADVENTURER_2",
                                "entity_name": "은퇴한 모험가 엘레나",
                                "entity_type": "npc",
                                "base_stats": {
                                    "strength": 12,
                                    "dexterity": 14,
                                    "constitution": 13,
                                    "intelligence": 13,
                                    "wisdom": 15,
                                    "charisma": 12
                                },
                                "entity_properties": {
                                    "template_type": "quest_giver",
                                    "occupation": "retired_adventurer",
                                    "personality": "wise",
                                    "dialogue": "모험은 그만두고 여기서 평화롭게 살고 있어요. 레크레스타는 정말 살기 좋은 곳이에요.",
                                    "available_quests": ["rekresta_life"]
                                },
                                "default_position_3d": {"x": 15.0, "y": 10.0, "z": 0.0},
                                "entity_size": "medium"
                            }
                        ],
                        "world_objects": [
                            {
                                "object_id": "OBJ_RESIDENTIAL_BENCH",
                                "object_type": "interactive",
                                "object_name": "공원 벤치",
                                "description": "거리에 놓인 편안한 벤치",
                                "default_position": {"x": 20.0, "y": 10.0},
                                "interaction_type": "sit",
                                "properties": {"comfort": "medium"},
                                "wall_mounted": False,
                                "passable": False,
                                "movable": True,
                                "object_height": 0.5,
                                "object_width": 1.5,
                                "object_depth": 0.6,
                                "object_weight": 25.0
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    # Region 생성
    print("레크레스타 생성 시작...")
    result = await factory.create_region_with_children(rekresta_config)
    print(f"생성 완료!")
    print(f"Region ID: {result['region_id']}")
    print(f"Locations: {len(result['location_ids'])}개")
    print(f"Cells: {len(result['cell_ids'])}개")
    print(f"Entities: {len(result['entity_ids'])}개")
    print(f"World Objects: {len(result['object_ids'])}개")
    
    return result


if __name__ == "__main__":
    asyncio.run(create_rekresta())

