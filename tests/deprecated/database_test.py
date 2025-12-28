#!/usr/bin/env python3
"""
PostgreSQL 데이터베이스 연결 및 테이블 확인 테스트
"""

import psycopg2
import sys
import os

def test_database_connection():
    """데이터베이스 연결 테스트"""
    try:
        # PostgreSQL 연결
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='rpg_engine',
            user='postgres',
            password='2696Sjbj!'
        )
        
        cursor = conn.cursor()
        
        print('=' * 60)
        print('✅ PostgreSQL 연결 성공! (포트 5432)')
        print('=' * 60)
        
        # 1. 스키마 목록 확인
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name IN ('game_data', 'reference_layer', 'runtime_data')
            ORDER BY schema_name
        """)
        
        schemas = cursor.fetchall()
        print('\n📁 스키마 목록:')
        for schema in schemas:
            print(f'  ✓ {schema[0]}')
        
        if not schemas:
            print('  ❌ 스키마가 없습니다!')
            return False
        
        # 2. 각 스키마별 테이블 확인
        for schema_name in ['game_data', 'reference_layer', 'runtime_data']:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = %s 
                ORDER BY table_name
            """, (schema_name,))
            
            tables = cursor.fetchall()
            print(f'\n📋 {schema_name} 스키마의 테이블:')
            if tables:
                for table in tables:
                    print(f'  ✓ {table[0]}')
            else:
                print('  📝 아직 테이블이 없습니다 (정상)')
        
        # 3. 확장 기능 확인
        cursor.execute("""
            SELECT extname 
            FROM pg_extension 
            WHERE extname = 'uuid-ossp'
        """)
        
        if cursor.fetchone():
            print('\n✅ UUID 확장 기능 설치됨')
        else:
            print('\n❌ UUID 확장 기능이 설치되지 않음')
        
        cursor.close()
        conn.close()
        
        print('\n🎉 데이터베이스 설정 완료!')
        return True
        
    except psycopg2.OperationalError as e:
        print(f'❌ 연결 실패: {e}')
        return False
        
    except Exception as e:
        print(f'❌ 오류 발생: {e}')
        return False

def main():
    print('🧪 RPG Engine 데이터베이스 테스트')
    print('=' * 60)
    
    success = test_database_connection()
    
    if success:
        print('\n✅ 모든 테스트 통과!')
        print('\n📋 다음 단계:')
        print('1. 테이블 생성 스크립트 실행')
        print('2. 테스트 데이터 삽입')
        print('3. 애플리케이션 연결 테스트')
    else:
        print('\n❌ 테스트 실패!')
        print('데이터베이스 설정을 확인해주세요.')
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
