# World Objects & Effect Carriers API 설계

## 개요

Cell이 소유할 수 있는 World Objects와 Entity가 소유할 수 있는 Effect Carriers를 관리하기 위한 API 설계 문서입니다.

## 1. World Objects API

### 1.1 데이터베이스 스키마

```sql
CREATE TABLE game_data.world_objects (
    object_id VARCHAR(50) PRIMARY KEY,
    object_type VARCHAR(50) NOT NULL,  -- 'static', 'interactive', 'trigger'
    object_name VARCHAR(100) NOT NULL,
    object_description TEXT,
    default_cell_id VARCHAR(50),  -- Cell에 연결
    default_position JSONB,  -- {"x": 0, "y": 0}
    interaction_type VARCHAR(50),  -- 'none', 'openable', 'triggerable'
    possible_states JSONB,  -- {"closed": {...}, "open": {...}}
    properties JSONB,  -- 추가 속성
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (default_cell_id) REFERENCES game_data.world_cells(cell_id) ON DELETE SET NULL
);
```

### 1.2 API 엔드포인트

#### 기본 CRUD

```
GET    /api/world-objects                    # 모든 오브젝트 조회
GET    /api/world-objects/{object_id}       # 특정 오브젝트 조회
POST   /api/world-objects                   # 새 오브젝트 생성
PUT    /api/world-objects/{object_id}       # 오브젝트 업데이트
DELETE /api/world-objects/{object_id}        # 오브젝트 삭제
```

#### Cell 관련 조회

```
GET    /api/world-objects/cell/{cell_id}     # 특정 Cell의 모든 오브젝트 조회
```

### 1.3 요청/응답 스키마

#### WorldObjectBase
```python
class WorldObjectBase(BaseModel):
    object_type: str = Field(..., description="오브젝트 타입 (static, interactive, trigger)")
    object_name: str = Field(..., description="오브젝트 이름")
    object_description: Optional[str] = Field(None, description="오브젝트 설명")
    default_cell_id: Optional[str] = Field(None, description="기본 Cell ID")
    default_position: Dict[str, Any] = Field(default_factory=dict, description="기본 위치 (JSONB)")
    interaction_type: Optional[str] = Field(None, description="상호작용 타입 (none, openable, triggerable)")
    possible_states: Dict[str, Any] = Field(default_factory=dict, description="가능한 상태들 (JSONB)")
    properties: Dict[str, Any] = Field(default_factory=dict, description="추가 속성 (JSONB)")
```

#### WorldObjectCreate
```python
class WorldObjectCreate(WorldObjectBase):
    object_id: str = Field(..., description="오브젝트 ID (명명 규칙: OBJ_[타입]_[이름]_[일련번호])")
```

#### WorldObjectUpdate
```python
class WorldObjectUpdate(BaseModel):
    object_type: Optional[str] = None
    object_name: Optional[str] = None
    object_description: Optional[str] = None
    default_cell_id: Optional[str] = None
    default_position: Optional[Dict[str, Any]] = None
    interaction_type: Optional[str] = None
    possible_states: Optional[Dict[str, Any]] = None
    properties: Optional[Dict[str, Any]] = None
```

