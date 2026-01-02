# 계층적 맵 뷰 시스템 설계 (최종안)

## 개요

World → Region → Location → Cell의 계층적 맵 시스템으로, 각 레벨에서 적절한 엔티티를 배치하고 관리할 수 있습니다.

**현재 상태**: World Map (Region 배치) 구현 완료  
**다음 단계**: Region Map, Location Map, Cell 내 Entity 관리

## 관련 문서

- [45. 계층적 맵 뷰 시스템 설계 피드백](./45_hierarchical_map_view_feedback.md) - Senior 개발자/디자이너 피드백
- [46. 엔티티 위치 정보 및 3D 뷰 토론](./46_entity_position_discussion.md) - 위치 정보 저장 구조 토론
- [47. Cell 내 Entity 관리 (간소화 설계)](./47_simplified_cell_entity_management.md) - Entity 위치 관리
- [48. Entity 크기 시스템 설계](./48_entity_size_design.md) - D&D 스타일 크기 시스템
- [49. World Objects 기본 특성 시스템 설계](./49_world_object_properties_design.md) - World Objects 특성

## 계층 구조

```
World Map (2D) - Region 배치 ✅ 구현 완료
  └─ Region Map (2D) - Location 배치 (도시 수준, 예: 이오클라)
      └─ Location Map (2D) - Cell 배치 (장소 수준, 예: 시장, 교회)
          └─ Cell 내 Entity 관리 (2D 그리드 기반)
              ├─ Entity 위치 편집 (x, y, z)
              ├─ Entity 크기 관리 (D&D 스타일)
              └─ World Object 특성 관리
```

**⚠️ Deprecated**: Cell 3D 뷰 (블록 배치)는 복잡성 고려하여 보류. 현재는 2D 그리드 기반 위치 편집만 구현.

## 레벨별 상세 설계

### 1. World Map (현재 구현됨)
- **목적**: Region(대륙/대지역) 배치
- **타입**: 2D 맵
- **핀 타입**: `region`
- **배경**: `worldmap.png`

### 2. Region Map (다음 구현)
- **목적**: Location(장소) 배치
- **타입**: 2D 맵
- **핀 타입**: `location`
- **예시**: 이오클라 도시 지도 (시장, 교회, 상점 등)
- **배경**: 각 Region별 맵 이미지 또는 자동 생성 그리드

### 3. Location Map (다음 구현)
- **목적**: Cell(셀) 배치
- **타입**: 2D 맵
- **핀 타입**: `cell`
- **예시**: 시장 내부 지도 (각 셀 위치 표시)
- **배경**: 장소 내부 지도 이미지 또는 그리드

### 4. Cell 내 Entity 관리 (간소화)
- **목적**: Entity 및 World Object 위치 편집
- **타입**: 2D 그리드 기반 편집 (3D 뷰 보류)
- **기능**:
  - Entity 목록 조회
  - Entity 기본 위치 설정 (x, y, z)
  - Entity 크기 관리 (D&D 스타일)
  - 위치 충돌 검사 (크기 고려)
  - World Object 특성 관리

## 데이터 모델

### 맵 메타데이터 확장

```sql
-- map_metadata 테이블에 추가할 필드
ALTER TABLE game_data.map_metadata
ADD COLUMN IF NOT EXISTS map_level VARCHAR(20) DEFAULT 'world',
ADD COLUMN IF NOT EXISTS parent_entity_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS parent_entity_type VARCHAR(20);

-- 기본값 사용 권장: 커스텀 맵만 별도 저장
-- 대부분의 Region/Location은 기본 설정 사용
```

### Entity 기본 위치 및 크기

```sql
-- Entity 기본 위치 필드
ALTER TABLE game_data.entities
ADD COLUMN IF NOT EXISTS default_position_3d JSONB,
ADD COLUMN IF NOT EXISTS entity_size VARCHAR(20) DEFAULT 'medium';

-- default_position_3d 구조:
-- {
--   "x": 5.0,
--   "y": 4.0,
--   "z": 0.0,
--   "rotation_y": 0,
--   "cell_id": "CELL_MARKET_001"
-- }

-- entity_size: 'tiny', 'small', 'medium', 'large', 'huge', 'gargantuan'
-- 충돌 검사에 사용 (크기별 충돌 반경: 0.25 ~ 2.0)
```

### World Objects 기본 특성

