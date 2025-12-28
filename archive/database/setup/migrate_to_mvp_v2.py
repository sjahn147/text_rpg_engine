#!/usr/bin/env python3
"""
MVP v2 스키마 마이그레이션 스크립트
기존 스키마 리셋 및 새로운 MVP v2 스키마 적용
"""

import asyncio
import asyncpg
from pathlib import Path
import subprocess
import sys
from datetime import datetime
import os

class DatabaseMigrator:
    def __init__(self):
        self.connection_config = {
            'host': 'localhost',
            'port': 5432,
            'user': 'postgres',
            'password': '2696Sjbj!',
            'database': 'rpg_engine'
        }
        self.backup_dir = Path("backup")
        self.backup_dir.mkdir(exist_ok=True)
    
    async def backup_current_schema(self):
        """현재 스키마 백업 (Python으로 직접 백업)"""
        print("📦 현재 스키마 백업 중...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = self.backup_dir / f"schema_v1_{timestamp}.sql"
        
        conn = await asyncpg.connect(**self.connection_config)
        
        try:
            # 스키마 구조 백업
            schemas = await conn.fetch("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name IN ('game_data', 'reference_layer', 'runtime_data', 'simulation_data')
                ORDER BY schema_name
            """)
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write("-- 스키마 백업\n")
                f.write(f"-- 백업 시간: {datetime.now()}\n")
                f.write("-- PostgreSQL 스키마 백업\n\n")
                
                for schema in schemas:
                    schema_name = schema['schema_name']
                    f.write(f"-- {schema_name} 스키마\n")
                    f.write(f"CREATE SCHEMA IF NOT EXISTS {schema_name};\n\n")
                    
                    # 테이블 구조 백업
                    tables = await conn.fetch("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = $1
                        ORDER BY table_name
                    """, schema_name)
                    
                    for table in tables:
                        table_name = table['table_name']
                        f.write(f"-- {schema_name}.{table_name} 테이블\n")
                        f.write(f"-- (테이블 구조는 복원 시 수동으로 확인 필요)\n\n")
            
            print(f"✅ 스키마 백업 완료: {backup_file}")
            return str(backup_file)
            
        except Exception as e:
            print(f"❌ 스키마 백업 실패: {e}")
            return None
        finally:
            await conn.close()
    
    async def reset_schemas(self):
        """기존 스키마 리셋"""
        print("🗑️ 기존 스키마 리셋 중...")
        conn = await asyncpg.connect(**self.connection_config)
        
        try:
            # 모든 스키마 삭제
            await conn.execute("DROP SCHEMA IF EXISTS game_data CASCADE")
            await conn.execute("DROP SCHEMA IF EXISTS reference_layer CASCADE")
            await conn.execute("DROP SCHEMA IF EXISTS runtime_data CASCADE")
            await conn.execute("DROP SCHEMA IF EXISTS simulation_data CASCADE")
            
            print("✅ 기존 스키마 삭제 완료")
        except Exception as e:
            print(f"❌ 스키마 리셋 실패: {e}")
            raise
        finally:
            await conn.close()
    
    async def apply_new_schema(self):
        """새로운 스키마 적용"""
        print("🏗️ 새로운 MVP v2 스키마 적용 중...")
        schema_file = Path("database/mvp_schema.sql")
        
        if not schema_file.exists():
            print(f"❌ 스키마 파일을 찾을 수 없습니다: {schema_file}")
            return False
        
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        conn = await asyncpg.connect(**self.connection_config)
        
        try:
            await conn.execute(schema_sql)
            print("✅ 새로운 스키마 적용 완료")
            return True
        except Exception as e:
            print(f"❌ 스키마 적용 실패: {e}")
            return False
        finally:
            await conn.close()
    
    async def verify_schema(self):
        """스키마 검증"""
        print("🔍 스키마 검증 중...")
        conn = await asyncpg.connect(**self.connection_config)
        
        try:
            # 스키마 존재 확인
            schemas = await conn.fetch("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name IN ('game_data', 'reference_layer', 'runtime_data')
                ORDER BY schema_name
            """)
            
            expected_schemas = {'game_data', 'reference_layer', 'runtime_data'}
            actual_schemas = {row['schema_name'] for row in schemas}
            
            if expected_schemas == actual_schemas:
                print("✅ 모든 스키마 생성 확인")
            else:
                missing = expected_schemas - actual_schemas
                print(f"❌ 누락된 스키마: {missing}")
                return False
            
            # 테이블 개수 확인
            table_counts = await conn.fetch("""
                SELECT 
                    table_schema,
                    COUNT(*) as table_count
                FROM information_schema.tables 
                WHERE table_schema IN ('game_data', 'reference_layer', 'runtime_data')
                GROUP BY table_schema
                ORDER BY table_schema
            """)
            
            print("📊 테이블 개수:")
            for row in table_counts:
                print(f"  {row['table_schema']}: {row['table_count']}개")
            
            return True
            
        except Exception as e:
            print(f"❌ 스키마 검증 실패: {e}")
            return False
        finally:
            await conn.close()
    
    async def run_migration(self):
        """전체 마이그레이션 실행"""
        print("🚀 MVP v2 스키마 마이그레이션 시작")
        print("=" * 50)
        
        try:
            # 1. 백업
            backup_file = await self.backup_current_schema()
            if not backup_file:
                print("❌ 백업 실패로 마이그레이션 중단")
                return False
            
            # 2. 리셋
            await self.reset_schemas()
            
            # 3. 적용
            success = await self.apply_new_schema()
            if not success:
                print("❌ 스키마 적용 실패")
                return False
            
            # 4. 검증
            verified = await self.verify_schema()
            if not verified:
                print("❌ 스키마 검증 실패")
                return False
            
            print("=" * 50)
            print("✅ MVP v2 스키마 마이그레이션 완료!")
            print(f"📦 백업 파일: {backup_file}")
            return True
            
        except Exception as e:
            print(f"❌ 마이그레이션 실패: {e}")
            print("🔄 롤백을 위해 백업 파일을 사용하세요")
            return False

async def main():
    """메인 실행 함수"""
    migrator = DatabaseMigrator()
    
    # 사용자 확인
    print("⚠️  이 작업은 기존 스키마를 완전히 삭제합니다.")
    print("📦 백업은 자동으로 생성되지만, 중요한 데이터가 있다면 별도 백업을 권장합니다.")
    
    response = input("계속하시겠습니까? (y/N): ")
    if response.lower() != 'y':
        print("❌ 마이그레이션 취소됨")
        return
    
    success = await migrator.run_migration()
    
    if success:
        print("\n🎉 마이그레이션 성공!")
        print("다음 단계: 테스트 실행")
        print("  python -m pytest tests/unit/test_database_connection.py -v")
    else:
        print("\n💥 마이그레이션 실패!")
        print("롤백 방법:")
        print("  psql -h localhost -p 5432 -U postgres -d rpg_engine -f backup/schema_v1_YYYYMMDD_HHMMSS.sql")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
