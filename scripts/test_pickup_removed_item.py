"""
이미 제거된 아이템을 다시 획득 시도하는 테스트 (200 OK + success: false 반환 확인)
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

async def test_removed_item():
    """이미 제거된 아이템 재획득 시도 테스트"""
    db = DatabaseConnection()
    pool = await db.pool
    async with pool.acquire() as conn:
        # 가장 최근 세션 찾기
        session = await conn.fetchrow("""
            SELECT session_id FROM runtime_data.active_sessions
            ORDER BY created_at DESC
            LIMIT 1
        """)
        
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
        
        # 런타임 상태 확인
        runtime_state = await conn.fetchrow("""
            SELECT current_state FROM runtime_data.object_states
            WHERE runtime_object_id = $1
        """, runtime_object_id)
        
        if runtime_state:
            state_dict = runtime_state['current_state']
            if isinstance(state_dict, str):
                state_dict = json.loads(state_dict)
            runtime_contents = state_dict.get('contents', [])
            print(f"📋 런타임 contents: {runtime_contents}")
            
            # 이미 제거된 아이템 찾기
            removed_items = [item for item in default_contents if item not in runtime_contents]
            
            if not removed_items:
                print("\n❌ 제거된 아이템이 없습니다. 먼저 아이템을 획득하세요.")
                # 먼저 아이템을 획득
                if default_contents:
                    item_id = default_contents[0]
                    print(f"\n📤 먼저 아이템 획득: {item_id}")
                    request_data = {
                        "session_id": session_id,
                        "object_id": runtime_object_id,
                        "item_id": item_id
                    }
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        response = await client.post(
                            "http://localhost:8001/api/gameplay/interact/object/pickup",
                            json=request_data
                        )
                        if response.status_code == 200:
                            print(f"✅ 아이템 획득 성공")
                            # 다시 런타임 상태 확인
                            runtime_state = await conn.fetchrow("""
                                SELECT current_state FROM runtime_data.object_states
                                WHERE runtime_object_id = $1
                            """, runtime_object_id)
                            if runtime_state:
                                state_dict = runtime_state['current_state']
                                if isinstance(state_dict, str):
                                    state_dict = json.loads(state_dict)
                                runtime_contents = state_dict.get('contents', [])
                                removed_items = [item for item in default_contents if item not in runtime_contents]
            else:
                item_id = removed_items[0]
        else:
            # 런타임 상태가 없으면 먼저 아이템을 획득
            if not default_contents:
                print("❌ 기본 contents가 비어있습니다.")
                return
            item_id = default_contents[0]
            print(f"\n📤 먼저 아이템 획득: {item_id}")
            request_data = {
                "session_id": session_id,
                "object_id": runtime_object_id,
                "item_id": item_id
            }
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "http://localhost:8001/api/gameplay/interact/object/pickup",
                    json=request_data
                )
                if response.status_code == 200:
                    print(f"✅ 아이템 획득 성공")
                    # 다시 런타임 상태 확인
                    runtime_state = await conn.fetchrow("""
                        SELECT current_state FROM runtime_data.object_states
                        WHERE runtime_object_id = $1
                    """, runtime_object_id)
                    if runtime_state:
                        state_dict = runtime_state['current_state']
                        if isinstance(state_dict, str):
                            state_dict = json.loads(state_dict)
                        runtime_contents = state_dict.get('contents', [])
                        removed_items = [item for item in default_contents if item not in runtime_contents]
                        if removed_items:
                            item_id = removed_items[0]
                        else:
                            print("❌ 제거된 아이템이 없습니다.")
                            return
        
        if not item_id:
            print("❌ 테스트할 아이템이 없습니다.")
            return
        
        print(f"\n✅ 테스트할 item_id (이미 제거됨): {item_id}")
        print(f"   기본값에 있는가? {item_id in default_contents}")
        if runtime_state:
            state_dict = runtime_state['current_state']
            if isinstance(state_dict, str):
                state_dict = json.loads(state_dict)
            runtime_contents = state_dict.get('contents', [])
            print(f"   런타임에 있는가? {item_id in runtime_contents}")
        
        # FastAPI 엔드포인트 테스트 (200 OK + success: false 반환 확인)
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
                    
                    if response.status_code == 200:
                        if response_data.get('success') == False:
                            print("\n✅ 예상대로 200 OK + success: false가 반환되었습니다!")
                            print(f"   메시지: {response_data.get('message')}")
                            print("   게임에서 사용자 친화적인 메시지가 표시됩니다.")
                        elif response_data.get('success') == True:
                            print("\n❌ 문제: success: true가 반환되었습니다!")
                            print("   이미 제거된 아이템을 다시 획득할 수 있습니다. (잘못됨)")
                        else:
                            print(f"\n⚠️  success 필드가 없습니다: {response_data}")
                    else:
                        print(f"\n❌ 문제: 200 OK가 아닌 {response.status_code}가 반환되었습니다!")
                        print("   게임에서 에러로 처리될 수 있습니다.")
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
    asyncio.run(test_removed_item())

