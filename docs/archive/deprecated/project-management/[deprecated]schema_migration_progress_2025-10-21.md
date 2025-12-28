# [deprecated] MVP Schema 3-Layer 구조 마이그레이션 진행 상황

> **Deprecated 날짜**: 2025-12-28  
> **Deprecated 사유**: 스키마 마이그레이션 작업이 완료되어 더 이상 진행 중인 작업이 아닙니다. 현재는 Phase 4+ 개발이 진행 중이며, 이 문서는 특정 시점(2025-10-21)의 마이그레이션 진행 상황을 기록한 것입니다.

**날짜**: 2025-10-21  
**작업자**: AI Assistant  
**목표**: EntityManager, CellManager를 MVP Schema 3-Layer 구조에 맞게 수정

---

## 📊 MVP Schema 3-Layer 구조

```
game_data.entities (정적 템플릿)
        ↓
runtime_data.runtime_entities (참조: runtime_entity_id + game_entity_id + session_id)
        ↓
runtime_data.entity_states (가변 상태: current_stats, current_position, active_effects, inventory, equipped_items)
```

---

## ✅ 완료된 작업

### 1. **EntityManager.create_entity 수정**
- `runtime_data.entity_states` 테이블에 초기 상태 저장 로직 추가
- `runtime_entity_id`, `current_stats`, `current_position`, `active_effects`, `inventory`, `equipped_items` 삽입
- **파일**: `app/entity/entity_manager.py` (Line 243-255)

### 2. **CellManager.add_entity_to_cell 수정**
- `runtime_data.runtime_entities` → `runtime_data.entity_states` 테이블 사용
- `properties` → `current_position` JSONB 필드에 `current_cell_id` 저장
- `WHERE entity_id` → `WHERE runtime_entity_id` 수정
- **파일**: `app/world/cell_manager.py` (Line 744-757)

### 3. **CellManager.remove_entity_from_cell 수정**
- `runtime_data.entity_states` 테이블에서 `current_cell_id` 제거
- **파일**: `app/world/cell_manager.py` (Line 791-800)

### 4. **CellManager._load_cell_content_from_db 쿼리 수정**
- 3-Layer 조인 쿼리로 변경:
  ```sql
  SELECT 
      re.runtime_entity_id as entity_id,
      ge.entity_name as name,
      ge.entity_type,
      es.current_stats as properties,
      es.current_position as position
  FROM runtime_data.runtime_entities re
  JOIN game_data.entities ge ON re.game_entity_id = ge.entity_id
  JOIN runtime_data.entity_states es ON re.runtime_entity_id = es.runtime_entity_id
  WHERE es.current_position->>'current_cell_id' = $1
  ```
- **파일**: `app/world/cell_manager.py` (Line 543-554)

### 5. **데이터 변환 로직 추가**
- UUID → 문자열 변환
- JSONB 문자열 → Python dict 파싱 (`parse_jsonb_data` 사용)
- PostgreSQL alias fallback 처리 (runtime_entity_id/entity_id, current_stats/properties, current_position/position)
- **파일**: `app/world/cell_manager.py` (Line 562-576)

---

## ⚠️ 현재 이슈

### **Indentation 문제**
- **증상**: CURSOR의 `search_replace` 도구로 수정 시 indentation이 깨지는 현상 반복
- **원인**: 짧은 컨텍스트를 사용할 경우 유사한 패턴을 잘못 매칭
- **해결책**: 사용자 지침대로 **긴 고유한 컨텍스트**(위아래 10줄 이상)를 사용하여 수정
- **영향 받은 파일**:
  - `app/entity/entity_manager.py` (Line 367 - except 블록)
  - `app/world/cell_manager.py` (Line 540, 733, 760 - pool/except 블록)

### **PostgreSQL Alias 문제**
- **증상**: `SELECT re.runtime_entity_id as entity_id` alias가 작동하지 않음
- **에러**: `'runtime_entity_id': UUID...` - alias 대신 원본 컬럼명 반환
- **해결책**: Python 변환 로직에서 fallback 처리 (양쪽 컬럼명 모두 체크)

---

## 🔄 다음 단계

### 1. **Indentation 수정 완료** (최우선)
- 사용자가 수정한 올바른 버전 확인
- 추가 변경사항만 긴 컨텍스트로 적용

### 2. **테스트 실행 및 검증**
```bash
python -m pytest tests/active/scenarios/test_entity_cell_interaction.py::TestEntityCellInteraction::test_entity_enters_cell -xvs
```

### 3. **전체 시나리오 테스트 실행**
```bash
python -m pytest tests/active/scenarios/test_entity_cell_interaction.py -v
```

### 4. **추가 Manager 클래스 마이그레이션** (필요 시)
- `DialogueManager`
- `ActionHandler`
- `EffectCarrierManager`

---

## 📝 교훈

1. **긴 고유 컨텍스트 사용**: `search_replace` 사용 시 최소 10줄 이상의 고유한 컨텍스트 포함
2. **작업 버전 백업**: 각 단계마다 작동하는 버전을 `_working.py`, `_fixed.py`로 백업
3. **PostgreSQL alias 신뢰 금지**: JSONB 및 UUID 타입은 Python에서 명시적 변환 필요
4. **사용자 수정 존중**: 사용자가 직접 수정한 파일은 최대한 보존하고, 추가 변경만 적용

---

## 📂 관련 파일

- **Schema**: `database/setup/mvp_schema.sql`
- **Manager 클래스**: 
  - `app/entity/entity_manager.py`
  - `app/world/cell_manager.py`
- **테스트**: `tests/active/scenarios/test_entity_cell_interaction.py`
- **Utils**: `common/utils/jsonb_handler.py`

---

## 🎯 최종 목표

✅ `test_entity_enters_cell` 테스트 통과  
⬜ `test_entity_moves_between_cells` 테스트 통과  
⬜ `test_multiple_entities_in_cell` 테스트 통과  
⬜ `test_entity_leaves_cell` 테스트 통과  

**목표 달성 시**: Phase1 Entity-Cell Interaction 시나리오 완료 →  Phase2로 진행

