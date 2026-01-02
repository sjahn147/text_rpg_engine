# 데이터 무결성 문제 해결 상태 검토

**검토 일자**: 2025-12-30  
**참고 문서**: DB Schema Review for mvp_schema.sql

## 개요

이 문서는 RPG 게임 엔진의 데이터 무결성 문제를 0~6순위로 분류하여 해결 상태를 검토합니다. 
3계층 구조(game_data, reference_layer, runtime_data)를 기반으로 한 스키마 설계의 무결성 강화 작업을 추적합니다.

## 0순위 (즉시) — ID/타입 혼용으로 인한 FK/조인 붕괴

### 해결 상태: 대부분 해결

#### 완료된 작업:
1. **스키마 레벨 UUID 통일**
   - `reference_layer.cell_references.runtime_cell_id`: UUID
   - `reference_layer.object_references.runtime_object_id`: UUID
   - `runtime_data.runtime_cells.runtime_cell_id`: UUID
   - `runtime_data.runtime_entities.runtime_entity_id`: UUID
   - `runtime_data.cell_occupants`: `runtime_cell_id`, `runtime_entity_id` 모두 UUID

2. **데이터 마이그레이션 완료**
   - UUID가 아닌 값 50개 삭제
   - VARCHAR → UUID 타입 변환 완료

3. **FK 제약조건 추가**
   - 모든 runtime 레이어 FK가 UUID 타입으로 강제됨

#### 현재 구현 상태:

**매니저 레벨에서 타입 유연성 제공**
- `Union[str, UUID]` 타입으로 문자열과 UUID 모두 수용
- PostgreSQL 자동 변환 활용

**구현 예시:**
```python
# app/managers/cell_manager.py:928
async def add_entity_to_cell(
    self, 
    runtime_entity_id: Union[str, UUID], 
    runtime_cell_id: Union[str, UUID]
) -> CellResult:
    # PostgreSQL이 자동으로 타입 변환 처리
```

**남은 문제:**

**코드 레벨 타입 혼용**
- `Union[str, UUID]` 사용
- `app/managers/cell_manager.py`: `add_entity_to_cell(runtime_entity_id: Union[str, UUID], ...)`
- PostgreSQL은 자동 변환하지만, 타입 안정성을 위해 UUID로 통일 권장

**프론트엔드 클라이언트 ID 생성 (생성 규칙 미준수)**
  - `EditorMode.tsx:823`: `game_data_id: \`PIN_${Date.now()}\``
  - `PinEditorNew.tsx:986`: `entityId = \`NPC_${npcName.toUpperCase().replace(/\s+/g, '_')}_${Date.now()}\``
- 스키마에 정의된 ID 명명 규칙을 따르지 않음 (예: `REG_[대륙]_[지역]_[일련번호]`)
- 타임스탬프 기반 ID로 일관성 부족
- 규칙 검증 없이 생성하여 데이터 무결성 위험

**해결 방안**: 생성 규칙을 명확히 정의하고 백엔드에서 강제
- 이미 `app/services/world_editor/id_generator.py`에 규칙 기반 생성 로직 존재
- 백엔드 API에서 규칙 검증 및 자동 생성 제공 필요
- 프론트엔드에서 백엔드 ID 생성 API 사용하도록 변경

**game_data 레이어의 VARCHAR(50) 사용**
  - `game_data.entities.entity_id`: VARCHAR(50) (예: `NPC_VILLAGER_001`, `CELL_INN_ROOM_001`)
  - `game_data.world_cells.cell_id`: VARCHAR(50)
  - `game_data.world_objects.object_id`: VARCHAR(50)
- 불변 데이터: game_data는 게임 정의 템플릿으로 변경되지 않음
- 식별성: 의미 있는 ID로 가독성과 디버깅 용이성 확보
- 게임 디자이너 친화적: `CELL_INN_ROOM_001` 같은 ID가 UUID보다 직관적
- 충돌 걱정 없음: 불변 데이터이므로 생성 시점에만 고유성 보장하면 됨

**DB Schema Review 권장과의 차이**
- Schema Review는 성능 관점에서 UUID 권장했으나, game_data 레이어는 식별성과 가독성이 더 중요
- VARCHAR(50)은 인덱스 크기와 비교 연산에서 약간의 오버헤드가 있으나, 불변 데이터의 특성상 조회 빈도가 높지 않아 허용 가능한 트레이드오프

#### 권장 조치:

1. **즉시 조치: ID 생성 규칙 명확히 정의 및 강제**

   **1-1. ID 생성 규칙 문서화 및 검증 로직 구현**
   ```python
   # app/services/world_editor/id_generator.py
   class IDGenerator:
       """game_data ID 생성 규칙 강제"""
       
       # 명명 규칙 정의
       RULES = {
           'region': r'^REG_[A-Z0-9_]+_\d{3}$',  # REG_[대륙]_[지역]_[일련번호]
           'location': r'^LOC_[A-Z0-9_]+_\d{3}$',  # LOC_[지역]_[장소]_[일련번호]
           'cell': r'^CELL_[A-Z0-9_]+_\d{3}$',  # CELL_[위치타입]_[세부위치]_[일련번호]
           'entity': r'^[A-Z]+_[A-Z0-9_]+_\d{3}$',  # [종족]_[직업/역할]_[일련번호]
           'object': r'^OBJ_[A-Z0-9_]+_\d{3}$',
           'item': r'^ITEM_[A-Z0-9_]+_\d{3}$',
           'pin': r'^PIN_[A-Z0-9_]+_\d{3}$',
       }
       
       @classmethod
       def validate_id(cls, entity_type: str, entity_id: str) -> bool:
           """ID가 명명 규칙을 따르는지 검증"""
           pattern = cls.RULES.get(entity_type)
           if not pattern:
               return False
           return bool(re.match(pattern, entity_id))
       
       @classmethod
       def generate_id(cls, entity_type: str, prefix: str, name: str, sequence: int) -> str:
           """명명 규칙에 맞는 ID 생성"""
           # prefix와 name을 대문자로 변환하고 공백/특수문자 제거
           clean_prefix = prefix.upper().replace(' ', '_').replace('-', '_')
           clean_name = name.upper().replace(' ', '_').replace('-', '_')
           sequence_str = f"{sequence:03d}"
           
           if entity_type == 'region':
               return f"REG_{clean_prefix}_{clean_name}_{sequence_str}"
           elif entity_type == 'location':
               return f"LOC_{clean_prefix}_{clean_name}_{sequence_str}"
           elif entity_type == 'cell':
               return f"CELL_{clean_prefix}_{clean_name}_{sequence_str}"
           elif entity_type == 'entity':
               return f"{clean_prefix}_{clean_name}_{sequence_str}"
           # ... 기타 타입
   ```

   **1-2. 백엔드 API에서 ID 생성 규칙 강제**
   ```python
   # app/api/routes/entities.py
   @router.post("/", response_model=EntityResponse)
   async def create_entity(entity_data: EntityCreate):
       # ID가 제공된 경우 규칙 검증
       if entity_data.entity_id:
           if not IDGenerator.validate_id('entity', entity_data.entity_id):
               raise HTTPException(
                   status_code=400,
                   detail=f"Invalid entity_id format. Expected: [종족]_[직업/역할]_[일련번호]"
               )
       
       # ID가 없으면 자동 생성 (규칙에 맞게)
       if not entity_data.entity_id:
           entity_data.entity_id = IDGenerator.generate_id(
               'entity',
               entity_data.entity_type,  # 예: 'NPC'
               entity_data.entity_name,   # 예: 'Villager'
               await get_next_sequence('entity', entity_data.entity_type)
           )
       
       return await entity_service.create_entity(entity_data)
   ```

   **1-3. 프론트엔드에서 백엔드 ID 생성 API 사용**
   ```typescript
   // 프론트엔드에서 ID 생성 요청
   const createEntity = async (entityData: EntityCreate) => {
     // ID를 프론트엔드에서 생성하지 않고 백엔드에 위임
     const response = await entitiesApi.create({
       ...entityData,
       entity_id: undefined,  // 백엔드에서 규칙에 맞게 생성
     });
     return response;
   };
   ```

