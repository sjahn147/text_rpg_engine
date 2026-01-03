# 에이전트 문서 관리 규칙 (DEPRECATED)

> **⚠️ 이 문서는 더 이상 사용되지 않습니다.**  
> **최신 규칙**: `AGENT_DOCUMENT_MANAGEMENT_V2.md` 참조  
> **Deprecated 날짜**: 2026-01-03  
> **이유**: 과도한 복잡성으로 인한 비효율성

---

# 에이전트 문서 관리 규칙 (최종 버전 2.0) [DEPRECATED]

> **최신화 날짜**: 2026-01-03  
> **작성일**: 2026-01-01  
> **버전**: 2.0 (MECE 원칙 적용)  
> **목적**: 에이전트가 프로젝트 문서를 효율적으로 관리하기 위한 필수 규칙  
> **핵심 원칙**: 규칙 준수 → 자동화 달성  
> **설계 원칙**: MECE (Mutually Exclusive, Collectively Exhaustive)  
> **⚠️ DEPRECATED**: 이 규칙은 과도한 복잡성으로 인해 더 이상 사용되지 않습니다. `AGENT_DOCUMENT_MANAGEMENT_V2.md`를 참조하세요.

---

## ⚠️ 중요: 이 문서는 필수 읽기

**모든 에이전트는 이 문서의 규칙을 반드시 준수해야 합니다.**

- ❌ 규칙 위반 시 문서 저장 금지
- ✅ 규칙 준수 시 자동으로 문서 관리 가능
- ✅ 기존 문서도 이 규칙에 따라 처리

---

## 📋 목차

