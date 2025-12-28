# Legacy Tests (아카이브)

> **아카이브 날짜**: 2025-10-20  
> **이유**: 아키텍처 변경 (Factory 패턴 → Repository 패턴, 3-tier → 2-tier)

---

## ⚠️ 실행 불가 경고

이 디렉토리의 테스트들은 **구 아키텍처**를 전제로 작성되어 **현재 실행할 수 없습니다**.

### 주요 변경 사항

#### 1. 스키마 구조 변경
```
[이전] game_data → reference_layer → runtime_data (3-tier)
[현재] game_data → runtime_data (2-tier, 직접 연결)
```

#### 2. Manager API 변경
```python
# 이전 (Legacy)
entity = await entity_manager.create_entity(
    name="Test Player",
    entity_type=EntityType.PLAYER,
    properties={"health": 100}
)

# 현재 (Active)
result = await entity_manager.create_entity(
    static_entity_id="NPC_VILLAGER_001",  # DB 템플릿 참조
    session_id=session_id,
    custom_properties={"health": 150}
)
```

#### 3. Repository 초기화 변경
```python
# 이전 (Legacy)
repo = GameDataRepository()

# 현재 (Active)
db = DatabaseConnection()
await db.initialize()
repo = GameDataRepository(db)
```

---

## 📚 아카이브 목적

이 테스트들은 다음 목적으로 보관됩니다:

### 1. 테스트 시나리오 참고
- 엣지 케이스 발견 사례
- 테스트 데이터 구조 아이디어
- 검증 로직 패턴

### 2. 마이그레이션 가이드
- 구 API → 신 API 변환 예시
- 리팩토링 시 참고 자료

### 3. 히스토리 추적
- 프로젝트 진화 과정 기록
- 설계 결정 배경 이해

---

## 📂 디렉토리 구조

```
legacy/
├── integration/          # 통합 테스트 (12개)
│   ├── test_simple_db_integration.py        # 기본 CRUD (수정 예정)
│   ├── test_mvp_goals.py                    # MVP 목표 검증 (수정 예정)
│   ├── test_abstraction_principle_compliance.py
│   ├── test_manager_schema_compliance.py
│   └── test_effect_carrier_system.py        # Effect Carrier (미구현)
├── scenarios/            # 시나리오 테스트 (11개)
│   ├── basic_entity_creation.py             # 기본 엔티티 생성 (수정 예정)
│   ├── integrated_gameplay_scenarios.py     # 통합 게임플레이 (수정 예정)
│   ├── scenario_test.py                     # Factory 패턴
│   ├── class_based_scenario_test.py         # 3-tier 구조
│   └── modular_scenario_test.py             # 모듈화 구조 (참고용)
├── simulation/           # 시뮬레이션 테스트 (1개)
│   └── test_village_simulation_integration.py
├── unit/                 # 단위 테스트 (4개)
│   ├── test_entity_manager.py               # 구 API
│   ├── test_cell_manager.py                 # 구 API
│   ├── test_game_manager.py
│   └── test_effect_carrier_manager.py
├── setup_test_data.py    # 테스트 데이터 설정 (구버전)
└── test_mvp_compatibility.py  # MVP 호환성 검증
```

---

## 🔄 마이그레이션 가이드

### Step 1: 정적 템플릿 준비

**이전**: 코드에서 엔티티 생성
```python
entity = Entity(
    name="Test NPC",
    entity_type=EntityType.NPC,
    properties={"health": 100}
)
```

**현재**: DB에 템플릿 삽입
```sql
INSERT INTO game_data.entities (entity_id, entity_type, entity_name, base_stats)
VALUES ('NPC_TEST_001', 'npc', 'Test NPC', '{"health": 100}'::jsonb);
```

### Step 2: Manager API 업데이트

**이전**: 직접 생성
```python
entity = await entity_manager.create_entity(
    name="Test NPC",
    entity_type=EntityType.NPC
)
```

**현재**: 템플릿 기반 인스턴스화
```python
result = await entity_manager.create_entity(
    static_entity_id="NPC_TEST_001",
    session_id=session_id
)
entity_id = result.entity_id
```

### Step 3: Repository 초기화

**이전**: 글로벌 싱글톤
```python
repo = GameDataRepository()
```

**현재**: DB 연결 주입
```python
@pytest_asyncio.fixture
async def repositories(db_connection):
    return {
        'game_data_repo': GameDataRepository(db_connection),
        'runtime_data_repo': RuntimeDataRepository(db_connection),
        'reference_layer_repo': ReferenceLayerRepository(db_connection)
    }
```

---

## 📋 수정 예정 파일 (향후 Active로 이동)

다음 파일들은 정적 템플릿 데이터 준비 후 수정하여 `tests/active/`로 이동 예정:

### 우선순위 높음
1. `integration/test_simple_db_integration.py` - 기본 CRUD 검증
2. `integration/test_mvp_goals.py` - MVP 수용 기준 검증

### 우선순위 중간
3. `scenarios/basic_entity_creation.py` - 엔티티 생성 시나리오
4. `scenarios/integrated_gameplay_scenarios.py` - 통합 게임플레이

### 우선순위 낮음
5. `scenarios/test_action_execution_scenario.py` - 액션 실행
6. `scenarios/test_dialogue_interaction_scenario.py` - 대화 상호작용
7. `scenarios/test_village_simulation_db.py` - 마을 시뮬레이션

---

## ✨ 참고 가치 있는 테스트

### 1. 모듈화 구조
- `scenarios/modular_scenario_test.py`
- 테스트를 작은 단위로 분리한 좋은 예시

### 2. 통합 게임플레이
- `scenarios/integrated_gameplay_scenarios.py`
- 여러 시스템이 연동된 복합 시나리오

### 3. Effect Carrier 시스템
- `scenarios/effect_carrier_scenarios.py`
- 아직 미구현이지만 향후 참고 가능

---

## 🚫 삭제된 테스트 (Deprecated)

다음 테스트들은 `tests/deprecated/`로 이동되어 곧 삭제 예정:

- `database_test.py` - 중복
- `test_simple_db_connection.py` - 중복
- `test_db_connection_debug.py` - 디버깅 스크립트
- `fix_triggers.py` - 일회성 수정 스크립트
- `database_integrity_test.py` - 구버전 무결성 테스트
- 기타 중복/무의미 테스트 6개

---

## 📞 문의

이 테스트들을 마이그레이션하거나 참고하고 싶다면:
1. `docs/TEST_REFACTORING_DECISION.md` 참조
2. `tests/active/conftest.py`의 최신 픽스처 사용
3. `database/setup/test_templates.sql`의 정적 템플릿 데이터 활용

---

**마지막 업데이트**: 2025-10-20  
**다음 검토 예정**: 정적 템플릿 데이터 준비 완료 시

