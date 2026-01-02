# World Objects 기본 특성 시스템 설계

**⚠️ 이 문서는 [44. 계층적 맵 뷰 시스템 설계 (최종안)](./44_hierarchical_map_view_design.md)에 통합되었습니다.**

이 문서는 World Objects 기본 특성 시스템의 상세 설계를 담고 있으며, 최종 결정 사항은 44번 문서를 참조하세요.

## 개요

World Objects (문, 창문, 가구, 장식품 등)의 기본 상호작용 특성을 정의하여 게임 로직에서 활용할 수 있도록 합니다.

## 기본 특성 정의

### 1. 벽 부착 여부 (Wall Mounted)
- **필드명**: `wall_mounted`
- **타입**: `boolean`
- **기본값**: `false`
- **설명**: 객체가 벽에 달려있는지 여부
- **예시**: 문, 창문, 그림, 선반

### 2. 통과 가능 여부 (Passable)
- **필드명**: `passable`
- **타입**: `boolean`
- **기본값**: `false`
- **설명**: Entity가 이 객체를 통과할 수 있는지 여부
- **예시**: 
  - `true`: 열린 문, 투명한 유리, 마법 포털
  - `false`: 벽, 닫힌 문, 가구

### 3. 이동 가능 여부 (Movable)
- **필드명**: `movable`
- **타입**: `boolean`
- **기본값**: `false`
- **설명**: 객체가 이동 가능한지 여부 (밀기, 옮기기)
- **예시**:
  - `true`: 상자, 의자, 테이블
  - `false`: 벽, 문틀, 고정된 가구

### 4. 추가 특성

#### 높이 (Height)
- **필드명**: `height`
- **타입**: `float`
- **기본값**: `1.0`
- **설명**: 객체의 높이 (충돌 검사용)
- **단위**: 미터 또는 게임 단위

#### 너비/깊이 (Width/Depth)
- **필드명**: `width`, `depth`
- **타입**: `float`
- **기본값**: `1.0`
- **설명**: 객체의 너비와 깊이 (충돌 검사용)

#### 무게 (Weight)
- **필드명**: `weight`
- **타입**: `float`
- **기본값**: `0.0`
- **설명**: 객체의 무게 (이동 가능 여부와 연관)

#### 견고도 (Durability)
- **필드명**: `durability`
- **타입**: `integer`
- **기본값**: `100`
- **설명**: 객체의 내구도 (파괴 가능 여부)

## 데이터베이스 스키마

### World Objects 테이블 확장

```sql
-- game_data.world_objects 테이블에 기본 특성 필드 추가
-- 옵션 1: properties JSONB에 포함 (현재 구조 활용)
-- 옵션 2: 별도 필드로 추가 (명시적)

-- 옵션 1 권장: properties JSONB 활용
-- 기존 properties JSONB 구조 확장:
-- {
--   "material": "wood",
--   "durability": 100,
--   "wall_mounted": false,
--   "passable": false,
--   "movable": false,
--   "height": 1.0,
--   "width": 1.0,
--   "depth": 1.0,
--   "weight": 0.0
-- }

-- 또는 별도 필드로 추가 (더 명시적)
ALTER TABLE game_data.world_objects
ADD COLUMN IF NOT EXISTS wall_mounted BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS passable BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS movable BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS object_height FLOAT DEFAULT 1.0,
ADD COLUMN IF NOT EXISTS object_width FLOAT DEFAULT 1.0,
ADD COLUMN IF NOT EXISTS object_depth FLOAT DEFAULT 1.0,
ADD COLUMN IF NOT EXISTS object_weight FLOAT DEFAULT 0.0;

COMMENT ON COLUMN game_data.world_objects.wall_mounted IS '벽에 부착된 객체인지 여부';
COMMENT ON COLUMN game_data.world_objects.passable IS 'Entity가 통과 가능한지 여부';
COMMENT ON COLUMN game_data.world_objects.movable IS '이동 가능한 객체인지 여부';
COMMENT ON COLUMN game_data.world_objects.object_height IS '객체 높이 (충돌 검사용)';
COMMENT ON COLUMN game_data.world_objects.object_width IS '객체 너비 (충돌 검사용)';
COMMENT ON COLUMN game_data.world_objects.object_depth IS '객체 깊이 (충돌 검사용)';
COMMENT ON COLUMN game_data.world_objects.object_weight IS '객체 무게';
```

