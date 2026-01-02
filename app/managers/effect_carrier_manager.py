"""
Effect Carrier Manager
Effect Carrier 생성, 조회, 수정, 삭제, 소유 관계 관리
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, field_validator
from enum import Enum
import asyncio
import json
from datetime import datetime
import uuid

from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from common.utils.logger import logger

class EffectCarrierType(str, Enum):
    """Effect Carrier 타입 열거형"""
    SKILL = "skill"
    BUFF = "buff"
    ITEM = "item"
    BLESSING = "blessing"
    CURSE = "curse"
    RITUAL = "ritual"

class EffectCarrierData(BaseModel):
    """Effect Carrier 데이터 모델"""
    effect_id: str = Field(..., description="Effect Carrier 고유 ID")
    name: str = Field(..., min_length=1, max_length=100, description="Effect Carrier 이름")
    carrier_type: EffectCarrierType = Field(..., description="Effect Carrier 타입")
    effect_json: Dict[str, Any] = Field(..., description="효과 데이터 (JSONB)")
    constraints_json: Dict[str, Any] = Field(default_factory=dict, description="제약 조건 (JSONB)")
    source_entity_id: Optional[str] = Field(None, description="신격/유래 엔티티 ID")
    tags: List[str] = Field(default_factory=list, description="태그 목록")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    updated_at: datetime = Field(default_factory=datetime.now, description="수정 시간")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    @field_validator('effect_json')
    @classmethod
    def validate_effect_json(cls, v):
        if not isinstance(v, dict):
            raise ValueError('effect_json must be a dictionary')
        return v
    
    @field_validator('constraints_json')
    @classmethod
    def validate_constraints_json(cls, v):
        if not isinstance(v, dict):
            raise ValueError('constraints_json must be a dictionary')
        return v
    
    model_config = {
        "use_enum_values": True,
        "validate_assignment": True
    }

class EffectOwnershipData(BaseModel):
    """Effect Carrier 소유 관계 데이터 모델"""
    session_id: str = Field(..., description="세션 ID")
    runtime_entity_id: str = Field(..., description="런타임 엔티티 ID")
    effect_id: str = Field(..., description="Effect Carrier ID")
    acquired_at: datetime = Field(default_factory=datetime.now, description="획득 시간")
    source: Optional[str] = Field(None, description="획득 경로")
    
    class Config:
        validate_assignment = True

class EffectCarrierResult(BaseModel):
    """Effect Carrier 작업 결과 모델"""
    success: bool
    message: str
    data: Optional[Union[EffectCarrierData, List[EffectCarrierData], Dict[str, Any]]] = None
    error: Optional[str] = None
    
    @classmethod
    def success_result(cls, message: str, data: Optional[Union[EffectCarrierData, List[EffectCarrierData], Dict[str, Any]]] = None) -> "EffectCarrierResult":
        return cls(success=True, message=message, data=data)
    
    @classmethod
    def error_result(cls, message: str, error: str = None) -> "EffectCarrierResult":
        return cls(success=False, message=message, error=error)

class EffectCarrierManager:
    """Effect Carrier 관리 클래스"""
    
    def __init__(self, 
                 db_connection: DatabaseConnection,
                 game_data_repo: GameDataRepository,
                 runtime_data_repo: RuntimeDataRepository,
                 reference_layer_repo: ReferenceLayerRepository):
        self.db = db_connection
        self.game_data = game_data_repo
        self.runtime_data = runtime_data_repo
        self.reference_layer = reference_layer_repo
        self.logger = logger
        self._cache: Dict[str, EffectCarrierData] = {}
        self._cache_lock = asyncio.Lock()
    
    async def create_effect_carrier(self, 
                                  name: str, 
                                  carrier_type: EffectCarrierType,
                                  effect_json: Dict[str, Any],
                                  constraints_json: Dict[str, Any] = None,
                                  source_entity_id: Optional[str] = None,
                                  tags: List[str] = None) -> EffectCarrierResult:
        """Effect Carrier 생성"""
        try:
            # 입력 데이터 검증
            if not name or not name.strip():
                return EffectCarrierResult.error_result("Effect Carrier 이름은 필수입니다")
            
            if not effect_json:
                return EffectCarrierResult.error_result("효과 데이터는 필수입니다")
            
            # Effect Carrier 데이터 생성
            # UUID 객체로 생성 후 Pydantic 모델 전달 시 문자열로 변환 (API 경계)
            effect_id_uuid = uuid.uuid4()
            effect_carrier = EffectCarrierData(
                effect_id=str(effect_id_uuid),
                name=name.strip(),
                carrier_type=carrier_type,
                effect_json=effect_json,
                constraints_json=constraints_json or {},
                source_entity_id=source_entity_id,
                tags=tags or []
            )
            
            # 데이터베이스에 저장
            await self._save_effect_carrier_to_db(effect_carrier)
            
            # 캐시에 저장
            async with self._cache_lock:
                self._cache[effect_carrier.effect_id] = effect_carrier
            
            self.logger.info(f"Effect Carrier 생성 완료: {effect_carrier.name} ({effect_carrier.carrier_type})")
            return EffectCarrierResult.success_result(
                f"Effect Carrier '{effect_carrier.name}' 생성 완료",
                effect_carrier
            )
            
        except Exception as e:
            self.logger.error(f"Effect Carrier 생성 실패: {str(e)}")
            return EffectCarrierResult.error_result(f"Effect Carrier 생성 실패: {str(e)}")
    
    async def get_effect_carrier(self, effect_id: str) -> EffectCarrierResult:
        """Effect Carrier 조회"""
        try:
            # 캐시에서 먼저 확인
            async with self._cache_lock:
                if effect_id in self._cache:
                    cached_effect = self._cache[effect_id]
                    return EffectCarrierResult.success_result(
                        f"Effect Carrier '{cached_effect.name}' 조회 완료",
                        cached_effect
                    )
            
            # 데이터베이스에서 조회
            effect_carrier = await self._load_effect_carrier_from_db(effect_id)
            if not effect_carrier:
                return EffectCarrierResult.error_result(f"Effect Carrier '{effect_id}'를 찾을 수 없습니다")
            
            # 캐시에 저장
            async with self._cache_lock:
                self._cache[effect_id] = effect_carrier
            
            return EffectCarrierResult.success_result(
                f"Effect Carrier '{effect_carrier.name}' 조회 완료",
                effect_carrier
            )
            
        except Exception as e:
            self.logger.error(f"Effect Carrier 조회 실패: {str(e)}")
            return EffectCarrierResult.error_result(f"Effect Carrier 조회 실패: {str(e)}")
    
    async def update_effect_carrier(self, 
                                  effect_id: str, 
                                  **kwargs) -> EffectCarrierResult:
        """Effect Carrier 수정"""
        try:
            # 기존 Effect Carrier 조회
            get_result = await self.get_effect_carrier(effect_id)
            if not get_result.success:
                return get_result
            
            effect_carrier = get_result.data
            if not isinstance(effect_carrier, EffectCarrierData):
                return EffectCarrierResult.error_result("Effect Carrier 데이터 형식이 올바르지 않습니다")
            
            # 수정할 필드만 업데이트
            update_data = effect_carrier.dict()
            for key, value in kwargs.items():
                if key in update_data and value is not None:
                    update_data[key] = value
            
            # 수정 시간 업데이트
            update_data['updated_at'] = datetime.now()
            
            # 새로운 Effect Carrier 데이터 생성
            updated_effect_carrier = EffectCarrierData(**update_data)
            
            # 데이터베이스에 저장
            await self._save_effect_carrier_to_db(updated_effect_carrier)
            
            # 캐시 업데이트
            async with self._cache_lock:
                self._cache[effect_id] = updated_effect_carrier
            
            self.logger.info(f"Effect Carrier 수정 완료: {updated_effect_carrier.name}")
            return EffectCarrierResult.success_result(
                f"Effect Carrier '{updated_effect_carrier.name}' 수정 완료",
                updated_effect_carrier
            )
            
        except Exception as e:
            self.logger.error(f"Effect Carrier 수정 실패: {str(e)}")
            return EffectCarrierResult.error_result(f"Effect Carrier 수정 실패: {str(e)}")
    
    async def delete_effect_carrier(self, effect_id: str) -> EffectCarrierResult:
        """Effect Carrier 삭제"""
        try:
            # 기존 Effect Carrier 조회
            get_result = await self.get_effect_carrier(effect_id)
            if not get_result.success:
                return get_result
            
            effect_carrier = get_result.data
            if not isinstance(effect_carrier, EffectCarrierData):
                return EffectCarrierResult.error_result("Effect Carrier 데이터 형식이 올바르지 않습니다")
            
            # 데이터베이스에서 삭제
            await self._delete_effect_carrier_from_db(effect_id)
            
            # 캐시에서 제거
            async with self._cache_lock:
                if effect_id in self._cache:
                    del self._cache[effect_id]
            
            self.logger.info(f"Effect Carrier 삭제 완료: {effect_carrier.name}")
            return EffectCarrierResult.success_result(
                f"Effect Carrier '{effect_carrier.name}' 삭제 완료"
            )
            
        except Exception as e:
            self.logger.error(f"Effect Carrier 삭제 실패: {str(e)}")
            return EffectCarrierResult.error_result(f"Effect Carrier 삭제 실패: {str(e)}")
    
    async def grant_effect_to_entity(self, 
                                   session_id: str, 
                                   entity_id: str, 
                                   effect_id: str,
                                   source: Optional[str] = None) -> EffectCarrierResult:
        """엔티티에 Effect Carrier 부여"""
        try:
            # Effect Carrier 존재 확인
            effect_result = await self.get_effect_carrier(effect_id)
            if not effect_result.success:
                return effect_result
            
            # 소유 관계 데이터 생성
            ownership = EffectOwnershipData(
                session_id=session_id,
                runtime_entity_id=entity_id,
                effect_id=effect_id,
                source=source
            )
            
            # 데이터베이스에 저장
            await self._save_effect_ownership_to_db(ownership)
            
            self.logger.info(f"Effect Carrier '{effect_id}'를 엔티티 '{entity_id}'에 부여 완료")
            return EffectCarrierResult.success_result(
                f"Effect Carrier를 엔티티에 부여 완료"
            )
            
        except Exception as e:
            self.logger.error(f"Effect Carrier 부여 실패: {str(e)}")
            return EffectCarrierResult.error_result(f"Effect Carrier 부여 실패: {str(e)}")
    
    async def revoke_effect_from_entity(self, 
                                      session_id: str, 
                                      entity_id: str, 
                                      effect_id: str) -> EffectCarrierResult:
        """엔티티에서 Effect Carrier 제거"""
        try:
            # 소유 관계 삭제
            await self._delete_effect_ownership_from_db(session_id, entity_id, effect_id)
            
            self.logger.info(f"Effect Carrier '{effect_id}'를 엔티티 '{entity_id}'에서 제거 완료")
            return EffectCarrierResult.success_result(
                f"Effect Carrier를 엔티티에서 제거 완료"
            )
            
        except Exception as e:
            self.logger.error(f"Effect Carrier 제거 실패: {str(e)}")
            return EffectCarrierResult.error_result(f"Effect Carrier 제거 실패: {str(e)}")
    
    async def get_entity_effects(self, session_id: str, entity_id: str) -> EffectCarrierResult:
        """엔티티의 Effect Carrier 목록 조회"""
        try:
            # 소유 관계 조회
            ownerships = await self._load_entity_effect_ownerships(session_id, entity_id)
            
            # Effect Carrier 데이터 조회
            effects = []
            for ownership in ownerships:
                effect_result = await self.get_effect_carrier(ownership.effect_id)
                if effect_result.success and effect_result.data:
                    effects.append(effect_result.data)
            
            return EffectCarrierResult.success_result(
                f"엔티티 '{entity_id}'의 Effect Carrier 목록 조회 완료",
                effects
            )
            
        except Exception as e:
            self.logger.error(f"엔티티 Effect Carrier 조회 실패: {str(e)}")
            return EffectCarrierResult.error_result(f"엔티티 Effect Carrier 조회 실패: {str(e)}")
    
    async def _save_effect_carrier_to_db(self, effect_carrier: EffectCarrierData) -> None:
        """데이터베이스에 Effect Carrier 저장"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO game_data.effect_carriers 
                    (effect_id, name, carrier_type, effect_json, constraints_json, source_entity_id, tags, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    ON CONFLICT (effect_id) 
                    DO UPDATE SET 
                        name = EXCLUDED.name,
                        carrier_type = EXCLUDED.carrier_type,
                        effect_json = EXCLUDED.effect_json,
                        constraints_json = EXCLUDED.constraints_json,
                        source_entity_id = EXCLUDED.source_entity_id,
                        tags = EXCLUDED.tags,
                        updated_at = EXCLUDED.updated_at
                """, 
                effect_carrier.effect_id,
                effect_carrier.name,
                effect_carrier.carrier_type.value if hasattr(effect_carrier.carrier_type, 'value') else str(effect_carrier.carrier_type),
                json.dumps(effect_carrier.effect_json),
                json.dumps(effect_carrier.constraints_json),
                effect_carrier.source_entity_id,
                effect_carrier.tags,
                effect_carrier.created_at,
                effect_carrier.updated_at
                )
        except Exception as e:
            self.logger.error(f"Effect Carrier DB 저장 실패: {str(e)}")
            raise
    
    async def _load_effect_carrier_from_db(self, effect_id: str) -> Optional[EffectCarrierData]:
        """데이터베이스에서 Effect Carrier 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT effect_id, name, carrier_type, effect_json, constraints_json, 
                           source_entity_id, tags, created_at, updated_at
                    FROM game_data.effect_carriers 
                    WHERE effect_id = $1
                """, effect_id)
                
                if not row:
                    return None
                
                # JSONB 데이터 처리
                effect_json = row['effect_json']
                if isinstance(effect_json, str):
                    effect_json = json.loads(effect_json)
                
                constraints_json = row['constraints_json']
                if isinstance(constraints_json, str):
                    constraints_json = json.loads(constraints_json)
                
                # effect_id를 문자열로 변환 (UUID 객체인 경우)
                effect_id = str(row['effect_id']) if row['effect_id'] else None
                source_entity_id = str(row['source_entity_id']) if row['source_entity_id'] else None
                
                return EffectCarrierData(
                    effect_id=effect_id,
                    name=row['name'],
                    carrier_type=EffectCarrierType(row['carrier_type']),
                    effect_json=effect_json,
                    constraints_json=constraints_json,
                    source_entity_id=source_entity_id,
                    tags=row['tags'] or [],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
        except Exception as e:
            self.logger.error(f"Effect Carrier DB 조회 실패: {str(e)}")
            raise
    
    async def _delete_effect_carrier_from_db(self, effect_id: str) -> None:
        """데이터베이스에서 Effect Carrier 삭제"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                await conn.execute("""
                    DELETE FROM game_data.effect_carriers 
                    WHERE effect_id = $1
                """, effect_id)
        except Exception as e:
            self.logger.error(f"Effect Carrier DB 삭제 실패: {str(e)}")
            raise
    
    async def _save_effect_ownership_to_db(self, ownership: EffectOwnershipData) -> None:
        """데이터베이스에 Effect Carrier 소유 관계 저장"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO reference_layer.entity_effect_ownership 
                    (session_id, runtime_entity_id, effect_id, acquired_at, source)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (session_id, runtime_entity_id, effect_id) 
                    DO UPDATE SET 
                        acquired_at = EXCLUDED.acquired_at,
                        source = EXCLUDED.source
                """, 
                ownership.session_id,
                ownership.runtime_entity_id,
                ownership.effect_id,
                ownership.acquired_at,
                ownership.source
                )
        except Exception as e:
            self.logger.error(f"Effect Carrier 소유 관계 DB 저장 실패: {str(e)}")
            raise
    
    async def _delete_effect_ownership_from_db(self, session_id: str, entity_id: str, effect_id: str) -> None:
        """데이터베이스에서 Effect Carrier 소유 관계 삭제"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                await conn.execute("""
                    DELETE FROM reference_layer.entity_effect_ownership 
                    WHERE session_id = $1 AND runtime_entity_id = $2 AND effect_id = $3
                """, session_id, entity_id, effect_id)
        except Exception as e:
            self.logger.error(f"Effect Carrier 소유 관계 DB 삭제 실패: {str(e)}")
            raise
    
    async def _load_entity_effect_ownerships(self, session_id: str, entity_id: str) -> List[EffectOwnershipData]:
        """엔티티의 Effect Carrier 소유 관계 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT session_id, runtime_entity_id, effect_id, acquired_at, source
                    FROM reference_layer.entity_effect_ownership 
                    WHERE session_id = $1 AND runtime_entity_id = $2
                    ORDER BY acquired_at DESC
                """, session_id, entity_id)
                
                return [
                    EffectOwnershipData(
                        session_id=row['session_id'],
                        runtime_entity_id=row['runtime_entity_id'],
                        effect_id=row['effect_id'],
                        acquired_at=row['acquired_at'],
                        source=row['source']
                    )
                    for row in rows
                ]
        except Exception as e:
            self.logger.error(f"엔티티 Effect Carrier 소유 관계 DB 조회 실패: {str(e)}")
            raise
