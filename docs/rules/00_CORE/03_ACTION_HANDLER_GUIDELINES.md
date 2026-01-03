# Action Handler 시스템 가이드라인

> **최신화 날짜**: 2026-01-03  
> **적용 범위**: Action Handler 시스템 사용 전 필수 읽기

## 1. 개요

Action Handler는 게임 내 모든 플레이어 행동을 처리하는 핵심 시스템입니다. 모든 게임 로직은 "행동(Action)"으로 표현되며, ActionHandler가 이를 통합적으로 처리합니다.

**핵심 원칙**:
- 모든 게임 로직은 Action으로 표현
- ActionHandler가 모든 행동을 통합 처리
- 카테고리별로 Handler 분리 (확장성 및 유지보수성)
- 엔티티 특성 기반 성공 판정 시스템 (향후 구현)

## 2. ActionType 정의

### 2.1 ActionType Enum

`ActionType`은 게임 내 모든 가능한 행동을 정의하는 열거형입니다:

```python
from app.handlers.action_result import ActionType

# 기본 게임 액션
ActionType.INVESTIGATE  # 조사
ActionType.DIALOGUE     # 대화
ActionType.TRADE        # 거래
ActionType.VISIT        # 방문
ActionType.WAIT         # 대기
ActionType.MOVE         # 이동
ActionType.ATTACK       # 공격
ActionType.USE_ITEM     # 아이템 사용
```

### 2.2 ActionType 카테고리

ActionType은 다음과 같이 카테고리별로 분류됩니다:

#### 2.2.1 Entity Interactions (엔티티 상호작용)

다른 엔티티와의 상호작용:

- `DIALOGUE`: NPC와 대화
- `TRADE`: NPC와 거래
- `ATTACK`: 엔티티 공격

**Handler**: `DialogueHandler`, `TradeHandler`, `CombatHandler`

#### 2.2.2 Cell Interactions (셀 상호작용)

셀(위치) 관련 행동:

- `INVESTIGATE`: 셀 조사
- `VISIT`: 셀 방문
- `MOVE`: 셀 간 이동
- `MOVE_TO_CELL`: 특정 셀로 이동

**Handler**: `InvestigationHandler`, `VisitHandler`, `MovementHandler`

#### 2.2.3 Object Interactions (오브젝트 상호작용)

월드 오브젝트와의 상호작용:

**1. Information (정보 확인)**
- `EXAMINE_OBJECT`: 오브젝트 검사
- `INSPECT_OBJECT`: 오브젝트 자세히 살펴보기
- `SEARCH_OBJECT`: 오브젝트 검색

**2. State Change (상태 변경)**
- `OPEN_OBJECT`: 오브젝트 열기
- `CLOSE_OBJECT`: 오브젝트 닫기
- `LIGHT_OBJECT`: 오브젝트 켜기
- `EXTINGUISH_OBJECT`: 오브젝트 끄기
- `ACTIVATE_OBJECT`: 오브젝트 활성화
- `DEACTIVATE_OBJECT`: 오브젝트 비활성화
- `LOCK_OBJECT`: 오브젝트 잠그기
- `UNLOCK_OBJECT`: 오브젝트 잠금 해제

**3. Position (위치 변경)**
- `SIT_AT_OBJECT`: 오브젝트에 앉기
- `STAND_FROM_OBJECT`: 오브젝트에서 일어나기
- `LIE_ON_OBJECT`: 오브젝트에 눕기
- `GET_UP_FROM_OBJECT`: 오브젝트에서 일어나기
- `CLIMB_OBJECT`: 오브젝트 오르기
- `DESCEND_FROM_OBJECT`: 오브젝트에서 내려오기

**4. Recovery (회복)**
- `REST_AT_OBJECT`: 오브젝트에서 휴식
- `SLEEP_AT_OBJECT`: 오브젝트에서 잠자기
- `MEDITATE_AT_OBJECT`: 오브젝트에서 명상

