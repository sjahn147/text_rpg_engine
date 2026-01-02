# ActionHandler 모듈화 제안

**작성일**: 2025-12-28  
**최신화 날짜**: 2025-12-28  
**목적**: ActionHandler의 모든 액션 유형을 체계적으로 분리하는 방안 제안

**관련 문서**:
- `OBJECT_INTERACTION_COMPLETE_GUIDE.md`: 오브젝트 상호작용 완전 가이드 (Ownership 설계 포함)
- `ARCHITECTURE_DISCUSSION.md`: 아키텍처 설계 토론

---

## 현재 ActionHandler 구조 분석

### 현재 ActionType 분류

```
1. 기본 게임 액션 (Core Game Actions)
   - INVESTIGATE: 조사
   - DIALOGUE: 대화
   - TRADE: 거래
   - VISIT: 방문
   - WAIT: 대기
   - MOVE: 이동
   - ATTACK: 공격
   - USE_ITEM: 아이템 사용

2. 오브젝트 상호작용 (Object Interactions) - 이미 모듈화됨
   - Information, State Change, Position, Recovery, Consumption, etc.
```

---

## 문제점

1. **기본 게임 액션이 ActionHandler에 집중**: 8개의 핸들러 메서드가 하나의 파일에 있음
2. **확장성 부족**: 새로운 액션 추가 시 ActionHandler 파일이 커짐
3. **책임 분리 부족**: 각 액션 타입별로 다른 Manager를 사용하지만 한 곳에 모여있음

---

## 제안: 액션 유형별 분류

### 1. Entity Actions (엔티티 액션)

**대상**: 다른 엔티티와의 상호작용

| 액션 | 설명 | 사용 Manager | 분리 필요성 |
|------|------|-------------|------------|
| `DIALOGUE` | NPC와 대화 | EntityManager, DialogueManager | ✅ 높음 |
| `TRADE` | NPC와 거래 | EntityManager, InventoryManager | ✅ 높음 |
| `ATTACK` | 엔티티 공격 | EntityManager, CombatManager | ✅ 높음 |

**제안 구조**:
```
app/handlers/entity_interactions/
├── __init__.py
├── dialogue_handler.py      # DIALOGUE
├── trade_handler.py         # TRADE
└── combat_handler.py        # ATTACK
```

**이유**:
- 엔티티 간 상호작용은 복잡한 로직 필요
- DialogueManager, TradeManager 등 별도 Manager 필요
- 독립적으로 테스트 가능

---

### 2. Cell Actions (셀 액션)

**대상**: 셀(위치)과의 상호작용

| 액션 | 설명 | 사용 Manager | 분리 필요성 |
|------|------|-------------|------------|
| `INVESTIGATE` | 셀 조사 | CellManager | ✅ 중간 |
| `VISIT` | 셀 방문 | CellManager | ✅ 중간 |
| `MOVE` | 셀 이동 | CellManager, EntityManager | ✅ 높음 |

**제안 구조**:
```
app/handlers/cell_interactions/
├── __init__.py
├── investigation_handler.py  # INVESTIGATE
├── visit_handler.py         # VISIT
└── movement_handler.py      # MOVE
```

**이유**:
- 셀 관련 로직은 CellManager 중심
- 이동은 복잡한 로직 (충돌 검사, 경로 찾기 등)
- 독립적으로 확장 가능

---

### 3. Item Actions (아이템 액션)

**대상**: 인벤토리 아이템과의 상호작용

| 액션 | 설명 | 사용 Manager | 분리 필요성 |
|------|------|-------------|------------|
| `USE_ITEM` | 아이템 사용 | InventoryManager, EntityManager | ✅ 높음 |
| `EAT_ITEM` | 아이템 먹기 (신규) | InventoryManager, EntityManager | ✅ 높음 |
| `DRINK_ITEM` | 아이템 마시기 (신규) | InventoryManager, EntityManager | ✅ 높음 |
| `CONSUME_ITEM` | 아이템 소비 (신규) | InventoryManager, EntityManager | ✅ 높음 |
| `EQUIP_ITEM` | 아이템 장착 (신규) | InventoryManager, EntityManager | ✅ 높음 |
| `UNEQUIP_ITEM` | 아이템 해제 (신규) | InventoryManager, EntityManager | ✅ 높음 |
| `DROP_ITEM` | 아이템 버리기 (신규) | InventoryManager, CellManager | ✅ 높음 |

**제안 구조**:
```
app/handlers/item_interactions/
├── __init__.py
├── use_handler.py           # USE_ITEM
├── consumption_handler.py   # EAT_ITEM, DRINK_ITEM, CONSUME_ITEM
├── equipment_handler.py     # EQUIP_ITEM, UNEQUIP_ITEM
└── inventory_handler.py     # DROP_ITEM
```

**이유**:
- 아이템 관련 로직은 InventoryManager 중심
- 소비, 장착 등 다양한 상호작용 타입
- Object Interactions와 대칭적 구조

---

### 4. Time Actions (시간 액션)

