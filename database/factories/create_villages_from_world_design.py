"""
world_design.md를 기반으로 Factory를 사용하여 15개 이상의 마을(Region) 생성

Region = 영지 (마을 단위)
Location = 영지 안의 건물 단위
Cell = Location 안의 방 단위
"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from database.factories.world_data_factory import WorldDataFactory


async def create_villages():
    """world_design.md 기반으로 15개 이상의 마을 생성"""
    factory = WorldDataFactory()
    
    # Region 설정 리스트 (world_design.md 기반)
    regions_config = [
        # 1. 크랄루소스 (헬라로스)
        {
            "region_id": "REG_HELAROS_KRALUSOS_01",
            "region_name": "크랄루소스",
            "region_type": "village",
            "description": "비밀과 전설로 가득한 마을. 아름다운 풍광과 평화로운 일상 속에 감춰진 그림자",
            "properties": {
                "theme": "비밀과 탐욕",
                "population": 2000,
                "location": "헬라로스"
            },
            "locations": [
                {
                    "location_id": "LOC_KRALUSOS_TAVERN_01",
                    "location_name": "여행자의 선술집",
                    "description": "모험가들이 모이는 선술집",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_TAVERN_MAIN_HALL",
                            "cell_name": "주홀",
                            "description": "선술집의 메인 홀",
                            "matrix_width": 20,
                            "matrix_height": 20,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        },
                        {
                            "cell_id": "CELL_TAVERN_KITCHEN",
                            "cell_name": "주방",
                            "description": "음식을 준비하는 주방",
                            "matrix_width": 10,
                            "matrix_height": 10,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                },
                {
                    "location_id": "LOC_KRALUSOS_MARKET_01",
                    "location_name": "시장",
                    "description": "마을의 중심 시장",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_MARKET_SQUARE",
                            "cell_name": "시장 광장",
                            "description": "상인들이 물건을 파는 광장",
                            "matrix_width": 30,
                            "matrix_height": 30,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                }
            ]
        },
        
        # 2. 레크레스타 (안브레티아)
        {
            "region_id": "REG_ANBRETIA_REKRESSTA_01",
            "region_name": "레크레스타",
            "region_type": "town",
            "description": "해변을 접하고 있는 아름다운 관광지. 부르겐 남작이 다스리는 중소 도시",
            "properties": {
                "theme": "아름다운 것은 거기에 비밀이 있기 때문",
                "population": 5000,
                "location": "안브레티아"
            },
            "locations": [
                {
                    "location_id": "LOC_REKRESSTA_HOTEL_01",
                    "location_name": "레크레스타 호텔",
                    "description": "최고의 서비스를 제공하는 호텔",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_HOTEL_LOBBY",
                            "cell_name": "로비",
                            "description": "호텔의 로비",
                            "matrix_width": 25,
                            "matrix_height": 25,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        },
                        {
                            "cell_id": "CELL_HOTEL_ROOM_01",
                            "cell_name": "객실 1",
                            "description": "호텔 객실",
                            "matrix_width": 15,
                            "matrix_height": 15,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                },
                {
                    "location_id": "LOC_REKRESSTA_BEACH_01",
                    "location_name": "해수욕장",
                    "description": "안브레티아의 보석 같은 해수욕장",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_BEACH_MAIN",
                            "cell_name": "해변",
                            "description": "주요 해변 지역",
                            "matrix_width": 50,
                            "matrix_height": 50,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                }
            ]
        },
        
        # 3. 베카림 (안브레티아)
        {
            "region_id": "REG_ANBRETIA_BEKARIM_01",
            "region_name": "베카림",
            "region_type": "city",
            "description": "미궁의 도시. 모험가들의 천국이자 기회의 땅",
            "properties": {
                "theme": "기회와 모험",
                "population": 15000,
                "location": "안브레티아"
            },
            "locations": [
                {
                    "location_id": "LOC_BEKARIM_DUNGEON_ENTRANCE",
                    "location_name": "미궁 입구",
                    "description": "거대한 지하 미궁으로 통하는 입구",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_DUNGEON_ENTRANCE_HALL",
                            "cell_name": "입구 홀",
                            "description": "미궁 입구의 거대한 홀",
                            "matrix_width": 40,
                            "matrix_height": 40,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                },
                {
                    "location_id": "LOC_BEKARIM_ADVENTURERS_GUILD",
                    "location_name": "모험가 길드",
                    "description": "모험가들이 모이는 길드",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_GUILD_HALL",
                            "cell_name": "길드 홀",
                            "description": "모험가들이 모이는 메인 홀",
                            "matrix_width": 30,
                            "matrix_height": 30,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        },
                        {
                            "cell_id": "CELL_GUILD_OFFICE",
                            "cell_name": "사무실",
                            "description": "길드 업무를 처리하는 사무실",
                            "matrix_width": 15,
                            "matrix_height": 15,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                },
                {
                    "location_id": "LOC_BEKARIM_MARKET",
                    "location_name": "보물의 장터",
                    "description": "모험가들의 전리품이 거래되는 시장",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_MARKET_AREA",
                            "cell_name": "장터",
                            "description": "전리품 거래 장터",
                            "matrix_width": 35,
                            "matrix_height": 35,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                }
            ]
        },
        
        # 4. 이오클라란 (아르보이아)
        {
            "region_id": "REG_ARBOIA_IOKLARAN_01",
            "region_name": "이오클라란",
            "region_type": "port_city",
            "description": "항구 도시. 포이키아 반도로 들어가는 입구이면서 번화한 항구도시",
            "properties": {
                "theme": "바다와 무역",
                "population": 50000,
                "location": "아르보이아"
            },
            "locations": [
                {
                    "location_id": "LOC_IOKLARAN_PORT",
                    "location_name": "붉은 등대",
                    "description": "300년 전 해전의 승리를 기리는 등대",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_LIGHTHOUSE_TOP",
                            "cell_name": "등대 꼭대기",
                            "description": "등대의 최상층",
                            "matrix_width": 10,
                            "matrix_height": 10,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        },
                        {
                            "cell_id": "CELL_LIGHTHOUSE_BASE",
                            "cell_name": "등대 기단",
                            "description": "등대의 기단부",
                            "matrix_width": 15,
                            "matrix_height": 15,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                },
                {
                    "location_id": "LOC_IOKLARAN_TAVERN",
                    "location_name": "고래의 술집",
                    "description": "선원들의 노래와 전설이 흐르는 술집",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_TAVERN_MAIN",
                            "cell_name": "주홀",
                            "description": "술집의 메인 홀",
                            "matrix_width": 25,
                            "matrix_height": 25,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                },
                {
                    "location_id": "LOC_IOKLARAN_SHIPYARD",
                    "location_name": "조선소",
                    "description": "배의 숨결이 느껴지는 창조의 현장",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_SHIPYARD_MAIN",
                            "cell_name": "조선소 작업장",
                            "description": "배를 만드는 작업장",
                            "matrix_width": 40,
                            "matrix_height": 40,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                }
            ]
        },
        
        # 5. 인그로투스 (안브레티아)
        {
            "region_id": "REG_ANBRETIA_INGROTUS_01",
            "region_name": "인그로투스",
            "region_type": "estate",
            "description": "1공주 트리스테사의 휴양지로 쓰였던 왕실 영지. 여학교가 있는 한적한 농촌 마을",
            "properties": {
                "theme": "고상한 분위기와 비밀",
                "population": 500,
                "location": "안브레티아"
            },
            "locations": [
                {
                    "location_id": "LOC_INGROTUS_SCHOOL",
                    "location_name": "인그로투스 여학교",
                    "description": "수도 귀족의 규수들이 모여서 공부하는 여학교",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_SCHOOL_CLASSROOM_01",
                            "cell_name": "교실 1",
                            "description": "학생들이 수업을 받는 교실",
                            "matrix_width": 20,
                            "matrix_height": 20,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        },
                        {
                            "cell_id": "CELL_SCHOOL_DORMITORY_01",
                            "cell_name": "기숙사 방 1",
                            "description": "학생들의 기숙사 방",
                            "matrix_width": 12,
                            "matrix_height": 12,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        },
                        {
                            "cell_id": "CELL_SCHOOL_LIBRARY",
                            "cell_name": "도서관",
                            "description": "지식의 보고이자 비밀의 장소",
                            "matrix_width": 30,
                            "matrix_height": 30,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                },
                {
                    "location_id": "LOC_INGROTUS_LAKE",
                    "location_name": "호수",
                    "description": "학교 부지 안쪽에 있는 작은 호수",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_LAKE_SHORE",
                            "cell_name": "호수 기슭",
                            "description": "학생들이 소풍을 나오는 호수 기슭",
                            "matrix_width": 40,
                            "matrix_height": 40,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                }
            ]
        },
        
        # 6. 키넬레스 (안브레티아)
        {
            "region_id": "REG_ANBRETIA_KINELES_01",
            "region_name": "키넬레스",
            "region_type": "suburb",
            "description": "수도 귀족들이 형식상의 영지를 하사받는 교외 지역. 고급 주택이 대부분",
            "properties": {
                "theme": "권력과 특권",
                "population": 3000,
                "location": "안브레티아"
            },
            "locations": [
                {
                    "location_id": "LOC_KINELES_MANSION_01",
                    "location_name": "귀족 저택 1",
                    "description": "요새 같은 저택. 철통 보안 뒤에 숨겨진 기득권의 성채",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_MANSION_ENTRANCE",
                            "cell_name": "현관",
                            "description": "저택의 현관",
                            "matrix_width": 15,
                            "matrix_height": 15,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        },
                        {
                            "cell_id": "CELL_MANSION_BALLROOM",
                            "cell_name": "연회장",
                            "description": "과시의 미덕을 꽃피우는 사교계의 전쟁터",
                            "matrix_width": 30,
                            "matrix_height": 30,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        },
                        {
                            "cell_id": "CELL_MANSION_STUDY",
                            "cell_name": "서재",
                            "description": "귀족의 서재",
                            "matrix_width": 15,
                            "matrix_height": 15,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                },
                {
                    "location_id": "LOC_KINELES_GARDEN",
                    "location_name": "장미의 정원",
                    "description": "아름다움으로 치장한 권력의 카니발",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_GARDEN_MAIN",
                            "cell_name": "정원",
                            "description": "화려한 정원",
                            "matrix_width": 35,
                            "matrix_height": 35,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                }
            ]
        },
        
        # 7. 히에라로스 (소키아)
        {
            "region_id": "REG_SOKIA_HIERAROS_01",
            "region_name": "히에라로스",
            "region_type": "military_town",
            "description": "포이키아로 들어가는 입구에 자리잡은 도시. 기사단의 주둔지로서 발달한 산간 마을",
            "properties": {
                "theme": "자연과 마법의 조화",
                "population": 8000,
                "location": "소키아"
            },
            "locations": [
                {
                    "location_id": "LOC_HIERAROS_KNIGHT_HQ",
                    "location_name": "기사단 본부",
                    "description": "웅장한 대리석 기둥과 화려한 스테인드글라스 창문이 인상적인 건물",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_KNIGHT_HALL",
                            "cell_name": "기사단 홀",
                            "description": "기사들이 모이는 메인 홀",
                            "matrix_width": 35,
                            "matrix_height": 35,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        },
                        {
                            "cell_id": "CELL_KNIGHT_TRAINING",
                            "cell_name": "훈련장",
                            "description": "기사들의 훈련장",
                            "matrix_width": 40,
                            "matrix_height": 40,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                },
                {
                    "location_id": "LOC_HIERAROS_MAGE_TOWER",
                    "location_name": "마법의 탑",
                    "description": "마법사단이 거처를 정한 탑",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_TOWER_LIBRARY",
                            "cell_name": "마법 도서관",
                            "description": "고대 마법서의 비밀이 잠든 곳",
                            "matrix_width": 25,
                            "matrix_height": 25,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        },
                        {
                            "cell_id": "CELL_TOWER_LAB",
                            "cell_name": "연구실",
                            "description": "마법 연구를 하는 연구실",
                            "matrix_width": 20,
                            "matrix_height": 20,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                }
            ]
        },
        
        # 8. 카푸스고프 (아르보이아)
        {
            "region_id": "REG_ARBOIA_KAPUSGOF_01",
            "region_name": "카푸스고프",
            "region_type": "coastal_town",
            "description": "그라로로스 섬과 마주보고 있는 연안 도시",
            "properties": {
                "theme": "바다와 섬",
                "population": 6000,
                "location": "아르보이아"
            },
            "locations": [
                {
                    "location_id": "LOC_KAPUSGOF_HARBOR",
                    "location_name": "항구",
                    "description": "그라로로스 섬으로 가는 배가 출발하는 항구",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_HARBOR_DOCK",
                            "cell_name": "부두",
                            "description": "배가 정박하는 부두",
                            "matrix_width": 30,
                            "matrix_height": 30,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                },
                {
                    "location_id": "LOC_KAPUSGOF_INN",
                    "location_name": "여관",
                    "description": "여행자들이 머무는 여관",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_INN_COMMON_ROOM",
                            "cell_name": "공용실",
                            "description": "여관의 공용실",
                            "matrix_width": 20,
                            "matrix_height": 20,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                }
            ]
        },
        
        # 9. 코르시움 (안브레티아)
        {
            "region_id": "REG_ANBRETIA_CORSIUM_01",
            "region_name": "코르시움",
            "region_type": "village",
            "description": "안브레티아의 작은 마을",
            "properties": {
                "theme": "평화로운 마을",
                "population": 1500,
                "location": "안브레티아"
            },
            "locations": [
                {
                    "location_id": "LOC_CORSIUM_TOWN_HALL",
                    "location_name": "마을회관",
                    "description": "마을의 행정을 처리하는 회관",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_TOWN_HALL_MAIN",
                            "cell_name": "회의실",
                            "description": "마을 회의가 열리는 회의실",
                            "matrix_width": 20,
                            "matrix_height": 20,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                }
            ]
        },
        
        # 10. 에아노멜 (요르그)
        {
            "region_id": "REG_YORG_EAANOMEL_01",
            "region_name": "에아노멜",
            "region_type": "village",
            "description": "요르그 지방의 작은 마을. 촌장이 다스리는 평화로운 마을",
            "properties": {
                "theme": "전통과 평화",
                "population": 800,
                "location": "요르그"
            },
            "locations": [
                {
                    "location_id": "LOC_EAANOMEL_FARM_01",
                    "location_name": "농장 1",
                    "description": "마을의 농장",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_FARM_FIELD",
                            "cell_name": "농지",
                            "description": "작물을 기르는 농지",
                            "matrix_width": 30,
                            "matrix_height": 30,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                }
            ]
        },
        
        # 11. 위드리고스 (요르그)
        {
            "region_id": "REG_YORG_WIDRIGOS_01",
            "region_name": "위드리고스",
            "region_type": "city",
            "description": "고등 교양 교육의 중심지. 학문의 도시",
            "properties": {
                "theme": "학문과 지식",
                "population": 25000,
                "location": "요르그"
            },
            "locations": [
                {
                    "location_id": "LOC_WIDRIGOS_UNIVERSITY",
                    "location_name": "위드리고스 대학",
                    "description": "고등 교양 교육의 중심지",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_UNIVERSITY_LECTURE_HALL",
                            "cell_name": "강의실",
                            "description": "학생들이 강의를 듣는 강의실",
                            "matrix_width": 25,
                            "matrix_height": 25,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        },
                        {
                            "cell_id": "CELL_UNIVERSITY_LIBRARY",
                            "cell_name": "도서관",
                            "description": "방대한 서적이 있는 도서관",
                            "matrix_width": 40,
                            "matrix_height": 40,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                }
            ]
        },
        
        # 12. 오그로돌론 (요르그)
        {
            "region_id": "REG_YORG_OGRODOLON_01",
            "region_name": "오그로돌론",
            "region_type": "elven_city",
            "description": "하이 말레니어드가 모여 사는 요정 도시",
            "properties": {
                "theme": "요정의 도시",
                "population": 12000,
                "location": "요르그"
            },
            "locations": [
                {
                    "location_id": "LOC_OGRODOLON_PALACE",
                    "location_name": "요정 궁전",
                    "description": "하이 말레니어드의 궁전",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_PALACE_THRONE_ROOM",
                            "cell_name": "왕좌의 방",
                            "description": "요정왕의 왕좌가 있는 방",
                            "matrix_width": 30,
                            "matrix_height": 30,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                }
            ]
        },
        
        # 13. 요트문드 (레제톤)
        {
            "region_id": "REG_REZETON_YOTMUND_01",
            "region_name": "요트문드",
            "region_type": "capital",
            "description": "레제톤 왕성이 있는 전통적인 수도. 불을 피우는 자 우지레이그와 이델슨 그레프로리드 대공이 다스림",
            "properties": {
                "theme": "전통과 권력",
                "population": 80000,
                "location": "레제톤"
            },
            "locations": [
                {
                    "location_id": "LOC_YOTMUND_PALACE",
                    "location_name": "레제톤 왕궁",
                    "description": "그레프로리드 대공의 왕궁",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_YOTMUND_PALACE_THRONE_ROOM",
                            "cell_name": "왕좌의 방",
                            "description": "대공의 왕좌가 있는 방",
                            "matrix_width": 40,
                            "matrix_height": 40,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        },
                        {
                            "cell_id": "CELL_YOTMUND_PALACE_COURTYARD",
                            "cell_name": "궁정",
                            "description": "왕궁의 넓은 궁정",
                            "matrix_width": 50,
                            "matrix_height": 50,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                },
                {
                    "location_id": "LOC_YOTMUND_DRAGON_LAIR",
                    "location_name": "용의 둥지",
                    "description": "불을 피우는 자 우지레이그의 둥지",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_YOTMUND_DRAGON_LAIR_MAIN",
                            "cell_name": "용의 둥지",
                            "description": "우지레이그가 거주하는 거대한 동굴",
                            "matrix_width": 60,
                            "matrix_height": 60,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                }
            ]
        },
        
        # 14. 스트레데얀 (레제톤)
        {
            "region_id": "REG_REZETON_STREDEYAN_01",
            "region_name": "스트레데얀",
            "region_type": "industrial_city",
            "description": "북부의 신흥 공업 중심도시. 심술쟁이 짐보르와 에버울프 백작이 다스림",
            "properties": {
                "theme": "산업과 용",
                "population": 45000,
                "location": "레제톤"
            },
            "locations": [
                {
                    "location_id": "LOC_STREDEYAN_FACTORY_01",
                    "location_name": "공장 1",
                    "description": "산업 도시의 공장",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_FACTORY_WORKSHOP",
                            "cell_name": "작업장",
                            "description": "공장의 메인 작업장",
                            "matrix_width": 40,
                            "matrix_height": 40,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                },
                {
                    "location_id": "LOC_STREDEYAN_DRAGON_LAIR",
                    "location_name": "심술쟁이 짐보르의 둥지",
                    "description": "어두운 비늘과 빛나는 붉은 눈을 가진 거대한 드래곤의 둥지",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_STREDEYAN_DRAGON_LAIR_MAIN",
                            "cell_name": "용의 둥지",
                            "description": "심술쟁이 짐보르가 거주하는 동굴",
                            "matrix_width": 50,
                            "matrix_height": 50,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                }
            ]
        },
        
        # 15. 그렐레보그 (레제톤)
        {
            "region_id": "REG_REZETON_GRELLEBOG_01",
            "region_name": "그렐레보그",
            "region_type": "religious_estate",
            "description": "비쩍 마른 비에톨로이그와 쉴더 백작이 다스리는 영지. 폐쇄적인 종교 공동체",
            "properties": {
                "theme": "종교와 통제",
                "population": 10000,
                "location": "레제톤"
            },
            "locations": [
                {
                    "location_id": "LOC_GRELLEBOG_TEMPLE",
                    "location_name": "종교 사원",
                    "description": "종교 공동체의 중심 사원",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_TEMPLE_SANCTUARY",
                            "cell_name": "성소",
                            "description": "종교 의식이 열리는 성소",
                            "matrix_width": 30,
                            "matrix_height": 30,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        },
                        {
                            "cell_id": "CELL_TEMPLE_PRAYER_ROOM",
                            "cell_name": "기도실",
                            "description": "신도들이 기도하는 방",
                            "matrix_width": 20,
                            "matrix_height": 20,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                },
                {
                    "location_id": "LOC_GRELLEBOG_DRAGON_LAIR",
                    "location_name": "비에톨로이그의 둥지",
                    "description": "비쩍 마른 용 비에톨로이그의 둥지",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_GRELLEBOG_DRAGON_LAIR_MAIN",
                            "cell_name": "용의 둥지",
                            "description": "비에톨로이그가 거주하는 동굴",
                            "matrix_width": 45,
                            "matrix_height": 45,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                }
            ]
        },
        
        # 16. 아이아문트 (레제톤)
        {
            "region_id": "REG_REZETON_AIAMUNT_01",
            "region_name": "아이아문트",
            "region_type": "fortress_city",
            "description": "레제톤 남단에 위치하며 누한과 국경을 접하고 있는 천혜의 요새 도시. 보호자 에르고드와 비셔 변경백이 다스림",
            "properties": {
                "theme": "요새와 방어",
                "population": 35000,
                "location": "레제톤"
            },
            "locations": [
                {
                    "location_id": "LOC_AIAMUNT_FORTRESS",
                    "location_name": "요새",
                    "description": "천혜의 요새",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_FORTRESS_WALLS",
                            "cell_name": "성벽",
                            "description": "요새의 방어 성벽",
                            "matrix_width": 50,
                            "matrix_height": 50,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        },
                        {
                            "cell_id": "CELL_FORTRESS_KEEP",
                            "cell_name": "성채",
                            "description": "요새의 중심 성채",
                            "matrix_width": 35,
                            "matrix_height": 35,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                },
                {
                    "location_id": "LOC_AIAMUNT_DRAGON_LAIR",
                    "location_name": "에르고드의 둥지",
                    "description": "보호자 에르고드의 둥지",
                    "properties": {},
                    "cells": [
                        {
                            "cell_id": "CELL_AIAMUNT_DRAGON_LAIR_MAIN",
                            "cell_name": "용의 둥지",
                            "description": "에르고드가 거주하는 동굴",
                            "matrix_width": 50,
                            "matrix_height": 50,
                            "properties": {},
                            "characters": [],
                            "world_objects": []
                        }
                    ]
                }
            ]
        }
    ]
    
    print(f"총 {len(regions_config)}개의 마을(Region)을 생성합니다...")
    
    results = []
    for i, region_config in enumerate(regions_config, 1):
        try:
            print(f"\n[{i}/{len(regions_config)}] {region_config['region_name']} 생성 중...")
            result = await factory.create_region_with_children(region_config)
            results.append({
                "region_name": region_config["region_name"],
                "result": result
            })
            print(f"  ✓ Region: {result['region_id']}")
            print(f"  ✓ Locations: {len(result['location_ids'])}개")
            print(f"  ✓ Cells: {len(result['cell_ids'])}개")
        except Exception as e:
            print(f"  ✗ 오류 발생: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n\n생성 완료!")
    print(f"총 {len(results)}개의 마을이 성공적으로 생성되었습니다.")
    
    return results


if __name__ == "__main__":
    asyncio.run(create_villages())

