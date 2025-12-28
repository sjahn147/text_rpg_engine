"""
프론트엔드에서 보내는 요청과 동일한 형식으로 테스트
"""
import requests
import json

BASE_URL = "http://localhost:8001"

def test_interact_object(session_id: str, object_id: str, action_type: str = "examine"):
    """
    프론트엔드와 동일한 형식으로 요청 보내기
    
    프론트엔드 코드:
    await this.client.post(`/api/gameplay/interact/object`, {
      session_id: sessionId,
      object_id: objectId,
      action_type: actionType,
    });
    """
    url = f"{BASE_URL}/api/gameplay/interact/object"
    
    payload = {
        "session_id": session_id,
        "object_id": object_id,
        "action_type": action_type
    }
    
    print("=" * 70)
    print("프론트엔드 요청 형식 테스트")
    print("=" * 70)
    print(f"URL: {url}")
    print(f"Method: POST")
    print(f"Payload:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print()
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers={
                'Content-Type': 'application/json'
            },
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            print("✅ 성공!")
            print("Response:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        elif response.status_code == 404:
            print("❌ 404 Not Found")
            print("Response:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            print()
            print("가능한 원인:")
            print("1. 세션이 존재하지 않음")
            print("2. 오브젝트가 존재하지 않음")
            print("3. 엔드포인트가 등록되지 않음 (서버 재시작 필요)")
        elif response.status_code == 500:
            print("⚠️ 500 Internal Server Error")
            print("Response:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"Response ({response.status_code}):")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다!")
        print("서버가 실행 중인지 확인하세요.")
    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 실제 게임에서 사용하는 값들을 여기에 입력하세요
    # 브라우저 콘솔에서 확인한 session_id와 object_id를 사용
    
    print("프론트엔드 요청 형식 테스트")
    print("=" * 70)
    print()
    print("사용법:")
    print("1. 브라우저 콘솔에서 실제 session_id와 object_id 확인")
    print("2. 아래 변수에 값을 입력하고 실행")
    print()
    
    # 예시 값 (실제 값으로 교체 필요)
    SESSION_ID = "your-session-id-here"  # 실제 세션 ID로 교체
    OBJECT_ID = "your-object-id-here"     # 실제 오브젝트 ID로 교체
    ACTION_TYPE = "examine"                # examine, open, light, sit, rest 등
    
    # 값이 예시 값이면 안내 메시지 출력
    if SESSION_ID == "your-session-id-here" or OBJECT_ID == "your-object-id-here":
        print("⚠️  실제 세션 ID와 오브젝트 ID를 입력해주세요.")
        print()
        print("브라우저 콘솔에서 확인하는 방법:")
        print("1. 게임 화면에서 오브젝트를 우클릭")
        print("2. 개발자 도구 콘솔 열기")
        print("3. '[GameView] Interacting with object:' 로그 확인")
        print("   - targetId가 object_id")
        print("   - gameState.session_id가 session_id")
        print()
        print("또는 네트워크 탭에서:")
        print("1. 개발자 도구 > Network 탭")
        print("2. interact/object 요청 클릭")
        print("3. Payload에서 session_id, object_id 확인")
        print()
    else:
        test_interact_object(SESSION_ID, OBJECT_ID, ACTION_TYPE)


