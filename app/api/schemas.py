"""
월드 에디터 Pydantic 스키마
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


# =====================================================
# 지도 메타데이터 스키마
# =====================================================

class MapMetadataBase(BaseModel):
    """지도 메타데이터 기본 스키마"""
    map_name: str = Field(..., description="지도 이름")
    background_image: Optional[str] = Field(
        default="assets/world_editor/worldmap.png",
        description="지도 배경 이미지 경로"
    )
    background_color: str = Field(default="#FFFFFF", description="지도 배경색")
    width: int = Field(default=1920, description="지도 너비 (픽셀)")
    height: int = Field(default=1080, description="지도 높이 (픽셀)")
    grid_enabled: bool = Field(default=False, description="그리드 표시 여부")
    grid_size: int = Field(default=50, description="그리드 크기")
    zoom_level: float = Field(default=1.0, description="현재 확대/축소 레벨")
    viewport_x: int = Field(default=0, description="뷰포트 X 좌표")
    viewport_y: int = Field(default=0, description="뷰포트 Y 좌표")


class MapMetadataCreate(MapMetadataBase):
    """지도 메타데이터 생성 스키마"""
    map_id: str = Field(default="default_map", description="지도 ID")


class MapMetadataUpdate(BaseModel):
    """지도 메타데이터 업데이트 스키마"""
    map_name: Optional[str] = None
    background_image: Optional[str] = None
    background_color: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    grid_enabled: Optional[bool] = None
    grid_size: Optional[int] = None
    zoom_level: Optional[float] = None
    viewport_x: Optional[int] = None
    viewport_y: Optional[int] = None


class MapMetadataResponse(MapMetadataBase):
    """지도 메타데이터 응답 스키마"""
    map_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# 핀 위치 스키마
# =====================================================

class PinPositionBase(BaseModel):
    """핀 위치 기본 스키마"""
    pin_id: str = Field(..., description="핀 고유 ID")
    pin_name: str = Field(..., description="핀 표시 이름")
    game_data_id: str = Field(..., description="연결된 게임 데이터 ID (region_id, location_id, cell_id)")
    pin_type: str = Field(..., description="핀 타입 (region, location, cell)")
    x: float = Field(..., description="X 좌표")
    y: float = Field(..., description="Y 좌표")
    icon_type: str = Field(default="default", description="아이콘 타입")
    size: int = Field(default=20, description="핀 크기")
    color: str = Field(default="#FF0000", description="핀 색상")


class PinPositionCreate(BaseModel):
    """핀 위치 생성 스키마"""
    pin_id: Optional[str] = Field(None, description="핀 고유 ID (없으면 자동 생성)")
    pin_name: str = Field(..., description="핀 표시 이름")
    game_data_id: str = Field(..., description="연결된 게임 데이터 ID (region_id, location_id, cell_id)")
    pin_type: str = Field(..., description="핀 타입 (region, location, cell)")
    x: float = Field(..., description="X 좌표")
    y: float = Field(..., description="Y 좌표")
    icon_type: str = Field(default="default", description="아이콘 타입")
    size: int = Field(default=20, description="핀 크기")
    color: str = Field(default="#FF0000", description="핀 색상")


class PinPositionUpdate(BaseModel):
    """핀 위치 업데이트 스키마"""
    pin_name: Optional[str] = None
    game_data_id: Optional[str] = None
    pin_type: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    icon_type: Optional[str] = None
    size: Optional[int] = None
    color: Optional[str] = None


class PinPositionResponse(PinPositionBase):
    """핀 위치 응답 스키마"""
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# 도로 스키마
# =====================================================

class PathPoint(BaseModel):
    """경로 좌표 포인트"""
    x: float
    y: float


class RoadBase(BaseModel):
    """도로 기본 스키마"""
    from_region_id: Optional[str] = Field(None, description="시작 지역 ID (레거시)")
    from_location_id: Optional[str] = Field(None, description="시작 위치 ID (레거시)")
    to_region_id: Optional[str] = Field(None, description="종료 지역 ID (레거시)")
    to_location_id: Optional[str] = Field(None, description="종료 위치 ID (레거시)")
    from_pin_id: Optional[str] = Field(None, description="시작 핀 ID (권장)")
    to_pin_id: Optional[str] = Field(None, description="종료 핀 ID (권장)")
    road_type: str = Field(default="normal", description="도로 타입")
    distance: Optional[float] = Field(None, description="거리")
    travel_time: Optional[int] = Field(None, description="이동 시간 (분)")
    danger_level: int = Field(default=1, description="위험도 (1-10)")
    color: str = Field(default="#8B4513", description="도로 색상")
    width: int = Field(default=2, description="도로 너비 (픽셀)")
    dashed: bool = Field(default=False, description="점선 여부")
    road_properties: Dict[str, Any] = Field(default_factory=dict, description="도로 속성")
    path_coordinates: List[PathPoint] = Field(default_factory=list, description="경로 좌표")


class RoadCreate(RoadBase):
    """도로 생성 스키마"""
    road_id: Optional[str] = None


class RoadUpdate(BaseModel):
    """도로 업데이트 스키마"""
    from_pin_id: Optional[str] = None
    to_pin_id: Optional[str] = None
    road_type: Optional[str] = None
    distance: Optional[float] = None
    travel_time: Optional[int] = None
    danger_level: Optional[int] = None
    color: Optional[str] = None
    width: Optional[int] = None
    dashed: Optional[bool] = None
    road_properties: Optional[Dict[str, Any]] = None
    path_coordinates: Optional[List[PathPoint]] = None


class RoadResponse(RoadBase):
    """도로 응답 스키마"""
    road_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# Region/Location/Cell 스키마 (기존 스키마 확장)
# =====================================================

class RegionBase(BaseModel):
    """지역 기본 스키마"""
    region_name: str
    region_description: Optional[str] = None
    region_type: Optional[str] = None
    region_properties: Optional[Dict[str, Any]] = None


class RegionCreate(RegionBase):
    """지역 생성 스키마"""
    region_id: str


class RegionUpdate(BaseModel):
    """지역 업데이트 스키마"""
    region_name: Optional[str] = None
    region_description: Optional[str] = None
    region_type: Optional[str] = None
    region_properties: Optional[Dict[str, Any]] = None


class RegionResponse(RegionBase):
    """지역 응답 스키마"""
    region_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LocationBase(BaseModel):
    """위치 기본 스키마"""
    region_id: str
    location_name: str
    location_description: Optional[str] = None
    location_type: Optional[str] = None
    location_properties: Optional[Dict[str, Any]] = None


class LocationCreate(LocationBase):
    """위치 생성 스키마"""
    location_id: str


class LocationUpdate(BaseModel):
    """위치 업데이트 스키마"""
    region_id: Optional[str] = None
    location_name: Optional[str] = None
    location_description: Optional[str] = None
    location_type: Optional[str] = None
    location_properties: Optional[Dict[str, Any]] = None


class LocationResponse(LocationBase):
    """위치 응답 스키마"""
    location_id: str
    created_at: datetime
    updated_at: datetime
    # SSOT 준수: owner_name은 JOIN으로 해결, Properties에 저장하지 않음
    owner_name: Optional[str] = Field(default=None, description="주인 이름 (entities 테이블에서 JOIN)")

    class Config:
        from_attributes = True


class LocationResolvedResponse(LocationResponse):
    """모든 참조를 해결한 위치 응답 스키마 (Phase 4)"""
    # owner_entity: 전체 엔티티 정보 (선택적)
    owner_entity: Optional[Dict[str, Any]] = Field(default=None, description="주인 엔티티 전체 정보")
    # quest_giver_entities: quest_givers의 엔티티 정보
    quest_giver_entities: Optional[List[Dict[str, Any]]] = Field(default=None, description="퀘스트 제공자 엔티티 목록")
    # entry_point_cells: entry_points의 Cell 정보
    entry_point_cells: Optional[List[Dict[str, Any]]] = Field(default=None, description="진입점 Cell 목록")

    class Config:
        from_attributes = True


class CellBase(BaseModel):
    """셀 기본 스키마"""
    location_id: str
    cell_name: Optional[str] = None
    matrix_width: int
    matrix_height: int
    cell_description: Optional[str] = None
    cell_properties: Optional[Dict[str, Any]] = None
    cell_status: Optional[str] = Field(default='active', description="셀 상태 (active, inactive, locked, dangerous)")
    cell_type: Optional[str] = Field(default='indoor', description="셀 타입 (indoor, outdoor, dungeon, shop, tavern, temple)")


class CellCreate(CellBase):
    """셀 생성 스키마"""
    cell_id: str


class CellUpdate(BaseModel):
    """셀 업데이트 스키마"""
    location_id: Optional[str] = None
    cell_name: Optional[str] = None
    matrix_width: Optional[int] = None
    matrix_height: Optional[int] = None
    cell_description: Optional[str] = None
    cell_properties: Optional[Dict[str, Any]] = None
    cell_status: Optional[str] = None
    cell_type: Optional[str] = None


class CellResponse(CellBase):
    """셀 응답 스키마"""
    cell_id: str
    created_at: datetime
    updated_at: datetime
    # SSOT 준수: owner_name은 JOIN으로 해결, Properties에 저장하지 않음
    owner_name: Optional[str] = Field(default=None, description="주인 이름 (entities 테이블에서 JOIN)")

    class Config:
        from_attributes = True


class CellResolvedResponse(CellResponse):
    """모든 참조를 해결한 셀 응답 스키마 (Phase 4)"""
    # owner_entity: 전체 엔티티 정보 (선택적)
    owner_entity: Optional[Dict[str, Any]] = Field(default=None, description="주인 엔티티 전체 정보")
    # exit_cells: exits의 Cell 정보
    exit_cells: Optional[List[Dict[str, Any]]] = Field(default=None, description="출구 Cell 목록")
    # entrance_cells: entrances의 Cell 정보
    entrance_cells: Optional[List[Dict[str, Any]]] = Field(default=None, description="입구 Cell 목록")
    # connection_cells: connections의 Cell 정보
    connection_cells: Optional[List[Dict[str, Any]]] = Field(default=None, description="연결 Cell 목록")

    class Config:
        from_attributes = True


# =====================================================
# Entity (NPC) 스키마
# =====================================================

class EntityStatus(str, Enum):
    """엔티티 상태 열거형"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEAD = "dead"
    HIDDEN = "hidden"


