# Rules 문서 인덱스

> **최신화 날짜**: 2026-01-03  
> **목적**: 모든 개발 규칙 및 가이드라인 문서의 인덱스

---

## 🚀 신규 개발자 시작하기

**이 프로젝트에 처음 온보딩하는 개발자라면 아래 순서대로 읽으세요:**

### 1단계: 필수 문서 읽기 (1시간) ⭐⭐⭐

1. **[00_CORE/01_PHILOSOPHY.md](./00_CORE/01_PHILOSOPHY.md)** - 핵심 개발 철학 이해
   - 8가지 개발 철학 (Data-Centric, Immutability-First, Type-Safety-First 등)
   - 불확정성 불허 원칙
   - 금지 사항

2. **[00_CORE/02_ARCHITECTURE_PRINCIPLES.md](./00_CORE/02_ARCHITECTURE_PRINCIPLES.md)** - 아키텍처 원칙 이해
   - Reference Layer 우회 금지 원칙
   - Factory vs Handler 패턴
   - Service 계층 원칙

3. **[01_TYPE_SAFETY/UUID_GUIDELINES.md](./01_TYPE_SAFETY/UUID_GUIDELINES.md)** - UUID 사용법 ⚠️ **가장 중요한 에러 방지**
   - `uuid_helper.py` 사용 필수
   - UUID 타입 구분 및 사용법
   - 자주 발생하는 에러 및 해결

### 2단계: 환경 설정 (30분)

```bash
# 데이터베이스 설정
psql -U postgres -d rpg_engine -f database/setup/mvp_schema.sql

# 의존성 설치
pip install -r requirements.txt

# 테스트 실행
python -m pytest tests/qa/ -v
```

### 3단계: 개발 시작

- 작업할 시스템의 가이드라인 확인 (`03_SYSTEMS/` 폴더)
- 관련 문서 읽기
- 개발 시작

**더 자세한 온보딩 가이드는 [docs/onboarding/README.md](../../onboarding/README.md) 참조**

---

## 📁 디렉토리 구조

```
docs/rules/
├── 00_CORE/                    # 핵심 철학 및 원칙 (최우선)
│   ├── 01_PHILOSOPHY.md
│   └── 02_ARCHITECTURE_PRINCIPLES.md
│
├── 01_TYPE_SAFETY/             # 타입 안전성 (우선순위 1)
│   ├── TYPE_SAFETY_GUIDELINES.md
│   ├── UUID_GUIDELINES.md
│   └── TRANSACTION_GUIDELINES.md
│
├── 02_DATABASE/                # 데이터베이스 (우선순위 2)
│   ├── DATABASE_SCHEMA_DESIGN.md
│   └── MIGRATION_GUIDELINES.md
│
├── 03_SYSTEMS/                 # 게임 시스템 (우선순위 3)
│   ├── EFFECT_CARRIER_GUIDELINES.md
│   ├── ABILITIES_SYSTEM_GUIDELINES.md
│   └── DIALOGUE_SYSTEM_GUIDELINES.md
│
├── 04_DEVELOPMENT/             # 개발 프로세스 (우선순위 4)
│   ├── CODING_CONVENTIONS.md
│   └── PROJECT_MANAGEMENT_WORKFLOW.md
│
└── 05_AGENT/                   # 에이전트 규칙 (우선순위 5)
    ├── AGENT_DOCUMENT_MANAGEMENT_V2.md (최신)
    ├── AGENT_DOCUMENT_MANAGEMENT_CRITICAL_REVIEW.md
    └── AGENT_DOCUMENT_MANAGEMENT.md (deprecated)
```

## 📋 문서 목록 (우선순위별)

### 우선순위 0: 핵심 철학 (필수 읽기)

1. **[00_CORE/01_PHILOSOPHY.md](./00_CORE/01_PHILOSOPHY.md)** ⭐⭐⭐ **최우선 필수**
   - 핵심 개발 철학
   - 불변 원칙
   - 금지 사항
   - 불확정성 불허 원칙