2. **즉시 조치 (코드 레벨)**
   ```python
   # Pydantic 모델에서 UUID 타입 강제 (runtime_data용)
   from pydantic import BaseModel, UUID4
   
   class MovePlayerRequest(BaseModel):
       target_cell_id: UUID4  # str 대신 UUID4 사용
       position: Dict[str, float]
   ```

3. **단기 조치 (스키마 레벨) - game_data는 제외**
   ```sql
   -- game_data 레이어는 VARCHAR(50) 유지
   -- runtime_data 레이어만 UUID로 통일 (이미 완료)
   -- reference_layer 레이어만 UUID로 통일 (이미 완료)
   ```
   
   **game_data VARCHAR(50) 유지 근거**
   - 불변 데이터: 변경되지 않으므로 충돌 걱정 없음
   - 식별성: `CELL_INN_ROOM_001` 같은 의미 있는 ID가 디버깅과 개발에 유리
   - 게임 디자이너 친화적: UUID는 사람이 읽기 어려움
   - 성능 영향 미미: 불변 데이터는 조회 빈도가 낮고, VARCHAR(50) 인덱스도 충분히 효율적
   - 생성 규칙 강제로 일관성 보장: 명명 규칙을 명확히 정의하고 검증하면 VARCHAR(50)의 장점을 유지하면서 일관성 확보 가능

4. **API 입력 검증 강화**
   - FastAPI에서 UUID 타입 자동 검증 활용 (runtime_data용)
   - game_data ID는 정규식 패턴으로 검증
   - 잘못된 형식의 ID는 422 Unprocessable Entity 반환

---

## 1순위 — reference_layer 매핑의 고아 레코드(Orphan) 방지

### 해결 상태: 완전 해결

#### 완료된 작업:
1. **FK CASCADE 정책 적용**
   ```sql
   -- active_sessions 삭제 시 자동 정리
   FOREIGN KEY (session_id) REFERENCES runtime_data.active_sessions(session_id) ON DELETE CASCADE
   FOREIGN KEY (runtime_entity_id) REFERENCES runtime_data.runtime_entities(runtime_entity_id) ON DELETE CASCADE
   FOREIGN KEY (runtime_cell_id) REFERENCES runtime_data.runtime_cells(runtime_cell_id) ON DELETE CASCADE
   ```

2. **고아 레코드 정리 완료**
   - entity_references: 250개 삭제
   - cell_references: 504개 삭제
   - object_references: 39개 삭제
   - 중복 레코드: entity 578개, cell 2개 삭제

3. **세션 삭제 로직 단순화**
   - `game_manager.py`: 60줄 → 5줄 (FK CASCADE로 자동 처리)

#### 검증:
- `db_preflight.sql`로 고아 레코드 검사 가능
- 마이그레이션 후 고아 레코드 0개 확인

---

## 2순위 — "SSOT 위반 위험" 컬럼을 실제로 막기

### 해결 상태: 부분 해결

#### 완료된 작업:
1. **SSOT 명시**
   - `entity_states.current_position`이 단일 진실원으로 명시됨
   - 스키마 주석: "SSOT: 위치의 기록/갱신은 runtime_data.entity_states.current_position이 단일 진실원"

2. **파생 테이블 제한**
   - `cell_occupants`는 "조회 편의를 위한 파생 테이블"로 명시
   - 서비스 로직만이 갱신하도록 제한

3. **GENERATED 컬럼 추가**
   - `current_cell_id` GENERATED 컬럼으로 조회 성능 향상
   - 하지만 FK 제약조건은 PostgreSQL 제한으로 추가 불가

#### 남은 문제:
**쓰기 경로 봉쇄 미완성**
  - `cell_occupants`에 직접 INSERT/UPDATE 가능 (제약조건 없음)
  - 코드 레벨에서만 제한 (강제되지 않음)

#### 현재 스키마 상태:
```sql
-- SSOT 명시 (mvp_schema.sql:682-683)
-- SSOT: 위치의 기록/갱신은 runtime_data.entity_states.current_position이 단일 진실원;
-- cell_occupants는 조회 편의를 위한 파생 테이블로 서비스 로직만이 갱신하도록 제한한다.

-- GENERATED 컬럼 (mvp_schema.sql:1028-1035)
current_cell_id UUID GENERATED ALWAYS AS (
    CASE 
        WHEN jsonb_typeof(current_position -> 'runtime_cell_id') = 'string'
             AND (current_position->>'runtime_cell_id') ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        THEN (current_position->>'runtime_cell_id')::uuid
        ELSE NULL
    END
) STORED
```

#### 권장 조치:

1. **옵션 A: VIEW로 변경 (권장)**
   ```sql
   -- cell_occupants를 VIEW로 변경하여 쓰기 봉쇄
   DROP TABLE runtime_data.cell_occupants;
   
   CREATE VIEW runtime_data.cell_occupants AS
   SELECT 
       es.current_cell_id AS runtime_cell_id,
       es.runtime_entity_id,
       er.entity_type,
       es.current_position->'x' AS x,
       es.current_position->'y' AS y,
       es.current_position->'z' AS z,
       es.updated_at AS entered_at
   FROM runtime_data.entity_states es
   JOIN reference_layer.entity_references er 
       ON es.runtime_entity_id = er.runtime_entity_id
   WHERE es.current_cell_id IS NOT NULL;
   ```

2. **옵션 B: 트리거로 쓰기 경로 제한**
   ```sql
   -- cell_occupants에 직접 INSERT/UPDATE 방지
   CREATE OR REPLACE FUNCTION prevent_direct_cell_occupants_modification()
   RETURNS TRIGGER AS $$
   BEGIN
       RAISE EXCEPTION 'cell_occupants는 entity_states.current_position에서만 업데이트 가능합니다.';
   END;
   $$ LANGUAGE plpgsql;
   
   CREATE TRIGGER trg_prevent_cell_occupants_direct_modification
   BEFORE INSERT OR UPDATE ON runtime_data.cell_occupants
   FOR EACH ROW EXECUTE FUNCTION prevent_direct_cell_occupants_modification();
   ```

3. **옵션 C: RLS(Row Level Security) 적용**
   ```sql
   -- 특정 역할만 쓰기 허용
   ALTER TABLE runtime_data.cell_occupants ENABLE ROW LEVEL SECURITY;
   
   CREATE POLICY cell_occupants_service_only
   ON runtime_data.cell_occupants
   FOR ALL
   USING (current_user = 'service_role');
   ```

---

## 3순위 — JSONB 구조 데이터의 최소 스키마 검증

### 해결 상태: 미해결

#### 현재 상태:

**통일된 JSONB 처리 유틸리티**
  - `common.utils.jsonb_handler`: `parse_jsonb_data()`, `serialize_jsonb_data()` 함수 제공
  - 모든 매니저에서 일관된 방식으로 JSONB 파싱/직렬화 수행

**구현 예시:**
```python
# app/managers/cell_manager.py:824
cell_properties = parse_jsonb_data(row['cell_properties'])

# app/managers/entity_manager.py:227-228
base_stats = parse_jsonb_data(template["base_stats"])
entity_properties = parse_jsonb_data(template["entity_properties"])

# app/managers/object_state_manager.py:341
serialize_jsonb_data(current_state_dict)
```

