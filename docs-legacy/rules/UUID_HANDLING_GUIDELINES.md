# UUID 처리 가이드라인

## 개요

이 문서는 RPG 엔진 프로젝트에서 UUID를 처리하는 방법에 대한 DBA와 백엔드 개발자 관점의 가이드라인입니다.

## 현재 상황 분석

### 1. 데이터베이스 스키마 (PostgreSQL)

#### UUID 컬럼 정의
```sql
-- UUID 타입 컬럼 (PostgreSQL 네이티브)
CREATE TABLE runtime_data.runtime_objects (
    runtime_object_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    game_object_id VARCHAR(50) NOT NULL,
    session_id UUID NOT NULL,
    ...
);

CREATE TABLE reference_layer.object_references (
    runtime_object_id UUID PRIMARY KEY,
    game_object_id VARCHAR(50) NOT NULL,
    session_id UUID NOT NULL,
    ...
);
```

#### JSONB 필드 내 UUID 저장
```sql
-- JSONB 필드는 문자열로 저장 (JSON 표준)
CREATE TABLE runtime_data.entity_states (
    current_position JSONB,  -- {"x": 5.0, "y": 4.0, "runtime_cell_id": "uuid-string"}
    ...
);
```

**중요**: JSONB는 UUID 타입을 직접 지원하지 않으므로 **반드시 문자열로 저장**해야 합니다.

### 2. Python 코드에서의 UUID 사용 패턴

#### 현재 발견된 패턴들

**패턴 1: UUID 객체 생성**
```python
import uuid
runtime_object_id = uuid.uuid4()  # UUID 객체 반환
```

**패턴 2: DB 쿼리에 UUID 객체 직접 전달**
```python
# asyncpg가 자동으로 UUID 객체를 PostgreSQL UUID 타입으로 변환
await conn.execute("""
    INSERT INTO runtime_data.runtime_objects 
    (runtime_object_id, game_object_id, session_id)
    VALUES ($1, $2, $3)
""", runtime_object_id, game_object_id, session_id)  # UUID 객체 직접 전달
```

**패턴 3: JSONB에 저장 시 문자열 변환**
```python
import json
current_position = {
    'x': 5.0,
    'y': 4.0,
    'runtime_cell_id': str(runtime_cell_id)  # UUID 객체를 문자열로 변환
}
await conn.execute("""
    INSERT INTO runtime_data.object_states 
    (runtime_object_id, current_position)
    VALUES ($1, $2)
""", runtime_object_id, json.dumps(current_position))
```

**패턴 4: 타입 혼용 (문제 발생 가능)**
```python
# 문제: 문자열과 UUID 객체 혼용
target_id: Union[str, UUID]  # 타입 힌트에 혼용 표시

# 비교 시 문제 발생 가능
if obj.get('runtime_object_id') == object_id:  # UUID 객체 vs 문자열 비교 실패
```

## 문제점 분석

### 1. 타입 불일치 문제

**문제 상황:**
- DB에서 조회한 UUID는 `asyncpg.pgproto.pgproto.UUID` 객체로 반환됨
- JSONB에서 조회한 UUID는 문자열로 반환됨
- 코드에서 생성한 UUID는 `uuid.UUID` 객체

**발생 가능한 오류:**
```python
# TypeError: expected string or bytes-like object, got 'asyncpg.pgproto.pgproto.UUID'
import re
re.match(r'^[0-9a-f]{8}-...', target_id)  # UUID 객체는 정규식 매칭 불가
```

### 2. 비교 연산 문제

```python
# 문제: UUID 객체와 문자열 비교 실패
uuid_obj = uuid.uuid4()
uuid_str = str(uuid_obj)
uuid_obj == uuid_str  # False (타입이 다름)
```

### 3. JSONB 저장 시 타입 불일치

```python
# 문제: UUID 객체를 JSONB에 직접 저장 시도
position = {'runtime_cell_id': uuid.uuid4()}  # UUID 객체
json.dumps(position)  # TypeError: Object of type UUID is not JSON serializable
```

## 권장사항

### DBA 관점

#### 1. 데이터베이스 스키마 설계 원칙

**✅ 권장:**
- UUID 컬럼은 PostgreSQL `UUID` 타입 사용
- JSONB 필드 내 UUID는 문자열로 저장 (JSON 표준 준수)
- 인덱스는 UUID 컬럼에 직접 생성 (성능 최적화)

**❌ 비권장:**
- UUID를 `VARCHAR(36)`로 저장 (타입 안정성 및 성능 저하)
- JSONB 내부에 UUID 객체 저장 시도 (JSON 표준 위반)

#### 2. 성능 고려사항