2. **[00_CORE/02_ARCHITECTURE_PRINCIPLES.md](./00_CORE/02_ARCHITECTURE_PRINCIPLES.md)** ⭐⭐ **아키텍처 설계 전 필수**
   - Reference Layer 우회 금지 원칙
   - Factory vs Handler 패턴 사용 원칙
   - Service 계층 원칙 (BaseGameplayService, IntegrityService, ActionService)
   - Manager/Repository 계층 원칙
   - mvp_schema.sql 참조 필수
   - Dialogue Manager 시스템 이해

3. **[00_CORE/03_ACTION_HANDLER_GUIDELINES.md](./00_CORE/03_ACTION_HANDLER_GUIDELINES.md)** ⭐⭐ **Action Handler 사용 전 필수**
   - ActionType 정의 및 카테고리화
   - Handler 작동 원리
   - 카테고리별 Handler 구조
   - 엔티티 특성 기반 성공 판정 시스템 (향후 구현)

### 우선순위 1: 타입 안전성

4. **[01_TYPE_SAFETY/TYPE_SAFETY_GUIDELINES.md](./01_TYPE_SAFETY/TYPE_SAFETY_GUIDELINES.md)** ⭐⭐ **타입 안전성 종합**
   - 타입 안전성 원칙
   - UUID, 트랜잭션, JSONB 타입 안전성
   - 가장 자주 발생하는 타입 에러

5. **[01_TYPE_SAFETY/UUID_GUIDELINES.md](./01_TYPE_SAFETY/UUID_GUIDELINES.md)** ⭐⭐ **UUID 사용 전 필수**
   - uuid_helper.py 사용 필수
   - UUID 타입 구분 및 사용법
   - JSONB 저장 시 주의사항
   - 자주 발생하는 에러 및 해결

6. **[01_TYPE_SAFETY/TRANSACTION_GUIDELINES.md](./01_TYPE_SAFETY/TRANSACTION_GUIDELINES.md)** ⭐ **트랜잭션 사용 전 필수**
   - 트랜잭션이 필요한 작업
   - 트랜잭션 데코레이터 사용법
   - 트랜잭션 범위 최소화

### 우선순위 2: 데이터베이스

7. **[02_DATABASE/DATABASE_SCHEMA_DESIGN.md](./02_DATABASE/DATABASE_SCHEMA_DESIGN.md)** ⭐⭐ **스키마 설계 전 필수**
   - mvp_schema.sql 참조 필수
   - 데이터베이스 스키마 설계 원칙
   - FK 설계 원칙
   - UUID 타입 사용
   - 인덱스 설계 원칙
   - JSONB 필드 설계

8. **[02_DATABASE/GAME_DATA_PRODUCTION_GUIDELINES.md](./02_DATABASE/GAME_DATA_PRODUCTION_GUIDELINES.md)** ⭐⭐ **게임 데이터 제작 전 필수**
   - YAML 파일로 게임 데이터 정의
   - UnifiedGameDataLoader 사용법
   - ID 명명 규칙 준수
   - 의존성 규칙
   - Factory 패턴 사용
   - mvp_schema.sql 참조 필수

9. **[02_DATABASE/MIGRATION_GUIDELINES.md](./02_DATABASE/MIGRATION_GUIDELINES.md)** ⭐ **마이그레이션 작성 전 필수**
   - 마이그레이션 작성 규칙
   - Idempotent 마이그레이션
   - 롤백 계획

### 우선순위 3: 게임 시스템

10. **[03_SYSTEMS/EFFECT_CARRIER_GUIDELINES.md](./03_SYSTEMS/EFFECT_CARRIER_GUIDELINES.md)** ⭐⭐ **Effect Carrier 사용 전 필수**
   - Effect Carrier 시스템 개념
   - 두 가지 연결 방식 (아이템 속성 vs 적용 중인 상태)
   - Effect Carrier Manager 사용법
   - API 엔드포인트 설계

