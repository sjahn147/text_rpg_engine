---
id: EPIC-001-object-interaction-enhancement
type: epic
status: epic
ideation_ids:
  - ideation-object-interaction-problem-definition
  - ideation-object-interaction-current-status
  - ideation-object-interaction-solution-methodology
  - ideation-object-interaction-enhancement-plan
tasks:
  - TASK-001-action-generation-logic
  - TASK-002-state-based-action-filtering
  - TASK-003-handler-methods-completion
  - TASK-004-timesystem-integration
  - TASK-005-effect-system-integration
  - TASK-006-error-handling-enhancement
keyword: object-interaction-enhancement
created_at: 2026-01-01T16:00:00Z
updated_at: 2026-01-01T16:00:00Z
author: agent
---

# 오브젝트 상호작용 기능 고도화

## 설명

오브젝트 상호작용 시스템의 현재 문제점을 해결하고 기능을 고도화하기 위한 Epic입니다.

## 관련 Ideation

- [문제 정의](../01-problem-definition/ideation-object-interaction-problem-definition.md)
- [현황 진단](../02-current-status/ideation-object-interaction-current-status.md)
- [방법론 검토](../03-methodology/ideation-object-interaction-solution-methodology.md)
- [실행 계획](../04-plan/ideation-object-interaction-enhancement-plan.md)

## 고도화 목표

### 1. 핵심 목표 (대부분 완료)

1. ✅ **모든 오브젝트 상호작용 액션 동적 생성**: `properties.interactions` 기반으로 모든 액션 자동 생성 (완료)
2. ⚠️ **상태 기반 액션 필터링 강화**: 오브젝트의 현재 상태에 따라 가능한 액션만 표시 (부분 구현, 강화 필요)
3. ✅ **완전한 액션 타입 매핑**: 모든 ActionType을 백엔드에서 처리 가능하도록 매핑 (완료)
4. ✅ **프론트엔드 완전 연동**: 모든 액션이 프론트엔드에서 올바르게 표시 및 처리 (완료)

### 2. 부가 목표

1. ✅ **TimeSystem 연동**: 시간 소모가 필요한 상호작용에 TimeSystem 연동 (일부 완료: sleep, eat, drink)
2. ✅ **Effect 시스템 완전 연동**: 모든 상호작용에서 EffectCarrierManager 활용 (일부 완료: eat, drink)
3. ⚠️ **미구현 메서드 완성**: 일부 핸들러의 미구현 메서드 구현 (대부분 완료, 일부 보완 필요)
4. **에러 처리 강화**: 각 단계에서 상세한 에러 로그 및 사용자 피드백

## 고도화 계획

### Phase 1: 기능 보완 (긴급 이슈는 이미 해결됨)

**참고**: 대부분의 긴급 이슈는 이미 해결되었습니다. 이 Phase는 남은 개선 작업을 수행합니다.

#### 1.1 액션 생성 로직 보완
**목표**: 상태 전이 규칙 검증 강화 및 조건부 액션 처리 보완

**작업 내용**:
1. `action_service.py`의 상태 전이 규칙 검증 로직 강화
2. 조건부 액션 처리 보완 (예: `locked` 상태면 `unlock`만 가능)
3. 액션 조건 확인 로직 보완
4. 테스트 및 검증

**예상 작업 시간**: 2-3시간

#### 1.2 상태 기반 액션 필터링 강화
**목표**: 상태 전이 규칙 검증 강화 및 완전 통합

**작업 내용**:
1. 상태 전이 규칙 검증 강화 (예: closed → open만 가능, open → close만 가능)
2. 조건부 액션 처리 보완
3. 액션 생성 로직에 상태 필터링 완전 통합
4. 테스트 및 검증

**예상 작업 시간**: 2-3시간

**Phase 1 총 예상 시간**: 4-6시간

---

### Phase 2: 핸들러 메서드 보완

#### 2.1 핸들러 메서드 확인 및 보완
**목표**: 일부 핸들러의 미구현 메서드 확인 및 구현

**작업 내용**:
1. `recovery.py`: `reduce_fatigue` 메서드 확인 (EntityManager에 피로도 관리 기능 추가 필요)
2. `learning.py`: `handle_study` 메서드 확인 및 보완 (EffectCarrierManager, TimeSystem 연동)
3. `destruction.py`: `handle_dismantle` 메서드 확인 및 보완 (오브젝트 → 컴포넌트 아이템 변환)
4. 각 핸들러의 테스트 및 검증

