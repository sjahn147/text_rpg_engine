# Location 및 Cell Properties SSOT 분석 및 구현 계획

**작성일**: 2025-01-XX  
**프로젝트**: RPG Engine - World Editor  
**버전**: v1.0.0

## 🔍 SSOT (Single Source of Truth) 위험성 분석

### ⚠️ High Risk: 캐시된 데이터 (Denormalization)

#### 1. `ownership.owner_name` (Location, Cell)
**위험도**: 🔴 **HIGH**

**문제점:**
- `ownership.owner_entity_id`는 참조이므로 OK
- `ownership.owner_name`은 엔티티 이름을 캐시하는 것으로, 엔티티 이름 변경 시 동기화 문제 발생

**시나리오:**
```
1. Location의 owner_name = "상인 토마스" 저장
2. entities 테이블에서 entity_name = "상인 토마스" → "상인 존" 변경
3. location_properties.ownership.owner_name은 여전히 "상인 토마스" (불일치!)
```

**해결 방안:**
- **Option A (권장)**: `owner_name` 제거, 항상 `owner_entity_id`로 조회
  ```json
  {
    "ownership": {
      "owner_entity_id": "NPC_MERCHANT_001",
      // owner_name 제거 - entities 테이블에서 조회
    }
  }
  ```
- **Option B**: 트리거/이벤트로 동기화 (복잡도 증가)
- **Option C**: 읽기 전용 표시 필드로만 사용 (UI 표시용, 수정 불가)

**권장**: Option A - `owner_name` 제거, API에서 조회 시 JOIN하여 반환

---

### ⚠️ Medium Risk: 중복 참조 (Redundant References)

#### 2. `quests.quest_givers` (Location)
**위험도**: 🟡 **MEDIUM**

**문제점:**
- NPC ID 목록을 Properties에 저장하지만, 실제 NPC는 `entities` 테이블에 존재
- NPC 삭제 시 Properties의 참조가 고아(orphan)가 될 수 있음

**해결 방안:**
- **Option A (권장)**: 참조만 저장, 삭제 시 검증
  ```json
  {
    "quests": {
      "available_quests": ["QUEST_DELIVERY_001"],
      "quest_givers": ["NPC_MERCHANT_001"]  // 참조만 저장
    }
  }
  ```
- **Option B**: Foreign Key 제약조건 (JSONB 배열은 FK 불가능)
- **Option C**: 별도 테이블로 분리 (과도한 정규화)

**권장**: Option A + 삭제 시 검증 로직 추가

---

#### 3. `accessibility.entry_points.cell_id` (Location)
**위험도**: 🟡 **MEDIUM**

**문제점:**
- Cell ID 참조가 Properties에 저장되지만, 실제 Cell은 `world_cells` 테이블에 존재
- Cell 삭제 시 Properties의 참조가 고아가 될 수 있음

**해결 방안:**
- **Option A (권장)**: 참조만 저장, 삭제 시 검증
  ```json
  {
    "accessibility": {
      "entry_points": [
        {"direction": "north", "cell_id": "CELL_MARKET_ENTRANCE_001"}
      ]
    }
  }
  ```
- **Option B**: 별도 테이블로 분리 (과도한 정규화)

**권장**: Option A + 삭제 시 검증 로직 추가

---

#### 4. `structure.exits.cell_id`, `structure.entrances.cell_id` (Cell)
**위험도**: 🟡 **MEDIUM**

**문제점:**
- Cell 간 연결 정보가 Properties에 저장되지만, 양방향 일관성 보장 어려움
- Cell A → Cell B 연결이 있으면, Cell B → Cell A 연결도 있어야 하는가?

**해결 방안:**
- **Option A (권장)**: 단방향 참조만 저장, 양방향은 애플리케이션 로직으로 처리
  ```json
  {
    "structure": {
      "exits": [
        {"direction": "north", "cell_id": "CELL_CORRIDOR_001", "requires_key": false}
      ]
    }
  }
  ```
- **Option B**: 별도 테이블 `cell_connections`로 분리 (정규화)

**권장**: Option A (게임플레이상 단방향 연결이 자연스러움)

---

### ⚠️ Low Risk: 구조적 중복 (Structural Duplication)

#### 5. `structure.exits` vs `special.locked_doors` (Cell)
**위험도**: 🟢 **LOW**

**문제점:**
- 잠금 정보가 두 곳에 저장될 수 있음
- `structure.exits[].requires_key`와 `special.locked_doors[]`의 역할 구분 필요

**해결 방안:**
- **Option A (권장)**: 역할 분리
  - `structure.exits`: 셀 간 연결 정보 (방향, 목적지, 잠금 여부)
  - `special.locked_doors`: 특수 문 오브젝트 정보 (위치, 열쇠 ID)