11. **[03_SYSTEMS/TIME_SYSTEM_GUIDELINES.md](./03_SYSTEMS/TIME_SYSTEM_GUIDELINES.md)** ⭐⭐ **Time System 사용 전 필수**
   - 게임 시간 관리 (GameTime, TimeScale, TimePeriod)
   - 이벤트 스케줄링
   - 세션 상태 저장/로드
   - mvp_schema.sql 참조 필수

12. **[03_SYSTEMS/NPC_BEHAVIOR_GUIDELINES.md](./03_SYSTEMS/NPC_BEHAVIOR_GUIDELINES.md)** ⭐⭐ **NPC Behavior System 사용 전 필수**
    - NPC 자동 행동 시스템
    - 시간대별 행동 패턴 실행
    - 행동 스케줄 데이터 구조
    - mvp_schema.sql 참조 필수

13. **[03_SYSTEMS/ABILITIES_SYSTEM_GUIDELINES.md](./03_SYSTEMS/ABILITIES_SYSTEM_GUIDELINES.md)** ⭐⭐ **스킬/주문 시스템 사용 전 필수**
    - 스킬/주문 시스템 구조
    - Effect Carrier와의 차이점
    - 스킬/주문 조회 방법
    - API 엔드포인트 설계

14. **[03_SYSTEMS/DIALOGUE_SYSTEM_GUIDELINES.md](./03_SYSTEMS/DIALOGUE_SYSTEM_GUIDELINES.md)** ⭐⭐ **Dialogue Manager 사용 전 필수**
    - Dialogue Manager 시스템 이해
    - mvp_schema.sql 참조 필수
    - ID 변환 방법 (불확정성 불허 원칙)
    - 사용법 및 예시 코드
    - 자주 발생하는 에러 및 해결

15. **[03_SYSTEMS/QUEST_SYSTEM_GUIDELINES.md](./03_SYSTEMS/QUEST_SYSTEM_GUIDELINES.md)** ⚠️ **Placeholder - 구현 예정**
    - 퀘스트 시스템 가이드라인 (구현 예정)
    - 참고: `04_DEVELOPMENT/UI_REDESIGN_TODO.md`

16. **[03_SYSTEMS/JOURNAL_SYSTEM_GUIDELINES.md](./03_SYSTEMS/JOURNAL_SYSTEM_GUIDELINES.md)** ⚠️ **Placeholder - 구현 예정**
    - 저널 시스템 가이드라인 (구현 예정)
    - 참고: `04_DEVELOPMENT/UI_REDESIGN_TODO.md`

17. **[03_SYSTEMS/MAP_SYSTEM_GUIDELINES.md](./03_SYSTEMS/MAP_SYSTEM_GUIDELINES.md)** ⚠️ **Placeholder - 구현 예정**
    - 맵 시스템 가이드라인 (구현 예정)
    - 참고: `04_DEVELOPMENT/UI_REDESIGN_TODO.md`

18. **[03_SYSTEMS/EXPLORATION_SYSTEM_GUIDELINES.md](./03_SYSTEMS/EXPLORATION_SYSTEM_GUIDELINES.md)** ⚠️ **Placeholder - 구현 예정**
    - 탐험 시스템 가이드라인 (구현 예정)
    - 참고: `04_DEVELOPMENT/UI_REDESIGN_TODO.md`

### 우선순위 4: 개발 프로세스

19. **[04_DEVELOPMENT/TESTING_GUIDELINES.md](./04_DEVELOPMENT/TESTING_GUIDELINES.md)** ⭐⭐ **테스트 작성 전 필수**
    - pytest 기반 테스트 작성 가이드
    - 공통 픽스처 사용법
    - 테스트 카테고리 (Unit, Integration, Scenario, QA)
    - 커버리지 80% 이상 요구
    - 비동기 테스트 작성법