**JSONB 스키마 검증 도구 존재**
- `database/utils/scripts/jsonb_schema_validator.py`: JSONB 스키마 검증 클래스
- 하지만 DB 레벨 CHECK 제약조건은 없음

**문제점:**

**CHECK 제약조건 없음**
- `position`, `inventory`, `object_state` JSONB 필드에 스키마 검증 없음
- 코드 레벨에서만 검증 (`database/utils/scripts/jsonb_schema_validator.py` 존재하나 DB 레벨 검증 없음)

**JSONB 사용의 장단점**
  - **장점**: 유연한 구조, 빠른 개발
  - **단점**: 정규화 약화, 복잡한 쿼리 성능 저하, 구조 검증 어려움

#### 문제점:
- 잘못된 JSON 구조가 저장되면 런타임 예외 발생
- 데이터 복구 어려움
- **DB Schema Review 지적**: "자주 조회하는 필드(예: 엔티티의 위치)나 범주형 속성은 별도 컬럼으로 분리하고 부분 인덱스나 생성형 컬럼을 통해 더 빠른 검색을 고려할 수 있습니다."

#### 현재 JSONB 필드 목록:
```sql
-- game_data 레이어
entities.default_position_3d        -- {"x": 5.0, "y": 4.0, "z": 0.0, "cell_id": "CELL_XXX"}
entities.base_stats                 -- {"hp": 100, "mp": 50, ...}
entities.default_inventory          -- {"items": [...], "quantities": {...}}
entities.entity_properties          -- {"is_hostile": false, ...}

-- runtime_data 레이어
entity_states.current_position      -- {"runtime_cell_id": "uuid", "x": 5.0, "y": 4.0, "z": 0.0}
entity_states.inventory             -- {"items": [...], "quantities": {...}}
entity_states.current_stats          -- {"hp": 100, "mp": 50, ...}
object_states.current_state         -- {"state": "open", "durability": 100, ...}
```

#### 권장 조치:

1. **즉시 조치: CHECK 제약조건 추가**
   ```sql
   -- position 필수 키 검증
   ALTER TABLE runtime_data.entity_states
   ADD CONSTRAINT chk_position_structure
   CHECK (
       current_position IS NULL OR
       (
           jsonb_typeof(current_position -> 'runtime_cell_id') = 'string' AND
           (current_position->>'runtime_cell_id') ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$' AND
           jsonb_typeof(current_position -> 'x') IN ('number', 'null') AND
           jsonb_typeof(current_position -> 'y') IN ('number', 'null')
       )
   );
   
   -- inventory 기본 구조 검증
   ALTER TABLE runtime_data.entity_states
   ADD CONSTRAINT chk_inventory_structure
   CHECK (
       inventory IS NULL OR
       (
           jsonb_typeof(inventory) = 'object' AND
           (inventory ? 'items' OR jsonb_typeof(inventory -> 'items') = 'array')
       )
   );
   
   -- current_stats 기본 구조 검증
   ALTER TABLE runtime_data.entity_states
   ADD CONSTRAINT chk_stats_structure
   CHECK (
       current_stats IS NULL OR
       (
           jsonb_typeof(current_stats) = 'object' AND
           jsonb_typeof(current_stats -> 'hp') IN ('number', 'null') AND
           jsonb_typeof(current_stats -> 'mp') IN ('number', 'null')
       )
   );
   ```

2. **단기 조치: 핵심 필드 컬럼 승격 (DB Schema Review 권장)**
   ```sql
   -- 자주 조회하는 필드를 별도 컬럼으로 분리
   ALTER TABLE runtime_data.entity_states
   ADD COLUMN position_x FLOAT GENERATED ALWAYS AS (
       (current_position->>'x')::float
   ) STORED,
   ADD COLUMN position_y FLOAT GENERATED ALWAYS AS (
       (current_position->>'y')::float
   ) STORED,
   ADD COLUMN position_z FLOAT GENERATED ALWAYS AS (
       (current_position->>'z')::float
   ) STORED;
   
   -- 공간 인덱스 추가 (PostGIS 사용 시)
   CREATE INDEX idx_entity_states_position_3d 
   ON runtime_data.entity_states USING GIST (
       point(position_x, position_y, position_z)
   );
   ```

3. **장기 조치: 정규화 수준 재검토**
   - `default_inventory`, `default_abilities` 등을 관계형 테이블로 분리 검토
   - **DB Schema Review 지적**: "중복 가능성을 줄이고 쿼리 효율을 높이려면 관계형 테이블(예: 엔티티-아이템 관계)로 분리하는 것을 고려할 수 있습니다."

---

## 4순위 — 서비스마다 흩어진 "삭제/업데이트 무결성 검사" 통합

### 해결 상태: 부분 구현 (재사용성 부족)

#### 현재 구현 상태:

**실제 동작하는 검증 로직 존재**
  - `EntityService.validate_entity_references()`: Location/Cell owner, Quest giver 참조 검사
  - `CellService.validate_cell_references()`: Location entry_points, Cell exits/entrances 참조 검사
  - 삭제 전 참조 무결성 검증 후 명확한 에러 메시지 제공

**구현 예시:**
```python
# app/services/world_editor/entity_service.py:332-370
async def validate_entity_references(self, entity_id: str) -> Dict[str, List[str]]:
    """엔티티가 참조되는 Location/Cell 목록 반환 (SSOT 참조 무결성 검증)"""
    # 1. Location의 owner로 참조되는 경우
    locations_as_owner = await conn.fetch("""
        SELECT location_id, location_name
        FROM game_data.world_locations
        WHERE location_properties->'ownership'->>'owner_entity_id' = $1
    """, entity_id)
    
    # 2. Cell의 owner로 참조되는 경우
    cells_as_owner = await conn.fetch("""
        SELECT cell_id, cell_name
        FROM game_data.world_cells
        WHERE cell_properties->'ownership'->>'owner_entity_id' = $1
    """, entity_id)
    
    # 3. Location의 quest_givers에 포함된 경우
    locations_in_quest_givers = await conn.fetch("""
        SELECT location_id, location_name
        FROM game_data.world_locations
        WHERE location_properties->'quests'->'quest_givers' @> $1::jsonb
    """, serialize_jsonb_data([entity_id]))
    
    return {
        "locations_as_owner": [row['location_id'] for row in locations_as_owner],
        "cells_as_owner": [row['cell_id'] for row in cells_as_owner],
        "locations_in_quest_givers": [row['location_id'] for row in locations_in_quest_givers]
    }
```

**문제점:**

**검증 로직 분산**
- 각 서비스마다 유사한 패턴이지만 코드 중복

**일관성 부족**
- 서비스마다 다른 에러 메시지 형식

**재사용성 낮음**
- 새로운 서비스 추가 시 검증 로직을 다시 작성해야 함

#### 문제점:
- 검증 로직이 서비스마다 다름
- 일관성 없는 에러 메시지
- 중복 코드

#### 현재 구현 상태:
```python
# app/services/world_editor/entity_service.py:372-406
async def delete_entity(self, entity_id: str) -> bool:
    """엔티티 삭제 (SSOT 참조 무결성 검증 포함)"""
    # 참조 검증
    references = await self.validate_entity_references(entity_id)
    # ... 개별 서비스마다 다른 검증 로직
```

