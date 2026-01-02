# Cell 내 Entity 관리 (간소화 설계)

**⚠️ 이 문서는 [44. 계층적 맵 뷰 시스템 설계 (최종안)](./44_hierarchical_map_view_design.md)에 통합되었습니다.**

이 문서는 Cell 내 Entity 관리의 상세 설계를 담고 있으며, 최종 결정 사항은 44번 문서를 참조하세요.

## 결정 사항

### 3D 뷰 보류
- **이유**: 복잡성이 크고, 우선순위가 낮음
- **대안**: Cell 내 Entity 목록 조회 및 기본 위치 설정
- **추후**: 필요시 3D 뷰 추가 가능

### 핵심 기능
1. **Cell 내 Entity 목록 조회**: Cell에 속한 모든 Entity 조회
2. **Entity 기본 위치 설정**: game_data에 좌표 기본값 저장
3. **위치 충돌 방지**: Entity 배치 시 충돌 검사

## 데이터 모델 확장

### 1. Entity 기본 위치 필드 추가

```sql
-- game_data.entities 테이블에 기본 위치 필드 추가
ALTER TABLE game_data.entities
ADD COLUMN IF NOT EXISTS default_position_3d JSONB;

-- 기본값: null (위치 미설정)
-- 구조 (설정 시):
-- {
--   "x": 5.0,
--   "y": 4.0,
--   "z": 0.0,
--   "rotation_y": 0,
--   "cell_id": "CELL_MARKET_001"
-- }

COMMENT ON COLUMN game_data.entities.default_position_3d IS '엔티티 기본 위치 (3D 좌표, cell_id 포함)';
```

### 1-1. Entity 크기 필드 추가

```sql
-- game_data.entities 테이블에 크기 필드 추가
ALTER TABLE game_data.entities
ADD COLUMN IF NOT EXISTS entity_size VARCHAR(20);

-- D&D 스타일 크기 타입:
-- 'tiny' (초소형) - 0.5x0.5
-- 'small' (소형) - 1x1
-- 'medium' (중형) - 1x1 (기본값)
-- 'large' (대형) - 2x2
-- 'huge' (거대형) - 3x3
-- 'gargantuan' (초거대형) - 4x4 이상

-- 기본값 설정
ALTER TABLE game_data.entities
ALTER COLUMN entity_size SET DEFAULT 'medium';

-- 기존 데이터에 기본값 설정
UPDATE game_data.entities
SET entity_size = 'medium'
WHERE entity_size IS NULL;

COMMENT ON COLUMN game_data.entities.entity_size IS '엔티티 크기 (D&D 스타일: tiny, small, medium, large, huge, gargantuan)';
```

### 2. 위치 충돌 검사 로직 (크기 고려)

```python
# 크기별 충돌 반경 정의
SIZE_COLLISION_RADIUS = {
    'tiny': 0.25,      # 0.5x0.5 공간
    'small': 0.5,      # 1x1 공간
    'medium': 0.5,     # 1x1 공간 (기본)
    'large': 1.0,      # 2x2 공간
    'huge': 1.5,       # 3x3 공간
    'gargantuan': 2.0  # 4x4 이상 공간
}

async def check_position_collision(
    cell_id: str,
    position: Dict[str, float],
    entity_size: str = 'medium',
    exclude_entity_id: Optional[str] = None
) -> bool:
    """
    Cell 내 특정 위치에 다른 Entity가 있는지 확인 (크기 고려)
    
    Args:
        cell_id: 셀 ID
        position: 확인할 위치 {"x": 5.0, "y": 4.0, "z": 0.0}
        entity_size: 엔티티 크기 ('tiny', 'small', 'medium', 'large', 'huge', 'gargantuan')
        exclude_entity_id: 제외할 엔티티 ID (수정 시 자신 제외)
    
    Returns:
        True: 충돌 있음, False: 충돌 없음
    """
    # 같은 cell_id를 가진 다른 Entity들의 위치와 크기 확인
    # 각 Entity의 크기를 고려한 충돌 반경으로 검사
    # 두 Entity의 충돌 반경 합이 거리보다 작으면 충돌
```

