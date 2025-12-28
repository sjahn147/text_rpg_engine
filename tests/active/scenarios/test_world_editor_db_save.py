"""
월드 에디터 DB 저장 테스트
- PinEditor에서 입력한 값들이 DB에 올바르게 저장되는지 확인
"""
import pytest
import pytest_asyncio
from typing import Dict, Any
import json

from database.connection import DatabaseConnection
from common.utils.logger import logger


@pytest_asyncio.fixture
async def db_connection():
    """데이터베이스 연결 픽스처"""
    db = DatabaseConnection()
    await db.initialize()
    yield db
    await db.close()


@pytest_asyncio.fixture
async def test_region(db_connection):
    """테스트용 지역 생성"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        region_id = "REG_TEST_001"
        await conn.execute("""
            INSERT INTO game_data.world_regions
            (region_id, region_name, region_description, region_type, region_properties)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (region_id) DO UPDATE
            SET region_name = EXCLUDED.region_name,
                region_description = EXCLUDED.region_description,
                region_type = EXCLUDED.region_type,
                region_properties = EXCLUDED.region_properties
        """, region_id, "테스트 지역", "테스트 설명", "forest", json.dumps({}))
        
        yield region_id
        
        # 정리
        await conn.execute("DELETE FROM game_data.world_regions WHERE region_id = $1", region_id)


@pytest.mark.asyncio
async def test_region_properties_save_complete_data(db_connection, test_region):
    """지역 properties에 모든 데이터가 올바르게 저장되는지 테스트"""
    pool = await db_connection.pool
    region_id = test_region
    
    # PinEditor에서 저장하는 형태의 데이터
    properties = {
        "dnd_stats": {
            "climate": "temperate",
            "danger_level": 3,
            "recommended_level": {
                "min": 1,
                "max": 10
            },
            "bgm": "peaceful_01",
            "ambient_effects": ["birds", "wind"]
        },
        "dnd_structured_info": {
            "name": "테스트 지역",
            "description": "테스트 설명",
            "type": "forest",
            "demographics": {
                "population": 1000,
                "races": {
                    "human": 600,
                    "elf": 300,
                    "dwarf": 100
                },
                "classes": {
                    "warrior": 400,
                    "mage": 200,
                    "rogue": 400
                }
            },
            "economy": {
                "primary_industry": "목재",
                "trade_goods": ["나무", "과일", "허브"],
                "gold_value": 5000
            },
            "government": {
                "type": "democracy",
                "leader": "테스트 지도자",
                "laws": ["법률 1", "법률 2", "법률 3"]
            },
            "culture": {
                "religion": ["자연신", "수호신"],
                "customs": ["축제 1", "축제 2"],
                "festivals": ["봄 축제", "가을 축제"]
            },
            "lore": {
                "history": "이 지역은 오래전부터 존재해왔습니다.",
                "legends": ["전설 1", "전설 2"],
                "secrets": ["비밀 1"]
            },
            "npcs": [],
            "quests": [],
            "shops": []
        },
        "detail_sections": [
            {
                "id": "section1",
                "type": "text",
                "title": "외관",
                "content": "이 지역은 아름다운 숲으로 둘러싸여 있습니다."
            },
            {
                "id": "section2",
                "type": "list",
                "title": "주요 장소",
                "items": ["장소 1", "장소 2", "장소 3"]
            }
        ]
    }
    
    # DB에 저장
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE game_data.world_regions
            SET region_properties = $1
            WHERE region_id = $2
        """, json.dumps(properties), region_id)
    
    # DB에서 조회하여 검증
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT region_properties
            FROM game_data.world_regions
            WHERE region_id = $1
        """, region_id)
        
        assert row is not None
        saved_properties = json.loads(row['region_properties']) if isinstance(row['region_properties'], str) else row['region_properties']
        
        # dnd_stats 검증
        assert "dnd_stats" in saved_properties
        assert saved_properties["dnd_stats"]["climate"] == "temperate"
        assert saved_properties["dnd_stats"]["danger_level"] == 3
        assert saved_properties["dnd_stats"]["recommended_level"]["min"] == 1
        assert saved_properties["dnd_stats"]["recommended_level"]["max"] == 10
        assert saved_properties["dnd_stats"]["bgm"] == "peaceful_01"
        assert saved_properties["dnd_stats"]["ambient_effects"] == ["birds", "wind"]
        
        # dnd_structured_info 검증
        assert "dnd_structured_info" in saved_properties
        structured_info = saved_properties["dnd_structured_info"]
        assert structured_info["demographics"]["population"] == 1000
        assert structured_info["demographics"]["races"]["human"] == 600
        assert structured_info["economy"]["primary_industry"] == "목재"
        assert structured_info["economy"]["trade_goods"] == ["나무", "과일", "허브"]
        assert structured_info["government"]["type"] == "democracy"
        assert structured_info["government"]["leader"] == "테스트 지도자"
        assert len(structured_info["government"]["laws"]) == 3
        assert structured_info["lore"]["history"] == "이 지역은 오래전부터 존재해왔습니다."
        
        # detail_sections 검증
        assert "detail_sections" in saved_properties
        assert len(saved_properties["detail_sections"]) == 2
        assert saved_properties["detail_sections"][0]["type"] == "text"
        assert saved_properties["detail_sections"][0]["title"] == "외관"
        assert saved_properties["detail_sections"][1]["type"] == "list"
        assert len(saved_properties["detail_sections"][1]["items"]) == 3
        
        logger.info("✅ 모든 데이터가 올바르게 저장되었습니다.")


@pytest.mark.asyncio
async def test_region_properties_partial_update(db_connection, test_region):
    """부분 업데이트 테스트 - 기존 properties를 유지하면서 일부만 업데이트"""
    pool = await db_connection.pool
    region_id = test_region
    
    # 기존 properties 설정
    initial_properties = {
        "existing_field": "기존 값",
        "dnd_stats": {
            "climate": "temperate",
            "danger_level": 1
        }
    }
    
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE game_data.world_regions
            SET region_properties = $1
            WHERE region_id = $2
        """, json.dumps(initial_properties), region_id)
    
    # 부분 업데이트 (PinEditor의 handleSaveAll처럼)
    updated_properties = {
        **initial_properties,
        "dnd_stats": {
            "climate": "temperate",
            "danger_level": 3,
            "recommended_level": {
                "min": 1,
                "max": 10
            },
            "bgm": "peaceful_01",
            "ambient_effects": ["birds", "wind"]
        }
    }
    
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE game_data.world_regions
            SET region_properties = $1
            WHERE region_id = $2
        """, json.dumps(updated_properties), region_id)
    
    # 검증
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT region_properties
            FROM game_data.world_regions
            WHERE region_id = $1
        """, region_id)
        
        saved_properties = json.loads(row['region_properties']) if isinstance(row['region_properties'], str) else row['region_properties']
        
        # 기존 필드 유지 확인
        assert saved_properties["existing_field"] == "기존 값"
        
        # 업데이트된 필드 확인
        assert saved_properties["dnd_stats"]["danger_level"] == 3
        assert saved_properties["dnd_stats"]["bgm"] == "peaceful_01"
        
        logger.info("✅ 부분 업데이트가 올바르게 작동합니다.")