#### 문제점 상세:
- **검증 로직 분산**: 각 서비스(`EntityService`, `CellService`, `LocationService`)마다 다른 검증 방식
- **에러 메시지 불일치**: 서비스마다 다른 형식의 에러 메시지
- **중복 코드**: 유사한 참조 검증 로직이 여러 곳에 반복
- **테스트 어려움**: 검증 로직이 분산되어 통합 테스트 복잡

#### 권장 조치:

1. **IntegrityService 생성**
   ```python
   # app/services/integrity/integrity_service.py
   from typing import Dict, List, Any
   from dataclasses import dataclass
   
   @dataclass
   class IntegrityCheckResult:
       can_delete: bool
       blocking_references: List[Dict[str, Any]]
       error_message: str = ""
   
   class IntegrityService:
       def __init__(self, db_connection):
           self.db = db_connection
       
       async def can_delete_entity(self, entity_id: str) -> IntegrityCheckResult:
           """엔티티 삭제 가능 여부 검사"""
           blocking = []
           
           # 1. Location owner 참조 확인
           locations = await self._check_location_owner(entity_id)
           if locations:
               blocking.append({
                   "type": "location_owner",
                   "items": locations,
                   "message": f"다음 Location의 소유자로 참조됨: {', '.join(locations)}"
               })
           
           # 2. Cell owner 참조 확인
           cells = await self._check_cell_owner(entity_id)
           if cells:
               blocking.append({
                   "type": "cell_owner",
                   "items": cells,
                   "message": f"다음 Cell의 소유자로 참조됨: {', '.join(cells)}"
               })
           
           # 3. Quest giver 참조 확인
           quest_locations = await self._check_quest_giver(entity_id)
           if quest_locations:
               blocking.append({
                   "type": "quest_giver",
                   "items": quest_locations,
                   "message": f"다음 Location의 퀘스트 제공자로 참조됨: {', '.join(quest_locations)}"
               })
           
           # 4. Runtime 세션 참조 확인
           active_sessions = await self._check_runtime_references(entity_id)
           if active_sessions:
               blocking.append({
                   "type": "runtime_reference",
                   "items": active_sessions,
                   "message": f"다음 세션에서 활성 참조됨: {', '.join(active_sessions)}"
               })
           
           return IntegrityCheckResult(
               can_delete=len(blocking) == 0,
               blocking_references=blocking,
               error_message="\n".join([b["message"] for b in blocking]) if blocking else ""
           )
       
       async def can_delete_cell(self, cell_id: str) -> IntegrityCheckResult:
           """Cell 삭제 가능 여부 검사"""
           # 유사한 패턴으로 구현
           ...
       
       async def can_delete_location(self, location_id: str) -> IntegrityCheckResult:
           """Location 삭제 가능 여부 검사"""
           # 유사한 패턴으로 구현
           ...
   ```

2. **서비스 레이어 통합**
   ```python
   # app/services/world_editor/entity_service.py 수정
   class EntityService:
       def __init__(self, db_connection, integrity_service: IntegrityService):
           self.db = db_connection
           self.integrity = integrity_service
       
       async def delete_entity(self, entity_id: str) -> bool:
           # 통합된 검증 서비스 사용
           check_result = await self.integrity.can_delete_entity(entity_id)
           
           if not check_result.can_delete:
               raise ValueError(
                   f"엔티티 '{entity_id}' 삭제 불가:\n{check_result.error_message}"
               )
           
           # 삭제 수행
           ...
   ```

3. **UX 친화적 에러 메시지**
   - 사용자에게 어떤 참조가 문제인지 명확히 표시
   - 해결 방법 제시 (예: "먼저 Location의 소유자를 변경하세요")

---

## 5순위 — 트랜잭션 경계 불일치

### 해결 상태: 부분 해결

#### 완료된 작업:
1. **이동 작업 트랜잭션 사용**
   - `CellManager.move_entity_between_cells()`: `async with conn.transaction()`
   - `GameSession.enter_cell()`: `async with conn.transaction()`

2. **세션 정리 트랜잭션 사용**
   - `InstanceManager.cleanup_session_instances()`: `async with conn.transaction()`

#### 현재 구현 상태:

**핵심 작업에서 트랜잭션 사용**
  - `CellManager.move_entity_between_cells()`: 엔티티 이동 시 트랜잭션으로 원자성 보장
  - `GameSession.enter_cell()`: 셀 진입 및 이벤트 기록을 트랜잭션으로 처리
  - `InstanceManager.cleanup_session_instances()`: 세션 정리 시 여러 테이블 삭제를 트랜잭션으로 안전하게 수행

**구현 예시:**
```python
# app/managers/cell_manager.py:1041
async def move_entity_between_cells(...):
    async with pool.acquire() as conn:
        async with conn.transaction():
            # 1. 출발 셀에서 제거
            remove_result = await self.remove_entity_from_cell(...)
            # 2. 도착 셀에 추가
            add_result = await self.add_entity_to_cell(...)
            # 3. 위치 업데이트
            if new_position:
                await conn.execute(...)
```

**남은 문제:**

**일관성 부족**
- 일부 작업은 트랜잭션 사용, 일부는 미사용
- 명시적인 트랜잭션 정책 없음

#### 현재 트랜잭션 사용 현황:
```python
# 트랜잭션 사용 중
# app/managers/cell_manager.py:1041
async def move_entity_between_cells(...):
    async with conn.transaction():
        remove_result = await self.remove_entity_from_cell(...)
        add_result = await self.add_entity_to_cell(...)

# app/core/game_session.py:70
async def enter_cell(self, runtime_cell_id: str):
    async with conn.transaction():
        # 셀 컨텐츠 로드 및 이벤트 기록

# app/managers/instance_manager.py:304
async def cleanup_session_instances(self, session_id: str):
    async with conn.transaction():
        # 여러 테이블 삭제 작업
```

#### 문제점:
- **일관성 부족**: 일부 작업은 트랜잭션 사용, 일부는 미사용
- **명시적 정책 없음**: 어떤 작업에 트랜잭션이 필요한지 문서화되지 않음
- **중간 실패 시나리오**: 트랜잭션 없이 여러 테이블 업데이트 시 "반쯤 이동한 엔티티" 상태 발생 가능

#### 권장 조치:

1. **트랜잭션 정책 문서화**
   ```markdown
   # 트랜잭션 사용 가이드라인
   
   ## 반드시 트랜잭션 사용해야 하는 작업:
   
   1. **상태 전이 작업**
      - 엔티티 이동 (셀 간 이동)
      - 셀 진입/퇴장
      - 세션 생성/종료
      - 인벤토리 아이템 추가/제거
   
   2. **다중 테이블 업데이트**
      - 엔티티 생성 (entity_references + entity_states)
      - 셀 생성 (cell_references + runtime_cells)
      - 오브젝트 상태 변경 (object_states + cell_occupants)
   
   3. **원자성이 중요한 작업**
      - 게임 시간 틱 처리
      - 이벤트 트리거 및 결과 적용
   ```

2. **트랜잭션 데코레이터 패턴 도입**
   ```python
   # app/common/decorators/transaction.py
   from functools import wraps
   
   def with_transaction(func):
       @wraps(func)
       async def wrapper(self, *args, **kwargs):
           pool = await self.db.pool
           async with pool.acquire() as conn:
               async with conn.transaction():
                   return await func(self, *args, **kwargs, conn=conn)
       return wrapper
   
   # 사용 예시
   class CellManager:
       @with_transaction
       async def move_entity(self, entity_id, from_cell, to_cell, conn=None):
           # conn은 자동으로 트랜잭션 내부
           ...
   ```

