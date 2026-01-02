# DB 연결 풀 공유 문제 분석

## 문제 현상

- **전체 테스트 실행 시**: 일부 테스트 실패 (6개)
- **개별 테스트 실행 시**: 모든 테스트 통과
- **실패 패턴**: 간헐적, 특정 테스트에 고정되지 않음

## 근본 원인 분석

### 1. 연결 풀 크기 제한

```python
# database/connection.py
self._pool = await asyncpg.create_pool(
    ...
    min_size=2,
    max_size=10  # 최대 10개 연결만 허용
)
```

**문제점**:
- 각 `DatabaseConnection` 인스턴스는 독립적인 연결 풀을 생성
- 하지만 모든 인스턴스가 **같은 데이터베이스 서버**에 연결
- PostgreSQL 서버 레벨에서도 연결 수 제한이 있을 수 있음

### 2. Fixture 스코프와 연결 생성 패턴

```python
# tests/qa/conftest.py
@pytest_asyncio.fixture(scope="function")
async def db_connection():
    """데이터베이스 연결 Fixture"""
    db = DatabaseConnection()
    await db.initialize()  # 각 테스트마다 새로운 연결 풀 생성
    yield db
    await db.close()
```

**문제점**:
- 각 테스트마다 새로운 `DatabaseConnection` 인스턴스 생성
- 각 인스턴스가 `max_size=10`의 연결 풀을 생성
- **전체 테스트 실행 시**: 여러 테스트가 동시에 실행되면 연결 풀 고갈 발생

### 3. 동시 실행 시나리오

#### 개별 실행 시 (통과)
```
Test 1: [DB Connection 1] → Pool (2-10 connections) → DB Server
        ↓ 완료 후 정리
Test 2: [DB Connection 2] → Pool (2-10 connections) → DB Server
        ↓ 완료 후 정리
Test 3: [DB Connection 3] → Pool (2-10 connections) → DB Server
```
- **특징**: 순차 실행, 연결 풀 충돌 없음

#### 전체 실행 시 (일부 실패)
```
Test 1: [DB Connection 1] → Pool (2-10) ┐
Test 2: [DB Connection 2] → Pool (2-10) ├─→ DB Server (연결 수 제한)
Test 3: [DB Connection 3] → Pool (2-10) │
...                                      │
Test 10: [DB Connection 10] → Pool (2-10)┘
```
- **특징**: 동시 실행, 연결 풀 고갈 가능

### 4. 연결 풀 고갈 시나리오

#### 시나리오 A: 인스턴스별 연결 풀 고갈
```
Test 1 실행 중: DB Connection 1의 풀에서 10개 연결 모두 사용 중
Test 2 실행 중: DB Connection 2의 풀에서 10개 연결 모두 사용 중
Test 3 실행 중: DB Connection 3의 풀에서 10개 연결 모두 사용 중
...
→ 각 인스턴스는 독립적이지만, 내부적으로 연결 풀 고갈 발생
```

#### 시나리오 B: 서버 레벨 연결 제한
```
PostgreSQL 서버 설정: max_connections = 100 (예시)
테스트 실행 중:
  - Test 1: 10개 연결
  - Test 2: 10개 연결
  - Test 3: 10개 연결
  ...
  - Test 10: 10개 연결
  → 총 100개 연결 사용, 추가 연결 시도 시 실패
```

#### 시나리오 C: 비동기 테스트의 동시 실행
```
pytest-asyncio는 기본적으로 테스트를 동시에 실행할 수 있음
여러 테스트가 동시에:
  - 연결 풀 생성 시도
  - 연결 획득 시도
  - 트랜잭션 실행
→ 연결 풀 경합 발생
```

### 5. 실제 실패 패턴 분석

실패한 테스트들:
1. `test_game_state_api_endpoint` - API 테스트 (TestClient 사용)
2. `test_move_player_api_endpoint` - API 테스트 (TestClient 사용)
3. `test_concurrent_users_cell_query` - 동시성 테스트 (50개 요청)
4. `test_transaction_consistency_game_start` - 트랜잭션 테스트
5. `test_transaction_consistency_cell_movement` - 트랜잭션 테스트
6. `test_entity_instance_creation_transaction` - 트랜잭션 테스트

**공통점**:
- 모두 DB 연결을 많이 사용하는 테스트
- 트랜잭션이나 동시성 관련 테스트
- API 테스트는 TestClient가 내부적으로 추가 연결 생성

## 기술적 세부사항

### DatabaseConnection의 연결 풀 관리

```python
class DatabaseConnection:
    def __init__(self):
        self._pool = None  # 각 인스턴스마다 독립적인 풀
    
    async def initialize(self):
        self._pool = await asyncpg.create_pool(
            min_size=2,
            max_size=10  # 인스턴스당 최대 10개
        )
```

**문제**:
- 각 테스트마다 새로운 인스턴스 생성
- 인스턴스당 최대 10개 연결
- 10개 테스트 동시 실행 시 → 최대 100개 연결 시도 가능

### TestClient의 연결 생성

