---
id: TODO-002-state-filtering-integration
type: todo
status: development
sub_status: implement_green
task_id: TASK-002-state-based-action-filtering
file: app/services/gameplay/action_service.py
line: 322
code_snippet: |
  # interactions에 정의된 모든 액션 생성
  for action_type, action_config in interactions.items():
      if not isinstance(action_config, dict):
          continue
      
      # 액션 가능 여부 확인 (강화된 검증 로직 사용)
      can_perform = self._check_action_conditions(
          action_config=action_config,
          current_state=current_state or '',
          possible_states=possible_states or []
      )
keyword: state-filtering-integration
created_at: 2026-01-01T17:10:00Z
updated_at: 2026-01-01T17:10:00Z
author: agent
---

# 상태 기반 액션 필터링 완전 통합

## 설명

액션 생성 로직에 상태 필터링을 완전 통합하여 상태 전이 규칙 검증을 강화합니다.

## 작업 내용

### 1. 상태 전이 규칙 검증 강화

**현재 상태**: TODO-001에서 `_check_action_conditions` 메서드가 추가되었지만, 실제 액션 생성 로직과의 통합이 완전하지 않음

**개선 방안**:
1. `possible_states` 배열을 활용한 자동 상태 전이 규칙 생성
2. 상태 전이 방향성 검증 강화
3. 상태별 허용/금지 액션 목록 검증 통합

### 2. 조건부 액션 처리 보완

**개선 방안**:
1. `locked` 상태에서 `unlock`만 가능하도록 하는 로직 강화
2. 상태별 특수 조건 처리 (예: `closed` → `open`만 가능, 역방향 불가)

### 3. 액션 생성 로직에 상태 필터링 완전 통합

**개선 방안**:
1. 모든 액션 생성 경로에서 상태 필터링 적용
2. 레거시 `interaction_type` 기반 액션 생성에도 상태 필터링 적용

## 구현 계획

### Step 1: 레거시 interaction_type 기반 액션에도 상태 필터링 적용

현재 `interaction_type` 기반 액션 생성(367-424줄)에는 상태 필터링이 없음. 이를 추가해야 함.

### Step 2: 상태 전이 규칙 검증 로직 개선

`_can_transition_state` 메서드의 인접 상태 전이 로직을 개선하여 더 정확한 상태 전이 검증

## 테스트 계획

1. **상태 전이 규칙 검증 테스트**
   - `closed` → `open` 전이 가능 확인
   - `open` → `closed` 전이 가능 확인
   - `closed` → `locked` 전이 불가능 확인

2. **조건부 액션 처리 테스트**
   - `locked` 상태에서 `unlock`만 가능 확인
   - `locked` 상태에서 `open` 불가능 확인

3. **레거시 interaction_type 테스트**
   - `openable` 타입 오브젝트에서 상태 필터링 작동 확인

## 관련 파일

- `app/services/gameplay/action_service.py` (322-424줄)

## 관련 Task

- [TASK-002-state-based-action-filtering](../06-task/TASK-002-state-based-action-filtering.md)

## 구현 상태

- [x] 요구사항 분석 완료 ✅
- [x] 테스트 작성 (test_red) ✅
- [x] 구현 (implement_green) ✅
- [x] 리팩토링 (refactor) ✅
- [ ] 품질 게이트 통과 (quality_gate)

