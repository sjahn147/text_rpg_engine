# QA 테스트에서 놓친 이슈 분석

## 발견된 문제

**이슈**: `ActionService.get_available_actions`에서 연결된 셀(connected_cells) 생성 시 FK 제약조건 위반

**에러**: 
```
asyncpg.exceptions.ForeignKeyViolationError: "cell_references" 테이블에서 자료 추가, 갱신 작업이 "fk_cell_references_runtime" 참조키(foreign key) 제약 조건을 위배했습니다
DETAIL: (runtime_cell_id)=(53b672dc-a6c2-4aea-a02f-1e36be20f734) 키가 "runtime_cells" 테이블에 없습니다.
```

**발생 위치**: `/api/gameplay/actions/{session_id}` 엔드포인트

**발생 시나리오**: 
1. 게임 시작 후 프론트엔드가 액션 목록을 조회
2. 현재 셀에 `connected_cells`가 정의되어 있음
3. `ActionService`가 연결된 셀의 런타임 인스턴스를 생성하려고 시도
4. `create_cell_reference`를 먼저 호출하여 FK 제약조건 위반

## 왜 QA 테스트에서 놓쳤는가?

### 1. API 엔드포인트 테스트 커버리지 부족

**현재 테스트 상태** (`docs/qa/TEST_COVERAGE_STATUS.md`):
- ✅ `/api/gameplay/start` - 게임 시작 API
- ✅ `/api/gameplay/state/{session_id}` - 게임 상태 조회 API
- ✅ `/api/gameplay/move` - 플레이어 이동 API
- ❌ `/api/gameplay/actions/{session_id}` - **액션 조회 API 테스트 없음**

**결론**: `get_available_actions` 엔드포인트에 대한 테스트가 전혀 작성되지 않았습니다.

### 2. 테스트 계획 문서의 누락

**`docs/qa/TEST_PLAN.md` 확인 결과**:
- 5. 상호작용 (Interactions) 섹션에는 엔티티/오브젝트 상호작용 테스트만 포함
- 6. API 엔드포인트 검증 섹션에는 게임 시작, 상태 조회, 이동 API만 포함
- **액션 조회 API에 대한 테스트 계획이 없음**

### 3. 실제 사용 시나리오와 테스트 시나리오의 차이

**실제 사용 플로우**:
```
1. 게임 시작 (POST /api/gameplay/start)
2. 액션 목록 조회 (GET /api/gameplay/actions/{session_id}) ← 이 단계가 테스트되지 않음
3. 액션 실행 (POST /api/gameplay/interact 등)
```

**테스트 플로우**:
```
1. 게임 시작 (POST /api/gameplay/start) ✅
2. 게임 상태 조회 (GET /api/gameplay/state/{session_id}) ✅
3. 직접 상호작용 (POST /api/gameplay/interact) ✅
```

**문제점**: 액션 목록 조회 단계를 건너뛰고 직접 상호작용으로 진행하여, 액션 목록 생성 로직의 문제를 발견하지 못함

### 4. 연결된 셀(Connected Cells) 시나리오 미검증

**현재 테스트**:
- `test_get_current_cell`: 현재 셀 정보 조회 (연결된 셀 정보 포함)
- 하지만 **연결된 셀의 런타임 인스턴스 생성**은 테스트하지 않음

**실제 문제 발생 조건**:
- 현재 셀의 `cell_properties.connected_cells`에 연결된 셀이 정의되어 있음
- `ActionService`가 이 연결된 셀들에 대한 이동 액션을 생성하려고 시도
- 연결된 셀의 런타임 인스턴스가 아직 생성되지 않았을 때 FK 제약조건 위반 발생

### 5. FK 제약조건 테스트의 한계

**현재 FK 제약조건 테스트** (`test_foreign_key_constraints_cell_references`):
- 게임 시작 시 셀 인스턴스 생성 순서만 검증
- **게임 시작 후 동적으로 셀 인스턴스를 생성하는 경우**는 검증하지 않음

**문제점**: 
- 게임 시작 시에는 `InstanceFactory`나 `GameManager`가 올바른 순서로 생성
- 하지만 `ActionService`에서 동적으로 생성할 때는 다른 코드 경로를 사용
- 이 코드 경로에 대한 테스트가 없음

## 근본 원인 분석

### 1. 엔드포인트 중심 테스트 부족

**현재 접근**:
- 기능별 테스트 (게임 시작, 이동, 상호작용)
- 서비스 레이어 직접 테스트

**부족한 부분**:
- **API 엔드포인트 전체 플로우 테스트**
- 실제 프론트엔드 사용 시나리오 기반 테스트

### 2. 동적 리소스 생성 시나리오 미검증

**검증된 시나리오**:
- 게임 시작 시 리소스 생성 (정적)
- 명시적 이동 요청 시 리소스 생성

**미검증 시나리오**:
- **액션 목록 조회 시 연결된 셀 동적 생성** ← 이 문제
- 기타 lazy loading 시나리오

### 3. 테스트 계획 수립 시 실제 사용 플로우 미반영

**테스트 계획 수립 시**:
- 기능별로 분리하여 테스트 계획 수립
- 각 기능의 정상 동작만 검증

**실제 사용 플로우**:
- 여러 API가 연속적으로 호출됨
- 이전 API 호출의 부수 효과(side effect)가 다음 API에 영향

## 개선 방안

### 1. 즉시 조치

#### 1.1 누락된 API 엔드포인트 테스트 추가

