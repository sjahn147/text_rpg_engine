# 테스트 가이드라인

> **최신화 날짜**: 2026-01-03  
> **적용 범위**: 모든 테스트 작성 및 실행 시 필수 읽기

## ⚠️ 중요: 테스트 커버리지 80% 이상 필수

**모든 테스트는 반드시 80% 이상의 커버리지를 달성해야 합니다.**

## 1. 개요

RPG Engine은 pytest 기반의 포괄적인 테스트 스위트를 사용합니다. 모든 테스트는 비동기 환경에서 실행되며, 실제 데이터베이스를 사용합니다.

### 1.1 테스트 프레임워크

- **pytest**: 테스트 프레임워크
- **pytest-asyncio**: 비동기 테스트 지원
- **pytest-cov**: 커버리지 측정

### 1.2 테스트 디렉토리 구조

```
tests/
├── conftest.py              # 공통 픽스처 및 설정
├── run_tests.py             # 테스트 실행 스크립트
├── active/                  # 활성 테스트 (현재 사용 중)
│   ├── integration/        # 통합 테스트
│   ├── scenarios/          # 시나리오 테스트
│   └── simulation/         # 시뮬레이션 테스트
├── qa/                      # QA 테스트 스위트
├── unit/                    # 단위 테스트
├── integration/             # 통합 테스트
├── database/                # 데이터베이스 테스트
│   ├── game_data/          # 게임 데이터 테스트
│   └── factories/          # Factory 테스트
├── world_editor/            # 월드 에디터 테스트
├── legacy/                  # 레거시 테스트 (아카이브)
└── deprecated/              # 사용 중단된 테스트
```

## 2. 테스트 작성 원칙

### 2.1 필수 원칙

1. **비동기 함수 사용**: 모든 테스트는 `async def`로 작성
2. **픽스처 사용**: `conftest.py`의 픽스처 활용
3. **독립성**: 각 테스트는 독립적으로 실행 가능해야 함
4. **명확한 이름**: 테스트 함수명은 `test_`로 시작하고 의도를 명확히 표현
5. **에러 처리**: 모든 예외를 명시적으로 처리
6. **트랜잭션 관리**: 데이터 변경 작업은 트랜잭션 내에서 수행

### 2.2 테스트 함수 명명 규칙

```python
# ✅ 올바른 명명
async def test_entity_creation_with_valid_data():
    """유효한 데이터로 엔티티 생성 테스트"""
    pass

async def test_cell_manager_move_entity_success():
    """CellManager 엔티티 이동 성공 테스트"""
    pass

# ❌ 잘못된 명명
async def test1():  # 의도 불명확
    pass

async def test_entity():  # 너무 모호함
    pass
```

### 2.3 테스트 구조 (AAA 패턴)

```python
@pytest.mark.asyncio
async def test_example(db_connection, managers):
    """테스트 예시"""
    # Arrange (준비)
    entity_manager = managers['entity_manager']
    test_entity_id = "TEST_ENTITY_001"
    
    # Act (실행)
    result = await entity_manager.create_entity(
        entity_id=test_entity_id,
        entity_type="npc",
        entity_name="Test NPC"
    )
    
    # Assert (검증)
    assert result.success is True
    assert result.entity_id == test_entity_id
```

## 3. 공통 픽스처 (conftest.py)

### 3.1 주요 픽스처

**데이터베이스 연결**:
```python
@pytest.fixture(scope="function")
async def db_connection() -> AsyncGenerator[DatabaseConnection, None]:
    """테스트용 DB 연결"""
    # 자동으로 테스트별 독립적인 연결 생성 및 정리
```

**리포지토리**:
```python
@pytest.fixture(scope="function")
async def repositories(db_connection: DatabaseConnection) -> Dict[str, Any]:
    """리포지토리 인스턴스들"""
    return {
        'game_data_repo': GameDataRepository(db_connection),
        'runtime_data_repo': RuntimeDataRepository(db_connection),
        'reference_layer_repo': ReferenceLayerRepository(db_connection)
    }
```

