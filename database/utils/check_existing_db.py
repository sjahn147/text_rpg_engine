"""
기존 데이터베이스 상태 확인 스크립트
"""
import asyncio
import asyncpg

async def check_existing_database():
    """기존 데이터베이스 상태 확인"""
    try:
        # 데이터베이스 연결
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='2696Sjbj!',
            database='rpg_engine'
        )
        
        print("🔍 기존 데이터베이스 상태 확인 중...")
        
        # 스키마 존재 여부 확인
        schemas = await conn.fetch("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name IN ('game_data', 'reference_layer', 'runtime_data')
            ORDER BY schema_name
        """)
        
        print(f"📊 발견된 스키마: {[row['schema_name'] for row in schemas]}")
        
        # 각 스키마의 테이블 확인
        for schema in schemas:
            schema_name = schema['schema_name']
            tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = $1
                ORDER BY table_name
            """, schema_name)
            
            print(f"\n📋 {schema_name} 스키마의 테이블:")
            for table in tables:
                print(f"  - {table['table_name']}")
        
        # 데이터 개수 확인
        print(f"\n📈 데이터 개수 확인:")
        for schema in schemas:
            schema_name = schema['schema_name']
            tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = $1
                ORDER BY table_name
            """, schema_name)
            
            for table in tables:
                table_name = table['table_name']
                try:
                    count = await conn.fetchval(f"SELECT COUNT(*) FROM {schema_name}.{table_name}")
                    print(f"  - {schema_name}.{table_name}: {count}개")
                except Exception as e:
                    print(f"  - {schema_name}.{table_name}: 확인 불가 ({str(e)})")
        
        await conn.close()
        print("\n✅ 데이터베이스 상태 확인 완료")
        
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {str(e)}")

if __name__ == "__main__":
    asyncio.run(check_existing_database())