**5. Consumption (소비)**
- `EAT_FROM_OBJECT`: 오브젝트에서 먹기
- `DRINK_FROM_OBJECT`: 오브젝트에서 마시기
- `CONSUME_OBJECT`: 오브젝트 소비

**6. Learning (학습/정보)**
- `READ_OBJECT`: 오브젝트 읽기
- `STUDY_OBJECT`: 오브젝트 공부하기
- `WRITE_OBJECT`: 오브젝트에 쓰기

**7. Item Manipulation (아이템 조작)**
- `PICKUP_FROM_OBJECT`: 오브젝트에서 아이템 집기
- `PLACE_IN_OBJECT`: 오브젝트에 아이템 놓기
- `TAKE_FROM_OBJECT`: 오브젝트에서 아이템 가져오기
- `PUT_IN_OBJECT`: 오브젝트에 아이템 넣기

**8. Crafting (조합/제작)**
- `COMBINE_WITH_OBJECT`: 오브젝트와 조합
- `CRAFT_AT_OBJECT`: 오브젝트에서 제작
- `COOK_AT_OBJECT`: 오브젝트에서 요리
- `REPAIR_OBJECT`: 오브젝트 수리

**9. Destruction (파괴/변형)**
- `DESTROY_OBJECT`: 오브젝트 파괴
- `BREAK_OBJECT`: 오브젝트 부수기
- `DISMANTLE_OBJECT`: 오브젝트 분해

**Handler**: `InformationInteractionHandler`, `StateChangeInteractionHandler`, `PositionInteractionHandler`, `RecoveryInteractionHandler`, `ConsumptionInteractionHandler`, `LearningInteractionHandler`, `ItemManipulationInteractionHandler`, `CraftingInteractionHandler`, `DestructionInteractionHandler`

#### 2.2.4 Item Interactions (아이템 상호작용)

아이템 관련 행동:

- `USE_ITEM`: 아이템 사용
- `EQUIP_ITEM`: 아이템 장착
- `UNEQUIP_ITEM`: 아이템 해제
- `EAT_ITEM`: 아이템 먹기 (향후)
- `DRINK_ITEM`: 아이템 마시기 (향후)
- `CONSUME_ITEM`: 아이템 소비 (향후)
- `DROP_ITEM`: 아이템 버리기 (향후)

**Handler**: `UseItemHandler`, `EquipmentItemHandler`, `ConsumptionItemHandler`, `InventoryItemHandler`

#### 2.2.5 Time Interactions (시간 상호작용)

시간 관련 행동:

- `WAIT`: 대기

**Handler**: `WaitHandler`

## 3. ActionHandler 작동 원리

### 3.1 ActionHandler 구조

```python
class ActionHandler:
    """핵심 게임 행동 처리 클래스"""
    
    def __init__(self, ...):
        # Manager 초기화
        self.entity_manager = entity_manager
        self.cell_manager = cell_manager
        # ...
        
        # 카테고리별 Handler 초기화
        self._init_object_interaction_handlers()
        self._init_entity_interaction_handlers()
        self._init_cell_interaction_handlers()
        self._init_item_interaction_handlers()
        self._init_time_interaction_handlers()
        
        # ActionType → Handler 매핑
        self.action_handlers = {
            ActionType.DIALOGUE: self.dialogue_handler.handle,
            ActionType.INVESTIGATE: self.investigation_handler.handle,
            # ...
        }
    
    async def execute_action(
        self,
        action_type: ActionType,
        entity_id: UUID,
        target_id: Optional[UUID] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """액션 실행 (라우터)"""
        handler = self.action_handlers.get(action_type)
        if not handler:
            return ActionResult.failure_result(f"Unknown action type: {action_type}")
        return await handler(entity_id, target_id, parameters)
```

### 3.2 실행 흐름

