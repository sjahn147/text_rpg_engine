from typing import Optional, List, Dict, Any
import asyncpg
import json
from ..connection import DatabaseConnection

class ReferenceLayerRepository:
    def __init__(self, db_connection=None):
        self.db = db_connection or DatabaseConnection()

    async def create_entity_reference(self, reference_data: Dict[str, Any]) -> str:
        """엔티티 참조를 생성합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO reference_layer.entity_references
                (runtime_entity_id, game_entity_id, session_id, entity_type, is_player)
                VALUES ($1, $2, $3, $4, $5)
                """,
                reference_data['runtime_entity_id'],
                reference_data['game_entity_id'],
                reference_data['session_id'],
                reference_data['entity_type'],
                reference_data.get('is_player', False)
            )
            return reference_data['runtime_entity_id']

    async def create_object_reference(self, reference_data: Dict[str, Any]) -> str:
        """오브젝트 참조를 생성합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO reference_layer.object_references
                (runtime_object_id, game_object_id, session_id, object_type)
                VALUES ($1, $2, $3, $4)
                """,
                reference_data['runtime_object_id'],
                reference_data['game_object_id'],
                reference_data['session_id'],
                reference_data['object_type']
            )
            return reference_data['runtime_object_id']

    async def create_cell_reference(self, reference_data: Dict[str, Any]) -> str:
        """셀 참조를 생성합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO reference_layer.cell_references
                (runtime_cell_id, game_cell_id, session_id)
                VALUES ($1, $2, $3)
                """,
                reference_data['runtime_cell_id'],
                reference_data['game_cell_id'],
                reference_data['session_id']
            )
            return reference_data['runtime_cell_id']

    async def get_entity_reference(self, runtime_entity_id: str) -> Optional[Dict[str, Any]]:
        """런타임 엔티티 ID로 엔티티 참조 정보를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM reference_layer.entity_references 
                WHERE runtime_entity_id = $1
                """, 
                runtime_entity_id
            )
            return dict(row) if row else None

    async def get_entity_references_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        """세션 ID로 모든 엔티티 참조를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM reference_layer.entity_references 
                WHERE session_id = $1
                """, 
                session_id
            )
            return [dict(row) for row in rows]

    async def get_entity_references_by_type(self, entity_type: str, session_id: str) -> List[Dict[str, Any]]:
        """특정 타입의 엔티티 참조를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM reference_layer.entity_references 
                WHERE entity_type = $1 AND session_id = $2
                """, 
                entity_type, session_id
            )
            return [dict(row) for row in rows]

    async def get_player_entity_references(self, session_id: str) -> List[Dict[str, Any]]:
        """세션의 플레이어 엔티티 참조를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM reference_layer.entity_references 
                WHERE session_id = $1 AND is_player = TRUE
                """, 
                session_id
            )
            return [dict(row) for row in rows]

    async def get_npc_entity_references(self, session_id: str) -> List[Dict[str, Any]]:
        """세션의 NPC 엔티티 참조를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM reference_layer.entity_references 
                WHERE session_id = $1 AND is_player = FALSE
                """, 
                session_id
            )
            return [dict(row) for row in rows]

    async def get_object_reference(self, runtime_object_id: str) -> Optional[Dict[str, Any]]:
        """런타임 오브젝트 ID로 오브젝트 참조 정보를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM reference_layer.object_references 
                WHERE runtime_object_id = $1
                """, 
                runtime_object_id
            )
            return dict(row) if row else None

    async def get_object_references_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        """세션 ID로 모든 오브젝트 참조를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM reference_layer.object_references 
                WHERE session_id = $1
                """, 
                session_id
            )
            return [dict(row) for row in rows]

    async def get_cell_reference(self, runtime_cell_id: str) -> Optional[Dict[str, Any]]:
        """런타임 셀 ID로 셀 참조 정보를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM reference_layer.cell_references 
                WHERE runtime_cell_id = $1
                """, 
                runtime_cell_id
            )
            return dict(row) if row else None

    async def get_cell_references_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        """세션 ID로 모든 셀 참조를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM reference_layer.cell_references 
                WHERE session_id = $1
                """, 
                session_id
            )
            return [dict(row) for row in rows]

    async def delete_entity_reference(self, runtime_entity_id: str) -> bool:
        """엔티티 참조를 삭제합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            result = await conn.execute(
                """
                DELETE FROM reference_layer.entity_references 
                WHERE runtime_entity_id = $1
                """, 
                runtime_entity_id
            )
            return result != "DELETE 0"

    async def delete_object_reference(self, runtime_object_id: str) -> bool:
        """오브젝트 참조를 삭제합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            result = await conn.execute(
                """
                DELETE FROM reference_layer.object_references 
                WHERE runtime_object_id = $1
                """, 
                runtime_object_id
            )
            return result != "DELETE 0"

    async def delete_cell_reference(self, runtime_cell_id: str) -> bool:
        """셀 참조를 삭제합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            result = await conn.execute(
                """
                DELETE FROM reference_layer.cell_references 
                WHERE runtime_cell_id = $1
                """, 
                runtime_cell_id
            )
            return result != "DELETE 0" 