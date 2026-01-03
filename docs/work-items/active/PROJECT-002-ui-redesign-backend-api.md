---
id: PROJECT-002
title: UI 리디자인 백엔드 API 구현
status: active
category: backend-api
priority: high
created_at: 2026-01-03T13:00:00Z
updated_at: 2026-01-03T13:00:00Z
author: agent
---

# UI 리디자인 백엔드 API 구현

## 개요

BG3 스타일 UI 리디자인을 위한 백엔드 API 엔드포인트 및 Service Layer 구현. `04_DEVELOPMENT/UI_REDESIGN_TODO.md`에 정의된 모든 API 엔드포인트와 Service를 구현합니다.

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

#### Phase 1: 캐릭터 관련 API (우선순위: 높음) ✅ 완료
- [x] `/api/gameplay/character/stats/{session_id}`: 캐릭터 능력치 조회
- [x] `/api/gameplay/character/inventory/{session_id}`: 인벤토리 및 장착 아이템 조회 (Effect Carrier 포함)
- [x] `/api/gameplay/character/equipped/{session_id}`: 장착 아이템 조회 (Effect Carrier 포함)
- [x] `/api/gameplay/character/applied-effects/{session_id}`: 적용 중인 Effect Carrier 조회
- [x] `/api/gameplay/character/abilities/{session_id}`: 엔티티의 스킬/주문 목록 조회
- [x] `/api/gameplay/character/spells/{session_id}`: 주문 목록 조회

#### Phase 2: 오브젝트 및 액션 관련 API (우선순위: 높음) ✅ 완료
- [x] `/api/gameplay/object/{object_id}/state`: 오브젝트 상태 조회
- [x] `/api/gameplay/object/{object_id}/actions`: 가능한 액션 조회 (상태 기반)
- [x] `/api/gameplay/actions/categorized/{session_id}`: 카테고리별 액션 조회

#### Phase 3: Service Layer 구현 (우선순위: 높음) ✅ 완료
- [x] `CharacterService`: 캐릭터 관련 비즈니스 로직 (Phase 1에서 완료)
- [x] `JournalService`: 저널 시스템 비즈니스 로직
- [x] `MapService`: 맵 시스템 비즈니스 로직
- [x] `ExplorationService`: 탐험 시스템 비즈니스 로직

#### Phase 4: 데이터베이스 스키마 추가 (우선순위: 중간) ✅ 완료
- [x] `runtime_data.quests` 테이블 생성 (퀘스트 시스템)
- [x] `items.effect_carrier_id` FK 추가 확인 및 추가 (완료)
- [x] `equipment_weapons.effect_carrier_id` FK 추가 확인 및 추가 (완료)
- [x] `equipment_armors.effect_carrier_id` FK 추가 확인 및 추가 (완료)

#### Phase 5: 퀘스트/저널/맵/탐험 시스템 (우선순위: 중간)
- [ ] 퀘스트 시스템 구현 (`03_SYSTEMS/QUEST_SYSTEM_GUIDELINES.md` 참조)
- [ ] 저널 시스템 구현 (`03_SYSTEMS/JOURNAL_SYSTEM_GUIDELINES.md` 참조)
- [ ] 맵 시스템 구현 (`03_SYSTEMS/MAP_SYSTEM_GUIDELINES.md` 참조)
- [ ] 탐험 시스템 구현 (`03_SYSTEMS/EXPLORATION_SYSTEM_GUIDELINES.md` 참조)

## 작업 이력

### 2026-01-03
- 13:00: 프로젝트 시작
- 13:00: 문제 정의 및 현황 진단 완료
  - `04_DEVELOPMENT/UI_REDESIGN_TODO.md` 검토 완료
  - 구현 필요 API 엔드포인트 목록 확인
  - 구현 필요 Service Layer 목록 확인
  - 데이터베이스 스키마 추가 필요 사항 확인

### 2026-01-04
- 14:00: Phase 1 완료
  - CharacterService 생성 및 구현 완료
  - 캐릭터 관련 API 엔드포인트 6개 구현 완료
  - 통합 테스트 작성 및 실행 완료 (6개 테스트 모두 통과)
  - UUID 처리 로직 추가 (UUID 객체를 문자열로 변환)
  - EffectCarrierManager 직접 사용으로 수정
- 15:00: Phase 2 완료
  - ObjectService 생성 및 구현 완료
  - 오브젝트 및 액션 관련 API 엔드포인트 3개 구현 완료
  - ActionService에 get_available_actions_for_object 메서드 추가
  - BaseGameplayService에 action_service property 추가 (순환 import 방지)
  - 통합 테스트 작성 및 실행 완료 (3개 테스트 모두 통과)
- 16:00: Phase 3 완료
  - JournalService 생성 및 구현 완료 (5개 메서드)
  - MapService 생성 및 구현 완료 (2개 메서드)
  - ExplorationService 생성 및 구현 완료 (1개 메서드)
  - 저널/맵/탐험 관련 API 엔드포인트 8개 구현 완료
  - 통합 테스트 작성 및 실행 완료 (3개 테스트 모두 통과)
- 17:00: Phase 4 완료
  - runtime_data.quests 테이블 생성 완료 (제약조건, 인덱스 포함)
  - items, equipment_weapons, equipment_armors 테이블에 effect_carrier_id FK 추가 완료
  - 마이그레이션 스크립트 작성 완료 (add_quests_table.sql, verify_effect_carrier_fks.sql)
  - run_migration.py 스크립트 작성 완료
  - 통합 테스트 작성 및 실행 완료 (7개 테스트 모두 통과)
  - connection_manager.py teardown 오류 수정

## 관련 문서
- [UI 리디자인 TODO](../../rules/04_DEVELOPMENT/UI_REDESIGN_TODO.md)
- [Effect Carrier 가이드라인](../../rules/03_SYSTEMS/EFFECT_CARRIER_GUIDELINES.md)
- [Abilities System 가이드라인](../../rules/03_SYSTEMS/ABILITIES_SYSTEM_GUIDELINES.md)
- [Quest System 가이드라인](../../rules/03_SYSTEMS/QUEST_SYSTEM_GUIDELINES.md) (Placeholder)
- [Journal System 가이드라인](../../rules/03_SYSTEMS/JOURNAL_SYSTEM_GUIDELINES.md) (Placeholder)
- [Map System 가이드라인](../../rules/03_SYSTEMS/MAP_SYSTEM_GUIDELINES.md) (Placeholder)
- [Exploration System 가이드라인](../../rules/03_SYSTEMS/EXPLORATION_SYSTEM_GUIDELINES.md) (Placeholder)
- [개발 워크플로우 가이드](../../rules/04_DEVELOPMENT/DEVELOPMENT_WORKFLOW_GUIDE.md)
- [데이터베이스 스키마](../../../database/setup/mvp_schema.sql) ⭐ **필수 참조**

## 참고 사항
- 모든 API는 `04_DEVELOPMENT/DEVELOPMENT_WORKFLOW_GUIDE.md`의 "API 엔드포인트 추가하기" 가이드를 따라야 합니다.
- 데이터베이스 스키마 변경은 `02_DATABASE/MIGRATION_GUIDELINES.md`를 참조해야 합니다.
- UUID 처리는 `01_TYPE_SAFETY/UUID_GUIDELINES.md`를 참조하고 `uuid_helper.py`를 사용해야 합니다.
- Effect Carrier 관련 작업은 `03_SYSTEMS/EFFECT_CARRIER_GUIDELINES.md`를 참조해야 합니다.

