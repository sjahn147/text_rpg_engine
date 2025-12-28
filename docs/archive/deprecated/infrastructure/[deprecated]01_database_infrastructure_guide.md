# [deprecated] 데이터베이스 인프라 가이드

> **Deprecated 날짜**: 2025-12-28  
> **Deprecated 사유**: 데이터베이스 인프라 구축이 완료되어 더 이상 진행 중인 작업이 아닙니다. 주요 내용은 `docs/changelog/CHANGELOG.md`와 `docs/architecture/` 폴더의 최신 문서들에 통합되었습니다.

> **최종 업데이트**: 2025-10-21  
> **현재 상태**: Phase 3 Village Simulation 완료, 모든 인프라 안정화, World Editor 80% 완료  
> **성능**: 1,226 entities/sec, 960 sessions/sec, 275 dialogues/sec

## 개요

RPG 엔진의 데이터베이스 연결 관리 및 테스트 인프라에 대한 종합 가이드입니다.  
Phase 3 Village Simulation을 통해 모든 인프라가 안정적으로 검증되었습니다.

## 🏗️ **아키텍처 개요**

### 1. **DB 연결 관리 계층**

```
┌─────────────────────────────────────┐
│        Application Layer            │
│  (EntityManager, CellManager, etc.) │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│      DatabaseConnectionManager      │
│     (Connection Lifecycle Mgmt)     │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│        DatabaseConnection           │
│      (Connection Pool Mgmt)         │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│           PostgreSQL                │
│         (Database Server)           │
└─────────────────────────────────────┘
```

### 2. **핵심 컴포넌트**

#### **DatabaseConnectionManager**
- **위치**: `database/connection_manager.py`
- **역할**: 연결 풀 생명주기 관리, 테스트 환경별 연결 분리
- **주요 기능**:
  - 연결 초기화/종료 관리
  - 테스트별 독립적인 이벤트 루프 생성
  - 연결 상태 추적

#### **DatabaseConnection (개선됨)**
- **위치**: `database/connection.py`
- **역할**: 실제 DB 연결 풀 관리
- **개선사항**:
  - 연결 상태 관리 (`_is_initialized`, `_is_closed`)
  - 명시적 초기화/종료 메서드
  - 연결 풀 크기 최적화 (min_size=2, max_size=10)

#### **TestDatabaseManager**
- **위치**: `database/connection_manager.py`
- **역할**: 테스트용 DB 연결 관리
- **주요 기능**:
  - 테스트별 독립적인 연결 생성
  - 테스트 완료 후 자동 정리
  - 이벤트 루프 격리

## 🔧 **설정 및 사용법**

### 1. **기본 DB 연결 사용**

```python
from database.connection import DatabaseConnection

# 연결 생성 및 초기화
db_connection = DatabaseConnection()
await db_connection.initialize()

# 사용
pool = await db_connection.pool
async with pool.acquire() as conn:
    result = await conn.fetchval("SELECT 1")

# 연결 정리
await db_connection.close()
```

### 2. **테스트용 DB 연결 사용**

```python
from database.connection_manager import test_db_manager

# 테스트용 연결 생성
test_id = "test-001"
connection = await test_db_manager.create_test_connection(test_id)

# 테스트 실행
# ... 테스트 코드 ...

# 연결 정리
await test_db_manager.cleanup_test_connection(test_id)
```

### 3. **통합 테스트 픽스처 사용**

```python
import pytest

@pytest.mark.asyncio
async def test_with_db_infrastructure(db_connection, managers, clean_database):
    """DB 인프라를 사용한 테스트"""
    entity_manager = managers['entity_manager']
    
    result = await entity_manager.create_entity(
        name="Test Player",
        entity_type=EntityType.PLAYER
    )
    
    assert result.success
```

## 🧪 **테스트 전략**

### 1. **테스트 계층 분리**

| 테스트 유형 | DB 연결 방식 | 격리 수준 | 목적 |
|------------|-------------|----------|------|
| **단위 테스트** | Mock | 완전 격리 | 로직 검증 |
| **시나리오 테스트** | Mock | 완전 격리 | 시나리오 검증 |
| **통합 테스트** | 실제 DB | 테스트별 격리 | DB 연동 검증 |

