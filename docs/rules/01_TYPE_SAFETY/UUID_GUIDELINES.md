# UUID 가이드라인

> **최신화 날짜**: 2026-01-03  
> **적용 범위**: UUID 사용 시 필수 읽기

## ⚠️ 중요: uuid_helper.py 사용 필수

**모든 UUID 변환, 비교, 검증은 반드시 `app/common/utils/uuid_helper.py`의 헬퍼 함수를 사용해야 합니다.**

### 필수 사용 함수

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

**⚠️ 경고**: 직접 `str(uuid)` 또는 `UUID(string)` 변환을 사용하지 마세요. 헬퍼 함수를 사용하여 타입 안전성과 일관성을 보장하세요.

## 1. 개요

이 문서는 RPG 엔진에서 UUID를 처리하는 방법에 대한 종합 가이드라인입니다. DBA와 백엔드 개발자 모두를 위한 내용을 포함합니다.

## 2. 핵심 원칙

### 2.1 타입 구분

- **UUID 객체**: Python `uuid.UUID` 타입
  - 내부 로직에서 사용
  - 타입 안정성 보장
  - 비교 및 연산에 유리

- **UUID 문자열**: `str` 타입 (예: `"550e8400-e29b-41d4-a716-446655440000"`)
  - API 경계에서만 사용 (JSON 직렬화)
  - JSONB 필드 저장 시 사용
  - 데이터베이스 저장 시 asyncpg가 자동 변환

### 2.2 데이터베이스

- **스키마**: PostgreSQL `UUID` 타입
- **변환**: asyncpg가 UUID 객체 ↔ UUID 타입 자동 변환
- **JSONB**: JSONB 필드는 문자열로 저장 (JSON 표준)

## 3. uuid_helper.py 사용법

### 3.1 normalize_uuid() - UUID를 문자열로 정규화

**용도**: JSONB 저장, API 응답, 비교 전 정규화

```python
from app.common.utils.uuid_helper import normalize_uuid
import uuid

# UUID 객체 → 문자열
uuid_obj = uuid.uuid4()
uuid_str = normalize_uuid(uuid_obj)  # ✅ '550e8400-e29b-41d4-a716-446655440000'

# 이미 문자열인 경우 검증 후 반환
uuid_str = normalize_uuid('550e8400-e29b-41d4-a716-446655440000')  # ✅ 동일 문자열 반환

# None 처리
result = normalize_uuid(None)  # ✅ None 반환

# 유효하지 않은 값
result = normalize_uuid('invalid')  # ✅ None 반환
```

**사용 예시**:
```python
# JSONB 저장 시
current_position = {
    'x': 5.0,
    'y': 4.0,
    'runtime_cell_id': normalize_uuid(runtime_cell_id)  # ✅ 항상 문자열
}
```

### 3.2 to_uuid() - 문자열을 UUID 객체로 변환

**용도**: API 경계에서 받은 문자열을 내부 로직용 UUID 객체로 변환

```python
from app.common.utils.uuid_helper import to_uuid

# 문자열 → UUID 객체
uuid_str = '550e8400-e29b-41d4-a716-446655440000'
uuid_obj = to_uuid(uuid_str)  # ✅ UUID 객체

# 이미 UUID 객체인 경우
uuid_obj = to_uuid(uuid.uuid4())  # ✅ 동일 객체 반환

# None 처리
result = to_uuid(None)  # ✅ None 반환

# 유효하지 않은 값
result = to_uuid('invalid')  # ✅ None 반환
```

**사용 예시**:
```python
# API 경계에서 받은 문자열을 UUID 객체로 변환
@router.get("/entities/{entity_id}")
async def get_entity(entity_id: str):
    uuid_obj = to_uuid(entity_id)
    if not uuid_obj:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    result = await entity_manager.get_entity(uuid_obj)
    return {"entity_id": normalize_uuid(result.entity.id)}  # 응답은 문자열
```

### 3.3 compare_uuids() - 타입 무관 비교

**용도**: UUID 객체와 문자열을 안전하게 비교

```python
from app.common.utils.uuid_helper import compare_uuids
import uuid

uuid_obj = uuid.uuid4()
uuid_str = str(uuid_obj)

# 타입 무관 비교
if compare_uuids(uuid_obj, uuid_str):  # ✅ True
    print("Same UUID")

# None 처리
if compare_uuids(None, None):  # ✅ False
    pass
```

**사용 예시**:
```python
# JSONB에서 조회한 UUID 문자열과 UUID 객체 비교
position = await conn.fetchrow("SELECT current_position FROM entity_states ...")
cell_id_from_json = position['current_position'].get('runtime_cell_id')  # 문자열

if compare_uuids(cell_id_from_json, current_cell_id):  # ✅ 타입 무관 비교
    # 같은 셀
    pass
```

