"""
이미 획득한 아이템을 다시 획득 시도하는 테스트 (404가 나와야 함)
"""
import asyncio
import sys
from pathlib import Path
import json
import httpx

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from database.connection import DatabaseConnection

async def test_already_taken():
    """이미 획득한 아이템 재획득 시도 테스트"""
    db = DatabaseConnection()
    pool = await db.pool
    async with pool.acquire() as conn:
        # 가장 최근 세션 찾기
        session = await conn.fetchrow("""
            SELECT session_id FROM runtime_data.active_sessions
            ORDER BY created_at DESC
            LIMIT 1
        """, )
        
        if not session:
            print("❌ 활성 세션이 없습니다.")
            return
        
        session_id = str(session['session_id'])
        print(f"✅ 세션 ID: {session_id}")
        
        # 여행 가방 오브젝트 찾기
        bag_obj = await conn.fetchrow("""
            SELECT 
                wo.object_id as game_object_id,
                or_ref.runtime_object_id
            FROM game_data.world_objects wo
            LEFT JOIN reference_layer.object_references or_ref 
                ON wo.object_id = or_ref.game_object_id 
                AND or_ref.session_id = $1
            WHERE wo.object_id = 'OBJ_INN_BAG_001'
        """, session_id)
        
        if not bag_obj:
            print("❌ 여행 가방 오브젝트를 찾을 수 없습니다.")
            return
        
        runtime_object_id = str(bag_obj['runtime_object_id'])
        print(f"✅ 여행 가방 runtime_object_id: {runtime_object_id}\n")
        
        # 런타임 상태 확인
        runtime_state = await conn.fetchrow("""
            SELECT current_state FROM runtime_data.object_states
            WHERE runtime_object_id = $1
        """, runtime_object_id)
        
        if not runtime_state:
            print("❌ 런타임 상태가 없습니다. 먼저 아이템을 획득하세요.")
            return
        
        state_dict = runtime_state['current_state']
        if isinstance(state_dict, str):
            state_dict = json.loads(state_dict)
        runtime_contents = state_dict.get('contents', [])
        
        print(f"📋 현재 런타임 contents: {runtime_contents}")
        
        if not runtime_contents:
            print("❌ contents가 비어있습니다. 테스트할 수 없습니다.")
            return
        
        # 기본값 확인
        game_obj = await conn.fetchrow("""
            SELECT properties FROM game_data.world_objects
            WHERE object_id = 'OBJ_INN_BAG_001'
        """)
        
        props = game_obj['properties']
        if isinstance(props, str):
            props = json.loads(props)
        default_contents = props.get('contents', [])
        
        print(f"📋 기본 contents: {default_contents}")
        
        # 이미 제거된 아이템 찾기 (기본값에는 있지만 런타임에는 없는 것)
        removed_items = [item for item in default_contents if item not in runtime_contents]
        
        if not removed_items:
            print("❌ 제거된 아이템이 없습니다.")
            return
        
        item_id = removed_items[0]
        print(f"\n✅ 테스트할 item_id (이미 제거됨): {item_id}")
        print(f"   기본값에 있는가? {item_id in default_contents}")
        print(f"   런타임에 있는가? {item_id in runtime_contents}")
        
        # FastAPI 엔드포인트 테스트 (404가 나와야 함)
        request_data = {
            "session_id": session_id,
            "object_id": runtime_object_id,
            "item_id": item_id
        }
        
        print(f"\n📤 요청 데이터:")
        print(json.dumps(request_data, indent=2, ensure_ascii=False))
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "http://localhost:8001/api/gameplay/interact/object/pickup",
                    json=request_data
                )
                
                print(f"\n📥 응답 상태: {response.status_code}")
                
                try:
                    response_data = response.json()
                    print(f"📥 응답 데이터:")
                    print(json.dumps(response_data, indent=2, ensure_ascii=False))
                    
                    if response.status_code == 404:
                        print("\n✅ 예상대로 404 에러가 발생했습니다!")
                        print("   이미 제거된 아이템은 더 이상 획득할 수 없습니다.")
                    elif response.status_code == 200:
                        print("\n❌ 문제: 200 OK가 반환되었습니다!")
                        print("   이미 제거된 아이템을 다시 획득할 수 있습니다. (잘못됨)")
                    else:
                        print(f"\n⚠️  예상치 못한 상태 코드: {response.status_code}")
                except:
                    print(f"📥 응답 본문 (텍스트):")
                    print(response.text)
        except httpx.ConnectError:
            print("\n❌ 백엔드 서버에 연결할 수 없습니다.")
            print("서버가 실행 중인지 확인하세요: http://localhost:8001")
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_already_taken())

