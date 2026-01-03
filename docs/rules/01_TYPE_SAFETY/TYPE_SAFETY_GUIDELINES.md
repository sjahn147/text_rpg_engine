# 타입 안전성 종합 가이드라인

> **최신화 날짜**: 2026-01-03  
> **적용 범위**: 모든 백엔드 코드 작성 전 필수 읽기

## 1. 개요

이 문서는 RPG 엔진에서 타입 안전성을 보장하기 위한 종합 가이드라인입니다. UUID, 트랜잭션, JSONB 처리 등 타입 관련 모든 규칙을 통합합니다.

## 2. 핵심 원칙

### 2.1 Type-Safety-First (타입 안전성 우선)

- 모든 함수, 클래스, API는 타입으로 계약을 명시
- `Any`, `untyped`, `dynamic` 구조는 시스템을 불투명하게 만드는 요소로 금지
- 런타임 오류는 타입 시스템이 예방해야 함

### 2.2 No Uncertainty Principle (불확정성 불허 원칙)

- **추측 로직 금지**: 타입을 추측하는 코드는 절대 금지
- **명시적 처리 필수**: 모든 타입 변환은 명시적으로 처리하고 검증
- **에러 우선 처리**: 변환 실패 시 기본값으로 대체하지 않고 명시적 에러 발생

## 3. UUID 타입 안전성

**⚠️ 중요**: UUID 관련 상세 가이드라인은 `01_TYPE_SAFETY/UUID_GUIDELINES.md`를 참조하세요.

### 3.1 핵심 원칙 요약

- **UUID 객체**: 내부 로직에서 사용 (`uuid.UUID` 타입)
- **UUID 문자열**: API 경계 및 JSONB 저장 시 사용 (`str` 타입)
- **헬퍼 함수 필수**: 모든 UUID 변환/비교는 `app/common/utils/uuid_helper.py` 사용

### 3.2 필수 사용 함수

```python
from app.common.utils.uuid_helper import (
    normalize_uuid,        # UUID → 문자열 (JSONB 저장용)
    to_uuid,              # 문자열 → UUID 객체
    compare_uuids,        # 타입 무관 비교
    is_valid_uuid,        # 유효성 검증
    ensure_uuid_string,   # UUID 문자열 보장
    ensure_uuid_object    # UUID 객체 보장
)
```

### 3.3 빠른 참조

```python
# ✅ 올바른 사용
from app.common.utils.uuid_helper import normalize_uuid, to_uuid

# JSONB 저장
position = {'runtime_cell_id': normalize_uuid(uuid_obj)}

# API 경계 변환
uuid_obj = to_uuid(api_string)

# ❌ 잘못된 사용
position = {'runtime_cell_id': str(uuid_obj)}  # ❌ 직접 변환 금지
uuid_obj = UUID(api_string)  # ❌ 직접 변환 금지
```

**자세한 내용**: `01_TYPE_SAFETY/UUID_GUIDELINES.md` 참조

## 4. 트랜잭션 타입 안전성

**⚠️ 중요**: 트랜잭션 관련 상세 가이드라인은 `01_TYPE_SAFETY/TRANSACTION_GUIDELINES.md`를 참조하세요.

### 4.1 트랜잭션 데코레이터 사용

**✅ 올바른 사용**:

```python
from app.common.decorators.transaction import with_transaction

@with_transaction
async def move_entity(
    self,
    entity_id: UUID,
    target_cell_id: UUID,
    conn=None  # 데코레이터가 자동 제공
):
    """엔티티 이동 (트랜잭션 보장)"""
    # conn은 트랜잭션 내부 연결
    await conn.execute("DELETE FROM cell_occupants ...")
    await conn.execute("INSERT INTO cell_occupants ...")
    # 실패 시 자동 롤백
```

**❌ 잘못된 사용**:

```python
# 트랜잭션 없이 다중 테이블 업데이트
async def move_entity(self, entity_id: UUID, target_cell_id: UUID):
    await conn.execute("DELETE FROM cell_occupants ...")  # 실패 시 불일치
    await conn.execute("INSERT INTO cell_occupants ...")  # 실행 안됨
```

