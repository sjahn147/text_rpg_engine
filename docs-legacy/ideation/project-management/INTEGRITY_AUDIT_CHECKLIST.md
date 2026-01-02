# Integrity 감사 체크리스트

**작성일**: 2026-01-01  
**목적**: Audit 단계에서 검증해야 할 핵심 규칙 준수 여부 체크리스트  
**관련 문서**: 
- `PROJECT_MANAGEMENT_WORKFLOW.md`
- `docs/rules/코딩 컨벤션 및 품질 가이드.md`
- `docs/rules/UUID_HANDLING_GUIDELINES.md`
- `docs/rules/TRANSACTION_GUIDELINES.md`
- `docs/rules/MIGRATION_GUIDELINES.md`

---

## 📋 목차

1. [3계층 아키텍처 준수](#3계층-아키텍처-준수)
2. [UUID 규칙 준수](#uuid-규칙-준수)
3. [데이터 중심 개발 준수](#데이터-중심-개발-준수)
4. [타입 안전성 준수](#타입-안전성-준수)
5. [비동기 우선 개발 준수](#비동기-우선-개발-준수)
6. [트랜잭션 규칙 준수](#트랜잭션-규칙-준수)
7. [마이그레이션 규칙 준수](#마이그레이션-규칙-준수)

---

## 3계층 아키텍처 준수

### 체크리스트

- [ ] **의존성 방향 준수**
  - ✅ UI Layer는 Business Logic에만 의존
  - ✅ Business Logic은 Data Layer에 의존 (인터페이스 통해서)
  - ❌ UI Layer에서 Data Layer 직접 접근 금지
  - ❌ Business Logic에서 UI Layer 의존 금지

- [ ] **인터페이스 의존**
  - ✅ 구체 클래스가 아닌 인터페이스에 의존
  - ✅ 의존성 주입 사용 (생성자 주입)
  - ❌ 하드코딩된 의존성 금지

- [ ] **전역 상태 금지**
  - ✅ 전역 변수 사용 금지
  - ✅ 싱글톤 패턴으로 상태 공유 금지
  - ✅ 상태는 의존성 주입으로 전달

### 검증 방법

**정적 분석**:
```python
# UI Layer에서 Data Layer 직접 접근 탐지
# 예: app/ui/frontend/에서 app/database/ 직접 import 탐지
# 예: app/services/에서 app/ui/ import 탐지
```

**수동 검토**:
- 의존성 그래프 확인
- import 문 검토
- 전역 변수 사용 여부 확인

### 위반 예시

```python
# ❌ 위반: UI Layer에서 Data Layer 직접 접근
# app/ui/frontend/src/components/GameView.tsx
import { getDbConnection } from '../../database/connection'  # 금지!

# ✅ 올바른 방법
# app/ui/frontend/src/components/GameView.tsx
import { gameService } from '../../services/game_service'  # Business Logic 통해서만
```

---

## UUID 규칙 준수

### 체크리스트

- [ ] **UUID 컬럼 사용**
  - ✅ PostgreSQL UUID 컬럼에는 `uuid.UUID` 객체 사용
  - ✅ `asyncpg`가 자동으로 변환 (UUID 객체 → PostgreSQL UUID)
  - ❌ 문자열을 UUID 컬럼에 직접 저장 금지

- [ ] **JSONB 필드 사용**
  - ✅ JSONB 필드에는 UUID를 문자열로 저장 (`str(uuid_obj)`)
  - ✅ JSON 직렬화 시 UUID 객체를 문자열로 변환
  - ❌ JSONB에 UUID 객체 직접 저장 금지

- [ ] **헬퍼 함수 사용**
  - ✅ `uuid_helper.normalize_uuid()`: UUID → 문자열
  - ✅ `uuid_helper.to_uuid()`: 문자열 → UUID 객체
  - ✅ `uuid_helper.compare_uuids()`: 타입에 상관없이 비교

- [ ] **타입 혼용 방지**
  - ✅ 함수 시그니처에서 UUID 타입 명시
  - ✅ `Union[str, UUID]` 사용 시 헬퍼 함수로 정규화
  - ❌ 타입 혼용으로 인한 비교 실패 방지

### 검증 방법

**정적 분석**:
```python
# UUID 사용 패턴 검증
# - UUID 컬럼에 문자열 직접 저장 탐지
# - JSONB에 UUID 객체 직접 저장 탐지
# - uuid_helper 사용 여부 확인
```

**수동 검토**:
- UUID 관련 코드 검토
- 타입 힌트 확인
- 헬퍼 함수 사용 여부 확인

### 위반 예시

```python
# ❌ 위반: JSONB에 UUID 객체 직접 저장
current_position = {
    'x': 5.0,
    'y': 4.0,
    'runtime_cell_id': runtime_cell_id  # UUID 객체 (금지!)
}

# ✅ 올바른 방법
from app.common.utils.uuid_helper import normalize_uuid
current_position = {
    'x': 5.0,
    'y': 4.0,
    'runtime_cell_id': normalize_uuid(runtime_cell_id)  # 문자열로 변환
}
```

---

## 데이터 중심 개발 준수

### 체크리스트

- [ ] **DB 스키마 우선**
  - ✅ 데이터베이스 스키마를 먼저 설계
  - ✅ 코드는 스키마를 반영
  - ❌ 코드에서 데이터 구조 임의 정의 후 DB에 맞추기 금지

- [ ] **데이터 무결성**
  - ✅ SSOT (Single Source of Truth) 준수
  - ✅ 트랜잭션으로 데이터 무결성 보장
  - ❌ 데이터 중복 저장 금지

- [ ] **비즈니스 로직**
  - ✅ 비즈니스 로직을 데이터베이스 트랜잭션으로 표현
  - ✅ 데이터 구조 위에서 비즈니스 로직 정의
  - ❌ 데이터베이스 없이 코드만으로 비즈니스 로직 구현 금지

### 검증 방법

**수동 검토**:
- 스키마 변경 시 코드 변경 여부 확인
- 데이터 중복 여부 확인
- 트랜잭션 사용 여부 확인

---

## 타입 안전성 준수

### 체크리스트

- [ ] **타입 힌트 100% 적용**
  - ✅ 모든 함수에 타입 힌트 추가
  - ✅ 모든 클래스에 타입 힌트 추가
  - ✅ 공개 API 100% 타입 힌트
  - ❌ 타입 힌트 없이 코드 작성 금지

- [ ] **Any 타입 금지**
  - ✅ `Any` 타입 사용 금지
  - ✅ `typing.Any` 사용 금지
  - ✅ 구체적인 타입 명시

- [ ] **Pydantic 모델**
  - ✅ 런타임 검증을 위한 Pydantic 모델 사용
  - ✅ 입력 데이터 검증
  - ✅ 출력 데이터 검증

### 검증 방법

**정적 분석**:
```bash
# mypy로 타입 체크
mypy app/ --strict

# 타입 힌트 누락 탐지
# Any 타입 사용 탐지
```

**수동 검토**:
- 타입 힌트 누락 확인
- `Any` 타입 사용 여부 확인
- Pydantic 모델 사용 여부 확인

### 위반 예시

```python
# ❌ 위반: 타입 힌트 없음
def get_user_data(user_id):
    return db.query(User).filter(User.id == user_id).first()

# ✅ 올바른 방법
from typing import Optional
from app.models.user import User

def get_user_data(user_id: str) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()
```

---

## 비동기 우선 개발 준수

### 체크리스트

- [ ] **모든 I/O 작업 비동기**
  - ✅ 데이터베이스 쿼리: `async/await`
  - ✅ 파일 I/O: `async/await`
  - ✅ 네트워크 요청: `async/await`
  - ❌ 동기 I/O 금지

- [ ] **동기 함수에서 비동기 함수 호출 금지**
  - ✅ 비동기 함수는 비동기 컨텍스트에서만 호출
  - ❌ 동기 함수에서 `await` 사용 금지
  - ❌ `asyncio.run()` 남용 금지

- [ ] **동시성 문제 해결**
  - ✅ 락/세마포어로 동시성 문제 해결
  - ✅ 전역 락으로 성능 저하 방지
  - ❌ 전역 락 남용 금지

### 검증 방법

**정적 분석**:
```python
# 동기 I/O 사용 탐지
# - psycopg2 사용 탐지 (asyncpg 사용해야 함)
# - open() 사용 탐지 (aiofiles 사용해야 함)
# - requests 사용 탐지 (aiohttp 사용해야 함)
```

**수동 검토**:
- I/O 작업 비동기 여부 확인
- 동기 함수에서 비동기 함수 호출 여부 확인
- 동시성 문제 해결 방법 확인

### 위반 예시

```python
# ❌ 위반: 동기 I/O
import psycopg2

def get_user_data(user_id: str):
    conn = psycopg2.connect("...")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    return cursor.fetchone()

# ✅ 올바른 방법
import asyncpg

async def get_user_data(user_id: str) -> Optional[User]:
    async with get_db_connection() as conn:
        query = "SELECT * FROM users WHERE id = $1"
        result = await conn.fetchrow(query, user_id)
        return User.from_dict(result) if result else None
```

---

## 트랜잭션 규칙 준수

### 체크리스트

- [ ] **적절한 트랜잭션 범위**
  - ✅ 비즈니스 로직 단위로 트랜잭션 설정
  - ✅ 트랜잭션 범위 최소화
  - ❌ 불필요한 트랜잭션 확장 금지

- [ ] **트랜잭션 격리 수준**
  - ✅ 적절한 격리 수준 설정
  - ✅ 동시성 문제 고려
  - ❌ 불필요한 높은 격리 수준 사용 금지

- [ ] **롤백 처리**
  - ✅ 예외 발생 시 롤백 처리
  - ✅ 명시적 롤백 로직
  - ❌ 예외 무시 금지

### 검증 방법

**수동 검토**:
- 트랜잭션 범위 확인
- 롤백 처리 확인
- 격리 수준 확인

### 위반 예시

```python
# ❌ 위반: 롤백 처리 없음
async def update_user(user_id: str, data: dict):
    async with get_db_connection() as conn:
        await conn.execute("UPDATE users SET ...", ...)
        # 예외 발생 시 롤백 없음

# ✅ 올바른 방법
async def update_user(user_id: str, data: dict):
    async with get_db_connection() as conn:
        async with conn.transaction():
            try:
                await conn.execute("UPDATE users SET ...", ...)
            except Exception:
                # 자동 롤백 (transaction 컨텍스트 매니저)
                raise
```

---

## 마이그레이션 규칙 준수

### 체크리스트

- [ ] **안전한 마이그레이션 스크립트**
  - ✅ 롤백 가능한 마이그레이션
  - ✅ 데이터 손실 방지
  - ❌ 데이터 손실 가능한 마이그레이션 금지

- [ ] **백업 생성 및 복구 계획**
  - ✅ 마이그레이션 전 백업 생성
  - ✅ 복구 계획 수립
  - ❌ 백업 없이 마이그레이션 실행 금지

- [ ] **사용자 컨펌 요청**
  - ✅ 위험한 작업 (삭제, 수정, 스키마 변경) 시 컨펌 요청
  - ✅ 명시적 경고
  - ❌ 사용자 컨펌 없이 위험한 작업 실행 금지

### 검증 방법

**수동 검토**:
- 마이그레이션 스크립트 검토
- 백업 생성 여부 확인
- 컨펌 요청 여부 확인

### 위반 예시

```python
# ❌ 위반: 백업 없이 데이터 삭제
async def migrate():
    await conn.execute("DELETE FROM old_table")  # 위험!

# ✅ 올바른 방법
async def migrate():
    # 백업 생성
    await backup_table("old_table")
    
    # 사용자 컨펌 요청
    if not await confirm_dangerous_operation("데이터 삭제"):
        raise CancelledError("사용자가 취소했습니다")
    
    # 마이그레이션 실행
    await conn.execute("DELETE FROM old_table")
```

---

## 자동화된 Integrity 체크

### 도구

**정적 분석 도구**:
- `mypy`: 타입 체크
- `flake8`: 코드 스타일 및 아키텍처 위반 탐지
- `pylint`: 코드 품질 및 아키텍처 위반 탐지
- **커스텀 스크립트**: 프로젝트 특화 규칙 검증

**커스텀 스크립트 예시**:
```python
# tools/integrity_checker.py
async def check_three_layer_architecture():
    """3계층 아키텍처 위반 탐지"""
    # UI Layer에서 Data Layer 직접 접근 탐지
    # Business Logic에서 UI Layer 의존 탐지
    pass

async def check_uuid_compliance():
    """UUID 규칙 준수 여부 확인"""
    # UUID 사용 패턴 검증
    # uuid_helper 사용 여부 확인
    pass
```

### 통합

**CI/CD 파이프라인**:
```yaml
# .github/workflows/integrity_check.yml
- name: Integrity Check
  run: |
    python tools/integrity_checker.py
    mypy app/ --strict
    flake8 app/ --select=E999
```

---

## Audit YAML 제출 형식

```yaml
# docs/project-management/submissions/AUDIT-001.yaml
audit_id: AUDIT-001
qa_id: QA-001
todo_id: TODO-001

integrity_checks:
  three_layer_architecture:
    status: passed|failed
    violations: []
    # 또는
    # violations:
    #   - file: "app/ui/frontend/src/components/GameView.tsx"
    #     line: 123
    #     description: "UI Layer에서 Data Layer 직접 접근"
  
  uuid_compliance:
    status: passed|failed
    violations: []
  
  data_centric_compliance:
    status: passed|failed
    violations: []
  
  type_safety_compliance:
    status: passed|failed
    violations: []
  
  async_first_compliance:
    status: passed|failed
    violations: []
  
  transaction_compliance:
    status: passed|failed
    violations: []
  
  migration_compliance:
    status: passed|failed
    violations: []

summary:
  total_checks: 7
  passed: 7
  failed: 0
  critical_violations: 0

submitted_at: 2026-01-01T12:00:00Z
submitted_by: agent
```

---

## 다음 단계

1. **자동화 도구 개발**: Integrity 체크 자동화 스크립트
2. **CI/CD 통합**: 파이프라인에 Integrity 체크 추가
3. **대시보드 통합**: Streamlit 대시보드에 Integrity 체크 결과 표시

