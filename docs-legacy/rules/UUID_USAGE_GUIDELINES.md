# UUID 사용 가이드라인

## 원칙

### 1. 타입 구분

- **UUID 객체**: Python `uuid.UUID` 타입
  - 내부 로직에서 사용
  - 타입 안정성 보장
  - 비교 및 연산에 유리

- **UUID 문자열**: `str` 타입 (예: `"550e8400-e29b-41d4-a716-446655440000"`)
  - API 경계에서만 사용 (JSON 직렬화)
  - 데이터베이스 저장 시 asyncpg가 자동 변환

### 2. 데이터베이스

- **스키마**: PostgreSQL `UUID` 타입
- **변환**: asyncpg가 UUID 객체 ↔ UUID 타입 자동 변환

### 3. 코드 레벨 원칙

#### ✅ 올바른 사용

```python
# 1. UUID 생성: 객체로 생성
from uuid import UUID
import uuid

runtime_cell_id: UUID = uuid.uuid4()  # ✅ UUID 객체

# 2. 내부 로직: UUID 객체 사용
async def get_cell(self, cell_id: UUID) -> CellResult:
    # ✅ UUID 객체로 처리
    pass

# 3. 데이터베이스 저장: asyncpg가 자동 변환
await conn.execute(
    "INSERT INTO runtime_data.runtime_cells (runtime_cell_id) VALUES ($1)",
    runtime_cell_id  # ✅ UUID 객체 전달
)

# 4. API 경계: 문자열로 변환
@router.post("/cells")
async def create_cell(cell_id: str):  # ✅ API는 문자열
    # 내부 로직으로 전달 시 UUID 객체로 변환
    uuid_obj = UUID(cell_id)
    result = await cell_manager.get_cell(uuid_obj)
    return {"cell_id": str(result.cell.cell_id)}  # ✅ 응답은 문자열
```

#### ❌ 잘못된 사용

```python
# 1. 생성 시 문자열로 변환
runtime_cell_id = str(uuid.uuid4())  # ❌ 불필요한 변환

# 2. Union 타입으로 혼용
def get_cell(self, cell_id: Union[str, UUID]):  # ❌ 타입 불명확
    pass

# 3. 문자열로 저장
await conn.execute(
    "INSERT INTO runtime_cells (runtime_cell_id) VALUES ($1)",
    str(runtime_cell_id)  # ❌ 불필요한 변환
)
```

## 마이그레이션 완료 상태

### ✅ Phase 1: UUID 생성 통일 (완료)

1. ✅ `str(uuid.uuid4())` → `uuid.uuid4()` 변경
2. ✅ 내부 로직은 UUID 객체로 통일
3. ✅ 데이터베이스에서 가져온 UUID도 객체로 유지

### ✅ Phase 2: 테스트 및 검증 (완료)

1. ✅ 런타임 테스트 통과 확인
2. ✅ CellManager SSOT 테스트 통과

### 🔄 Phase 3: 타입 힌트 정리 (진행 중)

1. `Union[str, UUID]` → `UUID` 변경 (선택적, API 호환성 유지)
2. API 경계에서만 문자열 ↔ UUID 변환 (현재 유지)

## 예외 사항

### API 경계

- **FastAPI 엔드포인트**: `str` 타입 허용 (JSON 직렬화)
- **변환 로직**: 엔드포인트 내부에서 `UUID(cell_id)` 변환

### 데이터베이스 쿼리 결과

- **asyncpg fetch**: UUID 타입 컬럼은 UUID 객체로 반환
- **문자열 필요 시**: `str(uuid_obj)` 명시적 변환

## 참고

- PostgreSQL UUID 타입: https://www.postgresql.org/docs/current/datatype-uuid.html
- Python uuid 모듈: https://docs.python.org/3/library/uuid.html
- asyncpg 타입 변환: https://magicstack.github.io/asyncpg/current/usage.html#type-conversion