### 4.2 트랜잭션이 필요한 작업

다음 작업들은 **반드시** 트랜잭션 내에서 수행:

1. **상태 전이 작업**: 엔티티 이동, 셀 진입/퇴장, 오브젝트 상태 변경
2. **다중 테이블 업데이트**: 엔티티 생성, 셀 생성, 오브젝트 상태 변경
3. **원자성이 중요한 작업**: 게임 시간 틱 처리, 이벤트 트리거

## 5. JSONB 타입 안전성

### 5.1 JSONB 파싱 및 직렬화

**✅ 올바른 사용**:

```python
from common.utils.jsonb_handler import parse_jsonb_data, serialize_jsonb_data

# JSONB 파싱
default_abilities_raw = entity_data.get('default_abilities')
if not default_abilities_raw:
    raise ValueError("default_abilities is required")

default_abilities = parse_jsonb_data(default_abilities_raw)
if not isinstance(default_abilities, dict):
    raise ValueError(f"Invalid default_abilities format: {default_abilities}")

# JSONB 직렬화
abilities_json = serialize_jsonb_data({
    'skills': ['SKILL_001'],
    'magic': ['MAGIC_001']
})
```

**❌ 잘못된 사용**:

```python
# 기본값으로 에러 은폐
default_abilities = parse_jsonb_data(
    entity_data.get('default_abilities', {})  # ❌ 기본값 사용
)

# 타입 검증 없이 사용
skill_ids = default_abilities.get('skills', [])  # ❌ 타입 보장 없음
for skill_id in skill_ids:  # skill_ids가 리스트가 아닐 수 있음
    pass
```

### 5.2 JSONB 내 UUID 처리

**✅ 올바른 사용**:

```python
from app.common.utils.uuid_helper import normalize_uuid

# JSONB에 UUID 저장 시 문자열로 변환
current_position = {
    'x': 5.0,
    'y': 4.0,
    'runtime_cell_id': normalize_uuid(runtime_cell_id)  # ✅ 문자열
}

# JSONB에서 UUID 읽기
position = parse_jsonb_data(current_position_json)
cell_id_str = position.get('runtime_cell_id')
if cell_id_str:
    cell_id_uuid = to_uuid(cell_id_str)  # ✅ 명시적 변환
    if not cell_id_uuid:
        raise ValueError(f"Invalid UUID: {cell_id_str}")
```

**❌ 잘못된 사용**:

```python
# JSONB에 UUID 객체 직접 저장
position = {
    'runtime_cell_id': runtime_cell_id  # ❌ UUID 객체
}
json.dumps(position)  # TypeError 발생

# JSONB에서 UUID 읽기 시 타입 추측
cell_id = position.get('runtime_cell_id')
if isinstance(cell_id, UUID):  # ❌ JSONB는 항상 문자열
    pass
```

## 6. Pydantic 모델 타입 안전성

### 6.1 Pydantic 모델 사용

**✅ 올바른 사용**:

```python
from pydantic import BaseModel, Field, field_validator
from uuid import UUID

class EntityData(BaseModel):
    """엔티티 데이터 모델"""
    entity_id: str = Field(..., min_length=1, max_length=50)
    runtime_entity_id: UUID = Field(...)
    session_id: UUID = Field(...)
    base_stats: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('entity_id')
    @classmethod
    def validate_entity_id(cls, v):
        if not v.strip():
            raise ValueError('entity_id cannot be empty')
        return v.strip()
    
    @field_validator('base_stats')
    @classmethod
    def validate_base_stats(cls, v):
        if not isinstance(v, dict):
            raise ValueError('base_stats must be a dictionary')
        return v
```

**❌ 잘못된 사용**:

