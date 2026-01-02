# 테스트 커버리지 분석: 게임 시작 외래키 제약조건 위반 사례

## 문제 요약

게임 시작 시 `cell_references` 테이블에 데이터를 삽입할 때 `runtime_cells` 테이블에 해당 레코드가 없어 외래키 제약조건 위반이 발생했습니다. 이는 **가장 기본적인 데이터베이스 무결성 문제**임에도 테스트로 발견되지 않았습니다.

## 테스트 커버리지 분석

### 1. 게임 시작 전체 플로우 테스트 부재

#### 발견된 테스트 코드
- `tests/legacy/unit/test_game_manager.py`: **Mock 기반 단위 테스트만 존재**
  - `test_start_new_game_success`: 모든 의존성을 Mock으로 처리
  - 실제 데이터베이스 연동 없음
  - 외래키 제약조건 검증 불가능

```python
# tests/legacy/unit/test_game_manager.py
async def test_start_new_game_success(self, game_manager):
    # Mock 설정 - 실제 DB 호출 없음
    game_manager._create_cell_instance = AsyncMock(return_value="CELL_INSTANCE_001")
    # 실제 DB 제약조건 검증 불가능
```

#### 누락된 테스트
- **통합 테스트**: `GameManager.start_new_game()` → `InstanceFactory.create_cell_instance()` → 실제 DB 삽입
- **외래키 제약조건 검증**: `runtime_cells` 생성 후 `cell_references` 생성 순서 검증
- **게임 시작 API 엔드포인트 테스트**: `POST /api/gameplay/start` 실제 호출 테스트

### 2. 부분적 통합 테스트의 한계

#### `tests/active/integration/test_gameplay_api_migration.py`
```python
async def test_game_service_start_game(self, db_connection):
    try:
        result = await game_service.start_game(...)
        # ...
    except Exception as e:
        # 테스트 데이터가 없을 수 있으므로 스킵
        pytest.skip(f"테스트 데이터 부족: {str(e)}")
```

**문제점:**
- 예외 발생 시 `pytest.skip`으로 테스트를 건너뜀
- 외래키 제약조건 위반도 예외로 처리되어 스킵됨
- 실제 실패 원인을 파악하지 못함

### 3. 셀 생성 로직 테스트의 분리

#### `scripts/test_cell_manager_ssot.py`
- `CellManager.create_cell()` 메서드만 테스트
- `InstanceFactory.create_cell_instance()`는 테스트하지 않음
- 게임 시작 플로우에서 사용되는 실제 경로와 다름

#### `scripts/setup_test_data_for_cell_manager.py`
- `CellManager`를 통한 셀 생성만 테스트
- `InstanceFactory`를 통한 셀 생성은 테스트하지 않음

**문제점:**
- `CellManager.create_cell()`은 올바르게 구현됨 (`runtime_cells` 먼저 생성)
- 하지만 게임 시작 시 사용되는 `InstanceFactory.create_cell_instance()`는 잘못 구현됨
- 테스트가 실제 사용 경로를 커버하지 못함

## 근본 원인 분석

### 1. 테스트 전략의 문제

#### 단위 테스트에만 의존
- Mock 기반 테스트는 실제 데이터베이스 제약조건을 검증하지 못함
- 외래키, 트랜잭션, 데이터 무결성 등은 통합 테스트에서만 검증 가능

#### 통합 테스트의 부재
- 게임 시작 전체 플로우를 검증하는 통합 테스트가 없음
- API 엔드포인트부터 데이터베이스까지의 전체 경로 테스트 부재

### 2. 테스트 커버리지의 불일치

#### 테스트된 경로 vs 실제 사용 경로
- **테스트된 경로**: `CellManager.create_cell()` (올바른 구현)
- **실제 사용 경로**: `InstanceFactory.create_cell_instance()` (잘못된 구현)
- 테스트가 실제 사용 경로를 커버하지 못함

#### 코드 경로 분석 부재
- 어떤 코드 경로가 실제로 사용되는지 분석하지 않음
- 게임 시작 플로우에서 `InstanceFactory`가 사용됨을 테스트에서 확인하지 않음

### 3. 기본 시나리오 테스트 부재

#### "Happy Path" 테스트 누락
- 게임 시작은 가장 기본적인 시나리오
- 하지만 실제 DB를 사용한 통합 테스트가 없음
- Mock 테스트만으로는 실제 동작을 검증할 수 없음

## 개선 방안

### 1. 게임 시작 통합 테스트 추가

```python
# tests/active/integration/test_game_start_integration.py
@pytest.mark.asyncio
async def test_game_start_full_flow(db_connection):
    """게임 시작 전체 플로우 통합 테스트"""
    # 1. 게임 데이터 준비
    # 2. GameService.start_game() 호출
    # 3. 실제 DB에서 데이터 검증
    #    - runtime_cells에 레코드 존재 확인
    #    - cell_references에 레코드 존재 확인
    #    - 외래키 제약조건 준수 확인
```

### 2. 외래키 제약조건 검증 테스트

```python
@pytest.mark.asyncio
async def test_cell_instance_creation_order(db_connection):
    """셀 인스턴스 생성 순서 검증"""
    # runtime_cells 먼저 생성 확인
    # cell_references 나중에 생성 확인
    # 순서가 바뀌면 외래키 제약조건 위반 발생
```

### 3. API 엔드포인트 통합 테스트

```python
@pytest.mark.asyncio
async def test_game_start_api_endpoint(client, db_connection):
    """게임 시작 API 엔드포인트 통합 테스트"""
    response = await client.post("/api/gameplay/start", json={
        "player_template_id": "NPC_VILLAGER_001",
        "start_cell_id": "CELL_INN_ROOM_001"
    })
    assert response.status_code == 201
    # 실제 DB 검증
```

### 4. 테스트 데이터 자동 생성

```python
@pytest.fixture
async def game_start_test_data(db_connection):
    """게임 시작 테스트를 위한 데이터 자동 생성"""
    # game_data.world_cells 생성
    # game_data.entities 생성
    # 테스트 후 자동 정리
```

### 5. 코드 경로 분석 및 테스트 매핑

- 실제 사용되는 코드 경로를 분석
- 각 경로에 대한 테스트 작성
- 테스트 커버리지 리포트로 누락된 경로 확인

## 결론

이번 문제는 다음 테스트 전략의 결함으로 발생했습니다:

1. **Mock 기반 단위 테스트에만 의존**: 실제 DB 제약조건 검증 불가
2. **통합 테스트 부재**: 게임 시작 전체 플로우 검증 없음
3. **테스트 경로와 실제 사용 경로 불일치**: `CellManager`는 테스트했지만 `InstanceFactory`는 테스트하지 않음
4. **기본 시나리오 테스트 누락**: 게임 시작이라는 가장 기본적인 시나리오에 대한 통합 테스트 없음

**개선이 필요한 사항:**
- 모든 기본 시나리오에 대한 통합 테스트 필수
- 실제 데이터베이스를 사용한 외래키 제약조건 검증
- API 엔드포인트부터 데이터베이스까지의 전체 경로 테스트
- 테스트 커버리지 리포트를 통한 누락된 경로 확인

