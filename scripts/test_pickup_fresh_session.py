"""
새로운 세션에서 아이템 획득 테스트 (런타임 상태가 없는 경우)
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

async def test_fresh_pickup():
    """새로운 세션에서 아이템 획득 테스트"""
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
        
        # 플레이어의 현재 셀 찾기
        player = await conn.fetchrow("""
            SELECT 
                es.runtime_entity_id,
                es.current_position
            FROM runtime_data.entity_states es
            JOIN reference_layer.entity_references er ON es.runtime_entity_id = er.runtime_entity_id
            WHERE er.entity_type = 'player' AND er.session_id = $1
            LIMIT 1
        """, session_id)
        
        if not player:
            print("❌ 플레이어를 찾을 수 없습니다.")
            return
        
        current_position = player['current_position']
        if isinstance(current_position, str):
            current_position = json.loads(current_position)
        current_cell_id = current_position.get('runtime_cell_id')
        
        if not current_cell_id:
            print("❌ 현재 셀을 찾을 수 없습니다.")
            return
        
        print(f"✅ 현재 셀 ID: {current_cell_id}")
        
        # 셀의 게임 셀 ID 찾기
        cell_ref = await conn.fetchrow("""
            SELECT game_cell_id FROM reference_layer.cell_references
            WHERE runtime_cell_id = $1 AND session_id = $2
        """, current_cell_id, session_id)
        
        if not cell_ref:
            print("❌ 셀 참조를 찾을 수 없습니다.")
            return
        
        game_cell_id = cell_ref['game_cell_id']
        print(f"✅ 게임 셀 ID: {game_cell_id}\n")
        
        # 여행 가방 오브젝트 찾기 (아직 아이템이 모두 있어야 함)
        bag_obj = await conn.fetchrow("""
            SELECT 
                wo.object_id as game_object_id,
                or_ref.runtime_object_id,
                wo.properties
            FROM game_data.world_objects wo
            LEFT JOIN reference_layer.object_references or_ref 
                ON wo.object_id = or_ref.game_object_id 
                AND or_ref.session_id = $1
            WHERE wo.default_cell_id = $2
            AND wo.object_id = 'OBJ_INN_BAG_001'
        """, session_id, game_cell_id)
        
        if not bag_obj:
            print("❌ 여행 가방 오브젝트를 찾을 수 없습니다.")
            return
        
        runtime_object_id = str(bag_obj['runtime_object_id'])
        print(f"✅ 여행 가방:")
        print(f"   game_object_id: {bag_obj['game_object_id']}")
        print(f"   runtime_object_id: {runtime_object_id}")
        
        # 기본 properties 확인
        props = bag_obj['properties']
        if isinstance(props, str):
            props = json.loads(props)
        default_contents = props.get('contents', [])
        print(f"   기본 contents: {default_contents}")
        
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
            print(f"   런타임 contents: {runtime_contents}")
        else:
            print(f"   런타임 상태: 없음 (기본값 사용)")
        
        if not default_contents:
            print("\n❌ 기본 contents가 비어있습니다.")
            return
        
        item_id = default_contents[0]
        print(f"\n✅ 테스트할 item_id: {item_id}")
        
        # FastAPI 엔드포인트 테스트
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
                        print("\n✅ 성공!")
                        
                        # 획득 후 런타임 상태 확인
                        runtime_state_after = await conn.fetchrow("""
                            SELECT current_state FROM runtime_data.object_states
                            WHERE runtime_object_id = $1
                        """, runtime_object_id)
                        
                        if runtime_state_after:
                            state_dict_after = runtime_state_after['current_state']
                            if isinstance(state_dict_after, str):
                                state_dict_after = json.loads(state_dict_after)
                            runtime_contents_after = state_dict_after.get('contents', [])
                            print(f"\n📋 획득 후 런타임 상태:")
                            print(f"   contents: {runtime_contents_after}")
                            print(f"   item_id가 제거되었는가? {item_id not in runtime_contents_after}")
                            
                            if item_id not in runtime_contents_after:
                                print("✅ 런타임 상태가 올바르게 업데이트되었습니다!")
                            else:
                                print("❌ 런타임 상태가 업데이트되지 않았습니다!")
                    else:
                        print(f"\n❌ 실패: {response_data.get('detail', 'Unknown error')}")
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
    asyncio.run(test_fresh_pickup())