```python
# 타입 힌트 없이 정의
class EntityData(BaseModel):
    entity_id = None  # ❌ 타입 불명확
    base_stats = {}   # ❌ 타입 불명확

# Any 타입 사용
class EntityData(BaseModel):
    base_stats: Any = Field(...)  # ❌ 타입 안전성 없음
```

## 7. API 경계 타입 안전성

### 7.1 FastAPI 엔드포인트

**✅ 올바른 사용**:

```python
from fastapi import APIRouter
from pydantic import BaseModel
from uuid import UUID

class MovePlayerRequest(BaseModel):
    session_id: str
    target_cell_id: str

@router.post("/move")
async def move_player(request: MovePlayerRequest):
    """플레이어 이동"""
    # API 경계에서 문자열로 받음
    try:
        session_uuid = UUID(request.session_id)
        target_uuid = UUID(request.target_cell_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid UUID: {e}")
    
    # 내부 로직으로 UUID 객체 전달
    result = await cell_service.move_player(session_uuid, target_uuid)
    
    # 응답은 문자열로 변환
    return {"session_id": str(result.session_id)}
```

**❌ 잘못된 사용**:

```python
# 타입 검증 없이 사용
@router.post("/move")
async def move_player(session_id: str, target_cell_id: str):
    # ❌ UUID 형식 검증 없음
    result = await cell_service.move_player(session_id, target_cell_id)
    # session_id가 UUID 형식이 아닐 수 있음
```

## 8. 타입 에러 방지 체크리스트

### 8.1 개발 전 확인

- [ ] 모든 함수에 타입 힌트가 있는가?
- [ ] UUID 사용 시 `uuid_helper.py` 함수를 사용하는가?
- [ ] JSONB 저장 시 UUID를 문자열로 변환하는가?
- [ ] 트랜잭션이 필요한 작업에 `@with_transaction` 데코레이터를 사용하는가?
- [ ] Pydantic 모델로 런타임 검증을 하는가?
- [ ] `Any` 타입을 사용하지 않는가?
- [ ] 추측 로직을 사용하지 않는가?
- [ ] 기본값으로 에러를 은폐하지 않는가?

### 8.2 코드 리뷰 시 확인

- [ ] 타입 힌트가 명확한가?
- [ ] UUID 변환이 올바른가?
- [ ] JSONB 처리가 올바른가?
- [ ] 트랜잭션이 필요한 곳에 사용되었는가?
- [ ] 에러 처리가 명시적인가?
- [ ] 추측 로직이 없는가?

## 9. 가장 자주 발생하는 타입 에러

### 9.1 UUID 타입 혼용 에러

**증상**: `TypeError: expected string or bytes-like object, got 'UUID'`

**원인**: UUID 객체를 문자열로 기대하는 곳에 전달

**해결**: `normalize_uuid()` 사용

### 9.2 JSON 직렬화 실패

**증상**: `TypeError: Object of type UUID is not JSON serializable`

**원인**: JSONB에 UUID 객체 직접 저장

**해결**: `normalize_uuid()`로 문자열 변환

### 9.3 타입 불일치 에러

**증상**: `ValueError: Invalid UUID format`

**원인**: UUID 형식이 아닌 문자열을 UUID로 변환 시도

**해결**: `to_uuid()`로 변환 후 검증

### 9.4 트랜잭션 범위 오류

**증상**: 데이터 불일치 (부분 업데이트)

**원인**: 트랜잭션 없이 다중 테이블 업데이트

**해결**: `@with_transaction` 데코레이터 사용

## 10. 참고 문서

- `docs/rules/01_PHILOSOPHY.md`: 핵심 개발 철학
- `docs/rules/UUID_USAGE_GUIDELINES.md`: UUID 사용 가이드라인
- `docs/rules/UUID_HANDLING_GUIDELINES.md`: UUID 처리 가이드라인
- `docs/rules/TRANSACTION_GUIDELINES.md`: 트랜잭션 사용 가이드라인
- `app/common/utils/uuid_helper.py`: UUID 헬퍼 함수
- `app/common/decorators/transaction.py`: 트랜잭션 데코레이터