**대상**: 시간 관련 액션

| 액션 | 설명 | 사용 Manager | 분리 필요성 |
|------|------|-------------|------------|
| `WAIT` | 시간 대기 | TimeSystem | ✅ 중간 |

**제안 구조**:
```
app/handlers/time_interactions/
├── __init__.py
└── wait_handler.py          # WAIT
```

**이유**:
- TimeSystem과 밀접한 연관
- 나중에 시간 관련 액션 추가 가능 (빠르게 이동, 시간 정지 등)

---

## 최종 제안 구조

```
app/handlers/
├── action_handler.py              # 메인 라우터 (약 500줄)
├── action_handler_base.py         # 베이스 클래스
├── entity_interactions/           # 엔티티 상호작용
│   ├── __init__.py
│   ├── dialogue_handler.py
│   ├── trade_handler.py
│   └── combat_handler.py
├── cell_interactions/             # 셀 상호작용
│   ├── __init__.py
│   ├── investigation_handler.py
│   ├── visit_handler.py
│   └── movement_handler.py
├── item_interactions/             # 아이템 상호작용 (신규)
│   ├── __init__.py
│   ├── use_handler.py
│   ├── consumption_handler.py
│   ├── equipment_handler.py
│   └── inventory_handler.py
├── object_interactions/           # 오브젝트 상호작용 (기존)
│   ├── __init__.py
│   ├── information.py
│   ├── state_change.py
│   ├── position.py
│   ├── recovery.py
│   ├── consumption.py
│   ├── learning.py
│   ├── item_manipulation.py
│   ├── crafting.py
│   └── destruction.py
└── time_interactions/             # 시간 상호작용
    ├── __init__.py
    └── wait_handler.py
```

---

## ActionHandler 리팩토링 계획

### Phase 1: Item Interactions 추가 (우선순위: 높음)

1. `app/handlers/item_interactions/` 디렉토리 생성
2. `ConsumptionItemHandler`: `eat_item`, `drink_item`, `consume_item`
3. `UseItemHandler`: `use_item` (기존 로직 이동)
4. `EquipmentItemHandler`: `equip_item`, `unequip_item`
5. `InventoryItemHandler`: `drop_item`

### Phase 2: Entity Interactions 분리 (우선순위: 중간)

1. `app/handlers/entity_interactions/` 디렉토리 생성
2. `DialogueHandler`: `handle_dialogue`
3. `TradeHandler`: `handle_trade`
4. `CombatHandler`: `handle_attack`

### Phase 3: Cell Interactions 분리 (우선순위: 중간)

1. `app/handlers/cell_interactions/` 디렉토리 생성
2. `InvestigationHandler`: `handle_investigate`
3. `VisitHandler`: `handle_visit`
4. `MovementHandler`: `handle_move`

### Phase 4: Time Interactions 분리 (우선순위: 낮음)

1. `app/handlers/time_interactions/` 디렉토리 생성
2. `WaitHandler`: `handle_wait`

---

## 베이스 클래스 설계

### ActionHandlerBase

```python
class ActionHandlerBase(ABC):
    """액션 핸들러 베이스 클래스"""
    
    def __init__(
        self,
        db_connection: DatabaseConnection,
        entity_manager: Optional[EntityManager] = None,
        cell_manager: Optional[CellManager] = None,
        inventory_manager: Optional[InventoryManager] = None,
        # ... 기타 Manager들
    ):
        self.db = db_connection
        self.entity_manager = entity_manager
        self.cell_manager = cell_manager
        self.inventory_manager = inventory_manager
        # ...
    
    @abstractmethod
    async def handle(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """액션 처리"""
        pass
```

---

## ActionHandler 라우터 구조

```python
class ActionHandler:
    """핵심 게임 행동 처리 클래스 (라우터)"""
    
    def __init__(self, ...):
        # Manager 초기화
        # ...
        
        # 각 카테고리별 핸들러 초기화
        self._init_entity_interaction_handlers()
        self._init_cell_interaction_handlers()
        self._init_item_interaction_handlers()
        self._init_object_interaction_handlers()
        self._init_time_interaction_handlers()
        
        # 액션 핸들러 매핑
        self.action_handlers = {
            # Entity Interactions
            ActionType.DIALOGUE: self.dialogue_handler.handle,
            ActionType.TRADE: self.trade_handler.handle,
            ActionType.ATTACK: self.combat_handler.handle,
            
            # Cell Interactions
            ActionType.INVESTIGATE: self.investigation_handler.handle,
            ActionType.VISIT: self.visit_handler.handle,
            ActionType.MOVE: self.movement_handler.handle,
            
            # Item Interactions
            ActionType.USE_ITEM: self.use_item_handler.handle,
            ActionType.EAT_ITEM: self.consumption_item_handler.handle_eat,
            # ...
            
            # Object Interactions (기존)
            # ...
            
            # Time Interactions
            ActionType.WAIT: self.wait_handler.handle,
        }
    
    async def execute_action(self, action_type: ActionType, ...):
        """액션 실행 (라우터)"""
        handler = self.action_handlers.get(action_type)
        if not handler:
            return ActionResult.failure_result(f"Unknown action type: {action_type}")
        return await handler(entity_id, target_id, parameters)
```