1. [워크플로우 개요](#워크플로우-개요)
2. [문서 타입 및 순서 정의](#문서-타입-및-순서-정의)
3. [디렉토리 구조](#디렉토리-구조)
4. [파일명 규칙](#파일명-규칙)
5. [문서 작성 규칙](#문서-작성-규칙)
6. [상태 전환 규칙](#상태-전환-규칙)
7. [문서 관계 모델](#문서-관계-모델)
8. [네이밍 컨벤션](#네이밍-컨벤션)
9. [검증 규칙](#검증-규칙)
10. [실제 사용 예시](#실제-사용-예시)

---

## 워크플로우 개요

### 전체 워크플로우 (순서 1~N)

```
Phase 1: Ideation (아이디어 단계)
  1. 문제 정의 (problem-definition)
  2. 현황 진단 (current-status)
  3. 방법론 검토 (methodology)
  4. 실행 계획 수립 (plan)
  ↓
Phase 2: Development (개발 단계)
  5. Epic (epic)
  6. Task (task)
  7. To-do (todo)
  8. Test (test)
  9. Troubleshooting (troubleshooting)
  ↓
Phase 3: Audit (검증 단계)
  10. QA (qa)
  11. Rule Compliance (audit)
  ↓
Phase 4: 프로젝트 종결 처리 (종결 단계)
  12. 문서 최신화 (documentation-update)
  13. Done 처리 (done)
  14. Deprecated 처리 (deprecated)
  15. 항구 보존 문서 생성 (permanent-docs)
```

### 핵심 원칙

1. **순차적 진행**: 1단계부터 N단계까지 순서대로 진행
2. **MECE 원칙**: 각 단계는 상호 배타적이며 전체를 포괄
3. **명확한 전환 조건**: 각 단계 전환 시 명확한 조건 필요
4. **자동화 가능**: 모든 단계가 자동화 가능하도록 설계

---

## 문서 타입 및 순서 정의

### Phase 1: Ideation (아이디어 단계)

#### 1.1 문제 정의 (ideation-problem-definition)

**순서**: 1  
**타입**: `ideation`  
**서브타입**: `problem-definition`  
**목적**: 문제를 정의하고 해결 방향을 제시

**폴더**: `docs/work-items/01-problem-definition/`  
**파일명 규칙**: `ideation-{category}-{title-slug}-problem-definition.md`  
**예시**: `ideation-object-interaction-problem-definition.md`

**메타데이터**:
```yaml
id: ideation-{category}-{title-slug}-problem-definition
type: ideation
ideation_type: problem-definition
status: ideation
category: {category}
priority: high|medium|low
created_at: {YYYY-MM-DDTHH:MM:SSZ}
updated_at: {YYYY-MM-DDTHH:MM:SSZ}
author: agent|user
epic_id: null
related_ideations: []
```

**전환 조건**: 문제 정의 완료 → 현황 진단

---

#### 1.2 현황 진단 (ideation-status)

**순서**: 2  
**타입**: `ideation`  
**서브타입**: `status`  
**목적**: 현재 상황을 파악하고 구현 상태를 진단

**폴더**: `docs/work-items/02-current-status/`  
**파일명 규칙**: `ideation-{category}-{title-slug}-status.md`  
**예시**: `ideation-object-interaction-current-status.md`

**메타데이터**:
```yaml
id: ideation-{category}-{title-slug}-status
type: ideation
ideation_type: status
status: ideation
category: {category}
priority: high|medium|low
created_at: {YYYY-MM-DDTHH:MM:SSZ}
updated_at: {YYYY-MM-DDTHH:MM:SSZ}
author: agent|user
epic_id: null
related_ideations:
  - id: ideation-{category}-{title-slug}-problem-definition
    relation: based_on
```

**전환 조건**: 현황 파악 완료 → 방법론 검토

---

#### 1.3 방법론 검토 (ideation-methodology)

**순서**: 3  
**타입**: `ideation`  
**서브타입**: `methodology`  
**목적**: 해결 방법론 검토 및 비교

**폴더**: `docs/work-items/03-methodology/`  
**파일명 규칙**: `ideation-{category}-{title-slug}-methodology.md`  
**예시**: `ideation-object-interaction-solution-methodology.md`

**메타데이터**:
```yaml
id: ideation-{category}-{title-slug}-methodology
type: ideation
ideation_type: methodology
status: ideation
category: {category}
priority: high|medium|low
created_at: {YYYY-MM-DDTHH:MM:SSZ}
updated_at: {YYYY-MM-DDTHH:MM:SSZ}
author: agent|user
epic_id: null
related_ideations:
  - id: ideation-{category}-{title-slug}-problem-definition
    relation: based_on
  - id: ideation-{category}-{title-slug}-status
    relation: based_on
```

**전환 조건**: 방법론 검토 완료 → 실행 계획 수립

---

#### 1.4 실행 계획 수립 (ideation-plan)

**순서**: 3  
**타입**: `ideation`  
**서브타입**: `methodology`  
**목적**: 해결 방법론 검토 및 비교

**폴더**: `docs/work-items/03-methodology/`  
**파일명 규칙**: `ideation-{category}-{title-slug}-methodology.md`  
**예시**: `ideation-object-interaction-solution-methodology.md`

**메타데이터**:
```yaml
id: ideation-{category}-{title-slug}-methodology
type: ideation
ideation_type: methodology
status: ideation
category: {category}
priority: high|medium|low
created_at: {YYYY-MM-DDTHH:MM:SSZ}
updated_at: {YYYY-MM-DDTHH:MM:SSZ}
author: agent|user
epic_id: null
related_ideations:
  - id: ideation-{category}-{title-slug}-status
    relation: based_on
```

**전환 조건**: 방법론 검토 완료 → 실행 계획 수립

---

#### 1.4 실행 계획 수립 (ideation-plan)

**순서**: 4  
**타입**: `ideation`  
**서브타입**: `plan`  
**목적**: 구체적인 실행 계획 수립

**폴더**: `docs/work-items/04-plan/`  
**파일명 규칙**: `ideation-{category}-{title-slug}-plan.md`  
**예시**: `ideation-object-interaction-enhancement-plan.md`

**메타데이터**:
```yaml
id: ideation-{category}-{title-slug}-plan
type: ideation
ideation_type: plan
status: ideation
category: {category}
priority: high|medium|low
created_at: {YYYY-MM-DDTHH:MM:SSZ}
updated_at: {YYYY-MM-DDTHH:MM:SSZ}
author: agent|user
epic_id: null
related_ideations:
  - id: ideation-{category}-{title-slug}-problem-definition
    relation: plan_of
  - id: ideation-{category}-{title-slug}-status
    relation: plan_of
  - id: ideation-{category}-{title-slug}-methodology
    relation: based_on
```

**전환 조건**: 실행 계획 승인 → Epic 생성

**특별 규칙**: `plan` 타입 ideation이 Epic으로 전환될 때 우선적으로 사용

---

### Phase 2: Development (개발 단계)

#### 2.1 Epic (epic)

**순서**: 5  
**타입**: `epic`  
**목적**: 대규모 기능 단위 정의

**폴더**: `docs/work-items/05-epic/`  
**파일명 규칙**: `EPIC-{번호}-{keyword}.md`  
**예시**: `EPIC-001-object-interaction-enhancement.md`

**키워드 추출 규칙**:
- 관련 ideation의 `category`와 `title-slug`에서 추출
- 형식: `{category}-{title-slug}` (최대 50자)
- 예: `ideation-object-interaction-enhancement-plan` → `object-interaction-enhancement`

**메타데이터**:
```yaml
id: EPIC-{번호}-{keyword}
type: epic
status: epic
ideation_ids: []  # 관련 ideation ID 목록
tasks: []  # 하위 Task ID 목록
keyword: {keyword}  # 파일명에 사용된 키워드
created_at: {YYYY-MM-DDTHH:MM:SSZ}
updated_at: {YYYY-MM-DDTHH:MM:SSZ}
author: agent|user
```

**전환 조건**: Epic 승인 → Task 생성

---

#### 2.2 Task (task)

**순서**: 6  
**타입**: `task`  
**목적**: 구체적인 작업 단위 정의

**폴더**: `docs/work-items/06-task/`  
**파일명 규칙**: `TASK-{번호}-{keyword}.md`  
**예시**: `TASK-001-action-generation-logic.md`

**키워드 추출 규칙**:
- 작업 내용에서 의미 있는 단어 추출 (최대 30자)
- 예: "액션 생성 로직 보완" → `action-generation-logic`

**메타데이터**:
```yaml
id: TASK-{번호}-{keyword}
type: task
status: task
epic_id: EPIC-{번호}-{keyword}
dependencies: []  # 의존성 Task ID 목록
todos: []  # 하위 TODO ID 목록
estimated_hours: {숫자}
keyword: {keyword}  # 파일명에 사용된 키워드
created_at: {YYYY-MM-DDTHH:MM:SSZ}
updated_at: {YYYY-MM-DDTHH:MM:SSZ}
author: agent|user
```

**전환 조건**: Task 승인 → TODO 생성

---

#### 2.3 To-do (todo)

**순서**: 7  
**타입**: `todo`  
**목적**: 구체적인 개발 작업 정의

**폴더**: `docs/work-items/07-todo/`  
**파일명 규칙**: `TODO-{번호}-{keyword}.md`  
**예시**: `TODO-001-state-transition-validation.md`

**키워드 추출 규칙**:
- 작업 내용에서 의미 있는 단어 추출 (최대 30자)
- 예: "상태 전이 규칙 검증 강화" → `state-transition-validation`

**메타데이터**:
```yaml
id: TODO-{번호}-{keyword}
type: todo
status: development
sub_status: requirement|test_red|implement_green|refactor|quality_gate
task_id: TASK-{번호}-{keyword}
file: {파일 경로}
line: {라인 번호}
code_snippet: {코드 스니펫}
keyword: {keyword}  # 파일명에 사용된 키워드
created_at: {YYYY-MM-DDTHH:MM:SSZ}
updated_at: {YYYY-MM-DDTHH:MM:SSZ}
author: agent|user
```

**전환 조건**: 
- `quality_gate` 통과 → Test 생성
- 문제 발생 → Troubleshooting 생성

---

#### 2.4 Test (test)

**순서**: 8  
**타입**: `test`  
**목적**: 테스트 케이스 작성 및 실행

**폴더**: `docs/work-items/08-test/`  
**파일명 규칙**: `TEST-{번호}-{keyword}.md`  
**예시**: `TEST-001-state-transition-test.md`

**키워드 추출 규칙**:
- 관련 TODO의 키워드 사용 또는 테스트 내용에서 추출 (최대 30자)
- 예: TODO가 `state-transition-validation`이면 → `state-transition-test`

**메타데이터**:
```yaml
id: TEST-{번호}-{keyword}
type: test
status: development
todo_id: TODO-{번호}-{keyword}
test_file: {테스트 파일 경로}
test_results:
  passed: {숫자}
  failed: {숫자}
  skipped: {숫자}
coverage: {0.0-1.0}
keyword: {keyword}  # 파일명에 사용된 키워드
created_at: {YYYY-MM-DDTHH:MM:SSZ}
updated_at: {YYYY-MM-DDTHH:MM:SSZ}
author: agent|user
```

**전환 조건**: 
- 모든 테스트 통과 및 커버리지 기준 충족 → QA 생성
- 테스트 실패 → Troubleshooting 생성

---

#### 2.5 Troubleshooting (troubleshooting)

**순서**: 9  
**타입**: `troubleshooting`  
**목적**: 문제 해결 및 디버깅

**폴더**: `docs/work-items/09-troubleshooting/`  
**파일명 규칙**: `TROUBLESHOOT-{번호}-{keyword}.md`  
**예시**: `TROUBLESHOOT-001-action-generation-issue.md`

**키워드 추출 규칙**:
- 문제 내용에서 의미 있는 단어 추출 (최대 30자)
- 예: "액션 생성 로직 문제" → `action-generation-issue`

**메타데이터**:
```yaml
id: TROUBLESHOOT-{번호}-{keyword}
type: troubleshooting
status: development
related_todo_id: TODO-{번호}-{keyword}
related_test_id: TEST-{번호}-{keyword}  # 선택사항
issue_description: {문제 설명}
solution: {해결 방법}
resolved: true|false
keyword: {keyword}  # 파일명에 사용된 키워드
created_at: {YYYY-MM-DDTHH:MM:SSZ}
updated_at: {YYYY-MM-DDTHH:MM:SSZ}
author: agent|user
```

**전환 조건**: 
- 문제 해결 → 원래 단계로 복귀 (TODO 또는 Test)
- 해결 불가 → Task로 롤백

---

### Phase 3: Audit (검증 단계)

#### 3.1 QA (qa)

**순서**: 10  
**타입**: `qa`  
**목적**: 품질 보증 및 테스트 검증

**폴더**: `docs/work-items/10-qa/`  
**파일명 규칙**: `QA-{번호}-{keyword}.md`  
**예시**: `QA-001-state-transition-qa.md`

**키워드 추출 규칙**:
- 관련 TODO의 키워드 사용 (최대 30자)
- 예: TODO가 `state-transition-validation`이면 → `state-transition-qa`

**메타데이터**:
```yaml
id: QA-{번호}-{keyword}
type: qa
status: qa
todo_id: TODO-{번호}-{keyword}
test_id: TEST-{번호}-{keyword}
qa_results:
  all_tests_passed: true|false
  coverage: {0.0-1.0}
  linter_errors: {숫자}
  type_check_passed: true|false
quality_score: {0.0-10.0}
keyword: {keyword}  # 파일명에 사용된 키워드
created_at: {YYYY-MM-DDTHH:MM:SSZ}
updated_at: {YYYY-MM-DDTHH:MM:SSZ}
author: agent|user
```

**전환 조건**: 
- QA 통과 기준 충족 → Audit (Rule Compliance) 생성
- QA 실패 → Development 단계로 롤백

**QA 통과 기준**:
- 모든 테스트 통과
- 코드 커버리지 ≥ 80%
- 린터 오류 없음
- 타입 체크 통과

---

#### 3.2 Rule Compliance (audit)

**순서**: 11  
**타입**: `audit`  
**목적**: 규칙 준수 검증 (3계층 구조, UUID, 데이터 중심, 타입 안전성, 비동기, 트랜잭션, 마이그레이션)

**폴더**: `docs/work-items/11-audit/`  
**파일명 규칙**: `AUDIT-{번호}-{keyword}.md`  
**예시**: `AUDIT-001-state-transition-audit.md`

**키워드 추출 규칙**:
- 관련 QA의 키워드 사용 (최대 30자)
- 예: QA가 `state-transition-qa`이면 → `state-transition-audit`

**메타데이터**:
```yaml
id: AUDIT-{번호}-{keyword}
type: audit
status: audit
qa_id: QA-{번호}-{keyword}
audit_results:
  three_layer_architecture: pass|fail|warning
  uuid_compliance: pass|fail|warning
  data_centric: pass|fail|warning
  type_safety: pass|fail|warning
  async_first: pass|fail|warning
  transactions: pass|fail|warning
  migrations: pass|fail|warning
overall_compliance: pass|fail|warning
violations: []  # 위반 사항 목록
keyword: {keyword}  # 파일명에 사용된 키워드
created_at: {YYYY-MM-DDTHH:MM:SSZ}
updated_at: {YYYY-MM-DDTHH:MM:SSZ}
author: agent|user
```

**전환 조건**: 
- 모든 규칙 준수 → 프로젝트 종결 처리 시작
- 규칙 위반 → Development 단계로 롤백

---

### Phase 4: 프로젝트 종결 처리 (종결 단계)

#### 4.1 문서 최신화 (documentation-update)

**순서**: 12  
**타입**: `documentation-update`  
**목적**: 관련 문서 최신화

**폴더**: `docs/work-items/12-documentation/`  
**파일명 규칙**: `DOC-UPDATE-{번호}-{keyword}.md`  
**예시**: `DOC-UPDATE-001-object-interaction-docs.md`

**키워드 추출 규칙**:
- 관련 Epic의 키워드 사용 또는 문서 타입 포함 (최대 40자)
- 예: Epic이 `object-interaction-enhancement`이면 → `object-interaction-docs`

**메타데이터**:
```yaml
id: DOC-UPDATE-{번호}-{keyword}
type: documentation-update
status: documentation
related_epic_id: EPIC-{번호}-{keyword}
updated_documents: []  # 업데이트된 문서 목록
keyword: {keyword}  # 파일명에 사용된 키워드
created_at: {YYYY-MM-DDTHH:MM:SSZ}
updated_at: {YYYY-MM-DDTHH:MM:SSZ}
author: agent|user
```

**전환 조건**: 문서 최신화 완료 → Done 처리

---

#### 4.2 Done 처리 (done)

**순서**: 13  
**타입**: `done`  
**목적**: 작업 완료 처리

**폴더**: `docs/work-items/13-done/`  
**파일명 규칙**: `DONE-{원본ID}.md`  
**예시**: `DONE-EPIC-001-object-interaction-enhancement.md`

**메타데이터**:
```yaml
id: {원본ID}
type: {원본타입}
status: done
completed_at: {YYYY-MM-DDTHH:MM:SSZ}
original_path: {원본 경로}
created_at: {YYYY-MM-DDTHH:MM:SSZ}
updated_at: {YYYY-MM-DDTHH:MM:SSZ}
author: agent|user
```

**전환 조건**: Done 처리 완료 → Deprecated 처리 또는 항구 보존 문서 생성

---

#### 4.3 Deprecated 처리 (deprecated)

**순서**: 14  
**타입**: `deprecated`  
**목적**: 더 이상 사용하지 않는 문서 처리

**폴더**: `docs/work-items/14-deprecated/`  
**파일명 규칙**: `[deprecated]{원본ID}.md`  
**예시**: `[deprecated]ideation-object-interaction-current-status.md`

**메타데이터**:
```yaml
id: {원본ID}
type: {원본타입}
status: deprecated
deprecated_at: {YYYY-MM-DDTHH:MM:SSZ}
deprecated_reason: {사유}
original_path: {원본 경로}
created_at: {YYYY-MM-DDTHH:MM:SSZ}
updated_at: {YYYY-MM-DDTHH:MM:SSZ}
author: agent|user
```

**전환 조건**: Deprecated 처리 완료 → 항구 보존 문서 생성

---

#### 4.4 항구 보존 문서 생성 (permanent-docs)

**순서**: 15  
**타입**: `permanent-docs`  
**목적**: changelog, 규칙, 아키텍처 등 항구 보존 문서 생성 및 업데이트

**폴더**: `docs/work-items/15-permanent/`  
**파일명 규칙**: `PERM-DOC-{번호}-{keyword}.md`  
**예시**: `PERM-DOC-001-object-interaction-changelog.md`

**키워드 추출 규칙**:
- 관련 Epic의 키워드 사용 또는 문서 타입 포함 (최대 40자)
- 예: Epic이 `object-interaction-enhancement`이고 changelog 업데이트면 → `object-interaction-changelog`

**메타데이터**:
```yaml
id: PERM-DOC-{번호}-{keyword}
type: permanent-docs
status: permanent
related_epic_id: EPIC-{번호}-{keyword}
document_types: []  # changelog|rules|architecture|api-reference|...
target_files: []  # 업데이트할 파일 목록
keyword: {keyword}  # 파일명에 사용된 키워드
created_at: {YYYY-MM-DDTHH:MM:SSZ}
updated_at: {YYYY-MM-DDTHH:MM:SSZ}
author: agent|user
```

**전환 조건**: 항구 보존 문서 생성 완료 → 워크플로우 종료

**생성 대상 문서**:
- `docs/changelog/CHANGELOG.md`: 변경 이력 업데이트
- `docs/rules/*.md`: 규칙 문서 업데이트 (필요 시)
- `docs/architecture/*.md`: 아키텍처 문서 업데이트 (필요 시)
- `docs/api/*.md`: API 문서 업데이트 (필요 시)

---

## 디렉토리 구조

### 필수 구조

**모든 작업 항목은 다음 구조를 따라야 함:**

```
docs/
├── work-items/                    # 모든 작업 항목 (통합 관리)
│   ├── 01-problem-definition/     # 순서 1: 문제 정의
│   │   └── ideation-{category}-{title-slug}-problem-definition.md
│   │
│   ├── 02-current-status/         # 순서 2: 현황 진단
│   │   └── ideation-{category}-{title-slug}-status.md
│   │
│   ├── 03-methodology/            # 순서 3: 방법론 검토
│   │   └── ideation-{category}-{title-slug}-methodology.md
│   │
│   ├── 04-plan/                   # 순서 4: 실행 계획 수립
│   │   └── ideation-{category}-{title-slug}-plan.md
│   │
│   ├── 05-epic/                   # 순서 5: Epic
│   │   └── EPIC-{번호}-{keyword}.md
│   │
│   ├── 06-task/                   # 순서 6: Task
│   │   └── TASK-{번호}-{keyword}.md
│   │
│   ├── 07-todo/                   # 순서 7: To-do
│   │   └── TODO-{번호}-{keyword}.md
│   │
│   ├── 08-test/                   # 순서 8: Test
│   │   └── TEST-{번호}-{keyword}.md
│   │
│   ├── 09-troubleshooting/        # 순서 9: Troubleshooting
│   │   └── TROUBLESHOOT-{번호}-{keyword}.md
│   │
│   ├── 10-qa/                     # 순서 10: QA
│   │   └── QA-{번호}-{keyword}.md
│   │
│   ├── 11-audit/                  # 순서 11: Audit
│   │   └── AUDIT-{번호}-{keyword}.md
│   │
│   ├── 12-documentation/          # 순서 12: Documentation Update
│   │   └── DOC-UPDATE-{번호}-{keyword}.md
│   │
│   ├── 13-done/                   # 순서 13: Done
│   │   └── DONE-{원본ID}.md
│   │
│   ├── 14-deprecated/             # 순서 14: Deprecated
│   │   └── [deprecated]{원본ID}.md
│   │
│   └── 15-permanent/              # 순서 15: Permanent Docs
│       └── PERM-DOC-{번호}-{keyword}.md
│
├── submissions/                   # 에이전트 제출 파일 (YAML만)
│   ├── TODO-{ID}.yaml
│   ├── TEST-{ID}.yaml
│   ├── QA-{ID}.yaml
│   ├── AUDIT-{ID}.yaml
│   └── TRANSITION-{ID}.yaml
│
├── rules/                         # 개발 규칙 (항구 보존)
├── architecture/                  # 아키텍처 문서 (항구 보존)
├── changelog/                     # 변경 이력 (항구 보존)
└── api/                           # API 문서 (항구 보존)
```

### 핵심 원칙

1. **순서별 폴더**: `docs/work-items/{순서}-{type}/` (예: `01-problem-definition/`, `02-current-status/`, `07-test/`)
2. **각 순서별 독립 폴더**: 순서 1~14 각각 별도 폴더
3. **플랫 구조**: 최대 2단계 깊이
4. **ID + 키워드 기반 파일명**: 시퀀스 번호와 의미 있는 키워드 포함
5. **메타데이터 내장**: YAML frontmatter (별도 파일 불필요)
6. **순서 명확**: 1~14 단계 순서대로 진행

---

## 파일명 규칙

### 필수 규칙

**에이전트는 다음 파일명 규칙을 반드시 준수해야 함:**

| 순서 | 타입 | 서브타입 | 파일명 형식 | 예시 |
|------|------|---------|------------|------|
| 1 | ideation | problem-definition | `ideation-{category}-{title-slug}-problem-definition.md` | `ideation-object-interaction-problem-definition.md` |
| 2 | ideation | status | `ideation-{category}-{title-slug}-status.md` | `ideation-object-interaction-current-status.md` |
| 3 | ideation | methodology | `ideation-{category}-{title-slug}-methodology.md` | `ideation-object-interaction-solution-methodology.md` |
| 4 | ideation | plan | `ideation-{category}-{title-slug}-plan.md` | `ideation-object-interaction-enhancement-plan.md` |
| 5 | epic | - | `EPIC-{번호}-{keyword}.md` | `EPIC-001-object-interaction-enhancement.md` |
| 6 | task | - | `TASK-{번호}-{keyword}.md` | `TASK-001-action-generation-logic.md` |
| 7 | todo | - | `TODO-{번호}-{keyword}.md` | `TODO-001-state-transition-validation.md` |
| 8 | test | - | `TEST-{번호}-{keyword}.md` | `TEST-001-state-transition-test.md` |
| 9 | troubleshooting | - | `TROUBLESHOOT-{번호}-{keyword}.md` | `TROUBLESHOOT-001-action-generation-issue.md` |
| 10 | qa | - | `QA-{번호}-{keyword}.md` | `QA-001-state-transition-qa.md` |
| 11 | audit | - | `AUDIT-{번호}-{keyword}.md` | `AUDIT-001-state-transition-audit.md` |
| 12 | documentation-update | - | `DOC-UPDATE-{번호}-{keyword}.md` | `DOC-UPDATE-001-object-interaction-docs.md` |
| 13 | done | - | `DONE-{원본ID}.md` | `DONE-EPIC-001-object-interaction-enhancement.md` |
| 14 | deprecated | - | `[deprecated]{원본ID}.md` | `[deprecated]ideation-object-interaction-current-status.md` |
| 15 | permanent-docs | - | `PERM-DOC-{번호}-{keyword}.md` | `PERM-DOC-001-object-interaction-changelog.md` |

### 키워드 추출 규칙

**키워드는 관련 ideation에서 추출:**

1. **Epic 키워드 추출**:
   - 관련 ideation의 `category`와 `title-slug`에서 추출
   - 형식: `{category}-{title-slug}` (최대 50자)
   - 예: `ideation-object-interaction-enhancement-plan` → `object-interaction-enhancement`

2. **Task/TODO/Test/QA/Audit 키워드 추출**:
   - 상위 Epic 또는 Task의 키워드 사용
   - 또는 작업 내용에서 의미 있는 키워드 추출 (최대 30자)
   - 예: `action-generation-logic`, `state-transition-validation`

3. **Documentation Update/Permanent Docs 키워드 추출**:
   - 관련 Epic의 키워드 사용
   - 또는 문서 타입 포함 (최대 40자)
   - 예: `object-interaction-docs`, `object-interaction-changelog`

**키워드 네이밍 규칙**:
- 소문자만 사용
- 단어는 하이픈(`-`)으로 구분
- 최대 길이 제한 (Epic: 50자, Task/TODO/Test/QA/Audit: 30자, Documentation/Permanent: 40자)
- 의미 있는 단어만 포함 (불필요한 단어 제거)

### ID 생성 규칙

**Ideation ID**:
- 형식: `ideation-{category}-{title-slug}-{ideation_type}`
- 예시: `ideation-object-interaction-current-status`
- 규칙: 소문자, 하이픈으로 단어 구분, 서브타입 포함

**Epic ID**:
- 형식: `EPIC-{순차번호}-{keyword}`
- 예시: `EPIC-001-object-interaction-enhancement`
- 규칙: 
  - 순차적 번호 부여 (기존 번호 확인 후 다음 번호 사용)
  - 키워드는 관련 ideation에서 추출 (`{category}-{title-slug}`)
  - 키워드 최대 50자

**Task ID**:
- 형식: `TASK-{순차번호}-{keyword}`
- 예시: `TASK-001-action-generation-logic`
- 규칙:
  - 순차적 번호 부여
  - 키워드는 작업 내용에서 의미 있는 단어 추출
  - 키워드 최대 30자

**TODO ID**:
- 형식: `TODO-{순차번호}-{keyword}`
- 예시: `TODO-001-state-transition-validation`
- 규칙:
  - 순차적 번호 부여
  - 키워드는 작업 내용에서 의미 있는 단어 추출
  - 키워드 최대 30자

**Test ID**:
- 형식: `TEST-{순차번호}-{keyword}`
- 예시: `TEST-001-state-transition-test`
- 규칙:
  - 순차적 번호 부여
  - 키워드는 관련 TODO의 키워드 사용 또는 테스트 내용에서 추출
  - 키워드 최대 30자

**Troubleshooting ID**:
- 형식: `TROUBLESHOOT-{순차번호}-{keyword}`
- 예시: `TROUBLESHOOT-001-action-generation-issue`
- 규칙:
  - 순차적 번호 부여
  - 키워드는 문제 내용에서 의미 있는 단어 추출
  - 키워드 최대 30자

**QA ID**:
- 형식: `QA-{순차번호}-{keyword}`
- 예시: `QA-001-state-transition-qa`
- 규칙:
  - 순차적 번호 부여
  - 키워드는 관련 TODO의 키워드 사용
  - 키워드 최대 30자

**Audit ID**:
- 형식: `AUDIT-{순차번호}-{keyword}`
- 예시: `AUDIT-001-state-transition-audit`
- 규칙:
  - 순차적 번호 부여
  - 키워드는 관련 QA의 키워드 사용
  - 키워드 최대 30자

**Documentation Update ID**:
- 형식: `DOC-UPDATE-{순차번호}-{keyword}`
- 예시: `DOC-UPDATE-001-object-interaction-docs`
- 규칙:
  - 순차적 번호 부여
  - 키워드는 관련 Epic의 키워드 사용 또는 문서 타입 포함
  - 키워드 최대 40자

**Permanent Docs ID**:
- 형식: `PERM-DOC-{순차번호}-{keyword}`
- 예시: `PERM-DOC-001-object-interaction-changelog`
- 규칙:
  - 순차적 번호 부여
  - 키워드는 관련 Epic의 키워드 사용 또는 문서 타입 포함
  - 키워드 최대 40자

---

## 문서 작성 규칙

### 규칙 1: 필수 메타데이터 (MUST)

**에이전트는 문서를 작성할 때 반드시 다음 형식을 준수해야 함:**

#### Ideation 문서 (순서 1-3)

```markdown
---
id: ideation-{category}-{title-slug}-{ideation_type}
type: ideation
ideation_type: status|methodology|plan
status: ideation
category: {category}
priority: high|medium|low
created_at: {YYYY-MM-DDTHH:MM:SSZ}
updated_at: {YYYY-MM-DDTHH:MM:SSZ}
author: agent|user
epic_id: null
related_ideations: []
---

# {제목}

## 설명
{내용}
```

#### Epic 문서 (순서 4)

```markdown
---
id: EPIC-{번호}-{keyword}
type: epic
status: epic
ideation_ids: []
tasks: []
keyword: {keyword}
created_at: {YYYY-MM-DDTHH:MM:SSZ}
updated_at: {YYYY-MM-DDTHH:MM:SSZ}
author: agent|user
---

# {제목}

## 설명
{내용}
```

#### Task 문서 (순서 5)

```markdown
---
id: TASK-{번호}-{keyword}
type: task
status: task
epic_id: EPIC-{번호}-{keyword}
dependencies: []
todos: []
estimated_hours: {숫자}
keyword: {keyword}
created_at: {YYYY-MM-DDTHH:MM:SSZ}
updated_at: {YYYY-MM-DDTHH:MM:SSZ}
author: agent|user
---

# {제목}

## 설명
{내용}
```

#### TODO 문서 (순서 6)

```markdown
---
id: TODO-{번호}-{keyword}
type: todo
status: development
sub_status: requirement|test_red|implement_green|refactor|quality_gate
task_id: TASK-{번호}-{keyword}
file: {파일 경로}
line: {라인 번호}
code_snippet: {코드 스니펫}
keyword: {keyword}
created_at: {YYYY-MM-DDTHH:MM:SSZ}
updated_at: {YYYY-MM-DDTHH:MM:SSZ}
author: agent|user
---

# {제목}

## 설명
{내용}
```

#### Test 문서 (순서 7)

```markdown
---
id: TEST-{번호}-{keyword}
type: test
status: development
todo_id: TODO-{번호}-{keyword}
test_file: {테스트 파일 경로}
test_results:
  passed: {숫자}
  failed: {숫자}
  skipped: {숫자}
coverage: {0.0-1.0}
keyword: {keyword}
created_at: {YYYY-MM-DDTHH:MM:SSZ}
updated_at: {YYYY-MM-DDTHH:MM:SSZ}
author: agent|user
---

# {제목}

## 설명
{내용}
```

#### Troubleshooting 문서 (순서 8)

```markdown
---
id: TROUBLESHOOT-{번호}-{keyword}
type: troubleshooting
status: development
related_todo_id: TODO-{번호}-{keyword}
related_test_id: TEST-{번호}-{keyword}
issue_description: {문제 설명}
solution: {해결 방법}
resolved: true|false
keyword: {keyword}
created_at: {YYYY-MM-DDTHH:MM:SSZ}
updated_at: {YYYY-MM-DDTHH:MM:SSZ}
author: agent|user
---

# {제목}

## 설명
{내용}
```

#### QA 문서 (순서 9)

```markdown
---
id: QA-{번호}-{keyword}
type: qa
status: qa
todo_id: TODO-{번호}-{keyword}
test_id: TEST-{번호}-{keyword}
qa_results:
  all_tests_passed: true|false
  coverage: {0.0-1.0}
  linter_errors: {숫자}
  type_check_passed: true|false
quality_score: {0.0-10.0}
keyword: {keyword}
created_at: {YYYY-MM-DDTHH:MM:SSZ}
updated_at: {YYYY-MM-DDTHH:MM:SSZ}
author: agent|user
---

# {제목}

## 설명
{내용}
```

#### Audit 문서 (순서 10)

```markdown
---
id: AUDIT-{번호}-{keyword}
type: audit
status: audit
qa_id: QA-{번호}-{keyword}
audit_results:
  three_layer_architecture: pass|fail|warning
  uuid_compliance: pass|fail|warning
  data_centric: pass|fail|warning
  type_safety: pass|fail|warning
  async_first: pass|fail|warning
  transactions: pass|fail|warning
  migrations: pass|fail|warning
overall_compliance: pass|fail|warning
violations: []
keyword: {keyword}
created_at: {YYYY-MM-DDTHH:MM:SSZ}
updated_at: {YYYY-MM-DDTHH:MM:SSZ}
author: agent|user
---

# {제목}

## 설명
{내용}
```

#### Documentation Update 문서 (순서 11)

```markdown
---
id: DOC-UPDATE-{번호}-{keyword}
type: documentation-update
status: documentation
related_epic_id: EPIC-{번호}-{keyword}
updated_documents: []
keyword: {keyword}
created_at: {YYYY-MM-DDTHH:MM:SSZ}
updated_at: {YYYY-MM-DDTHH:MM:SSZ}
author: agent|user
---

# {제목}

## 설명
{내용}
```

#### Done 문서 (순서 12)

```markdown
---
id: {원본ID}
type: {원본타입}
status: done
completed_at: {YYYY-MM-DDTHH:MM:SSZ}
original_path: {원본 경로}
created_at: {YYYY-MM-DDTHH:MM:SSZ}
updated_at: {YYYY-MM-DDTHH:MM:SSZ}
author: agent|user
---

# {제목} (완료)

## 설명
{내용}
```

#### Deprecated 문서 (순서 13)

```markdown
---
id: {원본ID}
type: {원본타입}
status: deprecated
deprecated_at: {YYYY-MM-DDTHH:MM:SSZ}
deprecated_reason: {사유}
original_path: {원본 경로}
created_at: {YYYY-MM-DDTHH:MM:SSZ}
updated_at: {YYYY-MM-DDTHH:MM:SSZ}
author: agent|user
---

# {제목} (Deprecated)

**Deprecated 사유**: {사유}

## 원본 내용
{내용}
```

#### Permanent Docs 문서 (순서 14)

```markdown
---
id: PERM-DOC-{번호}-{keyword}
type: permanent-docs
status: permanent
related_epic_id: EPIC-{번호}-{keyword}
document_types: []
target_files: []
keyword: {keyword}
created_at: {YYYY-MM-DDTHH:MM:SSZ}
updated_at: {YYYY-MM-DDTHH:MM:SSZ}
author: agent|user
---

# {제목}

## 설명
{내용}
```

### 필수 체크리스트

**문서 저장 전 반드시 확인:**

- [ ] YAML frontmatter가 있는가?
- [ ] `id` 필드가 있고 유효한가?
- [ ] `type` 필드가 있고 유효한가?
- [ ] `status` 필드가 있고 유효한가?
- [ ] `created_at` 필드가 있고 ISO 형식인가?
- [ ] `updated_at` 필드가 있고 ISO 형식인가?
- [ ] ideation인 경우 `ideation_type`, `category`, `priority`가 있는가?
- [ ] 연결 정보가 있으면 명시되어 있는가?
- [ ] 파일명이 규칙에 맞는가?

**❌ 위 항목 중 하나라도 없으면 문서 저장 금지**

---

## 상태 전환 규칙

### 규칙 2: 순차적 상태 전환 (MUST)

**에이전트는 상태를 변경할 때 반드시 다음 순서를 준수해야 함:**

#### 2.1 Ideation 단계 전환 (순서 1→2→3)

**1→2: status → methodology**
- **필수 작업**:
  1. Methodology 문서 생성: `ideation-{category}-{title-slug}-methodology.md`
  2. Methodology 문서에 `related_ideations`에 status 문서 연결 (`relation: based_on`)
  3. **원본 status 문서 업데이트** (반드시):
     - `related_ideations`에 methodology 문서 추가 (`relation: followed_by`)
     - `updated_at` 업데이트

**2→3: methodology → plan**
- **필수 작업**:
  1. Plan 문서 생성: `ideation-{category}-{title-slug}-plan.md`
  2. Plan 문서에 `related_ideations`에 status, methodology 문서 연결
  3. **원본 status, methodology 문서 업데이트** (반드시):
     - `related_ideations`에 plan 문서 추가
     - `updated_at` 업데이트

**3→4: methodology → plan**
- **필수 작업**:
  1. Plan 문서 생성: `ideation-{category}-{title-slug}-plan.md`
  2. Plan 문서에 `related_ideations`에 problem-definition, status, methodology 문서 연결
  3. **원본 problem-definition, status, methodology 문서 업데이트** (반드시):
     - `related_ideations`에 plan 문서 추가
     - `updated_at` 업데이트

**4→5: plan → epic**
- **필수 작업**:
  1. Epic 문서 생성: `EPIC-{번호}-{keyword}.md`
  2. **키워드 추출**: 관련 ideation의 `category`와 `title-slug`에서 추출
  3. Epic 문서에 `ideation_ids`에 모든 관련 ideation ID 추가
  4. **원본 plan 문서 업데이트** (반드시):
     - `status: epic` 변경 (또는 `epic_id` 추가)
     - `updated_at` 업데이트
  5. **관련 problem-definition, status, methodology 문서 업데이트** (권장):
     - `epic_id` 추가
     - `updated_at` 업데이트

#### 2.2 Development 단계 전환 (순서 4→5→6→7→8)

**5→6: epic → task**
- **필수 작업**:
  1. Task 문서 생성: `TASK-{번호}-{keyword}.md`
  2. Task 문서에 `epic_id: EPIC-{번호}-{keyword}` 명시
  3. **키워드 추출**: 작업 내용에서 의미 있는 키워드 추출 (최대 30자)
  4. **원본 epic 문서 업데이트** (반드시):
     - `tasks: [TASK-{번호}-{keyword}]` 추가
     - `updated_at` 업데이트

**6→7: task → todo**
- **필수 작업**:
  1. TODO 문서 생성: `TODO-{번호}-{keyword}.md`
  2. TODO 문서에 `task_id: TASK-{번호}-{keyword}` 명시
  3. **키워드 추출**: 작업 내용에서 의미 있는 키워드 추출 (최대 30자)
  4. **원본 task 문서 업데이트** (반드시):
     - `todos: [TODO-{번호}-{keyword}]` 추가
     - `updated_at` 업데이트

**7→8: todo → test**
- **필수 작업**:
  1. Test 문서 생성: `TEST-{번호}-{keyword}.md`
  2. Test 문서에 `todo_id: TODO-{번호}-{keyword}` 명시
  3. **키워드 추출**: TODO의 키워드 사용 또는 테스트 내용에서 추출 (최대 30자)
  4. **원본 TODO 문서 업데이트** (반드시):
     - `status: development` 유지
     - `sub_status: quality_gate` 변경
     - `updated_at` 업데이트

**7→9: todo → troubleshooting** (문제 발생 시)
- **필수 작업**:
  1. Troubleshooting 문서 생성: `TROUBLESHOOT-{번호}-{keyword}.md`
  2. Troubleshooting 문서에 `related_todo_id: TODO-{번호}-{keyword}` 명시
  3. **키워드 추출**: 문제 내용에서 의미 있는 키워드 추출 (최대 30자)
  4. **원본 TODO 문서 업데이트** (반드시):
     - `status: development` 유지
     - `updated_at` 업데이트

**8→10: test → qa** (테스트 통과 시)
- **필수 작업**:
  1. QA 문서 생성: `QA-{번호}-{keyword}.md`
  2. QA 문서에 `todo_id: TODO-{번호}-{keyword}`, `test_id: TEST-{번호}-{keyword}` 명시
  3. **키워드 추출**: TODO의 키워드 사용 (최대 30자)
  4. **원본 TODO, Test 문서 업데이트** (반드시):
     - TODO: `status: qa` 변경
     - Test: `updated_at` 업데이트

**8→9: test → troubleshooting** (테스트 실패 시)
- **필수 작업**:
  1. Troubleshooting 문서 생성: `TROUBLESHOOT-{번호}-{keyword}.md`
  2. Troubleshooting 문서에 `related_test_id: TEST-{번호}-{keyword}` 명시
  3. **키워드 추출**: 문제 내용에서 의미 있는 키워드 추출 (최대 30자)
  4. **원본 Test 문서 업데이트** (반드시):
     - `updated_at` 업데이트

**9→7: troubleshooting → todo** (문제 해결 시)
- **필수 작업**:
  1. Troubleshooting 문서에 `resolved: true` 설정
  2. **원본 TODO 문서 업데이트** (반드시):
     - `status: development` 유지
     - `updated_at` 업데이트

#### 2.3 Audit 단계 전환 (순서 9→10)

**10→11: qa → audit**
- **필수 작업**:
  1. Audit 문서 생성: `AUDIT-{번호}-{keyword}.md`
  2. Audit 문서에 `qa_id: QA-{번호}-{keyword}` 명시
  3. **키워드 추출**: QA의 키워드 사용 (최대 30자)
  4. **원본 QA 문서 업데이트** (반드시):
     - `status: audit` 변경
     - `updated_at` 업데이트

**11→12: audit → documentation-update** (규칙 준수 시)
- **필수 작업**:
  1. Documentation Update 문서 생성: `DOC-UPDATE-{번호}-{keyword}.md`
  2. Documentation Update 문서에 `related_epic_id: EPIC-{번호}-{keyword}` 명시
  3. **키워드 추출**: Epic의 키워드 사용 또는 문서 타입 포함 (최대 40자)
  4. **원본 Audit 문서 업데이트** (반드시):
     - `updated_at` 업데이트

**11→7: audit → todo** (규칙 위반 시)
- **필수 작업**:
  1. Audit 문서에 `overall_compliance: fail` 설정
  2. **원본 TODO 문서 업데이트** (반드시):
     - `status: development` 변경
     - `updated_at` 업데이트

#### 2.4 종결 단계 전환 (순서 11→12→13→14)

**12→13: documentation-update → done**
- **필수 작업**:
  1. Done 문서 생성: `DONE-{원본ID}.md`
  2. Done 문서에 원본 정보 복사
  3. **원본 문서 업데이트** (반드시):
     - `status: done` 변경
     - `completed_at` 추가
     - `updated_at` 업데이트
  4. **원본 문서를 done 폴더로 이동**

**13→14: done → deprecated** (선택사항)
- **필수 작업**:
  1. Deprecated 문서 생성: `[deprecated]{원본ID}.md`
  2. Deprecated 문서에 `deprecated_reason` 명시
  3. **원본 Done 문서 업데이트** (반드시):
     - `status: deprecated` 변경
     - `deprecated_at` 추가
     - `updated_at` 업데이트
  4. **원본 문서를 deprecated 폴더로 이동**

**13→15 또는 14→15: done/deprecated → permanent-docs**
- **필수 작업**:
  1. Permanent Docs 문서 생성: `PERM-DOC-{번호}-{keyword}.md`
  2. Permanent Docs 문서에 `related_epic_id: EPIC-{번호}-{keyword}` 명시
  3. **키워드 추출**: Epic의 키워드 사용 또는 문서 타입 포함 (최대 40자)
  4. **항구 보존 문서 업데이트**:
     - `docs/changelog/CHANGELOG.md` 업데이트
     - `docs/rules/*.md` 업데이트 (필요 시)
     - `docs/architecture/*.md` 업데이트 (필요 시)
     - `docs/api/*.md` 업데이트 (필요 시)

---

## 문서 관계 모델

### 관계 타입 정의

**문서 간 관계는 다음 타입으로 명시:**

| 관계 타입 | 의미 | 방향성 | 예시 |
|----------|------|--------|------|
| `based_on` | 기반으로 함 | 단방향 | methodology → status |
| `plan_of` | 계획 | 단방향 | plan → status |
| `followed_by` | 다음 단계 | 단방향 | status → methodology |
| `parent_of` | 상위 문서 | 단방향 | epic → task |
| `child_of` | 하위 문서 | 단방향 | task → epic |
| `depends_on` | 의존성 | 단방향 | task → task |
| `related_to` | 관련 있음 | 양방향 | ideation → ideation |
| `replaces` | 대체함 | 단방향 | new → old |
| `validates` | 검증함 | 단방향 | qa → todo |
| `audits` | 감사함 | 단방향 | audit → qa |

### 관계 표현 방법

**메타데이터에서 관계 표현:**

```yaml
related_ideations:
  - id: ideation-{category}-{title-slug}-status
    relation: based_on
    direction: incoming  # incoming|outgoing|bidirectional
```

**양방향 연결 규칙**:
- 관계가 `parent_of`, `child_of`, `validates`, `audits`인 경우 양방향 연결 필수
- 한쪽 문서에 관계를 추가하면 반대쪽 문서도 자동 업데이트

---

## 네이밍 컨벤션

### 파일명 네이밍 규칙

#### Ideation 파일명
- **형식**: `ideation-{category}-{title-slug}-{ideation_type}.md`
- **규칙**:
  - 소문자만 사용
  - 단어는 하이픈(`-`)으로 구분
  - `ideation_type`은 반드시 포함: `status`, `methodology`, `plan`
- **예시**:
  - ✅ `ideation-object-interaction-current-status.md`
  - ✅ `ideation-object-interaction-solution-methodology.md`
  - ✅ `ideation-object-interaction-enhancement-plan.md`
  - ❌ `ideation-object-interaction-status.md` (ideation_type 누락)

#### Epic/Task/TODO/Test/QA/Audit 파일명
- **형식**: `{TYPE}-{순차번호}.md`
- **규칙**:
  - 대문자 타입 코드 사용
  - 순차적 번호 (001, 002, 003, ...)
  - 3자리 숫자 (001-999)
- **예시**:
  - ✅ `EPIC-001.md`
  - ✅ `TASK-001.md`
  - ✅ `TODO-001.md`
  - ✅ `TEST-001.md`
  - ✅ `QA-001.md`
  - ✅ `AUDIT-001.md`
  - ❌ `epic-001.md` (소문자)
  - ❌ `EPIC-1.md` (1자리 숫자)

#### Troubleshooting 파일명
- **형식**: `TROUBLESHOOT-{순차번호}.md`
- **예시**: `TROUBLESHOOT-001.md`

#### Documentation Update 파일명
- **형식**: `DOC-UPDATE-{순차번호}.md`
- **예시**: `DOC-UPDATE-001.md`

#### Done 파일명
- **형식**: `DONE-{원본ID}.md`
- **예시**: 
  - `DONE-EPIC-001.md`
  - `DONE-ideation-object-interaction-enhancement-plan.md`

#### Deprecated 파일명
- **형식**: `[deprecated]{원본ID}.md`
- **예시**: 
  - `[deprecated]EPIC-001.md`
  - `[deprecated]ideation-object-interaction-current-status.md`

#### Permanent Docs 파일명
- **형식**: `PERM-DOC-{순차번호}.md`
- **예시**: `PERM-DOC-001.md`

### ID 네이밍 규칙

#### Ideation ID
- **형식**: `ideation-{category}-{title-slug}-{ideation_type}`
- **규칙**: 파일명과 동일 (확장자 제외)
- **예시**: `ideation-object-interaction-current-status`

#### Epic/Task/TODO/Test/QA/Audit ID
- **형식**: `{TYPE}-{순차번호}`
- **규칙**: 파일명과 동일 (확장자 제외)
- **예시**: `EPIC-001`, `TASK-001`, `TODO-001`

#### Troubleshooting ID
- **형식**: `TROUBLESHOOT-{순차번호}`
- **예시**: `TROUBLESHOOT-001`

#### Documentation Update ID
- **형식**: `DOC-UPDATE-{순차번호}`
- **예시**: `DOC-UPDATE-001`

#### Permanent Docs ID
- **형식**: `PERM-DOC-{순차번호}`
- **예시**: `PERM-DOC-001`

### 카테고리 네이밍 규칙

**카테고리는 소문자, 하이픈 구분:**

- ✅ `object-interaction`
- ✅ `action-handler`
- ✅ `item-equipment`
- ✅ `world-editor`
- ❌ `ObjectInteraction` (대문자)
- ❌ `object_interaction` (언더스코어)

---

## 연결고리 설정 규칙

### 규칙 3: 양방향 연결 필수 (MUST)

**에이전트는 문서를 참조할 때 반드시 양방향 연결을 설정해야 함:**

#### 3.1 Ideation 간 연결

**필수 작업**:
1. 관련 ideation 문서 찾기
2. 양쪽 문서 모두 `related_ideations`에 추가
3. `relation` 타입 명시 (`based_on`, `plan_of`, `followed_by` 등)
4. `updated_at` 업데이트

**예시**:
```yaml
# status 문서
related_ideations:
  - id: ideation-object-interaction-enhancement-plan
    relation: followed_by

# plan 문서
related_ideations:
  - id: ideation-object-interaction-current-status
    relation: plan_of
```

#### 3.2 Epic 생성 시

**필수 작업**:
1. **키워드 추출**: 관련 ideation의 `category`와 `title-slug`에서 추출
   - 예: `ideation-object-interaction-enhancement-plan` → `object-interaction-enhancement`
2. Epic 문서 작성: `EPIC-{번호}-{keyword}.md`
3. Epic 문서에 `ideation_ids`에 모든 관련 ideation ID 추가
4. **원본 ideation 문서들 업데이트** (반드시):
   - `epic_id: EPIC-{번호}-{keyword}` 추가
   - `updated_at` 업데이트

#### 3.3 Task 생성 시

**필수 작업**:
1. **키워드 추출**: 작업 내용에서 의미 있는 단어 추출 (최대 30자)
2. Task 문서 작성: `TASK-{번호}-{keyword}.md`
3. Task 문서에 `epic_id: EPIC-{번호}-{keyword}` 명시
4. **원본 epic 문서 업데이트** (반드시):
   - `tasks: [TASK-{번호}-{keyword}]` 추가
   - `updated_at` 업데이트

#### 3.4 TODO 생성 시

**필수 작업**:
1. **키워드 추출**: 작업 내용에서 의미 있는 단어 추출 (최대 30자)
2. TODO 문서 작성: `TODO-{번호}-{keyword}.md`
3. TODO 문서에 `task_id: TASK-{번호}-{keyword}` 명시
4. **원본 task 문서 업데이트** (반드시):
   - `todos: [TODO-{번호}-{keyword}]` 추가
   - `updated_at` 업데이트

#### 3.5 Test 생성 시

**필수 작업**:
1. **키워드 추출**: TODO의 키워드 사용 또는 테스트 내용에서 추출 (최대 30자)
2. Test 문서 작성: `TEST-{번호}-{keyword}.md`
3. Test 문서에 `todo_id: TODO-{번호}-{keyword}` 명시
4. **원본 TODO 문서 업데이트** (반드시):
   - `sub_status: quality_gate` 변경
   - `updated_at` 업데이트

#### 3.6 QA 생성 시

**필수 작업**:
1. **키워드 추출**: TODO의 키워드 사용 (최대 30자)
2. QA 문서 작성: `QA-{번호}-{keyword}.md`
3. QA 문서에 `todo_id: TODO-{번호}-{keyword}`, `test_id: TEST-{번호}-{keyword}` 명시
4. **원본 TODO 문서 업데이트** (반드시):
   - `status: qa` 변경
   - `updated_at` 업데이트

#### 3.7 Audit 생성 시

**필수 작업**:
1. **키워드 추출**: QA의 키워드 사용 (최대 30자)
2. Audit 문서 작성: `AUDIT-{번호}-{keyword}.md`
3. Audit 문서에 `qa_id: QA-{번호}-{keyword}` 명시
4. **원본 QA 문서 업데이트** (반드시):
   - `status: audit` 변경
   - `updated_at` 업데이트

---

## 기존 문서 처리 규칙

### 규칙 4: 기존 문서 마이그레이션

**에이전트는 기존 문서를 처리할 때 다음 규칙을 준수해야 함:**

#### 4.1 기존 문서 발견 시

**필수 작업**:
1. 문서 읽기
2. YAML frontmatter가 있는지 확인
3. 없으면 **반드시 추가**:
   - `id`: 파일명에서 추출하거나 생성
   - `type`: 문서 내용 분석하여 추론
   - `status`: 문서 내용 분석하여 추론
   - `ideation_type`: 내용 분석하여 추론 (status, methodology, plan)
   - `category`: 폴더 구조 또는 파일명에서 추론
   - `priority`: 내용 분석하여 추론 (high/medium/low)
   - `created_at`: 파일 생성일 또는 문서 내 날짜
   - `updated_at`: 파일 수정일 또는 오늘 날짜
4. 문서 업데이트

#### 4.2 구현 완료 문서 감지

**필수 작업**:
1. 문서 내용 분석
2. "구현 완료", "완성", "완료", "✅" 등의 키워드 확인
3. 실제 코드베이스 확인 (가능한 경우)
4. 완료 확인되면:
   - `status: done` 변경
   - 또는 `status: deprecated` 변경 (모든 관련 작업 완료 시)

#### 4.3 기존 문서 위치 마이그레이션

**기존 위치**:
- `docs/ideation/{category}/{TITLE}.md`
- `docs/project-management/epics/{EPIC_ID}.md`
- `docs/project-management/tasks/{TASK_ID}.md`

**새 위치**:
- `docs/work-items/ideation/ideation-{category}-{title-slug}-{ideation_type}.md`
- `docs/work-items/epic/EPIC-{번호}.md`
- `docs/work-items/task/TASK-{번호}.md`

**마이그레이션 규칙**:
```
기존 문서를 새 구조로 마이그레이션할 때:
1. 문서를 읽는다
2. 메타데이터를 추가한다 (없는 경우)
3. ideation_type을 추론한다 (status, methodology, plan)
4. 새 위치로 이동한다
5. 파일명을 새 규칙에 맞게 변경한다
6. 원본 문서는 삭제한다 (또는 백업)
```

---

## 검증 규칙

### 규칙 5: 저장 전 필수 검증

**에이전트는 문서를 저장하기 전에 반드시 다음을 확인해야 함:**

#### 5.1 메타데이터 검증

**체크리스트**:
- [ ] YAML frontmatter가 있는가?
- [ ] `id` 필드가 있고 유효한가?
- [ ] `type` 필드가 있고 유효한가?
- [ ] `status` 필드가 있고 유효한가?
- [ ] `created_at` 필드가 있고 ISO 형식인가?
- [ ] `updated_at` 필드가 있고 ISO 형식인가?
- [ ] ideation인 경우 `ideation_type`, `category`, `priority`가 있는가?
- [ ] 파일명이 규칙에 맞는가?

**❌ 하나라도 없으면 저장 금지**

#### 5.2 연결 정보 일관성 검증

**체크리스트**:
- [ ] Epic 문서에 `ideation_ids`가 있으면, 해당 ideation 문서들에도 `epic_id`가 있는가?
- [ ] Task 문서에 `epic_id`가 있으면, 해당 epic 문서의 `tasks` 배열에 포함되어 있는가?
- [ ] TODO 문서에 `task_id`가 있으면, 해당 task 문서의 `todos` 배열에 포함되어 있는가?
- [ ] Test 문서에 `todo_id`가 있으면, 해당 TODO 문서의 `sub_status`가 `quality_gate`인가?
- [ ] QA 문서에 `todo_id`, `test_id`가 있으면, 해당 문서들이 연결되어 있는가?
- [ ] Audit 문서에 `qa_id`가 있으면, 해당 QA 문서의 `status`가 `audit`인가?
- [ ] 양방향 연결이 되어 있는가?

**❌ 일관성이 없으면 저장 금지**

#### 5.3 상태 전환 검증

**체크리스트**:
- [ ] 상태를 변경했으면 원본 문서도 업데이트했는가?
- [ ] `updated_at`을 업데이트했는가?
- [ ] 파일이 올바른 폴더에 있는가?
- [ ] 순서가 올바른가? (1→2→3→...→14)

**❌ 검증 실패 시 저장 금지**

#### 5.4 파일명 검증

**체크리스트**:
- [ ] 파일명이 규칙에 맞는가?
- [ ] ID가 파일명에 포함되어 있는가?
- [ ] ideation인 경우 `ideation_type`이 파일명에 포함되어 있는가?
- [ ] deprecated인 경우 `[deprecated]` 접두어가 있는가?

**❌ 파일명 규칙 위반 시 저장 금지**

---

## 실제 사용 예시

### 예시 1: Ideation 단계 (순서 1-3)

**사용자 요청**:
```
"오브젝트 상호작용 기능의 현재 상황 파악 및 고도화"
```

**에이전트가 해야 할 일**:

#### 1단계: 문제 정의 및 현황 진단 (순서 1)

1. **ID 생성**: `ideation-object-interaction-current-status`
2. **파일 경로**: `docs/work-items/ideation/ideation-object-interaction-current-status.md`
3. **문서 작성**:
```markdown
---
id: ideation-object-interaction-current-status
type: ideation
ideation_type: status
status: ideation
category: object-interaction
priority: high
created_at: 2026-01-01T12:00:00Z
updated_at: 2026-01-01T12:00:00Z
author: agent
epic_id: null
related_ideations: []
---

# 오브젝트 상호작용 기능 현재 상황 파악

## 설명
오브젝트 상호작용 시스템의 현재 구현 상태를 종합적으로 분석합니다.
```

#### 2단계: 방법론 검토 (순서 2)

1. **ID 생성**: `ideation-object-interaction-solution-methodology`
2. **파일 경로**: `docs/work-items/ideation/ideation-object-interaction-solution-methodology.md`
3. **문서 작성**:
```markdown
---
id: ideation-object-interaction-solution-methodology
type: ideation
ideation_type: methodology
status: ideation
category: object-interaction
priority: high
created_at: 2026-01-01T12:30:00Z
updated_at: 2026-01-01T12:30:00Z
author: agent
epic_id: null
related_ideations:
  - id: ideation-object-interaction-current-status
    relation: based_on
---

# 오브젝트 상호작용 해결 방법론 검토

## 설명
현황 분석을 기반으로 해결 방법론을 검토합니다.
```

4. **원본 status 문서 업데이트**:
```yaml
related_ideations:
  - id: ideation-object-interaction-solution-methodology
    relation: followed_by
```

#### 3단계: 실행 계획 수립 (순서 3)

1. **ID 생성**: `ideation-object-interaction-enhancement-plan`
2. **파일 경로**: `docs/work-items/ideation/ideation-object-interaction-enhancement-plan.md`
3. **문서 작성**:
```markdown
---
id: ideation-object-interaction-enhancement-plan
type: ideation
ideation_type: plan
status: ideation
category: object-interaction
priority: high
created_at: 2026-01-01T13:00:00Z
updated_at: 2026-01-01T13:00:00Z
author: agent
epic_id: null
related_ideations:
  - id: ideation-object-interaction-current-status
    relation: plan_of
  - id: ideation-object-interaction-solution-methodology
    relation: based_on
---

# 오브젝트 상호작용 기능 고도화 계획

## 설명
방법론 검토를 기반으로 구체적인 실행 계획을 수립합니다.
```

4. **원본 status, methodology 문서 업데이트**:
```yaml
# status 문서
related_ideations:
  - id: ideation-object-interaction-solution-methodology
    relation: followed_by
  - id: ideation-object-interaction-enhancement-plan
    relation: plan_of

# methodology 문서
related_ideations:
  - id: ideation-object-interaction-current-status
    relation: based_on
  - id: ideation-object-interaction-enhancement-plan
    relation: followed_by
```

---

### 예시 2: Epic 생성 및 연결 (순서 4)

**사용자 요청**:
```
"이 plan ideation을 Epic으로 만들어주세요"
```

**에이전트가 해야 할 일**:

1. **원본 plan 문서 읽기**
2. **키워드 추출**: `ideation-object-interaction-enhancement-plan` → `object-interaction-enhancement`
3. **Epic ID 생성**: `EPIC-001-object-interaction-enhancement` (기존 Epic 확인 후 다음 번호)
4. **Epic 문서 생성**:
   - 파일: `docs/work-items/04-epic/EPIC-001-object-interaction-enhancement.md`
   - 내용:
```markdown
---
id: EPIC-001-object-interaction-enhancement
type: epic
status: epic
ideation_ids:
  - ideation-object-interaction-current-status
  - ideation-object-interaction-solution-methodology
  - ideation-object-interaction-enhancement-plan
tasks: []
keyword: object-interaction-enhancement
created_at: 2026-01-01T14:00:00Z
updated_at: 2026-01-01T14:00:00Z
author: agent
---

# 오브젝트 상호작용 기능 고도화

## 설명
오브젝트 상호작용 시스템을 고도화합니다.
```

5. **원본 ideation 문서들 업데이트** (반드시):
```yaml
# plan 문서
epic_id: EPIC-001-object-interaction-enhancement
status: epic  # 또는 ideation 유지

# status 문서
epic_id: EPIC-001-object-interaction-enhancement

# methodology 문서
epic_id: EPIC-001-object-interaction-enhancement
```

---

### 예시 3: Task 생성 및 연결 (순서 5)

**사용자 요청**:
```
"이 Epic을 Task로 분해해주세요"
```

**에이전트가 해야 할 일**:

1. **원본 epic 문서 읽기**
2. **키워드 추출**: "액션 생성 로직 보완" → `action-generation-logic`
3. **Task ID 생성**: `TASK-001-action-generation-logic` (기존 Task 확인 후 다음 번호)
4. **Task 문서 생성**:
   - 파일: `docs/work-items/05-task/TASK-001-action-generation-logic.md`
   - 내용:
```markdown
---
id: TASK-001-action-generation-logic
type: task
status: task
epic_id: EPIC-001-object-interaction-enhancement
dependencies: []
todos: []
estimated_hours: 4.0
keyword: action-generation-logic
created_at: 2026-01-01T15:00:00Z
updated_at: 2026-01-01T15:00:00Z
author: agent
---

# 액션 생성 로직 보완

## 설명
상태 전이 규칙 검증 강화 및 조건부 액션 처리 보완
```

5. **원본 epic 문서 업데이트** (반드시):
```yaml
tasks:
  - TASK-001-action-generation-logic
  - TASK-002-state-filtering-enhancement
```

---

### 예시 4: TODO 생성 및 TDD 프로세스 (순서 6)

**사용자 요청**:
```
"이 Task를 TODO로 만들어서 개발 시작해주세요"
```

**에이전트가 해야 할 일**:

1. **원본 task 문서 읽기**
2. **키워드 추출**: "상태 전이 규칙 검증 강화" → `state-transition-validation`
3. **TODO ID 생성**: `TODO-001-state-transition-validation` (기존 TODO 확인 후 다음 번호)
4. **TODO 문서 생성** (TDD 프로세스):
   - 파일: `docs/work-items/06-development/TODO-001-state-transition-validation.md`
   - 내용:
```markdown
---
id: TODO-001-state-transition-validation
type: todo
status: development
sub_status: requirement
task_id: TASK-001-action-generation-logic
file: app/services/gameplay/action_service.py
line: 327
code_snippet: |
  # 상태 전이 규칙 검증 강화 필요
keyword: state-transition-validation
created_at: 2026-01-01T16:00:00Z
updated_at: 2026-01-01T16:00:00Z
author: agent
---

# 상태 전이 규칙 검증 강화

## 설명
액션 생성 로직에 상태 전이 규칙 검증을 강화합니다.
```

5. **TDD 프로세스 진행**:
   - `sub_status: requirement` → 요구사항 정의
   - `sub_status: test_red` → 실패하는 테스트 작성
   - `sub_status: implement_green` → 테스트 통과하는 코드 구현
   - `sub_status: refactor` → 리팩토링
   - `sub_status: quality_gate` → 품질 게이트 통과

6. **원본 task 문서 업데이트** (반드시):
```yaml
todos:
  - TODO-001-state-transition-validation
```

---

### 예시 5: Test 생성 (순서 7)

**TODO의 `sub_status: quality_gate` 통과 시:**

1. **키워드 추출**: TODO의 키워드 사용 → `state-transition-test`
2. **Test 문서 생성**:
   - 파일: `docs/work-items/06-development/TEST-001-state-transition-test.md`
   - 내용:
```markdown
---
id: TEST-001-state-transition-test
type: test
status: development
todo_id: TODO-001-state-transition-validation
test_file: tests/test_action_service.py
test_results:
  passed: 10
  failed: 0
  skipped: 0
coverage: 0.95
keyword: state-transition-test
created_at: 2026-01-01T17:00:00Z
updated_at: 2026-01-01T17:00:00Z
author: agent
---

# 상태 전이 규칙 검증 테스트

## 설명
상태 전이 규칙 검증 로직에 대한 테스트
```

3. **원본 TODO 문서 업데이트** (반드시):
```yaml
sub_status: quality_gate
```

---

### 예시 6: QA 생성 (순서 9)

**Test 통과 및 커버리지 기준 충족 시:**

1. **키워드 추출**: TODO의 키워드 사용 → `state-transition-qa`
2. **QA 문서 생성**:
   - 파일: `docs/work-items/09-qa/QA-001-state-transition-qa.md`
   - 내용:
```markdown
---
id: QA-001-state-transition-qa
type: qa
status: qa
todo_id: TODO-001-state-transition-validation
test_id: TEST-001-state-transition-test
qa_results:
  all_tests_passed: true
  coverage: 0.95
  linter_errors: 0
  type_check_passed: true
quality_score: 9.0
keyword: state-transition-qa
created_at: 2026-01-01T18:00:00Z
updated_at: 2026-01-01T18:00:00Z
author: agent
---

# 상태 전이 규칙 검증 QA

## 설명
상태 전이 규칙 검증 로직에 대한 QA 결과
```

3. **원본 TODO 문서 업데이트** (반드시):
```yaml
status: qa
```

---

### 예시 7: Audit 생성 (순서 10)

**QA 통과 시:**

1. **키워드 추출**: QA의 키워드 사용 → `state-transition-audit`
2. **Audit 문서 생성**:
   - 파일: `docs/work-items/10-audit/AUDIT-001-state-transition-audit.md`
   - 내용:
```markdown
---
id: AUDIT-001-state-transition-audit
type: audit
status: audit
qa_id: QA-001-state-transition-qa
audit_results:
  three_layer_architecture: pass
  uuid_compliance: pass
  data_centric: pass
  type_safety: pass
  async_first: pass
  transactions: pass
  migrations: pass
overall_compliance: pass
violations: []
keyword: state-transition-audit
created_at: 2026-01-01T19:00:00Z
updated_at: 2026-01-01T19:00:00Z
author: agent
---

# 상태 전이 규칙 검증 Audit

## 설명
상태 전이 규칙 검증 로직에 대한 규칙 준수 검증
```

3. **원본 QA 문서 업데이트** (반드시):
```yaml
status: audit
```

---

### 예시 8: 프로젝트 종결 처리 (순서 11-14)

#### 11단계: 문서 최신화

1. **Documentation Update 문서 생성**:
   - 파일: `docs/work-items/documentation/DOC-UPDATE-001.md`
   - 내용:
```markdown
---
id: DOC-UPDATE-001
type: documentation-update
status: documentation
related_epic_id: EPIC-001
updated_documents:
  - docs/changelog/CHANGELOG.md
created_at: 2026-01-01T20:00:00Z
updated_at: 2026-01-01T20:00:00Z
author: agent
---

# 오브젝트 상호작용 고도화 문서 최신화

## 설명
관련 문서를 최신화합니다.
```

2. **CHANGELOG.md 업데이트**

#### 12단계: Done 처리

1. **Done 문서 생성**:
   - 파일: `docs/work-items/done/DONE-EPIC-001.md`
   - 원본 Epic 문서를 done 폴더로 이동

#### 13단계: Deprecated 처리 (선택사항)

1. **Deprecated 문서 생성**:
   - 파일: `docs/work-items/deprecated/[deprecated]ideation-object-interaction-current-status.md`
   - 원본 ideation 문서를 deprecated 폴더로 이동

#### 14단계: 항구 보존 문서 생성

1. **Permanent Docs 문서 생성**:
   - 파일: `docs/work-items/permanent/PERM-DOC-001.md`
   - `docs/changelog/CHANGELOG.md` 업데이트
   - `docs/rules/*.md` 업데이트 (필요 시)
   - `docs/architecture/*.md` 업데이트 (필요 시)

---

## 핵심 원칙 요약

### 반드시 준수해야 할 규칙 (MUST)

1. ✅ **순서 준수**: 1단계부터 14단계까지 순서대로 진행
2. ✅ **메타데이터 필수**: YAML frontmatter 반드시 포함
3. ✅ **양방향 연결**: 한쪽만 연결 금지
4. ✅ **상태 전환 시 원본 업데이트**: 반드시 원본 문서도 업데이트
5. ✅ **파일명 규칙 준수**: ID 기반 파일명 사용
6. ✅ **네이밍 컨벤션 준수**: 모든 네이밍 규칙 준수
7. ✅ **저장 전 검증**: 모든 체크리스트 확인

### 금지 사항 (DO NOT)

1. ❌ 순서 건너뛰기 금지
2. ❌ 메타데이터 없이 문서 작성 금지
3. ❌ 한쪽만 연결 금지
4. ❌ 상태 전환 시 원본 미업데이트 금지
5. ❌ 파일명 규칙 위반 금지
6. ❌ 네이밍 컨벤션 위반 금지
7. ❌ 검증 없이 저장 금지

---

## 디렉토리 구조 참고

### 전체 구조

```
docs/
├── work-items/                    # 모든 작업 항목
│   ├── ideation/                  # 순서 1-3
│   ├── epic/                      # 순서 4
│   ├── task/                      # 순서 5
│   ├── development/               # 순서 6-8
│   ├── qa/                        # 순서 9
│   ├── audit/                     # 순서 10
│   ├── documentation/             # 순서 11
│   ├── done/                      # 순서 12
│   ├── deprecated/                # 순서 13
│   └── permanent/                 # 순서 14
│
├── submissions/                   # 제출 파일 (YAML만)
├── rules/                         # 개발 규칙 (항구 보존)
├── architecture/                  # 아키텍처 문서 (항구 보존)
├── changelog/                     # 변경 이력 (항구 보존)
└── api/                           # API 문서 (항구 보존)
```

### 상대 경로 참조

**연결 문서 참조 시**:
- ideation → ideation: `./ideation-xxx.md`
- ideation → epic: `../epic/EPIC-001.md`
- epic → ideation: `../ideation/ideation-xxx.md`
- task → epic: `../epic/EPIC-001.md`
- epic → task: `../task/TASK-001.md`
- todo → task: `../task/TASK-001.md`
- test → todo: `./TODO-001.md`
- qa → todo: `../development/TODO-001.md`
- audit → qa: `../qa/QA-001.md`

---

## 작업 체크리스트

### 문서 작성 시

- [ ] 올바른 순서인가? (1-14)
- [ ] 올바른 폴더에 저장하는가? (`docs/work-items/{status}/`)
- [ ] 파일명이 규칙에 맞는가?
- [ ] YAML frontmatter가 있는가?
- [ ] 모든 필수 메타데이터가 있는가?
- [ ] ideation인 경우 `ideation_type`이 있는가?
- [ ] 연결 정보가 있으면 명시했는가?

### 상태 전환 시

- [ ] 순서가 올바른가? (1→2→3→...→14)
- [ ] 새 문서를 생성했는가?
- [ ] 원본 문서를 찾았는가?
- [ ] 원본 문서를 업데이트했는가?
- [ ] 양방향 연결을 설정했는가?
- [ ] `updated_at`을 업데이트했는가?

### 저장 전

- [ ] 메타데이터 검증 통과?
- [ ] 연결 정보 일관성 확인?
- [ ] 상태 전환 검증 통과?
- [ ] 파일명 검증 통과?
- [ ] 순서 검증 통과?

**모든 체크리스트 통과 시에만 저장**

---

## 결론

**이 규칙을 준수하면:**

1. ✅ 모든 문서가 일관된 형식
2. ✅ 문서 간 연결고리 자동 설정
3. ✅ 순서가 명확하여 진행 상황 추적 가능
4. ✅ MECE 원칙으로 누락 없이 전체 프로세스 커버
5. ✅ 대시보드에서 조회 가능
6. ✅ 자동화된 문서 관리

**핵심**: 에이전트가 이 규칙을 **반드시 준수**하도록 프롬프트에 명시

---

## 부록: 빠른 참조

### 순서 요약

1. **Ideation Status** → 문제 정의 및 현황 진단
2. **Ideation Methodology** → 방법론 검토
3. **Ideation Plan** → 실행 계획 수립
4. **Epic** → 대규모 기능 정의
5. **Task** → 작업 단위 정의
6. **TODO** → 개발 작업 (TDD)
7. **Test** → 테스트 작성 및 실행
8. **Troubleshooting** → 문제 해결
9. **QA** → 품질 보증
10. **Audit** → 규칙 준수 검증
11. **Documentation Update** → 문서 최신화
12. **Done** → 완료 처리
13. **Deprecated** → 폐기 처리
14. **Permanent Docs** → 항구 보존 문서 생성

### 파일명 규칙 요약

- ideation: `ideation-{category}-{title-slug}-{ideation_type}.md`
- epic: `EPIC-{번호}.md`
- task: `TASK-{번호}.md`
- todo: `TODO-{번호}.md`
- test: `TEST-{번호}.md`
- troubleshooting: `TROUBLESHOOT-{번호}.md`
- qa: `QA-{번호}.md`
- audit: `AUDIT-{번호}.md`
- documentation-update: `DOC-UPDATE-{번호}.md`
- done: `DONE-{원본ID}.md`
- deprecated: `[deprecated]{원본ID}.md`
- permanent-docs: `PERM-DOC-{번호}.md`

### 필수 메타데이터 요약

- 공통: `id`, `type`, `status`, `created_at`, `updated_at`, `author`
- ideation: `ideation_type`, `category`, `priority`, `related_ideations`
- epic: `ideation_ids`, `tasks`
- task: `epic_id`, `dependencies`, `todos`, `estimated_hours`
- todo: `task_id`, `sub_status`, `file`, `line`, `code_snippet`
- test: `todo_id`, `test_file`, `test_results`, `coverage`
- troubleshooting: `related_todo_id`, `related_test_id`, `issue_description`, `solution`, `resolved`
- qa: `todo_id`, `test_id`, `qa_results`, `quality_score`
- audit: `qa_id`, `audit_results`, `overall_compliance`, `violations`
- documentation-update: `related_epic_id`, `updated_documents`
- done: `completed_at`, `original_path`
- deprecated: `deprecated_at`, `deprecated_reason`, `original_path`
- permanent-docs: `related_epic_id`, `document_types`, `target_files`

### 상태 전환 체크리스트

1. 순서 확인 (1→2→3→...→14)
2. 새 문서 생성
3. 원본 문서 찾기
4. 원본 문서 업데이트
5. 양방향 연결 설정
6. 검증 후 저장

## 참고 문서

- `docs/rules/01_PHILOSOPHY.md`: 핵심 개발 철학
- `docs/rules/PROJECT_MANAGEMENT_WORKFLOW.md`: 프로젝트 관리 워크플로우
- `docs/rules/README.md`: 모든 규칙 문서 인덱스