#### WorldObjectResponse
```python
class WorldObjectResponse(WorldObjectBase):
    object_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

### 1.4 예시 요청/응답

#### POST /api/world-objects
```json
{
  "object_id": "OBJ_INTERACTIVE_CHEST_001",
  "object_type": "interactive",
  "object_name": "보물 상자",
  "object_description": "열 수 있는 보물 상자",
  "default_cell_id": "CELL_TAVERN_MAIN_001",
  "default_position": {"x": 5, "y": 3},
  "interaction_type": "openable",
  "possible_states": {
    "closed": {"locked": false},
    "open": {"empty": false}
  },
  "properties": {
    "loot_table": ["ITEM_GOLD_001", "ITEM_POTION_001"],
    "lock_difficulty": 15
  }
}
```

#### GET /api/world-objects/cell/{cell_id}
```json
[
  {
    "object_id": "OBJ_INTERACTIVE_CHEST_001",
    "object_type": "interactive",
    "object_name": "보물 상자",
    "object_description": "열 수 있는 보물 상자",
    "default_cell_id": "CELL_TAVERN_MAIN_001",
    "default_position": {"x": 5, "y": 3},
    "interaction_type": "openable",
    "possible_states": {...},
    "properties": {...},
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

---

## 2. Effect Carriers API

### 2.1 데이터베이스 스키마

```sql
CREATE TABLE game_data.effect_carriers (
    effect_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    carrier_type VARCHAR(20) NOT NULL CHECK (carrier_type IN ('skill', 'buff', 'item', 'blessing', 'curse', 'ritual')),
    effect_json JSONB NOT NULL,  -- 효과의 세부 데이터
    constraints_json JSONB DEFAULT '{}'::jsonb,  -- 사용 조건 및 제약사항
    source_entity_id VARCHAR(50),  -- Entity에 연결 (출처)
    tags TEXT[],  -- 태그 배열
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_entity_id) REFERENCES game_data.entities(entity_id) ON DELETE SET NULL
);
```

### 2.2 API 엔드포인트

#### 기본 CRUD

```
GET    /api/effect-carriers                    # 모든 Effect Carrier 조회
GET    /api/effect-carriers/{effect_id}        # 특정 Effect Carrier 조회
POST   /api/effect-carriers                   # 새 Effect Carrier 생성
PUT    /api/effect-carriers/{effect_id}        # Effect Carrier 업데이트
DELETE /api/effect-carriers/{effect_id}        # Effect Carrier 삭제
```

#### Entity 관련 조회

```
GET    /api/effect-carriers/entity/{entity_id}  # 특정 Entity가 소유한 모든 Effect Carrier 조회
GET    /api/effect-carriers/type/{carrier_type} # 특정 타입의 모든 Effect Carrier 조회
```

#### 필터링 및 검색

```
GET    /api/effect-carriers?carrier_type={type}&source_entity_id={id}&tags={tag1,tag2}  # 필터링
```

### 2.3 요청/응답 스키마

#### EffectCarrierBase
```python
class EffectCarrierBase(BaseModel):
    name: str = Field(..., description="Effect Carrier 이름")
    carrier_type: str = Field(..., description="타입 (skill, buff, item, blessing, curse, ritual)")
    effect_json: Dict[str, Any] = Field(..., description="효과의 세부 데이터 (JSONB)")
    constraints_json: Dict[str, Any] = Field(default_factory=dict, description="사용 조건 및 제약사항 (JSONB)")
    source_entity_id: Optional[str] = Field(None, description="출처 Entity ID")
    tags: List[str] = Field(default_factory=list, description="태그 배열")
```

#### EffectCarrierCreate
```python
class EffectCarrierCreate(EffectCarrierBase):
    effect_id: Optional[UUID] = Field(None, description="Effect ID (생략 시 자동 생성)")
```

#### EffectCarrierUpdate
```python
class EffectCarrierUpdate(BaseModel):
    name: Optional[str] = None
    carrier_type: Optional[str] = None
    effect_json: Optional[Dict[str, Any]] = None
    constraints_json: Optional[Dict[str, Any]] = None
    source_entity_id: Optional[str] = None
    tags: Optional[List[str]] = None
```

#### EffectCarrierResponse
```python
class EffectCarrierResponse(EffectCarrierBase):
    effect_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

### 2.4 예시 요청/응답

#### POST /api/effect-carriers
```json
{
  "name": "신의 축복",
  "carrier_type": "blessing",
  "effect_json": {
    "strength_mod": 10,
    "duration": 3600,
    "description": "힘이 10 증가합니다"
  },
  "constraints_json": {
    "requires_prayer": true,
    "cooldown": 86400
  },
  "source_entity_id": "NPC_PRIEST_001",
  "tags": ["divine", "buff", "temporary"]
}
```

#### GET /api/effect-carriers/entity/{entity_id}
```json
[
  {
    "effect_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "신의 축복",
    "carrier_type": "blessing",
    "effect_json": {...},
    "constraints_json": {...},
    "source_entity_id": "NPC_PRIEST_001",
    "tags": ["divine", "buff", "temporary"],
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

#### GET /api/effect-carriers?carrier_type=buff&tags=divine
```json
[
  {
    "effect_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "신의 축복",
    "carrier_type": "blessing",
    ...
  }
]
```

---

## 3. 구현 파일 구조

### 3.1 백엔드 파일 구조

```
app/world_editor/
├── routes/
│   ├── world_objects.py          # World Objects API 라우터
│   └── effect_carriers.py         # Effect Carriers API 라우터
├── services/
│   ├── world_object_service.py    # World Objects 비즈니스 로직
│   └── effect_carrier_service.py  # Effect Carriers 비즈니스 로직
└── schemas.py                     # Pydantic 스키마 추가
```

### 3.2 프론트엔드 파일 구조

```
app/world_editor/frontend/src/
├── services/
│   └── api.ts                    # API 클라이언트 추가
└── components/
    ├── WorldObjectEditorModal.tsx # World Object 편집 모달
    └── EffectCarrierEditorModal.tsx  # Effect Carrier 편집 모달
```

---

## 4. 구현 우선순위

### Phase 1: World Objects API
1. ✅ 스키마 정의 (`schemas.py`)
2. ✅ 서비스 레이어 (`world_object_service.py`)
3. ✅ API 라우터 (`world_objects.py`)
4. ✅ 메인 앱에 라우터 등록
5. ✅ 프론트엔드 API 클라이언트 추가
6. ✅ Cell 편집기에 World Objects 관리 UI 추가

### Phase 2: Effect Carriers API
1. ✅ 스키마 정의 (`schemas.py`)
2. ✅ 서비스 레이어 (`effect_carrier_service.py`)
3. ✅ API 라우터 (`effect_carriers.py`)
4. ✅ 메인 앱에 라우터 등록
5. ✅ 프론트엔드 API 클라이언트 추가
6. ✅ Entity 편집기에 Effect Carriers 관리 UI 추가

---

## 5. 추가 고려사항

### 5.1 ID 생성 규칙

#### World Objects
- 형식: `OBJ_[타입]_[이름]_[일련번호]`
- 예시: `OBJ_INTERACTIVE_CHEST_001`, `OBJ_STATIC_TREE_001`

#### Effect Carriers
- UUID 자동 생성 (PostgreSQL의 `uuid_generate_v4()` 사용)
- 또는 명시적으로 UUID 제공 가능

### 5.2 검증 규칙

#### World Objects
- `object_type`은 'static', 'interactive', 'trigger' 중 하나여야 함
- `default_cell_id`가 제공된 경우, 해당 Cell이 존재해야 함

#### Effect Carriers
- `carrier_type`은 'skill', 'buff', 'item', 'blessing', 'curse', 'ritual' 중 하나여야 함
- `source_entity_id`가 제공된 경우, 해당 Entity가 존재해야 함
- `effect_json`은 필수이며 비어있을 수 없음

### 5.3 에러 처리

- 404: 리소스를 찾을 수 없음
- 400: 잘못된 요청 (검증 실패)
- 500: 서버 내부 오류

### 5.4 성능 최적화

- Cell별 오브젝트 조회 시 인덱스 활용 (`idx_object_type`, `default_cell_id` 외래키)
- Entity별 Effect Carrier 조회 시 인덱스 활용 (`idx_effect_carriers_type`, `source_entity_id` 외래키)
- 태그 검색 시 GIN 인덱스 활용 (`idx_effect_carriers_tags`)

---

## 6. API 사용 예시

### 6.1 Cell에 World Object 추가

```typescript
// 1. World Object 생성
const object = await worldObjectsApi.create({
  object_id: 'OBJ_INTERACTIVE_CHEST_001',
  object_type: 'interactive',
  object_name: '보물 상자',
  default_cell_id: 'CELL_TAVERN_MAIN_001',
  default_position: { x: 5, y: 3 },
  interaction_type: 'openable',
  properties: { loot_table: ['ITEM_GOLD_001'] }
});

// 2. Cell의 모든 오브젝트 조회
const objects = await worldObjectsApi.getByCell('CELL_TAVERN_MAIN_001');
```

### 6.2 Entity에 Effect Carrier 추가

```typescript
// 1. Effect Carrier 생성
const effect = await effectCarriersApi.create({
  name: '신의 축복',
  carrier_type: 'blessing',
  effect_json: { strength_mod: 10, duration: 3600 },
  source_entity_id: 'NPC_PRIEST_001',
  tags: ['divine', 'buff']
});

// 2. Entity의 모든 Effect Carrier 조회
const effects = await effectCarriersApi.getByEntity('NPC_PRIEST_001');
```

---

## 7. 다음 단계

1. 백엔드 구현 (서비스, 라우터, 스키마)
2. 프론트엔드 API 클라이언트 구현
3. Cell 편집기에 World Objects 관리 UI 추가
4. Entity 편집기에 Effect Carriers 관리 UI 추가
5. 테스트 작성 및 검증