## API 설계

### Cell 내 Entity 조회
```python
GET /api/entities/cell/{cell_id}
# 이미 구현되어 있음 (entity_service.get_entities_by_cell)
```

### Entity 기본 위치 설정
```python
PUT /api/entities/{entity_id}
{
  "default_position_3d": {
    "x": 5.0,
    "y": 4.0,
    "z": 0.0,
    "rotation_y": 90,
    "cell_id": "CELL_MARKET_001"
  },
  "entity_size": "medium"  # 새로 추가
}
```

### 위치 충돌 검사
```python
POST /api/entities/check-position
{
  "cell_id": "CELL_MARKET_001",
  "position": {"x": 5.0, "y": 4.0, "z": 0.0},
  "entity_size": "medium",  # 새로 추가
  "exclude_entity_id": "NPC_MERCHANT_001"  # 선택적
}

Response:
{
  "collision": false,
  "nearby_entities": [
    {
      "entity_id": "NPC_001",
      "distance": 2.5,
      "entity_size": "large",
      "collision_radius": 1.0
    }
  ],
  "collision_radius": 0.5  # 요청한 Entity의 충돌 반경
}
```

## 프론트엔드 구현

### Cell 편집기 확장

#### 현재 구조
```
CellEditorModal
├─ 기본 정보
├─ 엔티티 목록 (현재 구현됨)
│   ├─ Entity 목록 표시
│   ├─ + Add 버튼
│   ├─ 편집 버튼
│   └─ 삭제 버튼
└─ World Objects
```

#### 추가 기능
```
CellEditorModal
├─ 기본 정보
├─ 엔티티 목록
│   ├─ Entity 목록 표시
│   │   └─ 각 Entity에 위치 정보 표시 (x, y, z)
│   ├─ + Add 버튼
│   ├─ 편집 버튼
│   │   └─ EntityEditorModal에서 위치 편집
│   └─ 삭제 버튼
└─ World Objects
```

### Entity 편집기 확장

#### 위치 편집 섹션 추가
```
EntityEditorModal
├─ 기본 정보
│   └─ 크기 (Size) - 새로 추가
│       └─ 드롭다운: tiny, small, medium, large, huge, gargantuan
├─ 능력치
├─ 장비
├─ 인벤토리
├─ 속성
└─ 위치 설정 (새로 추가)
    ├─ Cell 선택
    ├─ X 좌표
    ├─ Y 좌표
    ├─ Z 좌표
    ├─ 회전 (Y축)
    └─ [충돌 검사] 버튼
```

## 위치 충돌 방지 로직

### 충돌 검사 알고리즘 (크기 고려)

```python
# 크기별 충돌 반경 정의
SIZE_COLLISION_RADIUS = {
    'tiny': 0.25,      # 0.5x0.5 공간
    'small': 0.5,      # 1x1 공간
    'medium': 0.5,     # 1x1 공간 (기본)
    'large': 1.0,      # 2x2 공간
    'huge': 1.5,       # 3x3 공간
    'gargantuan': 2.0  # 4x4 이상 공간
}

def check_collision(
    position1: Dict[str, float],
    size1: str,
    position2: Dict[str, float],
    size2: str
) -> bool:
    """
    두 위치가 충돌하는지 확인 (크기 고려)
    
    Args:
        position1: 첫 번째 위치 {"x": 5.0, "y": 4.0, "z": 0.0}
        size1: 첫 번째 Entity 크기 ('tiny', 'small', 'medium', 'large', 'huge', 'gargantuan')
        position2: 두 번째 위치 {"x": 5.5, "y": 4.0, "z": 0.0}
        size2: 두 번째 Entity 크기
    
    Returns:
        True: 충돌, False: 충돌 없음
    """
    # 거리 계산
    dx = position1.get('x', 0) - position2.get('x', 0)
    dy = position1.get('y', 0) - position2.get('y', 0)
    dz = position1.get('z', 0) - position2.get('z', 0)
    distance = math.sqrt(dx*dx + dy*dy + dz*dz)
    
    # 각 Entity의 충돌 반경 가져오기
    radius1 = SIZE_COLLISION_RADIUS.get(size1, 0.5)
    radius2 = SIZE_COLLISION_RADIUS.get(size2, 0.5)
    
    # 두 충돌 반경의 합이 거리보다 크면 충돌
    return distance < (radius1 + radius2)
```