- **Option B**: 통합 (하나로 통합)

**권장**: Option A - 역할이 다르므로 분리 유지

---

#### 6. `gameplay.interaction_zones` vs `objects.interaction_zones` (Cell)
**위험도**: 🟢 **LOW**

**문제점:**
- 상호작용 영역이 두 곳에 정의될 수 있음

**해결 방안:**
- **Option A (권장)**: 역할 분리
  - `gameplay.interaction_zones`: 게임플레이 메커니즘용 (제작대, 휴식 지점)
  - `objects.interaction_zones`: 오브젝트 배치용 (실제 오브젝트와 연관)
- **Option B**: 통합

**권장**: Option A - 역할이 다르므로 분리 유지

---

## 📋 수정된 Properties 구조 (SSOT 준수)

### Location Properties (수정안)

```json
{
  "background_music": "peaceful_01",
  "ambient_effects": ["birds", "wind"],
  
  "accessibility": {
    "is_public": true,
    "requires_key": false,
    "key_item_id": null,
    "requires_permission": null,
    "access_conditions": [],
    "entry_points": [
      {"direction": "north", "cell_id": "CELL_MARKET_ENTRANCE_001"}
      // cell_id는 참조만 저장, 삭제 시 검증 필요
    ]
  },
  
  "ownership": {
    "owner_entity_id": "NPC_MERCHANT_001",
    // owner_name 제거 - entities 테이블에서 조회
    "ownership_type": "public",
    "faction_control": null,
    "tax_rate": 0.05
  },
  
  "quests": {
    "available_quests": ["QUEST_DELIVERY_001"],
    "quest_givers": ["NPC_MERCHANT_001"]
    // 참조만 저장, 삭제 시 검증 필요
  }
  
  // ... 나머지 속성 동일
}
```

### Cell Properties (수정안)

```json
{
  "structure": {
    "exits": [
      {"direction": "north", "cell_id": "CELL_CORRIDOR_001", "requires_key": false}
      // cell_id는 참조만 저장, 삭제 시 검증 필요
    ],
    "entrances": [
      {"direction": "south", "cell_id": "CELL_LOBBY_001"}
    ],
    "connections": [
      {"cell_id": "CELL_ADJACENT_001", "connection_type": "door", "is_locked": false}
    ],
    "barriers": [
      {"type": "wall", "position": {"x": 10, "y": 0}, "direction": "north"}
    ]
  },
  
  "ownership": {
    "owner_entity_id": "NPC_MERCHANT_001",
    // owner_name 제거 - entities 테이블에서 조회
    "is_private": false,
    "access_restrictions": {
      "requires_key": false,
      "requires_permission": null,
      "allowed_entities": []
    }
  }
  
  // ... 나머지 속성 동일
}
```

---

## 🛠️ 구현 계획

### Phase 1: SSOT 위험 제거 (High Priority)

#### 1.1 `owner_name` 제거 및 API 수정
**작업:**
- [ ] `ownership.owner_name` 필드 제거
- [ ] Location/Cell 조회 API에서 `owner_entity_id`로 JOIN하여 `owner_name` 반환
- [ ] 프론트엔드에서 `owner_name` 직접 표시 대신 API 응답 사용

**파일:**
- `app/world_editor/schemas.py`: `LocationProperties`, `CellProperties` 스키마 수정
- `app/world_editor/services/location_service.py`: `get_location`에서 JOIN 추가
- `app/world_editor/services/cell_service.py`: `get_cell`에서 JOIN 추가
- `app/world_editor/frontend/src/components/PinEditorNew.tsx`: UI 수정

**테스트:**
- [ ] 엔티티 이름 변경 시 Location/Cell의 owner_name이 자동 업데이트되는지 확인
- [ ] `owner_entity_id`가 null인 경우 처리 확인

---

### Phase 2: 참조 무결성 검증 (Medium Priority)

#### 2.1 삭제 시 참조 검증 로직 추가
**작업:**
- [ ] Entity 삭제 시 `location_properties.ownership.owner_entity_id` 참조 검증
- [ ] Entity 삭제 시 `cell_properties.ownership.owner_entity_id` 참조 검증
- [ ] Entity 삭제 시 `location_properties.quests.quest_givers` 참조 검증
- [ ] Cell 삭제 시 `location_properties.accessibility.entry_points.cell_id` 참조 검증
- [ ] Cell 삭제 시 `cell_properties.structure.exits.cell_id` 참조 검증

**파일:**
- `app/world_editor/services/entity_service.py`: `delete_entity` 수정
- `app/world_editor/services/cell_service.py`: `delete_cell` 수정
- `app/world_editor/services/location_service.py`: `delete_location` 수정

