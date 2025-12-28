# 구현 TODO 리스트

**작성일**: 2025-12-29  
**목적**: 코드베이스에 남아있는 미구현 항목 및 버그 수정 사항 정리

---

## 🔴 긴급 (게임 플레이 차단 이슈)

### 1. 오브젝트 상호작용 액션 생성 개선
**파일**: `app/services/gameplay/action_service.py`  
**문제**: 현재 `interaction_type`에 따라 제한적으로만 액션을 생성하고 있음 (openable, lightable, restable, sitable만 처리)  
**영향**: 오브젝트 조회 시 모든 20개의 액션이 나타나지 않음

**필요 작업**:
- [ ] `properties.interactions` JSONB 필드를 확인하여 동적으로 액션 생성
- [ ] 모든 ActionType에 대한 액션 생성 로직 추가:
  - [ ] Information: `examine`, `inspect`, `search`
  - [ ] State Change: `open`, `close`, `light`, `extinguish`, `activate`, `deactivate`, `lock`, `unlock`
  - [ ] Position: `sit`, `stand`, `lie`, `get_up`, `climb`, `descend`
  - [ ] Recovery: `rest`, `sleep`, `meditate`
  - [ ] Consumption: `eat`, `drink`, `consume`
  - [ ] Learning: `read`, `study`, `write`
  - [ ] Item Manipulation: `pickup`, `place`, `take`, `put`
  - [ ] Crafting: `combine`, `craft`, `cook`, `repair`
  - [ ] Destruction: `destroy`, `break`, `dismantle`
- [ ] `possible_states`를 확인하여 현재 상태에 따라 가능한 액션만 표시
- [ ] 액션 조건 확인 (예: `locked` 상태면 `unlock`만 가능)

**참고**: `docs/architecture/OBJECT_INTERACTION_COMPLETE_GUIDE.md`의 "6. 상호작용 타입 정의" 섹션 참조

---

### 2. 오브젝트 상호작용 액션 타입 매핑 확장
**파일**: `app/services/gameplay/interaction_service.py`  
**문제**: `action_type_map`에 일부 액션만 매핑되어 있음 (9개만 매핑)  
**영향**: 프론트엔드에서 요청한 액션이 백엔드에서 처리되지 않음

**필요 작업**:
- [ ] 모든 ActionType을 `action_type_map`에 추가:
  ```python
  action_type_map = {
      # Information
      'examine': ActionType.EXAMINE_OBJECT,
      'inspect': ActionType.INSPECT_OBJECT,
      'search': ActionType.SEARCH_OBJECT,
      # State Change
      'open': ActionType.OPEN_OBJECT,
      'close': ActionType.CLOSE_OBJECT,
      'light': ActionType.LIGHT_OBJECT,
      'extinguish': ActionType.EXTINGUISH_OBJECT,
      'activate': ActionType.ACTIVATE_OBJECT,
      'deactivate': ActionType.DEACTIVATE_OBJECT,
      'lock': ActionType.LOCK_OBJECT,
      'unlock': ActionType.UNLOCK_OBJECT,
      # Position
      'sit': ActionType.SIT_AT_OBJECT,
      'stand': ActionType.STAND_FROM_OBJECT,
      'lie': ActionType.LIE_ON_OBJECT,
      'get_up': ActionType.GET_UP_FROM_OBJECT,
      'climb': ActionType.CLIMB_OBJECT,
      'descend': ActionType.DESCEND_FROM_OBJECT,
      # Recovery
      'rest': ActionType.REST_AT_OBJECT,
      'sleep': ActionType.SLEEP_AT_OBJECT,
      'meditate': ActionType.MEDITATE_AT_OBJECT,
      # Consumption
      'eat': ActionType.EAT_FROM_OBJECT,
      'drink': ActionType.DRINK_FROM_OBJECT,
      'consume': ActionType.CONSUME_OBJECT,
      # Learning
      'read': ActionType.READ_OBJECT,
      'study': ActionType.STUDY_OBJECT,
      'write': ActionType.WRITE_OBJECT,
      # Item Manipulation
      'pickup': ActionType.PICKUP_FROM_OBJECT,
      'place': ActionType.PLACE_IN_OBJECT,
      'take': ActionType.TAKE_FROM_OBJECT,
      'put': ActionType.PUT_IN_OBJECT,
      # Crafting
      'combine': ActionType.COMBINE_WITH_OBJECT,
      'craft': ActionType.CRAFT_AT_OBJECT,
      'cook': ActionType.COOK_AT_OBJECT,
      'repair': ActionType.REPAIR_OBJECT,
      # Destruction
      'destroy': ActionType.DESTROY_OBJECT,
      'break': ActionType.BREAK_OBJECT,
      'dismantle': ActionType.DISMANTLE_OBJECT,
      # Other
      'use': ActionType.USE_OBJECT,
  }
  ```

