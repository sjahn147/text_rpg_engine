# 에이전트 기반 프로젝트 관리 도구 전체 명세서 (v2.0)

**작성일**: 2026-01-01  
**버전**: 2.0  
**목적**: 문서 기반 + 자동화된 프로젝트 관리 시스템의 완전한 명세  
**핵심 원칙**: 문서는 문서대로, 연결고리는 자동화

---

## 📋 목차

1. [핵심 설계 원칙](#핵심-설계-원칙)
2. [시스템 아키텍처](#시스템-아키텍처)
3. [에이전트 도구 사용법](#에이전트-도구-사용법)
4. [문서 구조 및 메타데이터](#문서-구조-및-메타데이터)
5. [자동 연결 메커니즘](#자동-연결-메커니즘)
6. [대시보드 통합](#대시보드-통합)
7. [API 스펙](#api-스펙)
8. [구현 상세](#구현-상세)

---

## 핵심 설계 원칙

### 1. 문서 우선 (Document-First)

- **문서는 문서대로**: 모든 작업은 Markdown 문서로 시작
- **상세한 내용**: 에이전트가 읽고 이해할 수 있도록 상세히 작성
- **정해진 위치**: 각 상태별로 정해진 폴더에 저장

### 2. 자동화된 연결 (Automated Linking)

- **에이전트는 ID만 참조**: 연결고리는 시스템이 자동 처리
- **양방향 자동 연결**: 한쪽에서 연결하면 반대편도 자동 업데이트
- **문서 자동 업데이트**: 연결 시 관련 문서도 자동으로 업데이트

### 3. 도구 기반 생성 (Tool-Based Creation)

- **에이전트는 도구 사용**: 직접 파일 작성하지 않고 도구 사용
- **템플릿 기반**: 도구가 템플릿을 사용해서 일관된 문서 생성
- **메타데이터 자동 관리**: 도구가 메타데이터 파일도 자동 생성

### 4. 하이브리드 저장 (Hybrid Storage)

- **문서**: Markdown 파일 (사람이 읽기 쉬움)
- **메타데이터**: YAML 파일 + 데이터베이스 (시스템이 관리)
- **연결 정보**: 데이터베이스 + 문서 내 자동 주입

---

## 시스템 아키텍처

### 전체 구조

```
┌─────────────────────────────────────────────────────────┐
│                    사용자 (User)                         │
│              Cursor에서 지시 또는                        │
│              Streamlit 대시보드 사용                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│                  에이전트 (Agent)                         │
│  - 도구 사용 (CLI/API)                                   │
│  - 문서 생성 요청                                        │
│  - 연결 ID만 참조                                        │
└────────────────────┬────────────────────────────────────┘
                     │ 도구 호출
                     ↓
┌─────────────────────────────────────────────────────────┐
│            프로젝트 관리 도구 (Tools)                     │
│  - create_ideation()                                     │
│  - create_epic()                                         │
│  - create_task()                                         │
│  - submit_todo()                                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ├──→ 문서 생성 (템플릿 사용)
                     ├──→ 메타데이터 파일 생성
                     ├──→ API 호출 (DB 등록)
                     └──→ 자동 연결 처리
                     ↓
┌─────────────────────────────────────────────────────────┐
│              워크플로우 API (FastAPI)                     │
│  - 문서 등록                                              │
│  - 메타데이터 관리                                        │
│  - 연결 관계 설정                                         │
│  - 상태 관리                                              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│              데이터베이스 (SQLite)                       │
│  - 작업 항목 저장                                         │
│  - 메타데이터 저장                                        │
│  - 연결 관계 저장                                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│          Streamlit 대시보드                              │
│  - 데이터베이스에서 조회                                  │
│  - 문서 링크 표시                                         │
│  - 실시간 업데이트                                        │
└─────────────────────────────────────────────────────────┘
```

### 파일 구조

```
docs/
├── ideation/
│   └── {category}/
│       ├── {TITLE}.md              # 문서 (Markdown)
│       └── {TITLE}.meta.yaml       # 메타데이터 (YAML)
├── project-management/
│   ├── epics/
│   │   ├── {EPIC_ID}.md
│   │   └── {EPIC_ID}.meta.yaml
│   ├── tasks/
│   │   ├── {TASK_ID}.md
│   │   └── {TASK_ID}.meta.yaml
│   ├── todos/
│   │   ├── {TODO_ID}.md
│   │   └── {TODO_ID}.meta.yaml
│   └── submissions/
│       └── {TYPE}-{ID}.yaml        # 제출 파일 (YAML만)
```

---

## 에이전트 도구 사용법

### 1. ideation 생성

**에이전트가 사용하는 도구**:
```python
from tools.project_management.cli import create_ideation

# 사용법
result = create_ideation(
    title="ObjectInteractionHandlerBase 리팩토링",
    description="ObjectInteractionHandlerBase 클래스를 모듈화하고 개선합니다.",
    category="object-interaction",
    priority="high",
    content="""
## 목표
- 모듈화
- 코드 품질 개선
- 테스트 커버리지 향상

## 상세 내용
ObjectInteractionHandlerBase는 현재 모든 오브젝트 상호작용을 처리하고 있습니다.
이를 카테고리별로 모듈화하여 유지보수성을 향상시키겠습니다.

## 구현 계획
1. 인터페이스 정의
2. 카테고리별 핸들러 분리
3. 테스트 작성
"""
)
```

**도구가 자동으로 하는 일**:
1. **ID 생성**: `ideation-object-interaction-handler-refactoring`
2. **문서 생성**: `docs/ideation/object-interaction/OBJECT_INTERACTION_HANDLER_REFACTORING.md`
   - 템플릿 사용
   - 제목, 설명, 상세 내용 포함
   - ID 자동 주입
3. **메타데이터 파일 생성**: `{TITLE}.meta.yaml`
4. **API 호출**: DB에 등록
5. **응답 반환**: `{"id": "ideation-xxx", "file_path": "...", ...}`

**생성되는 문서 예시**:
```markdown
# ObjectInteractionHandlerBase 리팩토링

**ID**: ideation-object-interaction-handler-refactoring
**상태**: ideation
**우선순위**: high
**카테고리**: object-interaction
**생성일**: 2026-01-01T12:00:00Z

## 설명
ObjectInteractionHandlerBase 클래스를 모듈화하고 개선합니다.

## 목표
- 모듈화
- 코드 품질 개선
- 테스트 커버리지 향상

## 상세 내용
ObjectInteractionHandlerBase는 현재 모든 오브젝트 상호작용을 처리하고 있습니다.
이를 카테고리별로 모듈화하여 유지보수성을 향상시키겠습니다.

## 구현 계획
1. 인터페이스 정의
2. 카테고리별 핸들러 분리
3. 테스트 작성
```

**생성되는 메타데이터 파일**:
```yaml
# OBJECT_INTERACTION_HANDLER_REFACTORING.meta.yaml
id: ideation-object-interaction-handler-refactoring
type: ideation
status: ideation
title: ObjectInteractionHandlerBase 리팩토링
category: object-interaction
priority: high
file_path: docs/ideation/object-interaction/OBJECT_INTERACTION_HANDLER_REFACTORING.md
epic_id: null
created_at: 2026-01-01T12:00:00Z
updated_at: 2026-01-01T12:00:00Z
author: agent
```

---

### 2. Epic 생성 및 자동 연결

**에이전트가 사용하는 도구**:
```python
from tools.project_management.cli import create_epic

# 사용법 (ideation ID만 참조)
result = create_epic(
    ideation_id="ideation-object-interaction-handler-refactoring",  # ID만 참조
    title="ObjectInteractionHandlerBase 리팩토링",
    description="ObjectInteractionHandlerBase 클래스를 모듈화하고 개선",
    content="""
## Epic 개요
이 Epic은 ObjectInteractionHandlerBase의 모듈화를 다룹니다.

## 관련 Ideation
- ideation-object-interaction-handler-refactoring

## 예상 작업
1. 인터페이스 정의 (Task 1)
2. 구현 (Task 2)
3. 테스트 (Task 3)
"""
)
```

**도구가 자동으로 하는 일**:
1. **Epic ID 생성**: `EPIC-001`
2. **Epic 문서 생성**: `docs/project-management/epics/EPIC-001.md`
3. **메타데이터 파일 생성**: `EPIC-001.meta.yaml`
   - `ideation_id` 자동 포함
4. **ideation 문서 업데이트**:
   - ideation 문서에 Epic ID 추가
   - ideation 메타데이터 파일에 `epic_id` 추가
5. **API 호출**: 
   - Epic 등록
   - ideation 업데이트
   - 양방향 연결 설정
6. **응답 반환**: `{"epic_id": "EPIC-001", "ideation_id": "ideation-xxx", ...}`

**생성되는 Epic 문서**:
```markdown
# ObjectInteractionHandlerBase 리팩토링

**ID**: EPIC-001
**상태**: epic
**관련 Ideation**: ideation-object-interaction-handler-refactoring
**생성일**: 2026-01-01T12:00:00Z

## Epic 개요
이 Epic은 ObjectInteractionHandlerBase의 모듈화를 다룹니다.

## 관련 Ideation
- [ideation-object-interaction-handler-refactoring](../../ideation/object-interaction/OBJECT_INTERACTION_HANDLER_REFACTORING.md)

## 예상 작업
1. 인터페이스 정의 (Task 1)
2. 구현 (Task 2)
3. 테스트 (Task 3)
```

**자동 업데이트되는 ideation 문서**:
```markdown
# ObjectInteractionHandlerBase 리팩토링

**ID**: ideation-object-interaction-handler-refactoring
**상태**: ideation
**관련 Epic**: EPIC-001  <!-- 자동 추가됨 -->
...
```

---

### 3. Task 생성 및 의존성 설정

**에이전트가 사용하는 도구**:
```python
from tools.project_management.cli import create_task

# 사용법
result = create_task(
    epic_id="EPIC-001",  # Epic ID 참조
    title="ObjectInteractionHandlerBase 인터페이스 정의",
    description="인터페이스를 정의합니다.",
    estimated_hours=2.0,
    dependencies=[],  # 의존성은 ID 리스트
    content="""
## 작업 내용
ObjectInteractionHandlerBase의 인터페이스를 정의합니다.

## 구현 세부사항
1. 인터페이스 메서드 정의
2. 타입 힌트 추가
3. Docstring 작성
"""
)
```

**도구가 자동으로 하는 일**:
1. **Task ID 생성**: `TASK-001`
2. **Task 문서 생성**
3. **메타데이터 파일 생성**
   - `epic_id` 자동 포함
   - `dependencies` 포함
4. **Epic 문서 업데이트**:
   - Epic 문서에 Task 목록 추가
   - Epic 메타데이터에 `tasks` 추가
5. **의존성 Task 업데이트** (있는 경우):
   - 의존성 Task의 `dependents`에 추가
6. **API 호출**: 등록 및 연결

---

### 4. TODO 제출

**에이전트가 사용하는 도구**:
```python
from tools.project_management.cli import submit_todo

# 사용법
result = submit_todo(
    task_id="TASK-001",
    status="implement_green",
    title="ObjectInteractionHandlerBase 클래스 구현",
    description="구현 완료",
    file="app/handlers/object_interaction_base.py",
    code_changes=[
        {
            "file": "app/handlers/object_interaction_base.py",
            "added_lines": 150,
            "modified_lines": 0,
            "deleted_lines": 0
        }
    ],
    test_results={
        "total": 10,
        "passed": 10,
        "failed": 0,
        "coverage": 0.95
    }
)
```

**도구가 자동으로 하는 일**:
1. **TODO ID 생성**: `TODO-001`
2. **제출 YAML 파일 생성**: `docs/project-management/submissions/TODO-001.yaml`
3. **API 호출**: 제출 등록
4. **대시보드에 표시**: 즉시 반영

---

## 문서 구조 및 메타데이터

### 문서 템플릿

**ideation 템플릿**:
```markdown
# {title}

**ID**: {id}
**상태**: ideation
**우선순위**: {priority}
**카테고리**: {category}
**생성일**: {created_at}
{epic_section}  <!-- Epic 생성 시 자동 추가 -->

## 설명
{description}

{content}  <!-- 에이전트가 작성한 상세 내용 -->
```

**epic 템플릿**:
```markdown
# {title}

**ID**: {epic_id}
**상태**: epic
**관련 Ideation**: {ideation_id}
**생성일**: {created_at}

## Epic 개요
{description}

## 관련 Ideation
- [{ideation_id}](../../ideation/{category}/{ideation_file})

{content}

## 작업 목록
{tasks_section}  <!-- Task 생성 시 자동 업데이트 -->
```

### 메타데이터 파일 구조

**공통 필드**:
```yaml
id: {unique_id}
type: ideation|epic|task|todo
status: {current_status}
title: {title}
file_path: {relative_path}
created_at: {iso_timestamp}
updated_at: {iso_timestamp}
author: agent|user
```

**타입별 추가 필드**:
- **ideation**: `category`, `priority`, `epic_id`
- **epic**: `epic_id`, `ideation_id`, `tasks[]`
- **task**: `task_id`, `epic_id`, `estimated_hours`, `dependencies[]`, `todos[]`
- **todo**: `todo_id`, `task_id`, `file`, `code_changes`, `test_results`

---

## 자동 연결 메커니즘

### 연결 규칙

1. **ideation ↔ epic**: 1:1
   - Epic 생성 시 `ideation_id` 참조
   - → ideation 문서에 `epic_id` 자동 추가
   - → ideation 메타데이터 파일 업데이트

2. **epic ↔ task**: 1:N
   - Task 생성 시 `epic_id` 참조
   - → Epic 문서에 Task 목록 자동 추가
   - → Epic 메타데이터 파일 업데이트

3. **task ↔ todo**: 1:N
   - TODO 제출 시 `task_id` 참조
   - → Task 문서에 TODO 목록 자동 추가

4. **task ↔ task**: N:N (의존성)
   - Task 생성 시 `dependencies` 참조
   - → 의존성 Task의 `dependents` 자동 추가

### 자동 업데이트 프로세스

**Epic 생성 시**:
```python
# 도구 내부 로직
async def create_epic(ideation_id: str, ...):
    # 1. Epic 생성
    epic_id = generate_epic_id()
    epic_doc = create_epic_document(epic_id, ideation_id, ...)
    epic_meta = create_epic_metadata(epic_id, ideation_id, ...)
    
    # 2. ideation 업데이트
    ideation_doc = read_document(ideation_id)
    ideation_doc = add_epic_reference(ideation_doc, epic_id)  # 문서 업데이트
    write_document(ideation_id, ideation_doc)
    
    ideation_meta = read_metadata(ideation_id)
    ideation_meta['epic_id'] = epic_id  # 메타데이터 업데이트
    write_metadata(ideation_id, ideation_meta)
    
    # 3. API 호출
    await api.create_epic(epic_id, ideation_id, ...)
    await api.update_ideation(ideation_id, epic_id)
    
    return {"epic_id": epic_id, "ideation_id": ideation_id}
```

---

## 대시보드 통합

### 데이터 조회

**대시보드가 하는 일**:
1. **데이터베이스에서 조회**: 모든 작업 항목
2. **메타데이터 파일 읽기**: 최신 정보 확인
3. **문서 링크 표시**: 클릭 시 문서 열기
4. **연결 관계 시각화**: 그래프로 표시

**예시**:
```python
# Streamlit 대시보드
items = await db.get_all_items()

for item in items:
    # 메타데이터 파일 읽기
    meta = read_metadata_file(item.file_path.replace('.md', '.meta.yaml'))
    
    # 문서 링크
    st.markdown(f"[{item.title}]({item.file_path})")
    
    # 연결 관계 표시
    if meta.get('epic_id'):
        st.caption(f"Epic: {meta['epic_id']}")
    if meta.get('ideation_id'):
        st.caption(f"Ideation: {meta['ideation_id']}")
```

---

## API 스펙

### 워크플로우 API

**Base URL**: `http://localhost:8000/api/workflow`

**1. ideation 생성**
```http
POST /api/workflow/create_ideation
Content-Type: application/json

{
    "title": "ObjectInteractionHandlerBase 리팩토링",
    "description": "...",
    "category": "object-interaction",
    "priority": "high",
    "content": "..."
}

Response:
{
    "success": true,
    "id": "ideation-object-interaction-handler-refactoring",
    "file_path": "docs/ideation/object-interaction/OBJECT_INTERACTION_HANDLER_REFACTORING.md",
    "meta_path": "docs/ideation/object-interaction/OBJECT_INTERACTION_HANDLER_REFACTORING.meta.yaml"
}
```

**2. Epic 생성**
```http
POST /api/workflow/create_epic
Content-Type: application/json

{
    "ideation_id": "ideation-object-interaction-handler-refactoring",
    "title": "ObjectInteractionHandlerBase 리팩토링",
    "description": "...",
    "content": "..."
}

Response:
{
    "success": true,
    "epic_id": "EPIC-001",
    "ideation_id": "ideation-object-interaction-handler-refactoring",
    "file_path": "docs/project-management/epics/EPIC-001.md",
    "ideation_updated": true  // ideation 문서도 업데이트됨
}
```

**3. Task 생성**
```http
POST /api/workflow/create_task
Content-Type: application/json

{
    "epic_id": "EPIC-001",
    "title": "인터페이스 정의",
    "description": "...",
    "estimated_hours": 2.0,
    "dependencies": [],
    "content": "..."
}

Response:
{
    "success": true,
    "task_id": "TASK-001",
    "epic_id": "EPIC-001",
    "file_path": "docs/project-management/tasks/TASK-001.md",
    "epic_updated": true  // Epic 문서도 업데이트됨
}
```

**4. TODO 제출**
```http
POST /api/submissions/submit_todo
Content-Type: application/json

{
    "task_id": "TASK-001",
    "status": "implement_green",
    "title": "클래스 구현",
    "code_changes": [...],
    "test_results": {...}
}

Response:
{
    "success": true,
    "todo_id": "TODO-001",
    "submission_path": "docs/project-management/submissions/TODO-001.yaml",
    "status": "pending"
}
```

---

## 구현 상세

### 도구 구현 (CLI)

**파일**: `tools/project_management/cli.py`

```python
from pathlib import Path
import yaml
import httpx
from typing import Optional, List, Dict, Any

class ProjectManagementCLI:
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.client = httpx.AsyncClient(base_url=api_base_url)
    
    async def create_ideation(
        self,
        title: str,
        description: str,
        category: str,
        priority: str = "medium",
        content: str = ""
    ) -> Dict[str, Any]:
        """ideation 생성"""
        # 1. API 호출
        response = await self.client.post(
            "/api/workflow/create_ideation",
            json={
                "title": title,
                "description": description,
                "category": category,
                "priority": priority,
                "content": content
            }
        )
        result = response.json()
        
        # 2. 문서 생성 (API가 반환한 경로에)
        if result["success"]:
            doc_path = Path(result["file_path"])
            meta_path = Path(result["meta_path"])
            
            # 문서 내용 생성
            doc_content = self._generate_ideation_document(
                result["id"], title, description, content, category, priority
            )
            
            # 메타데이터 생성
            meta_content = self._generate_ideation_metadata(
                result["id"], title, category, priority, doc_path
            )
            
            # 파일 저장
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            doc_path.write_text(doc_content, encoding="utf-8")
            meta_path.write_text(yaml.dump(meta_content), encoding="utf-8")
        
        return result
    
    async def create_epic(
        self,
        ideation_id: str,
        title: str,
        description: str,
        content: str = ""
    ) -> Dict[str, Any]:
        """Epic 생성 및 ideation 자동 연결"""
        # 1. API 호출
        response = await self.client.post(
            "/api/workflow/create_epic",
            json={
                "ideation_id": ideation_id,
                "title": title,
                "description": description,
                "content": content
            }
        )
        result = response.json()
        
        # 2. Epic 문서 생성
        if result["success"]:
            epic_doc_path = Path(result["file_path"])
            epic_meta_path = epic_doc_path.with_suffix(".meta.yaml")
            
            # ideation 정보 조회
            ideation_meta = self._read_metadata(ideation_id)
            ideation_doc_path = Path(ideation_meta["file_path"])
            
            # Epic 문서 생성
            epic_doc = self._generate_epic_document(
                result["epic_id"], ideation_id, title, description, content, ideation_doc_path
            )
            epic_meta = self._generate_epic_metadata(
                result["epic_id"], ideation_id, title, epic_doc_path
            )
            
            epic_doc_path.parent.mkdir(parents=True, exist_ok=True)
            epic_doc_path.write_text(epic_doc, encoding="utf-8")
            epic_meta_path.write_text(yaml.dump(epic_meta), encoding="utf-8")
            
            # 3. ideation 문서 업데이트
            ideation_doc = ideation_doc_path.read_text(encoding="utf-8")
            ideation_doc = self._add_epic_reference(ideation_doc, result["epic_id"])
            ideation_doc_path.write_text(ideation_doc, encoding="utf-8")
            
            # 4. ideation 메타데이터 업데이트
            ideation_meta["epic_id"] = result["epic_id"]
            ideation_meta_path = ideation_doc_path.with_suffix(".meta.yaml")
            ideation_meta_path.write_text(yaml.dump(ideation_meta), encoding="utf-8")
        
        return result
    
    def _generate_ideation_document(
        self, id: str, title: str, description: str, content: str,
        category: str, priority: str
    ) -> str:
        """ideation 문서 템플릿"""
        return f"""# {title}

**ID**: {id}
**상태**: ideation
**우선순위**: {priority}
**카테고리**: {category}
**생성일**: {datetime.now().isoformat()}

## 설명
{description}

{content}
"""
    
    def _add_epic_reference(self, doc_content: str, epic_id: str) -> str:
        """ideation 문서에 Epic 참조 추가"""
        if "**관련 Epic**" not in doc_content:
            # 생성일 다음에 추가
            doc_content = doc_content.replace(
                "**생성일**:",
                f"**관련 Epic**: {epic_id}\n**생성일**:"
            )
        return doc_content
    
    def _read_metadata(self, item_id: str) -> Dict[str, Any]:
        """메타데이터 파일 읽기"""
        # ID로 파일 찾기
        # 실제 구현에서는 DB나 파일 시스템에서 찾기
        pass

# 사용 편의를 위한 함수
async def create_ideation(*args, **kwargs):
    cli = ProjectManagementCLI()
    return await cli.create_ideation(*args, **kwargs)

async def create_epic(*args, **kwargs):
    cli = ProjectManagementCLI()
    return await cli.create_epic(*args, **kwargs)
```

### API 구현 (FastAPI)

**파일**: `tools/project_management/api/routes/workflow.py`

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import sqlite3

router = APIRouter(prefix="/api/workflow", tags=["workflow"])

class CreateIdeationRequest(BaseModel):
    title: str
    description: str
    category: str
    priority: str = "medium"
    content: str = ""

class CreateEpicRequest(BaseModel):
    ideation_id: str
    title: str
    description: str
    content: str = ""

@router.post("/create_ideation")
async def create_ideation(request: CreateIdeationRequest):
    """ideation 생성 API"""
    # 1. ID 생성
    ideation_id = generate_ideation_id(request.category, request.title)
    
    # 2. 파일 경로 결정
    file_path = f"docs/ideation/{request.category}/{sanitize_title(request.title)}.md"
    meta_path = file_path.replace(".md", ".meta.yaml")
    
    # 3. 데이터베이스에 저장
    db = get_db()
    db.execute("""
        INSERT INTO workflow_items (id, type, title, status, file_path, metadata)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        ideation_id,
        "ideation",
        request.title,
        "ideation",
        file_path,
        json.dumps({
            "category": request.category,
            "priority": request.priority,
            "epic_id": None
        })
    ))
    db.commit()
    
    return {
        "success": True,
        "id": ideation_id,
        "file_path": file_path,
        "meta_path": meta_path
    }

@router.post("/create_epic")
async def create_epic(request: CreateEpicRequest):
    """Epic 생성 및 ideation 자동 연결"""
    # 1. Epic ID 생성
    epic_id = generate_epic_id()
    
    # 2. ideation 존재 확인
    db = get_db()
    ideation = db.execute(
        "SELECT * FROM workflow_items WHERE id = ?", (request.ideation_id,)
    ).fetchone()
    
    if not ideation:
        raise HTTPException(404, "Ideation not found")
    
    # 3. Epic 저장
    epic_file_path = f"docs/project-management/epics/{epic_id}.md"
    db.execute("""
        INSERT INTO workflow_items (id, type, title, status, file_path, metadata)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        epic_id,
        "epic",
        request.title,
        "epic",
        epic_file_path,
        json.dumps({
            "epic_id": epic_id,
            "ideation_id": request.ideation_id,
            "tasks": []
        })
    ))
    
    # 4. ideation 업데이트
    ideation_meta = json.loads(ideation["metadata"])
    ideation_meta["epic_id"] = epic_id
    db.execute("""
        UPDATE workflow_items
        SET metadata = ?
        WHERE id = ?
    """, (json.dumps(ideation_meta), request.ideation_id))
    
    db.commit()
    
    return {
        "success": True,
        "epic_id": epic_id,
        "ideation_id": request.ideation_id,
        "file_path": epic_file_path,
        "ideation_updated": True
    }
```

---

## 사용 예시

### 전체 워크플로우

**1. 사용자가 Cursor에서 요청**:
```
"ObjectInteractionHandlerBase 리팩토링해주세요"
```

**2. 에이전트가 도구 사용**:
```python
result = await create_ideation(
    title="ObjectInteractionHandlerBase 리팩토링",
    description="...",
    category="object-interaction",
    priority="high",
    content="상세 내용..."
)
```

**3. 시스템이 자동 처리**:
- 문서 생성
- 메타데이터 생성
- DB 등록
- 대시보드 표시

**4. 사용자가 "Epic으로 만들어주세요" 요청**

**5. 에이전트가 도구 사용**:
```python
result = await create_epic(
    ideation_id="ideation-object-interaction-handler-refactoring",  # ID만 참조
    title="...",
    description="...",
    content="..."
)
```

**6. 시스템이 자동 처리**:
- Epic 문서 생성
- ideation 문서 업데이트 (Epic ID 추가)
- 양방향 연결 설정
- 대시보드 업데이트

---

## 핵심 해결 사항

✅ **문서는 문서대로**: Markdown 파일로 상세한 내용 작성  
✅ **정해진 폴더**: 각 상태별로 정해진 위치에 저장  
✅ **연결고리 자동화**: 에이전트는 ID만 참조, 시스템이 자동 연결  
✅ **자동화된 개발**: 도구 사용으로 일관성 보장  
✅ **메타데이터 분리**: 문서는 읽기 쉽게, 메타데이터는 시스템이 관리

이제 모든 문제가 해결되었습니다!
