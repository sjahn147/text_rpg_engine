"""
WorldDataFactory 단위 테스트
"""
import pytest
import pytest_asyncio
import asyncio
from pathlib import Path
import sys
import tempfile
import os

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from database.connection import DatabaseConnection
from database.factories.world_data_factory import WorldDataFactory


@pytest_asyncio.fixture
async def db_connection():
    """데이터베이스 연결 픽스처"""
    db = DatabaseConnection()
    pool = await db.pool
    yield pool
    await db.close()


@pytest_asyncio.fixture
async def factory():
    """WorldDataFactory 픽스처"""
    return WorldDataFactory()


@pytest.mark.asyncio
async def test_create_region_with_children(db_connection, factory):
    """Region과 하위 엔티티 일괄 생성 테스트"""
    import uuid
    test_id = uuid.uuid4().hex[:8]
    
    region_config = {
        "region_id": f"TEST_REG_{test_id}",
        "region_name": f"Test Region {test_id}",
        "region_type": "empire",
        "description": "A test region",
        "properties": {"climate": "temperate"},
        "locations": [
            {
                "location_id": f"TEST_LOC_{test_id}",
                "location_name": "Test Location",
                "description": "A test location",
                "properties": {"type": "city"},
                "cells": [
                    {
                        "cell_id": f"TEST_CELL_{test_id}",
                        "cell_name": "Test Cell",
                        "description": "A test cell",
                        "matrix_width": 20,
                        "matrix_height": 20,
                        "properties": {"terrain": "indoor"},
                        "characters": [
                            {
                                "entity_id": f"TEST_NPC_{test_id}",
                                "entity_name": "Test NPC",
                                "entity_type": "npc",
                                "base_stats": {"hp": 100, "mp": 50},
                                "entity_properties": {"personality": "friendly"},                                                                             
                                "entity_size": "medium"
                            }
                        ],
                        "world_objects": [
                            {
                                "object_id": f"TEST_OBJ_{test_id}",
                                "object_type": "interactive",
                                "object_name": "Test Chest",
                                "properties": {"material": "wood"}
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    try:
        # Region과 하위 엔티티 생성
        result = await factory.create_region_with_children(region_config)
        
        # 결과 검증
        assert result["region_id"] == f"TEST_REG_{test_id}"
        assert len(result["location_ids"]) == 1
        assert len(result["cell_ids"]) == 1
        assert len(result["entity_ids"]) == 1
        assert len(result["object_ids"]) == 1
        
        # 데이터베이스에서 확인
        async with db_connection.acquire() as conn:
            # Region 확인
            region = await conn.fetchrow("""
                SELECT region_id, region_name, region_type
                FROM game_data.world_regions
                WHERE region_id = $1
            """, result["region_id"])
            assert region is not None
            assert region["region_name"] == f"Test Region {test_id}"
            
            # Location 확인
            location = await conn.fetchrow("""
                SELECT location_id, location_name, region_id
                FROM game_data.world_locations
                WHERE location_id = $1
            """, result["location_ids"][0])
            assert location is not None
            assert location["region_id"] == result["region_id"]
            
            # Cell 확인
            cell = await conn.fetchrow("""
                SELECT cell_id, cell_name, location_id
                FROM game_data.world_cells
                WHERE cell_id = $1
            """, result["cell_ids"][0])
            assert cell is not None
            assert cell["location_id"] == result["location_ids"][0]
            
            # Entity 확인
            entity = await conn.fetchrow("""
                SELECT entity_id, entity_name, entity_size
                FROM game_data.entities
                WHERE entity_id = $1
            """, result["entity_ids"][0])
            assert entity is not None
            assert entity["entity_name"] == "Test NPC"
            assert entity["entity_size"] == "medium"
            
            # World Object 확인
            obj = await conn.fetchrow("""
                SELECT object_id, object_name, default_cell_id
                FROM game_data.world_objects
                WHERE object_id = $1
            """, result["object_ids"][0])
            assert obj is not None
            assert obj["object_name"] == "Test Chest"
            assert obj["default_cell_id"] == result["cell_ids"][0]
    
    finally:
        # 테스트 데이터 정리 (외래키 제약조건 고려하여 역순으로 삭제)        
        async with db_connection.acquire() as conn:
            # 참조 테이블 먼저 삭제
            await conn.execute(f"""
                DELETE FROM reference_layer.entity_references
                WHERE game_entity_id LIKE 'TEST_%{test_id}'
            """)
            await conn.execute(f"""
                DELETE FROM reference_layer.cell_references
                WHERE game_cell_id LIKE 'TEST_%{test_id}'
            """)
            await conn.execute(f"DELETE FROM game_data.world_objects WHERE object_id LIKE 'TEST_%{test_id}'")                                                           
            await conn.execute(f"DELETE FROM game_data.entities WHERE entity_id LIKE 'TEST_%{test_id}'")                                                                
            await conn.execute(f"DELETE FROM game_data.world_cells WHERE cell_id LIKE 'TEST_%{test_id}'")
            await conn.execute(f"DELETE FROM game_data.world_locations WHERE location_id LIKE 'TEST_%{test_id}'")
            await conn.execute(f"DELETE FROM game_data.world_regions WHERE region_id LIKE 'TEST_%{test_id}'")


# Note: world_design.md 파서는 비정형 데이터이므로 나중에 별도로 데이터를 만들어서 넣을 예정입니다.
# 파서 관련 테스트는 제거되었습니다.


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

