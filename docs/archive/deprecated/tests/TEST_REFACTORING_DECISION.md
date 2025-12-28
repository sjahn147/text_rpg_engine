# 테스트 코드 리팩토링 vs 재작성 의사결정 보고서

> **최신화 날짜**: 2025-12-28  
> **작성일**: 2025-10-20  
> **목적**: 기존 테스트 코드의 처리 방향 결정  
> **현재 상태**: 이 의사결정이 반영되어 테스트 재구성이 완료되었으며, 현재는 모든 테스트 100% 통과

---

## 🎯 핵심 결론

**권장사항: 단계적 정리 + 선택적 재작성**

```
✅ 유지/업데이트: 최신 아키텍처 반영 테스트 (25%)
⚠️ 아카이브: 참고용 구버전 테스트 (50%)
❌ 삭제: 중복/무의미 테스트 (25%)
```

---

## 📊 현재 테스트 코드 현황 분석

### 1. 전체 테스트 파일 구조

```
tests/
├── unit/                           # 단위 테스트 (6개)
├── integration/                    # 통합 테스트 (11개)
├── scenarios/                      # 시나리오 테스트 (13개)
└── simulation/                     # 시뮬레이션 테스트 (2개)

총 32개 테스트 파일
```

### 2. 테스트 코드 상태 분류

#### ✅ **활성(Active) 테스트** - 최신 아키텍처 반영
```
tests/scenarios/test_real_db_scenarios.py          # 실제 DB 시나리오
tests/simulation/test_village_simulation.py        # 마을 시뮬레이션
tests/integration/test_manager_integration.py      # Manager 통합
```
**특징**:
- 현재 MVP 스키마 (`runtime_entities`, `runtime_cells`) 사용
- Repository 패턴 사용
- `static_entity_id` + `session_id` 기반 API 사용

#### ⚠️ **과도기(Transitional) 테스트** - 부분 업데이트 필요
```
tests/integration/test_simple_db_integration.py    # 구버전 API 사용
tests/integration/test_mvp_goals.py                # MVP 목표 검증
tests/scenarios/basic_entity_creation.py           # 기본 엔티티 생성
tests/scenarios/integrated_gameplay_scenarios.py   # 통합 게임플레이
```
**특징**:
- Repository 초기화는 수정됨 (오늘 작업)
- 하지만 Manager API는 구버전 사용
- 정적 템플릿 데이터 부족

#### ❌ **레거시(Legacy) 테스트** - 구 아키텍처
```
tests/scenarios/scenario_test.py                   # Factory 패턴 사용
tests/scenarios/class_based_scenario_test.py       # 구 아키텍처
tests/scenarios/modular_scenario_test.py           # 구 아키텍처
tests/unit/test_entity_manager.py                  # 구 API 테스트
```
**특징**:
- `reference_layer` 의존
- `GameDataFactory`, `InstanceFactory` 사용
- 3-tier 아키텍처 전제

---

## 🔍 주요 아키텍처 변경 사항

### 변경 1: 스키마 단순화

**이전 (복잡한 3-tier)**:
```
game_data.entities
    ↓
reference_layer.entity_references (중간 계층)
    ↓
runtime_data.entity_states (상태만 저장)
```

**현재 (단순화된 2-tier)**:
```
game_data.entities (정적 템플릿)
    ↓
runtime_data.runtime_entities (직접 인스턴스화)
```

### 변경 2: Manager API 변경

**이전**:
```python
entity = await entity_manager.create_entity(
    name="Test Player",
    entity_type=EntityType.PLAYER,
    properties={"health": 100}
)
```

**현재**:
```python
result = await entity_manager.create_entity(
    static_entity_id="NPC_VILLAGER_001",  # DB 템플릿 참조
    session_id=session_id,
    custom_properties={"health": 150}     # 선택적 오버라이드
)
```

### 변경 3: Repository 초기화

**이전**:
```python
repo = GameDataRepository()  # 인자 없음
```

**현재**:
```python
db = DatabaseConnection()
await db.initialize()
repo = GameDataRepository(db)  # DB 인스턴스 필요
```

---

## 💡 의사결정 기준

### A. 리팩토링이 적합한 경우

✅ **다음 조건을 만족하면 리팩토링**:
1. 테스트의 **의도(Intent)**가 여전히 유효함
2. MVP 목표와 직접 관련됨
3. 수정 범위가 명확하고 제한적임
4. 정적 템플릿 데이터가 이미 존재함