**매니저**:
```python
@pytest.fixture(scope="function")
async def managers(db_connection, repositories) -> Dict[str, Any]:
    """매니저 인스턴스들"""
    return {
        'entity_manager': EntityManager(...),
        'cell_manager': CellManager(...),
        'dialogue_manager': DialogueManager(...),
        'action_handler': ActionHandler(...),
        'effect_carrier_manager': EffectCarrierManager(...)
    }
```

**데이터베이스 정리**:
```python
@pytest.fixture(scope="function")
async def clean_database(db_connection: DatabaseConnection):
    """테스트 전 DB 정리"""
    # 런타임 데이터 자동 정리
```

**테스트 세션 ID**:
```python
@pytest.fixture(scope="function")
async def test_session_id() -> str:
    """테스트용 세션 ID"""
    return str(uuid.uuid4())
```

### 3.2 픽스처 사용 예시

```python
@pytest.mark.asyncio
async def test_entity_creation(
    db_connection: DatabaseConnection,
    repositories: Dict[str, Any],
    managers: Dict[str, Any],
    clean_database,
    test_session_id: str
):
    """엔티티 생성 테스트"""
    entity_manager = managers['entity_manager']
    # 테스트 로직...
```

## 4. 테스트 카테고리

### 4.1 Unit Tests (단위 테스트)

**위치**: `tests/unit/`

**목적**: 개별 함수/메서드의 동작 검증

**예시**:
```python
@pytest.mark.asyncio
async def test_uuid_helper_normalize():
    """uuid_helper.normalize_uuid() 테스트"""
    from app.common.utils.uuid_helper import normalize_uuid
    
    # UUID 객체 → 문자열
    uuid_obj = uuid.uuid4()
    result = normalize_uuid(uuid_obj)
    assert isinstance(result, str)
```

### 4.2 Integration Tests (통합 테스트)

**위치**: `tests/active/integration/`, `tests/integration/`

**목적**: 여러 컴포넌트 간 상호작용 검증

**예시**:
```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_entity_cell_interaction(managers, test_session_id):
    """엔티티-셀 상호작용 통합 테스트"""
    entity_manager = managers['entity_manager']
    cell_manager = managers['cell_manager']
    
    # 엔티티 생성
    entity_result = await entity_manager.create_entity(...)
    
    # 셀 생성
    cell_result = await cell_manager.create_cell(...)
    
    # 엔티티를 셀에 배치
    move_result = await cell_manager.move_entity(...)
    
    assert move_result.success is True
```

### 4.3 Scenario Tests (시나리오 테스트)

**위치**: `tests/active/scenarios/`

**목적**: 실제 게임 플레이 시나리오 검증

**예시**:
```python
@pytest.mark.asyncio
async def test_dialogue_system_scenario(managers, test_session_id):
    """대화 시스템 시나리오 테스트"""
    # 1. 플레이어와 NPC 생성
    # 2. 대화 시작
    # 3. 대화 계속
    # 4. 대화 종료
    # 5. 대화 기록 확인
```

### 4.4 QA Tests (QA 테스트)

**위치**: `tests/qa/`

**목적**: 핵심 기능 및 데이터 무결성 검증

**우선순위**:
- **P0 (Critical)**: 게임 시작 플로우, 데이터 무결성, 트랜잭션 무결성
- **P1 (High)**: API 엔드포인트, 에러 처리

**예시**:
```python
@pytest.mark.asyncio
@pytest.mark.qa
@pytest.mark.p0
async def test_game_start_flow(managers, test_session_id):
    """게임 시작 플로우 P0 테스트"""
    # 게임 시작 → 플레이어 생성 → 초기 셀 배치 → 게임 상태 확인
```

### 4.5 Database Tests (데이터베이스 테스트)

**위치**: `tests/database/`

**목적**: 데이터베이스 스키마 및 쿼리 검증

**예시**:
```python
@pytest.mark.asyncio
async def test_schema_compliance(db_connection):
    """스키마 준수 테스트"""
    # mvp_schema.sql과 실제 스키마 비교
```

## 5. 테스트 실행

### 5.1 전체 테스트 실행

```bash
# 프로젝트 루트에서
python tests/run_tests.py

# 또는 pytest 직접 실행
pytest tests/ -v --cov=app --cov=database --cov=common --cov-report=term-missing --cov-fail-under=80
```

