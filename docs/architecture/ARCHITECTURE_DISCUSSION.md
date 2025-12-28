# 아키텍처 토론 문서

**작성일**: 2025-12-28  
**목적**: 오브젝트 상호작용 아키텍처에 대한 심층 토론

---

## 토론 포인트

### 1. Factory 패턴과 JSONB 속성 관리

#### 질문
> Object는 JSONB로 복잡한 속성들을 관리하니 Factory 패턴이 적합하지 않나요?

#### 현재 상황 분석

**Factory의 현재 사용**:
- `GameDataFactory.create_world_object()`: 정적 게임 데이터 생성
  - `properties` (JSONB)를 받아서 저장
  - 복잡한 속성 구조를 단순화하여 생성
- `InstanceFactory.create_npc_instance()`: 런타임 인스턴스 생성
  - 템플릿에서 속성 복사 및 커스터마이징

**Factory 패턴의 목적**:
- 복잡한 객체 생성 로직 캡슐화
- 생성 과정의 복잡성을 숨기고 단순한 인터페이스 제공
- 생성 로직의 변경이 사용자 코드에 영향을 주지 않도록 분리

#### 분석: Factory vs Manager vs Builder

| 패턴 | 목적 | 사용 시점 | 예시 |
|------|------|-----------|------|
| **Factory** | 객체 생성 | 데이터 생성 시 | `GameDataFactory.create_world_object()` |
| **Manager** | 상태 관리 | 런타임 상태 조회/변경 | `ObjectStateManager.get_object_state()` |
| **Builder** | 복잡한 객체 구성 | 단계별 속성 설정 | `ObjectPropertiesBuilder` (없음) |
| **Handler** | 행동 실행 | 게임 로직 실행 | `ActionHandler.execute_action()` |

#### 결론: Factory는 적합하지만 목적이 다름

**✅ Factory 패턴은 이미 사용 중**:
- `GameDataFactory.create_world_object()`: 오브젝트 생성 시 복잡한 JSONB properties 처리
- `InstanceFactory.create_item_instance()`: 런타임 인스턴스 생성 시 properties 커스터마이징

**하지만 상호작용 실행은 Factory가 아님**:
- 상호작용은 "행동 실행"이지 "객체 생성"이 아님
- Factory는 데이터 생성에 사용, Handler는 행동 실행에 사용

**제안: Builder 패턴 추가 (선택사항)**

복잡한 JSONB properties를 단계별로 구성하고 싶다면:

```python
# app/builders/object_properties_builder.py
class ObjectPropertiesBuilder:
    """오브젝트 properties 빌더"""
    
    def __init__(self):
        self.properties = {}
    
    def set_interaction_type(self, interaction_type: str):
        self.properties['interaction_type'] = interaction_type
        return self
    
    def add_interaction(self, interaction_name: str, config: Dict[str, Any]):
        if 'interactions' not in self.properties:
            self.properties['interactions'] = {}
        self.properties['interactions'][interaction_name] = config
        return self
    
    def set_contents(self, contents: List[str]):
        self.properties['contents'] = contents
        return self
    
    def build(self) -> Dict[str, Any]:
        return self.properties.copy()

# 사용 예시
properties = (ObjectPropertiesBuilder()
    .set_interaction_type("restable")
    .add_interaction("rest", {
        "effects": {"hp": 50, "mp": 30},
        "time_cost": 30,
        "state_change": "rested"
    })
    .set_contents(["ITEM_PAPER_001"])
    .build())
```

**하지만 현재는 불필요**:
- JSONB는 이미 Dict로 직접 구성 가능
- Factory가 이미 properties를 받아서 처리
- Builder 패턴은 properties가 매우 복잡하고 단계별 구성이 필요할 때만 유용

---

### 2. Handler가 Action만 있는 이유

#### 질문
> Handler가 현재 action 밖에 없는데 이렇게 된 이유는 무엇이라고 생각하나요?

#### 현재 구조 분석

**현재 Handler 구조**:
```
app/handlers/
└── action_handler.py  # ActionHandler만 존재
```

**인터페이스**:
```
app/interfaces/
└── handlers.py  # IActionHandler 인터페이스만 정의
```

**ActionHandler의 역할**:
- 플레이어 행동 처리 (investigate, dialogue, trade, visit, wait, move, attack, use_item)
- Manager들을 조합하여 사용
- 행동 로그 기록

#### 분석: 왜 Action만 있는가?