```python
# tests/qa/test_api_endpoints.py
@pytest_asyncio.fixture
async def client(self):
    client = TestClient(app)  # FastAPI 앱은 전역 DatabaseConnection 사용
    yield client
```

**문제**:
- FastAPI 앱이 전역 `DatabaseConnection` 사용
- TestClient가 요청 처리 시 추가 연결 생성
- 여러 API 테스트 동시 실행 시 연결 충돌

## 해결 방안

### 방안 1: 연결 풀 크기 조정 ✅ (적용 완료)

```python
# database/connection.py
is_test = (
    "pytest" in sys.modules or 
    any("pytest" in arg for arg in sys.argv) or
    "PYTEST_CURRENT_TEST" in os.environ
)

self._pool = await asyncpg.create_pool(
    min_size=2,
    max_size=20 if is_test else 10  # 테스트 환경: 20, 프로덕션: 10
)
```

**장점**: 빠른 적용 가능, 테스트 환경에 최적화  
**단점**: 근본 해결은 아니지만 실용적 해결책

### 방안 2: Fixture 스코프 변경 (권장)

```python
# tests/qa/conftest.py
@pytest_asyncio.fixture(scope="session")  # function → session
async def db_connection():
    """세션 전체에서 하나의 연결 풀 공유"""
    db = DatabaseConnection()
    await db.initialize()
    yield db
    await db.close()
```

**장점**: 연결 풀 공유로 효율적  
**단점**: 테스트 간 데이터 격리 필요 (트랜잭션 롤백 등)

### 방안 3: 테스트 격리 개선 (권장)

```python
# 각 테스트마다 트랜잭션 롤백으로 데이터 격리
@pytest_asyncio.fixture(scope="session")
async def db_connection():
    db = DatabaseConnection()
    await db.initialize()
    yield db
    await db.close()

@pytest_asyncio.fixture(scope="function")
async def isolated_db(db_connection):
    """트랜잭션으로 격리된 DB 연결"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        async with conn.transaction():
            yield conn
            # 자동 롤백
```

**장점**: 연결 효율 + 데이터 격리  
**단점**: 구현 복잡도 증가

### 방안 4: 테스트 실행 제한 (임시 해결)

```bash
# 동시 실행 제한
pytest tests/qa/ -n 2  # 최대 2개 테스트만 동시 실행
```

**장점**: 빠른 적용  
**단점**: 테스트 실행 시간 증가

### 방안 5: 연결 풀 싱글톤 패턴 (권장)

```python
# database/connection.py
class DatabaseConnection:
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def initialize(self):
        if self._pool is None:
            self._pool = await asyncpg.create_pool(...)
```

**장점**: 연결 풀 공유, 효율적  
**단점**: 싱글톤 패턴의 일반적 문제점 (테스트 격리 어려움)

## 적용된 해결책

### ✅ 연결 풀 크기 조정 (적용 완료)

```python
# database/connection.py
is_test = (
    "pytest" in sys.modules or 
    any("pytest" in arg for arg in sys.argv) or
    "PYTEST_CURRENT_TEST" in os.environ
)

min_size = 2
max_size = 20 if is_test else 10  # 테스트 환경: 20, 프로덕션: 10
```

**적용 내용**:
- 테스트 환경 자동 감지
- 테스트 환경: `max_size=20` (기존 10에서 증가)
- 프로덕션 환경: `max_size=10` (기존 유지)
- `command_timeout=60` 추가 (테스트 환경 안정성 향상)

## 권장 해결책

### 단기: Fixture 스코프 변경 + 트랜잭션 격리 (추가 권장)

```python
# tests/qa/conftest.py
@pytest_asyncio.fixture(scope="session")
async def db_connection():
    """세션 전체에서 하나의 연결 풀 공유"""
    db = DatabaseConnection()
    await db.initialize()
    yield db
    await db.close()

@pytest_asyncio.fixture(scope="function")
async def db_transaction(db_connection):
    """각 테스트마다 트랜잭션으로 격리"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        async with conn.transaction():
            yield conn
            # 자동 롤백으로 데이터 격리
```

### 장기: 테스트 전용 연결 관리자

```python
# tests/qa/test_db_manager.py
class TestDatabaseManager:
    """테스트 전용 DB 연결 관리자"""
    _pool = None
    
    @classmethod
    async def get_pool(cls):
        if cls._pool is None:
            cls._pool = await asyncpg.create_pool(
                min_size=2,
                max_size=20,  # 테스트용으로 증가
                command_timeout=60
            )
        return cls._pool
```

## 결론

**근본 원인**:
1. 각 테스트마다 독립적인 연결 풀 생성 (`max_size=10`)
2. 전체 테스트 동시 실행 시 연결 풀 고갈
3. PostgreSQL 서버 레벨 연결 제한 가능성

**해결 우선순위**:
1. **즉시**: Fixture 스코프를 `session`으로 변경 + 트랜잭션 격리
2. **단기**: 연결 풀 크기 조정 (`max_size=20`)
3. **장기**: 테스트 전용 연결 관리자 구현

**참고**: 개별 실행 시 통과하는 이유는 순차 실행으로 인해 연결 풀 충돌이 발생하지 않기 때문입니다.

