"""
interact/object 엔드포인트 실제 테스트
프론트엔드에서 보내는 값과 동일한 형식으로 테스트
"""
import asyncio
import sys
import os
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

os.chdir(project_root)

from database.connection import DatabaseConnection
import asyncpg

async def get_test_data():
    """테스트에 사용할 실제 데이터 조회"""
    db = DatabaseConnection()
    pool = await db.pool
    
    async with pool.acquire() as conn:
        # 1. 세션 ID 조회 (active_sessions에서)
        session_row = await conn.fetchrow("""
            SELECT session_id
            FROM runtime_data.active_sessions
            WHERE session_state = 'active'
            ORDER BY created_at DESC
            LIMIT 1
        """)
        
        if not session_row:
            # entity_references에서 찾기
            session_row = await conn.fetchrow("""
                SELECT session_id
                FROM reference_layer.entity_references
                WHERE session_id IS NOT NULL
                LIMIT 1
            """)
        
        if not session_row:
            print("❌ 게임 세션이 없습니다. 먼저 게임을 시작하세요.")
            print("   프론트엔드에서 게임을 시작한 후 세션 ID를 확인하세요.")
            return None
        
        session_id = str(session_row['session_id'])
        print(f"✅ 세션 ID: {session_id}")
        
        # 2. 플레이어의 현재 셀 조회
        player_entity = await conn.fetchrow("""
            SELECT es.current_position
            FROM runtime_data.entity_states es
            JOIN reference_layer.entity_references er ON es.runtime_entity_id = er.runtime_entity_id
            WHERE er.entity_type = 'player'
            AND es.current_position->>'runtime_cell_id' IS NOT NULL
            LIMIT 1
        """)
        
        if not player_entity:
            print("❌ 플레이어 엔티티를 찾을 수 없습니다.")
            return None
        
        current_position = player_entity['current_position']
        if isinstance(current_position, str):
            import json
            current_position = json.loads(current_position)
        
        runtime_cell_id = current_position.get('runtime_cell_id')
        if not runtime_cell_id:
            print("❌ 현재 셀을 찾을 수 없습니다.")
            return None
        
        runtime_cell_id = str(runtime_cell_id)
        print(f"✅ 현재 셀 ID: {runtime_cell_id}")
        
        # 3. 현재 셀의 오브젝트 조회
        cell_ref = await conn.fetchrow("""
            SELECT game_cell_id
            FROM reference_layer.cell_references
            WHERE runtime_cell_id = $1
        """, runtime_cell_id)
        
        if not cell_ref:
            print("❌ 셀 참조를 찾을 수 없습니다.")
            return None
        
        game_cell_id = cell_ref['game_cell_id']
        
        # 셀의 오브젝트 조회 (CellManager와 동일한 방식)
        objects = await conn.fetch("""
            SELECT 
                COALESCE(or_ref.runtime_object_id, wo.object_id) as runtime_object_id,
                wo.object_id as game_object_id,
                wo.object_name,
                wo.object_description,
                wo.interaction_type,
                wo.properties
            FROM game_data.world_objects wo
            LEFT JOIN reference_layer.object_references or_ref 
                ON wo.object_id = or_ref.game_object_id 
                AND (or_ref.session_id = $1 OR or_ref.session_id IS NULL)
            WHERE wo.default_cell_id = $2
            LIMIT 5
        """, session_id, game_cell_id)
        
        if not objects:
            print("❌ 현재 셀에 오브젝트가 없습니다.")
            return None
        
        print(f"\n✅ 현재 셀의 오브젝트 ({len(objects)}개):")
        for obj in objects:
            print(f"   - {obj['object_name']} (runtime_object_id: {obj['runtime_object_id']}, game_object_id: {obj['game_object_id']})")
        
        # 첫 번째 오브젝트 선택
        test_object = objects[0]
        
        return {
            'session_id': session_id,
            'object_id': str(test_object['runtime_object_id']),
            'object_name': test_object['object_name'],
            'action_type': 'examine'
        }

async def test_endpoint():
    """엔드포인트 테스트"""
    print("=== interact/object 엔드포인트 테스트 ===\n")
    
    # 테스트 데이터 조회
    test_data = await get_test_data()
    if not test_data:
        return
    
    print(f"\n📤 전송할 데이터:")
    print(f"   session_id: {test_data['session_id']}")
    print(f"   object_id: {test_data['object_id']}")
    print(f"   action_type: {test_data['action_type']}")
    print(f"   object_name: {test_data['object_name']}")
    
    # FastAPI 테스트 클라이언트로 테스트
    from fastapi.testclient import TestClient
    from app.ui.backend.main import app
    
    client = TestClient(app)
    
    print(f"\n📥 엔드포인트 호출: POST /api/gameplay/interact/object")
    
    try:
        response = client.post(
            "/api/gameplay/interact/object",
            json={
                "session_id": test_data['session_id'],
                "object_id": test_data['object_id'],
                "action_type": test_data['action_type']
            }
        )
        
        print(f"\n📊 응답 상태 코드: {response.status_code}")
        print(f"📊 응답 헤더: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("\n✅ 성공!")
            response_data = response.json()
            print(f"\n📥 응답 데이터:")
            print(f"   success: {response_data.get('success')}")
            print(f"   message: {response_data.get('message', '')[:200]}")
            if 'result' in response_data:
                print(f"   result: {response_data['result']}")
        elif response.status_code == 404:
            print("\n❌ 404 Not Found")
            print(f"응답: {response.text}")
        elif response.status_code == 500:
            print("\n❌ 500 Internal Server Error")
            print(f"응답: {response.text[:500]}")
        else:
            print(f"\n⚠️ 예상치 못한 상태 코드: {response.status_code}")
            print(f"응답: {response.text[:500]}")
            
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_endpoint())