**1. 게임 로직의 본질**
- RPG 게임의 핵심은 "플레이어 행동"
- 모든 게임 로직이 "행동"으로 표현 가능
- 예: 이동, 대화, 거래, 조사, 공격, 아이템 사용

**2. 현재 아키텍처의 철학**
- **Manager**: 도메인별 상태 관리 (Entity, Cell, Inventory)
- **Handler**: 게임 행동 실행 (Action)
- **Service**: 특정 기능 제공 (Collision, Search)

**3. 다른 Handler가 필요한가?**

**가능한 Handler 타입들**:
- `EventHandler`: 이벤트 처리 (예: 퀘스트 이벤트, 스크립트 이벤트)
- `CommandHandler`: 명령 처리 (예: 관리자 명령, 치트)
- `InteractionHandler`: 상호작용 처리 (오브젝트 상호작용)
- `QuestHandler`: 퀘스트 처리
- `CombatHandler`: 전투 처리

**하지만 현재는 Action으로 충분**:
- 모든 행동이 `ActionType`으로 표현 가능
- `ActionHandler`가 모든 행동을 처리
- 추가 Handler는 관심사 분리가 필요할 때만 생성

#### 결론: Action 중심 설계가 의도적

**이유**:
1. **단순성**: 모든 게임 로직을 Action으로 통일
2. **일관성**: 모든 행동이 동일한 인터페이스 (`execute_action`)
3. **확장성**: 새로운 행동은 `ActionType` 추가로 해결

**다른 Handler가 필요한 시점**:
- ActionHandler가 너무 커질 때 (1000줄 이상)
- 관심사가 명확히 분리될 때 (예: 전투 로직이 매우 복잡해질 때)
- 다른 추상화 레벨이 필요할 때 (예: 이벤트 시스템)

---

### 3. 더 추상화된 개념의 부재

#### 질문
> Manager들을 모아서 처리해야할 더 추상화된 개념이 action 밖에 아직 기획된게 없어서 그럴까요?

#### 현재 구조 분석

**현재 추상화 레벨**:
```
API Layer (FastAPI Routes)
    ↓
Handler Layer (ActionHandler)
    ↓
Manager Layer (EntityManager, CellManager, InventoryManager, ...)
    ↓
Repository Layer (GameDataRepository, RuntimeDataRepository, ...)
    ↓
Database Layer
```

**ActionHandler의 역할**:
- 여러 Manager를 조합
- 행동 실행 로직
- 행동 로그 기록

#### 분석: 더 추상화된 개념이 필요한가?

**현재 ActionHandler가 하는 일**:
```python
async def handle_investigate(self, entity_id, target_id, parameters):
    # 1. EntityManager로 플레이어 조회
    player_result = await self.entity_manager.get_entity(entity_id)
    
    # 2. CellManager로 셀 조회
    cell_result = await self.cell_manager.get_cell(current_cell_id)
    
    # 3. CellManager로 컨텐츠 로드
    content_result = await self.cell_manager.load_cell_content(current_cell_id)
    
    # 4. 결과 생성 및 반환
    return ActionResult.success_result(...)
```

**더 추상화된 개념 예시**:

#### 옵션 A: UseCase/Service 패턴
```python
# app/usecases/investigate_usecase.py
class InvestigateUseCase:
    """조사 UseCase"""
    
    def __init__(self, entity_manager, cell_manager):
        self.entity_manager = entity_manager
        self.cell_manager = cell_manager
    
    async def execute(self, entity_id: str, cell_id: str) -> InvestigationResult:
        # 조사 로직
        pass

# ActionHandler에서 사용
class ActionHandler:
    async def handle_investigate(self, ...):
        use_case = InvestigateUseCase(self.entity_manager, self.cell_manager)
        return await use_case.execute(entity_id, cell_id)
```

**장점**:
- ✅ 관심사 분리
- ✅ 테스트 용이
- ✅ 재사용 가능

**단점**:
- ⚠️ 현재는 ActionHandler가 이미 충분히 작음
- ⚠️ 추가 계층으로 인한 복잡성 증가

#### 옵션 B: Command 패턴
```python
# app/commands/investigate_command.py
class InvestigateCommand:
    """조사 명령"""
    
    async def execute(self, context: GameContext) -> ActionResult:
        # 조사 로직
        pass

# CommandHandler
class CommandHandler:
    async def execute_command(self, command: Command):
        return await command.execute(self.context)
```

**장점**:
- ✅ 명령의 실행/취소 가능
- ✅ 명령 히스토리 관리
- ✅ 비동기 처리 용이

