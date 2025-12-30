"""
엔티티 관리 모듈
"""
from typing import Dict, List, Optional, Any, Tuple
import uuid
import asyncio
import json
from datetime import datetime
from common.utils.jsonb_handler import parse_jsonb_data, serialize_jsonb_data
from common.utils.error_handler import handle_database_error, handle_validation_error, validate_session_id, validate_entity_id
from common.utils.schema_validator import SchemaValidator
from enum import Enum
from pydantic import BaseModel, Field
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from app.managers.effect_carrier_manager import EffectCarrierManager
from common.utils.logger import logger


class EntityType(str, Enum):
    """엔티티 타입 열거형"""
    PLAYER = "player"
    NPC = "npc"
    MONSTER = "monster"
    ENEMY = "enemy"
    OBJECT = "object"


class EntityStatus(str, Enum):
    """엔티티 상태 열거형"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEAD = "dead"
    HIDDEN = "hidden"


class EntityData(BaseModel):
    """엔티티 데이터 모델"""
    entity_id: str = Field(..., description="엔티티 고유 ID")
    name: str = Field(..., min_length=1, max_length=100, description="엔티티 이름")
    entity_type: EntityType = Field(..., description="엔티티 타입")
    status: EntityStatus = Field(default=EntityStatus.ACTIVE, description="엔티티 상태")
    properties: Dict[str, Any] = Field(default_factory=dict, description="엔티티 속성")
    position: Optional[Dict[str, float]] = Field(default=None, description="위치 정보")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    updated_at: datetime = Field(default_factory=datetime.now, description="수정 시간")
    
    class Config:
        use_enum_values = True
        validate_assignment = True


class EntityCreationStatus(str, Enum):
    """엔티티 생성 상태 열거형"""
    SUCCESS = "success"
    ERROR = "error"
    VALIDATION_ERROR = "validation_error"
    DATABASE_ERROR = "database_error"
    TEMPLATE_NOT_FOUND = "template_not_found"

class EntityCreationResult(BaseModel):
    """엔티티 생성 결과 모델 - 명확한 반환 타입과 일관성"""
    status: EntityCreationStatus = Field(..., description="생성 상태")
    entity_id: Optional[str] = Field(default=None, description="생성된 엔티티 ID")
    entity_data: Optional[EntityData] = Field(default=None, description="엔티티 데이터")
    message: str = Field(..., description="결과 메시지")
    error_code: Optional[str] = Field(default=None, description="에러 코드")
    
    @classmethod
    def success(cls, entity_id: str, entity_data: EntityData, message: str = "엔티티 생성 성공") -> "EntityCreationResult":
        return cls(
            status=EntityCreationStatus.SUCCESS,
            entity_id=entity_id,
            entity_data=entity_data,
            message=message
        )
    
    @classmethod
    def error(cls, message: str, error_code: str = "UNKNOWN_ERROR") -> "EntityCreationResult":
        return cls(
            status=EntityCreationStatus.ERROR,
            message=message,
            error_code=error_code
        )

class EntityResult(BaseModel):
    """엔티티 작업 결과 모델 - 기존 호환성 유지"""
    success: bool = Field(..., description="작업 성공 여부")
    entity: Optional[EntityData] = Field(default=None, description="엔티티 데이터")
    message: str = Field(default="", description="결과 메시지")
    error: Optional[str] = Field(default=None, description="에러 메시지")
    
    @classmethod
    def success_result(cls, entity: EntityData, message: str = "Success") -> "EntityResult":
        """성공 결과 생성"""
        return cls(success=True, entity=entity, message=message)
    
    @classmethod
    def error_result(cls, message: str, error: str = None) -> "EntityResult":
        """에러 결과 생성"""
        return cls(success=False, message=message, error=error)


class EntityManager:
    """엔티티 관리 클래스"""
    
    def __init__(self, 
                 db_connection: DatabaseConnection,
                 game_data_repo: GameDataRepository,
                 runtime_data_repo: RuntimeDataRepository,
                 reference_layer_repo: ReferenceLayerRepository,
                 effect_carrier_manager: Optional[EffectCarrierManager] = None):
        """
        EntityManager 초기화
        
        Args:
            db_connection: 데이터베이스 연결
            game_data_repo: 게임 데이터 저장소
            runtime_data_repo: 런타임 데이터 저장소
            reference_layer_repo: 참조 레이어 저장소
            effect_carrier_manager: Effect Carrier 관리자 (선택사항)
        """
        self.db = db_connection
        self.game_data = game_data_repo
        self.runtime_data = runtime_data_repo
        self.reference_layer = reference_layer_repo
        self.effect_carrier_manager = effect_carrier_manager
        self.logger = logger
        
        # 엔티티 캐시
        self._entity_cache: Dict[str, EntityData] = {}
        self._cache_lock = asyncio.Lock()
        
        # 스키마 검증기
        self._schema_validator = SchemaValidator(db_connection)
    
    async def create_entity(self, 
                          static_entity_id: str,
                          session_id: str,
                          custom_properties: Dict[str, Any] = None,
                          custom_position: Dict[str, float] = None) -> EntityCreationResult:
        """
        정적 엔티티 템플릿에서 런타임 엔티티 인스턴스 생성
        
        Args:
            static_entity_id: 정적 엔티티 템플릿 ID (NPC_* 패턴)
            session_id: 세션 ID
            custom_properties: 커스텀 속성 (선택사항)
            custom_position: 커스텀 위치 (선택사항)
            
        Returns:
            EntityCreationResult: 생성 결과
        """
        try:
            # 입력 검증
            if not validate_entity_id(static_entity_id):
                return EntityCreationResult.error(
                    message=f"유효하지 않은 엔티티 ID 형식: {static_entity_id}",
                    error_code="VALIDATION_ERROR"
                )
            
            if not validate_session_id(session_id):
                return EntityCreationResult.error(
                    message=f"유효하지 않은 세션 ID 형식: {session_id}",
                    error_code="VALIDATION_ERROR"
                )
            
            # 정적 엔티티 템플릿 조회
            template_result = await self.db.execute_query("""
                SELECT entity_id, entity_type, entity_name, entity_description, 
                       base_stats, default_equipment, default_abilities, 
                       default_inventory, entity_properties
                FROM game_data.entities 
                WHERE entity_id = $1
            """, static_entity_id)
            
            if not template_result:
                return EntityCreationResult.error(
                    message=f"정적 엔티티 템플릿을 찾을 수 없습니다: {static_entity_id}",
                    error_code="TEMPLATE_NOT_FOUND"
                )
            
            template = template_result[0]
            
            # 런타임 엔티티 인스턴스 ID 생성 (UUID)
            runtime_entity_id = str(uuid.uuid4())
            
            # 먼저 세션 생성 (존재하지 않는 경우)
            await self.db.execute_query("""
                INSERT INTO runtime_data.active_sessions 
                (session_id, session_name, session_state, created_at, updated_at)
                VALUES ($1, $2, $3, NOW(), NOW())
                ON CONFLICT (session_id) DO NOTHING
            """, 
            session_id,
            f"Session {session_id[:8]}",
            "active"
            )
            
            # 런타임 엔티티 인스턴스를 runtime_data.runtime_entities에 매핑만 저장
            await self.db.execute_query("""
                INSERT INTO runtime_data.runtime_entities 
                (runtime_entity_id, game_entity_id, session_id, created_at, updated_at)
                VALUES ($1, $2, $3, NOW(), NOW())
            """, 
            runtime_entity_id,
            static_entity_id,
            session_id
            )
            
            # reference_layer에 매핑 저장
            await self.db.execute_query("""
                INSERT INTO reference_layer.entity_references 
                (runtime_entity_id, game_entity_id, session_id, entity_type, is_player, created_at)
                VALUES ($1, $2, $3, $4, $5, NOW())
            """, 
            runtime_entity_id, 
            static_entity_id, 
            session_id, 
            template["entity_type"],
            template["entity_type"] == "player"
            )
            
            # JSONB 데이터 파싱 (통일된 처리)
            base_stats = parse_jsonb_data(template["base_stats"])
            entity_properties = parse_jsonb_data(template["entity_properties"])
            
            # 커스텀 속성 병합
            final_properties = base_stats.copy() if base_stats else {}
            if custom_properties:
                final_properties.update(custom_properties)
            
            # 엔티티 데이터 생성 (정적 템플릿 정보 사용)
            entity_data = EntityData(
                entity_id=runtime_entity_id,
                name=template["entity_name"],
                entity_type=EntityType(template["entity_type"]),
                properties=final_properties,
                position=custom_position or {"x": 0.0, "y": 0.0}
            )
            
            # entity_states 테이블에 초기 상태 저장 (MVP 스키마 준수)
            await self.db.execute_query("""
                INSERT INTO runtime_data.entity_states 
                (runtime_entity_id, session_id, current_stats, current_position, active_effects, inventory, equipped_items, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
            """, 
            runtime_entity_id,
            session_id,
            serialize_jsonb_data(base_stats or {}),
            serialize_jsonb_data(custom_position or {"x": 0.0, "y": 0.0}),
            serialize_jsonb_data([]),  # active_effects
            serialize_jsonb_data([]),  # inventory
            serialize_jsonb_data([])   # equipped_items
            )
            
            # 캐시에 추가
            async with self._cache_lock:
                self._entity_cache[runtime_entity_id] = entity_data
            
            return EntityCreationResult.success(
                entity_id=runtime_entity_id,
                entity_data=entity_data,
                message=f"런타임 엔티티 인스턴스 '{template['entity_name']}' 생성 완료"
            )
            
        except Exception as e:
            # 개선된 에러 처리
            if "database" in str(e).lower() or "connection" in str(e).lower():
                db_error = handle_database_error(e, "create_entity", "game_data.entities")
                self.logger.error(f"Database error in create_entity: {db_error.message}")
                return EntityCreationResult.error(
                    message=db_error.message,
                    error_code="DATABASE_ERROR"
                )
            else:
                self.logger.error(f"Unexpected error in create_entity: {str(e)}")
                return EntityCreationResult.error(
                    message=f"런타임 엔티티 인스턴스 생성 실패: {str(e)}",
                    error_code="UNKNOWN_ERROR"
                )
    
    async def get_entity(self, entity_id: str) -> EntityResult:
        """
        엔티티 조회
        
        Args:
            entity_id: 엔티티 ID
            
        Returns:
            EntityResult: 조회 결과
        """
        try:
            # 캐시에서 먼저 확인
            async with self._cache_lock:
                if entity_id in self._entity_cache:
                    entity = self._entity_cache[entity_id]
                    return EntityResult.success_result(entity, "캐시에서 조회")
            
            # 데이터베이스에서 조회
            entity_data = await self._load_entity_from_db(entity_id)
            
            if not entity_data:
                return EntityResult.error_result(f"엔티티 '{entity_id}'를 찾을 수 없습니다.")
            
            # 캐시에 추가
            async with self._cache_lock:
                self._entity_cache[entity_id] = entity_data
            
            return EntityResult.success_result(entity_data, "데이터베이스에서 조회")
            
        except Exception as e:
            return EntityResult.error_result(
                f"엔티티 조회 실패: {str(e)}",
                str(e)
            )
    
    async def update_entity(self, 
                          entity_id: str, 
                          updates: Dict[str, Any]) -> EntityResult:
        """
        엔티티 업데이트
        
        Args:
            entity_id: 엔티티 ID
            updates: 업데이트할 속성들
            
        Returns:
            EntityResult: 업데이트 결과
        """
        try:
            # 기존 엔티티 조회
            get_result = await self.get_entity(entity_id)
            if not get_result.success:
                return get_result
            
            entity = get_result.entity
            
            # 업데이트 적용
            updated_properties = entity.properties.copy()
            updated_properties.update(updates)
            
            # 업데이트된 엔티티 생성
            updated_entity = EntityData(
                entity_id=entity.entity_id,
                name=entity.name,
                entity_type=entity.entity_type,
                status=entity.status,
                properties=updated_properties,
                position=entity.position,
                created_at=entity.created_at,
                updated_at=datetime.now()
            )
            
            # 데이터베이스에 저장
            await self._save_entity_to_db(updated_entity)
            
            # 캐시 업데이트
            async with self._cache_lock:
                self._entity_cache[entity_id] = updated_entity
            
            return EntityResult.success_result(
                updated_entity,
                f"엔티티 '{entity.name}' 업데이트 완료"
            )
            
        except Exception as e:
            return EntityResult.error_result(
                f"엔티티 업데이트 실패: {str(e)}",
                str(e)
            )
    
    async def delete_entity(self, entity_id: str) -> EntityResult:
        """
        엔티티 삭제 (비활성화)
        
        Args:
            entity_id: 엔티티 ID
            
        Returns:
            EntityResult: 삭제 결과
        """
        try:
            # 엔티티 조회
            get_result = await self.get_entity(entity_id)
            if not get_result.success:
                return get_result
            
            entity = get_result.entity
            
            # 데이터베이스에서 실제 삭제
            await self._delete_entity_from_db(entity_id)
            
            # 캐시에서 제거
            async with self._cache_lock:
                if entity_id in self._entity_cache:
                    del self._entity_cache[entity_id]
            
            # 삭제된 엔티티의 상태를 INACTIVE로 설정
            deleted_entity = EntityData(
                entity_id=entity.entity_id,
                name=entity.name,
                entity_type=entity.entity_type,
                status=EntityStatus.INACTIVE,
                properties=entity.properties,
                position=entity.position,
                created_at=entity.created_at,
                updated_at=entity.updated_at
            )
            
            return EntityResult.success_result(
                deleted_entity,
                f"엔티티 '{entity.name}' 삭제 완료"
            )
            
        except Exception as e:
            return EntityResult.error_result(
                f"엔티티 삭제 실패: {str(e)}",
                str(e)
            )
    
    async def list_entities(self, 
                          entity_type: Optional[EntityType] = None,
                          status: Optional[EntityStatus] = None) -> List[EntityData]:
        """
        엔티티 목록 조회
        
        Args:
            entity_type: 필터링할 엔티티 타입
            status: 필터링할 상태
            
        Returns:
            List[EntityData]: 엔티티 목록
        """
        try:
            # 데이터베이스에서 조회
            entities = await self._load_entities_from_db(entity_type, status)
            
            # 캐시 업데이트
            async with self._cache_lock:
                for entity in entities:
                    self._entity_cache[entity.entity_id] = entity
            
            return entities
            
        except Exception as e:
            print(f"엔티티 목록 조회 실패: {str(e)}")
            return []
    
    
    async def _load_entity_from_db(self, entity_id: str) -> Optional[EntityData]:
        """데이터베이스에서 엔티티 로드 (런타임 엔티티 인스턴스)"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # 런타임 엔티티와 정적 템플릿을 조인하여 조회
                row = await conn.fetchrow("""
                SELECT 
                        re.runtime_entity_id,
                        re.game_entity_id,
                        re.session_id,
                        e.entity_name,
                        e.entity_type,
                        e.base_stats,
                        e.entity_properties,
                        re.created_at,
                        re.updated_at
                    FROM runtime_data.runtime_entities re
                    JOIN game_data.entities e ON re.game_entity_id = e.entity_id
                    WHERE re.runtime_entity_id = $1
                """, entity_id)
                
                if not row:
                    return None

                # JSONB 데이터 처리 (통일된 처리)
                base_stats = parse_jsonb_data(row['base_stats'])
                entity_properties = parse_jsonb_data(row['entity_properties'])
                
                position = entity_properties.get('position') if entity_properties else None
                
                return EntityData(
                    entity_id=row['runtime_entity_id'],
                    name=row['entity_name'],
                    entity_type=EntityType(row['entity_type']),
                    status=EntityStatus.ACTIVE,  # 기본값
                    properties=base_stats or {},
                    position=position,
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
        except Exception as e:
            self.logger.error(f"Failed to load entity from database: {str(e)}")
            return None
    
    async def _load_entities_from_db(self, 
                                   entity_type: Optional[EntityType] = None,
                                   status: Optional[EntityStatus] = None) -> List[EntityData]:
        """데이터베이스에서 엔티티 목록 로드 (런타임 엔티티 인스턴스)"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                query = """
                    SELECT 
                        re.runtime_entity_id,
                        re.game_entity_id,
                        re.session_id,
                        e.entity_name,
                        e.entity_type,
                        e.base_stats,
                        e.entity_properties,
                        re.created_at,
                        re.updated_at
                    FROM runtime_data.runtime_entities re
                    JOIN game_data.entities e ON re.game_entity_id = e.entity_id
                    WHERE 1=1
                """
                params = []
                
                if entity_type:
                    query += " AND e.entity_type = $" + str(len(params) + 1)
                    params.append(entity_type.value)
                
                query += " ORDER BY re.created_at DESC"
                
                rows = await conn.fetch(query, *params)
                
                entities = []
                for row in rows:
                    # JSONB 데이터 처리 (통일된 처리)
                    base_stats = parse_jsonb_data(row['base_stats'])
                    entity_properties = parse_jsonb_data(row['entity_properties'])
                    
                    position = entity_properties.get('position') if entity_properties else None
                    
                    entity = EntityData(
                        entity_id=row['runtime_entity_id'],
                        name=row['entity_name'],
                        entity_type=EntityType(row['entity_type']),
                        status=EntityStatus.ACTIVE,  # 기본값
                        properties=base_stats or {},
                position=position,
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    )
                    entities.append(entity)
                
                return entities
        except Exception as e:
            self.logger.error(f"Failed to load entities from database: {str(e)}")
            return []
    
    async def apply_effect_carrier(self, entity_id: str, effect_id: str, session_id: str) -> EntityResult:
        """엔티티에 Effect Carrier 적용"""
        try:
            if not self.effect_carrier_manager:
                return EntityResult.error_result("Effect Carrier Manager가 설정되지 않았습니다")
            
            # Effect Carrier 부여
            effect_result = await self.effect_carrier_manager.grant_effect_to_entity(
                session_id, entity_id, effect_id
            )
            
            if not effect_result.success:
                return EntityResult.error_result(f"Effect Carrier 적용 실패: {effect_result.message}")
            
            self.logger.info(f"Effect Carrier '{effect_id}'를 엔티티 '{entity_id}'에 적용 완료")
            return EntityResult.success_result(
                f"Effect Carrier '{effect_id}' 적용 완료"
            )
            
        except Exception as e:
            self.logger.error(f"Effect Carrier 적용 실패: {str(e)}")
            return EntityResult.error_result(f"Effect Carrier 적용 실패: {str(e)}")
    
    async def remove_effect_carrier(self, entity_id: str, effect_id: str, session_id: str) -> EntityResult:
        """엔티티에서 Effect Carrier 제거"""
        try:
            if not self.effect_carrier_manager:
                return EntityResult.error_result("Effect Carrier Manager가 설정되지 않았습니다")
            
            # Effect Carrier 제거
            effect_result = await self.effect_carrier_manager.revoke_effect_from_entity(
                session_id, entity_id, effect_id
            )
            
            if not effect_result.success:
                return EntityResult.error_result(f"Effect Carrier 제거 실패: {effect_result.message}")
            
            self.logger.info(f"Effect Carrier '{effect_id}'를 엔티티 '{entity_id}'에서 제거 완료")
            return EntityResult.success_result(
                f"Effect Carrier '{effect_id}' 제거 완료"
            )
            
        except Exception as e:
            self.logger.error(f"Effect Carrier 제거 실패: {str(e)}")
            return EntityResult.error_result(f"Effect Carrier 제거 실패: {str(e)}")
    
    async def get_entity_effects(self, entity_id: str, session_id: str) -> EntityResult:
        """엔티티의 Effect Carrier 목록 조회"""
        try:
            if not self.effect_carrier_manager:
                return EntityResult.error_result("Effect Carrier Manager가 설정되지 않았습니다")
            
            # Effect Carrier 목록 조회
            effect_result = await self.effect_carrier_manager.get_entity_effects(session_id, entity_id)
            
            if not effect_result.success:
                return EntityResult.error_result(f"Effect Carrier 조회 실패: {effect_result.message}")
            
            return EntityResult.success_result(
                f"엔티티 '{entity_id}'의 Effect Carrier 목록 조회 완료",
                effect_result.data
            )
            
        except Exception as e:
            self.logger.error(f"엔티티 Effect Carrier 조회 실패: {str(e)}")
            return EntityResult.error_result(f"엔티티 Effect Carrier 조회 실패: {str(e)}")
    
    async def update_entity_stats(self, entity_id: str, stats: Dict[str, Any]) -> EntityResult:
        """엔티티 스탯 업데이트"""
        try:
            # 기존 엔티티 조회
            get_result = await self.get_entity(entity_id)
            if not get_result.success:
                return get_result
            
            entity = get_result.entity
            if not entity:
                return EntityResult.error_result("엔티티를 찾을 수 없습니다")
            
            # 스탯 업데이트
            updated_properties = entity.properties.copy()
            updated_properties.update(stats)
            
            # 엔티티 업데이트 (properties를 직접 업데이트)
            update_result = await self.update_entity(
                entity_id, 
                updated_properties
            )
            
            if not update_result.success:
                return update_result
            
            self.logger.info(f"엔티티 '{entity_id}' 스탯 업데이트 완료")
            return EntityResult.success_result(
                update_result.entity,
                f"엔티티 스탯 업데이트 완료"
            )
            
        except Exception as e:
            self.logger.error(f"엔티티 스탯 업데이트 실패: {str(e)}")
            return EntityResult.error_result(f"엔티티 스탯 업데이트 실패: {str(e)}")
    
    async def restore_hp_mp(
        self,
        runtime_entity_id: str,
        hp: int = 0,
        mp: int = 0
    ) -> EntityResult:
        """
        HP/MP 회복
        
        Args:
            runtime_entity_id: 런타임 엔티티 ID
            hp: 회복할 HP 양 (기본값: 0)
            mp: 회복할 MP 양 (기본값: 0)
        
        Returns:
            EntityResult: 회복 결과
        """
        try:
            # 1. 현재 엔티티 조회
            get_result = await self.get_entity(runtime_entity_id)
            if not get_result.success:
                return get_result
            
            entity = get_result.entity
            if not entity:
                return EntityResult.error_result("엔티티를 찾을 수 없습니다")
            
            # 2. 현재 스탯 조회 (runtime_data.entity_states에서)
            pool = await self.db.pool
            async with pool.acquire() as conn:
                entity_state = await conn.fetchrow(
                    """
                    SELECT current_stats FROM runtime_data.entity_states
                    WHERE runtime_entity_id = $1
                    """,
                    runtime_entity_id
                )
                
                if not entity_state:
                    return EntityResult.error_result("엔티티 상태를 찾을 수 없습니다")
                
                current_stats = parse_jsonb_data(entity_state.get('current_stats', {}))
                
                # 3. 현재 HP/MP 및 최대값 확인
                current_hp = current_stats.get('hp', 0)
                current_mp = current_stats.get('mp', 0)
                max_hp = current_stats.get('max_hp', current_hp)
                max_mp = current_stats.get('max_mp', current_mp)
                
                # 4. HP/MP 회복 (최대값 초과 방지)
                new_hp = min(current_hp + hp, max_hp)
                new_mp = min(current_mp + mp, max_mp)
                
                # 실제 회복량 계산
                actual_hp_restored = new_hp - current_hp
                actual_mp_restored = new_mp - current_mp
                
                # 5. 스탯 업데이트
                updated_stats = {
                    'hp': new_hp,
                    'mp': new_mp
                }
                
                await self.runtime_data.update_entity_stats(
                    runtime_entity_id,
                    updated_stats
                )
                
                # 6. 캐시 무효화
                async with self._cache_lock:
                    if runtime_entity_id in self._entity_cache:
                        del self._entity_cache[runtime_entity_id]
                
                # 7. 결과 메시지 생성
                message_parts = []
                if actual_hp_restored > 0:
                    message_parts.append(f"HP +{actual_hp_restored}")
                if actual_mp_restored > 0:
                    message_parts.append(f"MP +{actual_mp_restored}")
                
                if not message_parts:
                    message = "회복할 수 없습니다 (이미 최대치)"
                else:
                    message = ", ".join(message_parts) + " 회복"
                
                self.logger.info(f"엔티티 '{runtime_entity_id}' HP/MP 회복: {message}")
                
                # 8. 업데이트된 엔티티 조회하여 반환
                updated_result = await self.get_entity(runtime_entity_id)
                if updated_result.success and updated_result.entity:
                    return EntityResult.success_result(
                        updated_result.entity,
                        message
                    )
                else:
                    return EntityResult.success_result(
                        entity,
                        message
                    )
                    
        except Exception as e:
            self.logger.error(f"HP/MP 회복 실패: {str(e)}")
            return EntityResult.error_result(f"HP/MP 회복 실패: {str(e)}")
    
    async def _delete_entity_from_db(self, entity_id: str) -> None:
        """데이터베이스에서 런타임 엔티티 삭제"""
        try:
           pool = await self.db.pool
           async with pool.acquire() as conn:
                # runtime_data.runtime_entities에서 삭제 (CASCADE로 관련 테이블도 자동 삭제)
                await conn.execute("""
                    DELETE FROM runtime_data.runtime_entities 
                    WHERE runtime_entity_id = $1
                """, entity_id)
                
                # reference_layer.entity_references에서도 삭제
                await conn.execute("""
                    DELETE FROM reference_layer.entity_references 
                WHERE runtime_entity_id = $1
                """, entity_id)
                
        except Exception as e:
            self.logger.error(f"Failed to delete entity from database: {str(e)}")
            raise

    async def clear_cache(self) -> None:
        """캐시 초기화"""
        async with self._cache_lock:
            self._entity_cache.clear()
    
    async def validate_schema(self) -> Dict[str, Any]:
        """스키마 검증"""
        try:
            return await self._schema_validator.validate_manager_schema("EntityManager")
        except Exception as e:
            self.logger.error(f"Schema validation failed: {str(e)}")
            return {
                "manager": "EntityManager",
                "valid": False,
                "errors": [f"Schema validation failed: {str(e)}"],
                "warnings": []
            }