@pytest.mark.asyncio
async def test_location_properties_save(db_connection):
    """Location properties 저장 테스트"""
    pool = await db_connection.pool
    
    # 테스트용 지역 생성
    region_id = "REG_TEST_LOC_001"
    location_id = "LOC_TEST_001"
    
    try:
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO game_data.world_regions
                (region_id, region_name, region_description, region_type)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (region_id) DO NOTHING
            """, region_id, "테스트 지역", "설명", "forest")
            
            await conn.execute("""
                INSERT INTO game_data.world_locations
                (location_id, region_id, location_name, location_description, location_type, location_properties)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (location_id) DO UPDATE
                SET location_name = EXCLUDED.location_name,
                    location_properties = EXCLUDED.location_properties
            """, location_id, region_id, "테스트 위치", "설명", "town", json.dumps({}))
        
        # Location properties 저장
        properties = {
            "dnd_stats": {
                "climate": "temperate",
                "danger_level": 2,
                "recommended_level": {"min": 1, "max": 5},
                "bgm": "town_01",
                "ambient_effects": ["people", "market"]
            },
            "dnd_structured_info": {
                "economy": {
                    "primary_industry": "상업",
                    "trade_goods": ["식료품", "직물"],
                    "gold_value": 10000
                }
            }
        }
        
        async with pool.acquire() as conn:
            await conn.execute("""
                UPDATE game_data.world_locations
                SET location_properties = $1
                WHERE location_id = $2
            """, json.dumps(properties), location_id)
        
        # 검증
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT location_properties
                FROM game_data.world_locations
                WHERE location_id = $1
            """, location_id)
            
            saved_properties = json.loads(row['location_properties']) if isinstance(row['location_properties'], str) else row['location_properties']
            
            assert saved_properties["dnd_stats"]["danger_level"] == 2
            assert saved_properties["dnd_structured_info"]["economy"]["primary_industry"] == "상업"
            
            logger.info("✅ Location properties가 올바르게 저장되었습니다.")
    
    finally:
        # 정리
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM game_data.world_locations WHERE location_id = $1", location_id)
            await conn.execute("DELETE FROM game_data.world_regions WHERE region_id = $1", region_id)

