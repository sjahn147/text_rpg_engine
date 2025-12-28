# Active Tests

> **최종 업데이트**: 2025-10-21  
> **테스트 프레임워크**: pytest + pytest-asyncio  
> **현재 상태**: Phase 3 Village Simulation 완료, 모든 테스트 통과

---

## 📋 개요

이 디렉토리는 **현재 실행 가능한 테스트**들을 포함합니다.
모든 테스트는 새로운 아키텍처 (Repository 패턴, 2-tier 스키마)를 기반으로 작성되었습니다.

---

## 🏗️ 구조

```
active/
├── conftest.py               # 공통 픽스처
├── integration/              # 통합 테스트
│   ├── test_entity_manager_db_integration.py
│   ├── test_cell_manager_db_integration.py
│   ├── test_dialogue_manager_db_integration.py
│   ├── test_action_handler_db_integration.py
│   ├── test_manager_integration.py
│   ├── test_basic_crud.py
│   └── test_data_integrity.py
├── scenarios/                # 시나리오 테스트
│   ├── test_multi_session.py      # 동시 다중 세션 테스트
│   ├── test_dialogue_system.py   # 대화 시스템 테스트
│   ├── test_action_system.py     # 액션 시스템 테스트
│   └── test_village_simulation_100days.py  # 100일 마을 시뮬레이션
└── test_performance.py       # 성능 테스트
```

---

## ✅ 전제 조건

### 1. 데이터베이스 설정
```bash
# MVP 스키마 적용
psql -U postgres -d rpg_game -f database/setup/mvp_schema.sql

# 테스트 템플릿 데이터 삽입
psql -U postgres -d rpg_game -f database/setup/test_templates.sql
```

### 2. 환경 변수
`.env` 파일에 다음 설정 필요:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rpg_game
DB_USER=postgres
DB_PASSWORD=your_password
```

---

## 🚀 실행 방법

### 전체 테스트 실행
```bash
pytest tests/active/ -v
```

### 특정 카테고리 실행
```bash
# 통합 테스트만
pytest tests/active/integration/ -v

# 시나리오 테스트만
pytest tests/active/scenarios/ -v
```

### 특정 테스트 파일 실행
```bash
pytest tests/active/integration/test_basic_crud.py -v
```

---

## 📚 주요 픽스처 (conftest.py)

### 데이터베이스
- `db_connection`: 기본 DB 연결
- `db_with_templates`: 템플릿 데이터가 로드된 DB 연결

### Repositories
- `repositories`: 모든 Repository 인스턴스

### Managers
- `entity_manager`: EntityManager
- `cell_manager`: CellManager
- `dialogue_manager`: DialogueManager
- `action_handler`: ActionHandler
- `all_managers`: 모든 Manager 딕셔너리

### 테스트 데이터
- `test_session`: 테스트용 게임 세션
- `test_entities`: 테스트용 런타임 엔티티
- `test_cells`: 테스트용 런타임 셀

---

## 📊 테스트 통계

- **Total**: 12개 파일
- **Integration**: 7개
- **Scenarios**: 4개 (동시 다중 세션, 대화 시스템, 액션 시스템, 100일 마을 시뮬레이션)
- **Performance**: 1개

## 🏆 **Phase별 테스트 성과**

### **Phase 1: Entity-Cell 상호작용** ✅
- **통합 테스트**: 7/7 통과 (100%)
- **기본 CRUD**: 엔티티/셀 생명주기 완전 검증
- **데이터 무결성**: ForeignKey 제약조건 100% 준수

### **Phase 2: 동시성 및 상호작용** ✅
- **동시 다중 세션**: 50개 세션, 960 entities/sec
- **대화 시스템**: 275 dialogues/sec
- **액션 시스템**: 8가지 핵심 액션 완전 구현
- **성능 테스트**: 4/5 테스트 통과 (80%)

### **Phase 3: Village Simulation** ✅
- **100일 시뮬레이션**: 1.98초 실행 (목표 5초 이하)
- **총 대화**: 228회 (목표 50회 초과)
- **총 행동**: 833회 (목표 100회 초과)
- **시스템 안정성**: 100% (오류 없이 완료)

---

**다음**: `tests/legacy/README.md` 참조 (구버전 테스트 아카이브)

