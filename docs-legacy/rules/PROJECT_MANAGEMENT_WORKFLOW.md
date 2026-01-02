# 프로젝트 관리 워크플로우 규칙

**작성일**: 2026-01-01  
**목적**: 자동화된 프로젝트 관리 시스템의 워크플로우 규칙 정의  
**대상**: 모든 개발자 및 에이전트

---

## 📋 목차

1. [워크플로우 개요](#워크플로우-개요)
2. [상태 정의](#상태-정의)
3. [TDD 통합 프로세스](#tdd-통합-프로세스)
4. [에이전트 작업 규칙](#에이전트-작업-규칙)
5. [문서 자동화 규칙](#문서-자동화-규칙)
6. [Streamlit 대시보드 사용법](#streamlit-대시보드-사용법)

---

## 워크플로우 개요

### 전체 워크플로우

```
ideation → epic → task → 
  development (TDD):
    requirement → test_red → implement_green → refactor → quality_gate →
  qa → audit → done → deprecated
```

### 핵심 원칙

1. **상태 기반 관리**: 모든 작업은 명확한 상태를 가짐
2. **자동 전환**: 조건 만족 시 자동으로 다음 단계로 전환
3. **TDD 통합**: development 단계에 TDD 프로세스 필수
4. **비판적 검토**: Audit 단계에서 실제 동작 중심 평가
5. **문서 자동화**: 상태 변경 시 자동으로 문서 처리
6. **대시보드 중심**: 모든 상태 변경은 Streamlit 대시보드를 통해 수행

---

## 상태 정의

### 1. ideation (아이디어)

**정의**: 새로운 기능이나 개선 사항에 대한 아이디어

**생성 방법**:
- 사용자 요청
- 에이전트 제안

**문서 위치**: `docs/ideation/{category}/{TITLE}.md`

**메타데이터**:
```yaml
status: ideation
priority: high|medium|low
category: action-handler|object-interaction|...
created_at: 2026-01-01T00:00:00Z
epic_id: null
```

**전환 조건**:
- 사용자 승인 → `epic`

---

### 2. epic (대규모 기능)

**정의**: 여러 Task로 구성되는 대규모 기능 단위

**생성 방법**:
- ideation 승인 시 자동 생성

**문서 위치**: `docs/project-management/epics/{EPIC_ID}.md`

**메타데이터**:
```yaml
status: epic
epic_id: EPIC-001
ideation_doc_id: ideation-action-handler-modularization
tasks: []
```

**전환 조건**:
- 사용자 승인 → `task` (여러 개 생성 가능)

---

### 3. task (작업 단위)

**정의**: Epic을 구성하는 개별 작업 단위

**생성 방법**:
- Epic 승인 시 자동 생성 (에이전트가 Epic 분석하여 Task 분해)

**문서 위치**: `docs/project-management/tasks/{TASK_ID}.md`

**메타데이터**:
```yaml
status: task
task_id: TASK-001
epic_id: EPIC-001
estimated_hours: 4.0
todos: []
dependencies: []
```

**전환 조건**:
- 사용자 승인 및 의존성 해결 → `development`

---

### 4. development (TDD 프로세스)

**정의**: 실제 코드 구현 작업 (TDD 프로세스 필수)

**세부 단계**:
1. **requirement** (요구사항 정의)
   - 기능 요구사항 정의
   - DB 스키마 검토 (필요 시)
   - 데이터 무결성 검토

2. **test_red** (테스트 작성 - Red)
   - 실패하는 테스트 작성
   - 시나리오 테스트 포함
   - Mock 사용 (외부 의존성)

3. **implement_green** (구현 - Green)
   - 테스트 통과에 필요한 최소 구현
   - TODO YAML 제출 필수

4. **refactor** (리팩토링)
   - 중복 제거
   - 단일 책임 원칙 적용
   - 리팩토링 YAML 제출 필수

5. **quality_gate** (품질 게이트)
   - 테스트 통과 확인
   - 커버리지 ≥ 80% 확인
   - 린터 오류 없음 확인
   - 타입 체크 통과 확인
   - Quality Gate YAML 제출 필수

**문서 위치**: 
- `docs/project-management/todos/{TODO_ID}.md` 또는 코드 내 TODO 주석

**메타데이터**:
```yaml
status: development
todo_id: TODO-001
task_id: TASK-001
file: app/handlers/object_interaction_base.py
line: 1
sub_stage: requirement|test_red|implement_green|refactor|quality_gate
```

**전환 조건**:
- Quality Gate 통과 → `qa`

---

### 5. qa (품질 보증)

**정의**: 코드 품질 검증 및 테스트

**처리 방법**:
- QA 테스트 자동 실행
- 에이전트가 QA YAML 제출
- Streamlit 대시보드에서 승인 대기

**문서 위치**: `docs/audit/qa/{QA_ID}.md`

**메타데이터**:
```yaml
status: qa
qa_id: QA-001
todo_id: TODO-001
test_results:
  passed: 10
  failed: 0
  skipped: 0
coverage: 0.95
```

**전환 조건**:
- QA 테스트 통과 및 커버리지 ≥ 80% → `audit`

---

### 6. audit (구현 품질 감사)

**정의**: 프로젝트 핵심 규칙 준수 여부 검증 및 Integrity 저해 요소 확인

**검토 기준 (Integrity 체크리스트)**:
1. **3계층 아키텍처 준수**
   - ✅ UI Layer → Business Logic → Data Layer (단방향 의존)
   - ✅ UI는 Business Logic에만 의존 (Data Layer 직접 접근 금지)
   - ✅ 인터페이스를 통한 의존성 주입
   - ✅ 전역 상태 사용 금지

2. **UUID 규칙 준수**
   - ✅ UUID 컬럼에는 UUID 객체 사용 (`uuid.UUID`)
   - ✅ JSONB 필드에는 문자열로 저장 (`str(uuid_obj)`)
   - ✅ `uuid_helper.py` 헬퍼 함수 사용
   - ✅ 타입 혼용 없음 (UUID 객체 vs 문자열)

3. **데이터 중심 개발 준수**
   - ✅ DB 스키마 우선 설계
   - ✅ 데이터 무결성 보장 (트랜잭션 사용)
   - ✅ SSOT (Single Source of Truth) 준수

4. **타입 안전성 준수**
   - ✅ 모든 함수/클래스에 타입 힌트 100% 적용
   - ✅ `Any` 타입 사용 금지
   - ✅ Pydantic 모델로 런타임 검증

5. **비동기 우선 개발 준수**
   - ✅ 모든 I/O 작업 비동기 (`async/await`)
   - ✅ 동기 함수에서 비동기 함수 호출 금지
   - ✅ 동시성 문제 락/세마포어로 해결

6. **트랜잭션 규칙 준수**
   - ✅ 적절한 트랜잭션 범위 설정
   - ✅ 트랜잭션 격리 수준 준수
   - ✅ 롤백 처리 명시

7. **마이그레이션 규칙 준수**
   - ✅ 안전한 마이그레이션 스크립트
   - ✅ 백업 생성 및 복구 계획
   - ✅ 사용자 컨펌 요청 (위험한 작업)

**처리 방법**:
- 자동화된 Integrity 체크 실행
- 에이전트가 Audit YAML 제출 (체크리스트 결과 포함)
- Streamlit 대시보드에서 승인 대기

**문서 위치**: `docs/audit/{AUDIT_ID}.md`

**메타데이터**:
```yaml
status: audit
audit_id: AUDIT-001
qa_id: QA-001
integrity_checks:
  three_layer_architecture: passed|failed
  uuid_compliance: passed|failed
  data_centric_compliance: passed|failed
  type_safety_compliance: passed|failed
  async_first_compliance: passed|failed
  transaction_compliance: passed|failed
  migration_compliance: passed|failed
violations:
  - rule: "3계층 아키텍처"
    description: "UI Layer에서 Data Layer 직접 접근"
    file: "app/ui/frontend/src/components/GameView.tsx"
    line: 123
  - rule: "UUID 규칙"
    description: "JSONB 필드에 UUID 객체 직접 저장"
    file: "app/managers/cell_manager.py"
    line: 45
approved: false
```

**전환 조건**:
- 모든 Integrity 체크 통과 → `done`
- Integrity 위반 발견 → `development`로 롤백 (수정 후 재검토)

---

### 7. done (완료)

**정의**: 작업 완료

**자동 처리**:
1. CHANGELOG 자동 업데이트
2. IMPLEMENTATION_STATUS.md 자동 업데이트
3. 관련 문서 상태 업데이트
4. Streamlit 대시보드에 완료 표시

**전환 조건**:
- 관련 ideation 문서의 모든 Epic, Task, TODO가 done 상태 → `deprecated`

---

### 8. deprecated (폐기)

**정의**: 완료된 ideation 문서 아카이브

**자동 처리**:
1. 파일 이동: `docs/archive/deprecated/ideation/[deprecated]{TITLE}.md`
2. 파일명에 `[deprecated]` 접두어 추가
3. 문서 내 deprecation 섹션 추가
4. CHANGELOG에 deprecation 기록

---

## TDD 통합 프로세스

### development 단계 세부 프로세스

#### 1. requirement (요구사항 정의)

**필수 작업**:
- 기능 요구사항 명시 (입력, 출력, 실패 조건)
- DB 스키마 검토 (필요 시 스키마 변경)
- 데이터 무결성 검토

**출력**:
- 요구사항 문서 또는 테스트 내부 docstring

#### 2. test_red (테스트 작성 - Red)

**필수 작업**:
- 실패하는 테스트 작성
- 시나리오 기반 테스트 포함
- 외부 의존성은 Mock으로 대체

**테스트 타입**:
- Unit Test (단일 함수/메서드)
- Integration Test (Entity ↔ Service ↔ DB)
- Scenario Test (게임 행위 흐름)

#### 3. implement_green (구현 - Green)

**필수 작업**:
- 테스트 통과에 필요한 최소 구현
- 성능 최적화, 구조 개선은 이 단계에서 하지 않음
- **TODO YAML 제출 필수**

**YAML 제출 형식**:
```yaml
# docs/project-management/submissions/TODO-001.yaml
todo_id: TODO-001
action: submit
status: implement_green
code_changes:
  - file: app/handlers/object_interaction_base.py
    added_lines: 150
```

#### 4. refactor (리팩토링)

**필수 작업**:
- 중복 제거
- 함수는 단일 책임을 가지도록 재구성
- 불변성, 타입 안정성, 의존성 주입 반영
- **리팩토링 YAML 제출 필수**

**리팩토링 트리거**:
- 함수 길이 > 50줄
- if/for 중첩 > 3단계
- 유사한 코드 반복 발견

#### 5. quality_gate (품질 게이트)

**필수 조건**:
- ✅ 모든 테스트 통과
- ✅ 코드 커버리지 ≥ 80%
- ✅ mypy (타입 오류 0)
- ✅ flake8 (Lint 오류 0)
- ✅ **Quality Gate YAML 제출 필수**

**통과하지 못하면**: `implement_green` 단계로 롤백

---

## 에이전트 작업 규칙

### 1. 필수 제출 사항

**에이전트는 다음 단계에서 반드시 YAML을 제출해야 함**:
- `implement_green`: TODO YAML 제출
- `refactor`: 리팩토링 YAML 제출
- `quality_gate`: Quality Gate YAML 제출
- `qa`: QA YAML 제출
- `audit`: Audit YAML 제출

### 2. YAML 제출 위치

**제출 디렉토리**: `docs/project-management/submissions/`

**파일명 형식**:
- TODO 제출: `TODO-{ID}.yaml`
- 상태 전환 요청: `TRANSITION-{ID}.yaml`
- 진행 상황 업데이트: `PROGRESS-{ID}.yaml`

### 3. 제출 형식

**TODO 제출**:
```yaml
todo_id: TODO-001
action: submit|update|transition
status: implement_green|refactor|quality_gate
code_changes:
  - file: app/handlers/object_interaction_base.py
    added_lines: 150
test_results:
  total: 10
  passed: 10
  coverage: 0.95
```

**상태 전환 요청**:
```yaml
transition_id: TRANSITION-001
item_id: TODO-001
from_status: quality_gate
to_status: qa
reason: "Quality Gate 통과"
validation:
  tests_pass: true
  coverage: 0.95
  linter_errors: 0
```

### 4. 제출 후 처리

**에이전트 제출 후**:
1. YAML 파일이 `docs/project-management/submissions/`에 생성됨
2. Streamlit 대시보드에 "에이전트 제출 대기" 섹션에 표시
3. 사용자 승인 대기
4. 승인 시 자동 처리 (상태 전환, 문서 이동 등)

---

## 문서 자동화 규칙

### 1. 상태 변경 시 자동 처리

**자동 처리 항목**:
1. **문서 이동**: 상태에 따라 문서 자동 이동
2. **메타데이터 업데이트**: 문서 메타데이터 자동 업데이트
3. **CHANGELOG 업데이트**: `done` 상태 시 CHANGELOG 자동 업데이트
4. **IMPLEMENTATION_STATUS.md 업데이트**: 구현 상태 표 자동 업데이트
5. **관련 문서 링크 업데이트**: 관련 문서의 링크 자동 업데이트

### 2. 문서 위치 규칙

**상태별 문서 위치**:
- `ideation`: `docs/ideation/{category}/{TITLE}.md`
- `epic`: `docs/project-management/epics/{EPIC_ID}.md`
- `task`: `docs/project-management/tasks/{TASK_ID}.md`
- `development`: `docs/project-management/todos/{TODO_ID}.md` 또는 코드 내 TODO
- `qa`: `docs/audit/qa/{QA_ID}.md`
- `audit`: `docs/audit/{AUDIT_ID}.md`
- `done`: 문서 유지 (상태만 변경)
- `deprecated`: `docs/archive/deprecated/ideation/[deprecated]{TITLE}.md`

### 3. CHANGELOG 업데이트 규칙

**업데이트 시점**: 작업이 `done` 상태가 될 때

**업데이트 형식**:
```markdown
## 주요 기능 구현 내역

### {작업 제목}

**완료일**: {완료일}

**구현 내용**:
- {구현 내용}

**관련 문서**:
- {관련 문서 링크}
```

### 4. IMPLEMENTATION_STATUS.md 업데이트 규칙

**업데이트 시점**: 작업이 `done` 상태가 될 때

**업데이트 내용**:
- 구현 상태 표 업데이트
- 완료율 재계산
- 관련 문서 상태 업데이트

---

## Streamlit 대시보드 사용법

### 1. 대시보드 접근

**실행 방법**:
```bash
streamlit run tools/dashboard/main.py
```

**URL**: `http://localhost:8501`

### 2. 상태 변경

**방법 1: 드래그 앤 드롭**
- 작업 카드를 드래그하여 다른 상태 칼럼으로 이동

**방법 2: 버튼 클릭**
- 작업 카드 클릭 → 상세 정보 패널 → 상태 변경 버튼

### 3. 에이전트 제출 승인

**프로세스**:
1. "에이전트 제출 대기" 섹션 확인
2. 제출 내용 검토
3. "승인" 또는 "거부" 버튼 클릭
4. 승인 시 자동 처리 (상태 전환, 문서 이동 등)

### 4. 필터 및 검색

**필터 옵션**:
- 카테고리: action-handler, object-interaction, ...
- 상태: ideation, epic, task, ...
- 우선순위: high, medium, low
- 검색: 제목, 설명 검색

---

## 강제 실행 규칙

### 1. 워크플로우 위반 방지

**금지 사항**:
- ❌ 상태를 건너뛰고 전환 (예: development → done)
- ❌ 필수 단계 생략 (예: quality_gate 없이 qa로 전환)
- ❌ 의존성 무시 (예: 의존 Task가 완료되지 않았는데 development 시작)

**강제 검증**:
- 상태 전환 전 필수 검증 수행
- 검증 실패 시 전환 차단
- 에러 메시지 표시

### 2. 필수 제출 강제

**에이전트 필수 제출**:
- `implement_green`: TODO YAML 제출 필수
- `quality_gate`: Quality Gate YAML 제출 필수
- `qa`: QA YAML 제출 필수
- `audit`: Audit YAML 제출 필수

**제출 없이 진행 불가**:
- YAML 제출 없이는 다음 단계로 전환 불가
- Streamlit 대시보드에서 제출 요청 표시

### 3. 문서 자동화 강제

**자동 처리 필수**:
- 상태 변경 시 문서 자동 이동 (수동 이동 금지)
- CHANGELOG 자동 업데이트 (수동 업데이트 금지)
- IMPLEMENTATION_STATUS.md 자동 업데이트 (수동 업데이트 금지)

---

## 예외 처리

### 1. 롤백 규칙

**자동 롤백 조건**:
- QA 실패 → `development`로 롤백
- Audit 실패 (품질 점수 < 6.0) → `development`로 롤백
- Audit 실패 (품질 점수 ≥ 6.0) → `qa`로 롤백

### 2. 수동 개입

**수동 개입이 필요한 경우**:
- 워크플로우 예외 상황
- 데이터 무결성 문제
- 시스템 오류

**처리 방법**:
- Streamlit 대시보드에서 "수동 처리" 모드 활성화
- 관리자 권한으로 상태 변경

---

## 다음 단계

1. **도구 구현**: Streamlit 대시보드 및 YAML 제출 시스템 구현
2. **통합 테스트**: 실제 시나리오로 테스트
3. **에이전트 통합**: 에이전트가 사용할 수 있도록 통합
4. **문서화**: 사용 가이드 작성

