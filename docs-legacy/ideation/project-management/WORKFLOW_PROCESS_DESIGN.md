# 워크플로우 프로세스 상세 설계

**작성일**: 2026-01-01  
**목적**: 자동화된 프로젝트 관리 시스템의 워크플로우 프로세스 상세 설계  
**관련 문서**: `AUTOMATED_PROJECT_MANAGEMENT_PROPOSAL.md`

---

## 📋 목차

1. [워크플로우 상태 정의](#워크플로우-상태-정의)
2. [상태 전환 규칙](#상태-전환-규칙)
3. [자동화 규칙](#자동화-규칙)
4. [검증 규칙](#검증-규칙)
5. [에러 처리](#에러-처리)

---

## 워크플로우 상태 정의

### 상태 다이어그램

```
ideation → epic → task → development → qa → audit → done → deprecated
   ↑        ↑       ↑         ↑          ↑      ↑      ↑         ↑
   └────────┴───────┴─────────┴──────────┴──────┴──────┴─────────┘
            (각 단계에서 이전 단계로 롤백 가능)
```

### 상태 상세 정의

#### 1. ideation (아이디어)

**정의**: 새로운 기능이나 개선 사항에 대한 아이디어

**속성**:
- `status`: `ideation`
- `priority`: `high` | `medium` | `low`
- `category`: `action-handler` | `object-interaction` | `item-equipment` | ...
- `file_path`: `docs/ideation/{category}/{TITLE}.md`
- `epic_id`: `None` (아직 Epic 생성 전)

**메타데이터**:
```yaml
status: ideation
priority: high
category: action-handler
created_at: 2026-01-01T00:00:00Z
updated_at: 2026-01-01T00:00:00Z
author: user|agent
epic_id: null
related_epics: []
```

**전환 가능한 상태**:
- `epic`: ideation이 승인되면
- `cancelled`: 취소된 경우

---

#### 2. epic (대규모 기능)

**정의**: 여러 Task로 구성되는 대규모 기능 단위

**속성**:
- `status`: `epic`
- `epic_id`: `EPIC-{번호}` (예: `EPIC-001`)
- `ideation_doc_id`: 연결된 ideation 문서 ID
- `tasks`: 연결된 Task ID 목록
- `file_path`: `docs/project-management/epics/{EPIC_ID}.md`

**메타데이터**:
```yaml
status: epic
epic_id: EPIC-001
ideation_doc_id: ideation-action-handler-modularization
title: "Action Handler 모듈화"
description: "ActionHandler를 카테고리별로 모듈화"
tasks: []
created_at: 2026-01-01T00:00:00Z
updated_at: 2026-01-01T00:00:00Z
```

**전환 가능한 상태**:
- `task`: Epic이 승인되고 Task가 생성되면
- `ideation`: Epic이 취소되면
- `cancelled`: 취소된 경우

---

#### 3. task (작업 단위)

**정의**: Epic을 구성하는 개별 작업 단위

**속성**:
- `status`: `task`
- `task_id`: `TASK-{번호}` (예: `TASK-001`)
- `epic_id`: 상위 Epic ID
- `estimated_hours`: 예상 작업 시간
- `todos`: 연결된 TODO ID 목록
- `dependencies`: 의존하는 다른 Task ID 목록
- `file_path`: `docs/project-management/tasks/{TASK_ID}.md`

**메타데이터**:
```yaml
status: task
task_id: TASK-001
epic_id: EPIC-001
title: "ObjectInteractionHandlerBase 구현"
description: "오브젝트 상호작용 핸들러 베이스 클래스 구현"
estimated_hours: 4.0
todos: []
dependencies: []
created_at: 2026-01-01T00:00:00Z
updated_at: 2026-01-01T00:00:00Z
```

**전환 가능한 상태**:
- `development`: Task가 승인되고 TODO가 생성되면
- `epic`: Task가 취소되면
- `blocked`: 의존성이 해결되지 않으면
- `cancelled`: 취소된 경우

---

#### 4. development (개발 작업)

**정의**: 실제 코드 구현 작업

**속성**:
- `status`: `development`
- `todo_id`: `TODO-{번호}` (예: `TODO-001`)
- `task_id`: 상위 Task ID
- `file`: 구현할 파일 경로
- `line`: TODO 위치 (라인 번호)
- `code_snippet`: 구현할 코드 스니펫 (선택)
- `file_path`: `docs/project-management/todos/{TODO_ID}.md` 또는 코드 내 TODO 주석

**메타데이터**:
```yaml
status: development
todo_id: TODO-001
task_id: TASK-001
title: "ObjectInteractionHandlerBase 클래스 생성"
file: app/handlers/object_interaction_base.py
line: 1
code_snippet: |
  class ObjectInteractionHandlerBase(ABC):
      ...
priority: high
created_at: 2026-01-01T00:00:00Z
updated_at: 2026-01-01T00:00:00Z
```

**전환 가능한 상태**:
- `qa`: 코드 구현 완료 및 테스트 통과
- `task`: 개발이 취소되면
- `blocked`: 의존성이 해결되지 않으면
- `cancelled`: 취소된 경우

---

#### 5. qa (품질 보증)

**정의**: 코드 품질 검증 및 테스트

**속성**:
- `status`: `qa`
- `qa_id`: `QA-{번호}` (예: `QA-001`)
- `todo_id`: 검증할 TODO ID
- `test_results`: 테스트 결과
- `coverage`: 코드 커버리지
- `file_path`: `docs/audit/qa/{QA_ID}.md`

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
quality_score: 8.5
created_at: 2026-01-01T00:00:00Z
updated_at: 2026-01-01T00:00:00Z
```

**전환 가능한 상태**:
- `audit`: QA 테스트 통과 및 커버리지 기준 충족
- `development`: QA 실패 시 재개발
- `cancelled`: 취소된 경우

**QA 통과 기준**:
- 모든 테스트 통과
- 코드 커버리지 ≥ 80%
- 린터 오류 없음
- 타입 체크 통과

---

#### 6. audit (검토)

**정의**: 코드 리뷰 및 최종 검증

**속성**:
- `status`: `audit`
- `audit_id`: `AUDIT-{번호}` (예: `AUDIT-001`)
- `qa_id`: 검토할 QA ID
- `review_results`: 리뷰 결과
- `approved`: 승인 여부
- `file_path`: `docs/audit/{AUDIT_ID}.md`

**메타데이터**:
```yaml
status: audit
audit_id: AUDIT-001
qa_id: QA-001
review_results:
  code_quality: 9.0
  architecture_compliance: 8.5
  documentation: 8.0
approved: false
reviewer: agent|user
comments: []
created_at: 2026-01-01T00:00:00Z
updated_at: 2026-01-01T00:00:00Z
```

**전환 가능한 상태**:
- `done`: Audit 승인
- `qa`: Audit 실패 시 재QA
- `development`: Audit 실패 시 재개발
- `cancelled`: 취소된 경우

**Audit 승인 기준**:
- 코드 품질 점수 ≥ 8.0
- 아키텍처 준수 점수 ≥ 8.0
- 문서화 점수 ≥ 7.0
- 사용자 또는 에이전트 승인

---

#### 7. done (완료)

**정의**: 작업 완료

**속성**:
- `status`: `done`
- `completed_at`: 완료 시각
- `changelog_updated`: CHANGELOG 업데이트 여부
- `implementation_status_updated`: IMPLEMENTATION_STATUS.md 업데이트 여부

**메타데이터**:
```yaml
status: done
completed_at: 2026-01-01T12:00:00Z
changelog_updated: true
implementation_status_updated: true
deprecated_triggered: false
```

**전환 가능한 상태**:
- `deprecated`: 관련 ideation 문서가 모두 완료되면

**자동 처리 작업**:
1. CHANGELOG 업데이트
2. IMPLEMENTATION_STATUS.md 업데이트
3. 관련 문서 상태 업데이트
4. Deprecated 처리 트리거 (조건 만족 시)

---

#### 8. deprecated (폐기)

**정의**: 완료된 ideation 문서 아카이브

**속성**:
- `status`: `deprecated`
- `deprecated_at`: 폐기 시각
- `reason`: 폐기 이유
- `new_location`: 새 위치 (`docs/archive/deprecated/ideation/`)

**메타데이터**:
```yaml
status: deprecated
deprecated_at: 2026-01-01T13:00:00Z
reason: "구현 완료 - 모든 Epic, Task, TODO가 done 상태"
new_location: docs/archive/deprecated/ideation/[deprecated]ACTION_HANDLER_MODULARIZATION_PROPOSAL.md
```

**전환 가능한 상태**:
- 없음 (최종 상태)

**자동 처리 작업**:
1. 파일 이동
2. 파일명에 `[deprecated]` 접두어 추가
3. 문서 내 deprecation 섹션 추가
4. CHANGELOG에 deprecation 기록

---

## 상태 전환 규칙

### 전환 규칙 정의

```python
TRANSITION_RULES = {
    # ideation → epic
    ("ideation", "epic"): {
        "condition": lambda item: item.metadata.get("approved") == True,
        "auto": True,
        "required_fields": ["title", "category"],
    },
    
    # epic → task
    ("epic", "task"): {
        "condition": lambda item: item.metadata.get("approved") == True,
        "auto": True,
        "required_fields": ["epic_id", "ideation_doc_id"],
    },
    
    # task → development
    ("task", "development"): {
        "condition": lambda item: (
            item.metadata.get("approved") == True and
            all_dependencies_resolved(item)
        ),
        "auto": True,
        "required_fields": ["task_id", "epic_id"],
    },
    
    # development → qa
    ("development", "qa"): {
        "condition": lambda item: (
            code_implemented(item) and
            tests_pass(item) and
            no_linter_errors(item)
        ),
        "auto": True,
        "required_fields": ["todo_id", "task_id", "file"],
    },
    
    # qa → audit
    ("qa", "audit"): {
        "condition": lambda item: (
            item.metadata.get("test_results", {}).get("failed", 0) == 0 and
            item.metadata.get("coverage", 0) >= 0.8
        ),
        "auto": True,
        "required_fields": ["qa_id", "todo_id"],
    },
    
    # audit → done
    ("audit", "done"): {
        "condition": lambda item: (
            item.metadata.get("approved") == True and
            item.metadata.get("review_results", {}).get("code_quality", 0) >= 8.0
        ),
        "auto": False,  # 사용자 또는 에이전트 승인 필요
        "required_fields": ["audit_id", "qa_id"],
    },
    
    # done → deprecated (ideation 문서만)
    ("done", "deprecated"): {
        "condition": lambda item: (
            isinstance(item, IdeationDoc) and
            all_related_items_done(item)
        ),
        "auto": True,
        "required_fields": ["ideation_doc_id"],
    },
}
```

### 롤백 규칙

```python
ROLLBACK_RULES = {
    # epic → ideation
    ("epic", "ideation"): {
        "condition": lambda item: item.metadata.get("cancelled") == True,
        "auto": True,
    },
    
    # task → epic
    ("task", "epic"): {
        "condition": lambda item: item.metadata.get("cancelled") == True,
        "auto": True,
    },
    
    # development → task
    ("development", "task"): {
        "condition": lambda item: item.metadata.get("cancelled") == True,
        "auto": True,
    },
    
    # qa → development
    ("qa", "development"): {
        "condition": lambda item: (
            item.metadata.get("test_results", {}).get("failed", 0) > 0 or
            item.metadata.get("coverage", 0) < 0.8
        ),
        "auto": True,
    },
    
    # audit → qa
    ("audit", "qa"): {
        "condition": lambda item: (
            item.metadata.get("approved") == False and
            item.metadata.get("review_results", {}).get("code_quality", 0) < 8.0
        ),
        "auto": True,
    },
    
    # audit → development
    ("audit", "development"): {
        "condition": lambda item: (
            item.metadata.get("approved") == False and
            item.metadata.get("review_results", {}).get("code_quality", 0) < 6.0
        ),
        "auto": True,
    },
}
```

---

## 자동화 규칙

### 1. 자동 생성 규칙

**Ideation → Epic**:
- ideation 문서가 승인되면 자동으로 Epic 생성
- Epic ID 자동 생성 (`EPIC-{순차번호}`)
- ideation 문서와 Epic 연결

**Epic → Task**:
- Epic이 승인되면 자동으로 Task 생성
- Epic 내용 분석하여 Task 자동 분해
- Task ID 자동 생성 (`TASK-{순차번호}`)

**Task → TODO**:
- Task가 승인되면 자동으로 TODO 생성
- 코드 파일 및 위치 자동 결정
- TODO ID 자동 생성 (`TODO-{순차번호}`)

### 2. 자동 전환 규칙

**Development → QA**:
- 코드 구현 완료 감지
- 테스트 자동 실행
- 모든 테스트 통과 시 자동으로 QA 단계로 전환

**QA → Audit**:
- QA 테스트 결과 확인
- 커버리지 기준 충족 확인
- 조건 만족 시 자동으로 Audit 단계로 전환

**Done → Deprecated**:
- 관련 ideation 문서의 모든 Epic, Task, TODO가 done 상태인지 확인
- 조건 만족 시 자동으로 Deprecated 처리

### 3. 자동 업데이트 규칙

**CHANGELOG 업데이트**:
- 작업이 `done` 상태가 되면 자동으로 CHANGELOG 업데이트
- 작업 내용, 완료일, 관련 문서 링크 추가

**IMPLEMENTATION_STATUS.md 업데이트**:
- 작업이 `done` 상태가 되면 자동으로 IMPLEMENTATION_STATUS.md 업데이트
- 구현 상태 표 업데이트
- 완료율 재계산

**문서 상태 업데이트**:
- 관련 문서의 상태 자동 업데이트
- 메타데이터 동기화

---

## 검증 규칙

### 1. 상태 전환 검증

**필수 필드 검증**:
- 각 상태 전환 시 필수 필드가 모두 존재하는지 확인
- 필수 필드가 없으면 전환 실패

**의존성 검증**:
- Task → Development: 의존하는 Task가 모두 완료되었는지 확인
- Epic → Task: 상위 Epic이 존재하는지 확인

**데이터 무결성 검증**:
- ID 중복 확인
- 참조 무결성 확인
- 파일 경로 유효성 확인

### 2. 코드 검증

**구현 완료 검증**:
- TODO에 지정된 파일이 존재하는지 확인
- 코드가 실제로 구현되었는지 확인 (AST 분석)
- 테스트가 작성되었는지 확인

**품질 검증**:
- 린터 오류 확인
- 타입 체크 통과 확인
- 코드 커버리지 확인

### 3. 문서 검증

**문서 존재 확인**:
- 각 단계의 문서가 생성되었는지 확인
- 문서 경로가 올바른지 확인

**메타데이터 검증**:
- 메타데이터 형식 확인
- 필수 메타데이터 존재 확인
- 메타데이터 일관성 확인

---

## 에러 처리

### 1. 전환 실패 처리

**자동 롤백**:
- 상태 전환 실패 시 이전 상태로 롤백
- 변경 사항 되돌리기
- 에러 로그 기록

**에러 리포트**:
- 전환 실패 원인 기록
- 해결 방안 제시
- 사용자 또는 에이전트에게 알림

### 2. 검증 실패 처리

**검증 실패 시**:
- 전환 중단
- 실패 원인 명시
- 수정 가이드 제공

**재시도 메커니즘**:
- 일시적 오류는 자동 재시도
- 영구적 오류는 수동 개입 필요

### 3. 예외 상황 처리

**파일 시스템 오류**:
- 파일 생성/수정 실패 시 롤백
- 백업 복원

**데이터베이스 오류**:
- 트랜잭션 롤백
- 데이터 일관성 유지

**네트워크 오류**:
- 재시도 메커니즘
- 오프라인 모드 지원

---

## 워크플로우 실행 예제

### 예제 1: 자동 전환

```python
# 1. Ideation 생성
ideation = await project_manager.create_ideation(
    title="Action Handler 모듈화",
    category="action-handler",
    content="..."
)

# 2. 승인 (자동으로 Epic 생성)
ideation.metadata["approved"] = True
epic = await workflow_engine.transition(ideation, "epic")

# 3. Epic 승인 (자동으로 Task 생성)
epic.metadata["approved"] = True
tasks = await workflow_engine.transition(epic, "task")

# 4. Task 승인 (자동으로 TODO 생성)
task = tasks[0]
task.metadata["approved"] = True
todo = await workflow_engine.transition(task, "development")

# 5. 코드 구현 완료 (자동으로 QA 실행)
# (코드 구현)
await code_validator.validate(todo)
qa = await workflow_engine.transition(todo, "qa")

# 6. QA 통과 (자동으로 Audit 실행)
# (QA 테스트 실행)
audit = await workflow_engine.transition(qa, "audit")

# 7. Audit 승인 (Done 처리)
audit.metadata["approved"] = True
done = await workflow_engine.transition(audit, "done")

# 8. 모든 작업 완료 (자동으로 Deprecated 처리)
deprecated = await workflow_engine.transition(ideation, "deprecated")
```

### 예제 2: 롤백

```python
# QA 실패 시 자동 롤백
qa.metadata["test_results"]["failed"] = 5
todo = await workflow_engine.transition(qa, "development")  # 자동 롤백

# Audit 실패 시 자동 롤백
audit.metadata["approved"] = False
audit.metadata["review_results"]["code_quality"] = 5.0
qa = await workflow_engine.transition(audit, "qa")  # 자동 롤백
```

---

## 다음 단계

1. **도구 구현**: 워크플로우 엔진 구현
2. **통합 테스트**: 실제 시나리오로 테스트
3. **에이전트 통합**: 에이전트가 사용할 수 있도록 통합
4. **문서화**: 사용 가이드 작성

