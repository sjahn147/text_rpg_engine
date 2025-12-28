"""
pickup_from_object 엔드포인트 테스트 스크립트
실제 프론트엔드에서 보내는 요청을 재현
"""
import asyncio
import sys
from pathlib import Path
import json

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from database.connection import DatabaseConnection

async def test_pickup_request():
    """pickup_from_object 요청 재현"""
    db = DatabaseConnection()
    pool = await db.pool
    async with pool.acquire() as conn:
        # 1. 활성 세션 찾기
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
        
        # 2. 플레이어 엔티티 찾기
        player = await conn.fetchrow("""
            SELECT 
                es.runtime_entity_id,
                es.current_position
            FROM runtime_data.entity_states es
            JOIN reference_layer.entity_references er ON es.runtime_entity_id = er.runtime_entity_id
            WHERE er.entity_type = 'player'
            AND er.session_id = $1
            LIMIT 1
        """, session_id)
        
        if not player:
            print("❌ 플레이어 엔티티를 찾을 수 없습니다.")
            return
        
        print(f"✅ 플레이어 ID: {player['runtime_entity_id']}")
        
        # 3. 현재 셀 ID 추출
        current_position = player['current_position']
        if isinstance(current_position, str):
            current_position = json.loads(current_position)
        current_cell_id = current_position.get('runtime_cell_id')
        
        if not current_cell_id:
            print("❌ 현재 셀을 찾을 수 없습니다.")
            return
        
        print(f"✅ 현재 셀 ID: {current_cell_id}")
        
        # 4. 셀의 오브젝트 찾기
        cell_ref = await conn.fetchrow("""
            SELECT game_cell_id FROM reference_layer.cell_references
            WHERE runtime_cell_id = $1 AND session_id = $2
        """, current_cell_id, session_id)
        
        if not cell_ref:
            print("❌ 셀 참조를 찾을 수 없습니다.")
            return
        
        game_cell_id = cell_ref['game_cell_id']
        print(f"✅ 게임 셀 ID: {game_cell_id}")
        
        # 5. 셀의 오브젝트 조회 (레퍼런스 레이어 포함)
        objects = await conn.fetch("""
            SELECT 
                wo.object_id as game_object_id,
                or_ref.runtime_object_id,
                wo.object_name,
                wo.properties
            FROM game_data.world_objects wo
            LEFT JOIN reference_layer.object_references or_ref 
                ON wo.object_id = or_ref.game_object_id 
                AND or_ref.session_id = $1
            WHERE wo.default_cell_id = $2
        """, session_id, game_cell_id)
        
        if not objects:
            print("❌ 셀에 오브젝트가 없습니다.")
            return
        
        print(f"\n✅ 셀의 오브젝트 ({len(objects)}개):")
        for obj in objects:
            print(f"  - {obj['object_name']} (game: {obj['game_object_id']}, runtime: {obj['runtime_object_id']})")
            props = obj['properties']
            if isinstance(props, str):
                props = json.loads(props)
            contents = props.get('contents', [])
            if contents:
                print(f"    contents: {contents}")
        
        # 6. contents가 있는 오브젝트 찾기
        target_obj = None
        for obj in objects:
            props = obj['properties']
            if isinstance(props, str):
                props = json.loads(props)
            contents = props.get('contents', [])
            if contents:
                target_obj = obj
                break
        
        if not target_obj:
            print("\n❌ contents가 있는 오브젝트가 없습니다.")
            return
        
        print(f"\n✅ 테스트 대상 오브젝트: {target_obj['object_name']}")
        print(f"   game_object_id: {target_obj['game_object_id']}")
        print(f"   runtime_object_id: {target_obj['runtime_object_id']}")
        
        props = target_obj['properties']
        if isinstance(props, str):
            props = json.loads(props)
        contents = props.get('contents', [])
        print(f"   contents: {contents}")
        
        if not contents:
            print("\n❌ contents가 비어있습니다.")
            return
        
        item_id = contents[0]
        print(f"\n✅ 테스트할 item_id: {item_id}")
        
        # 7. FastAPI 엔드포인트 테스트 (HTTP 요청)
        import httpx
        
        # object_id는 runtime_object_id 또는 game_object_id 사용 가능
        object_id = target_obj['runtime_object_id'] or target_obj['game_object_id']
        
        request_data = {
            "session_id": session_id,
            "object_id": str(object_id),
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
                print(f"📥 응답 헤더: {dict(response.headers)}")
                
                try:
                    response_data = response.json()
                    print(f"📥 응답 데이터:")
                    print(json.dumps(response_data, indent=2, ensure_ascii=False))
                except:
                    print(f"📥 응답 본문 (텍스트):")
                    print(response.text)
                
                if response.status_code == 500:
                    print("\n❌ 500 Internal Server Error 발생!")
                    print("백엔드 로그를 확인하세요.")
        except httpx.ConnectError:
            print("\n❌ 백엔드 서버에 연결할 수 없습니다.")
            print("서버가 실행 중인지 확인하세요: http://localhost:8001")
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_pickup_request())