20. **[04_DEVELOPMENT/ERROR_HANDLING_GUIDELINES.md](./04_DEVELOPMENT/ERROR_HANDLING_GUIDELINES.md)** ⭐⭐ **에러 처리 작성 전 필수**
    - 계층별 에러 처리 시스템 사용법
    - Manager 계층: common/utils/error_handler.py
    - Service 계층: app/common/decorators/error_handler.py
    - System 계층: common/error_handling/error_types.py
    - 에러 처리 원칙 및 패턴

21. **[04_DEVELOPMENT/DEVELOPMENT_WORKFLOW_GUIDE.md](./04_DEVELOPMENT/DEVELOPMENT_WORKFLOW_GUIDE.md)** ⭐⭐ **신규 개발자 필수 - 개발 워크플로우**
    - 새로운 기능 추가하기
    - 기존 기능 수정하기
    - 데이터베이스 스키마 변경하기
    - API 엔드포인트 추가하기
    - 테스트 작성하기
    - 코드 리뷰 체크리스트

22. **[04_DEVELOPMENT/CODING_CONVENTIONS.md](./04_DEVELOPMENT/CODING_CONVENTIONS.md)** ⭐ **코딩 컨벤션**
    - 코딩 정책
    - 품질 기준
    - 아키텍처 설계 방법론

23. **[04_DEVELOPMENT/UI_REDESIGN_TODO.md](./04_DEVELOPMENT/UI_REDESIGN_TODO.md)** ⭐⭐ **UI 리디자인 구현 전 필수**
    - UI 리디자인 구현 TODO 목록
    - 백엔드 API 엔드포인트 추가
    - Service Layer 추가
    - 프론트엔드 컴포넌트 구현
    - 데이터베이스 스키마 추가
    - 참고: `docs/design/UI_REDESIGN_BG3_STYLE.md`

24. **[04_DEVELOPMENT/PROJECT_MANAGEMENT_WORKFLOW.md](./04_DEVELOPMENT/PROJECT_MANAGEMENT_WORKFLOW.md)** ⭐ **프로젝트 관리**
    - 프로젝트 관리 워크플로우
    - 작업 추적
    - 문서 관리

### 우선순위 5: 에이전트 규칙

25. **[05_AGENT/AGENT_DOCUMENT_MANAGEMENT_V2.md](./05_AGENT/AGENT_DOCUMENT_MANAGEMENT_V2.md)** ⭐⭐ **에이전트 필수 - 프로젝트 문서 관리**
   - 단일 문서 기반 프로젝트 관리
   - 단순한 워크플로우
   - 체크리스트 기반 상태 관리

26. **[05_AGENT/AGENT_DOCUMENT_MANAGEMENT_CRITICAL_REVIEW.md](./05_AGENT/AGENT_DOCUMENT_MANAGEMENT_CRITICAL_REVIEW.md)** **참고용**
   - 기존 규칙의 문제점 분석
   - 개선 방안 제시

27. **[05_AGENT/AGENT_DOCUMENT_MANAGEMENT.md](./05_AGENT/AGENT_DOCUMENT_MANAGEMENT.md)** ⚠️ **DEPRECATED**
   - 더 이상 사용되지 않음
   - 참고용으로만 보관
    - 에이전트 문서 관리 규칙
    - 문서 생성 및 업데이트 규칙

## 🚀 빠른 시작 가이드

### 새로운 기능 개발 전

1. **필수 읽기 (우선순위 0)**:
   - `00_CORE/01_PHILOSOPHY.md`: 핵심 개발 철학 이해
   - `00_CORE/02_ARCHITECTURE_PRINCIPLES.md`: 아키텍처 설계 원칙 이해

2. **타입 안전성 (우선순위 1)**:
   - `01_TYPE_SAFETY/TYPE_SAFETY_GUIDELINES.md`: 타입 안전성 원칙 이해
   - `01_TYPE_SAFETY/UUID_GUIDELINES.md`: UUID 사용법 (uuid_helper.py 필수)
   - `01_TYPE_SAFETY/TRANSACTION_GUIDELINES.md`: 트랜잭션 사용법