## 객체 타입별 기본값

### 문 (Door)
```json
{
  "wall_mounted": true,
  "passable": false,  // 닫혀있으면 false, 열려있으면 true
  "movable": false,
  "height": 2.0,
  "width": 1.0,
  "depth": 0.1,
  "weight": 50.0
}
```

### 창문 (Window)
```json
{
  "wall_mounted": true,
  "passable": false,  // 일반적으로 통과 불가
  "movable": false,
  "height": 1.5,
  "width": 1.0,
  "depth": 0.1,
  "weight": 20.0
}
```

### 상자 (Chest/Box)
```json
{
  "wall_mounted": false,
  "passable": false,
  "movable": true,
  "height": 0.8,
  "width": 1.0,
  "depth": 1.0,
  "weight": 30.0
}
```

### 의자 (Chair)
```json
{
  "wall_mounted": false,
  "passable": false,
  "movable": true,
  "height": 1.0,
  "width": 0.5,
  "depth": 0.5,
  "weight": 10.0
}
```

### 테이블 (Table)
```json
{
  "wall_mounted": false,
  "passable": false,  // 아래로는 통과 가능할 수도 있음
  "movable": true,
  "height": 0.8,
  "width": 1.5,
  "depth": 1.0,
  "weight": 40.0
}
```

### 벽 (Wall)
```json
{
  "wall_mounted": false,  // 벽 자체는 부착이 아님
  "passable": false,
  "movable": false,
  "height": 3.0,
  "width": 1.0,
  "depth": 0.2,
  "weight": 0.0  // 무한대 또는 매우 큰 값
}
```

## Pydantic 스키마

### WorldObject 스키마 확장

```python
from typing import Optional
from pydantic import Field, BaseModel

class WorldObjectBase(BaseModel):
    """World Object 기본 스키마"""
    object_type: str
    object_name: str
    object_description: Optional[str] = None
    default_cell_id: Optional[str] = None
    default_position: Dict[str, Any] = Field(default_factory=dict)
    interaction_type: Optional[str] = None
    possible_states: Dict[str, Any] = Field(default_factory=dict)
    
    # 기본 특성 필드 추가
    wall_mounted: bool = Field(default=False, description="벽에 부착된 객체인지 여부")
    passable: bool = Field(default=False, description="Entity가 통과 가능한지 여부")
    movable: bool = Field(default=False, description="이동 가능한 객체인지 여부")
    object_height: float = Field(default=1.0, description="객체 높이")
    object_width: float = Field(default=1.0, description="객체 너비")
    object_depth: float = Field(default=1.0, description="객체 깊이")
    object_weight: float = Field(default=0.0, description="객체 무게")
    
    properties: Dict[str, Any] = Field(default_factory=dict)
```

## API 설계

### World Object 생성/업데이트

```python
POST /api/world-objects
PUT /api/world-objects/{object_id}
{
  "object_type": "door",
  "object_name": "나무 문",
  "default_cell_id": "CELL_HOUSE_001",
  "default_position": {"x": 5.0, "y": 4.0, "z": 0.0},
  "interaction_type": "openable",
  "possible_states": {"closed", "open"},
  "wall_mounted": true,
  "passable": false,  // 상태에 따라 변경 가능
  "movable": false,
  "object_height": 2.0,
  "object_width": 1.0,
  "object_depth": 0.1,
  "object_weight": 50.0,
  "properties": {
    "material": "wood",
    "locked": false
  }
}
```

### 객체 타입별 기본값 API

```python
GET /api/world-objects/type-defaults/{object_type}

Response:
{
  "object_type": "door",
  "default_properties": {
    "wall_mounted": true,
    "passable": false,
    "movable": false,
    "object_height": 2.0,
    "object_width": 1.0,
    "object_depth": 0.1,
    "object_weight": 50.0
  }
}
```

## 게임 로직 활용

### 통과 가능 여부 체크

