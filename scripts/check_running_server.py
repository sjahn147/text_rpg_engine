"""
실행 중인 서버의 라우트 확인
"""
import requests
import json

BASE_URL = "http://localhost:8001"

def check_openapi():
    """OpenAPI 스펙에서 라우트 확인"""
    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        if response.status_code == 200:
            spec = response.json()
            paths = spec.get('paths', {})
            
            interact_paths = {k: v for k, v in paths.items() if 'interact' in k}
            
            print("=== 실행 중인 서버의 라우트 확인 ===\n")
            print(f"총 {len(paths)}개 경로 중 'interact' 관련: {len(interact_paths)}개\n")
            
            if len(interact_paths) == 0:
                print("❌ 'interact' 관련 라우트가 등록되지 않았습니다!")
                print("\n가능한 원인:")
                print("1. 서버가 재시작되지 않았습니다")
                print("2. 다른 서버가 실행 중입니다")
                print("3. 라우터 import 에러로 인해 등록되지 않았습니다")
            else:
                print("✅ 'interact' 관련 라우트:")
                for path, methods in interact_paths.items():
                    method_list = list(methods.keys())
                    print(f"   {method_list} {path}")
                
            return len(interact_paths) > 0
        else:
            print(f"OpenAPI 스펙 조회 실패: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다!")
        print("서버가 실행 중인지 확인하세요.")
        return False
    except Exception as e:
        print(f"❌ 에러: {e}")
        return False

if __name__ == "__main__":
    check_openapi()