3. **트랜잭션 검증 도구**
   ```python
   # 개발 환경에서 트랜잭션 사용 여부 검증
   class TransactionValidator:
       def validate_transaction_usage(self, method_name, has_transaction):
           if not has_transaction and method_name in CRITICAL_OPERATIONS:
               logger.warning(f"{method_name}은 트랜잭션이 필요하지만 사용되지 않았습니다.")
   ```

---

## 6순위 — 뷰/지표 집계가 깨지는 정합성

### 해결 상태: 자동 해결 예상

#### 완료된 작업:
- 1~3순위 해결로 대부분 자동 안정화
- FK CASCADE로 고아 데이터 자동 정리
- SSOT 준수로 중복 데이터 방지

#### 추가 권장:
- 성능 모니터링 뷰 생성
- 정기적인 데이터 무결성 검사 스크립트 실행

---

## 프론트엔드 구현 현황

### EditorMode (월드 제작 통합 편집기)

**주요 기능:**
- **세계 데이터 편집**: `useWorldEditor()` 훅으로 지역·장소·셀 데이터 관리
- **지도 뷰**: world, hierarchical, cell 세 가지 모드 지원
- **지도 및 도로 편집**: MapCanvas와 HierarchicalMapView로 핀 추가·이동·삭제, 도로 그리기
- **엔티티 탐색기**: EntityExplorer와 EntityEditor로 트리 형태 탐색 및 속성 수정
- **Undo/Redo**: `useUndoRedo()` 훅으로 편집 기록 저장
- **백업/복원**: `saveBackup()`, `restoreBackup()` 함수로 전체 프로젝트 JSON 내보내기/불러오기
- **단축키**: `useKeyboardShortcuts()`로 단축키 제공
- **검색과 바꾸기**: 월드 데이터 전반에서 검색 및 일괄 바꾸기
- **WebSocket 동기화**: 실시간 동기화 지원

**구현 예시:**
```typescript
// app/ui/frontend/src/modes/EditorMode.tsx:32-85
export const EditorMode: React.FC = () => {
  const { addAction, undo, redo } = useUndoRedo({ maxHistorySize: 50 });
  const { settings } = useSettings();
  const {
    mapState, pins, roads, regions, locations, cells,
    addPin, updatePin, deletePin,
    addRoad, updateRoad, deleteRoad,
  } = useWorldEditor();
  const { sendMessage, connected } = useWebSocket(handleWebSocketMessage);
  // ... 2천여 줄의 로직
};
```

**문제점:**
- **거대한 컴포넌트**: 한 파일에 2천여 줄의 로직
- **클라이언트 ID 생성**: `PIN_${Date.now()}`, `NPC_${...}_${Date.now()}` 형식

### GameMode (텍스트 어드벤처 + 비주얼 노벨)

**주요 기능:**
- **게임 초기화**: `gameApi.startNewGame()`로 세션 생성 및 초기 셀 로드
- **레이어 기반 UI**: framer-motion으로 BackgroundLayer, CharacterLayer, LocationLayer, MessageLayer, ChoiceLayer 등 구성
- **행동 처리**: 이동·조사·상호작용·아이템 획득 등 다양한 동작 처리
- **오브젝트·엔티티 상호작용**: `useObjectInteraction`, `useEntityInteraction` 훅으로 컨텍스트 메뉴 및 상호작용 처리
- **메시지 및 선택지 시스템**: 한 줄씩 출력, 히스토리 추가
- **키보드 모드**: ESC/I로 정보 패널, Ctrl+S/L로 저장/불러오기, A키로 자동 모드

**구현 예시:**
```typescript
// app/ui/frontend/src/components/game/GameView.tsx:30-130
export const GameView: React.FC<GameViewProps> = ({ onNavigate }) => {
  const { handleObjectAction } = useObjectInteraction({...});
  const { handleEntityAction } = useEntityInteraction();
  const contextMenuActions = useContextMenuActions(...);
  
  const initializeGame = async () => {
    const response = await gameApi.startNewGame(playerTemplateId, startCellId);
    setGameState(response.game_state);
    const cell = await gameApi.getCurrentCell(response.game_state.session_id);
    setCurrentCell(cell);
    const actions = await gameApi.getAvailableActions(response.game_state.session_id);
    setAvailableActions(actions);
  };
};
```

**문제점:**
- **서버 API 호출 분산**: 프론트에 분산되어 에러 관리와 테스트 어려움

### 공통 개선 필요 사항

#### 1. 클라이언트 ID 생성 통합
**현재 상태**: 프론트엔드에서 문자열 ID 생성

**문제점:**
- 타임스탬프 기반 ID로 중복 가능성
- UUID 형식 불일치
- 백엔드와 클라이언트 간 ID 형식 불일치

**권장 조치:**
```typescript
// 백엔드에서 UUID 발급 API 추가
// app/ui/backend/routes/world_editor.py
@router.post("/generate-id")
async def generate_id(entity_type: str):
    """엔티티 타입별 UUID 생성"""
    return {"id": str(uuid.uuid4()), "type": entity_type}

// 프론트엔드에서 사용
const { data } = await api.post('/api/world-editor/generate-id', { entity_type: 'pin' });
const pinData = {
  ...pinData,
  game_data_id: data.id  // 백엔드에서 발급받은 UUID 사용
};
```

#### 2. 컴포넌트 분리

**권장 조치:**
- EditorMode를 기능별 컴포넌트로 분리
- 커스텀 훅으로 상태 관리 로직 추출
- 컨텍스트로 전역 상태 관리

---

## 매니저 및 서비스 구현 현황

### 매니저 구현

#### 1. CellManager

**주요 기능:**
- **캐시 관리**: `_cell_cache`, `_content_cache`로 조회 성능 최적화
- **CRUD 구현**: 생성, 조회, 업데이트, 삭제 모두 구현
- **컨텐츠 로딩**: 엔티티·오브젝트·이벤트를 별도 로딩하여 API 친화적 필드명 변환
- **JSONB 처리**: `parse_jsonb_data()`, `serialize_jsonb_data()`로 통일된 처리
- **트랜잭션 사용**: 엔티티 이동 시 원자성 보장

**구현 예시:**
```python
# app/managers/cell_manager.py:119-121
self._cell_cache: Dict[str, CellData] = {}
self._content_cache: Dict[str, CellContent] = {}
self._cache_lock = asyncio.Lock()

# 캐시 우선 검사 후 DB 로드
async with self._cache_lock:
    if cell_id in self._cell_cache:
        return self._cell_cache[cell_id]
```

#### 2. DialogueManager

**주요 기능:**
- **대화 시작**: NPC·플레이어 엔티티 로드, 대화 템플릿 동적 불러오기
- **대화 진행**: 주제별 조건 확인, 응답 생성
- **대화 기록**: `runtime_data.dialogue_history`에 저장
- **컨텍스트 관리**: 컨텍스트와 주제, 지식정보 로드·생성

#### 3. EffectCarrierManager

**주요 기능:**
- **CRUD 제공**: 생성·조회·수정·삭제
- **캐시와 DB 동시 갱신**: 성능과 일관성 확보
- **엔티티 효과 관리**: 효과 부여/제거 메서드 제공

#### 4. InstanceManager

**주요 기능:**
- **참조 레이어 위임**: 런타임 셀/엔티티 생성
- **트랜잭션 사용**: 세션 정리 시 일괄 삭제 안전하게 수행
- **캐시 병행**: DB와 캐시를 함께 사용하여 조회 성능 향상

#### 5. InventoryManager & ObjectStateManager

**주요 기능:**
- **인벤토리 관리**: 아이템 추가/제거/조회
- **오브젝트 상태**: 상태 조회·업데이트
- **자동 생성**: 런타임 오브젝트가 없을 경우 자동 생성 후 기본/런타임 상태 병합

