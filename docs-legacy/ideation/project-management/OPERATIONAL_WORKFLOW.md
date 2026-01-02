# 실제 작동 워크플로우 상세 가이드

**작성일**: 2026-01-01  
**목적**: 에이전트 기반 프로젝트 관리 도구의 실제 작동 방식을 단계별로 설명  
**관련 문서**: `AGENTIC_PROJECT_MANAGEMENT_TOOL_SPEC.md`

---

## 📋 목차

1. [전체 워크플로우 개요](#전체-워크플로우-개요)
2. [시나리오별 상세 설명](#시나리오별-상세-설명)
3. [파일 형식 및 메타데이터](#파일-형식-및-메타데이터)
4. [연관 관계 자동 설정](#연관-관계-자동-설정)
5. [시스템 감지 및 처리](#시스템-감지-및-처리)

---

## 전체 워크플로우 개요

### 기본 원칙

1. **문서 기반**: 모든 작업은 Markdown 문서로 시작
2. **메타데이터 포함**: 문서에 YAML frontmatter로 메타데이터 포함
3. **자동 감지**: 파일 감시 시스템이 새 문서 자동 감지
4. **자동 연관**: 워크플로우 엔진이 연관 관계 자동 설정
5. **대시보드 표시**: Streamlit 대시보드가 실시간으로 표시

---

## 시나리오별 상세 설명

### 시나리오 1: ideation 생성

#### 1단계: 사용자 요청

**사용자가 Cursor에서**:
```
"ObjectInteractionHandlerBase 클래스를 리팩토링해주세요"
```

#### 2단계: 에이전트 처리

**에이전트가 자동으로**:
```python
# 에이전트 내부 처리 (사용자에게 보이지 않음)
from tools.project_management.agent_tools.create_ideation import create_ideation

# 1. ideation ID 생성
ideation_id = "ideation-object-interaction-handler-refactoring"

# 2. 파일 경로 결정
file_path = "docs/ideation/object-interaction/OBJECT_INTERACTION_HANDLER_REFACTORING.md"

# 3. 문서 내용 생성
content = f"""---
ideation_id: {ideation_id}
status: ideation
priority: high
category: object-interaction
created_at: {datetime.now().isoformat()}
author: agent
epic_id: null
---

# ObjectInteractionHandlerBase 리팩토링

## 설명
ObjectInteractionHandlerBase 클래스를 모듈화하고 개선합니다.

## 목표
- 모듈화
- 코드 품질 개선
- 테스트 커버리지 향상
"""

# 4. 파일 저장
await write_file(file_path, content)
```

**결과**:
- 파일 생성: `docs/ideation/object-interaction/OBJECT_INTERACTION_HANDLER_REFACTORING.md`
- 메타데이터 포함 (YAML frontmatter)

#### 3단계: 시스템 감지

**파일 감시 시스템이 자동 감지**:
```python
# tools/project_management/submission/watcher.py
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class IdeationWatcher(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            if 'ideation' in event.src_path and event.src_path.endswith('.md'):
                # 새 ideation 문서 감지
                asyncio.create_task(self.process_ideation(event.src_path))
    
    async def process_ideation(self, file_path: str):
        # 1. 파일 읽기
        content = await read_file(file_path)
        
        # 2. 메타데이터 파싱 (YAML frontmatter)
        metadata = parse_yaml_frontmatter(content)
        
        # 3. 데이터베이스에 저장
        await db.create_workflow_item(
            id=metadata['ideation_id'],
            type='ideation',
            title=extract_title(content),
            status='ideation',
            file_path=file_path,
            metadata=metadata
        )
        
        # 4. 대시보드에 알림
        await notify_dashboard('new_item', metadata['ideation_id'])
```

#### 4단계: 대시보드 표시

**Streamlit 대시보드가 자동 업데이트**:
```python
# tools/project_management/dashboard/pages/kanban.py
import streamlit as st
from tools.project_management.engine.workflow_engine import WorkflowEngine

@st.cache_data(ttl=5)  # 5초마다 캐시 갱신
def get_ideation_items():
    engine = WorkflowEngine()
    return engine.list_items(status='ideation')

# 페이지 로드 시 자동 조회
ideation_items = get_ideation_items()

# 칸반 보드에 표시
for item in ideation_items:
    with st.container():
        st.markdown(f"### {item.title}")
        st.caption(f"Status: {item.status}")
        st.caption(f"Priority: {item.metadata.get('priority')}")
        # 클릭 시 상세 정보 표시
```

---

### 시나리오 2: Epic 생성 및 연관 관계 설정

#### 1단계: 사용자 요청

**옵션 A: 대시보드에서**
- ideation 항목 선택
- "Epic으로 전환" 버튼 클릭

**옵션 B: Cursor에서**
```
"이 ideation을 Epic으로 만들어주세요"
```

#### 2단계: 에이전트 처리

**에이전트가 자동으로**:
```python
# 에이전트 내부 처리
from tools.project_management.agent_tools.create_epic import create_epic

# 1. ideation 정보 조회
ideation_id = "ideation-object-interaction-handler-refactoring"
ideation_item = await db.get_item(ideation_id)
ideation_file = await read_file(ideation_item.file_path)

# 2. Epic ID 생성
epic_id = f"EPIC-{get_next_epic_number()}"  # EPIC-001

# 3. Epic 문서 생성
epic_file_path = f"docs/project-management/epics/{epic_id}.md"
epic_content = f"""---
epic_id: {epic_id}
ideation_id: {ideation_id}
status: epic
title: {ideation_item.title}
description: {ideation_item.description}
tasks: []
created_at: {datetime.now().isoformat()}
---

# {ideation_item.title}

## 설명
{ideation_item.description}

## 관련 Ideation
- [{ideation_id}](../ideation/object-interaction/OBJECT_INTERACTION_HANDLER_REFACTORING.md)
"""

# 4. Epic 파일 저장
await write_file(epic_file_path, epic_content)
```

#### 3단계: 연관 관계 자동 설정

**워크플로우 엔진이 자동 처리**:
```python
# tools/project_management/engine/workflow_engine.py
async def create_epic_from_ideation(
    self,
    ideation_id: str,
    epic_id: str
):
    # 1. Epic 항목 데이터베이스에 저장
    epic_item = await db.create_workflow_item(
        id=epic_id,
        type='epic',
        title=title,
        status='epic',
        file_path=epic_file_path,
        metadata={
            'epic_id': epic_id,
            'ideation_id': ideation_id,  # 연관 관계
            'tasks': []
        }
    )
    
    # 2. ideation 항목 업데이트 (epic_id 추가)
    ideation_item = await db.get_item(ideation_id)
    ideation_item.metadata['epic_id'] = epic_id
    await db.update_item(ideation_id, ideation_item)
    
    # 3. ideation 문서 업데이트 (epic_id 추가)
    ideation_content = await read_file(ideation_item.file_path)
    updated_content = update_yaml_frontmatter(
        ideation_content,
        {'epic_id': epic_id}
    )
    await write_file(ideation_item.file_path, updated_content)
    
    return epic_item
```

**결과**:
- Epic 문서 생성: `docs/project-management/epics/EPIC-001.md`
- ideation 문서 업데이트: `epic_id: EPIC-001` 추가
- 데이터베이스에 양방향 연관 관계 저장

#### 4단계: 대시보드 표시

**대시보드가 연관 관계 표시**:
```python
# Epic 항목 표시
st.markdown(f"### {epic_item.title}")
st.caption(f"Related Ideation: {ideation_id}")

# ideation 항목 표시
st.markdown(f"### {ideation_item.title}")
st.caption(f"Related Epic: {epic_id}")
```

---

### 시나리오 3: Task 생성 및 의존성 설정

#### 1단계: Epic 분석 및 Task 분해

**에이전트가 자동으로**:
```python
# Epic을 분석하여 Task 분해
epic_item = await db.get_item("EPIC-001")

# Task 목록 생성
tasks = [
    {
        "title": "ObjectInteractionHandlerBase 인터페이스 정의",
        "estimated_hours": 2.0
    },
    {
        "title": "ObjectInteractionHandlerBase 구현",
        "estimated_hours": 4.0,
        "dependencies": ["TASK-001"]  # 첫 번째 Task에 의존
    }
]

# 각 Task 생성
for i, task_data in enumerate(tasks, 1):
    task_id = f"TASK-{i:03d}"
    await create_task(
        task_id=task_id,
        epic_id="EPIC-001",
        title=task_data["title"],
        dependencies=task_data.get("dependencies", [])
    )
```

#### 2단계: Task 문서 생성

**각 Task마다**:
```markdown
---
task_id: TASK-001
epic_id: EPIC-001
status: task
title: ObjectInteractionHandlerBase 인터페이스 정의
estimated_hours: 2.0
todos: []
dependencies: []
created_at: 2026-01-01T12:00:00Z
---

# ObjectInteractionHandlerBase 인터페이스 정의

## 설명
ObjectInteractionHandlerBase의 인터페이스를 정의합니다.

## 관련 Epic
- [EPIC-001](../epics/EPIC-001.md)
```

#### 3단계: 의존성 자동 설정

**워크플로우 엔진이 자동 처리**:
```python
# TASK-002 생성 시
task_2 = await create_task(
    task_id="TASK-002",
    epic_id="EPIC-001",
    dependencies=["TASK-001"]
)

# 데이터베이스에 의존성 저장
task_2.metadata['dependencies'] = ["TASK-001"]

# TASK-001에도 역참조 추가 (선택사항)
task_1 = await db.get_item("TASK-001")
task_1.metadata.setdefault('dependents', []).append("TASK-002")
await db.update_item("TASK-001", task_1)
```

---

### 시나리오 4: TODO 제출 및 승인

#### 1단계: 에이전트가 코드 구현

**에이전트가 작업**:
- 코드 구현
- 테스트 작성
- 커버리지 확인

#### 2단계: TODO YAML 제출

**에이전트가 YAML 파일 생성**:
```python
# tools/project_management/agent_tools/submit_todo.py
from pathlib import Path
import yaml

async def submit_todo(todo_data: dict):
    # 1. TODO ID 생성
    todo_id = f"TODO-{get_next_todo_number()}"
    
    # 2. YAML 파일 생성
    submission_dir = Path("docs/project-management/submissions")
    yaml_path = submission_dir / f"{todo_id}.yaml"
    
    yaml_content = {
        "todo_id": todo_id,
        "task_id": todo_data["task_id"],
        "action": "submit",
        "status": "implement_green",
        "title": todo_data["title"],
        "description": todo_data["description"],
        "file": todo_data["file"],
        "code_changes": todo_data["code_changes"],
        "test_results": todo_data["test_results"],
        "submitted_at": datetime.now().isoformat(),
        "submitted_by": "agent"
    }
    
    # 3. YAML 파일 저장
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_content, f, allow_unicode=True)
```

**결과**:
- 파일 생성: `docs/project-management/submissions/TODO-001.yaml`

#### 3단계: 시스템 감지 및 처리

**파일 감시 시스템**:
```python
class SubmissionWatcher(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith('.yaml') and 'submissions' in event.src_path:
            asyncio.create_task(self.process_submission(event.src_path))
    
    async def process_submission(self, yaml_path: str):
        # 1. YAML 파싱
        with open(yaml_path, 'r') as f:
            submission_data = yaml.safe_load(f)
        
        # 2. 유효성 검증
        validation_result = await validate_submission(submission_data)
        if not validation_result.valid:
            # 오류 처리
            return
        
        # 3. 데이터베이스에 저장
        await db.create_submission(
            id=submission_data['todo_id'],
            item_id=submission_data['task_id'],
            action=submission_data['action'],
            yaml_path=yaml_path,
            status='pending'
        )
        
        # 4. 대시보드에 알림
        await notify_dashboard('new_submission', submission_data['todo_id'])
```

#### 4단계: 대시보드 표시

**Submissions 페이지**:
```python
# tools/project_management/dashboard/pages/submissions.py
pending_submissions = await db.get_submissions(status='pending')

for submission in pending_submissions:
    with st.expander(f"[{submission.item_id}] {submission.title}"):
        st.write(submission.description)
        st.json(submission.data)  # YAML 내용 표시
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("승인", key=f"approve_{submission.id}"):
                await approve_submission(submission.id)
        with col2:
            if st.button("거부", key=f"reject_{submission.id}"):
                reason = st.text_input("거부 사유")
                await reject_submission(submission.id, reason)
```

#### 5단계: 사용자 승인

**사용자가 "승인" 클릭**:
```python
async def approve_submission(submission_id: str):
    # 1. 제출 정보 조회
    submission = await db.get_submission(submission_id)
    
    # 2. 워크플로우 엔진 실행
    engine = WorkflowEngine()
    
    # 3. 상태 전환 (예: development → qa)
    await engine.transition_status(
        item_id=submission.item_id,
        to_status=submission.to_status,
        reason="사용자 승인"
    )
    
    # 4. 제출 상태 업데이트
    submission.status = 'approved'
    submission.reviewed_at = datetime.now()
    await db.update_submission(submission_id, submission)
    
    # 5. 문서 자동 처리
    await document_manager.handle_status_transition(
        item_id=submission.item_id,
        from_status=submission.from_status,
        to_status=submission.to_status
    )
```

---

## 파일 형식 및 메타데이터

### Markdown 문서 (ideation, epic, task)

**형식**: YAML frontmatter + Markdown 본문

**예시**:
```markdown
---
ideation_id: ideation-object-interaction-handler-refactoring
status: ideation
priority: high
category: object-interaction
created_at: 2026-01-01T12:00:00Z
author: agent
epic_id: null
---

# ObjectInteractionHandlerBase 리팩토링

## 설명
ObjectInteractionHandlerBase 클래스를 모듈화하고 개선합니다.

## 상세 내용
...
```

### YAML 제출 파일 (submissions)

**형식**: 순수 YAML

**예시**:
```yaml
todo_id: TODO-001
task_id: TASK-001
action: submit
status: implement_green
title: "ObjectInteractionHandlerBase 클래스 구현"
description: |
  오브젝트 상호작용 핸들러 베이스 클래스 구현 완료.
code_changes:
  - file: app/handlers/object_interaction_base.py
    added_lines: 150
test_results:
  total: 10
  passed: 10
  coverage: 0.95
submitted_at: 2026-01-01T12:00:00Z
submitted_by: agent
```

---

## 연관 관계 자동 설정

### 연관 관계 타입

1. **ideation ↔ epic**: 1:1
2. **epic ↔ task**: 1:N
3. **task ↔ todo**: 1:N
4. **task ↔ task**: N:N (의존성)

### 자동 설정 로직

**Epic 생성 시**:
```python
# 1. Epic 항목 생성
epic_item = {
    "id": "EPIC-001",
    "metadata": {
        "ideation_id": "ideation-xxx"  # 자동 설정
    }
}

# 2. ideation 항목 업데이트
ideation_item = {
    "id": "ideation-xxx",
    "metadata": {
        "epic_id": "EPIC-001"  # 자동 추가
    }
}

# 3. 문서 업데이트
# ideation 문서에 epic_id 추가
# epic 문서에 ideation_id 포함
```

**Task 생성 시**:
```python
# 1. Task 항목 생성
task_item = {
    "id": "TASK-001",
    "metadata": {
        "epic_id": "EPIC-001",  # 자동 설정
        "dependencies": ["TASK-000"]  # 명시적 설정
    }
}

# 2. Epic 항목 업데이트
epic_item = {
    "id": "EPIC-001",
    "metadata": {
        "tasks": ["TASK-001"]  # 자동 추가
    }
}
```

---

## 시스템 감지 및 처리

### 파일 감시 방식

**옵션 1: Watchdog (실시간)**
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

observer = Observer()
observer.schedule(IdeationWatcher(), 'docs/ideation', recursive=True)
observer.schedule(SubmissionWatcher(), 'docs/project-management/submissions', recursive=False)
observer.start()
```

**옵션 2: Polling (주기적 스캔)**
```python
async def poll_for_changes():
    while True:
        # ideation 폴더 스캔
        await scan_folder('docs/ideation')
        # submissions 폴더 스캔
        await scan_folder('docs/project-management/submissions')
        await asyncio.sleep(5)  # 5초마다
```

### 처리 순서

1. **파일 감지** → 파일 생성 이벤트
2. **파일 파싱** → 메타데이터 추출
3. **유효성 검증** → 규칙 확인
4. **데이터베이스 저장** → 상태 저장
5. **대시보드 알림** → 실시간 업데이트

---

## 다음 단계

1. **프로토타입 구현**: 파일 감시 시스템부터 시작
2. **통합 테스트**: 전체 워크플로우 테스트
3. **사용자 피드백**: 실제 사용 후 개선