---

### 3. 오브젝트 인벤토리 모달 표시
**파일**: `app/ui/frontend/src/hooks/game/useGameActions.ts`  
**문제**: `pickup` 액션 선택 시 `ObjectInventoryModal`이 열리지 않음  
**영향**: 오브젝트에서 아이템을 획득할 수 없음

**필요 작업**:
- [ ] `pickup` 액션 처리 시 `ObjectInventoryModal`을 여는 로직 추가
- [ ] `GameView.tsx`의 `ObjectInventoryModal` 사용 패턴 참조
- [ ] 모달 상태 관리를 위한 state 추가 (또는 GameView에서 처리)
- [ ] 오브젝트 contents 조회 후 모달에 표시

**참고 코드**: `app/ui/frontend/src/components/game/GameView.tsx` 라인 553-595

---

### 4. 방 이동 액션 표시 및 처리
**파일**: `app/services/gameplay/action_service.py`, `app/ui/frontend/src/hooks/game/useGameActions.ts`  
**문제**: 연결된 셀로 이동 액션이 생성되지만 프론트엔드에서 제대로 표시/처리되지 않을 수 있음  
**영향**: 다른 방으로 이동할 수 없음

**필요 작업**:
- [ ] `action_service.py`에서 연결된 셀 액션 생성 로직 확인 및 수정
- [ ] 프론트엔드에서 `move` 액션이 제대로 표시되는지 확인
- [ ] `useGameActions.ts`의 `move` 케이스가 올바르게 처리되는지 확인
- [ ] 이동 후 셀 정보 및 액션 목록 자동 새로고침 확인

---

## 🟡 중요 (기능 완성)

### 5. 오브젝트 조사 후 액션 목록 업데이트
**파일**: `app/ui/frontend/src/hooks/game/useGameActions.ts`  
**문제**: 오브젝트를 조사했을 때 해당 오브젝트에 대한 모든 가능한 액션들이 나타나지 않음  
**영향**: 사용자가 오브젝트와 상호작용할 수 있는 방법을 알 수 없음

**필요 작업**:
- [ ] `examine` 액션 처리 후 `getAvailableActions` 호출하여 액션 목록 업데이트
- [ ] 오브젝트별 액션 필터링 로직 추가 (선택사항)
- [ ] 오브젝트 조사 시 해당 오브젝트에 대한 액션만 표시하는 옵션 추가

---

### 6. 오브젝트 상태 기반 액션 필터링
**파일**: `app/services/gameplay/action_service.py`  
**문제**: 오브젝트의 현재 상태에 따라 가능한 액션만 표시해야 하는데, 모든 액션이 표시됨  
**영향**: 불가능한 액션이 표시되어 사용자 혼란

**필요 작업**:
- [ ] `possible_states` 확인하여 현재 상태에서 가능한 액션만 생성
- [ ] 상태 전이 규칙 확인 (예: `closed` → `open`만 가능, `open` → `close`만 가능)
- [ ] 조건부 액션 처리 (예: `locked` 상태면 `unlock`만 가능)

---