**검증 로직:**
```python
async def validate_entity_references(self, entity_id: str) -> List[str]:
    """엔티티가 참조되는 Location/Cell 목록 반환"""
    # location_properties에서 owner_entity_id 검색
    # cell_properties에서 owner_entity_id 검색
    # location_properties에서 quest_givers 검색
    return conflicting_locations_or_cells

async def validate_cell_references(self, cell_id: str) -> List[str]:
    """Cell이 참조되는 Location/Cell 목록 반환"""
    # location_properties에서 entry_points.cell_id 검색
    # cell_properties에서 structure.exits.cell_id 검색
    return conflicting_locations_or_cells
```

**테스트:**
- [ ] Entity 삭제 시 참조된 Location/Cell이 있으면 에러 반환
- [ ] Cell 삭제 시 참조된 Location/Cell이 있으면 에러 반환
- [ ] 참조 제거 후 삭제 가능한지 확인

---

### Phase 3: 데이터 마이그레이션 (Medium Priority)

#### 3.1 기존 데이터 정리
**작업:**
- [ ] 기존 `ownership.owner_name` 데이터 제거
- [ ] 고아 참조 정리 (존재하지 않는 entity_id, cell_id 제거)
- [ ] 중복 참조 정리 (`structure.exits`와 `special.locked_doors` 통합 검토)

**마이그레이션 스크립트:**
```sql
-- owner_name 제거
UPDATE game_data.world_locations
SET location_properties = location_properties - 'ownership' || 
    jsonb_build_object('ownership', 
      location_properties->'ownership' - 'owner_name'
    )
WHERE location_properties->'ownership'->>'owner_name' IS NOT NULL;

-- 고아 참조 정리 (예시)
UPDATE game_data.world_locations
SET location_properties = jsonb_set(
  location_properties,
  '{ownership,owner_entity_id}',
  'null'::jsonb
)
WHERE NOT EXISTS (
  SELECT 1 FROM game_data.entities 
  WHERE entity_id = location_properties->'ownership'->>'owner_entity_id'
);
```

---

### Phase 4: API 개선 (Low Priority)

#### 4.1 참조 해결 API 추가
**작업:**
- [ ] `GET /api/locations/{location_id}/resolved` - 모든 참조를 해결한 Location 반환
- [ ] `GET /api/cells/{cell_id}/resolved` - 모든 참조를 해결한 Cell 반환

**응답 구조:**
```json
{
  "location_id": "LOC_MARKET_001",
  "location_name": "시장",
  "ownership": {
    "owner_entity_id": "NPC_MERCHANT_001",
    "owner_name": "상인 토마스",  // JOIN으로 해결
    "owner_entity": {  // 전체 엔티티 정보 (선택적)
      "entity_id": "NPC_MERCHANT_001",
      "entity_name": "상인 토마스",
      "entity_type": "npc"
    }
  },
  "accessibility": {
    "entry_points": [
      {
        "direction": "north",
        "cell_id": "CELL_MARKET_ENTRANCE_001",
        "cell": {  // 전체 Cell 정보 (선택적)
          "cell_id": "CELL_MARKET_ENTRANCE_001",
          "cell_name": "시장 입구"
        }
      }
    ]
  }
}
```

---

## 📊 우선순위 요약

### High Priority (즉시 수정)
1. ✅ `ownership.owner_name` 제거
2. ✅ API에서 JOIN하여 `owner_name` 반환

### Medium Priority (다음 스프린트)
3. ✅ 삭제 시 참조 검증 로직 추가
4. ✅ 기존 데이터 마이그레이션

### Low Priority (향후 개선)
5. 참조 해결 API 추가
6. 양방향 연결 자동 동기화

---

## 📌 설계 원칙

### 1. 참조는 ID만 저장
- Properties에 저장되는 참조는 ID만 저장
- 이름, 설명 등은 항상 원본 테이블에서 조회

### 2. 삭제 시 검증 필수
- 참조된 엔티티/Cell 삭제 시 검증 로직 실행
- 고아 참조 방지

### 3. 읽기 시 JOIN
- API 응답에서 참조를 해결하여 반환
- 프론트엔드는 해결된 데이터 사용

### 4. 역할 분리
- 구조적 정보와 메타데이터는 역할에 따라 분리
- 중복은 허용하되 역할이 명확해야 함

---

## 🔗 관련 문서

- [Location 및 Cell Properties 확장 명세서](./53_location_cell_properties_extension.md)
- [Cell Properties 기본 명세](./51_cell_properties_specification.md)
- [데이터 일관성 이슈 분석](../../architecture/db_schema/04_data_consistency_issues.md)