class EntityBase(BaseModel):
    """엔티티 기본 스키마"""
    entity_type: str = Field(..., description="엔티티 타입 (npc, monster, etc.)")
    entity_name: str = Field(..., description="엔티티 이름")
    entity_description: Optional[str] = Field(None, description="엔티티 설명")
    entity_status: Optional[str] = Field("active", description="엔티티 상태 (active, inactive, dead, hidden)")
    base_stats: Dict[str, Any] = Field(default_factory=dict, description="기본 능력치")
    default_equipment: Dict[str, Any] = Field(default_factory=dict, description="기본 장비")
    default_abilities: Dict[str, Any] = Field(default_factory=dict, description="기본 능력")
    default_inventory: Dict[str, Any] = Field(default_factory=dict, description="기본 인벤토리")
    entity_properties: Dict[str, Any] = Field(default_factory=dict, description="엔티티 속성 (location_id 포함)")


class EntityCreate(EntityBase):
    """엔티티 생성 스키마"""
    entity_id: str


class EntityUpdate(BaseModel):
    """엔티티 업데이트 스키마"""
    entity_type: Optional[str] = None
    entity_name: Optional[str] = None
    entity_description: Optional[str] = None
    entity_status: Optional[str] = Field(None, description="엔티티 상태 (active, inactive, dead, hidden)")
    base_stats: Optional[Dict[str, Any]] = None
    default_equipment: Optional[Dict[str, Any]] = None
    default_abilities: Optional[Dict[str, Any]] = None
    default_inventory: Optional[Dict[str, Any]] = None
    entity_properties: Optional[Dict[str, Any]] = None
    dialogue_context_id: Optional[str] = Field(None, description="대화 컨텍스트 ID")


