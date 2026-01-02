# Streamlit 프로젝트 관리 대시보드 설계

**작성일**: 2026-01-01  
**목적**: Streamlit 기반 프로젝트 관리 대시보드 설계 및 에이전트 통합  
**관련 문서**: 
- `AUTOMATED_PROJECT_MANAGEMENT_PROPOSAL.md`
- `WORKFLOW_PROCESS_DESIGN.md`

---

## 📋 목차

1. [대시보드 개요](#대시보드-개요)
2. [기능 설계](#기능-설계)
3. [YAML 기반 TODO 제출 시스템](#yaml-기반-todo-제출-시스템)
4. [상태 변경 자동화](#상태-변경-자동화)
5. [에이전트 통합](#에이전트-통합)
6. [구현 계획](#구현-계획)

---

## 대시보드 개요

### 목적

1. **프로젝트 상태 시각화**: 모든 작업의 현재 상태를 한눈에 파악
2. **상태 변경 관리**: 드래그 앤 드롭 또는 버튼으로 상태 변경
3. **자동 문서 관리**: 상태 변경 시 자동으로 문서 이동 및 업데이트
4. **에이전트 작업 제출**: 에이전트가 YAML로 TODO 제출 및 상태 업데이트

### 기술 스택

- **Frontend**: Streamlit
- **Backend**: Python (FastAPI 또는 Streamlit 내장)
- **Data Format**: YAML (TODO 제출, 메타데이터)
- **Storage**: 파일 시스템 (문서 기반) + SQLite (상태 추적)

---

## 기능 설계

### 1. 대시보드 메인 화면

**레이아웃**:
```
┌─────────────────────────────────────────────────────────┐
│  RPG Engine 프로젝트 관리 대시보드                        │
├─────────────────────────────────────────────────────────┤
│  [필터] [카테고리] [상태] [우선순위] [검색]              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  📊 대시보드 요약                                        │
│  ┌──────────┬──────────┬──────────┬──────────┐          │
│  │ Ideation │  Epic   │  Task   │   Done   │          │
│  │    12    │    8    │   24    │   45     │          │
│  └──────────┴──────────┴──────────┴──────────┘          │
│                                                          │
│  📋 작업 목록 (칸반 보드)                                │
│  ┌──────────┬──────────┬──────────┬──────────┐          │
│  │ Ideation │  Epic   │  Task   │Development│          │
│  ├──────────┼──────────┼──────────┼──────────┤          │
│  │ [카드1]  │ [카드1] │ [카드1] │ [카드1]  │          │
│  │ [카드2]  │ [카드2] │ [카드2] │ [카드2]  │          │
│  │ [카드3]  │ [카드3] │ [카드3] │ [카드3]  │          │
│  └──────────┴──────────┴──────────┴──────────┘          │
│                                                          │
│  📝 에이전트 제출 대기                                   │
│  ┌──────────────────────────────────────────┐          │
│  │ [TODO-001] Action Handler 리팩토링        │          │
│  │ 상태: development → qa                    │          │
│  │ [승인] [거부] [보류]                      │          │
│  └──────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────┘
```

### 2. 작업 카드

**카드 정보**:
- 제목
- 상태 배지
- 우선순위 표시
- 진행률 (Task의 경우)
- 마지막 업데이트 시간
- 관련 문서 링크

**카드 액션**:
- 클릭: 상세 정보 보기
- 드래그 앤 드롭: 상태 변경
- 우클릭: 컨텍스트 메뉴 (편집, 삭제, 의존성 보기)

### 3. 상세 정보 패널

**표시 정보**:
- 작업 메타데이터
- 관련 문서
- 의존성 관계
- 진행 이력
- 에이전트 제출 내역
- **Audit 결과** (Integrity 체크리스트)

**액션**:
- 상태 변경
- 우선순위 변경
- 의존성 추가/제거
- 문서 링크 추가
- **Integrity 위반 상세 보기** (Audit 단계)

---

## YAML 기반 TODO 제출 시스템

### 1. TODO 제출 형식

**에이전트가 제출하는 YAML 형식**:

```yaml
# docs/project-management/submissions/TODO-001.yaml
todo_id: TODO-001
task_id: TASK-001
action: submit|update|transition
status: development|qa|audit|done
title: "ObjectInteractionHandlerBase 클래스 구현"
description: |
  오브젝트 상호작용 핸들러 베이스 클래스 구현 완료.
  - ObjectInteractionHandlerBase 클래스 생성
  - 공통 메서드 구현
  - 테스트 작성 완료

file: app/handlers/object_interaction_base.py
line: 1
code_changes:
  - file: app/handlers/object_interaction_base.py
    added_lines: 150
    modified_lines: 0
    deleted_lines: 0

test_results:
  total: 10
  passed: 10
  failed: 0
  coverage: 0.95

metadata:
  estimated_hours: 4.0
  actual_hours: 3.5
  complexity: medium
  dependencies: []

transition_request:
  from: development
  to: qa
  reason: "코드 구현 완료 및 테스트 통과"

submitted_at: 2026-01-01T12:00:00Z
submitted_by: agent
```

### 2. 제출 프로세스

**에이전트 작업 흐름**:
1. 코드 구현 완료
2. TODO YAML 파일 생성 (`docs/project-management/submissions/{TODO_ID}.yaml`)
3. 대시보드에 제출 알림
4. 사용자 승인 대기

**대시보드 처리**:
1. 제출된 YAML 파일 감지
2. 유효성 검증
3. "에이전트 제출 대기" 섹션에 표시
4. 사용자 승인 시 상태 전환 및 문서 업데이트

### 3. 상태 업데이트 제출

**상태 전환 요청**:

```yaml
# docs/project-management/submissions/TRANSITION-001.yaml
transition_id: TRANSITION-001
item_type: todo|task|epic|ideation
item_id: TODO-001
from_status: development
to_status: qa
reason: "코드 구현 완료 및 테스트 통과"
validation:
  code_implemented: true
  tests_pass: true
  coverage: 0.95
  linter_errors: 0
submitted_at: 2026-01-01T12:00:00Z
submitted_by: agent
```

---

## 상태 변경 자동화

### 1. 상태 변경 프로세스

**사용자 액션**:
- 대시보드에서 상태 변경 (드래그 앤 드롭 또는 버튼)
- 에이전트 제출 승인/거부

**자동 처리**:
1. 상태 변경 검증
2. 워크플로우 규칙 확인
3. 문서 자동 이동/업데이트
4. CHANGELOG 자동 업데이트
5. IMPLEMENTATION_STATUS.md 자동 업데이트

### 2. 문서 자동 이동

**상태별 문서 위치**:

```
ideation → docs/ideation/{category}/{TITLE}.md
epic → docs/project-management/epics/{EPIC_ID}.md
task → docs/project-management/tasks/{TASK_ID}.md
todo → docs/project-management/todos/{TODO_ID}.md (또는 코드 내 TODO)
qa → docs/audit/qa/{QA_ID}.md
audit → docs/audit/{AUDIT_ID}.md
done → (문서 유지, 상태만 변경)
deprecated → docs/archive/deprecated/ideation/[deprecated]{TITLE}.md
```

**자동 이동 로직**:

```python
async def move_document(item: WorkflowItem, new_status: str):
    """상태 변경 시 문서 자동 이동"""
    old_path = item.file_path
    new_path = get_path_for_status(new_status, item)
    
    if old_path != new_path:
        # 파일 이동
        await move_file(old_path, new_path)
        
        # 메타데이터 업데이트
        await update_metadata(new_path, {
            "status": new_status,
            "updated_at": datetime.now(),
            "previous_path": old_path
        })
        
        # 관련 문서 링크 업데이트
        await update_related_documents(item)
```

### 3. CHANGELOG 자동 업데이트

**업데이트 규칙**:
- 작업이 `done` 상태가 되면 자동으로 CHANGELOG에 추가
- 형식: 표준 CHANGELOG 형식 준수
- 섹션: 적절한 섹션에 자동 분류

**예제**:
```markdown
## 주요 기능 구현 내역

### ObjectInteractionHandlerBase 구현

**완료일**: 2026-01-01

**구현 내용**:
- ObjectInteractionHandlerBase 클래스 구현
- 공통 메서드 구현
- 테스트 작성 완료

**관련 문서**:
- `docs/ideation/object-interaction/OBJECT_INTERACTION_REFACTORING_PLAN.md`
```

### 4. IMPLEMENTATION_STATUS.md 자동 업데이트

**업데이트 규칙**:
- 작업 완료 시 구현 상태 표 자동 업데이트
- 완료율 재계산
- 관련 문서 상태 업데이트

---

## 에이전트 통합

### 1. 에이전트 제출 API

**에이전트가 사용할 수 있는 함수**:

```python
# tools/agent_submission.py
async def submit_todo(todo_data: dict) -> SubmissionResult:
    """TODO 제출"""
    # YAML 파일 생성
    # 대시보드에 알림
    # 검증 수행

async def request_transition(item_id: str, from_status: str, to_status: str, reason: str) -> TransitionResult:
    """상태 전환 요청"""
    # 전환 요청 YAML 생성
    # 검증 수행
    # 대시보드에 알림

async def update_progress(item_id: str, progress: dict) -> UpdateResult:
    """진행 상황 업데이트"""
    # 진행 상황 YAML 생성
    # 대시보드 업데이트
```

### 2. 에이전트 워크플로우

**에이전트 작업 순서**:
1. 사용자 요청 수신
2. ideation 문서 생성 (필요 시)
3. Epic/Task/TODO 생성 (워크플로우에 따라)
4. 코드 구현
5. TODO 제출 (YAML)
6. 상태 전환 요청
7. 사용자 승인 대기
8. 승인 시 자동 처리

### 3. 에이전트 온보딩

**필수 읽기**:
- `docs/rules/PROJECT_MANAGEMENT_WORKFLOW.md`
- `docs/rules/AGENT_WORKFLOW_GUIDE.md`
- `docs/ideation/project-management/STREAMLIT_DASHBOARD_DESIGN.md`

**도구 사용법**:
- `tools/agent_submission.py`: 제출 도구
- `tools/workflow_engine.py`: 워크플로우 엔진
- `tools/project_manager.py`: 프로젝트 관리

---

## 구현 계획

### Phase 1: 기본 대시보드 (1주)

1. **Streamlit 앱 구조**
   - 메인 대시보드 페이지
   - 작업 목록 표시
   - 필터 및 검색 기능

2. **상태 추적 시스템**
   - SQLite 데이터베이스 (상태 추적)
   - YAML 파일 파싱
   - 상태 동기화

### Phase 2: 상태 변경 자동화 (1주)

3. **상태 변경 로직**
   - 드래그 앤 드롭 지원
   - 워크플로우 검증
   - 문서 자동 이동

4. **문서 관리**
   - 파일 이동 자동화
   - 메타데이터 업데이트
   - 링크 업데이트

### Phase 3: 에이전트 통합 (1주)

5. **YAML 제출 시스템**
   - 제출 형식 정의
   - 유효성 검증
   - 승인/거부 처리

6. **자동 업데이트**
   - CHANGELOG 자동 업데이트
   - IMPLEMENTATION_STATUS.md 자동 업데이트

### Phase 4: 고급 기능 (1주)

7. **의존성 관리**
   - 의존성 그래프 시각화
   - 블로킹 작업 표시

8. **리포트 생성**
   - 진행 상황 리포트
   - 벨로시티 리포트
   - 품질 메트릭

---

## 데이터 구조

### SQLite 스키마

```sql
CREATE TABLE workflow_items (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,  -- ideation|epic|task|todo|qa|audit
    title TEXT NOT NULL,
    status TEXT NOT NULL,
    priority TEXT,  -- high|medium|low
    file_path TEXT,
    metadata JSON,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE submissions (
    id TEXT PRIMARY KEY,
    item_id TEXT,
    action TEXT,  -- submit|update|transition
    yaml_path TEXT,
    status TEXT,  -- pending|approved|rejected
    submitted_at TIMESTAMP,
    reviewed_at TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES workflow_items(id)
);

CREATE TABLE transitions (
    id TEXT PRIMARY KEY,
    item_id TEXT,
    from_status TEXT,
    to_status TEXT,
    reason TEXT,
    approved_by TEXT,
    transitioned_at TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES workflow_items(id)
);
```

---

## 사용자 인터페이스

### 1. 메인 대시보드

**Streamlit 코드 구조**:
```python
import streamlit as st
from tools.project_manager import ProjectManager
from tools.workflow_engine import WorkflowEngine

st.title("RPG Engine 프로젝트 관리 대시보드")

# 필터
category = st.selectbox("카테고리", ["전체", "action-handler", ...])
status = st.multiselect("상태", ["ideation", "epic", "task", ...])

# 대시보드 요약
col1, col2, col3, col4 = st.columns(4)
col1.metric("Ideation", count_by_status("ideation"))
col2.metric("Epic", count_by_status("epic"))
col3.metric("Task", count_by_status("task"))
col4.metric("Done", count_by_status("done"))

# 칸반 보드
kanban_board = create_kanban_board(items, status_filter=status)
st.components.v1.html(kanban_board, height=600)

# 에이전트 제출 대기
pending_submissions = get_pending_submissions()
for submission in pending_submissions:
    with st.expander(f"[{submission.item_id}] {submission.title}"):
        st.write(submission.description)
        if st.button("승인", key=f"approve_{submission.id}"):
            approve_submission(submission)
        if st.button("거부", key=f"reject_{submission.id}"):
            reject_submission(submission)
```

### 2. 작업 상세 페이지

**표시 정보**:
- 작업 메타데이터
- 관련 문서
- 의존성 관계
- 진행 이력
- 에이전트 제출 내역

**액션 버튼**:
- 상태 변경
- 우선순위 변경
- 의존성 추가/제거

---

## 다음 단계

1. **프로토타입 개발**: 기본 대시보드 구현
2. **통합 테스트**: 실제 시나리오로 테스트
3. **에이전트 통합**: 에이전트가 사용할 수 있도록 통합
4. **문서화**: 사용 가이드 작성