**예시**:
- `test_simple_db_integration.py`: 기본 CRUD 검증 → **리팩토링**
- `test_mvp_goals.py`: MVP 수용 기준 검증 → **리팩토링**

### B. 재작성이 적합한 경우

✅ **다음 조건을 만족하면 재작성**:
1. 테스트가 **구 아키텍처**를 전제로 설계됨
2. 수정 범위가 50% 이상
3. 새로운 테스트 전략이 필요함
4. 중복된 테스트 로직이 많음

**예시**:
- `scenario_test.py`: Factory 패턴 전체 의존 → **재작성**
- `class_based_scenario_test.py`: 3-tier 구조 전제 → **재작성**

### C. 아카이브가 적합한 경우

✅ **다음 조건을 만족하면 아카이브**:
1. 참고용으로만 의미 있음
2. 현재는 실행 불가하지만 나중에 참고할 수 있음
3. 삭제하기엔 아까운 테스트 시나리오

**예시**:
- `modular_scenario_test.py`: 좋은 테스트 구조 → **아카이브**
- `effect_carrier_scenarios.py`: 미구현 기능 → **아카이브**

---

## 📋 구체적인 작업 계획

### Phase 1: 테스트 정리 (우선순위 높음)

#### 1.1 디렉토리 구조 개선
```
tests/
├── active/                    # ✅ 실행 가능한 테스트
│   ├── integration/
│   ├── scenarios/
│   └── simulation/
├── legacy/                    # ⚠️ 아카이브 (참고용)
│   ├── old_api_tests/
│   └── factory_pattern_tests/
└── deprecated/                # ❌ 삭제 예정
    └── broken_tests/
```

#### 1.2 각 테스트 분류 작업

**✅ Active로 이동 (그대로 유지)**:
```
tests/scenarios/test_real_db_scenarios.py
tests/simulation/test_village_simulation.py
tests/integration/test_manager_integration.py
tests/integration/test_entity_manager_db_integration.py
tests/integration/test_cell_manager_db_integration.py
tests/integration/test_dialogue_manager_db_integration.py
tests/integration/test_action_handler_db_integration.py
```

**⚠️ Legacy로 이동 (아카이브)**:
```
tests/scenarios/scenario_test.py
tests/scenarios/class_based_scenario_test.py
tests/scenarios/modular_scenario_test.py
tests/scenarios/effect_carrier_scenarios.py
tests/unit/test_entity_manager.py (구 API)
tests/unit/test_cell_manager.py (구 API)
```

**🔧 수정 후 Active로 이동**:
```
tests/integration/test_simple_db_integration.py    # API 업데이트
tests/integration/test_mvp_goals.py               # 정적 템플릿 추가
tests/scenarios/basic_entity_creation.py          # API 업데이트
tests/scenarios/integrated_gameplay_scenarios.py  # API 업데이트
```

**❌ Deprecated로 이동 (삭제 예정)**:
```
tests/database_test.py              # 중복
tests/test_simple_db_connection.py  # 중복
tests/fix_triggers.py               # 일회성 스크립트
```

---

### Phase 2: 새 테스트 작성 (중장기)

#### 2.1 필수 테스트 (MVP 직접 검증)

**1. 기본 CRUD 테스트**
```python
# tests/active/integration/test_basic_crud.py
class TestBasicCRUD:
    async def test_entity_lifecycle():
        """엔티티 생성 → 조회 → 수정 → 삭제"""
    
    async def test_cell_lifecycle():
        """셀 생성 → 로딩 → 수정 → 삭제"""
```

**2. 시나리오 테스트 (MVP 수용 기준)**
```python
# tests/active/scenarios/test_mvp_acceptance.py
class TestMVPAcceptance:
    async def test_100_iterations_no_error():
        """100회 행동 루프 무오류"""
    
    async def test_session_save_load():
        """세션 저장 및 복구"""
    
    async def test_devmode_promote():
        """DevMode에서 생성한 엔티티 promote"""
```

**3. 데이터 무결성 테스트**
```python
# tests/active/integration/test_data_integrity.py
class TestDataIntegrity:
    async def test_foreign_key_constraints():
        """FK 제약조건 검증"""
    
    async def test_template_referential_integrity():
        """정적 템플릿 참조 무결성"""
```

#### 2.2 테스트 픽스처 중앙화

