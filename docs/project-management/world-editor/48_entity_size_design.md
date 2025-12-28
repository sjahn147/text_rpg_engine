# Entity 크기 시스템 설계

**⚠️ 이 문서는 [44. 계층적 맵 뷰 시스템 설계 (최종안)](./44_hierarchical_map_view_design.md)에 통합되었습니다.**

이 문서는 Entity 크기 시스템의 상세 설계를 담고 있으며, 최종 결정 사항은 44번 문서를 참조하세요.

## 개요

D&D 스타일의 크기 시스템을 도입하여 Entity의 물리적 크기를 관리하고, 충돌 판정에 활용합니다.

## 크기 타입 정의

### D&D 5e 크기 시스템 기반

| 크기 | 한국어 | 공간 크기 | 충돌 반경 | 예시 |
|------|--------|-----------|-----------|------|
| `tiny` | 초소형 | 0.5x0.5 | 0.25 | 쥐, 작은 새 |
| `small` | 소형 | 1x1 | 0.5 | 고블린, 할플링 |
| `medium` | 중형 | 1x1 | 0.5 | 인간, 엘프, 드워프 |
| `large` | 대형 | 2x2 | 1.0 | 말, 곰, 오거 |
| `huge` | 거대형 | 3x3 | 1.5 | 거인, 용 (중형) |
| `gargantuan` | 초거대형 | 4x4 이상 | 2.0 | 고대 용, 크라켄 |

## 데이터베이스 스키마

### Entity 크기 필드 추가

```sql
-- game_data.entities 테이블에 크기 필드 추가
ALTER TABLE game_data.entities
ADD COLUMN IF NOT EXISTS entity_size VARCHAR(20);

-- 제약조건: 허용된 크기 값만 입력 가능
ALTER TABLE game_data.entities
ADD CONSTRAINT chk_entity_size CHECK (
    entity_size IN ('tiny', 'small', 'medium', 'large', 'huge', 'gargantuan')
);

-- 기본값 설정 (중형)
ALTER TABLE game_data.entities
ALTER COLUMN entity_size SET DEFAULT 'medium';

-- 기존 데이터에 기본값 설정
UPDATE game_data.entities
SET entity_size = 'medium'
WHERE entity_size IS NULL;

-- NOT NULL 제약조건 추가
ALTER TABLE game_data.entities
ALTER COLUMN entity_size SET NOT NULL;

COMMENT ON COLUMN game_data.entities.entity_size IS '엔티티 크기 (D&D 스타일: tiny, small, medium, large, huge, gargantuan)';
```

## Pydantic 스키마

### Entity 스키마 확장

```python
from enum import Enum
from typing import Optional
from pydantic import Field

class EntitySize(str, Enum):
    """D&D 스타일 엔티티 크기"""
    TINY = "tiny"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    HUGE = "huge"
    GARGANTUAN = "gargantuan"

class EntityBase(BaseModel):
    """엔티티 기본 스키마"""
    entity_type: str
    entity_name: str
    entity_description: Optional[str] = None
    entity_size: EntitySize = Field(default=EntitySize.MEDIUM, description="엔티티 크기")
    base_stats: Dict[str, Any] = Field(default_factory=dict)
    # ... 기타 필드
```

## 충돌 검사 로직

### 크기별 충돌 반경

```python
SIZE_COLLISION_RADIUS = {
    EntitySize.TINY: 0.25,
    EntitySize.SMALL: 0.5,
    EntitySize.MEDIUM: 0.5,
    EntitySize.LARGE: 1.0,
    EntitySize.HUGE: 1.5,
    EntitySize.GARGANTUAN: 2.0
}

def get_collision_radius(entity_size: EntitySize) -> float:
    """엔티티 크기에 따른 충돌 반경 반환"""
    return SIZE_COLLISION_RADIUS.get(entity_size, 0.5)

def check_collision(
    position1: Dict[str, float],
    size1: EntitySize,
    position2: Dict[str, float],
    size2: EntitySize
) -> bool:
    """
    두 Entity가 충돌하는지 확인 (크기 고려)
    
    Args:
        position1: 첫 번째 Entity 위치
        size1: 첫 번째 Entity 크기
        position2: 두 번째 Entity 위치
        size2: 두 번째 Entity 크기
    
    Returns:
        True: 충돌, False: 충돌 없음
    """
    # 거리 계산
    dx = position1.get('x', 0) - position2.get('x', 0)
    dy = position1.get('y', 0) - position2.get('y', 0)
    dz = position1.get('z', 0) - position2.get('z', 0)
    distance = math.sqrt(dx*dx + dy*dy + dz*dz)
    
    # 각 Entity의 충돌 반경
    radius1 = get_collision_radius(size1)
    radius2 = get_collision_radius(size2)
    
    # 두 충돌 반경의 합이 거리보다 크면 충돌
    return distance < (radius1 + radius2)
```

## API 설계

### Entity 생성/업데이트

```python
POST /api/entities
PUT /api/entities/{entity_id}
{
  "entity_name": "NPC_MERCHANT_001",
  "entity_type": "npc",
  "entity_size": "medium",  # 새로 추가
  "default_position_3d": {
    "x": 5.0,
    "y": 4.0,
    "z": 0.0,
    "cell_id": "CELL_MARKET_001"
  }
}
```

