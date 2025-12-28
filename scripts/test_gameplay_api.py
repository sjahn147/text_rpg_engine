"""
게임플레이 API 테스트 스크립트
"""
import asyncio
import sys
import os

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.ui.backend.main import app

def test_api_routes():
    """API 라우트 테스트"""
    client = TestClient(app)
    
    # 모든 라우트 확인
    print("=== 등록된 라우트 확인 ===")
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append({
                'path': route.path,
                'methods': list(route.methods),
                'name': getattr(route, 'name', 'N/A')
            })
    
    # interact 관련 라우트만 필터링
    interact_routes = [r for r in routes if 'interact' in r['path']]
    
    print(f"\n총 {len(routes)}개의 라우트가 등록되어 있습니다.")
    print(f"\n'interact' 관련 라우트 ({len(interact_routes)}개):")
    for route in interact_routes:
        print(f"  {route['methods']} {route['path']} ({route['name']})")
    
    # 특정 엔드포인트 테스트
    print("\n=== 엔드포인트 테스트 ===")
    
    # /api/gameplay/interact/object 테스트
    test_path = "/api/gameplay/interact/object"
    print(f"\n테스트 경로: {test_path}")
    
    # OPTIONS 요청으로 경로 존재 확인
    response = client.options(test_path)
    print(f"OPTIONS {test_path}: {response.status_code}")
    
    # POST 요청 (에러가 나도 경로는 확인됨)
    try:
        response = client.post(
            test_path,
            json={
                "session_id": "test-session",
                "object_id": "test-object",
                "action_type": "examine"
            }
        )
        print(f"POST {test_path}: {response.status_code}")
        if response.status_code == 404:
            print(f"  ❌ 404 에러: 경로를 찾을 수 없습니다.")
        else:
            print(f"  ✅ 경로는 존재합니다 (상태 코드: {response.status_code})")
            if response.status_code != 200:
                print(f"  응답: {response.text[:200]}")
    except Exception as e:
        print(f"  ❌ 에러: {e}")
    
    # /api/gameplay/interact/object/pickup 테스트
    test_path2 = "/api/gameplay/interact/object/pickup"
    print(f"\n테스트 경로: {test_path2}")
    try:
        response = client.post(
            test_path2,
            json={
                "session_id": "test-session",
                "object_id": "test-object",
                "item_id": "test-item"
            }
        )
        print(f"POST {test_path2}: {response.status_code}")
        if response.status_code == 404:
            print(f"  ❌ 404 에러: 경로를 찾을 수 없습니다.")
        else:
            print(f"  ✅ 경로는 존재합니다 (상태 코드: {response.status_code})")
    except Exception as e:
        print(f"  ❌ 에러: {e}")

if __name__ == "__main__":
    test_api_routes()

