from typing import Optional, List, Dict, Any
import asyncpg
import json
from ..connection import DatabaseConnection

class RuntimeDataRepository:
    def __init__(self, db_connection=None):
        self.db = db_connection or DatabaseConnection()

    async def create_session(self, session_data: Dict[str, Any]) -> str:
        """세션을 생성합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO runtime_data.active_sessions
                (session_id, player_runtime_entity_id, session_state, created_at, last_active_at, closed_at, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                session_data['session_id'],
                session_data.get('player_runtime_entity_id'),
                session_data.get('session_state', 'active'),
                session_data['created_at'],
                session_data.get('last_active_at', session_data['created_at']),
                session_data.get('closed_at', None),
                session_data.get('metadata', '{}')
            )
            return session_data['session_id']

    async def create_entity_state(self, entity_state_data: Dict[str, Any]) -> str:
        """엔티티 상태를 생성합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO runtime_data.entity_states
                (runtime_entity_id, runtime_cell_id, current_stats, current_position, active_effects, inventory, equipped_items)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                entity_state_data['runtime_entity_id'],
                entity_state_data['runtime_cell_id'],
                entity_state_data['current_stats'],
                entity_state_data['current_position'],
                entity_state_data.get('active_effects', []),
                entity_state_data.get('inventory', []),
                entity_state_data.get('equipped_items', [])
            )
            return entity_state_data['runtime_entity_id']

    async def create_cell(self, cell_data: Dict[str, Any]) -> str:
        """셀을 생성합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO runtime_data.cells
                (runtime_cell_id, session_id, properties)
                VALUES ($1, $2, $3)
                """,
                cell_data['runtime_cell_id'],
                cell_data['session_id'],
                cell_data['properties']
            )
            return cell_data['runtime_cell_id']

    async def get_cell_data(self, runtime_cell_id: str) -> Dict[str, Any]:
        """셀의 엔티티와 오브젝트 정보를 로드합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # 엔티티 정보 조회 (current_position JSONB에서 runtime_cell_id 확인)
            entities = await conn.fetch(
                """
                SELECT 
                    es.*,
                    er.entity_type,
                    er.game_entity_id,
                    er.is_player
                FROM runtime_data.entity_states es
                JOIN reference_layer.entity_references er 
                    ON es.runtime_entity_id = er.runtime_entity_id
                WHERE es.current_position->>'runtime_cell_id' = $1
                """,
                runtime_cell_id
            )
            
            # 오브젝트 정보 조회 (session_id 기준으로 필터링)
            objects = await conn.fetch(
                """
                SELECT 
                    os.*,
                    or_ref.object_type,
                    or_ref.game_object_id
                FROM runtime_data.object_states os
                JOIN reference_layer.object_references or_ref
                    ON os.runtime_object_id = or_ref.runtime_object_id
                WHERE or_ref.session_id = (
                    SELECT session_id FROM reference_layer.cell_references 
                    WHERE runtime_cell_id = $1
                )
                """,
                runtime_cell_id
            )
            
            return {
                "cell_id": runtime_cell_id,
                "entities": [dict(entity) for entity in entities],
                "objects": [dict(obj) for obj in objects]
            }

    async def update_entity_cell(self, runtime_entity_id: str, runtime_cell_id: str, position: Dict[str, float]):
        """엔티티의 셀과 위치를 업데이트합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # current_position JSONB에 runtime_cell_id 포함
            position_with_cell = position.copy()
            position_with_cell['runtime_cell_id'] = runtime_cell_id
            await conn.execute(
                """
                UPDATE runtime_data.entity_states
                SET current_position = $1
                WHERE runtime_entity_id = $2
                """,
                json.dumps(position_with_cell), runtime_entity_id
            )

    async def update_entity_state(self, runtime_entity_id: str, properties: Dict[str, Any]):
        """엔티티의 상태를 업데이트합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # JSONB 필드 업데이트
            await conn.execute(
                """
                UPDATE runtime_data.entity_states
                SET properties = properties || $1::jsonb
                WHERE runtime_entity_id = $2
                """,
                json.dumps(properties), runtime_entity_id
            )

    async def update_entity_stats(self, runtime_entity_id: str, stats: Dict[str, Any]):
        """엔티티의 스탯을 업데이트합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE runtime_data.entity_states
                SET current_stats = current_stats || $1::jsonb
                WHERE runtime_entity_id = $2
                """,
                json.dumps(stats), runtime_entity_id
            )

    async def get_active_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """세션 정보를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM runtime_data.active_sessions 
                WHERE session_id = $1
                """, 
                session_id
            )
            return dict(row) if row else None

    async def get_active_sessions_by_player(self, player_runtime_entity_id: str) -> List[Dict[str, Any]]:
        """플레이어의 모든 활성 세션을 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM runtime_data.active_sessions 
                WHERE player_runtime_entity_id = $1 
                AND session_state = 'active'
                """, 
                player_runtime_entity_id
            )
            return [dict(row) for row in rows]

    async def get_entity_state(self, runtime_entity_id: str) -> Optional[Dict[str, Any]]:
        """엔티티의 현재 상태를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM runtime_data.entity_states 
                WHERE runtime_entity_id = $1
                """, 
                runtime_entity_id
            )
            return dict(row) if row else None

    async def get_entity_states_by_cell(self, runtime_cell_id: str) -> List[Dict[str, Any]]:
        """특정 셀에 있는 모든 엔티티의 상태를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT 
                    es.*,
                    er.entity_type,
                    er.game_entity_id,
                    er.is_player
                FROM runtime_data.entity_states es
                JOIN reference_layer.entity_references er 
                    ON es.runtime_entity_id = er.runtime_entity_id
                WHERE es.current_position->>'runtime_cell_id' = $1
                """, 
                runtime_cell_id
            )
            return [dict(row) for row in rows]

    async def get_object_state(self, runtime_object_id: str) -> Optional[Dict[str, Any]]:
        """오브젝트의 현재 상태를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM runtime_data.object_states 
                WHERE runtime_object_id = $1
                """, 
                runtime_object_id
            )
            return dict(row) if row else None

    async def get_triggered_events(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """세션의 최근 이벤트들을 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT 
                    te.*,
                    ser.entity_type as source_type,
                    ser.game_entity_id as source_game_id,
                    ter.entity_type as target_type,
                    ter.game_entity_id as target_game_id
                FROM runtime_data.triggered_events te
                LEFT JOIN reference_layer.entity_references ser 
                    ON te.source_entity_ref = ser.runtime_entity_id
                LEFT JOIN reference_layer.entity_references ter 
                    ON te.target_entity_ref = ter.runtime_entity_id
                WHERE te.session_id = $1
                ORDER BY te.triggered_at DESC
                LIMIT $2
                """, 
                session_id, limit
            )
            return [dict(row) for row in rows]

    async def get_entity_full_state(self, runtime_entity_id: str) -> Optional[Dict[str, Any]]:
        """엔티티의 전체 상태 정보를 조회합니다 (참조 정보 포함)."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT 
                    es.*,
                    er.entity_type,
                    er.game_entity_id,
                    er.session_id,
                    er.is_player
                FROM runtime_data.entity_states es
                JOIN reference_layer.entity_references er 
                    ON es.runtime_entity_id = er.runtime_entity_id
                WHERE es.runtime_entity_id = $1
                """, 
                runtime_entity_id
            )
            return dict(row) if row else None 