### API 서비스 구현

#### 1. Cells API

**주요 기능:**
- **CRUD 구현**: 모든 셀 조회, 특정 셀 조회, 생성, 수정, 삭제
- **소유자 JOIN**: DB에서 셀 조회 시 소유자 엔티티를 JOIN으로 가져옴
- **JSONB 파싱·정규화**: JSONB 속성을 파싱하여 API 응답 형식으로 변환
- **동적 SQL 생성**: 업데이트 시 필드별 변경을 동적으로 조합
- **참조 무결성 검증**: `validate_cell_references()`로 삭제 전 검사

#### 2. Entities API

**주요 기능:**
- **JSONB 파싱**: 능력치·장비·스킬·인벤토리 파싱
- **직렬화**: 생성/업데이트 시 입력값을 직렬화하여 저장
- **부분 업데이트**: 수정된 부분만 업데이트
- **참조 무결성 검증**: `validate_entity_references()`로 삭제 전 검사

#### 3. Dialogue API

**주요 기능:**
- **컨텍스트/주제 CRUD**: 컨텍스트와 주제 관리
- **엔티티별 컨텍스트 조회**: NPC별 대화 컨텍스트 조회
- **대화 엔진 연동**: DialogueManager를 호출하여 대화 진행

### 공통 개선 필요 사항

#### 1. 예외 처리 모듈화
**현재 상태**: 각 서비스에서 `try/except` 반복

**권장 조치:**
```python
# app/common/decorators/error_handler.py
from functools import wraps
from fastapi import HTTPException

def handle_service_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except IntegrityError as e:
            raise HTTPException(status_code=409, detail="데이터 무결성 오류")
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise HTTPException(status_code=500, detail="내부 서버 오류")
    return wrapper

# 사용 예시
class EntityService:
    @handle_service_errors
    async def delete_entity(self, entity_id: str) -> bool:
        ...
```

#### 2. JSONB 스키마화
**권장**: 자주 조회되는 속성(예: 셀 구조의 exits/entrances, 엔티티 속성)만큼은 별도 컬럼으로 끌어내어 인덱싱과 검증을 쉽게 함

---

## 추가 개선 사항 (DB Schema Review 기반)

### 7. ENUM 타입 도입

**현재 상태**: 문자열 + CHECK 제약조건
```sql
-- mvp_schema.sql:1206
carrier_type VARCHAR(20) NOT NULL CHECK (carrier_type IN ('skill', 'buff', 'item', 'blessing', 'curse', 'ritual'))
```

**문제점**:
- 타입 안전성 부족
- 오타 가능성
- 쿼리 성능 저하 (문자열 비교)

**권장 조치**:
```sql
-- ENUM 타입 생성
CREATE TYPE carrier_type_enum AS ENUM ('skill', 'buff', 'item', 'blessing', 'curse', 'ritual');
CREATE TYPE entity_type_enum AS ENUM ('player', 'npc', 'monster', 'creature');
CREATE TYPE object_type_enum AS ENUM ('static', 'interactive', 'trigger');

-- 컬럼 타입 변경
ALTER TABLE reference_layer.effect_carriers
ALTER COLUMN carrier_type TYPE carrier_type_enum USING carrier_type::carrier_type_enum;
```

### 8. 마이그레이션 전략

**현재 상태**: 단일 스키마 파일 (`mvp_schema.sql`)

**권장 조치**:
- Alembic 또는 Migra 도입
- 버전별 마이그레이션 스크립트 관리
- 롤백 전략 수립

---

## 문제별 해결 상태

| 순위 | 문제 | 해결 상태 | 우선순위 | DB Schema Review 연관성 |
|------|------|-----------|----------|------------------------|
| 0순위 | ID/타입 혼용 | 대부분 해결 | 낮음 | game_data는 VARCHAR(50) 유지 (설계 의도) |
| 1순위 | 고아 레코드 방지 | 완전 해결 | 완료 | FK CASCADE 정책 적용 |
| 2순위 | SSOT 위반 위험 | 부분 해결 | 중간 | SSOT 원칙 명시됨 |
| 3순위 | JSONB 검증 | 미해결 | 높음 | JSONB 사용 신중 접근 권장 |
| 4순위 | 무결성 검사 통합 | 부분 구현 | 중간 | 서비스 레이어 개선 필요 |
| 5순위 | 트랜잭션 경계 | 부분 해결 | 중간 | 트리거/함수 분리 권장 |
| 6순위 | 뷰/지표 정합성 | 자동 해결 | 완료 | 성능 뷰 이미 존재 |

## 다음 단계 권장사항

### 즉시 조치 (높은 우선순위)
1. **JSONB 구조 검증 추가 (3순위)**
   - CHECK 제약조건으로 필수 키 검증
   - 핵심 필드 컬럼 승격 검토 (position_x, position_y, position_z)
   - **현재 상태**: 코드 레벨 검증만 존재, DB 레벨 검증 필요

2. **IntegrityService 생성 (4순위)**
   - 통합된 무결성 검사 서비스
   - 일관된 에러 메시지 제공
   - **현재 상태**: 각 서비스에 검증 로직 존재하나 재사용성 부족

3. **ID 생성 규칙 명확히 정의 및 강제**
   - **생성 규칙 문서화**: 스키마에 정의된 명명 규칙을 코드 레벨에서 명확히 정의
   - **백엔드 검증 강제**: API에서 ID 생성 규칙 검증 및 자동 생성
   - **프론트엔드 규칙 준수**: 클라이언트에서 임의 ID 생성 금지, 백엔드 API 사용
   - **현재 상태**: 
     - 스키마에 주석으로 규칙 정의됨 (REG_[대륙]_[지역]_[일련번호] 등)
     - `app/services/world_editor/id_generator.py`에 규칙 기반 생성 로직 존재
     - 프론트엔드에서 `PIN_${Date.now()}` 형식으로 규칙 미준수
     - 백엔드 API에서 규칙 검증 및 강제 미흡
   - **해결 방안**: 
     - ID 생성 규칙을 명확히 문서화하고 검증 로직 구현
     - 백엔드 API에서 규칙 검증 및 자동 생성 제공
     - 프론트엔드에서 백엔드 ID 생성 API 사용
   - **장점**: 
     - 일관된 ID 형식으로 데이터 관리 용이
     - 가독성과 디버깅 용이성 유지 (VARCHAR(50)의 장점 활용)
     - 데이터 무결성 보장
     - 게임 디자이너 친화적 ID 유지

4. **공통 예외 처리 모듈화**
   - 미들웨어/데코레이터로 예외 처리 공통화
   - **현재 상태**: 각 서비스에서 `try/except` 반복

### 단기 조치 (중간 우선순위)
1. **SSOT 쓰기 경로 봉쇄 (2순위)**
   - `cell_occupants`를 VIEW로 변경 또는 트리거 적용
   - **현재 상태**: SSOT 명시 완료, 쓰기 경로 봉쇄 미완성

2. **트랜잭션 정책 문서화 (5순위)**
   - 트랜잭션 사용 가이드라인 작성
   - 데코레이터 패턴 도입
   - **현재 상태**: 핵심 작업에 트랜잭션 사용 중, 일관성 부족

3. **ENUM 타입 도입 (7순위)**
   - 문자열 타입을 ENUM으로 변경
   - 타입 안전성 및 성능 향상
   - **현재 상태**: CHECK 제약조건으로 제한, ENUM 미사용