### 3.4 is_valid_uuid() - 유효성 검증

**용도**: 값이 유효한 UUID인지 확인

```python
from app.common.utils.uuid_helper import is_valid_uuid

if is_valid_uuid('550e8400-e29b-41d4-a716-446655440000'):  # ✅ True
    pass

if is_valid_uuid('invalid'):  # ✅ False
    pass

if is_valid_uuid(None):  # ✅ False
    pass
```

### 3.5 ensure_uuid_string() - UUID 문자열 보장

**용도**: UUID 문자열이 필요할 때 None이면 기본값 반환

```python
from app.common.utils.uuid_helper import ensure_uuid_string
import uuid

# 유효한 값
result = ensure_uuid_string(uuid.uuid4())  # ✅ 문자열 반환

# None + 기본값
result = ensure_uuid_string(None, 'default-uuid')  # ✅ 'default-uuid'

# 유효하지 않은 값 + 기본값
result = ensure_uuid_string('invalid', 'default-uuid')  # ✅ 'default-uuid'

# None + 기본값 없음
result = ensure_uuid_string(None)  # ❌ ValueError 발생
```

### 3.6 ensure_uuid_object() - UUID 객체 보장

**용도**: UUID 객체가 필요할 때 None이면 기본값 반환

```python
from app.common.utils.uuid_helper import ensure_uuid_object
import uuid

# 유효한 값
result = ensure_uuid_object('550e8400-e29b-41d4-a716-446655440000')  # ✅ UUID 객체

# None + 기본값
default_uuid = uuid.uuid4()
result = ensure_uuid_object(None, default_uuid)  # ✅ default_uuid 반환

# 유효하지 않은 값 + 기본값
result = ensure_uuid_object('invalid', default_uuid)  # ✅ default_uuid 반환

# None + 기본값 없음
result = ensure_uuid_object(None)  # ❌ ValueError 발생
```

## 4. 올바른 사용 패턴

### 4.1 UUID 생성 및 저장

```python
import uuid
from app.common.utils.uuid_helper import normalize_uuid, to_uuid

# ✅ 1. UUID 생성: 객체로 생성
runtime_cell_id: UUID = uuid.uuid4()  # UUID 객체

# ✅ 2. 내부 로직: UUID 객체 사용
async def get_cell(self, cell_id: UUID) -> CellResult:
    # UUID 객체로 처리
    pass

# ✅ 3. 데이터베이스 저장: asyncpg가 자동 변환
await conn.execute(
    "INSERT INTO runtime_data.runtime_cells (runtime_cell_id) VALUES ($1)",
    runtime_cell_id  # ✅ UUID 객체 직접 전달
)

# ✅ 4. JSONB 저장: normalize_uuid() 사용
current_position = {
    'x': 5.0,
    'y': 4.0,
    'runtime_cell_id': normalize_uuid(runtime_cell_id)  # ✅ 문자열로 변환
}

# ✅ 5. API 경계: to_uuid() 사용
@router.post("/cells")
async def create_cell(cell_id: str):  # API는 문자열
    uuid_obj = to_uuid(cell_id)  # ✅ UUID 객체로 변환
    if not uuid_obj:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    result = await cell_manager.get_cell(uuid_obj)
    return {"cell_id": normalize_uuid(result.cell.cell_id)}  # ✅ 응답은 문자열
```

### 4.2 잘못된 사용 (금지)

```python
# ❌ 1. 생성 시 문자열로 변환
runtime_cell_id = str(uuid.uuid4())  # ❌ 불필요한 변환

# ❌ 2. 직접 변환 (헬퍼 함수 미사용)
uuid_str = str(uuid_obj)  # ❌ normalize_uuid() 사용해야 함
uuid_obj = UUID(uuid_str)  # ❌ to_uuid() 사용해야 함

# ❌ 3. Union 타입으로 혼용
def get_cell(self, cell_id: Union[str, UUID]):  # ❌ 타입 불명확
    pass

# ❌ 4. JSONB에 UUID 객체 직접 저장
position = {'runtime_cell_id': uuid.uuid4()}  # ❌ JSON 직렬화 실패
json.dumps(position)  # TypeError 발생

# ❌ 5. 타입 추측
if len(cell_id) == 36:  # ❌ UUID라고 추측 (불확정성 불허 원칙 위반)
    uuid_obj = UUID(cell_id)

# ❌ 6. 직접 비교 (타입 불일치 가능)
if uuid_obj == uuid_str:  # ❌ False (타입이 다름)
    pass
```

## 5. 데이터베이스 스키마 (PostgreSQL)

### 5.1 UUID 컬럼 정의