```
1. execute_action() 호출
   ↓
2. action_handlers 딕셔너리에서 Handler 조회
   ↓
3. 해당 Handler의 handle() 메서드 호출
   ↓
4. Handler가 필요한 Manager들을 조합하여 로직 실행
   ↓
5. ActionResult 반환
```

### 3.3 Handler 초기화

각 카테고리별 Handler는 독립적으로 초기화됩니다:

```python
def _init_object_interaction_handlers(self):
    """오브젝트 상호작용 Handler 초기화"""
    base = ObjectInteractionHandlerBase(
        self.db, self.game_data, self.runtime_data,
        self.reference_layer, self.entity_manager,
        self.cell_manager, self.object_state_manager
    )
    
    self.information_handler = InformationInteractionHandler(base)
    self.state_change_handler = StateChangeInteractionHandler(base)
    # ...
```

### 3.4 ActionResult

모든 Handler는 `ActionResult`를 반환합니다:

```python
class ActionResult(BaseModel):
    """행동 결과 모델"""
    success: bool              # 성공 여부
    message: str               # 결과 메시지
    data: Optional[Dict]       # 추가 데이터
    effects: Optional[List]    # 행동 효과
```

**사용 예시**:
```python
# 성공 결과
result = ActionResult.success_result(
    message="오브젝트를 열었습니다.",
    data={"object_state": "open"},
    effects=[{"hp": 10}]  # HP 회복 효과
)

# 실패 결과
result = ActionResult.failure_result(
    message="오브젝트를 열 수 없습니다. (잠겨있음)"
)
```

## 4. ActionType 카테고리화 로직

### 4.1 카테고리 Enum 정의 (향후 구현)

```python
class ActionCategory(str, Enum):
    """액션 카테고리"""
    ENTITY = "entity"      # 엔티티 상호작용
    CELL = "cell"          # 셀 상호작용
    OBJECT = "object"      # 오브젝트 상호작용
    ITEM = "item"          # 아이템 상호작용
    TIME = "time"          # 시간 상호작용
```

### 4.2 ActionType → 카테고리 매핑

```python
ACTION_CATEGORY_MAP = {
    # Entity Interactions
    ActionType.DIALOGUE: ActionCategory.ENTITY,
    ActionType.TRADE: ActionCategory.ENTITY,
    ActionType.ATTACK: ActionCategory.ENTITY,
    
    # Cell Interactions
    ActionType.INVESTIGATE: ActionCategory.CELL,
    ActionType.VISIT: ActionCategory.CELL,
    ActionType.MOVE: ActionCategory.CELL,
    
    # Object Interactions
    ActionType.EXAMINE_OBJECT: ActionCategory.OBJECT,
    ActionType.OPEN_OBJECT: ActionCategory.OBJECT,
    # ...
    
    # Item Interactions
    ActionType.USE_ITEM: ActionCategory.ITEM,
    ActionType.EQUIP_ITEM: ActionCategory.ITEM,
    # ...
    
    # Time Interactions
    ActionType.WAIT: ActionCategory.TIME,
}

def get_action_category(action_type: ActionType) -> ActionCategory:
    """ActionType의 카테고리 반환"""
    return ACTION_CATEGORY_MAP.get(action_type, ActionCategory.OBJECT)
```

### 4.3 카테고리별 그룹화

UI에서 액션을 카테고리별로 그룹화하여 표시할 수 있습니다:

```python
def get_actions_by_category(session_id: UUID) -> Dict[ActionCategory, List[ActionType]]:
    """카테고리별 액션 목록 반환"""
    available_actions = get_available_actions(session_id)
    
    categorized = {
        category: []
        for category in ActionCategory
    }
    
    for action_type in available_actions:
        category = get_action_category(action_type)
        categorized[category].append(action_type)
    
    return categorized
```

## 5. 엔티티 특성 기반 성공 판정 시스템 (향후 구현)

