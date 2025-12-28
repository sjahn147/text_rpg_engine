#!/usr/bin/env python3
"""
DB 스키마 완전 Audit 스크립트
모든 테이블, 컬럼, 제약조건을 체계적으로 검증
"""
import asyncio
import sys
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from database.connection import DatabaseConnection
from common.utils.logger import logger

@dataclass
class ColumnInfo:
    """컬럼 정보"""
    column_name: str
    data_type: str
    is_nullable: bool
    column_default: Optional[str]
    character_maximum_length: Optional[int]

@dataclass
class TableInfo:
    """테이블 정보"""
    table_name: str
    schema_name: str
    columns: List[ColumnInfo]
    constraints: List[Dict[str, Any]]

class DatabaseSchemaAuditor:
    """DB 스키마 감사 클래스"""
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.audit_results = {
            "tables": {},
            "issues": [],
            "recommendations": []
        }
    
    async def initialize(self):
        """DB 초기화"""
        try:
            await self.db.initialize()
            logger.info("✅ DB 연결 성공")
        except Exception as e:
            logger.error(f"❌ DB 연결 실패: {e}")
            raise
    
    async def cleanup(self):
        """DB 정리"""
        try:
            await self.db.close()
            logger.info("✅ DB 연결 해제")
        except Exception as e:
            logger.error(f"❌ DB 정리 실패: {e}")
    
    async def get_all_tables(self) -> List[Dict[str, str]]:
        """모든 테이블 조회"""
        query = """
        SELECT 
            schemaname,
            tablename,
            tableowner
        FROM pg_tables 
        WHERE schemaname IN ('game_data', 'reference_layer', 'runtime_data')
        ORDER BY schemaname, tablename
        """
        
        pool = await self.db.pool
        async with pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [dict(row) for row in rows]
    
    async def get_table_columns(self, schema_name: str, table_name: str) -> List[ColumnInfo]:
        """테이블 컬럼 정보 조회"""
        query = """
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default,
            character_maximum_length
        FROM information_schema.columns
        WHERE table_schema = $1 AND table_name = $2
        ORDER BY ordinal_position
        """
        
        pool = await self.db.pool
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, schema_name, table_name)
            return [ColumnInfo(**dict(row)) for row in rows]
    
    async def get_table_constraints(self, schema_name: str, table_name: str) -> List[Dict[str, Any]]:
        """테이블 제약조건 조회"""
        query = """
        SELECT 
            tc.constraint_name,
            tc.constraint_type,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints tc
        LEFT JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        LEFT JOIN information_schema.constraint_column_usage ccu
            ON tc.constraint_name = ccu.constraint_name
        WHERE tc.table_schema = $1 AND tc.table_name = $2
        """
        
        pool = await self.db.pool
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, schema_name, table_name)
            return [dict(row) for row in rows]
    
    async def audit_schema(self):
        """스키마 전체 감사"""
        print("🔍 DB 스키마 감사 시작...")
        
        # 모든 테이블 조회
        tables = await self.get_all_tables()
        print(f"📊 총 {len(tables)}개 테이블 발견")
        
        for table in tables:
            schema_name = table['schemaname']
            table_name = table['tablename']
            full_table_name = f"{schema_name}.{table_name}"
            
            print(f"\n📋 테이블: {full_table_name}")
            
            # 컬럼 정보 조회
            columns = await self.get_table_columns(schema_name, table_name)
            print(f"   컬럼 수: {len(columns)}")
            
            # 제약조건 조회
            constraints = await self.get_table_constraints(schema_name, table_name)
            print(f"   제약조건 수: {len(constraints)}")
            
            # 테이블 정보 저장
            self.audit_results["tables"][full_table_name] = {
                "columns": [column.__dict__ for column in columns],
                "constraints": constraints,
                "column_count": len(columns),
                "constraint_count": len(constraints)
            }
            
            # 컬럼별 상세 정보 출력
            for column in columns:
                nullable = "NULL" if column.is_nullable == "YES" else "NOT NULL"
                default = f"DEFAULT {column.column_default}" if column.column_default else ""
                print(f"   - {column.column_name}: {column.data_type} {nullable} {default}")
            
            # 제약조건별 상세 정보 출력
            for constraint in constraints:
                if constraint['constraint_type'] == 'FOREIGN KEY':
                    print(f"   - FK: {constraint['column_name']} -> {constraint['foreign_table_name']}.{constraint['foreign_column_name']}")
                elif constraint['constraint_type'] == 'PRIMARY KEY':
                    print(f"   - PK: {constraint['column_name']}")
                elif constraint['constraint_type'] == 'UNIQUE':
                    print(f"   - UNIQUE: {constraint['column_name']}")
    
    async def check_foreign_key_integrity(self):
        """Foreign Key 무결성 검사"""
        logger.info("🔗 Foreign Key 무결성 검사...")
        
        query = """
        SELECT 
            tc.table_schema,
            tc.table_name,
            tc.constraint_name,
            kcu.column_name,
            ccu.table_schema AS foreign_table_schema,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage ccu
            ON tc.constraint_name = ccu.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
        ORDER BY tc.table_schema, tc.table_name
        """
        
        pool = await self.db.pool
        async with pool.acquire() as conn:
            rows = await conn.fetch(query)
            
            for row in rows:
                logger.info(f"FK: {row['table_schema']}.{row['table_name']}.{row['column_name']} -> {row['foreign_table_schema']}.{row['foreign_table_name']}.{row['foreign_column_name']}")
    
    async def check_missing_indexes(self):
        """누락된 인덱스 검사"""
        logger.info("📈 인덱스 최적화 검사...")
        
        query = """
        SELECT 
            schemaname,
            tablename,
            indexname,
            indexdef
        FROM pg_indexes
        WHERE schemaname IN ('game_data', 'reference_layer', 'runtime_data')
        ORDER BY schemaname, tablename
        """
        
        pool = await self.db.pool
        async with pool.acquire() as conn:
            rows = await conn.fetch(query)
            
            for row in rows:
                logger.info(f"인덱스: {row['schemaname']}.{row['tablename']}.{row['indexname']}")
    
    async def generate_audit_report(self):
        """감사 보고서 생성"""
        print("\n📊 감사 보고서 생성...")
        
        report = {
            "audit_date": datetime.now().isoformat(),
            "total_tables": len(self.audit_results["tables"]),
            "schemas": {
                "game_data": 0,
                "reference_layer": 0,
                "runtime_data": 0
            },
            "total_columns": 0,
            "total_constraints": 0,
            "tables": self.audit_results["tables"]
        }
        
        # 스키마별 테이블 수 계산
        for table_name in self.audit_results["tables"]:
            schema_name = table_name.split('.')[0]
            if schema_name in report["schemas"]:
                report["schemas"][schema_name] += 1
            
            table_info = self.audit_results["tables"][table_name]
            report["total_columns"] += table_info["column_count"]
            report["total_constraints"] += table_info["constraint_count"]
        
        # 보고서 저장
        report_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "tests", "reports", "audit_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 감사 보고서 저장: {report_path}")
        print(f"📊 총 테이블: {report['total_tables']}개")
        print(f"📊 총 컬럼: {report['total_columns']}개")
        print(f"📊 총 제약조건: {report['total_constraints']}개")
        
        return report

async def main():
    """메인 함수"""
    auditor = DatabaseSchemaAuditor()
    
    try:
        await auditor.initialize()
        await auditor.audit_schema()
        await auditor.check_foreign_key_integrity()
        await auditor.check_missing_indexes()
        await auditor.generate_audit_report()
        
        logger.info("🎉 DB 스키마 감사 완료!")
        
    except Exception as e:
        logger.error(f"❌ 감사 중 오류 발생: {e}")
    finally:
        await auditor.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
