"""
World Objects API 테스트
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.world_editor.main import app


@pytest.mark.asyncio
async def test_create_world_object():
    """World Object 생성 테스트"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as client:
        response = await client.post("/api/world-objects", json={
            "object_id": "OBJ_TEST_CHEST_001",
            "object_type": "interactive",
            "object_name": "테스트 보물 상자",
            "object_description": "테스트용 보물 상자",
            "default_cell_id": None,
            "default_position": {"x": 5, "y": 3},
            "interaction_type": "openable",
            "possible_states": {
                "closed": {"locked": False},
                "open": {"empty": False}
            },
            "properties": {
                "loot_table": ["ITEM_GOLD_001"],
                "lock_difficulty": 15
            }
        })
        
        assert response.status_code == 200 or response.status_code == 201
        data = response.json()
        assert data["object_id"] == "OBJ_TEST_CHEST_001"
        assert data["object_type"] == "interactive"
        assert data["object_name"] == "테스트 보물 상자"


@pytest.mark.asyncio
async def test_get_world_object():
    """World Object 조회 테스트"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as client:
        # 먼저 생성
        await client.post("/api/world-objects", json={
            "object_id": "OBJ_TEST_GET_001",
            "object_type": "static",
            "object_name": "테스트 오브젝트",
            "default_position": {},
            "possible_states": {},
            "properties": {}
        })
        
        # 조회
        response = await client.get("/api/world-objects/OBJ_TEST_GET_001")
        assert response.status_code == 200
        data = response.json()
        assert data["object_id"] == "OBJ_TEST_GET_001"
        assert data["object_type"] == "static"


@pytest.mark.asyncio
async def test_get_all_world_objects():
    """모든 World Object 조회 테스트"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as client:
        response = await client.get("/api/world-objects")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_update_world_object():
    """World Object 업데이트 테스트"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as client:
        # 먼저 생성
        await client.post("/api/world-objects", json={
            "object_id": "OBJ_TEST_UPDATE_001",
            "object_type": "interactive",
            "object_name": "업데이트 전",
            "default_position": {},
            "possible_states": {},
            "properties": {}
        })
        
        # 업데이트
        response = await client.put("/api/world-objects/OBJ_TEST_UPDATE_001", json={
            "object_name": "업데이트 후"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["object_name"] == "업데이트 후"


@pytest.mark.asyncio
async def test_delete_world_object():
    """World Object 삭제 테스트"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as client:
        # 먼저 생성
        await client.post("/api/world-objects", json={
            "object_id": "OBJ_TEST_DELETE_001",
            "object_type": "static",
            "object_name": "삭제 테스트",
            "default_position": {},
            "possible_states": {},
            "properties": {}
        })
        
        # 삭제
        response = await client.delete("/api/world-objects/OBJ_TEST_DELETE_001")
        assert response.status_code == 200
        
        # 삭제 확인
        response = await client.get("/api/world-objects/OBJ_TEST_DELETE_001")
        assert response.status_code == 404

