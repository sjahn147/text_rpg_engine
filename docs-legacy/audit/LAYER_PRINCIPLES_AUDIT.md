# 3계층 구조 원칙 준수 검수 결과

**검수 일자**: 2025-12-31  
**검수 범위**: `app/managers/cell_manager.py`

## 원칙 요약

1. **game_data 레이어**: VARCHAR(50) 사용 (예: `CELL_VILLAGE_CENTER_001`)
2. **runtime_data 레이어**: UUID 사용 (예: `bd1d0168-b925-4b98-a6b6-441b187d9dc9`)
3. **reference_layer 레이어**: UUID ↔ VARCHAR 변환 역할

## 발견된 문제 및 수정 사항

### 1. `add_entity_to_cell` 메서드 (라인 1018)

**문제**:
```python
to_jsonb($1::text)  # UUID를 text로 직접 변환 시도
```

**원인**: UUID 타입을 받을 때 `::text`로 직접 변환하면 타입 불일치 발생

**수정**:
```python
to_jsonb($1::uuid::text)  # UUID → text 변환
```

**원칙 준수**: runtime_cell_id는 UUID이므로 명시적으로 uuid::text 변환 필요

### 2. `_load_cell_content_from_db` 메서드 (라인 650)

**문제**:
```python
# str인 경우에도 runtime_cell_id로 조회
WHERE runtime_cell_id = $1
```

**원인**: str인 경우 game_cell_id(VARCHAR)이므로 runtime_cells에서 조회 불가

**수정**:
```python
# UUID인 경우에만 runtime_cells에서 조회
if isinstance(cell_id, UUID):
    cell_ref = await conn.fetchrow("""
        SELECT game_cell_id, session_id
        FROM runtime_data.runtime_cells
        WHERE runtime_cell_id = $1
    """, cell_id)
```

**원칙 준수**: game_cell_id(VARCHAR)는 runtime_cells에 없으므로 조회 불가

### 3. `_load_cell_content_from_db` 메서드 (라인 668)

**문제**:
```python
WHERE es.current_position->>'runtime_cell_id' = $1
```

**원인**: UUID를 문자열로 변환하지 않으면 타입 불일치 발생

**수정**:
```python
WHERE es.current_position->>'runtime_cell_id' = $1::text
```

**원칙 준수**: JSONB에서 추출한 문자열과 UUID를 비교할 때 명시적 변환 필요

## 검수 결과

### ✅ 올바르게 구현된 부분

1. **`get_cell` 메서드**: UUID인 경우 reference_layer를 통해 game_cell_id 변환
2. **`_get_game_cell_id_from_runtime_id` 메서드**: reference_layer를 통한 변환 로직 구현
3. **`_load_cell_from_db` 메서드**: game_cell_id(VARCHAR)만 받아서 game_data 조회

### ⚠️ 수정 완료된 부분

1. `add_entity_to_cell`: UUID → text 변환 명시
2. `_load_cell_content_from_db`: str인 경우 runtime_cells 조회 제거
3. `_load_cell_content_from_db`: UUID → text 변환 명시

## 권장 사항

1. **타입 힌트 명확화**: `Union[str, UUID]` 사용 시 주석으로 각 경우 설명
2. **변환 로직 통합**: UUID ↔ VARCHAR 변환을 공통 함수로 추출
3. **테스트 강화**: UUID와 VARCHAR 모두 테스트 케이스 추가

## 검수 스크립트

`scripts/audit_layer_principles.py`로 자동 검수 가능

