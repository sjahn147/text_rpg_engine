"""
셀 관리 모듈
"""
from typing import Dict, List, Optional, Any, Tuple, Union
from uuid import UUID
import uuid
import asyncio
import json
from datetime import datetime
from common.utils.jsonb_handler import parse_jsonb_data, serialize_jsonb_data
from enum import Enum
from pydantic import BaseModel, Field
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from app.managers.entity_manager import EntityManager, EntityData, EntityType, EntityStatus
from app.managers.effect_carrier_manager import EffectCarrierManager
from common.utils.logger import logger


class CellType(str, Enum):
    """셀 타입 열거형"""
    INDOOR = "indoor"
    OUTDOOR = "outdoor"
    DUNGEON = "dungeon"
    SHOP = "shop"
    TAVERN = "tavern"
    TEMPLE = "temple"


class CellStatus(str, Enum):
    """셀 상태 열거형"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"
    DANGEROUS = "dangerous"


class CellData(BaseModel):
    """셀 데이터 모델"""
    cell_id: str = Field(..., description="셀 고유 ID")
    name: str = Field(..., min_length=1, max_length=100, description="셀 이름")
    cell_type: CellType = Field(..., description="셀 타입")
    status: CellStatus = Field(default=CellStatus.ACTIVE, description="셀 상태")
    description: str = Field(default="", description="셀 설명")
    location_id: str = Field(..., description="위치 ID")
    properties: Dict[str, Any] = Field(default_factory=dict, description="셀 속성")
    position: Dict[str, float] = Field(default_factory=dict, description="위치 정보")
    size: Dict[str, int] = Field(default_factory=lambda: {"width": 20, "height": 20}, description="셀 크기")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    updated_at: datetime = Field(default_factory=datetime.now, description="수정 시간")
    
    class Config:
        use_enum_values = True
        validate_assignment = True


class CellContent(BaseModel):
    """셀 컨텐츠 모델"""
    entities: List[EntityData] = Field(default_factory=list, description="엔티티 목록")
    objects: List[Dict[str, Any]] = Field(default_factory=list, description="오브젝트 목록")
    events: List[Dict[str, Any]] = Field(default_factory=list, description="이벤트 목록")
    atmosphere: Dict[str, Any] = Field(default_factory=dict, description="분위기 정보")
    
    class Config:
        validate_assignment = True


class CellResult(BaseModel):
    """셀 작업 결과 모델"""
    success: bool = Field(..., description="작업 성공 여부")
    cell: Optional[CellData] = Field(default=None, description="셀 데이터")
    content: Optional[CellContent] = Field(default=None, description="셀 컨텐츠")
    message: str = Field(default="", description="결과 메시지")
    error: Optional[str] = Field(default=None, description="에러 메시지")
    
    @classmethod
    def success_result(cls, cell: CellData, content: CellContent = None, message: str = "Success") -> "CellResult":
        """성공 결과 생성"""
        return cls(success=True, cell=cell, content=content, message=message)
    
    @classmethod
    def error_result(cls, message: str, error: str = None) -> "CellResult":
        """에러 결과 생성"""
        return cls(success=False, message=message, error=error)


class CellManager:
    """셀 관리 클래스"""
    
    def __init__(self, 
                 db_connection: DatabaseConnection,
                 game_data_repo: GameDataRepository,
                 runtime_data_repo: RuntimeDataRepository,
                 reference_layer_repo: ReferenceLayerRepository,
                 entity_manager: EntityManager,
                 effect_carrier_manager: Optional[EffectCarrierManager] = None):
        """
        CellManager 초기화
        
        Args:
            db_connection: 데이터베이스 연결
            game_data_repo: 게임 데이터 저장소
            runtime_data_repo: 런타임 데이터 저장소
            reference_layer_repo: 참조 레이어 저장소
            entity_manager: 엔티티 관리자
            effect_carrier_manager: Effect Carrier 관리자 (선택사항)
        """
        self.db = db_connection
        self.game_data = game_data_repo
        self.runtime_data = runtime_data_repo
        self.reference_layer = reference_layer_repo
        self.entity_manager = entity_manager
        self.effect_carrier_manager = effect_carrier_manager
        self.logger = logger
        
        # 셀 캐시
        self._cell_cache: Dict[str, CellData] = {}
        self._content_cache: Dict[str, CellContent] = {}
        self._cache_lock = asyncio.Lock()
    
    async def create_cell(self, 
                         static_cell_id: str,
                         session_id: Union[str, UUID]) -> CellResult:
        """
        정적 셀 템플릿에서 런타임 셀 인스턴스 생성
        
        Args:
            static_cell_id: 정적 셀 템플릿 ID (CELL_* 패턴)
            session_id: 세션 ID
            
        Returns:
            CellResult: 생성 결과
        """
        try:
            # 정적 셀 템플릿 조회
            template_result = await self.db.execute_query("""
                SELECT cell_name, location_id, cell_description, cell_properties, matrix_width, matrix_height
                FROM game_data.world_cells 
                WHERE cell_id = $1
            """, static_cell_id)
            
            if not template_result:
                return CellResult.error_result(f"정적 셀 템플릿을 찾을 수 없습니다: {static_cell_id}")
            
            template = template_result[0]
            
            # 런타임 셀 인스턴스 ID 생성 (UUID 객체)
            runtime_cell_id = uuid.uuid4()
            
            # 먼저 세션 생성 (존재하지 않는 경우)
            session_id_str = str(session_id)
            await self.db.execute_query("""
                INSERT INTO runtime_data.active_sessions 
                (session_id, session_name, player_runtime_entity_id, session_state, created_at, updated_at)
                VALUES ($1, $2, $3, $4, NOW(), NOW())
                ON CONFLICT (session_id) DO NOTHING
            """, 
            session_id,
            f"Test Session {session_id_str[:8]}",
            None,
            "active"
            )
            
            # 런타임 셀 인스턴스를 runtime_data.runtime_cells에 매핑만 저장
            await self.db.execute_query("""
                INSERT INTO runtime_data.runtime_cells (
                    runtime_cell_id, game_cell_id, session_id, status, cell_type, created_at
                ) VALUES ($1, $2, $3, $4, $5, NOW())
            """, 
            runtime_cell_id,
            static_cell_id,
            session_id,
            "active",
            "indoor"
            )
            
            # reference_layer에 매핑 저장
            await self.db.execute_query("""
                INSERT INTO reference_layer.cell_references (game_cell_id, runtime_cell_id, session_id, cell_type, created_at)
                VALUES ($1, $2, $3, $4, NOW())
            """, static_cell_id, runtime_cell_id, session_id, "template")
            
            # JSONB 데이터 파싱 (통일된 처리)
            cell_properties = parse_jsonb_data(template["cell_properties"])
            
            # 셀 데이터 생성 (정적 템플릿 정보 사용)
            from app.common.utils.uuid_helper import normalize_uuid
            cell_data = CellData(
                cell_id=normalize_uuid(runtime_cell_id),  # UUID 헬퍼 함수로 문자열로 정규화
                name=template["cell_name"],
                cell_type=CellType.INDOOR,  # 기본값
                location_id=template["location_id"],
                description=template["cell_description"],
                properties=cell_properties or {},
                position={"x": 0.0, "y": 0.0},
                size={"width": template["matrix_width"], "height": template["matrix_height"]}
            )
            
            # 캐시에 추가
            async with self._cache_lock:
                self._cell_cache[runtime_cell_id] = cell_data
            
            return CellResult.success_result(
                cell_data, 
                message=f"런타임 셀 인스턴스 '{template['cell_name']}' 생성 완료"
            )
            
        except Exception as e:
            return CellResult.error_result(
                f"런타임 셀 인스턴스 생성 실패: {str(e)}",
                str(e)
            )
    
    async def get_cell(self, cell_id: Union[str, UUID]) -> CellResult:
        """
        셀 조회
        
        Args:
            cell_id: 셀 ID
                - UUID인 경우: runtime_cell_id (reference_layer를 통해 game_cell_id 변환)
                - str인 경우: game_cell_id (VARCHAR, game_data.world_cells 직접 조회)
            
        Returns:
            CellResult: 조회 결과
        """
        try:
            # 캐시에서 먼저 확인
            async with self._cache_lock:
                cache_key = str(cell_id)
                if cache_key in self._cell_cache:
                    cell = self._cell_cache[cache_key]
                    return CellResult.success_result(cell, message="캐시에서 조회")
            
            # 데이터베이스에서 조회
            # 원칙: UUID는 runtime_cell_id → reference_layer → game_cell_id (VARCHAR)
            # UUID 객체 또는 UUID 형식 문자열인지 확인
            is_uuid = isinstance(cell_id, UUID)
            if not is_uuid and isinstance(cell_id, str):
                # UUID 형식 문자열인지 확인 (예: "550e8400-e29b-41d4-a716-446655440000")
                try:
                    uuid.UUID(cell_id)
                    is_uuid = True
                except (ValueError, AttributeError):
                    is_uuid = False
            
            if is_uuid:
                # runtime_cell_id를 game_cell_id로 변환
                runtime_uuid = cell_id if isinstance(cell_id, UUID) else uuid.UUID(cell_id)
                game_cell_id = await self._get_game_cell_id_from_runtime_id(runtime_uuid)
                if not game_cell_id:
                    return CellResult.error_result(f"런타임 셀 '{cell_id}'에 해당하는 game_cell_id를 찾을 수 없습니다.")
                cell_data = await self._load_cell_from_db(game_cell_id)
            else:
                # str인 경우 game_cell_id로 간주 (game_data.world_cells 직접 조회)
                cell_data = await self._load_cell_from_db(cell_id)
            
            if not cell_data:
                return CellResult.error_result(f"셀 '{cell_id}'를 찾을 수 없습니다.")
            
            # 캐시에 추가
            async with self._cache_lock:
                self._cell_cache[str(cell_id)] = cell_data
            
            return CellResult.success_result(cell_data, message="데이터베이스에서 조회")
            
        except Exception as e:
            return CellResult.error_result(
                f"셀 조회 실패: {str(e)}",
                str(e)
            )
    
    async def get_cell_contents(self, cell_id: Union[str, UUID]) -> Dict[str, Any]:
        """
        셀의 컨텐츠를 조회합니다 (간단한 버전)
        
        Args:
            cell_id: 런타임 셀 ID
            
        Returns:
            Dict[str, Any]: 셀 컨텐츠 (entities, objects, events)
        """
        try:
            content = await self._load_cell_content_from_db(cell_id)
            # EntityData 객체를 딕셔너리로 변환 (API 호환성을 위해 필드명 변환)
            entities_dict = []
            for e in content.entities:
                entity_dict = e.model_dump() if hasattr(e, 'model_dump') else e.dict() if hasattr(e, 'dict') else dict(e)
                # API 호환성을 위해 필드명 변환
                entity_dict['runtime_entity_id'] = entity_dict.pop('entity_id', '')
                entity_dict['entity_name'] = entity_dict.pop('name', 'Unknown')
                entity_dict['current_position'] = entity_dict.pop('position', {})
                entities_dict.append(entity_dict)
            
            return {
                'entities': entities_dict,
                'objects': content.objects,
                'events': content.events
            }
        except Exception as e:
            self.logger.error(f"Failed to get cell contents: {str(e)}")
            return {'entities': [], 'objects': [], 'events': []}
    
    async def load_cell_content(self, cell_id: Union[str, UUID]) -> CellResult:
        """
        셀 컨텐츠 로딩
        
        Args:
            cell_id: 셀 ID
            
        Returns:
            CellResult: 로딩 결과
        """
        try:
            # 셀 조회
            cell_result = await self.get_cell(cell_id)
            if not cell_result.success:
                return cell_result
            
            # 컨텐츠 캐시 확인
            async with self._cache_lock:
                if cell_id in self._content_cache:
                    content = self._content_cache[cell_id]
                    return CellResult.success_result(
                        cell_result.cell, 
                        content, 
                        "캐시에서 컨텐츠 조회"
                    )
            
            # 컨텐츠 로딩
            content = await self._load_cell_content_from_db(cell_id)
            
            # 캐시에 추가
            async with self._cache_lock:
                self._content_cache[cell_id] = content
            
            return CellResult.success_result(
                cell_result.cell, 
                content, 
                "데이터베이스에서 컨텐츠 로딩"
            )
            
        except Exception as e:
            return CellResult.error_result(
                f"셀 컨텐츠 로딩 실패: {str(e)}",
                str(e)
            )
    
    async def enter_cell(self, cell_id: Union[str, UUID], player_id: Union[str, UUID]) -> CellResult:
        """
        셀 진입
        
        Args:
            cell_id: 셀 ID
            player_id: 플레이어 ID
            
        Returns:
            CellResult: 진입 결과
        """
        try:
            # 셀 조회
            cell_result = await self.get_cell(cell_id)
            if not cell_result.success:
                return cell_result
            
            # 셀 상태 확인
            if cell_result.cell.status == CellStatus.LOCKED:
                return CellResult.error_result("잠긴 셀입니다.")
            
            if cell_result.cell.status == CellStatus.DANGEROUS:
                # 위험한 셀 진입 확인 로직
                pass
            
            # 컨텐츠 로딩
            content_result = await self.load_cell_content(cell_id)
            if not content_result.success:
                return content_result

            # 플레이어 위치 SSOT = entity_states.current_position
            await self.add_entity_to_cell(player_id, cell_id)
            # 셀 점유 테이블은 조회 편의를 위한 파생 데이터로 유지
            await self._add_player_to_cell(cell_id, player_id, conn=conn)
            
            return CellResult.success_result(
                cell_result.cell,
                content_result.content,
                f"셀 '{cell_result.cell.name}'에 진입했습니다."
            )
            
        except Exception as e:
            return CellResult.error_result(
                f"셀 진입 실패: {str(e)}",
                str(e)
            )
    
    async def leave_cell(self, cell_id: Union[str, UUID], player_id: Union[str, UUID]) -> CellResult:
        """
        셀 떠나기
        
        Args:
            cell_id: 셀 ID
            player_id: 플레이어 ID
            
        Returns:
            CellResult: 떠나기 결과
        """
        try:
            # 셀 조회
            cell_result = await self.get_cell(cell_id)
            if not cell_result.success:
                return cell_result
            
            # 플레이어 위치 SSOT = entity_states.current_position
            await self.remove_entity_from_cell(player_id, cell_id)
            # 셀 점유 파생 데이터 정리
            await self._remove_player_from_cell(cell_id, player_id, conn=conn)
            
            return CellResult.success_result(
                cell_result.cell,
                message=f"셀 '{cell_result.cell.name}'에서 떠났습니다."
            )
            
        except Exception as e:
            return CellResult.error_result(
                f"셀 떠나기 실패: {str(e)}",
                str(e)
            )
    
    async def update_cell(self, 
                         cell_id: str, 
                         updates: Dict[str, Any]) -> CellResult:
        """
        셀 업데이트
        
        Args:
            cell_id: 셀 ID
            updates: 업데이트할 속성들
            
        Returns:
            CellResult: 업데이트 결과
        """
        try:
            # 기존 셀 조회
            get_result = await self.get_cell(cell_id)
            if not get_result.success:
                return get_result
            
            cell = get_result.cell
            
            # 업데이트 적용
            updated_properties = cell.properties.copy()
            updated_properties.update(updates)
            
            # 업데이트된 셀 생성
            updated_cell = CellData(
                cell_id=cell.cell_id,
                name=cell.name,
                cell_type=cell.cell_type,
                status=cell.status,
                description=cell.description,
                properties=updated_properties,
                position=cell.position,
                size=cell.size,
                location_id=cell.location_id,
                created_at=cell.created_at,
                updated_at=datetime.now()
            )
            
            # 런타임 셀은 매핑만 저장되므로 별도 저장 불필요
            
            # 캐시 업데이트
            async with self._cache_lock:
                self._cell_cache[cell_id] = updated_cell
            
            return CellResult.success_result(
                updated_cell,
                message=f"셀 '{cell.name}' 업데이트 완료"
            )
            
        except Exception as e:
            return CellResult.error_result(
                f"셀 업데이트 실패: {str(e)}",
                str(e)
            )
    
    async def list_cells(self, 
                        cell_type: Optional[CellType] = None,
                        status: Optional[CellStatus] = None) -> List[CellData]:
        """
        셀 목록 조회
        
        Args:
            cell_type: 필터링할 셀 타입
            status: 필터링할 상태
            
        Returns:
            List[CellData]: 셀 목록
        """
        try:
            # 데이터베이스에서 조회
            cells = await self._load_cells_from_db(cell_type, status)
            
            # 캐시 업데이트
            async with self._cache_lock:
                for cell in cells:
                    self._cell_cache[cell.cell_id] = cell
            
            return cells
            
        except Exception as e:
            print(f"셀 목록 조회 실패: {str(e)}")
            return []
    
    async def delete_cell(self, cell_id: Union[str, UUID]) -> CellResult:
        """셀 삭제"""
        try:
            # 캐시에서 셀 조회
            async with self._cache_lock:
                if cell_id in self._cell_cache:
                    cell = self._cell_cache[cell_id]
                    
                    # DB에서 삭제
                    await self._delete_cell_from_db(cell_id)
                    
                    # 캐시에서 제거
                    del self._cell_cache[cell_id]
                    
                    self.logger.info(f"Cell '{cell_id}' deleted successfully")
                    return CellResult.success_result(
                        cell,
                        message=f"Cell '{cell_id}' deleted successfully"
                    )
                else:
                    return CellResult.error_result(f"Cell '{cell_id}' not found in cache")
                    
        except Exception as e:
            self.logger.error(f"Failed to delete cell '{cell_id}': {str(e)}")
            return CellResult.error_result(f"Failed to delete cell: {str(e)}")
    
    async def _delete_cell_from_db(self, cell_id: Union[str, UUID]) -> None:
        """데이터베이스에서 셀 삭제"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # 먼저 runtime_data.runtime_cells에서 삭제
                await conn.execute("""
                    DELETE FROM runtime_data.runtime_cells 
                    WHERE runtime_cell_id = $1
                """, cell_id)
                
                # 그 다음 game_data.world_cells에서 삭제
                await conn.execute("""
                    DELETE FROM game_data.world_cells 
                    WHERE cell_id = $1
                """, cell_id)
                
                self.logger.info(f"Cell '{cell_id}' deleted from database")
                
        except Exception as e:
            self.logger.error(f"Failed to delete cell from database: {str(e)}")
            raise
    
    
    async def _get_game_cell_id_from_runtime_id(self, runtime_cell_id: UUID) -> Optional[str]:
        """
        runtime_cell_id (UUID)를 game_cell_id (VARCHAR)로 변환
        
        원칙: reference_layer를 통해 변환
        """
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT game_cell_id
                    FROM reference_layer.cell_references
                    WHERE runtime_cell_id = $1
                """, runtime_cell_id)
                
                if row:
                    return row['game_cell_id']
                return None
        except Exception as e:
            self.logger.error(f"Failed to get game_cell_id from runtime_cell_id: {str(e)}")
            return None
    
    async def _load_cell_from_db(self, game_cell_id: str) -> Optional[CellData]:
        """
        데이터베이스에서 셀 로드
        
        Args:
            game_cell_id: game_cell_id (VARCHAR, game_data.world_cells의 cell_id)
        
        원칙: game_data 레이어는 VARCHAR(50) 사용
        """
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT c.cell_id, c.cell_name, c.cell_description, c.location_id, c.cell_properties, c.matrix_width, c.matrix_height
                    FROM game_data.world_cells c
                    WHERE c.cell_id = $1
                """, game_cell_id)
                
                if not row:
                    return None
                
                # JSONB 데이터 처리
                cell_properties = row['cell_properties']
                if isinstance(cell_properties, str):
                    cell_properties = json.loads(cell_properties)
                
                return CellData(
                    cell_id=row['cell_id'],
                    name=row['cell_name'],
                    description=row['cell_description'],
                    location_id=row['location_id'],
                    properties=cell_properties or {},
                    status=CellStatus.ACTIVE,  # 기본값
                    cell_type=CellType.INDOOR,  # 기본값
                    size={"width": row['matrix_width'], "height": row['matrix_height']},
                    created_at=datetime.now(),  # 기본값
                    updated_at=datetime.now()  # 기본값
                )
        except Exception as e:
            self.logger.error(f"Failed to load cell from database: {str(e)}")
            return None
    
    async def _load_cell_content_from_db(self, cell_id: Union[str, UUID]) -> CellContent:
        """
        데이터베이스에서 셀 컨텐츠 로드
        
        Args:
            cell_id: runtime_cell_id (UUID) 또는 game_cell_id (VARCHAR)
        
        원칙: UUID인 경우 reference_layer를 통해 game_cell_id 변환
        """
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # UUID인 경우 runtime_cell_id로 간주하고 reference_layer에서 game_cell_id 찾기
                if isinstance(cell_id, UUID):
                    cell_ref = await conn.fetchrow("""
                        SELECT game_cell_id, session_id
                        FROM reference_layer.cell_references
                        WHERE runtime_cell_id = $1
                    """, cell_id)
                else:
                    # str인 경우 UUID 형식인지 확인
                    # UUID 형식이면 runtime_cell_id로 간주
                    try:
                        cell_uuid = UUID(str(cell_id))
                        # UUID 형식이면 runtime_cell_id로 처리
                        cell_ref = await conn.fetchrow("""
                            SELECT game_cell_id, session_id
                            FROM reference_layer.cell_references
                            WHERE runtime_cell_id = $1
                        """, cell_uuid)
                        if not cell_ref:
                            # reference_layer에 없으면 runtime_cells에서 찾기
                            cell_ref = await conn.fetchrow("""
                                SELECT game_cell_id, session_id
                                FROM runtime_data.runtime_cells
                                WHERE runtime_cell_id = $1
                            """, cell_uuid)
                    except (ValueError, TypeError):
                        # UUID 형식이 아니면 game_cell_id로 간주
                        cell_ref = await conn.fetchrow("""
                            SELECT game_cell_id, session_id
                            FROM reference_layer.cell_references
                            WHERE game_cell_id = $1
                            LIMIT 1
                        """, cell_id)
                
                if not cell_ref:
                    # cell_references에 없으면 runtime_cells에서 찾기 (UUID인 경우)
                    if isinstance(cell_id, UUID):
                        cell_ref = await conn.fetchrow("""
                            SELECT game_cell_id, session_id
                            FROM runtime_data.runtime_cells
                            WHERE runtime_cell_id = $1
                        """, cell_id)
                    else:
                        # str이고 UUID 형식인지 다시 확인
                        try:
                            cell_uuid = UUID(str(cell_id))
                            cell_ref = await conn.fetchrow("""
                                SELECT game_cell_id, session_id
                                FROM runtime_data.runtime_cells
                                WHERE runtime_cell_id = $1
                            """, cell_uuid)
                        except (ValueError, TypeError):
                            pass  # game_cell_id로 처리했지만 찾지 못함
                
                game_cell_id = cell_ref['game_cell_id'] if cell_ref else None
                session_id = cell_ref['session_id'] if cell_ref else None
                
                # 디버그 로깅
                self.logger.debug(f"셀 컨텐츠 로드: cell_id={cell_id}, game_cell_id={game_cell_id}, session_id={session_id}")
                if not game_cell_id:
                    self.logger.warning(f"game_cell_id를 찾을 수 없음: cell_id={cell_id}, cell_ref={cell_ref}")
                if not session_id:
                    self.logger.warning(f"session_id를 찾을 수 없음: cell_id={cell_id}, cell_ref={cell_ref}")
                
                # 셀 내 엔티티 조회 (3-Layer 구조 사용)
                # current_position JSONB에서 runtime_cell_id 추출
                # 원칙: UUID를 문자열로 변환하여 비교
                entity_rows = await conn.fetch("""
                    SELECT 
                        re.runtime_entity_id,
                        ge.entity_name as name,
                        ge.entity_type,
                        ge.entity_description as description,
                        ge.entity_properties,
                        es.current_stats,
                        es.current_position
                    FROM reference_layer.entity_references re
                    JOIN game_data.entities ge ON re.game_entity_id = ge.entity_id
                    LEFT JOIN runtime_data.entity_states es ON re.runtime_entity_id = es.runtime_entity_id
                    WHERE es.current_position->>'runtime_cell_id' = $1::text
                """, str(cell_id))
                
                self.logger.debug(f"엔티티 조회 결과: {len(entity_rows)}개")
                
                # 셀 내 오브젝트 조회
                # 레퍼런스 레이어를 통해 game_object_id → runtime_object_id 변환
                object_rows = []
                if game_cell_id and session_id:
                    # 1. game_data.world_objects에서 default_cell_id가 현재 셀인 오브젝트 찾기
                    game_objects = await conn.fetch("""
                        SELECT 
                            wo.object_id as game_object_id,
                            wo.object_name,
                            wo.object_description as description,
                            wo.object_type,
                            wo.interaction_type,
                            wo.default_position,
                            wo.properties
                        FROM game_data.world_objects wo
                        WHERE wo.default_cell_id = $1
                    """, game_cell_id)
                    
                    self.logger.debug(f"게임 데이터에서 오브젝트 조회: game_cell_id={game_cell_id}, 오브젝트 수={len(game_objects)}")
                    
                    # 2. 각 오브젝트에 대해 레퍼런스 레이어에서 runtime_object_id 조회 또는 생성
                    for game_obj in game_objects:
                        game_object_id = game_obj['game_object_id']
                        
                        # object_references에서 조회
                        object_ref = await conn.fetchrow(
                            """
                            SELECT runtime_object_id FROM reference_layer.object_references
                            WHERE game_object_id = $1 AND session_id = $2
                            """,
                            game_object_id,
                            session_id
                        )
                        
                        if object_ref:
                            # 레퍼런스 레이어에 있으면 사용
                            runtime_object_id = object_ref['runtime_object_id']
                        else:
                            # 레퍼런스 레이어에 없으면 새로 생성하고 등록
                            runtime_object_id = uuid.uuid4()
                            
                            # Foreign Key 제약조건을 위해 runtime_objects를 먼저 생성
                            await conn.execute(
                                """
                                INSERT INTO runtime_data.runtime_objects 
                                (runtime_object_id, game_object_id, session_id)
                                VALUES ($1, $2, $3)
                                """,
                                runtime_object_id,
                                game_object_id,
                                session_id
                            )
                            
                            # 그 다음 object_references에 등록
                            await conn.execute(
                                """
                                INSERT INTO reference_layer.object_references 
                                (runtime_object_id, game_object_id, session_id, object_type)
                                VALUES ($1, $2, $3, $4)
                                """,
                                runtime_object_id,
                                game_object_id,
                                session_id,
                                game_obj['object_type']
                            )
                        
                        # object_states 생성 또는 업데이트 (current_position 포함)
                        # object_ref가 이미 있어도 object_states가 없을 수 있으므로 항상 확인
                        import json
                        from app.common.utils.uuid_helper import normalize_uuid
                        
                        default_pos = parse_jsonb_data(game_obj.get('default_position', {}))
                        current_position = {
                            **(default_pos if default_pos else {}),
                            'runtime_cell_id': normalize_uuid(cell_id)  # JSONB 저장용 문자열로 정규화
                        }
                        
                        # object_states가 있는지 확인
                        existing_state = await conn.fetchrow("""
                            SELECT runtime_object_id FROM runtime_data.object_states
                            WHERE runtime_object_id = $1
                        """, runtime_object_id)
                        
                        if not existing_state:
                            # object_states가 없으면 생성
                            await conn.execute(
                                """
                                INSERT INTO runtime_data.object_states 
                                (runtime_object_id, current_state, current_position)
                                VALUES ($1, $2, $3)
                                """,
                                runtime_object_id,
                                json.dumps({}),  # 기본 상태
                                json.dumps(current_position)
                            )
                        else:
                            # object_states가 있으면 current_position 업데이트
                            await conn.execute(
                                """
                                UPDATE runtime_data.object_states
                                SET current_position = $1
                                WHERE runtime_object_id = $2
                                """,
                                json.dumps(current_position),
                                runtime_object_id
                            )
                        
                        # object_rows에 추가
                        object_rows.append({
                            'runtime_object_id': runtime_object_id,
                            'game_object_id': game_object_id,
                            'object_name': game_obj['object_name'],
                            'object_description': game_obj['description'],
                            'object_type': game_obj['object_type'],
                            'interaction_type': game_obj['interaction_type'],
                            'default_position': game_obj['default_position'],
                            'properties': game_obj['properties']
                        })
                        self.logger.debug(f"오브젝트 추가: {game_obj['object_name']} (game_object_id={game_object_id}, runtime_object_id={runtime_object_id})")
                else:
                    if not game_cell_id:
                        self.logger.warning(f"game_cell_id가 없어서 오브젝트를 조회하지 않음: cell_id={cell_id}")
                    if not session_id:
                        self.logger.warning(f"session_id가 없어서 오브젝트를 조회하지 않음: cell_id={cell_id}")
                
                self.logger.debug(f"오브젝트 조회 결과: {len(object_rows)}개")
                
                # 셀 내 이벤트 조회 (현재는 빈 리스트)
                event_rows = []
                
                # 엔티티 데이터 변환
                entities = []
                for row in entity_rows:
                    position_data = parse_jsonb_data(row['current_position'])
                    # position에서 runtime_cell_id 제거 (숫자 좌표만 포함)
                    if position_data and 'runtime_cell_id' in position_data:
                        position_data = {k: v for k, v in position_data.items() if k != 'runtime_cell_id'}
                    
                    entity_properties = parse_jsonb_data(row.get('entity_properties', {}))
                    current_stats = parse_jsonb_data(row.get('current_stats', {}))
                    
                    # EntityData 모델에 맞게 변환
                    entity_data = EntityData(
                        entity_id=str(row['runtime_entity_id']),
                        name=row['name'],
                        entity_type=EntityType(row['entity_type']),
                        status=EntityStatus.ACTIVE,
                        properties=current_stats or {},
                        position=position_data or {'x': 0.0, 'y': 0.0, 'z': 0.0},
                    )
                    entities.append(entity_data)
                
                # 오브젝트 데이터 변환
                objects = []
                for row in object_rows:
                    position_data = parse_jsonb_data(row.get('default_position', {}))
                    properties = parse_jsonb_data(row.get('properties', {}))
                    runtime_object_id = row['runtime_object_id']
                    
                    # 런타임 상태에서 contents 확인 및 병합
                    runtime_state = await conn.fetchrow(
                        """
                        SELECT current_state FROM runtime_data.object_states
                        WHERE runtime_object_id = $1
                        """,
                        runtime_object_id
                    )
                    
                    if runtime_state and runtime_state.get('current_state'):
                        state_dict = parse_jsonb_data(runtime_state['current_state'])
                        # 런타임 상태에 'contents' 키가 명시적으로 있으면 사용
                        if 'contents' in state_dict:
                            # properties의 contents를 런타임 상태로 덮어쓰기
                            properties = properties.copy()
                            properties['contents'] = state_dict['contents']
                    
                    # 런타임 상태에서 state 확인 및 properties에 추가
                    if runtime_state and runtime_state.get('current_state'):
                        state_dict = parse_jsonb_data(runtime_state['current_state'])
                        # state를 properties에 추가
                        if 'state' in state_dict:
                            properties['state'] = state_dict['state']
                            properties['current_state'] = state_dict['state']
                        # contents도 properties에 추가 (이미 위에서 처리했지만 확실히)
                        if 'contents' in state_dict and 'contents' not in properties:
                            properties['contents'] = state_dict['contents']
                    
                    # runtime_object_id는 이미 레퍼런스 레이어를 통해 확보됨
                    # UUID 헬퍼 함수로 문자열로 정규화 (JSONB와의 호환성, 프론트엔드 호환성)
                    from app.common.utils.uuid_helper import normalize_uuid
                    runtime_object_id_str = normalize_uuid(runtime_object_id)
                    objects.append({
                        'object_id': runtime_object_id_str,  # 프론트엔드 호환성을 위해 object_id 추가
                        'runtime_object_id': runtime_object_id_str,  # 문자열로 정규화
                        'game_object_id': row['game_object_id'],
                        'object_name': row['object_name'],
                        'object_type': row['object_type'],
                        'description': row.get('description'),
                        'interaction_type': row.get('interaction_type'),
                        'position': position_data or {'x': 0.0, 'y': 0.0, 'z': 0.0},
                        'properties': properties,
                    })
                
                events = [dict(row) for row in event_rows]
                
                return CellContent(
                    entities=entities,
                    objects=objects,
                    events=events
                )
                
        except Exception as e:
            self.logger.error(f"Failed to load cell content from database: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return CellContent()
    
    async def _load_cells_from_db(self, 
                                 session_id: str = None,
                                 cell_type: Optional[CellType] = None) -> List[CellData]:
        """데이터베이스에서 셀 목록 로드 (런타임 셀 인스턴스 또는 정적 템플릿)"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                if session_id:
                    # 특정 세션의 런타임 셀 인스턴스 조회
                    query = """
                        SELECT 
                            rc.runtime_cell_id,
                            rc.game_cell_id,
                            rc.session_id,
                            c.cell_name,
                            c.cell_description,
                            c.location_id,
                            c.cell_properties,
                            c.matrix_width,
                            c.matrix_height
                        FROM runtime_data.runtime_cells rc
                        JOIN game_data.world_cells c ON rc.game_cell_id = c.cell_id
                        WHERE rc.session_id = $1
                    """
                    params = [session_id]
                else:
                    # 모든 정적 셀 템플릿 조회
                    query = """
                        SELECT 
                            c.cell_id,
                            c.cell_name,
                            c.cell_description,
                            c.location_id,
                            c.cell_properties,
                            c.matrix_width,
                            c.matrix_height
                        FROM game_data.world_cells c
                    """
                    params = []
                
                query += " ORDER BY c.cell_name"
                
                rows = await conn.fetch(query, *params)
                
                cells = []
                for row in rows:
                    # JSONB 데이터 처리 (통일된 처리)
                    cell_properties = parse_jsonb_data(row['cell_properties'])
                    
                    # 런타임 셀인지 정적 셀인지에 따라 ID 설정
                    cell_id = row.get('runtime_cell_id') or row['cell_id']
                    
                    # DB에서 셀의 실제 상태와 타입 조회
                    cell_status, cell_type = await self._get_cell_status_and_type(cell_id)
                    
                    cell_data = CellData(
                        cell_id=cell_id,
                        name=row['cell_name'],
                        description=row['cell_description'],
                        location_id=row['location_id'],
                        properties=cell_properties or {},
                        status=cell_status,
                        cell_type=cell_type,
                        size={"width": row['matrix_width'], "height": row['matrix_height']},
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    cells.append(cell_data)
                
                return cells
                
        except Exception as e:
            self.logger.error(f"Failed to load cells from database: {str(e)}")
            return []
    
    async def _get_cell_status_and_type(self, cell_id: Union[str, UUID]) -> Tuple[CellStatus, CellType]:
        """DB에서 셀의 상태와 타입 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # runtime_data.runtime_cells에서 상태 조회
                runtime_cell = await conn.fetchrow("""
                    SELECT rc.runtime_cell_id, rc.status, rc.cell_type
                    FROM runtime_data.runtime_cells rc
                    WHERE rc.runtime_cell_id = $1
                """, cell_id)
                
                if runtime_cell:
                    # 런타임 셀의 상태와 타입 사용
                    status = CellStatus(runtime_cell['status']) if runtime_cell['status'] else CellStatus.ACTIVE
                    cell_type = CellType(runtime_cell['cell_type']) if runtime_cell['cell_type'] else CellType.INDOOR
                else:
                    # 정적 셀의 경우 기본값 사용
                    status = CellStatus.ACTIVE
                    cell_type = CellType.INDOOR
                
                return status, cell_type
                
        except Exception as e:
            self.logger.error(f"Failed to get cell status and type: {str(e)}")
            # 오류 시 기본값 반환
            return CellStatus.ACTIVE, CellType.INDOOR
    
    async def _add_player_to_cell(self, runtime_cell_id: Union[str, UUID], runtime_entity_id: Union[str, UUID], conn=None) -> None:
        """
        플레이어를 셀에 추가 (SSOT: entity_states.current_position 사용)
        
        주의: cell_occupants는 트리거에 의해 자동 동기화됩니다.
        직접 INSERT/DELETE를 사용하지 마세요.
        """
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # SSOT: entity_states.current_position 업데이트
                # cell_occupants는 트리거에 의해 자동 동기화됨
                await conn.execute("""
                    UPDATE runtime_data.entity_states
                    SET current_position = jsonb_set(
                        COALESCE(current_position, '{}'::jsonb),
                        '{runtime_cell_id}',
                        to_jsonb($1::uuid::text)
                    ),
                    updated_at = NOW()
                    WHERE runtime_entity_id = $2
                """, runtime_cell_id, runtime_entity_id)
                
                self.logger.info(f"Player {runtime_entity_id} added to cell {runtime_cell_id} (SSOT: entity_states.current_position)")
                
        except Exception as e:
            self.logger.error(f"Failed to add player to cell: {str(e)}")
            raise
    
    async def _remove_player_from_cell(self, runtime_cell_id: Union[str, UUID], runtime_entity_id: Union[str, UUID], conn=None) -> None:
        """
        플레이어를 셀에서 제거 (SSOT: entity_states.current_position 사용)
        
        주의: cell_occupants는 트리거에 의해 자동 동기화됩니다.
        직접 INSERT/DELETE를 사용하지 마세요.
        """
        try:
            # conn이 제공된 경우 사용, 없으면 새로 생성
            if conn is None:
                pool = await self.db.pool
                async with pool.acquire() as new_conn:
                    async with new_conn.transaction():
                        await self._remove_player_from_cell(runtime_cell_id, runtime_entity_id, conn=new_conn)
                return
            
            # SSOT: entity_states.current_position에서 runtime_cell_id 제거
            # cell_occupants는 트리거에 의해 자동 동기화됨
            await conn.execute("""
                UPDATE runtime_data.entity_states
                SET current_position = current_position - 'runtime_cell_id',
                updated_at = NOW()
                WHERE runtime_entity_id = $1
            """, runtime_entity_id)
            
            self.logger.info(f"Player {runtime_entity_id} removed from cell {runtime_cell_id} (SSOT: entity_states.current_position)")
                
        except Exception as e:
            self.logger.error(f"Failed to remove player from cell: {str(e)}")
            raise

    async def add_entity_to_cell(self, runtime_entity_id: Union[str, UUID], runtime_cell_id: Union[str, UUID]) -> CellResult:
        """
        엔티티를 셀에 추가 (범용 메서드)
        
        Args:
            runtime_entity_id: 런타임 엔티티 ID
            runtime_cell_id: 런타임 셀 ID
            
        Returns:
            CellResult: 결과
        """
        try:
            # 셀 존재 확인
            cell_result = await self.get_cell(runtime_cell_id)
            if not cell_result.success:
                return cell_result
            
            # DB에 엔티티-셀 매핑 추가
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # entity_states 테이블에 runtime_cell_id 업데이트 (SSOT: current_position에 저장)
                # 원칙: runtime_cell_id는 UUID이므로 uuid::text로 변환
                await conn.execute("""
                    UPDATE runtime_data.entity_states
                    SET current_position = jsonb_set(
                        COALESCE(current_position, '{}'::jsonb),
                        '{runtime_cell_id}',
                        to_jsonb($1::uuid::text)
                    ),
                    updated_at = NOW()
                    WHERE runtime_entity_id = $2
                """, runtime_cell_id, runtime_entity_id)
            
            # 컨텐츠 캐시 무효화
            async with self._cache_lock:
                if runtime_cell_id in self._content_cache:
                    del self._content_cache[runtime_cell_id]
            
            self.logger.info(f"Entity {runtime_entity_id} added to cell {runtime_cell_id}")
            return CellResult.success_result(
                cell_result.cell,
                message=f"Entity added to cell '{cell_result.cell.name}'"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to add entity to cell: {str(e)}")
            return CellResult.error_result(f"Failed to add entity to cell: {str(e)}", str(e))
    
    async def remove_entity_from_cell(self, runtime_entity_id: Union[str, UUID], runtime_cell_id: Union[str, UUID]) -> CellResult:
        """
        엔티티를 셀에서 제거 (범용 메서드)
        
        Args:
            runtime_entity_id: 런타임 엔티티 ID
            runtime_cell_id: 런타임 셀 ID
            
        Returns:
            CellResult: 결과
        """
        try:
            # 셀 존재 확인
            cell_result = await self.get_cell(runtime_cell_id)
            if not cell_result.success:
                return cell_result
            
            # DB에서 엔티티-셀 매핑 제거
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # entity_states 테이블에서 runtime_cell_id 제거 (SSOT: current_position에서 제거)
                await conn.execute("""
                    UPDATE runtime_data.entity_states
                    SET current_position = current_position - 'runtime_cell_id',
                    updated_at = NOW()
                    WHERE runtime_entity_id = $1
                """, runtime_entity_id)
            
            # 컨텐츠 캐시 무효화
            async with self._cache_lock:
                if runtime_cell_id in self._content_cache:
                    del self._content_cache[runtime_cell_id]
            
            self.logger.info(f"Entity {runtime_entity_id} removed from cell {runtime_cell_id}")
            return CellResult.success_result(
                cell_result.cell,
                message=f"Entity removed from cell '{cell_result.cell.name}'"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to remove entity from cell: {str(e)}")
            return CellResult.error_result(f"Failed to remove entity from cell: {str(e)}", str(e))
    
    async def move_entity_between_cells(
        self, 
        runtime_entity_id: Union[str, UUID], 
        from_runtime_cell_id: Union[str, UUID], 
        to_runtime_cell_id: Union[str, UUID],
        new_position: Dict[str, float] = None
    ) -> CellResult:
        """
        엔티티를 한 셀에서 다른 셀로 이동
        
        Args:
            runtime_entity_id: 런타임 엔티티 ID
            from_runtime_cell_id: 출발 런타임 셀 ID
            to_runtime_cell_id: 도착 런타임 셀 ID
            new_position: 새 위치 (선택사항)
            
        Returns:
            CellResult: 이동 결과
        """
        try:
            # 트랜잭션으로 원자적 이동 보장
            pool = await self.db.pool
            async with pool.acquire() as conn:
                async with conn.transaction():
                    # 1. 출발 셀에서 제거
                    remove_result = await self.remove_entity_from_cell(runtime_entity_id, from_runtime_cell_id)
                    if not remove_result.success:
                        return remove_result
                    
                    # 2. 도착 셀에 추가
                    add_result = await self.add_entity_to_cell(runtime_entity_id, to_runtime_cell_id)
                    if not add_result.success:
                        return add_result
                    
                    # 3. 위치 업데이트 (선택사항 - current_cell_id 유지)
                    if new_position:
                        # current_cell_id를 유지하면서 좌표만 업데이트
                        position_with_cell = new_position.copy()
                        position_with_cell['current_cell_id'] = to_runtime_cell_id
                        
                        await conn.execute("""
                            UPDATE runtime_data.entity_states
                            SET current_position = $1,
                            updated_at = NOW()
                            WHERE runtime_entity_id = $2
                        """, serialize_jsonb_data(position_with_cell), runtime_entity_id)
            
            self.logger.info(f"Entity {runtime_entity_id} moved from {from_runtime_cell_id} to {to_runtime_cell_id}")
            
            # 도착 셀 반환
            to_cell_result = await self.get_cell(to_runtime_cell_id)
            return CellResult.success_result(
                to_cell_result.cell,
                message=f"Entity moved to cell '{to_cell_result.cell.name}'"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to move entity between cells: {str(e)}")
            return CellResult.error_result(f"Failed to move entity: {str(e)}", str(e))
    
    async def clear_cache(self) -> None:
        """캐시 초기화"""
        async with self._cache_lock:
            self._cell_cache.clear()
            self._content_cache.clear()
