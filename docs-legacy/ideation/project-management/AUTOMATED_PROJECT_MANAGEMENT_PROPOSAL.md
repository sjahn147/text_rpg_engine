# 자동화된 프로젝트 관리 시스템 제안

**작성일**: 2026-01-01  
**목적**: Jira 스타일의 자동화되고 체계화된 프로젝트 관리 시스템 구축  
**대상**: 에이전트 기반 자동화된 개발 프로세스

---

## 📋 목차

1. [현재 문제점](#현재-문제점)
2. [제안하는 시스템](#제안하는-시스템)
3. [워크플로우 정의](#워크플로우-정의)
4. [도구 설계](#도구-설계)
5. [에이전트 온보딩](#에이전트-온보딩)
6. [구현 계획](#구현-계획)

---

## 현재 문제점

### 1. 수동 프로세스
- ideation 문서 작성 → 수동으로 구현 상태 확인
- TODO 항목 관리 → 수동으로 체크리스트 업데이트
- 완료 처리 → 수동으로 deprecated 문서 이동
- 문서 동기화 → 수동으로 CHANGELOG 업데이트

### 2. 일관성 부족
- 프로세스가 명확하지 않음
- 각 작업마다 다른 방식으로 처리
- 문서화가 일관되지 않음

### 3. 추적 어려움
- 어떤 작업이 어느 단계에 있는지 파악 어려움
- 의존성 관계 파악 어려움
- 진행 상황 추적 어려움

### 4. 에이전트 온보딩 어려움
- 프로세스가 문서화되지 않음
- 에이전트가 자동으로 작업할 수 없음
- 일관된 방식으로 작업 강제 불가

---

## 제안하는 시스템

### 핵심 개념

**Jira 스타일의 계층 구조:**
```
Ideation (아이디어)
  ↓
Epic (대규모 기능)
  ↓
Task (작업 단위)
  ↓
Development TODO (개발 작업)
  ↓
QA (품질 보증)
  ↓
Audit (검토)
  ↓
Done (완료)
  ↓
Deprecated (폐기)
```

### 자동화 원칙

1. **상태 기반 워크플로우**: 각 작업은 명확한 상태를 가짐
2. **자동 전환**: 조건이 만족되면 자동으로 다음 단계로 전환
3. **강제 실행**: 프로세스를 벗어난 작업은 실행 불가
4. **에이전트 친화적**: 에이전트가 자동으로 이해하고 실행 가능

---

## 워크플로우 정의

### Phase 1: Ideation (아이디어)

**상태**: `ideation`

**입력**:
- 사용자 요청 또는 제안
- 새로운 기능 아이디어

**처리**:
1. ideation 문서 생성 (`docs/ideation/{category}/{TITLE}.md`)
2. 문서 메타데이터 설정:
   ```yaml
   status: ideation
   priority: high|medium|low
   category: action-handler|object-interaction|...
   created_at: 2026-01-01
   author: user|agent
   ```

**출력**:
- ideation 문서
- Epic 생성 트리거

**자동 전환 조건**:
- 문서가 승인되면 → Epic 생성

---

### Phase 2: Epic (대규모 기능)

**상태**: `epic`

**입력**:
- ideation 문서

**처리**:
1. Epic 문서 생성 (`docs/project-management/epics/{EPIC_ID}.md`)
2. Epic 메타데이터 설정:
   ```yaml
   epic_id: EPIC-001
   title: "Action Handler 모듈화"
   status: epic
   ideation_doc: docs/ideation/action-handler/ACTION_HANDLER_MODULARIZATION_PROPOSAL.md
   tasks: []
   created_at: 2026-01-01
   ```

**출력**:
- Epic 문서
- Task 생성 트리거

**자동 전환 조건**:
- Epic이 승인되면 → Task 생성

---

### Phase 3: Task (작업 단위)

**상태**: `task`

**입력**:
- Epic 문서

**처리**:
1. Task 문서 생성 (`docs/project-management/tasks/{TASK_ID}.md`)
2. Task 메타데이터 설정:
   ```yaml
   task_id: TASK-001
   epic_id: EPIC-001
   title: "ObjectInteractionHandlerBase 구현"
   status: task
   priority: high
   estimated_hours: 4
   dependencies: []
   todos: []
   created_at: 2026-01-01
   ```

**출력**:
- Task 문서
- Development TODO 생성 트리거

**자동 전환 조건**:
- Task가 승인되면 → Development TODO 생성

---

### Phase 4: Development TODO (개발 작업)

**상태**: `development`

**입력**:
- Task 문서

**처리**:
1. Development TODO 생성 (`docs/project-management/todos/{TODO_ID}.md` 또는 코드 내 TODO 주석)
2. TODO 메타데이터 설정:
   ```yaml
   todo_id: TODO-001
   task_id: TASK-001
   title: "ObjectInteractionHandlerBase 클래스 생성"
   status: development
   file: app/handlers/object_interaction_base.py
   line: 1
   priority: high
   created_at: 2026-01-01
   ```

**출력**:
- Development TODO
- 코드 구현

**자동 전환 조건**:
- 코드 구현 완료 및 테스트 통과 → QA 단계

---

### Phase 5: QA (품질 보증)

**상태**: `qa`

**입력**:
- 완료된 Development TODO

**처리**:
1. QA 테스트 실행
2. QA 문서 생성 (`docs/audit/qa/{QA_ID}.md`)
3. QA 메타데이터 설정:
   ```yaml
   qa_id: QA-001
   todo_id: TODO-001
   status: qa
   test_results: {}
   coverage: 0.0
   created_at: 2026-01-01
   ```

**출력**:
- QA 리포트
- Audit 단계 트리거

**자동 전환 조건**:
- QA 테스트 통과 및 커버리지 기준 충족 → Audit 단계

---

### Phase 6: Audit (검토)

**상태**: `audit`

**입력**:
- QA 통과한 작업

**처리**:
1. Audit 검토 실행
2. Audit 문서 생성 (`docs/audit/{AUDIT_ID}.md`)
3. Audit 메타데이터 설정:
   ```yaml
   audit_id: AUDIT-001
   qa_id: QA-001
   status: audit
   review_results: {}
   approved: false
   created_at: 2026-01-01
   ```

**출력**:
- Audit 리포트
- Done 단계 트리거

**자동 전환 조건**:
- Audit 승인 → Done 단계

---

### Phase 7: Done (완료)

**상태**: `done`

**입력**:
- Audit 승인된 작업

**처리**:
1. 상태를 `done`으로 변경
2. CHANGELOG 자동 업데이트
3. IMPLEMENTATION_STATUS.md 자동 업데이트
4. 관련 문서 상태 업데이트

**출력**:
- 완료된 작업 기록
- Deprecated 처리 트리거 (해당되는 경우)

**자동 전환 조건**:
- ideation 문서가 완전히 구현 완료 → Deprecated 단계

---

### Phase 8: Deprecated (폐기)

**상태**: `deprecated`

**입력**:
- 완료된 ideation 문서

**처리**:
1. ideation 문서를 `docs/archive/deprecated/ideation/`으로 이동
2. 파일명에 `[deprecated]` 접두어 추가
3. 문서 내 deprecation 이유 추가
4. CHANGELOG에 deprecation 기록

**출력**:
- Deprecated 문서
- 아카이브 완료

---

## 도구 설계

### 1. 프로젝트 관리 도구 (`tools/project_manager.py`)

**핵심 기능**:
- 워크플로우 상태 관리
- 자동 전환 로직
- 메타데이터 관리
- 문서 생성/업데이트

**인터페이스**:
```python
class ProjectManager:
    """프로젝트 관리 자동화 도구"""
    
    async def create_ideation(self, title: str, category: str, content: str) -> IdeationDoc
    async def create_epic(self, ideation_doc: IdeationDoc) -> Epic
    async def create_task(self, epic: Epic, title: str) -> Task
    async def create_todo(self, task: Task, file: str, line: int) -> Todo
    async def transition_to_qa(self, todo: Todo) -> QA
    async def transition_to_audit(self, qa: QA) -> Audit
    async def transition_to_done(self, audit: Audit) -> Done
    async def deprecate_ideation(self, ideation_doc: IdeationDoc) -> DeprecatedDoc
```

### 2. 워크플로우 엔진 (`tools/workflow_engine.py`)

**핵심 기능**:
- 상태 전환 규칙 정의
- 자동 전환 조건 검사
- 워크플로우 강제 실행

**인터페이스**:
```python
class WorkflowEngine:
    """워크플로우 자동화 엔진"""
    
    async def can_transition(self, current_state: str, target_state: str, context: dict) -> bool
    async def transition(self, item: WorkflowItem, target_state: str) -> WorkflowItem
    async def enforce_workflow(self, action: str, context: dict) -> bool
```

### 3. 문서 생성기 (`tools/document_generator.py`)

**핵심 기능**:
- 템플릿 기반 문서 생성
- 메타데이터 자동 삽입
- 문서 업데이트

**인터페이스**:
```python
class DocumentGenerator:
    """문서 자동 생성 도구"""
    
    async def generate_ideation_doc(self, ideation: Ideation) -> str
    async def generate_epic_doc(self, epic: Epic) -> str
    async def generate_task_doc(self, task: Task) -> str
    async def update_changelog(self, item: WorkflowItem) -> None
    async def update_implementation_status(self, item: WorkflowItem) -> None
```

### 4. 상태 추적기 (`tools/status_tracker.py`)

**핵심 기능**:
- 작업 상태 추적
- 의존성 관리
- 진행 상황 리포트

**인터페이스**:
```python
class StatusTracker:
    """상태 추적 도구"""
    
    async def get_status(self, item_id: str) -> WorkflowStatus
    async def get_dependencies(self, item_id: str) -> List[str]
    async def get_progress(self, epic_id: str) -> ProgressReport
    async def generate_report(self) -> ProjectReport
```

### 5. 에이전트 온보딩 도구 (`tools/agent_onboarding.py`)

**핵심 기능**:
- 프로세스 설명
- 워크플로우 규칙 제공
- 자동 실행 가이드

**인터페이스**:
```python
class AgentOnboarding:
    """에이전트 온보딩 도구"""
    
    async def get_workflow_rules(self) -> WorkflowRules
    async def get_process_guide(self) -> ProcessGuide
    async def validate_action(self, action: str, context: dict) -> ValidationResult
    async def suggest_next_action(self, current_state: str) -> List[str]
```

---

## 에이전트 온보딩

### 1. 프로세스 문서화

**필수 문서**:
- `docs/rules/PROJECT_MANAGEMENT_WORKFLOW.md`: 워크플로우 정의
- `docs/rules/AGENT_WORKFLOW_GUIDE.md`: 에이전트 작업 가이드
- `docs/rules/AUTOMATION_RULES.md`: 자동화 규칙

### 2. 도구 통합

**에이전트가 사용할 수 있는 도구**:
- `project_manager`: 프로젝트 관리 작업
- `workflow_engine`: 워크플로우 자동화
- `document_generator`: 문서 생성
- `status_tracker`: 상태 추적

### 3. 자동 실행 규칙

**에이전트가 자동으로 수행할 작업**:
1. 사용자 요청 수신 → ideation 문서 생성
2. ideation 승인 → epic 생성
3. epic 승인 → task 생성
4. task 승인 → todo 생성
5. 코드 구현 완료 → QA 실행
6. QA 통과 → Audit 실행
7. Audit 승인 → Done 처리
8. 완료된 ideation → Deprecated 처리

### 4. 강제 실행 메커니즘

**워크플로우 위반 방지**:
- 상태 전환 전 검증
- 필수 단계 건너뛰기 방지
- 의존성 확인
- 자동 롤백 (실패 시)

---

## 구현 계획

### Phase 1: 핵심 도구 개발 (1주)

1. **프로젝트 관리 도구**
   - `tools/project_manager.py` 구현
   - 기본 CRUD 작업
   - 메타데이터 관리

2. **워크플로우 엔진**
   - `tools/workflow_engine.py` 구현
   - 상태 전환 로직
   - 검증 규칙

### Phase 2: 문서 자동화 (1주)

3. **문서 생성기**
   - `tools/document_generator.py` 구현
   - 템플릿 시스템
   - CHANGELOG 자동 업데이트

4. **상태 추적기**
   - `tools/status_tracker.py` 구현
   - 진행 상황 리포트
   - 의존성 관리

### Phase 3: 에이전트 통합 (1주)

5. **에이전트 온보딩**
   - `tools/agent_onboarding.py` 구현
   - 프로세스 가이드 제공
   - 자동 실행 규칙

6. **강제 실행 메커니즘**
   - 워크플로우 검증
   - 자동 롤백
   - 에러 처리

### Phase 4: 통합 및 테스트 (1주)

7. **통합 테스트**
   - 전체 워크플로우 테스트
   - 에이전트 시나리오 테스트
   - 성능 테스트

8. **문서화**
   - 사용 가이드 작성
   - API 문서 작성
   - 예제 시나리오

---

## 데이터 구조

### WorkflowItem (기본 클래스)

```python
@dataclass
class WorkflowItem:
    """워크플로우 아이템 기본 클래스"""
    id: str
    title: str
    status: WorkflowStatus
    priority: Priority
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    dependencies: List[str]
    related_items: List[str]
```

### IdeationDoc

```python
@dataclass
class IdeationDoc(WorkflowItem):
    """Ideation 문서"""
    category: str
    file_path: str
    epic_id: Optional[str] = None
```

### Epic

```python
@dataclass
class Epic(WorkflowItem):
    """Epic"""
    epic_id: str
    ideation_doc_id: str
    tasks: List[str]
```

### Task

```python
@dataclass
class Task(WorkflowItem):
    """Task"""
    task_id: str
    epic_id: str
    estimated_hours: float
    todos: List[str]
```

### Todo

```python
@dataclass
class Todo(WorkflowItem):
    """Development TODO"""
    todo_id: str
    task_id: str
    file: str
    line: int
    code_snippet: Optional[str] = None
```

---

## 예제 시나리오

### 시나리오: "Action Handler 리팩토링" 요청

1. **사용자 요청**: "Action Handler를 모듈화하세요"
2. **에이전트 자동 처리**:
   - ideation 문서 생성 (`docs/ideation/action-handler/ACTION_HANDLER_MODULARIZATION_PROPOSAL.md`)
   - 상태: `ideation`
3. **사용자 승인**: "네, 진행하세요"
4. **에이전트 자동 처리**:
   - Epic 생성 (`docs/project-management/epics/EPIC-001.md`)
   - 상태: `epic`
5. **에이전트 자동 처리**:
   - Task 생성 (여러 개)
     - `TASK-001`: ObjectInteractionHandlerBase 구현
     - `TASK-002`: Information 핸들러 분리
     - ...
   - 상태: `task`
6. **에이전트 자동 처리**:
   - TODO 생성 (각 Task마다)
   - 코드 구현 시작
   - 상태: `development`
7. **코드 구현 완료**:
   - QA 자동 실행
   - 상태: `qa`
8. **QA 통과**:
   - Audit 자동 실행
   - 상태: `audit`
9. **Audit 승인**:
   - Done 처리
   - CHANGELOG 업데이트
   - IMPLEMENTATION_STATUS.md 업데이트
   - 상태: `done`
10. **모든 관련 작업 완료**:
    - ideation 문서 Deprecated 처리
    - `docs/archive/deprecated/ideation/[deprecated]ACTION_HANDLER_MODULARIZATION_PROPOSAL.md`
    - 상태: `deprecated`

---

## 장점

1. **일관성**: 모든 작업이 동일한 프로세스를 따름
2. **자동화**: 수동 작업 최소화
3. **추적 가능**: 모든 작업의 상태와 진행 상황 추적
4. **에이전트 친화적**: 에이전트가 자동으로 이해하고 실행 가능
5. **확장 가능**: 새로운 워크플로우 단계 추가 용이
6. **강제 실행**: 프로세스를 벗어난 작업 방지

---

## 다음 단계

1. **프로세스 상세 설계**: 각 단계의 상세 규칙 정의
2. **도구 구현**: 핵심 도구 개발
3. **통합 테스트**: 실제 시나리오로 테스트
4. **에이전트 통합**: 에이전트가 사용할 수 있도록 통합
5. **문서화**: 사용 가이드 및 API 문서 작성

