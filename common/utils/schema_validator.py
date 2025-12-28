"""
스키마 검증 유틸리티
"""
from typing import Dict, List, Optional, Any, Tuple
import asyncio
from database.connection import DatabaseConnection
from common.utils.logger import logger


class SchemaValidator:
    """스키마 검증 클래스"""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
        self.logger = logger
        self._schema_cache: Dict[str, Any] = {}
        self._cache_lock = asyncio.Lock()
    
    async def validate_table_exists(self, schema_name: str, table_name: str) -> bool:
        """
        테이블 존재 여부 검증
        
        Args:
            schema_name: 스키마 이름
            table_name: 테이블 이름
            
        Returns:
            테이블 존재 여부
        """
        try:
            cache_key = f"{schema_name}.{table_name}"
            
            async with self._cache_lock:
                if cache_key in self._schema_cache:
                    return self._schema_cache[cache_key]
            
            pool = await self.db.pool
            async with pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT EXISTS (
                        SELECT 1 
                        FROM information_schema.tables 
                        WHERE table_schema = $1 AND table_name = $2
                    )
                """, schema_name, table_name)
                
                exists = result['exists'] if result else False
                
                async with self._cache_lock:
                    self._schema_cache[cache_key] = exists
                
                return exists
                
        except Exception as e:
            self.logger.error(f"Failed to validate table existence: {str(e)}")
            return False
    
    async def validate_columns_exist(self, schema_name: str, table_name: str, 
                                   required_columns: List[str]) -> Tuple[bool, List[str]]:
        """
        컬럼 존재 여부 검증
        
        Args:
            schema_name: 스키마 이름
            table_name: 테이블 이름
            required_columns: 필수 컬럼 목록
            
        Returns:
            (모든 컬럼 존재 여부, 누락된 컬럼 목록)
        """
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                result = await conn.fetch("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_schema = $1 AND table_name = $2
                """, schema_name, table_name)
                
                existing_columns = [row['column_name'] for row in result]
                missing_columns = [col for col in required_columns if col not in existing_columns]
                
                return len(missing_columns) == 0, missing_columns
                
        except Exception as e:
            self.logger.error(f"Failed to validate columns: {str(e)}")
            return False, required_columns
    
    async def validate_foreign_keys(self, schema_name: str, table_name: str) -> bool:
        """
        외래 키 제약 조건 검증
        
        Args:
            schema_name: 스키마 이름
            table_name: 테이블 이름
            
        Returns:
            외래 키 제약 조건 존재 여부
        """
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT COUNT(*) as fk_count
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu 
                        ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.table_schema = $1 
                        AND tc.table_name = $2 
                        AND tc.constraint_type = 'FOREIGN KEY'
                """, schema_name, table_name)
                
                return result['fk_count'] > 0 if result else False
                
        except Exception as e:
            self.logger.error(f"Failed to validate foreign keys: {str(e)}")
            return False
    
    async def validate_indexes(self, schema_name: str, table_name: str, 
                             required_indexes: List[str]) -> Tuple[bool, List[str]]:
        """
        인덱스 존재 여부 검증
        
        Args:
            schema_name: 스키마 이름
            table_name: 테이블 이름
            required_indexes: 필수 인덱스 목록
            
        Returns:
            (모든 인덱스 존재 여부, 누락된 인덱스 목록)
        """
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                result = await conn.fetch("""
                    SELECT indexname 
                    FROM pg_indexes 
                    WHERE schemaname = $1 AND tablename = $2
                """, schema_name, table_name)
                
                existing_indexes = [row['indexname'] for row in result]
                missing_indexes = [idx for idx in required_indexes if idx not in existing_indexes]
                
                return len(missing_indexes) == 0, missing_indexes
                
        except Exception as e:
            self.logger.error(f"Failed to validate indexes: {str(e)}")
            return False, required_indexes
    
    async def validate_manager_schema(self, manager_name: str) -> Dict[str, Any]:
        """
        매니저별 스키마 검증
        
        Args:
            manager_name: 매니저 이름
            
        Returns:
            검증 결과
        """
        validation_results = {
            "manager": manager_name,
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            if manager_name == "EntityManager":
                # EntityManager 스키마 검증
                await self._validate_entity_manager_schema(validation_results)
            elif manager_name == "CellManager":
                # CellManager 스키마 검증
                await self._validate_cell_manager_schema(validation_results)
            elif manager_name == "ActionHandler":
                # ActionHandler 스키마 검증
                await self._validate_action_handler_schema(validation_results)
            elif manager_name == "DialogueManager":
                # DialogueManager 스키마 검증
                await self._validate_dialogue_manager_schema(validation_results)
            else:
                validation_results["errors"].append(f"Unknown manager: {manager_name}")
                validation_results["valid"] = False
            
        except Exception as e:
            validation_results["errors"].append(f"Schema validation failed: {str(e)}")
            validation_results["valid"] = False
        
        return validation_results
    
    async def _validate_entity_manager_schema(self, results: Dict[str, Any]):
        """EntityManager 스키마 검증"""
        # 필수 테이블 검증
        required_tables = [
            ("game_data", "entities"),
            ("runtime_data", "runtime_entities"),
            ("reference_layer", "entity_references")
        ]
        
        for schema, table in required_tables:
            if not await self.validate_table_exists(schema, table):
                results["errors"].append(f"Required table {schema}.{table} does not exist")
                results["valid"] = False
        
        # 필수 컬럼 검증
        if await self.validate_table_exists("game_data", "entities"):
            required_columns = ["entity_id", "entity_type", "entity_name", "base_stats"]
            valid, missing = await self.validate_columns_exist("game_data", "entities", required_columns)
            if not valid:
                results["errors"].append(f"Missing columns in game_data.entities: {missing}")
                results["valid"] = False
    
    async def _validate_cell_manager_schema(self, results: Dict[str, Any]):
        """CellManager 스키마 검증"""
        # 필수 테이블 검증
        required_tables = [
            ("game_data", "world_cells"),
            ("runtime_data", "runtime_cells"),
            ("reference_layer", "cell_references")
        ]
        
        for schema, table in required_tables:
            if not await self.validate_table_exists(schema, table):
                results["errors"].append(f"Required table {schema}.{table} does not exist")
                results["valid"] = False
    
    async def _validate_action_handler_schema(self, results: Dict[str, Any]):
        """ActionHandler 스키마 검증"""
        # 필수 테이블 검증
        required_tables = [
            ("runtime_data", "action_logs"),
            ("runtime_data", "active_sessions")
        ]
        
        for schema, table in required_tables:
            if not await self.validate_table_exists(schema, table):
                results["errors"].append(f"Required table {schema}.{table} does not exist")
                results["valid"] = False
    
    async def _validate_dialogue_manager_schema(self, results: Dict[str, Any]):
        """DialogueManager 스키마 검증"""
        # 필수 테이블 검증
        required_tables = [
            ("game_data", "dialogue_contexts"),
            ("game_data", "dialogue_topics"),
            ("runtime_data", "dialogue_history")
        ]
        
        for schema, table in required_tables:
            if not await self.validate_table_exists(schema, table):
                results["errors"].append(f"Required table {schema}.{table} does not exist")
                results["valid"] = False
    
    async def clear_cache(self):
        """스키마 캐시 초기화"""
        async with self._cache_lock:
            self._schema_cache.clear()
