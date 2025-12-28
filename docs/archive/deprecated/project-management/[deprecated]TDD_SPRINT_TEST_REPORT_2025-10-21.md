# [deprecated] 엔티티-셀 상호작용 시나리오 테스트 보고서

> **Deprecated 날짜**: 2025-12-28  
> **Deprecated 사유**: 이 테스트 보고서는 특정 시점(2025-10-21)의 테스트 결과를 기록한 것으로, 현재는 Phase 4+ 개발이 진행 중이며 더 최신 테스트 결과는 readme.md와 최신 문서들을 참조해야 합니다.

**날짜**: 2025-10-21  
**테스트 대상**: `tests/active/scenarios/test_entity_cell_interaction.py`  
**결과**: ✅ **4/4 테스트 통과**

---

## 🎯 테스트 목표

MVP 스키마 3-Layer 구조에서 엔티티와 셀 간의 상호작용이 올바르게 작동하는지 검증

### MVP 스키마 3-Layer 구조
```
game_data.entities (정적 템플릿)
        ↓
runtime_data.runtime_entities (참조: runtime_entity_id + game_entity_id + session_id)
        ↓
runtime_data.entity_states (가변 상태: current_stats, current_position, active_effects, inventory, equipped_items)
```

---

## ✅ 테스트 결과

### 1. `test_entity_enters_cell` ✅
- **시나리오**: 엔티티가 셀에 진입
- **검증**: 셀 컨텐츠에 엔티티가 포함됨
- **결과**: PASSED

### 2. `test_entity_moves_between_cells` ✅
- **시나리오**: 엔티티가 셀 A에서 셀 B로 이동
- **검증**: 
  - 셀 A에서 엔티티 제거 확인
  - 셀 B에 엔티티 추가 확인
- **결과**: PASSED

### 3. `test_multiple_entities_in_cell` ✅
- **시나리오**: 한 셀에 여러 엔티티 배치
- **검증**: 셀 컨텐츠에 3개의 엔티티 모두 포함됨
- **결과**: PASSED

### 4. `test_entity_leaves_cell` ✅
- **시나리오**: 엔티티가 셀에서 이탈
- **검증**: 셀 컨텐츠에서 엔티티 제거 확인
- **결과**: PASSED

---

## 🔧 수정된 내용

### 1. **EntityManager.create_entity**
- `runtime_data.entity_states` 테이블에 초기 상태 저장 로직 추가
- 파일: `app/entity/entity_manager.py` (Line 243-255)

```python
# entity_states 테이블에 초기 상태 저장 (MVP 스키마 준수)
await self.db.execute_query("""
    INSERT INTO runtime_data.entity_states 
    (runtime_entity_id, current_stats, current_position, active_effects, inventory, equipped_items, created_at, updated_at)
    VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
""", 
runtime_entity_id,
serialize_jsonb_data(base_stats or {}),
serialize_jsonb_data(custom_position or {"x": 0.0, "y": 0.0}),
serialize_jsonb_data([]),  # active_effects
serialize_jsonb_data([]),  # inventory
serialize_jsonb_data([])   # equipped_items
)
```

### 2. **CellManager.add_entity_to_cell**
- `runtime_data.entity_states` 테이블의 `current_position`에 `current_cell_id` 저장
- 파일: `app/world/cell_manager.py` (Line 760-773)

```python
# entity_states 테이블에 cell_id 업데이트 (current_position에 저장)
await conn.execute("""
    UPDATE runtime_data.entity_states
    SET current_position = jsonb_set(
        COALESCE(current_position, '{}'::jsonb),
        '{current_cell_id}',
        to_jsonb($1::text)
    ),
    updated_at = NOW()
    WHERE runtime_entity_id = $2
""", cell_id, entity_id)
```

### 3. **CellManager.remove_entity_from_cell**
- `runtime_data.entity_states` 테이블에서 `current_cell_id` 제거
- 파일: `app/world/cell_manager.py` (Line 803-812)

```python
# entity_states 테이블에서 cell_id 제거
await conn.execute("""
    UPDATE runtime_data.entity_states
    SET current_position = current_position - 'current_cell_id',
    updated_at = NOW()
    WHERE runtime_entity_id = $1
""", entity_id)
```

### 4. **CellManager._load_cell_content_from_db**
- 3-Layer 조인 쿼리로 변경
- UUID → 문자열 변환
- JSONB → dict 파싱
- position에서 current_cell_id 제거 (Pydantic validation)
- 파일: `app/world/cell_manager.py` (Line 537-589)

