"""
실제 실행 중인 서버의 API 엔드포인트 확인
"""
import requests
import json

BASE_URL = "http://localhost:8001"

def check_endpoint(method, path, data=None):
    """엔드포인트 확인"""
    try:
        url = f"{BASE_URL}{path}"
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data or {}, timeout=5)
        else:
            response = requests.request(method, url, json=data or {}, timeout=5)
        
        return {
            "status": response.status_code,
            "exists": response.status_code != 404,
            "message": response.text[:200] if response.status_code != 200 else "OK"
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "CONNECTION_ERROR",
            "exists": False,
            "message": "서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요."
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "exists": False,
            "message": str(e)
        }

def main():
    print("=== API 엔드포인트 확인 ===\n")
    
    # 헬스 체크
    print("1. 헬스 체크:")
    result = check_endpoint("GET", "/health")
    print(f"   GET /health: {result['status']} - {result['message']}\n")
    
    if result['status'] == "CONNECTION_ERROR":
        print("❌ 서버가 실행 중이지 않습니다!")
        print("   서버를 시작하려면: python app/ui/backend/run_server.py")
        return
    
    # 게임플레이 엔드포인트 확인
    endpoints = [
        ("POST", "/api/gameplay/interact/object", {
            "session_id": "00000000-0000-0000-0000-000000000000",
            "object_id": "test",
            "action_type": "examine"
        }),
        ("POST", "/api/gameplay/interact/object/pickup", {
            "session_id": "00000000-0000-0000-0000-000000000000",
            "object_id": "test",
            "item_id": "test"
        }),
        ("GET", "/api/gameplay/actions/00000000-0000-0000-0000-000000000000"),
    ]
    
    print("2. 게임플레이 엔드포인트:")
    for method, path, *data in endpoints:
        result = check_endpoint(method, path, data[0] if data else None)
        status_icon = "✅" if result['exists'] else "❌"
        print(f"   {status_icon} {method} {path}: {result['status']}")
        if not result['exists'] and result['status'] == 404:
            print(f"      ❌ 404 Not Found - 경로가 등록되지 않았습니다!")
        elif result['status'] != 404 and result['status'] != 200:
            print(f"      ⚠️  경로는 존재하지만 에러 발생: {result['message'][:100]}")
        print()

if __name__ == "__main__":
    main()