### 5.1 엔티티 특성 (Attributes)

엔티티는 다양한 특성을 가집니다:

```python
class EntityAttribute(str, Enum):
    """엔티티 특성"""
    STRENGTH = "strength"        # 힘
    DEXTERITY = "dexterity"      # 민첩
    CONSTITUTION = "constitution" # 체력
    INTELLIGENCE = "intelligence" # 지능
    WISDOM = "wisdom"            # 지혜
    CHARISMA = "charisma"        # 카리스마
```

### 5.2 액션별 요구 특성

각 액션은 특정 특성을 요구할 수 있습니다:

```python
ACTION_REQUIREMENTS = {
    ActionType.UNLOCK_OBJECT: {
        "primary": EntityAttribute.DEXTERITY,  # 주 특성
        "secondary": EntityAttribute.INTELLIGENCE,  # 보조 특성
        "difficulty": 15  # 난이도 (DC)
    },
    ActionType.DIALOGUE: {
        "primary": EntityAttribute.CHARISMA,
        "secondary": EntityAttribute.WISDOM,
        "difficulty": 12
    },
    ActionType.ATTACK: {
        "primary": EntityAttribute.STRENGTH,
        "secondary": EntityAttribute.DEXTERITY,
        "difficulty": 10
    },
    # ...
}
```

### 5.3 성공 판정 로직

```python
async def check_action_success(
    self,
    action_type: ActionType,
    entity_id: UUID,
    session_id: UUID
) -> Tuple[bool, int]:
    """
    액션 성공 여부 판정
    
    Returns:
        (성공 여부, 주사위 결과)
    """
    # 1. 엔티티 특성 조회
    entity_result = await self.entity_manager.get_entity(entity_id, session_id)
    if not entity_result.success:
        return False, 0
    
    entity_attributes = entity_result.data.base_stats
    
    # 2. 액션 요구사항 조회
    requirements = ACTION_REQUIREMENTS.get(action_type)
    if not requirements:
        # 요구사항이 없으면 자동 성공
        return True, 0
    
    # 3. 주사위 굴리기 (1d20)
    import random
    dice_roll = random.randint(1, 20)
    
    # 4. 특성 보정치 계산
    primary_attr = entity_attributes.get(requirements["primary"], 10)
    secondary_attr = entity_attributes.get(requirements["secondary"], 10)
    modifier = (primary_attr - 10) // 2 + (secondary_attr - 10) // 4
    
    # 5. 최종 결과 계산
    total = dice_roll + modifier
    success = total >= requirements["difficulty"]
    
    return success, total
```

### 5.4 성공 판정 통합

Handler에서 성공 판정을 통합:

```python
async def handle_unlock_object(
    self,
    entity_id: UUID,
    target_id: UUID,
    parameters: Optional[Dict[str, Any]] = None
) -> ActionResult:
    """오브젝트 잠금 해제"""
    # 1. 성공 판정
    success, total = await self.check_action_success(
        ActionType.UNLOCK_OBJECT,
        entity_id,
        parameters["session_id"]
    )
    
    if not success:
        return ActionResult.failure_result(
            f"잠금 해제 실패 (결과: {total}, 필요: {requirements['difficulty']})"
        )
    
    # 2. 잠금 해제 로직 실행
    # ...
    
    return ActionResult.success_result("잠금 해제 성공")
```

## 6. Handler 구현 원칙

### 6.1 단일 책임 원칙

각 Handler는 하나의 카테고리만 담당합니다:

- ✅ `DialogueHandler`: 대화만 처리
- ✅ `InvestigationHandler`: 조사만 처리
- ❌ 하나의 Handler가 여러 카테고리 처리 금지

### 6.2 Manager 조합

Handler는 여러 Manager를 조합하여 사용합니다:

