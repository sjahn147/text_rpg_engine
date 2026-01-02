# TODO 목록

## 프론트엔드

### 게임 화면 및 UI
- [ ] **InfoPanel 모달 표시 문제**: `GameView`에서 `isInfoPanelOpen` 상태 관리 및 `InfoPanel` 렌더링 확인 필요
- [ ] **오브젝트 조회 후 액션 업데이트**: `examine` 액션 처리 후 해당 오브젝트에 대한 액션들(open, close, light 등)이 `availableActions`에 추가되도록 수정
- [ ] **연결된 셀 이동 액션**: `availableActions`에 연결된 셀에 대한 `move` 액션이 포함되도록 백엔드/프론트엔드 확인
- [ ] **오브젝트별 액션 표시**: 오브젝트를 조사한 후 해당 오브젝트에 대한 개별 액션들이 선택지에 표시되도록 수정

### 저장/불러오기
- [ ] **SaveLoadScreen**: 저장 슬롯 목록 API 호출 구현
- [ ] **SaveLoadScreen**: 저장 API 호출 구현
- [ ] **SaveLoadScreen**: 불러오기 API 호출 구현
- [ ] **SaveLoadScreen**: 삭제 API 호출 구현
- [ ] **SaveLoadMenu**: 저장 API 호출 구현
- [ ] **SaveLoadMenu**: 불러오기 API 호출 구현

### 설정
- [ ] **SettingsScreen**: 설정 저장 API 호출 또는 localStorage 저장 구현

### 게임 재시작
- [ ] **GameScreen**: 게임 재시작 로직 구현

## 백엔드

### Action Handler
- [ ] **action_handler.py**: `EAT_ITEM`, `DRINK_ITEM`, `CONSUME_ITEM`, `DROP_ITEM` 액션 타입 추가 필요
- [ ] **action_handler.py**: `TimeSystem` 추가 필요 (라인 488)
- [ ] **action_handler.py**: `EffectCarrierManager`로 효과 적용 (라인 722)
- [ ] **action_handler.py**: `TimeSystem` 연동 (선택적, 라인 727)

### Dialogue Service
- [ ] **dialogue_service.py**: 대화 선택지 처리 로직 구현 (라인 83)

### Object Interactions
- [ ] **recovery.py**: `EntityManager`에 `reduce_fatigue` 메서드 추가 필요 (라인 143)

### Item Interactions
- [ ] **inventory_handler.py**: 오브젝트 생성 또는 셀 contents 구조에 맞춰 더 정교한 구현 필요 (라인 75)

## 현재 발견된 버그 (수정 완료)

### 1. ✅ 오브젝트 조회 시 액션이 나오지 않음 (수정 완료)
**원인**: `useGameActions.ts`와 `GameView.tsx`의 `examine` 케이스에서 오브젝트를 조사한 후 `availableActions`를 업데이트하지 않음

**수정 내용**:
- `useGameActions.ts`: `examine` 케이스에서 오브젝트 타입일 때 `interactWithObject` 호출 후 `getAvailableActions`로 액션 목록 업데이트
- `GameView.tsx`: `examine` 케이스에서 오브젝트 타입 처리 추가 및 액션 목록 업데이트

### 2. ⚠️ 다른 방 이동이 안 됨 (확인 필요)
**원인**: 백엔드 `action_service.py`에서 연결된 셀에 대한 `move` 액션을 생성하고 있지만, 다음 중 하나일 수 있음:
1. 셀의 `properties.connected_cells` 정보가 제대로 설정되지 않음
2. 프론트엔드에서 `availableActions`에 `move` 액션이 포함되어 있지만 표시되지 않음
3. `showChoices` 조건이 `currentMessage`가 있을 때만 true가 되어 메시지가 없으면 선택지가 표시되지 않음

**확인 필요**:
- 백엔드 `action_service.py`의 `get_available_actions`에서 연결된 셀에 대한 `move` 액션을 반환하는지 확인 (라인 88-96)
- 프론트엔드에서 `availableActions`에 `move` 타입 액션이 포함되어 있는지 확인
- `GameView`의 `showChoices` 로직 확인: `availableActions.length > 0 && currentMessage` 조건
- 셀 데이터의 `connected_cells` 정보가 제대로 설정되어 있는지 확인

### 3. ✅ 인벤토리 모달이 나오지 않음 (수정 완료)
**원인**: `InfoPanel`의 `inventory` 데이터 로드 로직에서 API 응답 구조가 맞지 않음

**수정 내용**:
- `InfoPanel.tsx`: `getPlayerInventory` API 응답이 `{inventory: [...], equipped_items: [...]}` 형태일 수 있으므로 이를 처리하도록 수정
- `GameView.tsx`에서 `InfoPanel` 컴포넌트가 제대로 렌더링되는지 확인 (라인 540-543)

## 우선순위

### 높음 (즉시 수정 필요)
1. 오브젝트 조회 시 액션 표시 문제
2. 인벤토리 모달 표시 문제
3. 연결된 셀 이동 기능

### 중간
4. 저장/불러오기 API 연동
5. 설정 저장 기능

### 낮음
6. TimeSystem 연동
7. EffectCarrierManager 연동
8. 대화 선택지 처리

