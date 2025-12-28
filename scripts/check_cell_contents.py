"""
셀의 오브젝트와 엔티티 확인 스크립트
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
from app.core.game_session import GameSession

async def check_cell_contents():
    db = DatabaseConnection()
    await db.initialize()
    pool = await db.pool
    
    async with pool.acquire() as conn:
        # 1. CELL_INN_ROOM_001의 game_cell_id 확인
        cell_data = await conn.fetchrow(
            """
            SELECT cell_id, cell_name, cell_description
            FROM game_data.world_cells
            WHERE cell_id = 'CELL_INN_ROOM_001'
            """
        )
        
        if not cell_data:
            print("❌ CELL_INN_ROOM_001을 찾을 수 없습니다.")
            return
        
        print(f"✅ 셀 정보: {cell_data['cell_id']} - {cell_data['cell_name']}")
        
        # 2. 해당 셀의 runtime_cell_id 확인
        runtime_cell = await conn.fetchrow(
            """
            SELECT runtime_cell_id, game_cell_id, cell_type
            FROM reference_layer.cell_references
            WHERE game_cell_id = 'CELL_INN_ROOM_001'
            LIMIT 1
            """
        )
        
        if not runtime_cell:
            print("❌ 런타임 셀 인스턴스를 찾을 수 없습니다.")
            return
        
        runtime_cell_id = runtime_cell['runtime_cell_id']
        print(f"✅ 런타임 셀 ID: {runtime_cell_id}")
        
        # 3. 해당 셀의 오브젝트 확인
        objects = await conn.fetch(
            """
            SELECT 
                or_ref.runtime_object_id,
                or_ref.game_object_id,
                or_ref.object_type,
                wo.object_name,
                wo.object_description,
                wo.default_position,
                wo.properties
            FROM reference_layer.object_references or_ref
            JOIN game_data.world_objects wo ON or_ref.game_object_id = wo.object_id
            WHERE or_ref.runtime_cell_id = $1
            """,
            runtime_cell_id
        )
        
        print(f"\n📦 오브젝트 개수: {len(objects)}")
        for obj in objects:
            position = json.loads(obj['default_position']) if isinstance(obj['default_position'], str) else obj['default_position']
            properties = json.loads(obj['properties']) if isinstance(obj['properties'], str) else obj['properties']
            contents = properties.get('contents', []) if properties else []
            print(f"  - {obj['object_name']} ({obj['game_object_id']})")
            print(f"    위치: {position}")
            print(f"    contents: {contents}")
        
        # 4. 해당 셀의 엔티티 확인
        entities = await conn.fetch(
            """
            SELECT 
                er.runtime_entity_id,
                er.game_entity_id,
                er.entity_type,
                e.entity_name,
                e.entity_description,
                es.current_position
            FROM reference_layer.entity_references er
            JOIN game_data.entities e ON er.game_entity_id = e.entity_id
            LEFT JOIN runtime_data.entity_states es ON er.runtime_entity_id = es.runtime_entity_id
            WHERE es.current_position->>'runtime_cell_id' = $1
            """,
            runtime_cell_id
        )
        
        print(f"\n👥 엔티티 개수: {len(entities)}")
        for entity in entities:
            current_position = json.loads(entity['current_position']) if isinstance(entity['current_position'], str) else entity['current_position']
            print(f"  - {entity['entity_name']} ({entity['game_entity_id']})")
            print(f"    타입: {entity['entity_type']}")
            print(f"    위치: {current_position}")
        
        # 5. CellManager를 통한 셀 내용 조회 테스트
        print("\n🔍 CellManager.get_cell_contents() 테스트:")
        from database.repositories.game_data import GameDataRepository
        from database.repositories.runtime_data import RuntimeDataRepository
        from database.repositories.reference_layer import ReferenceLayerRepository
        from app.managers.entity_manager import EntityManager
        from app.managers.cell_manager import CellManager
        
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
        
        cell_contents = await cell_manager.get_cell_contents(runtime_cell_id)
        print(f"  - 오브젝트: {len(cell_contents.get('objects', []))}개")
        print(f"  - 엔티티: {len(cell_contents.get('entities', []))}개")
        
        if cell_contents.get('objects'):
            print("\n  오브젝트 상세:")
            for obj in cell_contents['objects']:
                print(f"    - {obj.get('object_name', 'Unknown')} ({obj.get('runtime_object_id', 'N/A')})")
        
        if cell_contents.get('entities'):
            print("\n  엔티티 상세:")
            for entity in cell_contents['entities']:
                print(f"    - {entity.get('entity_name', 'Unknown')} ({entity.get('runtime_entity_id', 'N/A')})")
    
    await db.close()

if __name__ == "__main__":
    asyncio.run(check_cell_contents())