```sql
-- ✅ UUID 타입 컬럼 (PostgreSQL 네이티브)
CREATE TABLE runtime_data.runtime_objects (
    runtime_object_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    game_object_id VARCHAR(50) NOT NULL,
    session_id UUID NOT NULL,
    ...
);
```

### 5.2 JSONB 필드 내 UUID 저장

```sql
-- JSONB 필드는 문자열로 저장 (JSON 표준)
CREATE TABLE runtime_data.entity_states (
    current_position JSONB,  -- {"x": 5.0, "y": 4.0, "runtime_cell_id": "uuid-string"}
    ...
);
```

**중요**: JSONB는 UUID 타입을 직접 지원하지 않으므로 **반드시 문자열로 저장**해야 합니다.

### 5.3 인덱스 설계

```sql
-- ✅ 좋은 예: UUID 컬럼에 직접 인덱스
CREATE INDEX idx_runtime_objects_session 
ON runtime_data.runtime_objects(session_id);

-- ❌ 나쁜 예: JSONB 내 UUID 문자열에 인덱스 (비효율적)
CREATE INDEX idx_entity_states_cell 
ON runtime_data.entity_states USING GIN ((current_position -> 'runtime_cell_id'));
```

**권장**: JSONB 내 UUID는 조회용이므로 인덱스 불필요. 실제 조회는 UUID 컬럼을 사용.

## 6. 자주 발생하는 에러 및 해결

### 6.1 TypeError: Object of type UUID is not JSON serializable

**원인**: JSONB에 UUID 객체를 직접 저장 시도

**해결**:
```python
# ❌ 잘못된 방법
position = {'runtime_cell_id': uuid.uuid4()}
json.dumps(position)  # TypeError

# ✅ 올바른 방법
from app.common.utils.uuid_helper import normalize_uuid
position = {'runtime_cell_id': normalize_uuid(uuid.uuid4())}
json.dumps(position)  # ✅ 성공
```

### 6.2 UUID 객체와 문자열 비교 실패

**원인**: 직접 비교 연산자 사용

**해결**:
```python
# ❌ 잘못된 방법
uuid_obj = uuid.uuid4()
uuid_str = str(uuid_obj)
if uuid_obj == uuid_str:  # False (타입이 다름)
    pass

# ✅ 올바른 방법
from app.common.utils.uuid_helper import compare_uuids
if compare_uuids(uuid_obj, uuid_str):  # ✅ True
    pass
```

### 6.3 정규식 매칭 실패

**원인**: UUID 객체에 정규식 적용

**해결**:
```python
# ❌ 잘못된 방법
import re
re.match(r'^[0-9a-f]{8}-...', uuid_obj)  # TypeError

# ✅ 올바른 방법
from app.common.utils.uuid_helper import normalize_uuid, is_valid_uuid
uuid_str = normalize_uuid(uuid_obj)
if uuid_str and is_valid_uuid(uuid_str):
    # 유효한 UUID
    pass
```

## 7. 체크리스트

### 개발자 체크리스트

- [ ] UUID 생성 시 `uuid.uuid4()` 사용 (UUID 객체)
- [ ] DB 쿼리 전달 시 UUID 객체 직접 전달 (asyncpg 자동 변환)
- [ ] JSONB 저장 시 `normalize_uuid()` 사용 (문자열 변환)
- [ ] UUID 비교 시 `compare_uuids()` 사용 (타입 무관)
- [ ] API 경계에서는 `to_uuid()`로 변환하여 전달
- [ ] 직접 `str(uuid)` 또는 `UUID(string)` 변환 금지
- [ ] 타입 추측 로직 금지 (불확정성 불허 원칙)

### DBA 체크리스트

- [ ] UUID 컬럼은 PostgreSQL `UUID` 타입 사용
- [ ] JSONB 필드 내 UUID는 문자열로 저장 확인
- [ ] UUID 컬럼에 인덱스 생성 (성능 최적화)
- [ ] JSONB 내 UUID는 인덱스 불필요 (조회용)

## 8. 참고 문서

- `00_CORE/01_PHILOSOPHY.md`: 핵심 개발 철학 (불확정성 불허 원칙)
- `01_TYPE_SAFETY/TYPE_SAFETY_GUIDELINES.md`: 타입 안전성 종합 가이드라인
- `app/common/utils/uuid_helper.py`: **UUID 헬퍼 함수 구현 (필수 참조)**
- `02_DATABASE/DATABASE_SCHEMA_DESIGN.md`: 데이터베이스 스키마 설계 가이드라인

## 9. 외부 참고

- PostgreSQL UUID 타입: https://www.postgresql.org/docs/current/datatype-uuid.html
- Python uuid 모듈: https://docs.python.org/3/library/uuid.html
- asyncpg 타입 변환: https://magicstack.github.io/asyncpg/current/usage.html#type-conversion

