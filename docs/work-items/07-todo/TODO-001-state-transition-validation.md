---
id: TODO-001-state-transition-validation
type: todo
status: development
sub_status: implement_green
task_id: TASK-001-action-generation-logic
file: app/services/gameplay/action_service.py
line: 338
code_snippet: |
  # possible_states 기반 상태 전이 확인
  if possible_states and current_state:
      # 상태 전이 규칙 확인 (예: closed -> open만 가능)
      state_transitions = action_config.get('state_transitions', {})
      if state_transitions:
          # 현재 상태에서 이 액션으로 전이 가능한지 확인
          if current_state not in state_transitions:
              can_perform = False
keyword: state-transition-validation
created_at: 2026-01-01T16:30:00Z
updated_at: 2026-01-01T16:30:00Z
author: agent
---

# 상태 전이 규칙 검증 강화

## 설명

`action_service.py`의 상태 전이 규칙 검증 로직을 강화하여 오브젝트의 현재 상태에 따라 가능한 액션만 표시하도록 개선합니다.

## 작업 내용

### 1. 상태 전이 규칙 검증 로직 강화

**현재 코드 위치**: `app/services/gameplay/action_service.py` (338-348줄)

**문제점**:
- `state_transitions`가 `action_config`에 있을 때만 검증
- `possible_states`와 `current_state`를 활용한 전이 가능 여부 검증이 불완전
- 상태 전이 규칙이 명시적으로 정의되지 않은 경우 처리 부족

**개선 방안**:
1. `possible_states` 배열을 활용한 상태 전이 가능 여부 검증
   - 예: `possible_states: ['closed', 'open']`이고 현재 상태가 `closed`면 `open` 액션만 가능
   - 예: `possible_states: ['closed', 'open']`이고 현재 상태가 `open`이면 `close` 액션만 가능
2. `state_transitions`가 없는 경우 `possible_states` 기반으로 자동 전이 규칙 생성
3. 상태 전이 방향성 검증 (예: `closed` → `open`만 가능, 역방향 불가)

### 2. 조건부 액션 처리 보완

**문제점**:
- `locked` 상태에서 `unlock`만 가능하도록 하는 로직이 불완전
- 특정 상태에서 특정 액션만 가능하도록 하는 조건 처리 부족

**개선 방안**:
1. `required_state`와 `forbidden_states` 검증 강화
2. 상태별 허용 액션 목록 정의 및 검증
3. 상태 전이 불가능한 액션 필터링

### 3. 액션 조건 확인 로직 보완

**개선 방안**:
1. 액션 조건 확인 로직을 별도 함수로 분리
2. 조건 확인 실패 시 상세한 로그 기록
3. 조건 확인 결과를 액션 메타데이터에 포함

## 구현 계획

### Step 1: 상태 전이 규칙 검증 함수 추가

```python
def _can_transition_state(
    self,
    current_state: str,
    target_state: str,
    possible_states: List[str],
    state_transitions: Optional[Dict[str, List[str]]] = None
) -> bool:
    """
    상태 전이가 가능한지 확인
    
    Args:
        current_state: 현재 상태
        target_state: 목표 상태
        possible_states: 가능한 상태 목록
        state_transitions: 명시적 상태 전이 규칙 (선택사항)
    
    Returns:
        bool: 전이 가능 여부
    """
    # 명시적 전이 규칙이 있으면 우선 사용
    if state_transitions:
        allowed_transitions = state_transitions.get(current_state, [])
        return target_state in allowed_transitions
    
    # possible_states 기반 자동 전이 규칙
    if current_state in possible_states and target_state in possible_states:
        # 인접 상태로만 전이 가능 (순서 기반)
        current_idx = possible_states.index(current_state)
        target_idx = possible_states.index(target_state)
        # 인접 상태만 허용 (차이가 1 이하)
        return abs(current_idx - target_idx) <= 1
    
    return False
```

### Step 2: 액션 생성 로직에 상태 전이 검증 통합

```python
# interactions에 정의된 모든 액션 생성
for action_type, action_config in interactions.items():
    # ... 기존 코드 ...
    
    # 상태 전이 규칙 확인 강화
    target_state = action_config.get('target_state')
    if target_state and possible_states:
        can_transition = self._can_transition_state(
            current_state=current_state,
            target_state=target_state,
            possible_states=possible_states,
            state_transitions=action_config.get('state_transitions')
        )
        if not can_transition:
            can_perform = False
```

### Step 3: 조건부 액션 처리 보완

```python
# 상태별 허용 액션 목록 확인
allowed_actions_in_state = action_config.get('allowed_in_states', [])
if allowed_actions_in_state and current_state not in allowed_actions_in_state:
    can_perform = False

# 상태별 금지 액션 목록 확인
forbidden_actions_in_state = action_config.get('forbidden_in_states', [])
if forbidden_actions_in_state and current_state in forbidden_actions_in_state:
    can_perform = False
```

## 테스트 계획

1. **상태 전이 규칙 검증 테스트**
   - `closed` → `open` 전이 가능 확인
   - `open` → `closed` 전이 가능 확인
   - `closed` → `locked` 전이 불가능 확인

2. **조건부 액션 처리 테스트**
   - `locked` 상태에서 `unlock`만 가능 확인
   - `locked` 상태에서 `open` 불가능 확인

3. **통합 테스트**
   - 다양한 상태 조합에서 액션 생성 정확성 확인
   - 상태 전이 불가능한 액션 필터링 확인

## 관련 파일

- `app/services/gameplay/action_service.py` (338-348줄)

## 관련 Task

- [TASK-001-action-generation-logic](../06-task/TASK-001-action-generation-logic.md)

## 테스트 파일

- `tests/active/integration/test_action_service_state_transition.py`

## 구현 상태

- [x] 요구사항 분석 완료 ✅
- [x] 테스트 작성 (test_red) ✅
- [x] 구현 (implement_green) ✅
- [x] 리팩토링 (refactor) ✅
- [ ] 품질 게이트 통과 (quality_gate)

