# ActionHandler 리팩토링 완전 계획

**작성일**: 2025-12-28  
**최신화 날짜**: 2025-12-28  
**목적**: ActionHandler 모듈화 및 미구현 사항 완전 구현 계획

**관련 문서**:
- `ACTION_HANDLER_MODULARIZATION_PROPOSAL.md`: 모듈화 제안
- `OBJECT_INTERACTION_COMPLETE_GUIDE.md`: 오브젝트 상호작용 가이드
- `OBJECT_INTERACTION_REFACTORING_PLAN.md`: 오브젝트 상호작용 리팩토링 계획

---

## 목차

1. [현재 상태 분석](#1-현재-상태-분석)
2. [미구현 사항 정리](#2-미구현-사항-정리)
3. [리팩토링 단계](#3-리팩토링-단계)
4. [디렉토리 구조](#4-디렉토리-구조)
5. [구현 상세](#5-구현-상세)
6. [테스트 계획](#6-테스트-계획)
7. [API 업데이트](#7-api-업데이트)
8. [프론트엔드 연동](#8-프론트엔드-연동)

---

## 1. 현재 상태 분석

### 1.1 현재 ActionHandler 구조

```
app/handlers/
├── action_handler.py (1313줄) - 모든 액션 핸들러 포함
├── object_interactions/ (이미 모듈화됨)
│   ├── __init__.py
│   ├── object_interaction_base.py
│   ├── information.py
│   ├── state_change.py
│   ├── position.py
│   ├── recovery.py
│   ├── consumption.py
│   ├── learning.py
│   ├── item_manipulation.py
│   ├── crafting.py
│   └── destruction.py
```

### 1.2 현재 ActionType 분류

#### 기본 게임 액션 (ActionHandler에 집중)
- `INVESTIGATE`: 조사
- `DIALOGUE`: 대화
- `TRADE`: 거래
- `VISIT`: 방문
- `WAIT`: 대기
- `MOVE`: 이동
- `ATTACK`: 공격
- `USE_ITEM`: 아이템 사용

#### 오브젝트 상호작용 (이미 모듈화됨)
- Information: `EXAMINE_OBJECT`, `INSPECT_OBJECT`, `SEARCH_OBJECT`
- State Change: `OPEN_OBJECT`, `CLOSE_OBJECT`, `LIGHT_OBJECT`, etc.
- Position: `SIT_AT_OBJECT`, `STAND_FROM_OBJECT`, etc.
- Recovery: `REST_AT_OBJECT`, `SLEEP_AT_OBJECT`, `MEDITATE_AT_OBJECT`
- Consumption: `EAT_FROM_OBJECT`, `DRINK_FROM_OBJECT`, `CONSUME_OBJECT`
- Learning: `READ_OBJECT`, `STUDY_OBJECT`, `WRITE_OBJECT`
- Item Manipulation: `PICKUP_FROM_OBJECT`, `PLACE_IN_OBJECT`, etc.
- Crafting: `COMBINE_WITH_OBJECT`, `CRAFT_AT_OBJECT`, etc.
- Destruction: `DESTROY_OBJECT`, `BREAK_OBJECT`, `DISMANTLE_OBJECT`

---

## 2. 미구현 사항 정리

### 2.1 코드 내 TODO 주석

#### Object Interactions
1. **consumption.py**
   - `handle_eat`: 구현 예정 (EAT_FROM_OBJECT)
   - EffectCarrierManager로 효과 적용
   - TimeSystem 연동

2. **recovery.py**
   - `handle_sleep`: TimeSystem 연동 (480분 = 8시간)
   - 피로도 감소 처리

3. **crafting.py**
   - `handle_combine`: 구현 예정 (COMBINE_WITH_OBJECT)
   - `handle_craft`: 구현 예정 (재료 + 오브젝트 → 결과, 시간 소모)
   - `handle_cook`: 구현 예정 (재료 → 음식, 시간 소모)
   - TimeSystem 연동

4. **destruction.py**
   - TimeSystem 연동
   - `handle_dismantle`: 구현 예정 (오브젝트 → 부품, 시간 소모)

5. **learning.py**
   - EffectCarrierManager로 효과 적용
   - TimeSystem 연동
   - 아이템 생성 (필요시)

6. **action_handler.py**
   - EffectCarrierManager로 효과 적용
   - TimeSystem 연동 (선택적)

### 2.2 신규 구현 필요 사항

#### Item Interactions (신규)
1. **ConsumptionItemHandler**
   - `EAT_ITEM`: 인벤토리에서 아이템 먹기
   - `DRINK_ITEM`: 인벤토리에서 아이템 마시기
   - `CONSUME_ITEM`: 인벤토리에서 아이템 소비

2. **UseItemHandler**
   - `USE_ITEM`: 인벤토리에서 아이템 사용 (기존 로직 이동)

3. **EquipmentItemHandler**
   - `EQUIP_ITEM`: 아이템 장착
   - `UNEQUIP_ITEM`: 아이템 해제

4. **InventoryItemHandler**
   - `DROP_ITEM`: 아이템 버리기

#### Entity Interactions (신규)
1. **DialogueHandler**
   - `DIALOGUE`: NPC와 대화 (기존 로직 이동)

2. **TradeHandler**
   - `TRADE`: NPC와 거래 (기존 로직 이동)

3. **CombatHandler**
   - `ATTACK`: 엔티티 공격 (기존 로직 이동)

#### Cell Interactions (신규)
1. **InvestigationHandler**
   - `INVESTIGATE`: 셀 조사 (기존 로직 이동)

2. **VisitHandler**
   - `VISIT`: 셀 방문 (기존 로직 이동)

3. **MovementHandler**
   - `MOVE`: 셀 이동 (기존 로직 이동)

#### Time Interactions (신규)
1. **WaitHandler**
   - `WAIT`: 시간 대기 (기존 로직 이동)

### 2.3 시스템 연동 필요 사항

1. **TimeSystem 연동**
   - 모든 시간 소모 액션에 TimeSystem 연동
   - `sleep`: 480분 (8시간)
   - `craft`, `cook`, `dismantle`: 각각의 시간 소모량

2. **EffectCarrierManager 연동**
   - `eat`, `drink`, `consume`: Effect Carrier 효과 적용
   - `read`, `study`: Effect Carrier 효과 적용

3. **피로도 시스템**
   - `sleep`: 피로도 감소 처리

---

## 3. 리팩토링 단계

### Phase 1: 디렉토리 구조 변경
- [ ] `app/handlers/entity_interactions/` 생성
- [ ] `app/handlers/cell_interactions/` 생성
- [ ] `app/handlers/item_interactions/` 생성
- [ ] `app/handlers/time_interactions/` 생성
- [ ] `app/handlers/action_handler_base.py` 생성

### Phase 2: 필요한 모듈 생성
- [ ] 베이스 클래스 구현 (`ActionHandlerBase`)
- [ ] Entity Interactions 핸들러 모듈 생성
- [ ] Cell Interactions 핸들러 모듈 생성
- [ ] Item Interactions 핸들러 모듈 생성
- [ ] Time Interactions 핸들러 모듈 생성

### Phase 3: 미구현 사항 포함 모듈 구현
- [ ] Object Interactions 미구현 사항 구현
  - [ ] `handle_eat` 구현
  - [ ] `handle_combine` 구현
  - [ ] `handle_craft` 구현
  - [ ] `handle_cook` 구현
  - [ ] `handle_dismantle` 구현
  - [ ] TimeSystem 연동
  - [ ] EffectCarrierManager 연동
  - [ ] 피로도 시스템 연동
- [ ] Item Interactions 구현
  - [ ] ConsumptionItemHandler 구현
  - [ ] UseItemHandler 구현
  - [ ] EquipmentItemHandler 구현
  - [ ] InventoryItemHandler 구현
- [ ] Entity Interactions 구현
  - [ ] DialogueHandler 구현
  - [ ] TradeHandler 구현
  - [ ] CombatHandler 구현
- [ ] Cell Interactions 구현
  - [ ] InvestigationHandler 구현
  - [ ] VisitHandler 구현
  - [ ] MovementHandler 구현
- [ ] Time Interactions 구현
  - [ ] WaitHandler 구현

### Phase 4: ActionHandler 리팩토링
- [ ] ActionHandler를 라우터로 변경
- [ ] 기존 핸들러 메서드를 각 모듈로 이동
- [ ] 핸들러 매핑 업데이트

### Phase 5: 단위 테스트
- [ ] Object Interactions 단위 테스트
- [ ] Item Interactions 단위 테스트
- [ ] Entity Interactions 단위 테스트
- [ ] Cell Interactions 단위 테스트
- [ ] Time Interactions 단위 테스트

### Phase 6: 통합 테스트
- [ ] ActionHandler 통합 테스트
- [ ] API 엔드포인트 통합 테스트
- [ ] 전체 플로우 통합 테스트

### Phase 7: API 제작
- [ ] API 엔드포인트 업데이트
- [ ] 새로운 액션 타입 API 추가
- [ ] API 문서 업데이트

### Phase 8: 프론트엔드 연결
- [ ] 프론트엔드 액션 호출 업데이트
- [ ] 새로운 액션 타입 UI 추가
- [ ] 에러 처리 및 피드백

---

## 4. 디렉토리 구조

### 4.1 최종 디렉토리 구조

```
app/handlers/
├── action_handler.py              # 메인 라우터 (약 500줄)
├── action_handler_base.py         # 베이스 클래스
│
├── entity_interactions/           # 엔티티 상호작용
│   ├── __init__.py
│   ├── dialogue_handler.py        # DIALOGUE
│   ├── trade_handler.py           # TRADE
│   └── combat_handler.py          # ATTACK
│
├── cell_interactions/             # 셀 상호작용
│   ├── __init__.py
│   ├── investigation_handler.py  # INVESTIGATE
│   ├── visit_handler.py           # VISIT
│   └── movement_handler.py        # MOVE
│
├── item_interactions/             # 아이템 상호작용 (신규)
│   ├── __init__.py
│   ├── use_handler.py            # USE_ITEM
│   ├── consumption_handler.py    # EAT_ITEM, DRINK_ITEM, CONSUME_ITEM
│   ├── equipment_handler.py       # EQUIP_ITEM, UNEQUIP_ITEM
│   └── inventory_handler.py       # DROP_ITEM
│
├── object_interactions/           # 오브젝트 상호작용 (기존)
│   ├── __init__.py
│   ├── object_interaction_base.py
│   ├── information.py
│   ├── state_change.py
│   ├── position.py
│   ├── recovery.py
│   ├── consumption.py
│   ├── learning.py
│   ├── item_manipulation.py
│   ├── crafting.py
│   └── destruction.py
│
└── time_interactions/             # 시간 상호작용
    ├── __init__.py
    └── wait_handler.py            # WAIT
```

### 4.2 베이스 클래스 구조

```python
# app/handlers/action_handler_base.py
class ActionHandlerBase(ABC):
    """액션 핸들러 베이스 클래스"""
    
    def __init__(
        self,
        db_connection: DatabaseConnection,
        entity_manager: Optional[EntityManager] = None,
        cell_manager: Optional[CellManager] = None,
        inventory_manager: Optional[InventoryManager] = None,
        object_state_manager: Optional[ObjectStateManager] = None,
        effect_carrier_manager: Optional[EffectCarrierManager] = None,
        time_system: Optional[TimeSystem] = None,
    ):
        self.db = db_connection
        self.entity_manager = entity_manager
        self.cell_manager = cell_manager
        self.inventory_manager = inventory_manager
        self.object_state_manager = object_state_manager
        self.effect_carrier_manager = effect_carrier_manager
        self.time_system = time_system
        self.logger = logger
    
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

## 5. 구현 상세

### 5.1 Object Interactions 미구현 사항

#### 5.1.1 consumption.py - handle_eat
```python
async def handle_eat(...) -> ActionResult:
    """오브젝트에서 음식 먹기"""
    # 1. 오브젝트 상태 조회
    # 2. contents에서 아이템 ID 추출
    # 3. 아이템 템플릿 조회 (효과 확인)
    # 4. HP/MP 회복
    # 5. EffectCarrier 적용
    # 6. 오브젝트에서 아이템 제거
    # 7. TimeSystem 연동
```

#### 5.1.2 crafting.py - handle_combine, handle_craft, handle_cook
```python
async def handle_combine(...) -> ActionResult:
    """오브젝트와 아이템 조합하기"""
    # 1. 재료 확인 (인벤토리 + 오브젝트 contents)
    # 2. 조합 레시피 확인
    # 3. 결과 아이템 생성
    # 4. 재료 소모
    # 5. TimeSystem 연동

async def handle_craft(...) -> ActionResult:
    """오브젝트에서 제작하기"""
    # 1. 재료 확인
    # 2. 제작 레시피 확인
    # 3. 결과 아이템 생성
    # 4. 재료 소모
    # 5. TimeSystem 연동

async def handle_cook(...) -> ActionResult:
    """오브젝트에서 요리하기"""
    # 1. 재료 확인
    # 2. 요리 레시피 확인
    # 3. 음식 아이템 생성
    # 4. 재료 소모
    # 5. TimeSystem 연동
```

#### 5.1.3 destruction.py - handle_dismantle
```python
async def handle_dismantle(...) -> ActionResult:
    """오브젝트 분해하기"""
    # 1. 오브젝트 타입 확인
    # 2. 분해 레시피 확인
    # 3. 부품 아이템 생성
    # 4. 오브젝트 제거 또는 상태 변경
    # 5. TimeSystem 연동
```

#### 5.1.4 TimeSystem 연동
```python
# 모든 시간 소모 액션에 추가
if self.time_system:
    time_cost = config.get('time_cost', 0)
    if time_cost > 0:
        await self.time_system.advance_time(minutes=time_cost)
```

#### 5.1.5 EffectCarrierManager 연동
```python
# 모든 효과 적용 액션에 추가
if effect_carrier_id and self.effect_carrier_manager:
    await self.effect_carrier_manager.grant_effect_to_entity(
        entity_id=entity_id,
        effect_carrier_id=effect_carrier_id
    )
```

### 5.2 Item Interactions 구현

#### 5.2.1 consumption_handler.py
```python
class ConsumptionItemHandler(ActionHandlerBase):
    """인벤토리 아이템 소비 핸들러"""
    
    async def handle_eat_item(...) -> ActionResult:
        """인벤토리에서 아이템 먹기"""
        # 1. 인벤토리에서 아이템 확인
        # 2. 아이템 템플릿 조회
        # 3. HP/MP 회복
        # 4. EffectCarrier 적용
        # 5. 인벤토리에서 아이템 제거
        # 6. TimeSystem 연동
    
    async def handle_drink_item(...) -> ActionResult:
        """인벤토리에서 아이템 마시기"""
        # 동일한 로직
    
    async def handle_consume_item(...) -> ActionResult:
        """인벤토리에서 아이템 소비"""
        # 동일한 로직
```

#### 5.2.2 equipment_handler.py
```python
class EquipmentItemHandler(ActionHandlerBase):
    """아이템 장착 핸들러"""
    
    async def handle_equip_item(...) -> ActionResult:
        """아이템 장착"""
        # 1. 인벤토리에서 아이템 확인
        # 2. 장착 가능 여부 확인
        # 3. 기존 장착 아이템 해제 (있으면)
        # 4. 아이템 장착
        # 5. 인벤토리에서 제거, 장착 슬롯에 추가
    
    async def handle_unequip_item(...) -> ActionResult:
        """아이템 해제"""
        # 1. 장착 슬롯에서 아이템 확인
        # 2. 인벤토리에 추가
        # 3. 장착 슬롯에서 제거
```

#### 5.2.3 inventory_handler.py
```python
class InventoryItemHandler(ActionHandlerBase):
    """인벤토리 관리 핸들러"""
    
    async def handle_drop_item(...) -> ActionResult:
        """아이템 버리기"""
        # 1. 인벤토리에서 아이템 확인
        # 2. 현재 셀 조회
        # 3. 셀에 아이템 추가 (오브젝트 생성 또는 contents에 추가)
        # 4. 인벤토리에서 제거
```

### 5.3 Entity Interactions 구현

#### 5.3.1 dialogue_handler.py
```python
class DialogueHandler(ActionHandlerBase):
    """대화 핸들러"""
    
    async def handle(...) -> ActionResult:
        """NPC와 대화"""
        # 기존 handle_dialogue 로직 이동
        # DialogueManager 연동 (필요시)
```

#### 5.3.2 trade_handler.py
```python
class TradeHandler(ActionHandlerBase):
    """거래 핸들러"""
    
    async def handle(...) -> ActionResult:
        """NPC와 거래"""
        # 기존 handle_trade 로직 이동
        # TradeManager 연동 (필요시)
```

#### 5.3.3 combat_handler.py
```python
class CombatHandler(ActionHandlerBase):
    """전투 핸들러"""
    
    async def handle(...) -> ActionResult:
        """엔티티 공격"""
        # 기존 handle_attack 로직 이동
        # CombatManager 연동 (필요시)
```

### 5.4 Cell Interactions 구현

#### 5.4.1 investigation_handler.py
```python
class InvestigationHandler(ActionHandlerBase):
    """조사 핸들러"""
    
    async def handle(...) -> ActionResult:
        """셀 조사"""
        # 기존 handle_investigate 로직 이동
```

#### 5.4.2 visit_handler.py
```python
class VisitHandler(ActionHandlerBase):
    """방문 핸들러"""
    
    async def handle(...) -> ActionResult:
        """셀 방문"""
        # 기존 handle_visit 로직 이동
```

#### 5.4.3 movement_handler.py
```python
class MovementHandler(ActionHandlerBase):
    """이동 핸들러"""
    
    async def handle(...) -> ActionResult:
        """셀 이동"""
        # 기존 handle_move 로직 이동
        # 충돌 검사, 경로 찾기 등 추가 가능
```

### 5.5 Time Interactions 구현

#### 5.5.1 wait_handler.py
```python
class WaitHandler(ActionHandlerBase):
    """대기 핸들러"""
    
    async def handle(...) -> ActionResult:
        """시간 대기"""
        # 기존 handle_wait 로직 이동
        # TimeSystem 연동
```

---

## 6. 테스트 계획

### 6.1 단위 테스트

#### Object Interactions
- [ ] `handle_eat` 테스트
- [ ] `handle_combine` 테스트
- [ ] `handle_craft` 테스트
- [ ] `handle_cook` 테스트
- [ ] `handle_dismantle` 테스트
- [ ] TimeSystem 연동 테스트
- [ ] EffectCarrierManager 연동 테스트

#### Item Interactions
- [ ] `handle_eat_item` 테스트
- [ ] `handle_drink_item` 테스트
- [ ] `handle_equip_item` 테스트
- [ ] `handle_unequip_item` 테스트
- [ ] `handle_drop_item` 테스트

#### Entity Interactions
- [ ] `handle_dialogue` 테스트
- [ ] `handle_trade` 테스트
- [ ] `handle_attack` 테스트

#### Cell Interactions
- [ ] `handle_investigate` 테스트
- [ ] `handle_visit` 테스트
- [ ] `handle_move` 테스트

#### Time Interactions
- [ ] `handle_wait` 테스트

### 6.2 통합 테스트

- [ ] ActionHandler 라우터 테스트
- [ ] 전체 액션 플로우 테스트
- [ ] API 엔드포인트 통합 테스트
- [ ] 프론트엔드 연동 테스트

---

## 7. API 업데이트

### 7.1 기존 API 엔드포인트

현재 `app/ui/backend/routes/gameplay.py`에 있는 엔드포인트:
- `POST /api/gameplay/start`: 새 게임 시작
- `GET /api/gameplay/cell/{session_id}`: 현재 셀 정보 조회
- `POST /api/gameplay/interact/object`: 오브젝트 상호작용
- `GET /api/gameplay/actions/{session_id}`: 사용 가능한 액션 조회

### 7.2 업데이트 필요 사항

- [ ] `/api/gameplay/interact/object` 엔드포인트 업데이트
  - 새로운 액션 타입 지원
  - ActionHandler 라우터 사용하도록 업데이트
- [ ] 새로운 엔드포인트 추가
  - `POST /api/gameplay/interact/item`: 아이템 상호작용 (신규)
  - `POST /api/gameplay/interact/entity`: 엔티티 상호작용 (신규)
  - `POST /api/gameplay/action`: 범용 액션 실행 (기존 또는 신규)
- [ ] `GET /api/gameplay/actions/{session_id}` 업데이트
  - 새로운 액션 타입 포함
  - Item Interactions 액션 추가
- [ ] API 문서 업데이트

---

## 8. 프론트엔드 연동

### 8.1 프론트엔드 액션 호출

- [ ] 새로운 액션 타입 UI 추가
- [ ] Item Interactions UI 추가
- [ ] 액션 결과 처리 업데이트
- [ ] 에러 처리 및 피드백

### 8.2 UI 컴포넌트

- [ ] 아이템 상호작용 UI
  - 인벤토리에서 아이템 먹기/마시기
  - 아이템 장착/해제
  - 아이템 버리기
- [ ] 엔티티 상호작용 UI
  - 대화 UI
  - 거래 UI
  - 전투 UI

---

## 9. 체크리스트

### Phase 1: 디렉토리 구조 변경
- [ ] `app/handlers/entity_interactions/` 생성
- [ ] `app/handlers/cell_interactions/` 생성
- [ ] `app/handlers/item_interactions/` 생성
- [ ] `app/handlers/time_interactions/` 생성
- [ ] `app/handlers/action_handler_base.py` 생성

### Phase 2: 필요한 모듈 생성
- [ ] 베이스 클래스 구현
- [ ] Entity Interactions 핸들러 모듈 생성
- [ ] Cell Interactions 핸들러 모듈 생성
- [ ] Item Interactions 핸들러 모듈 생성
- [ ] Time Interactions 핸들러 모듈 생성

### Phase 3: 미구현 사항 포함 모듈 구현
- [ ] Object Interactions 미구현 사항 구현
- [ ] Item Interactions 구현
- [ ] Entity Interactions 구현
- [ ] Cell Interactions 구현
- [ ] Time Interactions 구현

### Phase 4: ActionHandler 리팩토링
- [ ] ActionHandler를 라우터로 변경
- [ ] 핸들러 매핑 업데이트

### Phase 5: 단위 테스트
- [ ] 모든 핸들러 단위 테스트 작성

### Phase 6: 통합 테스트
- [ ] 통합 테스트 작성

### Phase 7: API 제작
- [ ] API 엔드포인트 업데이트
- [ ] API 문서 업데이트

### Phase 8: 프론트엔드 연결
- [ ] 프론트엔드 액션 호출 업데이트
- [ ] UI 컴포넌트 추가

---

## 10. 우선순위

1. **최우선**: Item Interactions 구현 (Ownership 설계와 직접 연관)
2. **높음**: Object Interactions 미구현 사항 구현
3. **중간**: Entity Interactions 구현
4. **중간**: Cell Interactions 구현
5. **낮음**: Time Interactions 구현

---

## 11. 예상 소요 시간

- Phase 1-2: 디렉토리 구조 및 모듈 생성 (2-3시간)
- Phase 3: 미구현 사항 구현 (8-10시간)
- Phase 4: ActionHandler 리팩토링 (2-3시간)
- Phase 5-6: 테스트 작성 (4-6시간)
- Phase 7-8: API 및 프론트엔드 연동 (3-4시간)

**총 예상 시간**: 19-26시간