3. **개발 워크플로우 (우선순위 2)**:
   - 새로운 기능 추가 시: `04_DEVELOPMENT/DEVELOPMENT_WORKFLOW_GUIDE.md` ⭐⭐ **신규 개발자 필수**
   - 기존 기능 수정 시: `04_DEVELOPMENT/DEVELOPMENT_WORKFLOW_GUIDE.md`
   - 데이터베이스 스키마 변경 시: `04_DEVELOPMENT/DEVELOPMENT_WORKFLOW_GUIDE.md`
   - API 엔드포인트 추가 시: `04_DEVELOPMENT/DEVELOPMENT_WORKFLOW_GUIDE.md`

4. **시스템별 가이드라인 (우선순위 3)**:
   - 스키마 설계 시: `02_DATABASE/DATABASE_SCHEMA_DESIGN.md` (mvp_schema.sql 참조 필수)
   - 게임 데이터 제작 시: `02_DATABASE/GAME_DATA_PRODUCTION_GUIDELINES.md` (mvp_schema.sql 참조 필수)
   - Service 계층 개발 시: `00_CORE/02_ARCHITECTURE_PRINCIPLES.md` (Service 계층 원칙)
   - Action Handler 사용 시: `00_CORE/03_ACTION_HANDLER_GUIDELINES.md` (Action Handler 시스템)
   - 데이터 삭제 전: `00_CORE/02_ARCHITECTURE_PRINCIPLES.md` (IntegrityService 사용)
   - 상태 전이 검증: `00_CORE/02_ARCHITECTURE_PRINCIPLES.md` (ActionService 사용)
   - Effect Carrier 사용 시: `03_SYSTEMS/EFFECT_CARRIER_GUIDELINES.md`
   - Time System 사용 시: `03_SYSTEMS/TIME_SYSTEM_GUIDELINES.md` (mvp_schema.sql 참조 필수)
   - NPC Behavior System 사용 시: `03_SYSTEMS/NPC_BEHAVIOR_GUIDELINES.md` (mvp_schema.sql 참조 필수)
   - 스킬/주문 사용 시: `03_SYSTEMS/ABILITIES_SYSTEM_GUIDELINES.md`
   - Dialogue Manager 사용 시: `03_SYSTEMS/DIALOGUE_SYSTEM_GUIDELINES.md` (mvp_schema.sql 참조 필수)

5. **테스트 작성 시 (우선순위 4)**:
   - 테스트 작성 전: `04_DEVELOPMENT/TESTING_GUIDELINES.md` (커버리지 80% 이상 필수)

6. **에러 처리 작성 시 (우선순위 4)**:
   - 에러 처리 작성 전: `04_DEVELOPMENT/ERROR_HANDLING_GUIDELINES.md` (계층별 적절한 시스템 사용)

7. **UI 리디자인 구현 시 (우선순위 4)**:
   - UI 리디자인 구현 전: `04_DEVELOPMENT/UI_REDESIGN_TODO.md` (전체 TODO 목록 확인)
   - 관련 시스템 가이드라인 확인 (Quest, Journal, Map, Exploration)

### 가장 자주 발생하는 에러 방지

**⚠️ 설계 원칙에 대한 이해 없이 개발하면 오류 덩어리가 됩니다.**

1. **UUID 타입 혼용 에러** (가장 빈번)
   - 해결: `app/common/utils/uuid_helper.py` 함수 사용 필수
   - 참고: `01_TYPE_SAFETY/UUID_GUIDELINES.md`

2. **트랜잭션 범위 오류**
   - 해결: `@with_transaction` 데코레이터 사용
   - 참고: `01_TYPE_SAFETY/TRANSACTION_GUIDELINES.md`

3. **JSONB 직렬화 실패**
   - 해결: UUID를 문자열로 변환 (`normalize_uuid()`)
   - 참고: `01_TYPE_SAFETY/UUID_GUIDELINES.md`