```sql
-- World Objects 기본 특성 필드
ALTER TABLE game_data.world_objects
ADD COLUMN IF NOT EXISTS wall_mounted BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS passable BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS movable BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS object_height FLOAT DEFAULT 1.0,
ADD COLUMN IF NOT EXISTS object_width FLOAT DEFAULT 1.0,
ADD COLUMN IF NOT EXISTS object_depth FLOAT DEFAULT 1.0,
ADD COLUMN IF NOT EXISTS object_weight FLOAT DEFAULT 0.0;

-- 객체 타입별 기본값:
-- door: wall_mounted=true, passable=false (상태에 따라 변경), movable=false
-- window: wall_mounted=true, passable=false, movable=false
-- chest: wall_mounted=false, passable=false, movable=true
```

**⚠️ Deprecated**: Cell 3D 블록 배치 데이터는 별도 테이블(`cell_3d_blocks`)로 설계되었으나, 현재는 구현 보류.

## UI/UX 설계

### 뷰 전환 시스템

#### Breadcrumb 네비게이션
```
World > Region: 아르보이아 해 > Location: 그라로로스 섬
```

#### 뷰 전환 버튼
- **"Region 보기"**: Region 핀 선택 시 해당 Region의 맵으로 이동
- **"Location 보기"**: Location 핀 선택 시 해당 Location의 맵으로 이동
- **"상위로"**: 현재 맵의 부모 맵으로 돌아가기

**개선안** (Senior 피드백):
- 미니맵 네비게이션: 상단에 전체 계층 구조 표시
- 빠른 이동: 키보드 단축키 (Ctrl+↑ 상위, Ctrl+↓ 하위)
- 히스토리: 뒤로가기/앞으로가기 지원

### 맵 레벨별 UI

#### World Map
- 왼쪽 사이드바: Region 목록
- 중앙: World 맵 (Region 핀들)
- 오른쪽: Region 편집기

#### Region Map
- 왼쪽 사이드바: Location 목록
- 중앙: Region 맵 (Location 핀들)
- 오른쪽: Location 편집기
- 상단: Breadcrumb + "World로 돌아가기" 버튼

#### Location Map
- 왼쪽 사이드바: Cell 목록
- 중앙: Location 맵 (Cell 핀들)
- 오른쪽: Cell 편집기
- 상단: Breadcrumb + "Region으로 돌아가기" 버튼

#### Cell 편집기 (Entity 관리)
- 기본 정보 탭
- 엔티티 탭
  - Entity 목록 (위치, 크기 표시)
  - 위치 편집 (x, y, z 입력)
  - 크기 선택 (D&D 스타일)
  - 충돌 검사 버튼
- World Objects 탭
  - 기본 특성 편집 (wall_mounted, passable, movable)
  - 크기 편집 (height, width, depth, weight)

**⚠️ Deprecated**: Cell 3D 뷰 (Lego Creator 스타일 블록 배치)는 복잡성 고려하여 보류.

## 구현 단계

### Phase 1: 데이터 모델 확장 ✅ 우선순위 High
1. `map_metadata` 테이블에 `map_level`, `parent_entity_id`, `parent_entity_type` 추가
2. `game_data.entities`에 `default_position_3d`, `entity_size` 필드 추가
3. `game_data.world_objects`에 기본 특성 필드 추가
4. 마이그레이션 스크립트 작성
5. Pydantic 스키마 업데이트

### Phase 2: Region Map 구현 ✅ 우선순위 High
1. Region 선택 시 해당 Region의 맵으로 전환
2. Region 맵이 없으면 자동 생성 (기본 설정)
3. Location 핀 배치 기능
4. Breadcrumb 네비게이션

### Phase 3: Location Map 구현 ✅ 우선순위 High
1. Location 선택 시 해당 Location의 맵으로 전환
2. Location 맵이 없으면 그리드 기반 자동 생성
3. Cell 핀 배치 기능
4. Cell 자동 배치 알고리즘 (그리드 기반)

### Phase 4: Cell 내 Entity 관리 ✅ 우선순위 High
1. Cell 내 Entity 목록 조회 API (이미 구현됨)
2. Entity 기본 위치 설정 (`default_position_3d`)
3. Entity 크기 설정 (`entity_size`, D&D 스타일)
4. 위치 충돌 검사 API (크기 고려)
5. Entity 위치 편집 UI (2D 그리드 기반)
6. World Objects 기본 특성 편집 UI

### Phase 5: 맵 관리 기능 ⚠️ 우선순위 Medium
1. 맵 이미지 업로드 (Region/Location별)
2. 맵 설정 (크기, 그리드 등)
3. 맵 삭제/복제

**⚠️ Deprecated**: Cell 3D 뷰 (블록 배치)는 Phase 5 이후 재검토.

