# 트랜잭션 사용 가이드라인

## 개요

이 문서는 RPG 게임 엔진에서 트랜잭션을 사용하는 규칙과 모범 사례를 정의합니다.

## 트랜잭션이 필요한 작업

### 1. 상태 전이 작업

다음 작업들은 반드시 트랜잭션 내에서 수행해야 합니다:

- **엔티티 이동** (셀 간 이동)
- **셀 진입/퇴장**
- **세션 생성/종료**
- **인벤토리 아이템 추가/제거**
- **오브젝트 상태 변경** (열기/닫기 등)

**이유**: 중간 실패 시 "반쯤 이동한 엔티티" 같은 불일치 상태를 방지합니다.

### 2. 다중 테이블 업데이트

여러 테이블을 동시에 업데이트하는 작업:

- **엔티티 생성** (`entity_references` + `entity_states`)
- **셀 생성** (`cell_references` + `runtime_cells`)
- **오브젝트 상태 변경** (`object_states` + 관련 테이블)

**이유**: 원자성 보장으로 부분 업데이트를 방지합니다.

### 3. 원자성이 중요한 작업

- **게임 시간 틱 처리**
- **이벤트 트리거 및 결과 적용**
- **대화 진행 및 선택지 기록**

## 트랜잭션 데코레이터 사용

### 기본 사용법

```python
from app.common.decorators.transaction import with_transaction

class MyService:
    def __init__(self, db_connection):
        self.db = db_connection
    
    @with_transaction
    async def update_data(self, data_id: str, conn=None):
        """
        conn 파라미터는 데코레이터가 자동으로 제공합니다.
        트랜잭션 내부에서 실행됩니다.
        """
        await conn.execute("UPDATE ...", data_id)
        return result
```

### 중첩 트랜잭션 처리

이미 트랜잭션 내부에 있는 경우, `conn`을 명시적으로 전달하면 새 트랜잭션을 생성하지 않습니다:

```python
@with_transaction
async def outer_method(self, conn=None):
    # 이미 트랜잭션 내부
    await self.inner_method(conn=conn)  # 같은 트랜잭션 사용

@with_transaction
async def inner_method(self, conn=None):
    # outer_method의 트랜잭션을 재사용
    await conn.execute("...")
```

### 수동 트랜잭션 사용

데코레이터를 사용하지 않고 수동으로 트랜잭션을 관리할 수도 있습니다:

```python
async def manual_transaction(self):
    pool = await self.db.pool
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("...")
            await conn.execute("...")
```

## 현재 트랜잭션 사용 현황

### 이미 트랜잭션 사용 중인 메서드

1. **CellManager.move_entity_between_cells()**
   - 엔티티 이동 시 원자성 보장
   - 출발 셀 제거 → 도착 셀 추가 → 위치 업데이트

2. **GameSession.enter_cell()**
   - 셀 진입 및 이벤트 기록을 트랜잭션으로 처리

3. **InstanceManager.cleanup_session_instances()**
   - 세션 정리 시 여러 테이블 삭제를 트랜잭션으로 안전하게 수행

### 트랜잭션 적용 권장 메서드

다음 메서드들도 트랜잭션 적용을 검토해야 합니다:

- 인벤토리 아이템 추가/제거 메서드
- 오브젝트 상태 변경 메서드
- 게임 시간 틱 처리 메서드

## 주의사항

### 1. 트랜잭션 범위 최소화

트랜잭션은 가능한 한 짧게 유지해야 합니다:

```python
# 좋은 예: 트랜잭션 범위가 최소화됨
@with_transaction
async def update_entity(self, entity_id: str, conn=None):
    await conn.execute("UPDATE ...")
    # 트랜잭션 종료

# 나쁜 예: 불필요하게 긴 트랜잭션
@with_transaction
async def update_entity(self, entity_id: str, conn=None):
    await conn.execute("UPDATE ...")
    await self.expensive_operation()  # 트랜잭션 외부로 이동해야 함
    await conn.execute("UPDATE ...")
```

### 2. 롤백 처리

트랜잭션 내에서 예외가 발생하면 자동으로 롤백됩니다:

```python
@with_transaction
async def update_data(self, data_id: str, conn=None):
    try:
        await conn.execute("UPDATE ...")
        await conn.execute("INSERT ...")
    except Exception as e:
        # 자동 롤백됨
        raise
```

### 3. 읽기 전용 작업

단순 조회 작업은 트랜잭션이 필요 없습니다:

```python
# 트랜잭션 불필요
async def get_entity(self, entity_id: str):
    pool = await self.db.pool
    async with pool.acquire() as conn:
        return await conn.fetchrow("SELECT ...")
```

## 검증 도구

트랜잭션 사용 여부를 검증하는 스크립트:

```bash
python scripts/test_transaction_decorator.py
```

## 참고 자료

- PostgreSQL 트랜잭션 문서: https://www.postgresql.org/docs/current/tutorial-transactions.html
- asyncpg 트랜잭션 문서: https://magicstack.github.io/asyncpg/current/usage.html#transactions

