"""
Effect Carriers API 테스트
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.world_editor.main import app


@pytest.mark.asyncio
async def test_create_effect_carrier():
    """Effect Carrier 생성 테스트"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as client:
        response = await client.post("/api/effect-carriers", json={
            "name": "테스트 축복",
            "carrier_type": "blessing",
            "effect_json": {
                "strength_mod": 10,
                "duration": 3600,
                "description": "힘이 10 증가합니다"
            },
            "constraints_json": {
                "requires_prayer": True,
                "cooldown": 86400
            },
            "source_entity_id": None,
            "tags": ["divine", "buff", "temporary"]
        })
        
        assert response.status_code == 200 or response.status_code == 201
        data = response.json()
        assert data["name"] == "테스트 축복"
        assert data["carrier_type"] == "blessing"
        assert "effect_id" in data


@pytest.mark.asyncio
async def test_get_effect_carrier():
    """Effect Carrier 조회 테스트"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as client:
        # 먼저 생성
        create_response = await client.post("/api/effect-carriers", json={
            "name": "테스트 조회",
            "carrier_type": "buff",
            "effect_json": {"hp_mod": 20},
            "constraints_json": {},
            "tags": []
        })
        assert create_response.status_code == 200 or create_response.status_code == 201
        effect_id = create_response.json()["effect_id"]
        
        # 조회
        response = await client.get(f"/api/effect-carriers/{effect_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["effect_id"] == effect_id
        assert data["name"] == "테스트 조회"


@pytest.mark.asyncio
async def test_get_all_effect_carriers():
    """모든 Effect Carrier 조회 테스트"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as client:
        response = await client.get("/api/effect-carriers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_effect_carriers_by_type():
    """타입별 Effect Carrier 조회 테스트"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as client:
        # 먼저 생성
        await client.post("/api/effect-carriers", json={
            "name": "타입 테스트",
            "carrier_type": "skill",
            "effect_json": {"damage": 50},
            "constraints_json": {},
            "tags": []
        })
        
        # 타입별 조회
        response = await client.get("/api/effect-carriers/type/skill")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert all(carrier["carrier_type"] == "skill" for carrier in data)


@pytest.mark.asyncio
async def test_get_effect_carriers_with_filters():
    """필터링된 Effect Carrier 조회 테스트"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as client:
        # 먼저 생성
        await client.post("/api/effect-carriers", json={
            "name": "필터 테스트",
            "carrier_type": "buff",
            "effect_json": {"hp_mod": 30},
            "constraints_json": {},
            "tags": ["test", "filter"]
        })
        
        # 필터링 조회
        response = await client.get("/api/effect-carriers?carrier_type=buff&tags=test")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert all(carrier["carrier_type"] == "buff" for carrier in data)


@pytest.mark.asyncio
async def test_update_effect_carrier():
    """Effect Carrier 업데이트 테스트"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as client:
        # 먼저 생성
        create_response = await client.post("/api/effect-carriers", json={
            "name": "업데이트 전",
            "carrier_type": "buff",
            "effect_json": {"hp_mod": 10},
            "constraints_json": {},
            "tags": []
        })
        assert create_response.status_code == 200 or create_response.status_code == 201
        effect_id = create_response.json()["effect_id"]
        
        # 업데이트
        response = await client.put(f"/api/effect-carriers/{effect_id}", json={
            "name": "업데이트 후"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "업데이트 후"


@pytest.mark.asyncio
async def test_delete_effect_carrier():
    """Effect Carrier 삭제 테스트"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as client:
        # 먼저 생성
        create_response = await client.post("/api/effect-carriers", json={
            "name": "삭제 테스트",
            "carrier_type": "buff",
            "effect_json": {"hp_mod": 10},
            "constraints_json": {},
            "tags": []
        })
        assert create_response.status_code == 200 or create_response.status_code == 201
        effect_id = create_response.json()["effect_id"]
        
        # 삭제
        response = await client.delete(f"/api/effect-carriers/{effect_id}")
        assert response.status_code == 200
        
        # 삭제 확인
        response = await client.get(f"/api/effect-carriers/{effect_id}")
        assert response.status_code == 404