```python
# 셀 내 엔티티 조회 (3-Layer 구조 사용)
entity_rows = await conn.fetch("""
    SELECT 
        re.runtime_entity_id,
        ge.entity_name as name,
        ge.entity_type,
        es.current_stats,
        es.current_position
    FROM runtime_data.runtime_entities re
    JOIN game_data.entities ge ON re.game_entity_id = ge.entity_id
    JOIN runtime_data.entity_states es ON re.runtime_entity_id = es.runtime_entity_id
    WHERE es.current_position->>'current_cell_id' = $1
""", cell_id)

# 엔티티 데이터 변환 (UUID → str, JSONB → dict, position에서 current_cell_id 제거)
entities = []
for row in entity_rows:
    # position에서 current_cell_id 제거 (숫자 좌표만 포함)
    position_data = parse_jsonb_data(row['current_position'])
    if position_data and 'current_cell_id' in position_data:
        position_data = {k: v for k, v in position_data.items() if k != 'current_cell_id'}
    
    entities.append({
        'entity_id': str(row['runtime_entity_id']),
        'name': row['name'],
        'entity_type': row['entity_type'],
        'properties': parse_jsonb_data(row['current_stats']),
        'position': position_data or {'x': 0.0, 'y': 0.0}
    })
```

### 5. **CellManager.move_entity_between_cells**
- `new_position` 업데이트 시 `current_cell_id` 유지
- 파일: `app/world/cell_manager.py` (Line 865-876)

```python
# 3. 위치 업데이트 (선택사항 - current_cell_id 유지)
if new_position:
    # current_cell_id를 유지하면서 좌표만 업데이트
    position_with_cell = new_position.copy()
    position_with_cell['current_cell_id'] = to_cell_id
    
    await conn.execute("""
        UPDATE runtime_data.entity_states
        SET current_position = $1,
        updated_at = NOW()
        WHERE runtime_entity_id = $2
    """, serialize_jsonb_data(position_with_cell), entity_id)
```

### 6. **EntityType Enum에 ENEMY 추가**
- `test_templates.sql`의 `enemy` 타입과 매칭
- 파일: `app/entity/entity_manager.py` (Line 27)

```python
class EntityType(str, Enum):
    """엔티티 타입 열거형"""
    PLAYER = "player"
    NPC = "npc"
    MONSTER = "monster"
    ENEMY = "enemy"
    OBJECT = "object"
```

### 7. **테스트 코드 수정**
- `enter_cell` → `add_entity_to_cell` API 변경
- 파일: `tests/active/scenarios/test_entity_cell_interaction.py` (Line 231)

---

## 📊 성능

- **평균 테스트 시간**: 0.71초 (4개 테스트)
- **DB 트랜잭션**: 정상 작동
- **3-Layer 조인 쿼리**: 성능 이슈 없음

---

## 🎓 교훈

### 1. **CURSOR search_replace 도구의 한계**
- 짧은 컨텍스트 사용 시 잘못된 위치 매칭
- Indentation 문제 반복 발생
- **해결**: 사용자가 직접 Cell Manager 수정

### 2. **PostgreSQL JSONB alias 문제**
- `SELECT column as alias`가 일부 케이스에서 작동하지 않음
- **해결**: Python에서 명시적으로 컬럼명 사용

### 3. **position 데이터 구조**
- `current_cell_id`를 position에 저장하되, Pydantic validation 시 제거 필요
- `Dict[str, float]` 타입이므로 문자열 값 허용 안 됨

---

## 🔜 다음 단계

### Phase 1 완료 항목
- ✅ 엔티티-셀 상호작용 시나리오 테스트

### Phase 1 남은 항목
- ⬜ 동시 다중 세션 테스트
- ⬜ 대량 엔티티 생성 성능 테스트

### Phase 2
- ⬜ DialogueManager CRUD 메서드 검증
- ⬜ ActionHandler CRUD 메서드 검증

### Phase 3
- ⬜ 100일 Village Simulation 시나리오 테스트

---

## 📁 관련 파일

### 수정된 파일
- `app/entity/entity_manager.py`
- `app/world/cell_manager.py`
- `tests/active/scenarios/test_entity_cell_interaction.py`

### 참조 문서
- `database/setup/mvp_schema.sql` - MVP 스키마 정의
- `docs/dev/schema_migration_progress_2025-10-21.md` - 마이그레이션 진행 상황
- `docs/dev/TDD_SPRINT_PROGRESS_2025-10-20.md` - 기존 TDD 진행 상황

---

**작성**: AI Assistant  
**검증**: 사용자 리뷰 및 수동 테스트  
**최종 업데이트**: 2025-10-21 00:15 KST