### 7. 오브젝트 상호작용 핸들러 미구현 메서드
**파일**: `app/handlers/object_interactions/`  
**문제**: 일부 핸들러에 TODO 주석이 있거나 미구현 메서드가 있음

**필요 작업**:
- [ ] `recovery.py`: `reduce_fatigue` 메서드 구현 (EntityManager에 추가 필요)
- [ ] `consumption.py`: `handle_eat`, `handle_consume` 메서드 구현
- [ ] `learning.py`: `handle_study` 메서드 구현 (EffectCarrierManager, TimeSystem 연동)
- [ ] `destruction.py`: `handle_dismantle` 메서드 구현 (오브젝트 → 컴포넌트 아이템 변환)

---

## 🟢 개선 (선택사항)

### 8. 저장/불러오기 API 구현
**파일**: `app/ui/frontend/src/screens/game/SaveLoadScreen.tsx`  
**문제**: 저장/불러오기 API가 미구현 (TODO 주석만 있음)

**필요 작업**:
- [ ] 백엔드에 저장 API 엔드포인트 추가
- [ ] 백엔드에 불러오기 API 엔드포인트 추가
- [ ] 백엔드에 삭제 API 엔드포인트 추가
- [ ] 프론트엔드에서 API 호출 구현

---

### 9. 설정 저장 기능
**파일**: `app/ui/frontend/src/screens/game/SettingsScreen.tsx`  
**문제**: 설정 저장이 localStorage에만 저장되고 서버와 동기화되지 않음

**필요 작업**:
- [ ] 백엔드에 설정 저장 API 추가 (선택사항)
- [ ] 설정 불러오기 로직 개선

---

### 10. 게임 재시작 로직
**파일**: `app/ui/frontend/src/screens/game/GameScreen.tsx`  
**문제**: 게임 재시작 로직이 미구현 (TODO 주석만 있음)

**필요 작업**:
- [ ] 게임 상태 초기화 로직 구현
- [ ] 세션 재생성 또는 기존 세션 재사용 로직 구현

---

## 📝 기타 TODO 주석

### Backend
- `app/handlers/action_handler.py`:
  - [ ] 라인 124: EAT_ITEM, DRINK_ITEM, CONSUME_ITEM, DROP_ITEM 추가 필요
  - [ ] 라인 488: TimeSystem 추가 필요
  - [ ] 라인 722: EffectCarrierManager로 효과 적용
  - [ ] 라인 727: TimeSystem 연동 (선택적)

- `app/services/gameplay/dialogue_service.py`:
  - [ ] 라인 83: 대화 선택지 처리 로직 구현

- `app/handlers/item_interactions/inventory_handler.py`:
  - [ ] 라인 75: 더 정교한 구현 (오브젝트 생성 또는 셀 contents 구조에 맞춰)

### Frontend
- `app/ui/frontend/src/components/game/SaveLoadMenu.tsx`:
  - [ ] 라인 23: 저장 API 호출
  - [ ] 라인 29: 불러오기 API 호출

---

## 우선순위 요약

1. **긴급 (게임 플레이 차단)**:
   - 오브젝트 상호작용 액션 생성 개선
   - 오브젝트 상호작용 액션 타입 매핑 확장
   - 오브젝트 인벤토리 모달 표시
   - 방 이동 액션 표시 및 처리

2. **중요 (기능 완성)**:
   - 오브젝트 조사 후 액션 목록 업데이트
   - 오브젝트 상태 기반 액션 필터링
   - 오브젝트 상호작용 핸들러 미구현 메서드

3. **개선 (선택사항)**:
   - 저장/불러오기 API 구현
   - 설정 저장 기능
   - 게임 재시작 로직

---

**참고 문서**:
- `docs/architecture/OBJECT_INTERACTION_COMPLETE_GUIDE.md`: 오브젝트 상호작용 완전 가이드
- `docs/architecture/ACTION_HANDLER_MODULARIZATION_PROPOSAL.md`: ActionHandler 모듈화 제안