```python
# tests/active/conftest.py
@pytest_asyncio.fixture
async def db_with_templates():
    """테스트용 정적 템플릿이 준비된 DB"""
    db = DatabaseConnection()
    await db.initialize()
    
    # 테스트용 정적 템플릿 생성
    await setup_test_templates(db)
    
    yield db
    await db.close()

@pytest_asyncio.fixture
async def managers(db_with_templates):
    """모든 Manager 인스턴스 제공"""
    game_data_repo = GameDataRepository(db_with_templates)
    runtime_data_repo = RuntimeDataRepository(db_with_templates)
    reference_layer_repo = ReferenceLayerRepository(db_with_templates)
    
    return {
        'entity_manager': EntityManager(db_with_templates, game_data_repo, runtime_data_repo, reference_layer_repo),
        'cell_manager': CellManager(db_with_templates, game_data_repo, runtime_data_repo, reference_layer_repo),
        # ...
    }
```

---

## 🎯 최종 권장사항

### ✅ **즉시 실행 (1-2일)**

1. **테스트 디렉토리 재구성**
   ```bash
   mkdir tests/active tests/legacy tests/deprecated
   ```

2. **분류 작업 실행**
   - Active: 7개 파일 이동
   - Legacy: 10개 파일 이동 + README 작성
   - Deprecated: 3개 파일 이동

3. **Repository 초기화 수정 검증**
   - 오늘 수정한 20개 파일 테스트 실행
   - 통과하는 것만 Active로 확정

### 🔧 **단기 작업 (1주)**

4. **정적 템플릿 데이터 준비**
   ```sql
   -- database/setup/test_templates.sql
   INSERT INTO game_data.entities VALUES
   ('NPC_VILLAGER_001', 'villager', '마을 주민', ...),
   ('NPC_MERCHANT_001', 'merchant', '상인', ...);
   ```

5. **과도기 테스트 4개 업데이트**
   - `test_simple_db_integration.py`
   - `test_mvp_goals.py`
   - `basic_entity_creation.py`
   - `integrated_gameplay_scenarios.py`

6. **공통 픽스처 작성**
   - `tests/active/conftest.py`
   - `db_with_templates` fixture
   - `managers` fixture

### 📝 **중기 작업 (2-3주)**

7. **새 테스트 작성**
   - `test_basic_crud.py`
   - `test_mvp_acceptance.py`
   - `test_data_integrity.py`

8. **CI/CD 통합**
   - GitHub Actions 설정
   - 테스트 자동 실행

---

## 📌 구현 가이드

### 아카이브용 README 템플릿

```markdown
# Legacy Tests (아카이브)

이 디렉토리의 테스트들은 **구 아키텍처**(Factory 패턴, 3-tier 구조)를 전제로 작성되었습니다.

## ⚠️ 실행 불가

현재 프로젝트의 아키텍처가 변경되어 이 테스트들은 실행할 수 없습니다.

## 📚 참고 목적

- 테스트 시나리오 아이디어
- 테스트 구조 설계 패턴
- 엣지 케이스 발견 사례

## 🔄 마이그레이션

새 아키텍처로 마이그레이션하려면:
1. `active/conftest.py`의 픽스처 사용
2. Manager API를 `static_entity_id` + `session_id` 형태로 변경
3. `GameDataFactory` 제거, DB 템플릿 직접 참조

## 📋 파일 목록

- `scenario_test.py`: Factory 패턴 기반 시나리오
- `class_based_scenario_test.py`: 3-tier 구조 전제
- ...
```

---

## ✨ 결론

**리팩토링 vs 재작성**의 이분법이 아니라:

```
1. 정리 (Reorganize)     → 즉시
2. 선택적 수정 (Update)   → 단기
3. 선택적 재작성 (Rewrite) → 중기
```

**3단계 접근**이 가장 효율적입니다.

현재 프로젝트는 **아키텍처 전환기**이므로, 모든 테스트를 리팩토링하는 것은 비효율적입니다. 대신:

- ✅ **활성 테스트**: 현재 실행 가능한 것 유지
- ⚠️ **과도기 테스트**: 최소 수정으로 복구 (4개만)
- 📚 **레거시 테스트**: 아카이브 (참고용)
- ❌ **중복 테스트**: 삭제

이 접근법으로 **테스트 커버리지를 유지하면서** 불필요한 작업을 최소화할 수 있습니다.

