from typing import Dict, List, Any, Optional
import json
import uuid
from datetime import datetime
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository

class InstanceManager:
    """엔티티와 셀 인스턴스를 관리하는 클래스"""
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.game_data = GameDataRepository()
        self.runtime_data = RuntimeDataRepository()
        self.reference_layer = ReferenceLayerRepository()
        
        # 인스턴스 캐시
        self._cell_instances = {}
        self._entity_instances = {}

    async def create_cell_instance(self, game_cell_id: str, session_id: str) -> str:
        """셀 인스턴스를 생성합니다."""
        runtime_cell_id = await self.reference_layer.create_cell_reference(
            game_cell_id=game_cell_id,
            session_id=session_id
        )
        
        return runtime_cell_id

    async def create_entity_instance(
        self,
        game_entity_id: str,
        session_id: str,
        runtime_cell_id: str,
        position: Dict[str, float],
        entity_type: str = "npc"
    ) -> str:
        """엔티티 인스턴스를 생성합니다."""
        # 1. 엔티티 참조 생성
        runtime_entity_id = await self.reference_layer.create_entity_reference(
            game_entity_id=game_entity_id,
            session_id=session_id,
            entity_type=entity_type,
            is_player=(entity_type == "player")
        )
        
        # 2. 엔티티 상태 생성
        await self.runtime_data.create_entity_state(
            runtime_entity_id=runtime_entity_id,
            runtime_cell_id=runtime_cell_id,
            position=position
        )
        
        return runtime_entity_id

    async def get_cell_instance(self, runtime_cell_id: str) -> Optional[Dict[str, Any]]:
        """셀 인스턴스 정보를 조회합니다."""
        # 캐시 확인
        if runtime_cell_id in self._cell_instances:
            return self._cell_instances[runtime_cell_id]
        
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # 셀 참조 및 게임 데이터 조회
            cell_info = await conn.fetchrow(
                """
                SELECT 
                    cr.runtime_cell_id,
                    cr.game_cell_id,
                    cr.session_id,
                    wc.cell_name,
                    wc.cell_description,
                    wc.cell_properties
                FROM reference_layer.cell_references cr
                JOIN game_data.world_cells wc ON cr.game_cell_id = wc.cell_id
                WHERE cr.runtime_cell_id = $1
                """,
                runtime_cell_id
            )
            
            if not cell_info:
                return None
            
            # 캐시에 저장
            cell_data = dict(cell_info)
            self._cell_instances[runtime_cell_id] = cell_data
            
            return cell_data

    async def get_entity_instance(self, runtime_entity_id: str) -> Optional[Dict[str, Any]]:
        """엔티티 인스턴스 정보를 조회합니다."""
        # 캐시 확인
        if runtime_entity_id in self._entity_instances:
            return self._entity_instances[runtime_entity_id]
        
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # 엔티티 참조, 상태 및 게임 데이터 조회
            entity_info = await conn.fetchrow(
                """
                SELECT 
                    er.runtime_entity_id,
                    er.game_entity_id,
                    er.entity_type,
                    er.is_player,
                    er.session_id,
                    es.current_position->>'runtime_cell_id' as runtime_cell_id,
                    es.current_position,
                    es.current_stats,
                    es.active_effects,
                    e.entity_name,
                    e.entity_description,
                    e.entity_properties
                FROM reference_layer.entity_references er
                LEFT JOIN runtime_data.entity_states es ON er.runtime_entity_id = es.runtime_entity_id
                LEFT JOIN game_data.entities e ON er.game_entity_id = e.entity_id
                WHERE er.runtime_entity_id = $1
                """,
                runtime_entity_id
            )
            
            if not entity_info:
                return None
            
            # 캐시에 저장
            entity_data = dict(entity_info)
            self._entity_instances[runtime_entity_id] = entity_data
            
            return entity_data

    async def get_instances_in_session(self, session_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """세션에 있는 모든 인스턴스들을 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # 셀 인스턴스들 조회
            cells = await conn.fetch(
                """
                SELECT 
                    cr.runtime_cell_id,
                    cr.game_cell_id,
                    wc.cell_name
                FROM reference_layer.cell_references cr
                JOIN game_data.world_cells wc ON cr.game_cell_id = wc.cell_id
                WHERE cr.session_id = $1
                """,
                session_id
                )

            # 엔티티 인스턴스들 조회
            entities = await conn.fetch(
                    """
                SELECT 
                    er.runtime_entity_id,
                    er.game_entity_id,
                    er.entity_type,
                    er.is_player,
                    es.current_position->>'runtime_cell_id' as runtime_cell_id,
                    es.current_position,
                    e.entity_name
                FROM reference_layer.entity_references er
                LEFT JOIN runtime_data.entity_states es ON er.runtime_entity_id = es.runtime_entity_id
                LEFT JOIN game_data.entities e ON er.game_entity_id = e.entity_id
                WHERE er.session_id = $1
                    """,
                session_id
            )
            
            return {
                'cells': [dict(cell) for cell in cells],
                'entities': [dict(entity) for entity in entities]
            }

    async def move_entity_to_cell(self, runtime_entity_id: str, target_runtime_cell_id: str, new_position: Dict[str, float]) -> bool:
        """엔티티를 다른 셀로 이동시킵니다."""
        try:
            await self.runtime_data.update_entity_cell(
                runtime_entity_id=runtime_entity_id,
                runtime_cell_id=target_runtime_cell_id,
                position=new_position
            )
            return True
        except Exception as e:
            print(f"엔티티 이동 실패: {e}")
            return False

    async def remove_cell_instance(self, runtime_cell_id: str) -> bool:
        """
        셀 인스턴스를 제거합니다.
        
        Args:
            runtime_cell_id: 런타임 셀 ID
            
        Returns:
            제거 성공 여부
        """
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                try:
                    # 1. 셀에 있는 모든 엔티티들 제거
                    await conn.execute(
                        """
                        DELETE FROM runtime_data.entity_states
                        WHERE runtime_cell_id = $1
                        """,
                        runtime_cell_id
                    )
                    
                    await conn.execute(
                        """
                        DELETE FROM reference_layer.entity_references
                        WHERE runtime_entity_id IN (
                            SELECT runtime_entity_id FROM runtime_data.entity_states
                            WHERE runtime_cell_id = $1
                        )
                        """,
                        runtime_cell_id
                    )

                    # 2. 셀 인스턴스 제거
                    await conn.execute(
                        """
                        DELETE FROM reference_layer.cell_references
                        WHERE runtime_cell_id = $1
                        """,
                        runtime_cell_id
                    )
                    
                    # 3. 캐시에서 제거
                    if runtime_cell_id in self._cell_instances:
                        del self._cell_instances[runtime_cell_id]
                    
                    return True
                    
                except Exception as e:
                    print(f"셀 인스턴스 제거 실패: {e}")
                    return False

    async def remove_entity_instance(self, runtime_entity_id: str) -> bool:
        """
        엔티티 인스턴스를 제거합니다.
        
        Args:
            runtime_entity_id: 런타임 엔티티 ID
            
        Returns:
            제거 성공 여부
        """
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                try:
                    # 1. 엔티티 상태 삭제
                    await conn.execute(
                        """
                        DELETE FROM runtime_data.entity_states
                        WHERE runtime_entity_id = $1
                        """,
                        runtime_entity_id
                    )

                    # 2. 엔티티 참조 삭제
                    await conn.execute(
                        """
                        DELETE FROM reference_layer.entity_references
                        WHERE runtime_entity_id = $1
                        """,
                        runtime_entity_id
                    )
                    
                    # 3. 캐시에서 제거
                    if runtime_entity_id in self._entity_instances:
                        del self._entity_instances[runtime_entity_id]
                    
                    return True
                    
                except Exception as e:
                    print(f"엔티티 인스턴스 제거 실패: {e}")
                    return False

    async def cleanup_session_instances(self, session_id: str) -> bool:
        """
        세션의 모든 인스턴스들을 정리합니다.
        
        Args:
            session_id: 세션 ID
            
        Returns:
            정리 성공 여부
        """
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                try:
                    # 1. 세션의 모든 엔티티 상태 삭제
                    await conn.execute(
                        """
                        DELETE FROM runtime_data.entity_states
                        WHERE runtime_entity_id IN (
                            SELECT runtime_entity_id FROM reference_layer.entity_references
                            WHERE session_id = $1
                        )
                        """,
                        session_id
                    )

                    # 2. 세션의 모든 엔티티 참조 삭제
                    await conn.execute(
                        """
                        DELETE FROM reference_layer.entity_references
                        WHERE session_id = $1
                        """,
                        session_id
                    )

                    # 3. 세션의 모든 셀 참조 삭제
                    await conn.execute(
                        """
                        DELETE FROM reference_layer.cell_references
                        WHERE session_id = $1
                        """,
                        session_id
                    ) 
                    
                    # 4. 캐시 정리
                    self._cell_instances.clear()
                    self._entity_instances.clear()
                    
                    return True
                    
                except Exception as e:
                    print(f"세션 인스턴스 정리 실패: {e}")
                    return False

    async def get_cell_entities(self, runtime_cell_id: str) -> List[Dict[str, Any]]:
        """특정 셀에 있는 모든 엔티티들을 조회합니다."""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT 
                    er.runtime_entity_id,
                    er.game_entity_id,
                    er.entity_type,
                    er.is_player,
                    es.current_position,
                    es.current_stats,
                    e.entity_name
                FROM reference_layer.entity_references er
                LEFT JOIN runtime_data.entity_states es ON er.runtime_entity_id = es.runtime_entity_id
                LEFT JOIN game_data.entities e ON er.game_entity_id = e.entity_id
                WHERE es.current_position->>'runtime_cell_id' = $1
                ORDER BY er.is_player DESC, er.entity_type
                """,
                runtime_cell_id
            )
            
            return [dict(row) for row in rows]

    async def update_instance_cache(self, instance_type: str, instance_id: str):
        """
        인스턴스 캐시를 업데이트합니다.
        
        Args:
            instance_type: 인스턴스 타입 ('cell' 또는 'entity')
            instance_id: 인스턴스 ID
        """
        if instance_type == 'cell':
            if instance_id in self._cell_instances:
                del self._cell_instances[instance_id]
        elif instance_type == 'entity':
            if instance_id in self._entity_instances:
                del self._entity_instances[instance_id] 