**예상 작업 시간**: 3-5시간

**Phase 2 총 예상 시간**: 3-5시간

---

### Phase 3: 개선 이슈 (선택사항)

#### 3.1 TimeSystem 연동 확장
**목표**: 시간 소모가 필요한 나머지 상호작용에 TimeSystem 연동

**현재 상태**: ✅ 일부 완료 (sleep, eat, drink)

**작업 내용**:
1. TimeSystem 인터페이스 확인
2. 나머지 핸들러에서 `time_cost` 확인 및 TimeSystem 호출
3. 시간 소모가 필요한 상호작용 목록:
   - ✅ `sleep`: 480분 (완료)
   - ✅ `eat`: 5분 (완료)
   - ✅ `drink`: 2분 (완료)
   - ⚠️ `rest`: 30분 (확인 필요)
   - ⚠️ `read`: 10-30분 (확인 필요)
   - ⚠️ `study`: 60분 (확인 필요)
   - ⚠️ `write`: 15분 (확인 필요)
   - ⚠️ `craft`: 30-120분 (확인 필요)
   - ⚠️ `cook`: 20-60분 (확인 필요)
   - ⚠️ `repair`: 30-60분 (확인 필요)
   - ⚠️ `dismantle`: 15-30분 (확인 필요)

**예상 작업 시간**: 2-3시간

#### 3.2 Effect 시스템 연동 확장
**목표**: 나머지 상호작용에서 EffectCarrierManager 활용

**현재 상태**: ✅ 일부 완료 (eat, drink)

**작업 내용**:
1. 나머지 핸들러에서 `effect_carrier_id` 확인
2. EffectCarrierManager를 통한 효과 적용
3. 효과 적용이 필요한 상호작용:
   - ✅ `eat`: 음식 효과 (완료)
   - ✅ `drink`: 음료 효과 (완료)
   - ⚠️ `read`: 지식/정보 효과 (확인 필요)
   - ⚠️ `study`: 스킬/능력 효과 (확인 필요)
   - ⚠️ `meditate`: 버프 효과 (확인 필요)

**예상 작업 시간**: 1-2시간

#### 3.3 에러 처리 강화
**목표**: 각 단계에서 상세한 에러 로그 및 사용자 피드백

**작업 내용**:
1. 각 핸들러에서 에러 로깅 강화
2. 사용자 친화적인 에러 메시지 제공
3. 디버깅을 위한 상세 로그 추가

**예상 작업 시간**: 2-3시간

**Phase 3 총 예상 시간**: 5-8시간

---

## 전체 예상 작업 시간

| Phase | 예상 시간 |
|-------|----------|
| Phase 1 (기능 보완) | 4-6시간 |
| Phase 2 (핸들러 보완) | 3-5시간 |
| Phase 3 (개선) | 5-8시간 |
| **총계** | **12-19시간** |

**참고**: 대부분의 긴급 및 중요 이슈는 이미 해결되어 예상 작업 시간이 크게 줄어들었습니다.

## 우선순위

1. **우선 (Phase 1)**: 기능 보완 (상태 전이 규칙 검증 강화)
2. **중요 (Phase 2)**: 핸들러 메서드 보완
3. **선택 (Phase 3)**: 개선 및 최적화 (TimeSystem, Effect 시스템 연동 확장)

**참고**: 긴급 이슈는 이미 해결되어 게임 플레이에 문제가 없습니다.

## 구현 상태

- [x] Epic 생성 완료
- [x] Task 분해 완료 (모든 Phase)
- [x] Phase 1 Task 생성 완료
- [x] Phase 2 Task 생성 완료
- [x] Phase 3 Task 생성 완료
- [x] TODO 생성 및 구현 완료
- [x] Phase 1 구현 완료 (TODO-001, TODO-002)
- [x] Phase 3 구현 완료 (TODO-003, TODO-004, TODO-005)
- [ ] 테스트 실행 및 검증
- [ ] 품질 게이트 통과

## 다음 단계

1. **Epic 생성 완료** ✅
2. **Task 분해** → Phase별로 Task 생성
3. **개발 시작** → Task 분해 후 진행