4. **추측 로직 에러**
   - 해결: 명시적 처리 및 검증
   - 참고: `00_CORE/01_PHILOSOPHY.md` (불확정성 불허 원칙)

5. **스키마 불일치 에러**
   - 해결: `database/setup/mvp_schema.sql` 참조 필수
   - 참고: `02_DATABASE/DATABASE_SCHEMA_DESIGN.md`, `02_DATABASE/GAME_DATA_PRODUCTION_GUIDELINES.md`, `03_SYSTEMS/DIALOGUE_SYSTEM_GUIDELINES.md`

6. **게임 데이터 제작 에러**
   - 해결: ID 명명 규칙 준수, 의존성 확인, YAML 구조 확인
   - 참고: `02_DATABASE/GAME_DATA_PRODUCTION_GUIDELINES.md`

## 📚 문서 간 관계

```
00_CORE/01_PHILOSOPHY.md (최상위)
    ├── 00_CORE/02_ARCHITECTURE_PRINCIPLES.md
    │   ├── 02_DATABASE/DATABASE_SCHEMA_DESIGN.md
    │   │   ├── 02_DATABASE/GAME_DATA_PRODUCTION_GUIDELINES.md
    │   │   │   └── database/game_data/unified_loader.py (필수 참조)
    │   │   └── 02_DATABASE/MIGRATION_GUIDELINES.md
    │   └── 03_SYSTEMS/DIALOGUE_SYSTEM_GUIDELINES.md
    ├── 01_TYPE_SAFETY/TYPE_SAFETY_GUIDELINES.md
    │   ├── 01_TYPE_SAFETY/UUID_GUIDELINES.md
    │   │   └── app/common/utils/uuid_helper.py (필수 참조)
    │   └── 01_TYPE_SAFETY/TRANSACTION_GUIDELINES.md
    ├── 03_SYSTEMS/EFFECT_CARRIER_GUIDELINES.md
    └── 03_SYSTEMS/ABILITIES_SYSTEM_GUIDELINES.md
```

## ⚠️ 중요 경고

### 필수 참조 파일

1. **`app/common/utils/uuid_helper.py`**: 모든 UUID 변환/비교 시 필수 사용
2. **`database/setup/mvp_schema.sql`**: 모든 데이터베이스 관련 작업 시 필수 참조

### 개발 전 체크리스트

개발 전 반드시:
1. `00_CORE/01_PHILOSOPHY.md` 읽기
2. `00_CORE/02_ARCHITECTURE_PRINCIPLES.md` 읽기
3. 관련 시스템 가이드라인 읽기
4. 타입 안전성 가이드라인 확인
5. `mvp_schema.sql` 참조 (데이터베이스 관련 작업 시)
6. `uuid_helper.py` 사용 (UUID 관련 작업 시)
7. 체크리스트 확인

## 🔄 문서 업데이트 규칙

1. **새로운 가이드라인 추가 시**: 이 README에 추가
2. **기존 문서 수정 시**: 최신화 날짜 업데이트
3. **상호 참조 추가**: 관련 문서 간 링크 추가
4. **중복 제거**: 통합 가능한 문서는 통합

## 📋 온보딩 체크리스트

신규 개발자 온보딩 가능 여부를 검토한 결과는 [ONBOARDING_CHECKLIST.md](./ONBOARDING_CHECKLIST.md)를 참조하세요.

## 📖 추가 참고 자료

- **아키텍처 가이드**: `docs/architecture/08_architecture_guide.md`
- **아키텍처 토론**: `docs/architecture/ARCHITECTURE_DISCUSSION.md`
- **데이터베이스 스키마**: `database/setup/mvp_schema.sql` ⭐ **필수 참조**
- **UUID 헬퍼**: `app/common/utils/uuid_helper.py` ⭐ **필수 사용**
- **게임 데이터 로더**: `database/game_data/unified_loader.py` ⭐ **게임 데이터 제작 시 필수**
- **게임 데이터 정의**: `database/game_data/data_definitions/` ⭐ **YAML 파일 구조 참조**
