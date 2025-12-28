"""
CellManager.get_cell_contents()가 런타임 상태를 반영하는지 테스트
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
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from app.managers.entity_manager import EntityManager
from app.managers.cell_manager import CellManager

async def test_cell_contents():
    """CellManager.get_cell_contents() 테스트"""
    db = DatabaseConnection()
    game_data_repo = GameDataRepository(db)
    runtime_data_repo = RuntimeDataRepository(db)
    reference_layer_repo = ReferenceLayerRepository(db)
    entity_manager = EntityManager(db, game_data_repo, runtime_data_repo, reference_layer_repo)
    
    cell_manager = CellManager(
        db_connection=db,
        game_data_repo=game_data_repo,
        runtime_data_repo=runtime_data_repo,
        reference_layer_repo=reference_layer_repo,
        entity_manager=entity_manager
    )
    
    # 활성 세션 찾기
    pool = await db.pool
    async with pool.acquire() as conn:
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
            SELECT es.current_position
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
        
        print(f"✅ 현재 셀 ID: {current_cell_id}\n")
        
        # CellManager.get_cell_contents() 호출
        cell_contents = await cell_manager.get_cell_contents(current_cell_id)
        
        print("📋 CellManager.get_cell_contents() 결과:")
        print(f"  오브젝트 개수: {len(cell_contents.get('objects', []))}\n")
        
        # 책상 오브젝트 찾기
        desk_obj = None
        for obj in cell_contents.get('objects', []):
            if obj.get('game_object_id') == 'OBJ_INN_DESK_001':
                desk_obj = obj
                break
        
        if not desk_obj:
            print("❌ 책상 오브젝트를 찾을 수 없습니다.")
            return
        
        print("📋 책상 오브젝트 정보:")
        print(f"  game_object_id: {desk_obj.get('game_object_id')}")
        print(f"  runtime_object_id: {desk_obj.get('runtime_object_id')}")
        props = desk_obj.get('properties', {})
        contents = props.get('contents', [])
        print(f"  properties.contents: {contents}")
        print(f"  타입: {type(contents)}")
        
        # 런타임 상태 직접 확인
        runtime_state = await conn.fetchrow("""
            SELECT current_state FROM runtime_data.object_states
            WHERE runtime_object_id = $1
        """, desk_obj.get('runtime_object_id'))
        
        if runtime_state:
            state_dict = runtime_state['current_state']
            if isinstance(state_dict, str):
                state_dict = json.loads(state_dict)
            runtime_contents = state_dict.get('contents', [])
            print(f"\n📋 런타임 상태 직접 조회:")
            print(f"  runtime_data.object_states.contents: {runtime_contents}")
            
            if contents == runtime_contents:
                print("\n✅ CellManager가 런타임 상태를 올바르게 반영합니다!")
            else:
                print("\n❌ CellManager가 런타임 상태를 반영하지 않습니다!")
                print(f"   CellManager: {contents}")
                print(f"   런타임 상태: {runtime_contents}")
        else:
            print("\n📋 런타임 상태 없음 (기본값 사용)")

if __name__ == "__main__":
    asyncio.run(test_cell_contents())

