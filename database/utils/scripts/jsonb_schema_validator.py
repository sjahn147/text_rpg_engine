#!/usr/bin/env python3
"""
JSONB 스키마 검증 및 처리 개선 모듈
JSONB 데이터의 파싱/직렬화 통일 및 스키마 검증
"""
import json
import asyncio
import sys
import os
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from datetime import datetime
import jsonschema
from jsonschema import validate, ValidationError

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from database.connection import DatabaseConnection
from common.utils.logger import logger

@dataclass
class JSONBSchema:
    """JSONB 스키마 정의"""
    table_name: str
    column_name: str
    schema: Dict[str, Any]
    required_fields: List[str]
    optional_fields: List[str]

class JSONBSchemaValidator:
    """JSONB 스키마 검증 클래스"""
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.schemas: Dict[str, JSONBSchema] = {}
        self.validation_errors: List[Dict[str, Any]] = []
    
    async def initialize(self):
        """DB 초기화"""
        try:
            await self.db.initialize()
            logger.info("✅ JSONB 스키마 검증기 초기화 완료")
        except Exception as e:
            logger.error(f"❌ 초기화 실패: {e}")
            raise
    
    async def cleanup(self):
        """DB 정리"""
        try:
            await self.db.close()
            logger.info("✅ JSONB 스키마 검증기 정리 완료")
        except Exception as e:
            logger.error(f"❌ 정리 실패: {e}")
    
    def define_schemas(self):
        """JSONB 스키마 정의"""
        # 엔티티 속성 스키마
        self.schemas["entity_properties"] = JSONBSchema(
            table_name="entities",
            column_name="entity_properties",
            schema={
                "type": "object",
                "properties": {
                    "personality": {"type": "string"},
                    "alignment": {"type": "string"},
                    "background": {"type": "string"},
                    "position": {
                        "type": "object",
                        "properties": {
                            "x": {"type": "number"},
                            "y": {"type": "number"}
                        },
                        "required": ["x", "y"]
                    },
                    "status": {"type": "string"},
                    "level": {"type": "integer", "minimum": 1},
                    "experience": {"type": "integer", "minimum": 0}
                }
            },
            required_fields=["personality", "position"],
            optional_fields=["alignment", "background", "status", "level", "experience"]
        )
        
        # 대화 컨텍스트 스키마
        self.schemas["dialogue_contexts"] = JSONBSchema(
            table_name="dialogue_contexts",
            column_name="available_topics",
            schema={
                "type": "object",
                "properties": {
                    "topics": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "default_topic": {"type": "string"},
                    "priority": {"type": "integer", "minimum": 1}
                },
                "required": ["topics"]
            },
            required_fields=["topics"],
            optional_fields=["default_topic", "priority"]
        )
        
        # Effect Carrier 스키마
        self.schemas["effect_carriers"] = JSONBSchema(
            table_name="effect_carriers",
            column_name="effect_json",
            schema={
                "type": "object",
                "properties": {
                    "effect_type": {"type": "string"},
                    "magnitude": {"type": "number"},
                    "duration": {"type": "integer"},
                    "target": {"type": "string"},
                    "conditions": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["effect_type", "magnitude"]
            },
            required_fields=["effect_type", "magnitude"],
            optional_fields=["duration", "target", "conditions"]
        )
        
        # 셀 속성 스키마
        self.schemas["cell_properties"] = JSONBSchema(
            table_name="world_cells",
            column_name="cell_properties",
            schema={
                "type": "object",
                "properties": {
                    "terrain": {"type": "string"},
                    "lighting": {"type": "string"},
                    "temperature": {"type": "number"},
                    "humidity": {"type": "number"},
                    "accessibility": {"type": "boolean"},
                    "special_properties": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            },
            required_fields=["terrain", "lighting"],
            optional_fields=["temperature", "humidity", "accessibility", "special_properties"]
        )
    
    async def validate_jsonb_data(self, table_name: str, column_name: str, data: Any) -> Dict[str, Any]:
        """JSONB 데이터 검증"""
        schema_key = f"{table_name}_{column_name}"
        
        if schema_key not in self.schemas:
            logger.warning(f"스키마 정의 없음: {schema_key}")
            return {"valid": True, "errors": []}
        
        schema_def = self.schemas[schema_key]
        
        try:
            # JSONB 데이터가 문자열인 경우 파싱
            if isinstance(data, str):
                data = json.loads(data)
            
            # 스키마 검증
            validate(instance=data, schema=schema_def.schema)
            
            return {"valid": True, "errors": []}
            
        except ValidationError as e:
            error_info = {
                "table": table_name,
                "column": column_name,
                "error": str(e),
                "path": " -> ".join(str(p) for p in e.absolute_path) if e.absolute_path else "root"
            }
            self.validation_errors.append(error_info)
            return {"valid": False, "errors": [error_info]}
        
        except json.JSONDecodeError as e:
            error_info = {
                "table": table_name,
                "column": column_name,
                "error": f"JSON 파싱 오류: {str(e)}",
                "path": "root"
            }
            self.validation_errors.append(error_info)
            return {"valid": False, "errors": [error_info]}
    
    async def audit_all_jsonb_columns(self):
        """모든 JSONB 컬럼 감사"""
        logger.info("🔍 JSONB 컬럼 감사 시작...")
        
        # JSONB 컬럼 조회
        query = """
        SELECT 
            table_schema,
            table_name,
            column_name,
            data_type
        FROM information_schema.columns
        WHERE data_type = 'jsonb'
        AND table_schema IN ('game_data', 'reference_layer', 'runtime_data')
        ORDER BY table_schema, table_name, column_name
        """
        
        pool = await self.db.pool
        async with pool.acquire() as conn:
            rows = await conn.fetch(query)
            
            logger.info(f"📊 총 {len(rows)}개 JSONB 컬럼 발견")
            
            for row in rows:
                schema_name = row['table_schema']
                table_name = row['table_name']
                column_name = row['column_name']
                full_table_name = f"{schema_name}.{table_name}"
                
                logger.info(f"🔍 검증 중: {full_table_name}.{column_name}")
                
                # 샘플 데이터 조회 (최대 10개)
                sample_query = f"""
                SELECT {column_name}
                FROM {full_table_name}
                WHERE {column_name} IS NOT NULL
                LIMIT 10
                """
                
                try:
                    sample_rows = await conn.fetch(sample_query)
                    
                    for sample_row in sample_rows:
                        data = sample_row[column_name]
                        result = await self.validate_jsonb_data(table_name, column_name, data)
                        
                        if not result["valid"]:
                            logger.warning(f"❌ 검증 실패: {full_table_name}.{column_name}")
                            for error in result["errors"]:
                                logger.warning(f"   - {error['error']} (경로: {error['path']})")
                        else:
                            logger.info(f"✅ 검증 성공: {full_table_name}.{column_name}")
                
                except Exception as e:
                    logger.error(f"❌ 샘플 데이터 조회 실패: {full_table_name}.{column_name} - {str(e)}")
    
    async def generate_validation_report(self):
        """검증 보고서 생성"""
        logger.info("📊 JSONB 검증 보고서 생성...")
        
        report = {
            "validation_date": datetime.now().isoformat(),
            "total_schemas": len(self.schemas),
            "total_errors": len(self.validation_errors),
            "schemas": {key: schema.__dict__ for key, schema in self.schemas.items()},
            "validation_errors": self.validation_errors,
            "recommendations": []
        }
        
        # 권장사항 생성
        if self.validation_errors:
            report["recommendations"].append("JSONB 데이터 검증 실패 발견 - 데이터 정리 필요")
        
        if len(self.schemas) < 5:
            report["recommendations"].append("추가 JSONB 스키마 정의 필요")
        
        # 보고서 저장
        report_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "tests", "reports", "jsonb_validation_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ 검증 보고서 저장: {report_path}")
        logger.info(f"📊 총 스키마: {report['total_schemas']}개")
        logger.info(f"📊 총 오류: {report['total_errors']}개")
        
        return report

async def main():
    """메인 함수"""
    validator = JSONBSchemaValidator()
    
    try:
        await validator.initialize()
        validator.define_schemas()
        await validator.audit_all_jsonb_columns()
        await validator.generate_validation_report()
        
        logger.info("🎉 JSONB 스키마 검증 완료!")
        
    except Exception as e:
        logger.error(f"❌ 검증 중 오류 발생: {e}")
    finally:
        await validator.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