4. **JSONB 핵심 필드 컬럼 승격**
   - 자주 조회되는 속성을 별도 컬럼으로 분리
   - 인덱싱 및 검증 용이성 향상
   - 자주 조회되는 속성(예: 셀 구조의 exits/entrances, 엔티티 속성)만큼은 별도 컬럼으로 끌어내어 인덱싱과 검증을 쉽게 함

5. **프론트엔드 컴포넌트 분리**
   - EditorMode를 기능별 컴포넌트로 분리
   - 커스텀 훅으로 상태 관리 로직 추출
   - **현재 상태**: EditorMode 한 파일에 2천여 줄

### 장기 조치 (낮은 우선순위)
1. **코드 레벨 UUID 타입 통일 (0순위)**
   - Pydantic 모델에서 UUID 강제
   - `Union[str, UUID]` 제거

2. **game_data 레이어 VARCHAR(50) 유지 (설계 의도 반영)**
   - ✅ **현재 상태 유지 권장**: VARCHAR(50)이 적절함
   - **이유**: 
     - 불변 데이터이므로 충돌 걱정 없음
     - 식별성과 가독성이 UUID보다 우수
     - 게임 디자이너가 직접 사용하는 ID이므로 의미 있는 이름 필요
     - 성능 영향은 미미함 (불변 데이터, 조회 빈도 낮음)
   - **DB Schema Review와의 차이**: 
     - Schema Review는 성능 관점에서 UUID 권장했으나, game_data는 식별성과 가독성이 더 중요
     - 이는 설계 의도에 맞는 합리적인 트레이드오프

3. **정규화 수준 재검토 (3순위)**
   - JSONB 필드를 관계형 테이블로 분리 검토
   - `default_inventory`, `default_abilities` 등

4. **마이그레이션 전략 수립 (8순위)**
   - Alembic/Migra 도입
   - 버전 관리 체계 구축

---

## 구체적인 액션 플랜

### Phase 1: 즉시 조치

#### 1.1 ID 생성 규칙 강제 구현

**목표**: 프론트엔드에서 규칙을 따르지 않는 ID 생성 문제 해결

**작업 내용**:
1. **ID 검증 로직 강화** (`app/services/world_editor/id_generator.py`)
   ```python
   # 파일: app/services/world_editor/id_generator.py
   import re
   from typing import Dict, Optional
   
   class IDGenerator:
       # 기존 코드에 추가
       VALIDATION_PATTERNS = {
           'region': r'^REG_[A-Z0-9_]+_\d{3}$',
           'location': r'^LOC_[A-Z0-9_]+_\d{3}$',
           'cell': r'^CELL_[A-Z0-9_]+_\d{3}$',
           'entity': r'^[A-Z]+_[A-Z0-9_]+_\d{3}$',
           'object': r'^OBJ_[A-Z0-9_]+_\d{3}$',
           'item': r'^ITEM_[A-Z0-9_]+_\d{3}$',
           'pin': r'^PIN_[A-Z0-9_]+_\d{3}$',
       }
       
       @classmethod
       def validate_id(cls, entity_type: str, entity_id: str) -> tuple[bool, Optional[str]]:
           # Python 3.9+ 문법, 하위 호환성을 위해 Tuple 사용 고려
           """ID 검증 및 에러 메시지 반환"""
           pattern = cls.VALIDATION_PATTERNS.get(entity_type)
           if not pattern:
               return False, f"Unknown entity type: {entity_type}"
           
           if not re.match(pattern, entity_id):
               return False, f"Invalid {entity_type} ID format. Expected pattern: {pattern}"
           
           return True, None
   ```

2. **백엔드 API 엔드포인트에 검증 추가**
   - 파일: `app/api/routes/entities.py`, `app/api/routes/cells.py`, `app/api/routes/locations.py`
   - 각 POST/PUT 엔드포인트에서 ID 검증 수행
   - ID가 없으면 자동 생성, 있으면 검증 후 사용

3. **프론트엔드 수정**
   - 파일: `app/ui/frontend/src/modes/EditorMode.tsx:823`
   - 파일: `app/ui/frontend/src/components/editor/PinEditorNew.tsx:986`
   - 클라이언트 ID 생성 제거, 백엔드 API 호출로 변경

**⚠️ 주의**: 
- IDGenerator는 이미 존재하므로 검증 로직만 추가하면 됨
- 프론트엔드 수정 범위가 클 수 있음 (여러 파일에 걸쳐 ID 생성 로직이 분산되어 있을 수 있음)

#### 1.2 공통 예외 처리 모듈화

**목표**: 서비스 레이어의 반복적인 try/except 패턴 제거

**작업 내용**:
1. **에러 핸들러 데코레이터 생성**
   ```python
   # 파일: app/common/decorators/error_handler.py (신규 생성)
   from functools import wraps
   from fastapi import HTTPException
   from asyncpg.exceptions import ForeignKeyViolationError, UniqueViolationError
   from common.utils.logger import logger
   
   def handle_service_errors(func):
       @wraps(func)
       async def wrapper(*args, **kwargs):
           try:
               return await func(*args, **kwargs)
           except ValueError as e:
               raise HTTPException(status_code=400, detail=str(e))
           except ForeignKeyViolationError as e:
               raise HTTPException(status_code=409, detail=f"참조 무결성 오류: {str(e)}")
           except UniqueViolationError as e:
               raise HTTPException(status_code=409, detail=f"중복 데이터 오류: {str(e)}")
           except Exception as e:
               logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
               raise HTTPException(status_code=500, detail="내부 서버 오류")
       return wrapper
   ```

2. **서비스 클래스에 데코레이터 적용**
   - `app/services/world_editor/entity_service.py`
   - `app/services/world_editor/cell_service.py`
   - `app/services/world_editor/location_service.py`
   - 각 public 메서드에 `@handle_service_errors` 적용


#### 1.3 IntegrityService 생성

**목표**: 분산된 참조 무결성 검증 로직 통합

**작업 내용**:
1. **IntegrityService 클래스 생성**
   ```python
   # 파일: app/services/integrity_service.py (신규 생성)
   from typing import Dict, List
   from database.connection import DatabaseConnection
   
   class IntegrityService:
       """데이터 무결성 검증 통합 서비스"""
       
       def __init__(self, db_connection: DatabaseConnection):
           self.db = db_connection
       
       async def validate_entity_references(self, entity_id: str) -> Dict[str, List[str]]:
           """엔티티 참조 검증 (기존 EntityService 로직 이동)"""
           # 기존 validate_entity_references 로직
       
       async def validate_cell_references(self, cell_id: str) -> Dict[str, List[str]]:
           """셀 참조 검증 (기존 CellService 로직 이동)"""
           # 기존 validate_cell_references 로직
       
       async def validate_location_references(self, location_id: str) -> Dict[str, List[str]]:
           """위치 참조 검증"""
           # 유사한 패턴으로 구현
   ```

2. **기존 서비스에서 IntegrityService 사용**
   - `EntityService.validate_entity_references()` → `IntegrityService.validate_entity_references()`
   - `CellService.validate_cell_references()` → `IntegrityService.validate_cell_references()`


### Phase 2: 단기 조치

#### 2.1 JSONB 구조 검증 추가

**목표**: DB 레벨에서 JSONB 필드 구조 검증

**작업 내용**:
1. **CHECK 제약조건 추가**
   ```sql
   -- 파일: database/migrations/add_jsonb_validation.sql (신규 생성)
   -- entity_states.current_position 검증
   ALTER TABLE runtime_data.entity_states
   ADD CONSTRAINT chk_position_structure 
   CHECK (
       current_position IS NULL OR
       (
           current_position ? 'x' AND
           current_position ? 'y' AND
           (current_position ? 'runtime_cell_id' OR current_position->>'runtime_cell_id' ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
       )
   );
   
   -- object_states.current_state 검증
   ALTER TABLE runtime_data.object_states
   ADD CONSTRAINT chk_object_state_structure
   CHECK (
       current_state IS NULL OR
       (
           current_state ? 'state' AND
           jsonb_typeof(current_state->'state') = 'string'
       )
   );
   ```