**단점**:
- ⚠️ 현재는 단순 실행만 필요
- ⚠️ 취소/재실행 기능이 없음

#### 옵션 C: Event-Driven 아키텍처
```python
# app/events/investigation_completed_event.py
class InvestigationCompletedEvent:
    entity_id: str
    cell_id: str
    findings: List[str]

# EventHandler
class EventHandler:
    async def handle_event(self, event: Event):
        # 이벤트 처리
        pass
```

**장점**:
- ✅ 느슨한 결합
- ✅ 확장성 (여러 핸들러가 같은 이벤트 처리)
- ✅ 비동기 처리

**단점**:
- ⚠️ 현재는 동기 처리로 충분
- ⚠️ 복잡성 증가

#### 결론: 현재는 Action으로 충분

**이유**:
1. **현재 복잡도**: ActionHandler가 600줄 정도로 적절한 크기
2. **명확한 책임**: 행동 실행만 담당
3. **확장 가능**: 새로운 행동은 `ActionType` 추가로 해결

**더 추상화된 개념이 필요한 시점**:
- ActionHandler가 2000줄 이상이 될 때
- 행동 간 공통 로직이 많아질 때
- 행동 실행 흐름이 복잡해질 때 (예: 조건부 실행, 파이프라인)
- 행동의 실행/취소가 필요할 때
- 이벤트 기반 아키텍처가 필요할 때

---

## 종합 의견

### 1. Factory 패턴과 JSONB

**결론**: Factory는 이미 사용 중이지만, 목적이 다름
- ✅ **오브젝트 생성**: `GameDataFactory` 사용 (이미 구현됨)
- ✅ **인스턴스 생성**: `InstanceFactory` 사용 (이미 구현됨)
- ❌ **상호작용 실행**: Factory가 아닌 Handler 사용

**제안**: 
- 복잡한 properties 구성이 필요하면 **Builder 패턴** 고려
- 하지만 현재는 Dict 직접 구성으로 충분

### 2. Handler가 Action만 있는 이유

**결론**: Action 중심 설계가 의도적이고 적절함
- ✅ 모든 게임 로직이 "행동"으로 표현 가능
- ✅ 단순성과 일관성 유지
- ✅ 확장 가능 (새로운 ActionType 추가)

**제안**:
- 현재는 ActionHandler 유지
- 다른 Handler는 관심사 분리가 명확히 필요할 때만 생성
  - 예: 전투 로직이 매우 복잡해지면 `CombatHandler` 분리
  - 예: 이벤트 시스템이 필요하면 `EventHandler` 추가

### 3. 더 추상화된 개념

**결론**: 현재는 Action으로 충분, 필요 시 추가
- ✅ ActionHandler가 적절한 크기 (600줄)
- ✅ 명확한 책임 (행동 실행)
- ✅ Manager 조합이 간단함

**제안**:
- **현재**: ActionHandler 유지
- **미래**: 다음 상황에서 추가 추상화 고려
  1. ActionHandler가 2000줄 이상이 될 때
  2. 행동 간 공통 로직이 많아질 때
  3. 행동 실행 흐름이 복잡해질 때 (파이프라인, 조건부 실행)
  4. 행동의 실행/취소가 필요할 때
  5. 이벤트 기반 아키텍처가 필요할 때

**추가 추상화 옵션**:
- **UseCase 패턴**: 행동별 UseCase 클래스 생성
- **Command 패턴**: 명령 객체로 캡슐화
- **Event-Driven**: 이벤트 기반 아키텍처

---

## 최종 권장사항

### 현재 단계 (MVP)
1. ✅ **ActionHandler 확장**: 오브젝트 상호작용 추가
2. ✅ **ObjectStateManager 생성**: 오브젝트 상태 관리
3. ✅ **EntityManager 확장**: HP/MP 회복 메서드 추가

### 미래 단계 (복잡도 증가 시)
1. **UseCase 패턴 도입**: 행동별 UseCase 클래스 생성
2. **EventHandler 추가**: 이벤트 기반 아키텍처
3. **Command 패턴 도입**: 명령 실행/취소 기능

### 설계 원칙
- **YAGNI (You Aren't Gonna Need It)**: 현재 필요하지 않은 추상화는 추가하지 않음
- **KISS (Keep It Simple, Stupid)**: 단순한 해결책 우선
- **점진적 복잡도 증가**: 필요할 때만 추상화 추가