```sql
-- ✅ 좋은 예: UUID 컬럼에 직접 인덱스
CREATE INDEX idx_runtime_objects_session 
ON runtime_data.runtime_objects(session_id);

-- ❌ 나쁜 예: JSONB 내 UUID 문자열에 인덱스 (비효율적)
CREATE INDEX idx_entity_states_cell 
ON runtime_data.entity_states USING GIN ((current_position -> 'runtime_cell_id'));
```

**권장**: JSONB 내 UUID는 조회용이므로 인덱스 불필요. 실제 조회는 UUID 컬럼을 사용.

### 백엔드 개발자 관점

#### 1. UUID 생성 및 저장 원칙

**✅ 권장 패턴:**

```python
import uuid
from typing import Union

# 1. UUID 생성: UUID 객체로 생성
runtime_object_id = uuid.uuid4()  # UUID 객체

# 2. DB 쿼리: UUID 객체 직접 전달 (asyncpg 자동 변환)
await conn.execute("""
    INSERT INTO runtime_data.runtime_objects 
    (runtime_object_id, game_object_id, session_id)
    VALUES ($1, $2, $3)
""", runtime_object_id, game_object_id, session_id)

# 3. JSONB 저장: 문자열로 변환
current_position = {
    'x': 5.0,
    'y': 4.0,
    'runtime_cell_id': str(runtime_cell_id)  # 문자열 변환 필수
}
await conn.execute("""
    INSERT INTO runtime_data.object_states 
    (runtime_object_id, current_position)
    VALUES ($1, $2)
""", runtime_object_id, json.dumps(current_position))
```

#### 2. UUID 비교 및 변환 헬퍼 함수

**권장: UUID 처리 헬퍼 함수 생성**

```python
# common/utils/uuid_helper.py
from typing import Union
from uuid import UUID
import uuid

def normalize_uuid(value: Union[str, UUID, None]) -> Optional[str]:
    """
    UUID를 문자열로 정규화
    
    Args:
        value: UUID 객체, UUID 문자열, 또는 None
        
    Returns:
        UUID 문자열 또는 None
    """
    if value is None:
        return None
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, str):
        # UUID 형식 검증
        try:
            uuid.UUID(value)
            return value
        except (ValueError, AttributeError):
            return None
    return None

def to_uuid(value: Union[str, UUID, None]) -> Optional[UUID]:
    """
    값을 UUID 객체로 변환
    
    Args:
        value: UUID 문자열, UUID 객체, 또는 None
        
    Returns:
        UUID 객체 또는 None
    """
    if value is None:
        return None
    if isinstance(value, UUID):
        return value
    if isinstance(value, str):
        try:
            return UUID(value)
        except (ValueError, AttributeError):
            return None
    return None

def compare_uuids(uuid1: Union[str, UUID], uuid2: Union[str, UUID]) -> bool:
    """
    두 UUID를 비교 (타입 무관)
    
    Args:
        uuid1: 첫 번째 UUID (문자열 또는 UUID 객체)
        uuid2: 두 번째 UUID (문자열 또는 UUID 객체)
        
    Returns:
        두 UUID가 같으면 True
    """
    uuid1_str = normalize_uuid(uuid1)
    uuid2_str = normalize_uuid(uuid2)
    if uuid1_str is None or uuid2_str is None:
        return False
    return uuid1_str == uuid2_str
```

#### 3. 타입 힌트 및 검증

**✅ 권장: 명확한 타입 힌트**

```python
from typing import Union, Optional
from uuid import UUID

# 내부 처리: UUID 객체 사용
def create_object(runtime_object_id: UUID, session_id: UUID) -> None:
    """UUID 객체를 받아서 처리"""
    pass

# API 경계: 문자열 사용
def api_create_object(object_id: str, session_id: str) -> dict:
    """API에서 문자열로 받아서 내부적으로 UUID로 변환"""
    runtime_object_id = UUID(object_id)
    session_uuid = UUID(session_id)
    # ...
    return {'object_id': str(runtime_object_id)}  # 응답은 문자열
```

#### 4. JSONB 필드 처리 원칙

**✅ 권장: JSONB는 항상 문자열로 저장**

```python
# ✅ 좋은 예
def save_position(runtime_cell_id: UUID, position: dict) -> None:
    current_position = {
        **position,
        'runtime_cell_id': str(runtime_cell_id)  # 문자열 변환
    }
    await conn.execute("""
        UPDATE runtime_data.entity_states
        SET current_position = $1
        WHERE runtime_entity_id = $2
    """, json.dumps(current_position), entity_id)

# ❌ 나쁜 예
def save_position_bad(runtime_cell_id: UUID, position: dict) -> None:
    current_position = {
        **position,
        'runtime_cell_id': runtime_cell_id  # UUID 객체 - JSON 직렬화 실패
    }
    await conn.execute("""
        UPDATE runtime_data.entity_states
        SET current_position = $1
        WHERE runtime_entity_id = $2
    """, json.dumps(current_position), entity_id)  # TypeError 발생
```