```python
def can_entity_pass_through(world_object: WorldObject, entity: Entity) -> bool:
    """
    Entity가 World Object를 통과할 수 있는지 확인
    
    Args:
        world_object: World Object
        entity: Entity
    
    Returns:
        True: 통과 가능, False: 통과 불가
    """
    # 기본적으로 passable이 True면 통과 가능
    if world_object.passable:
        return True
    
    # 상태에 따라 변경 (예: 문이 열려있으면 통과 가능)
    if world_object.interaction_type == "openable":
        current_state = world_object.possible_states.get("current", "closed")
        if current_state == "open":
            return True
    
    return False
```

### 이동 가능 여부 체크

```python
def can_entity_move_object(world_object: WorldObject, entity: Entity) -> bool:
    """
    Entity가 World Object를 이동시킬 수 있는지 확인
    
    Args:
        world_object: World Object
        entity: Entity
    
    Returns:
        True: 이동 가능, False: 이동 불가
    """
    # movable이 False면 이동 불가
    if not world_object.movable:
        return False
    
    # Entity의 힘(Strength)과 객체의 무게 비교
    entity_strength = entity.base_stats.get("strength", 10)
    required_strength = world_object.object_weight / 10  # 예: 무게/10 = 필요 힘
    
    return entity_strength >= required_strength
```

### 벽 부착 객체 배치 검증

```python
def validate_wall_mounted_placement(
    world_object: WorldObject,
    position: Dict[str, float],
    cell: Cell
) -> bool:
    """
    벽에 부착된 객체의 배치가 유효한지 확인
    
    Args:
        world_object: World Object
        position: 배치 위치
        cell: Cell 정보
    
    Returns:
        True: 유효, False: 무효
    """
    if not world_object.wall_mounted:
        return True  # 벽 부착이 아니면 검증 불필요
    
    # 벽 위치 확인 (cell_properties에서 벽 정보 가져오기)
    walls = cell.cell_properties.get("walls", [])
    
    # position이 벽 근처인지 확인
    for wall in walls:
        wall_x = wall.get("x", 0)
        wall_y = wall.get("y", 0)
        distance = math.sqrt(
            (position["x"] - wall_x)**2 + 
            (position["y"] - wall_y)**2
        )
        if distance < 0.5:  # 벽 근처면 유효
            return True
    
    return False  # 벽 근처가 아니면 무효
```

## 프론트엔드 구현

### WorldObjectEditorModal 확장

```typescript
// 기본 특성 섹션 추가
<CollapsibleSection title="기본 특성" defaultExpanded={true}>
  <FormField label="벽 부착 (Wall Mounted)">
    <input
      type="checkbox"
      checked={worldObject.wall_mounted || false}
      onChange={(e) => setWorldObject({
        ...worldObject,
        wall_mounted: e.target.checked
      })}
    />
  </FormField>
  
  <FormField label="통과 가능 (Passable)">
    <input
      type="checkbox"
      checked={worldObject.passable || false}
      onChange={(e) => setWorldObject({
        ...worldObject,
        passable: e.target.checked
      })}
    />
  </FormField>
  
  <FormField label="이동 가능 (Movable)">
    <input
      type="checkbox"
      checked={worldObject.movable || false}
      onChange={(e) => setWorldObject({
        ...worldObject,
        movable: e.target.checked
      })}
    />
  </FormField>
  
  <FormField label="높이 (Height)">
    <InputField
      type="number"
      value={worldObject.object_height || 1.0}
      onChange={(val) => setWorldObject({
        ...worldObject,
        object_height: parseFloat(val)
      })}
      min="0"
      step="0.1"
    />
  </FormField>
  
  <FormField label="너비 (Width)">
    <InputField
      type="number"
      value={worldObject.object_width || 1.0}
      onChange={(val) => setWorldObject({
        ...worldObject,
        object_width: parseFloat(val)
      })}
      min="0"
      step="0.1"
    />
  </FormField>
  
  <FormField label="깊이 (Depth)">
    <InputField
      type="number"
      value={worldObject.object_depth || 1.0}
      onChange={(val) => setWorldObject({
        ...worldObject,
        object_depth: parseFloat(val)
      })}
      min="0"
      step="0.1"
    />
  </FormField>
  
  <FormField label="무게 (Weight)">
    <InputField
      type="number"
      value={worldObject.object_weight || 0.0}
      onChange={(val) => setWorldObject({
        ...worldObject,
        object_weight: parseFloat(val)
      })}
      min="0"
      step="0.1"
    />
  </FormField>
</CollapsibleSection>
```