**추가할 테스트**:
```python
def test_get_available_actions_api_endpoint(
    self,
    client,
    test_game_data
):
    """
    P1: 액션 조회 API 엔드포인트
    
    검증 항목:
    - 상태 코드 (200 OK)
    - 응답 스키마 검증
    - 연결된 셀이 있는 경우 FK 제약조건 준수
    - 연결된 셀이 없는 경우 빈 액션 리스트 반환
    - 에러 처리 (잘못된 세션 ID)
    """
    # 게임 시작
    start_response = client.post(
        "/api/gameplay/start",
        json={
            "player_template_id": test_game_data["player_template_id"],
            "start_cell_id": test_game_data["cell_id"]
        }
    )
    session_id = start_response.json()["game_state"]["session_id"]
    
    # 액션 조회
    actions_response = client.get(f"/api/gameplay/actions/{session_id}")
    
    assert actions_response.status_code == 200
    actions = actions_response.json()
    assert isinstance(actions, list)
    # FK 제약조건 위반이 발생하지 않아야 함
```

#### 1.2 연결된 셀 동적 생성 시나리오 테스트 추가

**추가할 테스트**:
```python
async def test_connected_cells_dynamic_creation(
    self,
    db_connection,
    game_service,
    test_game_data
):
    """
    P1: 연결된 셀 동적 생성 검증
    
    검증 항목:
    - 연결된 셀의 런타임 인스턴스가 올바른 순서로 생성됨
    - FK 제약조건 준수
    - cell_references 생성 전 runtime_cells 생성 확인
    """
    # 게임 시작
    result = await game_service.start_game(...)
    session_id = result["game_state"]["session_id"]
    
    # 연결된 셀이 있는 셀에서 액션 조회
    from app.services.gameplay import ActionService
    action_service = ActionService(db_connection)
    
    # FK 제약조건 위반이 발생하지 않아야 함
    actions = await action_service.get_available_actions(session_id)
    
    # 연결된 셀의 런타임 인스턴스가 올바르게 생성되었는지 확인
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        # cell_references에 있는 모든 runtime_cell_id가 runtime_cells에 존재하는지 확인
        cell_refs = await conn.fetch("""
            SELECT cr.runtime_cell_id
            FROM reference_layer.cell_references cr
            WHERE cr.session_id = $1
        """, session_id)
        
        for cell_ref in cell_refs:
            runtime_cell = await conn.fetchrow("""
                SELECT runtime_cell_id
                FROM runtime_data.runtime_cells
                WHERE runtime_cell_id = $1
            """, cell_ref['runtime_cell_id'])
            assert runtime_cell is not None, f"runtime_cell_id {cell_ref['runtime_cell_id']}가 runtime_cells에 존재해야 함"
```

### 2. 중기 개선

#### 2.1 실제 사용 플로우 기반 통합 테스트

**추가할 테스트 시나리오**:
```python
async def test_full_gameplay_flow(
    self,
    client,
    test_game_data
):
    """
    P0: 전체 게임플레이 플로우 통합 테스트
    
    실제 프론트엔드 사용 시나리오:
    1. 게임 시작
    2. 액션 목록 조회
    3. 액션 실행
    4. 상태 업데이트 확인
    """
    # 1. 게임 시작
    start_response = client.post("/api/gameplay/start", ...)
    session_id = start_response.json()["game_state"]["session_id"]
    
    # 2. 액션 목록 조회 (이전에 테스트되지 않았던 단계)
    actions_response = client.get(f"/api/gameplay/actions/{session_id}")
    assert actions_response.status_code == 200
    actions = actions_response.json()
    
    # 3. 액션 실행
    if actions:
        first_action = actions[0]
        # 액션 타입에 따라 적절한 API 호출
        # ...
```

#### 2.2 동적 리소스 생성 패턴 테스트

**추가할 테스트 카테고리**:
- Lazy Loading 시나리오 테스트
- 동적 인스턴스 생성 시나리오 테스트
- FK 제약조건 준수 패턴 테스트

### 3. 장기 개선

#### 3.1 테스트 계획 수립 프로세스 개선

**개선 사항**:
1. **실제 사용 플로우 분석**: 프론트엔드 코드를 분석하여 실제 API 호출 순서 파악
2. **엔드포인트 목록 자동 생성**: FastAPI 라우터에서 모든 엔드포인트를 자동으로 추출하여 테스트 계획에 포함
3. **코드 커버리지 기반 테스트 계획**: 코드 커버리지 도구를 사용하여 테스트되지 않은 코드 경로 식별

#### 3.2 테스트 자동화 개선

**추가할 도구**:
- API 엔드포인트 자동 테스트 생성 (OpenAPI 스펙 기반)
- 통합 테스트 시나리오 자동 생성 (프론트엔드 코드 분석 기반)

## 결론

### 핵심 문제점

1. **API 엔드포인트 테스트 커버리지 부족**: `get_available_actions` 엔드포인트에 대한 테스트가 전혀 없었음
2. **실제 사용 플로우 미반영**: 게임 시작 → 액션 조회 → 액션 실행 플로우 중 액션 조회 단계가 테스트되지 않음
3. **동적 리소스 생성 시나리오 미검증**: 게임 시작 후 동적으로 셀 인스턴스를 생성하는 경우가 테스트되지 않음

### 개선 효과

위 개선 방안을 적용하면:
- **API 엔드포인트 커버리지**: 100% 달성 가능
- **실제 사용 플로우 커버리지**: 향상
- **동적 리소스 생성 버그**: 사전 발견 가능

### 다음 단계

1. ✅ `get_available_actions` API 엔드포인트 테스트 추가 (즉시)
2. ✅ 연결된 셀 동적 생성 시나리오 테스트 추가 (즉시)
3. ⏳ 전체 게임플레이 플로우 통합 테스트 추가 (중기)
4. ⏳ 테스트 계획 수립 프로세스 개선 (장기)


