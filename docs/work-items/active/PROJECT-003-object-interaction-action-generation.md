---
id: PROJECT-003
title: 오브젝트 상호작용 액션 생성 개선
status: active
category: backend-core
priority: high
created_at: 2026-01-03T13:00:00Z
updated_at: 2026-01-03T13:00:00Z
author: agent
---

# 오브젝트 상호작용 액션 생성 개선

## 개요

오브젝트 상호작용 시 모든 가능한 액션(20개)이 동적으로 생성되도록 개선합니다. 현재는 `interaction_type`에 따라 제한적으로만 액션을 생성하고 있어, 오브젝트 조회 시 모든 액션이 나타나지 않는 문제를 해결합니다.

## 진행 상황

### 단계별 진행 상황
- [x] 문제 정의
- [x] 현황 진단
- [ ] 방법론 검토
- [ ] 실행 계획 수립
- [ ] 개발 시작
- [ ] 테스트
- [ ] QA
- [ ] 문서화
- [ ] 완료

### 작업 목록

#### Phase 1: 액션 생성 로직 개선 (우선순위: 높음) ✅ 완료
- [x] `properties.interactions` JSONB 필드를 확인하여 동적으로 액션 생성
- [x] `_generate_actions_from_interaction_type` 메서드 추가
- [x] `possible_states`를 기반으로 동적 액션 생성 로직 구현
- [x] 상태 전이 기반 액션 생성 (closed/open, unlit/lit, locked/unlocked 등)
- [x] `interaction_type` 기반 fallback 액션 생성
- [x] `properties.contents` 기반 pickup 액션 생성

#### Phase 2: 액션 타입 매핑 확장 (우선순위: 높음) ✅ 완료
- [x] `action_type_map`에 모든 ActionType 추가 확인 (이미 완료됨)
- [x] 각 ActionType에 대한 Handler 연결 확인 (이미 완료됨)

#### Phase 3: EntityManager 피로도 관리 추가 (우선순위: 중간)
- [ ] `EntityManager`에 `reduce_fatigue` 메서드 추가
- [ ] 피로도 시스템 구현

## 작업 이력

### 2026-01-03
- 13:00: 프로젝트 시작
- 13:00: 문제 정의 및 현황 진단 완료
  - `docs/ideation/object-interaction/IMPLEMENTATION_TODOS.md` 검토 완료
  - `docs/ideation/action-handler/ACTION_HANDLER_IMPLEMENTATION_STATUS.md` 검토 완료
  - 현재 문제점 확인:
    1. `action_service.py`에서 제한적으로만 액션 생성 (openable, lightable, restable, sitable만 처리)
    2. `interaction_service.py`의 `action_type_map`에 일부 액션만 매핑 (9개만 매핑)
    3. `EntityManager`에 `reduce_fatigue` 메서드 없음

## 관련 문서
- [Action Handler 가이드라인](../../rules/00_CORE/03_ACTION_HANDLER_GUIDELINES.md)
- [개발 워크플로우 가이드](../../rules/04_DEVELOPMENT/DEVELOPMENT_WORKFLOW_GUIDE.md)
- [구현 TODO](../../../ideation/object-interaction/IMPLEMENTATION_TODOS.md)
- [Action Handler 구현 상태](../../../ideation/action-handler/ACTION_HANDLER_IMPLEMENTATION_STATUS.md)

## 참고 사항
- `app/services/gameplay/action_service.py` 파일 수정 필요
- `app/services/gameplay/interaction_service.py` 파일 수정 필요
- `app/managers/entity_manager.py`에 피로도 관리 기능 추가 필요
- 모든 액션은 `00_CORE/03_ACTION_HANDLER_GUIDELINES.md`의 ActionType 정의를 따라야 합니다.

