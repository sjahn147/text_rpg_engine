from typing import Optional, Dict, Any, List, Tuple
import uuid
from datetime import datetime
import json
import copy

from ..connection import DatabaseConnection
from ..repositories.game_data import GameDataRepository
from ..repositories.reference_layer import ReferenceLayerRepository
from ..repositories.runtime_data import RuntimeDataRepository

class InstanceFactory:
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        self.db = db_connection or DatabaseConnection()
        self.game_data = GameDataRepository(self.db)
        self.reference_layer = ReferenceLayerRepository(self.db)
        self.runtime_data = RuntimeDataRepository(self.db)

    async def create_npc_instance(
        self,
        game_entity_id: str,
        session_id: str,
        runtime_cell_id: str,
        position: Dict[str, float],
        customization: Dict[str, Any] = None
    ) -> str:
        """
        NPC 템플릿으로부터 런타임 인스턴스를 생성합니다.
        
        Args:
            game_entity_id: 게임 데이터의 NPC 템플릿 ID
            session_id: 세션 ID
            runtime_cell_id: 배치될 셀의 런타임 ID
            position: 초기 위치 {"x": float, "y": float, "z": float}
            customization: 커스터마이징 속성 (선택사항)
        """
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                # 1. 게임 데이터에서 템플릿 로드
                template = await self.game_data.get_entity(game_entity_id)
                if not template:
                    raise ValueError(f"Template not found: {game_entity_id}")

                # 2. 속성 복사 및 커스터마이징
                properties = copy.deepcopy(json.loads(template['entity_properties']))
                if customization:
                    self._deep_update(properties, customization)

                # 3. 참조 레이어에 등록
                runtime_entity_id = str(uuid.uuid4())
                await conn.execute(
                    """
                    INSERT INTO reference_layer.entity_references 
                    (runtime_entity_id, game_entity_id, session_id, entity_type, is_player)
                    VALUES ($1, $2, $3, 'npc', FALSE)
                    """,
                    runtime_entity_id, game_entity_id, session_id
                )

                # 3-1. runtime_entities 테이블에 등록 (외래키 제약조건을 위해 필요)
                await conn.execute(
                    """
                    INSERT INTO runtime_data.runtime_entities 
                    (runtime_entity_id, game_entity_id, session_id)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (runtime_entity_id) DO NOTHING
                    """,
                    runtime_entity_id, game_entity_id, session_id
                )

                # 4. 런타임 상태 초기화
                base_stats = json.loads(template['base_stats'])
                # current_position에 셀 정보 포함
                position_with_cell = position.copy()
                position_with_cell['runtime_cell_id'] = runtime_cell_id
                await conn.execute(
                    """
                    INSERT INTO runtime_data.entity_states 
                    (runtime_entity_id, current_stats, 
                     current_position, active_effects, inventory, equipped_items)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    runtime_entity_id,
                    json.dumps(base_stats),
                    json.dumps(position_with_cell),
                    json.dumps([]),  # 초기에는 활성 효과 없음
                    json.dumps(properties.get('initial_inventory', {"items": []})),
                    json.dumps(properties.get('initial_equipment', {"equipped": []}))
                )

                return runtime_entity_id

    async def create_player_instance(
        self,
        game_entity_id: str,
        session_id: str,
        runtime_cell_id: str,
        position: Dict[str, float],
        customization: Dict[str, Any] = None
    ) -> str:
        """
        플레이어 템플릿으로부터 런타임 인스턴스를 생성합니다.
        
        Args:
            game_entity_id: 게임 데이터의 플레이어 템플릿 ID
            session_id: 세션 ID
            runtime_cell_id: 배치될 셀의 런타임 ID
            position: 초기 위치 {"x": float, "y": float, "z": float}
            customization: 커스터마이징 속성 (선택사항)
        """
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                # 1. 게임 데이터에서 템플릿 로드
                template = await self.game_data.get_entity(game_entity_id)
                if not template:
                    raise ValueError(f"Template not found: {game_entity_id}")

                # 2. 속성 복사 및 커스터마이징
                properties = copy.deepcopy(json.loads(template['entity_properties']))
                if customization:
                    self._deep_update(properties, customization)

                # 3. 참조 레이어에 등록
                runtime_entity_id = str(uuid.uuid4())
                await conn.execute(
                    """
                    INSERT INTO reference_layer.entity_references 
                    (runtime_entity_id, game_entity_id, session_id, entity_type, is_player)
                    VALUES ($1, $2, $3, 'player', TRUE)
                    """,
                    runtime_entity_id, game_entity_id, session_id
                )

                # 3-1. runtime_entities 테이블에 등록 (외래키 제약조건을 위해 필요)
                await conn.execute(
                    """
                    INSERT INTO runtime_data.runtime_entities 
                    (runtime_entity_id, game_entity_id, session_id)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (runtime_entity_id) DO NOTHING
                    """,
                    runtime_entity_id, game_entity_id, session_id
                )

                # 4. 런타임 상태 초기화
                base_stats = json.loads(template['base_stats'])
                # current_position에 셀 정보 포함
                position_with_cell = position.copy()
                position_with_cell['runtime_cell_id'] = runtime_cell_id
                await conn.execute(
                    """
                    INSERT INTO runtime_data.entity_states 
                    (runtime_entity_id, current_stats, 
                     current_position, active_effects, inventory, equipped_items)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    runtime_entity_id,
                    json.dumps(base_stats),
                    json.dumps(position_with_cell),
                    json.dumps([]),  # 초기에는 활성 효과 없음
                    json.dumps(properties.get('initial_inventory', {"items": []})),
                    json.dumps(properties.get('initial_equipment', {"equipped": []}))
                )

                return runtime_entity_id

    async def create_item_instance(
        self,
        game_item_id: str,
        session_id: str,
        owner_runtime_id: Optional[str] = None,
        customization: Dict[str, Any] = None
    ) -> str:
        """
        아이템 템플릿으로부터 런타임 인스턴스를 생성합니다.
        
        Args:
            game_item_id: 게임 데이터의 아이템 템플릿 ID
            session_id: 세션 ID
            owner_runtime_id: 소유자의 런타임 ID (선택사항)
            customization: 커스터마이징 속성 (선택사항)
        """
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                # 1. 게임 데이터에서 템플릿 로드
                template = await self.game_data.get_item(game_item_id)
                if not template:
                    raise ValueError(f"Template not found: {game_item_id}")

                # 2. 속성 복사 및 커스터마이징
                properties = copy.deepcopy(json.loads(template['item_properties']))
                if customization:
                    self._deep_update(properties, customization)

                # 3. 참조 레이어에 등록
                runtime_object_id = str(uuid.uuid4())
                await conn.execute(
                    """
                    INSERT INTO reference_layer.object_references 
                    (runtime_object_id, game_object_id, session_id, object_type)
                    VALUES ($1, $2, $3, 'item')
                    """,
                    runtime_object_id, game_item_id, session_id
                )

                # 4. 런타임 상태 초기화
                state = {
                    "condition": 100,  # 내구도
                    "owner_id": owner_runtime_id,
                    "properties": properties
                }

                await conn.execute(
                    """
                    INSERT INTO runtime_data.object_states 
                    (runtime_object_id, current_state)
                    VALUES ($1, $2)
                    """,
                    runtime_object_id, json.dumps(state)
                )

                return runtime_object_id

    async def create_effect_instance(
        self,
        game_effect_id: str,
        session_id: str,
        target_runtime_id: str,
        customization: Dict[str, Any] = None
    ) -> str:
        """
        효과 템플릿으로부터 런타임 인스턴스를 생성합니다.
        
        Args:
            game_effect_id: 게임 데이터의 효과 템플릿 ID
            session_id: 세션 ID
            target_runtime_id: 효과가 적용될 대상의 런타임 ID
            customization: 커스터마이징 속성 (선택사항)
        """
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                # 1. 게임 데이터에서 템플릿 로드
                template = await self.game_data.get_effect(game_effect_id)
                if not template:
                    raise ValueError(f"Template not found: {game_effect_id}")

                # 2. 속성 복사 및 커스터마이징
                properties = copy.deepcopy(json.loads(template['effect_properties']))
                if customization:
                    self._deep_update(properties, customization)

                # 3. 효과 인스턴스 생성 및 적용
                properties.update({
                    "applied_at": datetime.utcnow().isoformat(),
                    "target_id": target_runtime_id
                })

                # 4. 대상 엔티티의 active_effects에 추가
                await conn.execute(
                    """
                    UPDATE runtime_data.entity_states
                    SET active_effects = active_effects || $1::jsonb
                    WHERE runtime_entity_id = $2
                    """,
                    json.dumps([properties]), target_runtime_id
                )

                return properties['applied_at']

    async def create_cell_instance(
        self,
        game_cell_id: str,
        session_id: str,
        customization: Dict[str, Any] = None
    ) -> str:
        """
        셀 템플릿으로부터 런타임 인스턴스를 생성합니다.
        
        Args:
            game_cell_id: 게임 데이터의 셀 템플릿 ID
            session_id: 세션 ID
            customization: 커스터마이징 속성 (선택사항)
        """
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                # 1. 게임 데이터에서 템플릿 로드
                template = await self.game_data.get_world_cell(game_cell_id)
                if not template:
                    raise ValueError(f"Cell template not found: {game_cell_id}")

                # 2. 속성 복사 및 커스터마이징
                properties = copy.deepcopy(json.loads(template['cell_properties']) if template['cell_properties'] else {})
                if customization:
                    self._deep_update(properties, customization)

                # 3. 참조 레이어에 등록
                runtime_cell_id = str(uuid.uuid4())
                # cell_type은 템플릿에서 가져오거나 기본값 사용
                cell_type = template.get('cell_type') or 'indoor'
                await conn.execute(
                    """
                    INSERT INTO reference_layer.cell_references
                    (runtime_cell_id, game_cell_id, session_id, cell_type)
                    VALUES ($1, $2, $3, $4)
                    """,
                    runtime_cell_id, game_cell_id, session_id, cell_type
                )

                return runtime_cell_id

    def _deep_update(self, base: Dict, update: Dict):
        """딕셔너리를 재귀적으로 업데이트합니다."""
        for key, value in update.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value 