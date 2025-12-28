"""
pickup_from_object 404 에러 디버깅
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

async def debug_pickup():
    """pickup_from_object 404 에러 디버깅"""
    db = DatabaseConnection()
    pool = await db.pool
    async with pool.acquire() as conn:
        # 테스트 데이터
        session_id = "58183261-93d1-4f83-a91d-9121e88b3eff"
        object_id = "fa420cd1-262a-48d5-87d7-ffa9118bd734"  # runtime_object_id
        item_id = "ITEM_PAPER_BLANK_001"
        
        print(f"🔍 디버깅 정보:")
        print(f"  session_id: {session_id}")
        print(f"  object_id (runtime): {object_id}")
        print(f"  item_id: {item_id}\n")
        
        # 1. object_references에서 game_object_id 찾기
        object_ref = await conn.fetchrow("""
            SELECT game_object_id, runtime_object_id 
            FROM reference_layer.object_references
            WHERE runtime_object_id = $1 AND session_id = $2
        """, object_id, session_id)
        
        if not object_ref:
            print("❌ object_references에서 찾을 수 없습니다.")
            return
        
        game_object_id = object_ref['game_object_id']
        print(f"✅ game_object_id: {game_object_id}")
        
        # 2. game_data.world_objects에서 기본 properties 확인
        game_object = await conn.fetchrow("""
            SELECT properties FROM game_data.world_objects
            WHERE object_id = $1
        """, game_object_id)
        
        if not game_object:
            print("❌ game_data.world_objects에서 찾을 수 없습니다.")
            return
        
        properties = game_object['properties']
        if isinstance(properties, str):
            properties = json.loads(properties)
        
        default_contents = properties.get('contents', [])
        print(f"✅ game_data 기본 contents: {default_contents}")
        print(f"   item_id가 있는가? {item_id in default_contents}\n")
        
        # 3. runtime_data.object_states 확인
        runtime_state = await conn.fetchrow("""
            SELECT current_state FROM runtime_data.object_states
            WHERE runtime_object_id = $1
        """, object_id)
        
        if runtime_state:
            state_dict = runtime_state['current_state']
            if isinstance(state_dict, str):
                state_dict = json.loads(state_dict)
            
            runtime_contents = state_dict.get('contents', [])
            print(f"✅ runtime_data.object_states contents: {runtime_contents}")
            print(f"   item_id가 있는가? {item_id in runtime_contents}\n")
            
            # 최종 contents 결정
            contents = runtime_contents if runtime_contents else default_contents
        else:
            print("ℹ️  runtime_data.object_states 없음 (기본값 사용)")
            contents = default_contents
        
        print(f"📋 최종 contents: {contents}")
        print(f"   item_id가 있는가? {item_id in contents}")
        
        if item_id not in contents:
            print(f"\n❌ 문제 발견: contents에 {item_id}가 없습니다!")
            print(f"   contents 타입: {type(contents)}")
            print(f"   contents 값: {contents}")

if __name__ == "__main__":
    asyncio.run(debug_pickup())