### 위치 충돌 검사 (크기 고려)

```python
POST /api/entities/check-position
{
  "cell_id": "CELL_MARKET_001",
  "position": {"x": 5.0, "y": 4.0, "z": 0.0},
  "entity_size": "large",  # 크기 필수
  "exclude_entity_id": "NPC_MERCHANT_001"
}

Response:
{
  "collision": true,
  "colliding_entities": [
    {
      "entity_id": "NPC_001",
      "entity_name": "상인",
      "entity_size": "medium",
      "position": {"x": 5.2, "y": 4.0, "z": 0.0},
      "distance": 0.2,
      "collision_radius_self": 1.0,  # large
      "collision_radius_other": 0.5,  # medium
      "combined_radius": 1.5
    }
  ]
}
```

## 프론트엔드 구현

### EntityEditorModal 확장

```typescript
// 기본 정보 섹션에 크기 선택 추가
<FormField label="크기 (Size)">
  <select
    value={entity.entity_size || 'medium'}
    onChange={(e) => setEntity({ ...entity, entity_size: e.target.value })}
  >
    <option value="tiny">초소형 (Tiny) - 0.5x0.5</option>
    <option value="small">소형 (Small) - 1x1</option>
    <option value="medium">중형 (Medium) - 1x1</option>
    <option value="large">대형 (Large) - 2x2</option>
    <option value="huge">거대형 (Huge) - 3x3</option>
    <option value="gargantuan">초거대형 (Gargantuan) - 4x4+</option>
  </select>
</FormField>
```

### CellEditorModal에서 크기 표시

```typescript
// Entity 목록에 크기 정보 표시
{entities.map(entity => (
  <div key={entity.entity_id}>
    <span>{entity.entity_name}</span>
    <span>크기: {getSizeLabel(entity.entity_size)}</span>
    {entity.default_position_3d && (
      <span>
        위치: ({entity.default_position_3d.x}, {entity.default_position_3d.y}, {entity.default_position_3d.z})
      </span>
    )}
  </div>
))}
```

## 마이그레이션 스크립트

```sql
-- database/setup/add_entity_size_migration.sql

-- 1. 컬럼 추가
ALTER TABLE game_data.entities
ADD COLUMN IF NOT EXISTS entity_size VARCHAR(20);

-- 2. 기본값 설정
UPDATE game_data.entities
SET entity_size = 'medium'
WHERE entity_size IS NULL;

-- 3. 제약조건 추가
ALTER TABLE game_data.entities
ADD CONSTRAINT chk_entity_size CHECK (
    entity_size IN ('tiny', 'small', 'medium', 'large', 'huge', 'gargantuan')
);

-- 4. NOT NULL 제약조건
ALTER TABLE game_data.entities
ALTER COLUMN entity_size SET NOT NULL;

-- 5. 기본값 설정 (새로 추가되는 Entity용)
ALTER TABLE game_data.entities
ALTER COLUMN entity_size SET DEFAULT 'medium';

-- 6. 코멘트 추가
COMMENT ON COLUMN game_data.entities.entity_size IS '엔티티 크기 (D&D 스타일: tiny, small, medium, large, huge, gargantuan)';
```

## 테스트 케이스

### 충돌 검사 테스트

```python
def test_collision_detection():
    # 중형 Entity 두 개가 가까이 있을 때
    assert check_collision(
        {"x": 5.0, "y": 4.0, "z": 0.0}, EntitySize.MEDIUM,
        {"x": 5.4, "y": 4.0, "z": 0.0}, EntitySize.MEDIUM
    ) == True  # 거리 0.4 < 반경 합 1.0
    
    # 대형과 중형이 충돌
    assert check_collision(
        {"x": 5.0, "y": 4.0, "z": 0.0}, EntitySize.LARGE,
        {"x": 6.0, "y": 4.0, "z": 0.0}, EntitySize.MEDIUM
    ) == True  # 거리 1.0 < 반경 합 1.5
    
    # 충돌 없음
    assert check_collision(
        {"x": 5.0, "y": 4.0, "z": 0.0}, EntitySize.MEDIUM,
        {"x": 7.0, "y": 4.0, "z": 0.0}, EntitySize.MEDIUM
    ) == False  # 거리 2.0 > 반경 합 1.0
```

## 구현 체크리스트

- [ ] 데이터베이스 마이그레이션 스크립트 작성
- [ ] Pydantic 스키마에 `EntitySize` Enum 추가
- [ ] `EntityBase`, `EntityCreate`, `EntityUpdate`, `EntityResponse`에 `entity_size` 필드 추가
- [ ] `EntityService`에서 크기 필드 처리
- [ ] 충돌 검사 로직에 크기 반영
- [ ] API 엔드포인트 업데이트
- [ ] 프론트엔드 EntityEditorModal에 크기 선택 추가
- [ ] CellEditorModal에서 크기 정보 표시
- [ ] 충돌 검사 API 테스트
- [ ] 통합 테스트