### 객체 타입별 기본값 자동 설정

```typescript
const OBJECT_TYPE_DEFAULTS: Record<string, Partial<WorldObject>> = {
  "door": {
    wall_mounted: true,
    passable: false,
    movable: false,
    object_height: 2.0,
    object_width: 1.0,
    object_depth: 0.1,
    object_weight: 50.0
  },
  "window": {
    wall_mounted: true,
    passable: false,
    movable: false,
    object_height: 1.5,
    object_width: 1.0,
    object_depth: 0.1,
    object_weight: 20.0
  },
  "chest": {
    wall_mounted: false,
    passable: false,
    movable: true,
    object_height: 0.8,
    object_width: 1.0,
    object_depth: 1.0,
    object_weight: 30.0
  },
  "chair": {
    wall_mounted: false,
    passable: false,
    movable: true,
    object_height: 1.0,
    object_width: 0.5,
    object_depth: 0.5,
    object_weight: 10.0
  },
  "table": {
    wall_mounted: false,
    passable: false,
    movable: true,
    object_height: 0.8,
    object_width: 1.5,
    object_depth: 1.0,
    object_weight: 40.0
  }
};

// 객체 타입 선택 시 기본값 자동 적용
const handleObjectTypeChange = (objectType: string) => {
  const defaults = OBJECT_TYPE_DEFAULTS[objectType] || {};
  setWorldObject({
    ...worldObject,
    object_type: objectType,
    ...defaults
  });
};
```

## 마이그레이션 스크립트

```sql
-- database/setup/add_world_object_properties_migration.sql

-- 1. 기본 특성 필드 추가
ALTER TABLE game_data.world_objects
ADD COLUMN IF NOT EXISTS wall_mounted BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS passable BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS movable BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS object_height FLOAT DEFAULT 1.0,
ADD COLUMN IF NOT EXISTS object_width FLOAT DEFAULT 1.0,
ADD COLUMN IF NOT EXISTS object_depth FLOAT DEFAULT 1.0,
ADD COLUMN IF NOT EXISTS object_weight FLOAT DEFAULT 0.0;

-- 2. 기존 데이터에 기본값 설정 (이미 설정됨)

-- 3. 코멘트 추가
COMMENT ON COLUMN game_data.world_objects.wall_mounted IS '벽에 부착된 객체인지 여부';
COMMENT ON COLUMN game_data.world_objects.passable IS 'Entity가 통과 가능한지 여부';
COMMENT ON COLUMN game_data.world_objects.movable IS '이동 가능한 객체인지 여부';
COMMENT ON COLUMN game_data.world_objects.object_height IS '객체 높이 (충돌 검사용)';
COMMENT ON COLUMN game_data.world_objects.object_width IS '객체 너비 (충돌 검사용)';
COMMENT ON COLUMN game_data.world_objects.object_depth IS '객체 깊이 (충돌 검사용)';
COMMENT ON COLUMN game_data.world_objects.object_weight IS '객체 무게';

-- 4. 객체 타입별 기본값 업데이트 (선택적)
UPDATE game_data.world_objects
SET 
  wall_mounted = TRUE,
  object_height = 2.0,
  object_width = 1.0,
  object_depth = 0.1,
  object_weight = 50.0
WHERE object_type = 'door' AND wall_mounted IS NULL;

UPDATE game_data.world_objects
SET 
  wall_mounted = TRUE,
  object_height = 1.5,
  object_width = 1.0,
  object_depth = 0.1,
  object_weight = 20.0
WHERE object_type = 'window' AND wall_mounted IS NULL;
```

## 구현 체크리스트

- [ ] 데이터베이스 마이그레이션 스크립트 작성
- [ ] Pydantic 스키마에 기본 특성 필드 추가
- [ ] WorldObjectService에서 기본 특성 처리
- [ ] 객체 타입별 기본값 로직 구현
- [ ] API 엔드포인트 업데이트
- [ ] 프론트엔드 WorldObjectEditorModal에 기본 특성 UI 추가
- [ ] 객체 타입 선택 시 기본값 자동 적용
- [ ] 통과 가능 여부 체크 로직 구현
- [ ] 이동 가능 여부 체크 로직 구현
- [ ] 벽 부착 객체 배치 검증 로직 구현
- [ ] 테스트 케이스 작성

