# 🚀 RPG Engine 온보딩 가이드

> **최신화 날짜**: 2026-01-01  
> **목적**: 프로젝트에 처음 진입하는 개발자(에이전트)가 빠르게 시작할 수 있도록 지원

---

## ⚠️ 중요: 문서화 정책

**이 프로젝트는 문서를 지저분하게 늘리지 않습니다.**

### 📋 문서화 원칙

1. **중요 문서를 계속 업데이트하는 방식**
   - 새로운 문서를 만들기보다 기존 중요 문서를 업데이트
   - 중복 문서 생성 금지
   - Deprecated 문서는 `docs/archive/`로 이동

2. **CHANGELOG는 항상 최신화**
   - **`docs/changelog/CHANGELOG.md`**는 프로젝트의 모든 변경사항을 기록하는 단일 소스
   - 모든 주요 변경사항은 CHANGELOG에 기록
   - 새로운 기능, 버그 수정, 문서 업데이트 모두 포함
   - **개발 시작 전 반드시 CHANGELOG 확인!**

3. **핵심 문서만 유지**
   - 온보딩: 이 문서 (`docs/onboarding/README.md`)
   - 변경 이력: `docs/changelog/CHANGELOG.md` ⭐ **항상 최신 상태**
   - 개발 규칙: `docs/rules/코딩 컨벤션 및 품질 가이드.md`
   - 아키텍처: `docs/architecture/` 폴더의 핵심 문서들

---

## 📖 필수 읽기 순서 (2-3시간)

### Step 1: 프로젝트 현황 파악 (30분)

**1. CHANGELOG 확인** ⭐⭐⭐ **가장 먼저 읽을 것!**
```
docs/changelog/CHANGELOG.md
```
- 프로젝트의 최신 상태를 파악하는 가장 중요한 문서
- 모든 주요 변경사항, 완료된 작업, 현재 진행 상황 포함
- **항상 최신화되므로 여기서 시작하세요!**

**2. 프로젝트 개요**
```
readme.md
```
- 프로젝트 전체 개요
- 기술 스택, 디렉토리 구조

### Step 2: 개발 철학 및 규칙 이해 (45분)

**1. 코딩 컨벤션** ⭐⭐⭐
```
docs/rules/코딩 컨벤션 및 품질 가이드.md
```
- 8가지 개발 철학 (Data-Centric, Immutability-First 등)
- DO / DO NOT 원칙
- 아키텍처 설계 방법론
- **반드시 이해하고 준수해야 함**

**2. 개발 가이드라인**
```
docs/development/
├── MIGRATION_GUIDELINES.md      # 데이터베이스 마이그레이션 규칙
├── TRANSACTION_GUIDELINES.md    # 트랜잭션 사용 규칙
├── UUID_USAGE_GUIDELINES.md    # UUID 처리 가이드라인
└── FRONTEND_ARCHITECTURE.md    # 프론트엔드 아키텍처
```

### Step 3: 데이터베이스 아키텍처 이해 (60분) ⭐ 가장 중요!

**1. 스키마 정의**
```
database/setup/mvp_schema.sql ⭐⭐⭐
```
- 3-Layer 구조 완전 이해 필수
- game_data: 정적 템플릿 (불변)
- runtime_data: 세션별 런타임 데이터
- reference_layer: 관계 매핑

**2. UUID 처리 가이드라인**
```
docs/UUID_HANDLING_GUIDELINES.md
```
- UUID 객체 vs 문자열 사용 규칙
- JSONB 필드 내 UUID 저장 방식
- 헬퍼 함수 사용법

### Step 4: 핵심 코드 이해 (45분)

**1. Manager 클래스들**
```
app/managers/
├── entity_manager.py      # 엔티티 관리
├── cell_manager.py        # 셀 관리
└── ...
```

**2. 핵심 유틸리티**
```
app/common/utils/
├── uuid_helper.py         # UUID 처리 헬퍼
└── jsonb_handler.py       # JSONB 파싱
```

---

## 🏗️ 핵심 아키텍처

### 3-Layer 데이터베이스 구조

