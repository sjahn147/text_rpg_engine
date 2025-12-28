"""
MVP v2 최종 데이터베이스 생성 스크립트
"""
import asyncio
import asyncpg

async def create_mvp_v2_database():
    """MVP v2 최종 스키마 생성"""
    try:
        # 데이터베이스 연결
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='2696Sjbj!',
            database='rpg_engine'
        )
        
        print("🚀 MVP v2 최종 스키마 생성 중...")
        
        # MVP v2 최종 스키마 SQL 파일 읽기
        with open('database/mvp_schema.sql', 'r', encoding='utf-8') as f:
            mvp_schema_sql = f.read()
        
        # SQL 실행
        await conn.execute(mvp_schema_sql)
        
        print("✅ MVP v2 최종 스키마 생성 완료")
        
        # 생성된 테이블 확인
        print("\n📊 생성된 테이블 확인:")
        
        # game_data 스키마 테이블
        game_data_tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'game_data'
            ORDER BY table_name
        """)
        print("📋 game_data 스키마:")
        for table in game_data_tables:
            print(f"  - {table['table_name']}")
        
        # reference_layer 스키마 테이블
        reference_tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'reference_layer'
            ORDER BY table_name
        """)
        print("\n📋 reference_layer 스키마:")
        for table in reference_tables:
            print(f"  - {table['table_name']}")
        
        # runtime_data 스키마 테이블
        runtime_tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'runtime_data'
            ORDER BY table_name
        """)
        print("\n📋 runtime_data 스키마:")
        for table in runtime_tables:
            print(f"  - {table['table_name']}")
        
        # simulation_data 스키마 테이블
        simulation_tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'simulation_data'
            ORDER BY table_name
        """)
        print("\n📋 simulation_data 스키마:")
        for table in simulation_tables:
            print(f"  - {table['table_name']}")
        
        # 샘플 데이터 확인
        print("\n📈 샘플 데이터 확인:")
        sample_data = await conn.fetch("""
            SELECT 
                (SELECT COUNT(*) FROM game_data.world_regions) as regions,
                (SELECT COUNT(*) FROM game_data.world_locations) as locations,
                (SELECT COUNT(*) FROM game_data.world_cells) as cells,
                (SELECT COUNT(*) FROM game_data.entities) as entities,
                (SELECT COUNT(*) FROM game_data.world_objects) as objects,
                (SELECT COUNT(*) FROM game_data.dialogue_contexts) as dialogue_contexts
        """)
        
        data = sample_data[0]
        print(f"  - Regions: {data['regions']}개")
        print(f"  - Locations: {data['locations']}개")
        print(f"  - Cells: {data['cells']}개")
        print(f"  - Entities: {data['entities']}개")
        print(f"  - Objects: {data['objects']}개")
        print(f"  - Dialogue Contexts: {data['dialogue_contexts']}개")
        
        # MVP v2 핵심 기능 확인
        print("\n🎯 MVP v2 핵심 기능 확인:")
        
        # 시뮬레이션 테이블 확인
        simulation_count = await conn.fetchval("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'simulation_data'
        """)
        print(f"  - 시뮬레이션 테이블: {simulation_count}개")
        
        # 함수 확인
        functions = await conn.fetch("""
            SELECT routine_name 
            FROM information_schema.routines 
            WHERE routine_schema = 'simulation_data'
            ORDER BY routine_name
        """)
        print(f"  - 시뮬레이션 함수: {len(functions)}개")
        for func in functions:
            print(f"    - {func['routine_name']}")
        
        # 뷰 확인
        views = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = 'simulation_data'
            ORDER BY table_name
        """)
        print(f"  - 시뮬레이션 뷰: {len(views)}개")
        for view in views:
            print(f"    - {view['table_name']}")
        
        await conn.close()
        print("\n🎉 MVP v2 최종 데이터베이스 생성 완료!")
        print("📋 모든 기능이 포함된 완전한 스키마가 준비되었습니다.")
        
    except Exception as e:
        print(f"❌ MVP v2 스키마 생성 실패: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_mvp_v2_database())