class EntityResponse(EntityBase):
    """엔티티 응답 스키마"""
    entity_id: str
    dialogue_context_id: Optional[str] = Field(None, description="대화 컨텍스트 ID")
    default_position_3d: Optional[Dict[str, Any]] = Field(None, description="기본 위치 (3D 좌표)")
    entity_size: Optional[str] = Field(None, description="엔티티 크기")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# Entity Behavior Schedules 스키마
# =====================================================

class EntityBehaviorScheduleBase(BaseModel):
    """엔티티 행동 스케줄 기본 스키마"""
    entity_id: str = Field(..., description="엔티티 ID")
    time_period: str = Field(..., description="시간대 (morning, afternoon, evening, night)")
    action_type: str = Field(..., description="행동 타입 (work, rest, socialize, patrol, sleep)")
    action_priority: int = Field(default=1, description="행동 우선순위")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="행동 조건 (JSONB)")
    action_data: Dict[str, Any] = Field(default_factory=dict, description="행동 세부 데이터 (JSONB)")


class EntityBehaviorScheduleCreate(EntityBehaviorScheduleBase):
    """엔티티 행동 스케줄 생성 스키마"""
    schedule_id: Optional[str] = Field(None, description="스케줄 ID (없으면 자동 생성)")


class EntityBehaviorScheduleUpdate(BaseModel):
    """엔티티 행동 스케줄 업데이트 스키마"""
    time_period: Optional[str] = None
    action_type: Optional[str] = None
    action_priority: Optional[int] = None
    conditions: Optional[Dict[str, Any]] = None
    action_data: Optional[Dict[str, Any]] = None