2. **Pydantic 모델로 런타임 검증 강화**
   - `app/common/schemas/jsonb_schemas.py` 생성
   - Position, ObjectState, Inventory 등의 Pydantic 모델 정의


#### 2.2 트랜잭션 정책 문서화 및 데코레이터 도입

**목표**: 트랜잭션 사용 일관성 확보

**작업 내용**:
1. **트랜잭션 데코레이터 생성**
   ```python
   # 파일: app/common/decorators/transaction.py (신규 생성)
   from functools import wraps
   
   def with_transaction(func):
       @wraps(func)
       async def wrapper(self, *args, **kwargs):
           pool = await self.db.pool
           async with pool.acquire() as conn:
               async with conn.transaction():
                   return await func(self, *args, **kwargs, conn=conn)
       return wrapper
   ```

2. **트랜잭션 가이드라인 문서 작성**
   - 파일: `docs/development/TRANSACTION_GUIDELINES.md` (신규 생성)
   - 언제 트랜잭션을 사용해야 하는지 명시
   - 데코레이터 사용 예시

3. **기존 코드에 트랜잭션 적용**
   - `CellManager.move_entity_between_cells()` (이미 적용됨)
   - `InstanceManager.cleanup_session_instances()` (이미 적용됨)
   - 다른 상태 변경 메서드들 검토 및 적용


#### 2.3 프론트엔드 컴포넌트 분리

**목표**: EditorMode 거대 컴포넌트 분리

**작업 내용**:
1. **컴포넌트 구조 설계**
   ```
   app/ui/frontend/src/components/editor/
   ├── EditorMode.tsx (메인, 200줄 이하로 축소)
   ├── MapEditor/
   │   ├── MapCanvas.tsx
   │   ├── HierarchicalMapView.tsx
   │   └── MapToolbar.tsx
   ├── EntityExplorer/
   │   ├── EntityTree.tsx
   │   ├── EntityEditor.tsx
   │   └── EntityPropertyPanel.tsx
   ├── PinEditor/
   │   ├── PinList.tsx
   │   ├── PinEditor.tsx
   │   └── PinTreeView.tsx
   └── hooks/
       ├── useMapState.ts
       ├── useEntityState.ts
       └── usePinState.ts
   ```

2. **단계별 리팩토링**
   - 1단계: MapEditor 관련 로직 분리
   - 2단계: EntityExplorer 관련 로직 분리
   - 3단계: PinEditor 관련 로직 분리
   - 4단계: 커스텀 훅으로 상태 관리 추출


### Phase 3: 중기 조치

#### 3.1 SSOT 쓰기 경로 봉쇄

**목표**: `cell_occupants` 직접 쓰기 방지

**작업 내용**:
1. **VIEW로 변경 또는 트리거 적용 검토**
   ```sql
   -- 옵션 1: VIEW로 변경
   CREATE VIEW runtime_data.cell_occupants_view AS
   SELECT 
       es.runtime_entity_id,
       (es.current_position->>'runtime_cell_id')::uuid as runtime_cell_id,
       es.session_id
   FROM runtime_data.entity_states es
   WHERE es.current_position->>'runtime_cell_id' IS NOT NULL;
   
   -- 옵션 2: 트리거로 쓰기 방지
   CREATE OR REPLACE FUNCTION prevent_cell_occupants_direct_write()
   RETURNS TRIGGER AS $$
   BEGIN
       RAISE EXCEPTION 'cell_occupants는 직접 수정할 수 없습니다. entity_states.current_position을 수정하세요.';
   END;
   $$ LANGUAGE plpgsql;
   
   CREATE TRIGGER prevent_cell_occupants_write
   BEFORE INSERT OR UPDATE OR DELETE ON runtime_data.cell_occupants
   FOR EACH ROW EXECUTE FUNCTION prevent_cell_occupants_direct_write();
   ```

2. **코드 레벨 검증 추가**
   - `CellManager`에서 `cell_occupants` 직접 접근 금지
   - `current_position` 업데이트만 허용


#### 3.2 ENUM 타입 도입

**목표**: 문자열 타입을 ENUM으로 변경하여 타입 안전성 향상

**작업 내용**:
1. **ENUM 타입 생성**
   ```sql
   -- 파일: database/migrations/add_enum_types.sql (신규 생성)
   CREATE TYPE entity_type_enum AS ENUM ('player', 'npc', 'monster', 'creature');
   CREATE TYPE carrier_type_enum AS ENUM ('skill', 'buff', 'item', 'blessing', 'curse', 'ritual');
   CREATE TYPE effect_type_enum AS ENUM ('damage', 'heal', 'buff', 'debuff', 'status');
   ```

2. **컬럼 타입 변경**
   ```sql
   ALTER TABLE game_data.entities
   ALTER COLUMN entity_type TYPE entity_type_enum USING entity_type::entity_type_enum;
   
   ALTER TABLE reference_layer.effect_carriers
   ALTER COLUMN carrier_type TYPE carrier_type_enum USING carrier_type::carrier_type_enum;
   ```

3. **Python 코드 업데이트**
   - Pydantic 모델에서 Enum 사용
   - 타입 힌트 업데이트


### Phase 4: 장기 조치

#### 4.1 마이그레이션 전략 수립

**목표**: 스키마 변경을 체계적으로 관리

**작업 내용**:
1. **Alembic 도입**
   ```bash
   pip install alembic
   alembic init alembic
   ```

2. **마이그레이션 디렉토리 구조**
   ```
   database/
   ├── migrations/
   │   ├── versions/
   │   │   ├── 001_initial_schema.py
   │   │   ├── 002_add_uuid_constraints.py
   │   │   └── 003_add_jsonb_validation.py
   │   └── alembic.ini
   └── setup/
       └── mvp_schema.sql
   ```

3. **마이그레이션 가이드라인 문서 작성**
   - 파일: `docs/development/MIGRATION_GUIDELINES.md` (신규 생성)


### 우선순위 요약

| Phase | 작업 | 우선순위 | 의존성 |
|-------|------|----------|--------|
| 1 | ID 생성 규칙 강제 | 높음 | 없음 |
| 1 | 공통 예외 처리 모듈화 | 중간 | 없음 |
| 1 | IntegrityService 생성 | 중간 | 없음 |
| 2 | JSONB 구조 검증 | 높음 | 없음 (독립 가능) |
| 2 | 트랜잭션 정책 문서화 | 중간 | 없음 |
| 2 | 프론트엔드 컴포넌트 분리 | 낮음 | 없음 |
| 3 | SSOT 쓰기 경로 봉쇄 | 중간 | Phase 2 |
| 3 | ENUM 타입 도입 | 낮음 | Phase 2 |
| 4 | 마이그레이션 전략 | 낮음 | Phase 3 |

### 실행 체크리스트

각 Phase 시작 전:
- [ ] 관련 문서 검토 완료
- [ ] 테스트 환경 준비
- [ ] 백업 생성

각 작업 완료 후:
- [ ] 단위 테스트 작성/업데이트
- [ ] 통합 테스트 수행
- [ ] 문서 업데이트
- [ ] 코드 리뷰 (가능한 경우)

Phase 완료 후:
- [ ] 전체 시스템 테스트
- [ ] 성능 테스트 (필요시)
- [ ] 문서 최종 검토

