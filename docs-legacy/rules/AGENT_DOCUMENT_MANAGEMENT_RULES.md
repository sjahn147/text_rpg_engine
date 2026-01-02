# 에이전트 문서 관리 규칙 (최종 버전)

**작성일**: 2026-01-01  
**버전**: 1.0 (최종)  
**목적**: 에이전트가 프로젝트 문서를 효율적으로 관리하기 위한 필수 규칙  
**핵심 원칙**: 규칙 준수 → 자동화 달성

---

## ⚠️ 중요: 이 문서는 필수 읽기

**모든 에이전트는 이 문서의 규칙을 반드시 준수해야 합니다.**

- ❌ 규칙 위반 시 문서 저장 금지
- ✅ 규칙 준수 시 자동으로 문서 관리 가능
- ✅ 기존 문서도 이 규칙에 따라 처리

---

## 📋 목차

1. [디렉토리 구조](#디렉토리-구조)
2. [파일명 규칙](#파일명-규칙)
3. [문서 작성 규칙](#문서-작성-규칙)
4. [상태 전환 규칙](#상태-전환-규칙)
5. [연결고리 설정 규칙](#연결고리-설정-규칙)
6. [기존 문서 처리 규칙](#기존-문서-처리-규칙)
7. [검증 규칙](#검증-규칙)
8. [실제 사용 예시](#실제-사용-예시)

---

## 디렉토리 구조

### 필수 구조

**모든 작업 항목은 다음 구조를 따라야 함:**

```
docs/
├── work-items/                    # 모든 작업 항목 (통합 관리)
│   ├── ideation/                  # 상태: ideation
│   ├── epic/                      # 상태: epic
│   ├── task/                      # 상태: task
│   ├── development/                # 상태: development
│   ├── qa/                        # 상태: qa
│   ├── audit/                     # 상태: audit
│   ├── done/                      # 상태: done
│   └── deprecated/                # 상태: deprecated
│
├── submissions/                   # 에이전트 제출 파일 (YAML만)
│   ├── TODO-{ID}.yaml
│   ├── TRANSITION-{ID}.yaml
│   └── AUDIT-{ID}.yaml
│
├── rules/                         # 개발 규칙 (기존 유지)
├── architecture/                  # 아키텍처 문서 (기존 유지)
└── changelog/                     # 변경 이력 (기존 유지)
```

### 핵심 원칙

1. **상태별 폴더**: `docs/work-items/{status}/`
2. **플랫 구조**: 최대 2단계 깊이
3. **ID 기반 파일명**: 바로 찾기 가능
4. **메타데이터 내장**: YAML frontmatter (별도 파일 불필요)

---

## 파일명 규칙

### 필수 규칙

**에이전트는 다음 파일명 규칙을 반드시 준수해야 함:**

| 타입 | 파일명 형식 | 예시 |
|------|------------|------|
| ideation | `ideation-{category}-{title-slug}.md` | `ideation-action-handler-modularization.md` |
| epic | `EPIC-{번호}.md` | `EPIC-001.md` |
| task | `TASK-{번호}.md` | `TASK-001.md` |
| todo | `TODO-{번호}.md` | `TODO-001.md` |
| qa | `QA-{번호}.md` | `QA-001.md` |
| audit | `AUDIT-{번호}.md` | `AUDIT-001.md` |
| done | `DONE-{원본ID}.md` | `DONE-EPIC-001.md` |
| deprecated | `[deprecated]{원본ID}.md` | `[deprecated]ideation-xxx.md` |

### ID 생성 규칙

**ideation ID**:
- 형식: `ideation-{category}-{title-slug}`
- 예시: `ideation-action-handler-modularization`
- 규칙: 소문자, 하이픈으로 단어 구분

**Epic/Task/TODO ID**:
- 형식: `{TYPE}-{순차번호}`
- 예시: `EPIC-001`, `TASK-001`, `TODO-001`
- 규칙: 순차적 번호 부여 (기존 번호 확인 후 다음 번호 사용)

---

## 문서 작성 규칙

### 규칙 1: 필수 메타데이터 (MUST)

**에이전트는 문서를 작성할 때 반드시 다음 형식을 준수해야 함:**

```markdown
---
id: {unique_id}
type: ideation|epic|task|todo|qa|audit
status: ideation|epic|task|development|qa|audit|done|deprecated
category: {category}  # ideation만 필수
priority: high|medium|low  # ideation만 필수
created_at: {YYYY-MM-DDTHH:MM:SSZ}
updated_at: {YYYY-MM-DDTHH:MM:SSZ}
author: agent|user

# 연결 정보 (있는 경우)
epic_id: {EPIC_ID 또는 null}
ideation_id: {ideation_id 또는 null}
task_id: {TASK_ID 또는 null}
dependencies: []  # task만
todos: []  # task만
tasks: []  # epic만
---

# {제목}

## 설명
{내용}

## 구현 상태
- [ ] 구현 전
- [x] 구현 완료
- [ ] 부분 구현
- [ ] Deprecated

## 관련 문서
- [{관련 문서 제목}](../{status}/{파일명}.md)
```

### 필수 체크리스트

**문서 저장 전 반드시 확인:**

- [ ] YAML frontmatter가 있는가?
- [ ] `id` 필드가 있는가?
- [ ] `type` 필드가 있는가?
- [ ] `status` 필드가 있는가?
- [ ] `created_at` 필드가 있는가?
- [ ] `updated_at` 필드가 있는가?
- [ ] ideation인 경우 `category`와 `priority`가 있는가?
- [ ] 연결 정보가 있으면 명시되어 있는가?

**❌ 위 항목 중 하나라도 없으면 문서 저장 금지**

---

## 상태 전환 규칙

### 규칙 2: 상태 전환 시 필수 작업

**에이전트는 상태를 변경할 때 반드시 다음을 수행해야 함:**

#### 2.1 ideation → epic 전환

**필수 작업**:
1. Epic 문서 생성: `docs/work-items/epic/EPIC-{번호}.md`
2. Epic 문서에 `ideation_id` 명시
3. **원본 ideation 문서 업데이트** (반드시):
   - `status: epic` 변경
   - `epic_id: EPIC-{번호}` 추가
   - `updated_at: {오늘 날짜}` 업데이트
4. **파일 이동**: `docs/work-items/ideation/` → `docs/work-items/epic/` (선택사항, 또는 상태만 변경)

**프롬프트 규칙**:
```
ideation을 epic으로 전환할 때:
1. Epic 문서를 생성한다 (docs/work-items/epic/EPIC-{번호}.md)
2. Epic 문서에 ideation_id를 명시한다
3. 반드시 원본 ideation 문서를 찾아서 업데이트한다:
   - status를 epic으로 변경
   - epic_id 추가
   - updated_at 업데이트
4. 두 문서 모두 저장한다
5. 한쪽만 업데이트하는 것은 금지한다
```

#### 2.2 epic → task 전환

**필수 작업**:
1. Task 문서 생성: `docs/work-items/task/TASK-{번호}.md`
2. Task 문서에 `epic_id` 명시
3. **원본 epic 문서 업데이트** (반드시):
   - `tasks: [TASK-{번호}]` 추가
   - `updated_at: {오늘 날짜}` 업데이트

**프롬프트 규칙**:
```
epic을 task로 전환할 때:
1. Task 문서를 생성한다 (docs/work-items/task/TASK-{번호}.md)
2. Task 문서에 epic_id를 명시한다
3. 반드시 원본 epic 문서를 찾아서 업데이트한다:
   - tasks 배열에 TASK ID 추가
   - updated_at 업데이트
4. 두 문서 모두 저장한다
```

#### 2.3 development → qa 전환

**필수 작업**:
1. TODO 제출 YAML 생성: `docs/submissions/TODO-{ID}.yaml`
2. QA 문서 생성: `docs/work-items/qa/QA-{번호}.md`
3. **원본 TODO 문서 업데이트** (반드시):
   - `status: qa` 변경
   - `qa_id: QA-{번호}` 추가
   - `updated_at` 업데이트

#### 2.4 qa → audit 전환

**필수 작업**:
1. Audit 문서 생성: `docs/work-items/audit/AUDIT-{번호}.md`
2. Audit 제출 YAML 생성: `docs/submissions/AUDIT-{ID}.yaml`
3. **원본 QA 문서 업데이트** (반드시):
   - `status: audit` 변경
   - `audit_id: AUDIT-{번호}` 추가
   - `updated_at` 업데이트

#### 2.5 done → deprecated 전환

**필수 작업**:
1. 문서 내용 확인 (구현 완료 여부)
2. `status: deprecated` 변경
3. `deprecated_at: {날짜}` 추가
4. `deprecated_reason: {사유}` 추가
5. 파일명에 `[deprecated]` 접두어 추가
6. `docs/work-items/deprecated/`로 이동
7. 원본 위치의 문서 삭제

**프롬프트 규칙**:
```
구현이 완료되어 문서를 deprecated 처리할 때:
1. 문서 상태를 deprecated로 변경한다
2. Deprecated 사유를 명시한다 (deprecated_reason)
3. 파일명에 [deprecated] 접두어를 추가한다
4. docs/work-items/deprecated/ 폴더로 이동한다
5. 원본 위치의 문서는 삭제한다
```

---

## 연결고리 설정 규칙

### 규칙 3: 양방향 연결 필수 (MUST)

**에이전트는 문서를 참조할 때 반드시 양방향 연결을 설정해야 함:**

#### 3.1 Epic 생성 시

**필수 작업**:
1. Epic 문서 작성
2. Epic 문서에 `ideation_id: ideation-{id}` 명시
3. **원본 ideation 문서 찾아서 업데이트** (반드시):
   - `epic_id: EPIC-{번호}` 추가
   - `updated_at: {오늘 날짜}` 업데이트

**프롬프트 규칙**:
```
Epic을 생성할 때:
1. Epic 문서에 ideation_id를 명시한다
2. 반드시 원본 ideation 문서를 찾아서 업데이트한다:
   - epic_id 추가
   - updated_at 업데이트
3. 한쪽만 연결하는 것은 금지한다
4. ideation 문서를 찾지 못하면 에러를 발생시킨다
```

#### 3.2 Task 생성 시

**필수 작업**:
1. Task 문서 작성
2. Task 문서에 `epic_id: EPIC-{번호}` 명시
3. **원본 epic 문서 찾아서 업데이트** (반드시):
   - `tasks: [TASK-{번호}]` 추가
   - `updated_at: {오늘 날짜}` 업데이트

**프롬프트 규칙**:
```
Task를 생성할 때:
1. Task 문서에 epic_id를 명시한다
2. 반드시 원본 epic 문서를 찾아서 업데이트한다:
   - tasks 배열에 TASK ID 추가
   - updated_at 업데이트
3. 한쪽만 연결하는 것은 금지한다
4. epic 문서를 찾지 못하면 에러를 발생시킨다
```

#### 3.3 의존성 설정 (Task → Task)

**필수 작업**:
1. Task 문서에 `dependencies: [TASK-{번호}]` 명시
2. **의존성 Task 문서 찾아서 업데이트** (선택사항, 권장):
   - `dependents: [TASK-{번호}]` 추가 (없으면 생성)
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
   - 상태 추론 (내용 분석)
   - 카테고리 추론 (폴더 구조 또는 파일명)
   - 우선순위 추론 (내용 분석)
   - ID 생성 (파일명 또는 규칙에 따라)
4. 문서 업데이트

**프롬프트 규칙**:
```
기존 문서를 처리할 때:
1. 문서를 읽는다
2. YAML frontmatter가 있는지 확인한다
3. 없으면 반드시 추가한다:
   - id: 파일명에서 추출하거나 생성
   - type: 문서 내용 분석하여 추론
   - status: 문서 내용 분석하여 추론
   - category: 폴더 구조 또는 파일명에서 추론
   - priority: 내용 분석하여 추론 (high/medium/low)
   - created_at: 파일 생성일 또는 문서 내 날짜
   - updated_at: 파일 수정일 또는 오늘 날짜
4. 문서를 업데이트한다
```

#### 4.2 구현 완료 문서 감지

**필수 작업**:
1. 문서 내용 분석
2. "구현 완료", "완성", "완료", "✅" 등의 키워드 확인
3. 실제 코드베이스 확인 (가능한 경우)
4. 완료 확인되면:
   - `status: done` 변경
   - 또는 `status: deprecated` 변경 (모든 관련 작업 완료 시)

**프롬프트 규칙**:
```
문서를 읽을 때:
1. "구현 완료", "완성", "완료", "✅" 등의 키워드를 확인한다
2. 실제 코드베이스에서 구현 여부를 확인한다 (가능한 경우)
3. 완료 확인되면:
   - status를 done으로 변경
   - 또는 deprecated 처리 (모든 관련 작업 완료 시)
4. 문서를 업데이트한다
```

#### 4.3 기존 문서 위치 마이그레이션

**기존 위치**:
- `docs/ideation/{category}/{TITLE}.md`
- `docs/project-management/epics/{EPIC_ID}.md`
- `docs/project-management/tasks/{TASK_ID}.md`

**새 위치**:
- `docs/work-items/ideation/ideation-{category}-{title-slug}.md`
- `docs/work-items/epic/EPIC-{번호}.md`
- `docs/work-items/task/TASK-{번호}.md`

**마이그레이션 규칙**:
```
기존 문서를 새 구조로 마이그레이션할 때:
1. 문서를 읽는다
2. 메타데이터를 추가한다 (없는 경우)
3. 새 위치로 이동한다
4. 파일명을 새 규칙에 맞게 변경한다
5. 원본 문서는 삭제한다 (또는 백업)
```

---

## 검증 규칙

### 규칙 5: 저장 전 필수 검증

**에이전트는 문서를 저장하기 전에 반드시 다음을 확인해야 함:**

#### 5.1 메타데이터 검증

**체크리스트**:
- [ ] YAML frontmatter가 있는가?
- [ ] `id` 필드가 있고 유효한가?
- [ ] `type` 필드가 있고 유효한가? (ideation|epic|task|todo|qa|audit)
- [ ] `status` 필드가 있고 유효한가?
- [ ] `created_at` 필드가 있고 ISO 형식인가?
- [ ] `updated_at` 필드가 있고 ISO 형식인가?
- [ ] ideation인 경우 `category`와 `priority`가 있는가?

**❌ 하나라도 없으면 저장 금지**

#### 5.2 연결 정보 일관성 검증

**체크리스트**:
- [ ] Epic 문서에 `ideation_id`가 있으면, 해당 ideation 문서에도 `epic_id`가 있는가?
- [ ] Task 문서에 `epic_id`가 있으면, 해당 epic 문서의 `tasks` 배열에 포함되어 있는가?
- [ ] 양방향 연결이 되어 있는가?

**❌ 일관성이 없으면 저장 금지**

#### 5.3 상태 전환 검증

**체크리스트**:
- [ ] 상태를 변경했으면 원본 문서도 업데이트했는가?
- [ ] `updated_at`을 업데이트했는가?
- [ ] 파일이 올바른 폴더에 있는가?

**❌ 검증 실패 시 저장 금지**

#### 5.4 파일명 검증

**체크리스트**:
- [ ] 파일명이 규칙에 맞는가?
- [ ] ID가 파일명에 포함되어 있는가?
- [ ] deprecated인 경우 `[deprecated]` 접두어가 있는가?

**❌ 파일명 규칙 위반 시 저장 금지**

---

## 실제 사용 예시

### 예시 1: 새 ideation 문서 작성

**사용자 요청**:
```
"ObjectInteractionHandlerBase 리팩토링해주세요"
```

**에이전트가 해야 할 일**:

1. **ID 생성**: `ideation-object-interaction-handler-refactoring`
2. **파일 경로**: `docs/work-items/ideation/ideation-object-interaction-handler-refactoring.md`
3. **문서 작성**:
```markdown
---
id: ideation-object-interaction-handler-refactoring
type: ideation
status: ideation
category: object-interaction
priority: high
created_at: 2026-01-01T12:00:00Z
updated_at: 2026-01-01T12:00:00Z
author: agent
epic_id: null
---

# ObjectInteractionHandlerBase 리팩토링

## 설명
ObjectInteractionHandlerBase 클래스를 모듈화하고 개선합니다.

## 구현 상태
- [ ] 구현 전

## 관련 문서
- 없음
```

4. **검증**: 메타데이터 체크리스트 확인
5. **저장**: 파일 저장

---

### 예시 2: Epic 생성 및 연결

**사용자 요청**:
```
"이 ideation을 Epic으로 만들어주세요"
```

**에이전트가 해야 할 일**:

1. **원본 ideation 문서 읽기**:
   - `docs/work-items/ideation/ideation-object-interaction-handler-refactoring.md`
   - ID 확인: `ideation-object-interaction-handler-refactoring`

2. **Epic ID 생성**: `EPIC-001` (기존 Epic 확인 후 다음 번호)

3. **Epic 문서 생성**:
   - 파일: `docs/work-items/epic/EPIC-001.md`
   - 내용:
```markdown
---
id: EPIC-001
type: epic
status: epic
ideation_id: ideation-object-interaction-handler-refactoring
created_at: 2026-01-01T13:00:00Z
updated_at: 2026-01-01T13:00:00Z
author: agent
tasks: []
---

# ObjectInteractionHandlerBase 리팩토링

**관련 Ideation**: [ideation-object-interaction-handler-refactoring](../ideation/ideation-object-interaction-handler-refactoring.md)

## 설명
ObjectInteractionHandlerBase 클래스를 모듈화하고 개선합니다.

## 작업 목록
- (아직 없음)
```

4. **원본 ideation 문서 업데이트** (반드시):
```markdown
---
id: ideation-object-interaction-handler-refactoring
type: ideation
status: ideation
category: object-interaction
priority: high
created_at: 2026-01-01T12:00:00Z
updated_at: 2026-01-01T13:00:00Z  <!-- 업데이트 -->
author: agent
epic_id: EPIC-001  <!-- 추가 -->
---

# ObjectInteractionHandlerBase 리팩토링

**관련 Epic**: [EPIC-001](../epic/EPIC-001.md)  <!-- 추가 -->

## 설명
...
```

5. **검증**: 양방향 연결 확인
6. **저장**: 두 문서 모두 저장

---

### 예시 3: 기존 문서 마이그레이션

**기존 문서**:
- 위치: `docs/ideation/action-handler/ACTION_HANDLER_MODULARIZATION_PROPOSAL.md`
- 내용: 메타데이터 없음

**에이전트가 해야 할 일**:

1. **문서 읽기**
2. **메타데이터 추가**:
   - `id`: `ideation-action-handler-modularization` (파일명에서 추출)
   - `type`: `ideation` (내용 분석)
   - `status`: `done` (내용에 "모듈화 완료" 확인)
   - `category`: `action-handler` (폴더 구조에서 추론)
   - `priority`: `high` (내용 분석)

3. **문서 업데이트**:
```markdown
---
id: ideation-action-handler-modularization
type: ideation
status: done
category: action-handler
priority: high
created_at: 2025-12-28T00:00:00Z
updated_at: 2026-01-01T14:00:00Z
author: agent
epic_id: null
---

# ActionHandler 모듈화 제안

## 설명
...
```

4. **새 위치로 이동**:
   - `docs/work-items/ideation/ideation-action-handler-modularization.md`
   - 원본 삭제 (또는 백업)

---

### 예시 4: Deprecated 처리

**완료된 Epic 문서**:
- 위치: `docs/work-items/epic/EPIC-001.md`
- 상태: 모든 관련 Task, TODO가 done

**에이전트가 해야 할 일**:

1. **문서 읽기 및 확인**
2. **문서 업데이트**:
```markdown
---
id: EPIC-001
type: epic
status: deprecated
ideation_id: ideation-object-interaction-handler-refactoring
created_at: 2026-01-01T13:00:00Z
updated_at: 2026-01-01T16:00:00Z
deprecated_at: 2026-01-01T16:00:00Z
deprecated_reason: "구현 완료 - 모든 Epic, Task, TODO가 done 상태"
author: agent
tasks: [TASK-001, TASK-002]
---

# ObjectInteractionHandlerBase 리팩토링 (Deprecated)

**Deprecated 사유**: 구현 완료 - 모든 Epic, Task, TODO가 done 상태

## 원본 내용
...
```

3. **파일명 변경**: `[deprecated]EPIC-001.md`
4. **파일 이동**: `docs/work-items/deprecated/[deprecated]EPIC-001.md`
5. **원본 삭제**: `docs/work-items/epic/EPIC-001.md` 삭제

---

## 핵심 원칙 요약

### 반드시 준수해야 할 규칙 (MUST)

1. ✅ **메타데이터 필수**: YAML frontmatter 반드시 포함
2. ✅ **양방향 연결**: 한쪽만 연결 금지
3. ✅ **상태 전환 시 원본 업데이트**: 반드시 원본 문서도 업데이트
4. ✅ **파일명 규칙 준수**: ID 기반 파일명 사용
5. ✅ **저장 전 검증**: 모든 체크리스트 확인

### 금지 사항 (DO NOT)

1. ❌ 메타데이터 없이 문서 작성 금지
2. ❌ 한쪽만 연결 금지
3. ❌ 상태 전환 시 원본 미업데이트 금지
4. ❌ 파일명 규칙 위반 금지
5. ❌ 검증 없이 저장 금지

---

## 디렉토리 구조 참고

### 전체 구조

```
docs/
├── work-items/                    # 모든 작업 항목
│   ├── ideation/                  # ideation-{category}-{title-slug}.md
│   ├── epic/                      # EPIC-{번호}.md
│   ├── task/                      # TASK-{번호}.md
│   ├── development/               # TODO-{번호}.md
│   ├── qa/                        # QA-{번호}.md
│   ├── audit/                     # AUDIT-{번호}.md
│   ├── done/                      # DONE-{원본ID}.md
│   └── deprecated/                # [deprecated]{원본ID}.md
│
├── submissions/                   # 제출 파일 (YAML만)
│   ├── TODO-{ID}.yaml
│   ├── TRANSITION-{ID}.yaml
│   └── AUDIT-{ID}.yaml
│
├── rules/                         # 개발 규칙
├── architecture/                  # 아키텍처 문서
└── changelog/                     # 변경 이력
```

### 상대 경로 참조

**연결 문서 참조 시**:
- ideation → epic: `../epic/EPIC-001.md`
- epic → ideation: `../ideation/ideation-xxx.md`
- task → epic: `../epic/EPIC-001.md`
- epic → task: `../task/TASK-001.md`

---

## 작업 체크리스트

### 문서 작성 시

- [ ] 올바른 폴더에 저장하는가? (`docs/work-items/{status}/`)
- [ ] 파일명이 규칙에 맞는가?
- [ ] YAML frontmatter가 있는가?
- [ ] 모든 필수 메타데이터가 있는가?
- [ ] 연결 정보가 있으면 명시했는가?

### 상태 전환 시

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

**모든 체크리스트 통과 시에만 저장**

---

## 결론

**이 규칙을 준수하면:**

1. ✅ 모든 문서가 일관된 형식
2. ✅ 문서 간 연결고리 자동 설정
3. ✅ 상태 추적 가능
4. ✅ 대시보드에서 조회 가능
5. ✅ 자동화된 문서 관리

**핵심**: 에이전트가 이 규칙을 **반드시 준수**하도록 프롬프트에 명시

---

## 부록: 빠른 참조

### 파일명 규칙
- ideation: `ideation-{category}-{title-slug}.md`
- epic: `EPIC-{번호}.md`
- task: `TASK-{번호}.md`
- todo: `TODO-{번호}.md`
- deprecated: `[deprecated]{원본ID}.md`

### 필수 메타데이터
- `id`, `type`, `status`, `created_at`, `updated_at`
- ideation: `category`, `priority` 추가
- 연결 정보: `epic_id`, `ideation_id`, `task_id`

### 상태 전환 체크리스트
1. 새 문서 생성
2. 원본 문서 찾기
3. 원본 문서 업데이트
4. 양방향 연결 설정
5. 검증 후 저장