### 자동 위치 배치

```python
async def find_free_position(
    cell_id: str,
    start_x: float = 0.0,
    start_y: float = 0.0,
    start_z: float = 0.0,
    grid_size: float = 1.0
) -> Dict[str, float]:
    """
    Cell 내 빈 위치 찾기
    
    Args:
        cell_id: 셀 ID
        start_x, start_y, start_z: 시작 위치
        grid_size: 그리드 크기
    
    Returns:
        빈 위치 {"x": 5.0, "y": 4.0, "z": 0.0}
    """
    # 그리드 기반으로 빈 위치 탐색
    # 충돌이 없는 위치 반환
```

## 구현 단계

### Phase 1: 데이터 모델 확장
1. `game_data.entities`에 `default_position_3d` 필드 추가
2. `game_data.entities`에 `entity_size` 필드 추가 (D&D 스타일)
3. 마이그레이션 스크립트 작성
4. Pydantic 스키마 업데이트

### Phase 2: 백엔드 API
1. Entity 기본 위치 업데이트 API (크기 포함)
2. Entity 크기 업데이트 API
3. 위치 충돌 검사 API (크기 고려)
4. 자동 위치 배치 API (선택적, 크기 고려)

### Phase 3: 프론트엔드
1. EntityEditorModal에 크기 선택 필드 추가 (기본 정보 섹션)
2. EntityEditorModal에 위치 편집 섹션 추가
3. CellEditorModal에서 Entity 위치 정보 및 크기 표시
4. 충돌 검사 UI (경고 표시, 크기 고려)

### Phase 4: 검증 및 테스트
1. 위치 충돌 검사 테스트
2. Entity 목록 조회 테스트
3. 위치 업데이트 테스트

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

### 크기 타입 정의
```python
from enum import Enum

class EntitySize(str, Enum):
    """D&D 스타일 엔티티 크기"""
    TINY = "tiny"          # 초소형 (0.5x0.5)
    SMALL = "small"        # 소형 (1x1)
    MEDIUM = "medium"      # 중형 (1x1, 기본값)
    LARGE = "large"        # 대형 (2x2)
    HUGE = "huge"          # 거대형 (3x3)
    GARGANTUAN = "gargantuan"  # 초거대형 (4x4 이상)
```

### 크기별 충돌 반경 매핑
```python
SIZE_COLLISION_RADIUS = {
    EntitySize.TINY: 0.25,
    EntitySize.SMALL: 0.5,
    EntitySize.MEDIUM: 0.5,
    EntitySize.LARGE: 1.0,
    EntitySize.HUGE: 1.5,
    EntitySize.GARGANTUAN: 2.0
}
```

## 우선순위

1. **High**: Cell 내 Entity 목록 조회 (이미 구현됨)
2. **High**: Entity 기본 위치 필드 추가
3. **High**: Entity 크기 필드 추가 (D&D 스타일)
4. **Medium**: 위치 편집 UI
5. **Medium**: 크기 선택 UI
6. **Medium**: 위치 충돌 검사 (크기 고려)
7. **Low**: 자동 위치 배치 (크기 고려)

## 3D 뷰는 추후

- 현재는 2D 그리드 기반 위치 편집
- 나중에 필요시 3D 뷰 추가 가능
- 데이터 구조는 3D를 지원하도록 설계

