from typing import Optional, List, Dict, Any
import asyncpg
import json
from ..connection import DatabaseConnection

class GameDataRepository:
    def __init__(self, db_connection=None):
        self.db = db_connection or DatabaseConnection()

    async def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """엔티티 정보를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM game_data.entities 
                WHERE entity_id = $1
                """, 
                entity_id
            )
            return dict(row) if row else None

    async def get_entities_by_type(self, entity_type: str) -> List[Dict[str, Any]]:
        """특정 타입의 모든 엔티티를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM game_data.entities 
                WHERE entity_type = $1
                """, 
                entity_type
            )
            return [dict(row) for row in rows]

    async def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """아이템 정보를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # game_data.items 테이블 조회 (스키마에 맞게)
            row = await conn.fetchrow(
                """
                SELECT * FROM game_data.items 
                WHERE item_id = $1
                """, 
                item_id
            )
            return dict(row) if row else None

    async def get_effect(self, effect_id: str) -> Optional[Dict[str, Any]]:
        """효과 정보를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM game_data.effects 
                WHERE effect_id = $1
                """, 
                effect_id
            )
            return dict(row) if row else None

    async def create_event(self, event_data: Dict[str, Any]) -> str:
        """이벤트를 생성합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO game_data.events
                (event_id, name, type, properties, created_at, updated_at)
                VALUES ($1, $2, $3, $4, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """,
                event_data['event_id'],
                event_data['name'],
                event_data['type'],
                event_data['properties']
            )
            return event_data['event_id']

    async def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """이벤트 정보를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM game_data.events 
                WHERE event_id = $1
                """, 
                event_id
            )
            return dict(row) if row else None

    async def get_events_by_type(self, event_type: str) -> List[Dict[str, Any]]:
        """특정 타입의 모든 이벤트를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM game_data.events 
                WHERE type = $1
                """, 
                event_type
            )
            return [dict(row) for row in rows]

    async def get_world_region(self, region_id: str) -> Optional[Dict[str, Any]]:
        """특정 월드 지역의 정보를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM game_data.world_regions 
                WHERE region_id = $1
                """, 
                region_id
            )
            return dict(row) if row else None

    async def get_world_regions_by_type(self, region_type: str) -> List[Dict[str, Any]]:
        """특정 타입의 월드 지역들을 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM game_data.world_regions 
                WHERE type = $1
                """, 
                region_type
            )
            return [dict(row) for row in rows]

    async def get_world_location(self, location_id: str) -> Optional[Dict[str, Any]]:
        """특정 월드 위치의 정보를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM game_data.world_locations 
                WHERE location_id = $1
                """, 
                location_id
            )
            return dict(row) if row else None

    async def get_world_cell(self, cell_id: str) -> Optional[Dict[str, Any]]:
        """특정 월드 셀의 정보를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM game_data.world_cells 
                WHERE cell_id = $1
                """, 
                cell_id
            )
            return dict(row) if row else None

    async def get_cells_by_location(self, location_id: str) -> List[Dict[str, Any]]:
        """특정 위치의 모든 셀을 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM game_data.world_cells 
                WHERE location_id = $1
                ORDER BY x_coord, y_coord, z_coord
                """, 
                location_id
            )
            return [dict(row) for row in rows]

    async def get_base_property(self, property_id: str) -> Optional[Dict[str, Any]]:
        """기본 속성 정보를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM game_data.base_properties 
                WHERE property_id = $1
                """, 
                property_id
            )
            return dict(row) if row else None

    async def get_magic_ability(self, magic_id: str) -> Optional[Dict[str, Any]]:
        """마법 능력 정보를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT 
                    m.*,
                    b.name as base_name,
                    b.base_effects,
                    b.requirements
                FROM game_data.abilities_magic m
                JOIN game_data.base_properties b ON m.base_property_id = b.property_id
                WHERE magic_id = $1
                """, 
                magic_id
            )
            return dict(row) if row else None

    async def get_skill_ability(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """스킬 능력 정보를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT 
                    s.*,
                    b.name as base_name,
                    b.base_effects,
                    b.requirements
                FROM game_data.abilities_skills s
                JOIN game_data.base_properties b ON s.base_property_id = b.property_id
                WHERE skill_id = $1
                """, 
                skill_id
            )
            return dict(row) if row else None

    async def get_abilities_by_type(self, ability_type: str) -> List[Dict[str, Any]]:
        """특정 타입의 모든 능력을 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            if ability_type == 'magic':
                rows = await conn.fetch(
                    """
                    SELECT 
                        m.*,
                        b.name as base_name,
                        b.base_effects,
                        b.requirements
                    FROM game_data.abilities_magic m
                    JOIN game_data.base_properties b ON m.base_property_id = b.property_id
                    """
                )
            else:  # skill
                rows = await conn.fetch(
                    """
                    SELECT 
                        s.*,
                        b.name as base_name,
                        b.base_effects,
                        b.requirements
                    FROM game_data.abilities_skills s
                    JOIN game_data.base_properties b ON s.base_property_id = b.property_id
                    """
                )
            return [dict(row) for row in rows]

    async def get_dialogue_contexts(self, entity_id: str) -> List[Dict[str, Any]]:
        """엔티티의 대화 컨텍스트를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM game_data.dialogue_contexts
                WHERE entity_id = $1
                ORDER BY priority DESC
                """,
                entity_id
            )
            return [dict(row) for row in rows]

    async def get_dialogue_context_by_title(self, entity_id: str, title: str) -> Optional[Dict[str, Any]]:
        """특정 제목의 대화 컨텍스트를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM game_data.dialogue_contexts
                WHERE entity_id = $1 AND title LIKE $2
                ORDER BY priority DESC
                LIMIT 1
                """,
                entity_id, f"%{title}%"
            )
            return dict(row) if row else None

    async def get_dialogue_context_by_id(self, dialogue_id: str) -> Optional[Dict[str, Any]]:
        """대화 컨텍스트 ID로 대화 컨텍스트를 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM game_data.dialogue_contexts
                WHERE dialogue_id = $1
                """,
                dialogue_id
            )
            return dict(row) if row else None 