## API 설계

### 맵 조회
```python
GET /api/maps
GET /api/maps/world  # World 맵
GET /api/maps/region/{region_id}  # Region 맵
GET /api/maps/location/{location_id}  # Location 맵
```

### 맵 생성
```python
POST /api/maps
{
  "map_level": "region",
  "parent_entity_id": "REG_CONTINENT_01",
  "parent_entity_type": "region",
  "map_name": "아르보이아 해 맵",
  "width": 1920,
  "height": 1080,
  "background_image": "region_REG_CONTINENT_01_map.png"  # 선택적
}
```

### Entity 위치 관리
```python
# Entity 기본 위치 설정
PUT /api/entities/{entity_id}
{
  "default_position_3d": {
    "x": 5.0,
    "y": 4.0,
    "z": 0.0,
    "rotation_y": 0,
    "cell_id": "CELL_MARKET_001"
  },
  "entity_size": "medium"
}

# 위치 충돌 검사
POST /api/entities/check-position
{
  "cell_id": "CELL_MARKET_001",
  "position": {"x": 5.0, "y": 4.0, "z": 0.0},
  "entity_size": "medium",
  "exclude_entity_id": "NPC_MERCHANT_001"
}
```

### World Objects 특성 관리
```python
PUT /api/world-objects/{object_id}
{
  "wall_mounted": true,
  "passable": false,
  "movable": false,
  "object_height": 2.0,
  "object_width": 1.0,
  "object_depth": 0.1,
  "object_weight": 50.0
}
```

## 핵심 로직

### 위치 충돌 검사 (크기 고려)

```python
SIZE_COLLISION_RADIUS = {
    'tiny': 0.25,
    'small': 0.5,
    'medium': 0.5,
    'large': 1.0,
    'huge': 1.5,
    'gargantuan': 2.0
}

def check_collision(position1, size1, position2, size2) -> bool:
    """두 Entity가 충돌하는지 확인 (크기 고려)"""
    distance = calculate_distance(position1, position2)
    radius1 = SIZE_COLLISION_RADIUS.get(size1, 0.5)
    radius2 = SIZE_COLLISION_RADIUS.get(size2, 0.5)
    return distance < (radius1 + radius2)
```

### World Objects 통과 가능 여부

```python
def can_entity_pass_through(world_object, entity) -> bool:
    """Entity가 World Object를 통과할 수 있는지 확인"""
    if world_object.passable:
        return True
    # 상태에 따라 변경 (예: 문이 열려있으면 통과 가능)
    if world_object.interaction_type == "openable":
        current_state = world_object.possible_states.get("current", "closed")
        if current_state == "open":
            return True
    return False
```

## 성능 고려사항 (Senior 피드백)

1. **지연 로딩**: 필요한 맵만 로드
2. **캐싱**: 최근 사용한 맵 캐시
3. **배치 로딩**: 현재 레벨 + 상위 레벨만 로드
4. **가상화**: 많은 핀을 가진 맵의 경우 가상 스크롤

## 데이터 일관성

### Entity와 Cell 관계
- `entity_properties.cell_id`: Entity가 속한 Cell
- `default_position_3d.cell_id`: 위치가 설정된 Cell
- **일관성 검사**: 두 cell_id가 일치해야 함

### 위치 정보 구조 통일
```json
{
  "x": 5.0,      // 필수
  "y": 4.0,      // 필수
  "z": 0.0,      // 필수 (기본값 0)
  "rotation_y": 0,  // 선택적 (기본값 0)
  "cell_id": "CELL_MARKET_001"  // 필수
}
```

## 우선순위 (최종)

1. **High**: Phase 1 - 데이터 모델 확장
2. **High**: Phase 2 - Region Map 구현
3. **High**: Phase 3 - Location Map 구현
4. **High**: Phase 4 - Cell 내 Entity 관리
5. **Medium**: Phase 5 - 맵 관리 기능
6. **보류**: Cell 3D 뷰 (블록 배치) - Phase 1-4 완료 후 재검토

## 참고사항

- **3D 뷰**: 현재는 2D 그리드 기반 위치 편집만 구현. 3D 뷰는 추후 필요시 추가 가능하도록 데이터 구조는 3D를 지원.
- **맵 메타데이터**: 기본값 사용 권장. 커스텀 맵만 별도 저장하여 데이터 중복 최소화.
- **블록 시스템**: Cell 3D 블록 배치는 복잡성 고려하여 보류. 필요시 별도 테이블(`cell_3d_blocks`)로 구현 가능.