class EntityBehaviorScheduleResponse(EntityBehaviorScheduleBase):
    """엔티티 행동 스케줄 응답 스키마"""
    schedule_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# D&D 스타일 정보 스키마
# =====================================================

class DemographicsInfo(BaseModel):
    """인구 통계 정보"""
    population: int = 0
    races: Dict[str, int] = Field(default_factory=dict)
    classes: Dict[str, int] = Field(default_factory=dict)


class EconomyInfo(BaseModel):
    """경제 정보"""
    primary_industry: str = ""
    trade_goods: List[str] = Field(default_factory=list)
    gold_value: int = 0


class GovernmentInfo(BaseModel):
    """정부 정보"""
    type: str = ""
    leader: str = ""
    laws: List[str] = Field(default_factory=list)


class CultureInfo(BaseModel):
    """문화 정보"""
    religion: List[str] = Field(default_factory=list)
    customs: List[str] = Field(default_factory=list)
    festivals: List[str] = Field(default_factory=list)


class LoreInfo(BaseModel):
    """로어 정보"""
    history: str = ""
    legends: List[str] = Field(default_factory=list)

    secrets: List[str] = Field(default_factory=list)


class DnDLocationInfo(BaseModel):
    """D&D 스타일 지역 정보"""
    name: str
    description: str = ""
    type: str = ""
    demographics: DemographicsInfo = Field(default_factory=DemographicsInfo)
    economy: EconomyInfo = Field(default_factory=EconomyInfo)
    government: GovernmentInfo = Field(default_factory=GovernmentInfo)
    culture: CultureInfo = Field(default_factory=CultureInfo)
    lore: LoreInfo = Field(default_factory=LoreInfo)
    npcs: List[Dict[str, Any]] = Field(default_factory=list)
    quests: List[Dict[str, Any]] = Field(default_factory=list)
    shops: List[Dict[str, Any]] = Field(default_factory=list)


# =====================================================
# World Objects 스키마
# =====================================================

class WorldObjectBase(BaseModel):
    """World Object 기본 스키마"""
    object_type: str = Field(..., description="오브젝트 타입 (static, interactive, trigger)")
    object_name: str = Field(..., description="오브젝트 이름")
    object_description: Optional[str] = Field(None, description="오브젝트 설명")
    default_cell_id: Optional[str] = Field(None, description="기본 Cell ID")
    default_position: Dict[str, Any] = Field(default_factory=dict, description="기본 위치 (JSONB)")
    interaction_type: Optional[str] = Field(None, description="상호작용 타입 (none, openable, triggerable)")
    possible_states: Dict[str, Any] = Field(default_factory=dict, description="가능한 상태들 (JSONB)")
    properties: Dict[str, Any] = Field(default_factory=dict, description="추가 속성 (JSONB)")


class WorldObjectCreate(WorldObjectBase):
    """World Object 생성 스키마"""
    object_id: str = Field(..., description="오브젝트 ID (명명 규칙: OBJ_[타입]_[이름]_[일련번호])")


class WorldObjectUpdate(BaseModel):
    """World Object 업데이트 스키마"""
    object_type: Optional[str] = None
    object_name: Optional[str] = None
    object_description: Optional[str] = None
    default_cell_id: Optional[str] = None
    default_position: Optional[Dict[str, Any]] = None
    interaction_type: Optional[str] = None
    possible_states: Optional[Dict[str, Any]] = None
    properties: Optional[Dict[str, Any]] = None