#### 5. DB 쿼리에서 UUID 조회 시 처리

**✅ 권장: asyncpg 반환값 처리**

```python
# asyncpg는 UUID 컬럼을 UUID 객체로 반환
row = await conn.fetchrow("""
    SELECT runtime_object_id, game_object_id
    FROM reference_layer.object_references
    WHERE session_id = $1
""", session_id)

# UUID 객체를 문자열로 변환 (API 응답용)
object_id = str(row['runtime_object_id'])

# 또는 비교용으로 UUID 객체 유지
runtime_object_id = row['runtime_object_id']  # UUID 객체
if runtime_object_id == some_uuid:  # UUID 객체끼리 비교 가능
    pass
```

## 구체적인 수정 권장사항

### 1. UUID 헬퍼 함수 도입

**파일 생성**: `app/common/utils/uuid_helper.py`

```python
"""UUID 처리 헬퍼 함수"""
from typing import Union, Optional
from uuid import UUID
import uuid

def normalize_uuid(value: Union[str, UUID, None]) -> Optional[str]:
    """UUID를 문자열로 정규화"""
    # ... (위의 구현 참조)

def to_uuid(value: Union[str, UUID, None]) -> Optional[UUID]:
    """값을 UUID 객체로 변환"""
    # ... (위의 구현 참조)

def compare_uuids(uuid1: Union[str, UUID], uuid2: Union[str, UUID]) -> bool:
    """두 UUID를 비교"""
    # ... (위의 구현 참조)
```

### 2. 기존 코드 수정 패턴

**수정 전:**
```python
# app/handlers/object_interaction_base.py
async def _parse_object_id(self, target_id: Union[str, UUID], session_id: str):
    is_uuid = bool(re.match(r'^[0-9a-f]{8}-...', target_id))  # UUID 객체면 실패
    # ...
```

**수정 후:**
```python
# app/handlers/object_interaction_base.py
from app.common.utils.uuid_helper import normalize_uuid, to_uuid

async def _parse_object_id(self, target_id: Union[str, UUID], session_id: str):
    target_id_str = normalize_uuid(target_id)  # 항상 문자열로 정규화
    is_uuid = bool(target_id_str and len(target_id_str) == 36)
    # ...
```

### 3. JSONB 저장 시 일관성 확보

**수정 전:**
```python
# app/managers/cell_manager.py
current_position = {
    'runtime_cell_id': cell_id  # UUID 객체일 수 있음
}
```

**수정 후:**
```python
# app/managers/cell_manager.py
from app.common.utils.uuid_helper import normalize_uuid

current_position = {
    'runtime_cell_id': normalize_uuid(cell_id)  # 항상 문자열
}
```

## 체크리스트

### 개발자 체크리스트

- [ ] UUID 생성 시 `uuid.uuid4()` 사용 (UUID 객체)
- [ ] DB 쿼리 전달 시 UUID 객체 직접 전달 (asyncpg 자동 변환)
- [ ] JSONB 저장 시 `str(uuid)`로 문자열 변환
- [ ] UUID 비교 시 `normalize_uuid()` 또는 `compare_uuids()` 사용
- [ ] API 경계에서는 문자열로 변환하여 전달
- [ ] 타입 힌트에 `Union[str, UUID]` 명시 (혼용 가능한 경우)

### DBA 체크리스트

- [ ] UUID 컬럼은 PostgreSQL `UUID` 타입 사용
- [ ] JSONB 필드 내 UUID는 문자열로 저장 확인
- [ ] UUID 컬럼에 인덱스 생성 (성능 최적화)
- [ ] JSONB 내 UUID는 인덱스 불필요 (조회용)

## 결론

### 핵심 원칙

1. **DB UUID 컬럼**: UUID 객체 직접 사용 (asyncpg 자동 변환)
2. **JSONB 필드**: 문자열로 저장 (JSON 표준)
3. **API 경계**: 문자열로 통일 (프론트엔드 호환성)
4. **내부 처리**: UUID 헬퍼 함수로 일관성 확보

### 장점

- **타입 안정성**: Python에서 UUID 타입 검증 가능
- **성능**: PostgreSQL UUID 타입 사용으로 인덱스 효율성
- **호환성**: JSONB와 API 경계에서 문자열 사용으로 호환성 확보
- **유지보수성**: 헬퍼 함수로 일관된 처리 패턴

### 주의사항

- UUID 객체와 문자열 혼용 시 비교 오류 주의
- JSONB 저장 시 반드시 문자열 변환
- 정규식 매칭 전 UUID 객체를 문자열로 변환

