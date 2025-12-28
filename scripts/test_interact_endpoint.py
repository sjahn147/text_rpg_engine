"""
interact/object 엔드포인트 직접 테스트
"""
import requests
import json

BASE_URL = "http://localhost:8001"

def test_interact_object():
    """interact/object 엔드포인트 테스트"""
    url = f"{BASE_URL}/api/gameplay/interact/object"
    
    print(f"테스트 URL: {url}")
    print(f"요청 데이터: {{'session_id': 'test', 'object_id': 'test', 'action_type': 'examine'}}")
    
    try:
        response = requests.post(
            url,
            json={
                "session_id": "00000000-0000-0000-0000-000000000000",
                "object_id": "test-object-id",
                "action_type": "examine"
            },
            timeout=5
        )
        
        print(f"\n응답 상태 코드: {response.status_code}")
        print(f"응답 헤더: {dict(response.headers)}")
        
        if response.status_code == 404:
            print("\n❌ 404 Not Found - 엔드포인트가 등록되지 않았습니다!")
            print("\n가능한 원인:")
            print("1. 서버가 재시작되지 않았습니다")
            print("2. 라우터가 제대로 등록되지 않았습니다")
            print("3. 다른 서버가 실행 중입니다")
        elif response.status_code == 500:
            print(f"\n✅ 엔드포인트는 존재합니다 (500 에러는 정상 - 테스트 데이터 문제)")
            print(f"응답: {response.text[:300]}")
        else:
            print(f"\n응답: {response.text[:300]}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ 서버에 연결할 수 없습니다!")
        print("서버가 실행 중인지 확인하세요: python app/ui/backend/run_server.py")
    except Exception as e:
        print(f"\n❌ 에러: {e}")

if __name__ == "__main__":
    test_interact_object()