class WorldObjectResponse(WorldObjectBase):
    """World Object 응답 스키마"""
    object_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# Effect Carriers 스키마
# =====================================================

from uuid import UUID

class EffectCarrierBase(BaseModel):
    """Effect Carrier 기본 스키마"""
    name: str = Field(..., description="Effect Carrier 이름")
    carrier_type: str = Field(..., description="타입 (skill, buff, item, blessing, curse, ritual)")
    effect_json: Dict[str, Any] = Field(..., description="효과의 세부 데이터 (JSONB)")
    constraints_json: Dict[str, Any] = Field(default_factory=dict, description="사용 조건 및 제약사항 (JSONB)")
    source_entity_id: Optional[str] = Field(None, description="출처 Entity ID")
    tags: List[str] = Field(default_factory=list, description="태그 배열")


class EffectCarrierCreate(EffectCarrierBase):
    """Effect Carrier 생성 스키마"""
    effect_id: Optional[UUID] = Field(None, description="Effect ID (생략 시 자동 생성)")


class EffectCarrierUpdate(BaseModel):
    """Effect Carrier 업데이트 스키마"""
    name: Optional[str] = None
    carrier_type: Optional[str] = None
    effect_json: Optional[Dict[str, Any]] = None
    constraints_json: Optional[Dict[str, Any]] = None
    source_entity_id: Optional[str] = None
    tags: Optional[List[str]] = None


class EffectCarrierResponse(EffectCarrierBase):
    """Effect Carrier 응답 스키마"""
    effect_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# Items 스키마
# =====================================================

class ItemBase(BaseModel):
    """Item 기본 스키마"""
    item_id: str = Field(..., description="아이템 ID")
    base_property_id: str = Field(..., description="기본 속성 ID")
    item_type: Optional[str] = Field(None, description="아이템 타입")
    stack_size: int = Field(default=1, description="스택 크기")
    consumable: bool = Field(default=False, description="소비 가능 여부")
    item_properties: Dict[str, Any] = Field(default_factory=dict, description="아이템 속성 (JSONB)")
    base_property_name: Optional[str] = Field(None, description="기본 속성 이름 (JOIN 결과)")
    base_property_description: Optional[str] = Field(None, description="기본 속성 설명 (JOIN 결과)")


class ItemCreate(ItemBase):
    """Item 생성 스키마"""
    pass


class ItemUpdate(BaseModel):
    """Item 업데이트 스키마"""
    base_property_id: Optional[str] = None
    item_type: Optional[str] = None
    stack_size: Optional[int] = None
    consumable: Optional[bool] = None
    item_properties: Optional[Dict[str, Any]] = None


class ItemResponse(ItemBase):
    """Item 응답 스키마"""
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# 통합 검색 스키마
# =====================================================

class SearchResultItem(BaseModel):
    """검색 결과 항목"""
    entity_type: str = Field(..., description="엔티티 타입")
    entity_id: str = Field(..., description="엔티티 ID")
    name: str = Field(..., description="이름")
    description: Optional[str] = Field(None, description="설명")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="추가 메타데이터")


class SearchResponse(BaseModel):
    """검색 응답 스키마"""
    query: str
    results: List[SearchResultItem]
    total: int
    entity_type_counts: Dict[str, int] = Field(default_factory=dict)


# =====================================================
# 관계 조회 스키마
# =====================================================

class RelationshipItem(BaseModel):
    """관계 항목"""
    entity_type: str
    entity_id: str
    entity_name: str
    relationship_type: str = Field(..., description="관계 타입 (parent, child, owner, owned_by, etc.)")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RelationshipsResponse(BaseModel):
    """관계 조회 응답 스키마"""
    entity_type: str
    entity_id: str
    entity_name: str
    relationships: List[RelationshipItem]


# =====================================================
# 프로젝트 관리 스키마
# =====================================================

class ProjectExportResponse(BaseModel):
    """프로젝트 내보내기 응답 스키마"""
    success: bool
    data: Dict[str, Any]
    message: str


class ProjectImportResponse(BaseModel):
    """프로젝트 가져오기 응답 스키마"""
    success: bool
    stats: Dict[str, int]
    message: str


class ValidationResponse(BaseModel):
    """검증 응답 스키마"""
    success: bool
    issues: Dict[str, List[str]]
    total_issues: int
    message: str