```python
class DialogueHandler:
    def __init__(self, entity_manager, dialogue_manager):
        self.entity_manager = entity_manager
        self.dialogue_manager = dialogue_manager
    
    async def handle(self, entity_id, target_id, parameters):
        # EntityManager로 엔티티 조회
        player = await self.entity_manager.get_entity(entity_id)
        
        # DialogueManager로 대화 시작
        dialogue = await self.dialogue_manager.start_dialogue(...)
        
        return ActionResult.success_result(...)
```

### 6.3 에러 처리

모든 Handler는 명시적 에러 처리를 수행합니다:

```python
async def handle(self, entity_id, target_id, parameters):
    try:
        # 로직 실행
        result = await self._execute_logic(...)
        return ActionResult.success_result(...)
    except ValueError as e:
        return ActionResult.failure_result(str(e))
    except Exception as e:
        self.logger.error(f"Unexpected error: {e}")
        return ActionResult.failure_result("예상치 못한 오류가 발생했습니다.")
```

### 6.4 트랜잭션 사용

상태 변경이 있는 액션은 트랜잭션을 사용합니다:

```python
from app.common.decorators.transaction import with_transaction

@with_transaction
async def handle_open_object(
    self,
    entity_id: UUID,
    target_id: UUID,
    parameters: Optional[Dict[str, Any]] = None,
    conn=None
) -> ActionResult:
    """오브젝트 열기 (트랜잭션 보장)"""
    # 1. 오브젝트 상태 조회
    # 2. 상태 전이 검증
    # 3. 상태 업데이트
    # 4. 이벤트 트리거
    # ...
```

## 7. 새로운 액션 추가 방법

### 7.1 ActionType 추가

```python
# app/handlers/action_result.py
class ActionType(str, Enum):
    # 기존 액션들...
    
    # 새로운 액션 추가
    NEW_ACTION = "new_action"
```

### 7.2 Handler 구현

```python
# app/handlers/new_category/new_action_handler.py
class NewActionHandler:
    async def handle(
        self,
        entity_id: UUID,
        target_id: Optional[UUID] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        # 로직 구현
        pass
```

### 7.3 ActionHandler에 등록

```python
# app/handlers/action_handler.py
def _init_new_category_handlers(self):
    self.new_action_handler = NewActionHandler(...)

# action_handlers 딕셔너리에 추가
self.action_handlers = {
    # 기존 액션들...
    ActionType.NEW_ACTION: self.new_action_handler.handle,
}
```

## 8. 참고 문서

- `00_CORE/02_ARCHITECTURE_PRINCIPLES.md`: 아키텍처 설계 원칙 (Factory vs Handler)
- `docs/architecture/ARCHITECTURE_DISCUSSION.md`: 아키텍처 토론 문서
- `app/handlers/action_handler.py`: ActionHandler 구현
- `app/handlers/action_result.py`: ActionType 및 ActionResult 정의
- `04_DEVELOPMENT/UI_REDESIGN_TODO.md`: UI 리디자인 TODO (액션 카테고리화)

## 9. 향후 구현 사항

### 9.1 엔티티 특성 기반 성공 판정 시스템

- [ ] 엔티티 특성 정의 및 저장 방법 결정
- [ ] 액션별 요구 특성 및 난이도 정의
- [ ] 주사위 굴리기 시스템 구현
- [ ] 특성 보정치 계산 로직 구현
- [ ] 성공 판정 통합 (모든 Handler에 적용)

### 9.2 ActionType 카테고리화

- [ ] `ActionCategory` Enum 정의
- [ ] `ACTION_CATEGORY_MAP` 매핑 테이블 생성
- [ ] 카테고리별 액션 조회 API 구현
- [ ] UI에서 카테고리별 그룹화 표시

### 9.3 액션 조건 시스템

- [ ] 액션 사용 가능 조건 정의 (예: 특정 아이템 필요, 특정 상태 필요)
- [ ] 조건 검증 로직 구현
- [ ] 조건 미충족 시 액션 비활성화/숨김 처리