### 5.2 특정 카테고리 실행

```bash
# 활성 테스트만
pytest tests/active/ -v

# 통합 테스트만
pytest tests/active/integration/ -v

# 시나리오 테스트만
pytest tests/active/scenarios/ -v

# QA 테스트만
pytest tests/qa/ -v

# 단위 테스트만
pytest tests/unit/ -v
```

### 5.3 특정 테스트 파일 실행

```bash
# 특정 파일
pytest tests/active/integration/test_basic_crud.py -v

# 특정 테스트 함수
pytest tests/active/integration/test_basic_crud.py::test_entity_creation -v
```

### 5.4 마커를 사용한 필터링

```bash
# integration 마커만
pytest -m integration -v

# qa 마커만
pytest -m qa -v

# p0 우선순위만
pytest -m p0 -v
```

## 6. 커버리지 요구사항

### 6.1 커버리지 목표

- **전체 커버리지**: 80% 이상
- **핵심 모듈**: 90% 이상 (app/managers, app/handlers, app/services)
- **유틸리티**: 85% 이상 (common/utils)

### 6.2 커버리지 확인

```bash
# 터미널 출력
pytest --cov=app --cov-report=term-missing

# HTML 리포트 생성
pytest --cov=app --cov-report=html
# → htmlcov/index.html 열기
```

### 6.3 커버리지 실패 처리

커버리지가 80% 미만이면 테스트가 실패합니다:

```bash
# 커버리지 실패 허용 (개발 중)
pytest --cov=app --cov-fail-under=0

# 커버리지 목표 설정
pytest --cov=app --cov-fail-under=80
```

## 7. 테스트 작성 가이드라인

### 7.1 비동기 테스트

**✅ 올바른 방법**:
```python
@pytest.mark.asyncio
async def test_async_function(managers):
    """비동기 함수 테스트"""
    result = await managers['entity_manager'].create_entity(...)
    assert result.success is True
```

**❌ 잘못된 방법**:
```python
def test_async_function(managers):
    """비동기 함수를 동기로 호출 (에러 발생)"""
    result = managers['entity_manager'].create_entity(...)  # ❌
```

### 7.2 데이터베이스 트랜잭션

**✅ 올바른 방법**:
```python
@pytest.mark.asyncio
async def test_transaction(db_connection):
    """트랜잭션 테스트"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        async with conn.transaction():
            # 트랜잭션 내 작업
            await conn.execute("INSERT INTO ...")
            # 자동 롤백 (테스트 종료 시)
```

### 7.3 UUID 처리

**✅ 올바른 방법**:
```python
from app.common.utils.uuid_helper import normalize_uuid, to_uuid

@pytest.mark.asyncio
async def test_uuid_handling():
    """UUID 처리 테스트"""
    # UUID 객체 생성
    uuid_obj = uuid.uuid4()
    
    # 문자열로 변환
    uuid_str = normalize_uuid(uuid_obj)
    assert isinstance(uuid_str, str)
    
    # 문자열에서 UUID 객체로 변환
    uuid_obj2 = to_uuid(uuid_str)
    assert uuid_obj == uuid_obj2
```

### 7.4 에러 처리

**✅ 올바른 방법**:
```python
@pytest.mark.asyncio
async def test_error_handling(managers):
    """에러 처리 테스트"""
    entity_manager = managers['entity_manager']
    
    # 예외 발생 예상
    with pytest.raises(ValueError, match="Invalid entity ID"):
        await entity_manager.create_entity(
            entity_id="",  # 빈 ID (에러 발생 예상)
            entity_type="npc"
        )
```

### 7.5 Mock 사용 (제한적)

**⚠️ 주의**: 프로덕션 코드에는 Mock을 사용하지 않지만, 테스트에서는 제한적으로 사용 가능합니다.

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_with_mock():
    """Mock을 사용한 테스트 (외부 의존성 격리)"""
    with patch('app.managers.entity_manager.EntityManager.get_entity') as mock_get:
        mock_get.return_value = AsyncMock(success=True, entity_id="TEST_001")
        
        # 테스트 로직...