### 2. **테스트 격리 전략**

#### **이벤트 루프 격리**
```python
# 각 테스트마다 독립적인 이벤트 루프 생성
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
```

#### **DB 연결 격리**
```python
# 테스트별 독립적인 DB 연결
test_id = str(uuid.uuid4())
connection = await test_db_manager.create_test_connection(test_id)
```

#### **데이터 격리**
```python
# 테스트 전 DB 정리
async with pool.acquire() as conn:
    await conn.execute("DELETE FROM runtime_data.runtime_entities")
```

## 🚨 **문제 해결 가이드**

### 1. **Event loop is closed**
**원인**: 비동기 이벤트 루프가 테스트 간에 공유되면서 조기에 종료
**해결**: 테스트별 독립적인 이벤트 루프 생성

### 2. **cannot perform operation: another operation is in progress**
**원인**: DB 연결 풀이 동시성 제어 없이 사용
**해결**: 연결 풀 상태 관리 및 적절한 동시성 제어

### 3. **Pool is closed**
**원인**: DB 연결 풀이 테스트 간에 제대로 관리되지 않음
**해결**: 명시적 연결 생명주기 관리

## 📊 **성능 최적화**

### 1. **연결 풀 설정**
```python
# 최적화된 연결 풀 설정
self._pool = await asyncpg.create_pool(
    host=self.host,
    port=self.port,
    user=self.user,
    password=self.password,
    database=self.database,
    min_size=2,      # 최소 연결 수
    max_size=10,     # 최대 연결 수
    command_timeout=60,
    server_settings={
        'application_name': 'rpg_engine'
    }
)
```

### 2. **연결 재사용**
- 연결 풀을 통한 연결 재사용
- 테스트 간 연결 상태 유지
- 적절한 연결 수 유지

## 🔄 **개발 워크플로우**

### 1. **개발 단계**
1. **단위 테스트**: Mock 사용, 빠른 피드백
2. **시나리오 테스트**: Mock 사용, 시나리오 검증
3. **통합 테스트**: 실제 DB 사용, DB 연동 검증

### 2. **테스트 실행 순서**
```bash
# 1. 단위 테스트 (Mock 사용)
python -m pytest tests/unit/ -v

# 2. 시나리오 테스트 (Mock 사용)
python -m pytest tests/scenarios/ -v

# 3. 통합 테스트 (실제 DB 사용)
python -m pytest tests/integration/test_simple_db_integration.py -v
```

## 📈 **모니터링 및 로깅**

### 1. **연결 상태 모니터링**
```python
# 연결 상태 확인
print(f"연결 수: {connection_manager.get_connection_count()}")
print(f"초기화 상태: {connection_manager.is_initialized()}")
```

### 2. **로깅 설정**
```python
# DB 연결 로깅
logger.info("Database connection pool initialized successfully")
logger.error(f"Failed to initialize database connection: {str(e)}")
```

## 🎯 **다음 단계**

### 1. **즉시 실행**
- [ ] DB 스키마 완성 (`runtime_data.cell_occupants` 테이블 생성)
- [ ] 통합 테스트 안정화
- [ ] 성능 최적화

### 2. **중기 계획**
- [ ] 연결 풀 모니터링 대시보드
- [ ] 자동 스케일링 구현
- [ ] 백업 및 복구 시스템

### 3. **장기 계획**
- [ ] 분산 DB 지원
- [ ] 읽기 전용 복제본 지원
- [ ] 캐싱 레이어 추가

## 📚 **참고 자료**

- [PostgreSQL 공식 문서](https://www.postgresql.org/docs/)
- [asyncpg 문서](https://magicstack.github.io/asyncpg/)
- [pytest-asyncio 문서](https://pytest-asyncio.readthedocs.io/)

---

**작성일**: 2025-10-18  
**버전**: v1.0  
**작성자**: RPG Engine Development Team