---

## 장점

1. **명확한 책임 분리**: 각 액션 타입별로 독립적인 핸들러
2. **확장성**: 새로운 액션 추가 시 해당 카테고리만 수정
3. **테스트 용이성**: 각 핸들러를 독립적으로 테스트 가능
4. **유지보수성**: 특정 액션 타입만 수정하면 됨
5. **일관성**: Object Interactions와 동일한 패턴

---

## 구현 우선순위

1. **Item Interactions** (우선순위: 높음)
   - Ownership 설계와 직접 연관
   - `EAT_ITEM`, `DRINK_ITEM` 등 신규 액션 필요

2. **Entity Interactions** (우선순위: 중간)
   - Dialogue, Trade는 복잡한 로직
   - 별도 Manager 필요

3. **Cell Interactions** (우선순위: 중간)
   - MOVE는 복잡한 로직 (충돌 검사 등)
   - CellManager 중심

4. **Time Interactions** (우선순위: 낮음)
   - WAIT는 단순한 로직
   - 나중에 확장 가능

---

## 결론

### 권장 분리 구조

ActionHandler를 다음과 같이 분리하는 것을 권장:

1. **Entity Interactions**: 엔티티 간 상호작용 (Dialogue, Trade, Attack)
   - **이유**: 엔티티 간 상호작용은 복잡한 로직 필요 (DialogueManager, TradeManager 등)
   - **분리 필요성**: ✅ 높음

2. **Cell Interactions**: 셀과의 상호작용 (Investigate, Visit, Move)
   - **이유**: 셀 관련 로직은 CellManager 중심, MOVE는 복잡한 로직 (충돌 검사 등)
   - **분리 필요성**: ✅ 중간-높음

3. **Item Interactions**: 아이템과의 상호작용 (Use, Eat, Equip) - 신규
   - **이유**: Ownership 설계와 직접 연관, 인벤토리 아이템과의 직접 상호작용 필요
   - **분리 필요성**: ✅ 높음 (우선순위 최상)

4. **Object Interactions**: 오브젝트와의 상호작용 (기존, 이미 모듈화됨)
   - **상태**: ✅ 이미 모듈화 완료

5. **Time Interactions**: 시간 관련 액션 (Wait)
   - **이유**: TimeSystem과 밀접한 연관, 나중에 시간 관련 액션 추가 가능
   - **분리 필요성**: ✅ 중간

### 최종 구조

```
app/handlers/
├── action_handler.py              # 메인 라우터 (약 500줄)
├── action_handler_base.py         # 베이스 클래스
├── entity_interactions/           # 엔티티 상호작용
│   ├── dialogue_handler.py        # DIALOGUE
│   ├── trade_handler.py           # TRADE
│   └── combat_handler.py          # ATTACK
├── cell_interactions/             # 셀 상호작용
│   ├── investigation_handler.py  # INVESTIGATE
│   ├── visit_handler.py           # VISIT
│   └── movement_handler.py         # MOVE
├── item_interactions/             # 아이템 상호작용 (신규)
│   ├── use_handler.py            # USE_ITEM
│   ├── consumption_handler.py    # EAT_ITEM, DRINK_ITEM
│   ├── equipment_handler.py       # EQUIP_ITEM, UNEQUIP_ITEM
│   └── inventory_handler.py       # DROP_ITEM
├── object_interactions/           # 오브젝트 상호작용 (기존)
│   └── ... (이미 모듈화됨)
└── time_interactions/             # 시간 상호작용
    └── wait_handler.py            # WAIT
```

### 구현 우선순위

1. **Item Interactions** (우선순위: 최상)
   - Ownership 설계와 직접 연관
   - `EAT_ITEM`, `DRINK_ITEM` 등 신규 액션 필요
   - 인벤토리 아이템과의 직접 상호작용 지원

2. **Entity Interactions** (우선순위: 높음)
   - Dialogue, Trade는 복잡한 로직
   - 별도 Manager 필요 (DialogueManager, TradeManager)

3. **Cell Interactions** (우선순위: 중간)
   - MOVE는 복잡한 로직 (충돌 검사, 경로 찾기 등)
   - CellManager 중심

4. **Time Interactions** (우선순위: 낮음)
   - WAIT는 단순한 로직
   - 나중에 확장 가능 (빠르게 이동, 시간 정지 등)

### 예상 효과

- **ActionHandler 파일 크기**: 1313줄 → 약 500줄 (라우터 역할만)
- **모듈화**: 각 액션 타입별로 독립적인 핸들러
- **확장성**: 새로운 액션 추가 시 해당 카테고리만 수정
- **테스트 용이성**: 각 핸들러를 독립적으로 테스트 가능
- **유지보수성**: 특정 액션 타입만 수정하면 됨