```

## 8. 테스트 데이터 관리

### 8.1 테스트 데이터 생성

**✅ 올바른 방법**:
```python
@pytest.mark.asyncio
async def test_with_test_data(managers, clean_database):
    """테스트 데이터 사용"""
    entity_manager = managers['entity_manager']
    
    # 테스트 데이터 생성
    test_entity_id = "TEST_ENTITY_001"
    result = await entity_manager.create_entity(
        entity_id=test_entity_id,
        entity_type="npc",
        entity_name="Test NPC"
    )
    
    # clean_database 픽스처가 자동으로 정리
```

### 8.2 테스트 데이터 격리

각 테스트는 독립적으로 실행되며, `clean_database` 픽스처가 자동으로 데이터를 정리합니다:

```python
@pytest.fixture(scope="function")
async def clean_database(db_connection: DatabaseConnection):
    """테스트 전 DB 정리"""
    # 런타임 데이터 자동 정리
    await conn.execute("DELETE FROM runtime_data.runtime_entities")
    await conn.execute("DELETE FROM runtime_data.runtime_cells")
    # ...
```

## 9. 테스트 마커

### 9.1 기본 마커

- `@pytest.mark.asyncio`: 비동기 테스트
- `@pytest.mark.integration`: 통합 테스트
- `@pytest.mark.qa`: QA 테스트
- `@pytest.mark.unit`: 단위 테스트

### 9.2 우선순위 마커

- `@pytest.mark.p0`: Critical (즉시 수정 필요)
- `@pytest.mark.p1`: High (빠른 시일 내 수정)

### 9.3 마커 사용 예시

```python
@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.p0
async def test_critical_integration(managers):
    """Critical 통합 테스트"""
    pass
```

## 10. 자주 발생하는 에러 및 해결

### 10.1 비동기 함수 호출 오류

**에러**: `RuntimeError: This event loop is already running`

**해결**:
- `@pytest.mark.asyncio` 데코레이터 추가
- `async def` 사용 확인

### 10.2 데이터베이스 연결 오류

**에러**: `Connection refused` 또는 `Database does not exist`

**해결**:
- `.env` 파일의 데이터베이스 설정 확인
- 데이터베이스 서버 실행 확인
- `mvp_schema.sql` 적용 확인

### 10.3 UUID 타입 오류

**에러**: `TypeError: Object of type UUID is not JSON serializable`

**해결**:
- `uuid_helper.normalize_uuid()` 사용
- JSONB 필드에 저장 시 문자열로 변환

### 10.4 트랜잭션 오류

**에러**: `Transaction already in progress`

**해결**:
- 중첩된 트랜잭션 확인
- `async with conn.transaction():` 올바른 사용 확인

## 11. 체크리스트

테스트 작성 전 확인사항:

- [ ] `@pytest.mark.asyncio` 데코레이터 추가
- [ ] 테스트 함수명이 `test_`로 시작하고 의도가 명확한지 확인
- [ ] AAA 패턴 (Arrange-Act-Assert) 사용
- [ ] 필요한 픽스처 사용 (`db_connection`, `managers`, `clean_database` 등)
- [ ] UUID는 `uuid_helper.py` 사용
- [ ] 트랜잭션은 적절히 사용
- [ ] 에러 처리는 `pytest.raises()` 사용
- [ ] 커버리지 80% 이상 달성
- [ ] 테스트가 독립적으로 실행 가능한지 확인

## 12. 참고 문서

- `00_CORE/01_PHILOSOPHY.md`: 핵심 개발 철학 (테스트 주도 개발)
- `00_CORE/02_ARCHITECTURE_PRINCIPLES.md`: 아키텍처 원칙
- `01_TYPE_SAFETY/UUID_GUIDELINES.md`: UUID 처리 가이드라인
- `01_TYPE_SAFETY/TRANSACTION_GUIDELINES.md`: 트랜잭션 가이드라인
- `tests/conftest.py`: 공통 픽스처 정의
- `tests/run_tests.py`: 테스트 실행 스크립트
- `tests/active/README.md`: 활성 테스트 가이드
- `tests/qa/README.md`: QA 테스트 가이드