```
┌─────────────────────────────────────────┐
│ game_data (정적 템플릿 - 불변)          │
│ - entities, world_cells, items 등      │
│ - entity_id (VARCHAR PK)                │
└─────────────────────────────────────────┘
              ↓ FK: game_entity_id
┌─────────────────────────────────────────┐
│ runtime_data (런타임 참조 - 세션별)     │
│ - runtime_entities, runtime_cells      │
│ - runtime_entity_id (UUID PK)           │
│ - session_id (FK → active_sessions)     │
└─────────────────────────────────────────┘
              ↓ FK: runtime_entity_id
┌─────────────────────────────────────────┐
│ runtime_data (가변 상태 - 세션별)       │
│ - entity_states, object_states          │
│ - state_id (UUID PK)                    │
│ - current_stats, inventory (JSONB)     │
└─────────────────────────────────────────┘
              ↓ 매핑
┌─────────────────────────────────────────┐
│ reference_layer (관계 매핑)              │
│ - entity_references, object_references  │
│ - game ↔ runtime 매핑                   │
└─────────────────────────────────────────┘
```

### 디렉토리 구조

```
rpg_engine/
├── app/
│   ├── managers/          # 비즈니스 로직 (Entity, Cell 등)
│   ├── handlers/          # 액션 핸들러
│   ├── services/         # 서비스 레이어
│   ├── api/              # API 라우트
│   ├── ui/               # 프론트엔드 (React + TypeScript)
│   └── common/           # 공통 유틸리티
│
├── database/
│   ├── setup/
│   │   └── mvp_schema.sql ⭐⭐⭐ 가장 중요!
│   ├── migrations/       # 마이그레이션 스크립트
│   └── connection.py     # DB 연결 관리
│
├── tests/
│   ├── qa/               # QA 테스트 (40개 테스트 케이스)
│   └── ...
│
└── docs/
    ├── changelog/        # ⭐ CHANGELOG.md (항상 최신!)
    ├── onboarding/      # 이 문서
    ├── rules/            # 개발 규칙
    ├── development/       # 개발 가이드라인
    └── architecture/     # 아키텍처 문서
```

---

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 데이터베이스 초기화
psql -U postgres -d rpg_engine -f database/setup/mvp_schema.sql

# 의존성 설치
pip install -r requirements.txt

# 테스트 실행
python -m pytest tests/qa/ -v
```

### 2. 핵심 명령어

```bash
# 전체 테스트 실행
python -m pytest tests/qa/ -v

# 특정 테스트 실행
python -m pytest tests/qa/test_game_start_flow.py -v

# 타입 체크
mypy app/ --ignore-missing-imports

# 코드 포맷팅
black app/ tests/
```

### 3. 개발 워크플로우

1. **CHANGELOG 확인** - 최신 상태 파악
2. **관련 문서 읽기** - 개발 규칙 및 가이드라인 확인
3. **테스트 작성** - TDD 방식
4. **구현** - 코딩 컨벤션 준수
5. **테스트 통과** - 모든 테스트 확인
6. **CHANGELOG 업데이트** - 변경사항 기록

---

## 📋 현재 프로젝트 상태 (2026-01-01)

### ✅ 완료된 주요 작업

- **Phase 1-3**: 완료 (Entity-Cell 상호작용, Dialogue & Action 시스템, Village Simulation)
- **Phase 4**: World Editor 기본 구조 완성 (80% 완료)
- **데이터베이스 아키텍처**: 3계층 구조 완성 (40개 테이블)
- **오브젝트 상호작용 시스템**: 완전히 수정 및 개선 완료
- **UUID 처리 표준화**: 헬퍼 함수 및 가이드라인 완성
- **QA 테스트 시스템**: 40개 테스트 케이스 구축 완료
- **데이터 무결성 개선**: JSONB 검증, SSOT 강제, ENUM 타입 도입 완료

### 🚧 진행 중인 작업

- **Phase 4+**: World Editor 완성, UI System, TimeSystem, NPC AI
- **텍스트 어드벤처 게임 GUI**: Novel game adventure 스타일 인터페이스

**자세한 내용은 `docs/changelog/CHANGELOG.md` 참조**

---

## ⚠️ 중요한 주의사항

### 1. UUID 처리

- **DB 컬럼**: UUID 객체 사용 (asyncpg 자동 변환)
- **JSONB 필드**: 문자열로 저장
- **API 경계**: 문자열로 변환
- **헬퍼 함수 사용**: `app/common/utils/uuid_helper.py`

### 2. 데이터베이스 쓰기 작업

- **개발 정의서에 없는 DB 쓰기 작업 시 반드시 사용자 컨펌 요청**
- 백업 없이 위험한 작업 금지
- 코딩 컨벤션 8번 원칙 준수

### 3. 문서화 정책

- **새 문서 생성 금지** - 기존 중요 문서 업데이트
- **CHANGELOG 항상 최신화** - 모든 변경사항 기록
- **중복 문서 제거** - Deprecated 문서는 archive로 이동

### 4. 테스트

- **TDD 방식 준수** - 테스트 먼저 작성
- **QA 테스트 실행** - `tests/qa/` 폴더의 테스트들
- **커버리지 80% 이상 유지**

---

## 📚 핵심 문서 참조

### 항상 확인할 문서

1. **`docs/changelog/CHANGELOG.md`** ⭐⭐⭐
   - 프로젝트의 모든 변경사항
   - 항상 최신 상태
   - 개발 시작 전 반드시 확인

2. **`docs/rules/코딩 컨벤션 및 품질 가이드.md`** ⭐⭐⭐
   - 개발 철학 및 규칙
   - 반드시 준수

3. **`database/setup/mvp_schema.sql`** ⭐⭐⭐
   - 데이터베이스 스키마
   - 3-Layer 구조 이해 필수

### 필요시 참조

- `docs/development/` - 개발 가이드라인
- `docs/architecture/` - 아키텍처 문서
- `docs/UUID_HANDLING_GUIDELINES.md` - UUID 처리 가이드
- `docs/OBJECT_INTERACTION_FAILURE_ANALYSIS.md` - 오브젝트 상호작용 분석

---

## 🎯 온보딩 체크리스트

### Day 1: 이해 (2-3시간)

- [ ] `docs/changelog/CHANGELOG.md` 정독 ⭐ **가장 먼저!**
- [ ] `docs/rules/코딩 컨벤션 및 품질 가이드.md` 정독
- [ ] `database/setup/mvp_schema.sql` 정독 및 3-Layer 구조 이해
- [ ] `readme.md` 프로젝트 개요 파악
- [ ] 핵심 Manager 클래스 코드 리뷰 (`app/managers/`)

### Day 1: 검증 (1시간)

- [ ] 모든 테스트 실행 및 통과 확인
```bash
python -m pytest tests/qa/ -v
```
- [ ] 데이터베이스 스키마 확인
```bash
psql -U postgres -d rpg_engine -c "\dt game_data.*"
psql -U postgres -d rpg_engine -c "\dt runtime_data.*"
```

### Day 2: 첫 작업 (3-4시간)

- [ ] CHANGELOG 확인하여 현재 진행 중인 작업 파악
- [ ] 관련 문서 읽기
- [ ] 테스트 작성 (TDD)
- [ ] 구현
- [ ] **CHANGELOG 업데이트** ⭐ **반드시!**

---

## 📞 도움 요청

문제 발생 시:

1. **CHANGELOG 확인** - 최근 변경사항 확인
2. **관련 문서 확인** - `docs/development/`, `docs/architecture/`
3. **테스트 코드 확인** - `tests/qa/` 폴더
4. **스키마 다시 확인** - `database/setup/mvp_schema.sql`

---

## ✅ 온보딩 완료 확인

다음 항목들을 모두 완료했는지 확인하세요:

- [ ] CHANGELOG를 읽고 최신 상태 파악
- [ ] 코딩 컨벤션 문서 정독
- [ ] 3-Layer 데이터베이스 구조 이해
- [ ] 핵심 Manager 클래스 코드 리뷰
- [ ] 모든 테스트 통과 확인
- [ ] 첫 작업 시작 및 CHANGELOG 업데이트

---

**작성**: AI Assistant  
**최종 업데이트**: 2026-01-01  
**다음 업데이트**: CHANGELOG에 따라 지속적으로 업데이트

**Good Luck! 🚀**

