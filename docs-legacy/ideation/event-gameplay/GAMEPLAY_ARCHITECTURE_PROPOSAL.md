# 실제 게임플레이를 위한 아키텍처 제안

**작성 일자**: 2025-12-28  
**최신화 날짜**: 2025-12-28

## 🎯 문제 분석

### 현재 상태
- ✅ **Manager 클래스들**: EntityManager, CellManager, DialogueManager, ActionHandler
- ✅ **Repository 패턴**: 데이터 접근 계층 분리
- ✅ **의존성 주입**: Manager 클래스들이 Repository를 주입받음
- ❌ **게임 루프 없음**: 게임 상태를 지속적으로 업데이트하는 메커니즘이 없음
- ❌ **이벤트 시스템 없음**: 플레이어 액션과 NPC 행동을 조율하는 시스템이 없음
- ❌ **게임플레이 오케스트레이션 없음**: 플레이어 액션 → 게임 상태 업데이트 → NPC 반응의 흐름이 없음

### 필요한 기능
1. **플레이어 액션 처리**: 셀 진입, 이동, 대화, 상호작용
2. **NPC 자동 행동**: NPC가 스케줄에 따라 자동으로 행동
3. **게임 루프**: 게임 상태를 지속적으로 업데이트
4. **이벤트 시스템**: 액션과 반응을 연결
5. **상태 동기화**: 모든 엔티티의 상태를 일관되게 관리

---

## 🏗️ 제안하는 아키텍처

### 옵션 1: Game Engine + Event System (권장)

```
app/
├── engine/
│   ├── game_engine.py          # 게임 루프 및 상태 관리
│   ├── event_system.py         # 이벤트 버스 및 이벤트 처리
│   └── session_controller.py   # 세션 생명주기 관리
│
├── gameplay/
│   ├── player_controller.py    # 플레이어 액션 처리
│   ├── npc_controller.py       # NPC 자동 행동 처리
│   └── interaction_orchestrator.py  # 상호작용 오케스트레이션
│
├── managers/                    # 기존 유지
│   ├── entity_manager.py
│   ├── cell_manager.py
│   └── ...
│
└── handlers/                   # 기존 유지
    └── action_handler.py
```

**장점**:
- 게임 로직과 데이터 접근 계층 분리
- 이벤트 기반으로 느슨한 결합
- 테스트 용이
- 확장 가능

**단점**:
- 초기 구현 비용
- 이벤트 시스템 복잡도

---

### 옵션 2: Game Session 중심 (단순)

```
app/
├── core/
│   └── game_session.py         # 확장 (게임 루프 추가)
│
├── managers/                   # 기존 유지
│   └── ...
│
└── systems/
    └── npc_behavior.py         # 확장 (자동 행동 추가)
```

**장점**:
- 기존 코드 재사용
- 단순함
- 빠른 구현

**단점**:
- GameSession이 너무 많은 책임
- 확장성 제한
- 테스트 어려움

---

### 옵션 3: Service Layer 추가 (균형)

```
app/
├── services/
│   ├── gameplay_service.py     # 게임플레이 로직
│   ├── player_service.py       # 플레이어 액션 처리
│   └── npc_service.py          # NPC 자동 행동
│
├── engine/
│   └── game_engine.py          # 게임 루프
│
└── managers/                   # 기존 유지
    └── ...
```

**장점**:
- 비즈니스 로직과 데이터 접근 분리
- Manager는 데이터 CRUD만 담당
- Service는 게임플레이 로직 담당
- 확장 가능

**단점**:
- 추가 레이어
- Service와 Manager 역할 구분 필요

---

## 💡 최종 권장: 옵션 1 (Game Engine + Event System)

### 구조 상세

#### 1. Game Engine (`app/engine/game_engine.py`)
```python
class GameEngine:
    """게임 엔진 - 게임 루프 및 상태 관리"""
    
    def __init__(self,
                 entity_manager: EntityManager,
                 cell_manager: CellManager,
                 dialogue_manager: DialogueManager,
                 action_handler: ActionHandler,
                 event_bus: EventBus):
        self.entity_manager = entity_manager
        self.cell_manager = cell_manager
        self.dialogue_manager = dialogue_manager
        self.action_handler = action_handler
        self.event_bus = event_bus
        
        self.is_running = False
        self.current_session_id: Optional[str] = None
        self.tick_rate = 60  # 60 FPS
    
    async def start_game(self, session_id: str):
        """게임 시작"""
        self.current_session_id = session_id
        self.is_running = True
        await self.game_loop()
    
    async def game_loop(self):
        """게임 루프"""
        while self.is_running:
            start_time = time.time()
            
            # 1. 플레이어 액션 처리
            await self.process_player_actions()
            
            # 2. NPC 자동 행동 처리
            await self.process_npc_behaviors()
            
            # 3. 게임 상태 업데이트
            await self.update_game_state()
            
            # 4. 이벤트 처리
            await self.event_bus.process_events()
            
            # 5. 프레임 레이트 조절
            elapsed = time.time() - start_time
            sleep_time = (1.0 / self.tick_rate) - elapsed
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
    
    async def process_player_actions(self):
        """플레이어 액션 처리"""
        # 플레이어 액션 큐에서 액션 가져와서 처리
        ...
    
    async def process_npc_behaviors(self):
        """NPC 자동 행동 처리"""
        # NPC 스케줄에 따라 자동 행동 실행
        ...
    
    async def update_game_state(self):
        """게임 상태 업데이트"""
        # 시간 경과, 상태 변화 등 처리
        ...
```

#### 2. Event System (`app/engine/event_system.py`)
```python
class EventBus:
    """이벤트 버스 - 이벤트 기반 통신"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue()
    
    def subscribe(self, event_type: str, handler: Callable):
        """이벤트 구독"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
    
    async def publish(self, event: GameEvent):
        """이벤트 발행"""
        await self.event_queue.put(event)
    
    async def process_events(self):
        """이벤트 처리"""
        while not self.event_queue.empty():
            event = await self.event_queue.get()
            handlers = self.subscribers.get(event.event_type, [])
            for handler in handlers:
                await handler(event)

class GameEvent:
    """게임 이벤트"""
    event_type: str
    session_id: str
    source_entity_id: Optional[str]
    target_entity_id: Optional[str]
    data: Dict[str, Any]
    timestamp: datetime
```

#### 3. Player Controller (`app/gameplay/player_controller.py`)
```python
class PlayerController:
    """플레이어 액션 처리"""
    
    def __init__(self,
                 game_engine: GameEngine,
                 entity_manager: EntityManager,
                 cell_manager: CellManager,
                 action_handler: ActionHandler,
                 event_bus: EventBus):
        self.game_engine = game_engine
        self.entity_manager = entity_manager
        self.cell_manager = cell_manager
        self.action_handler = action_handler
        self.event_bus = event_bus
    
    async def enter_cell(self, player_id: str, cell_id: str):
        """플레이어가 셀에 진입"""
        # 1. 셀 진입 처리
        result = await self.cell_manager.enter_cell(cell_id, player_id)
        
        # 2. 이벤트 발행
        await self.event_bus.publish(GameEvent(
            event_type="CELL_ENTERED",
            session_id=self.game_engine.current_session_id,
            source_entity_id=player_id,
            target_entity_id=cell_id,
            data={"cell_id": cell_id}
        ))
        
        return result
    
    async def move_player(self, player_id: str, target_cell_id: str, position: Dict[str, float]):
        """플레이어 이동"""
        # 1. 이동 처리
        result = await self.cell_manager.move_entity_between_cells(
            player_id, current_cell_id, target_cell_id
        )
        
        # 2. 이벤트 발행
        await self.event_bus.publish(GameEvent(
            event_type="PLAYER_MOVED",
            session_id=self.game_engine.current_session_id,
            source_entity_id=player_id,
            data={"target_cell_id": target_cell_id, "position": position}
        ))
        
        return result
    
    async def start_dialogue(self, player_id: str, npc_id: str):
        """대화 시작"""
        # 1. 대화 시작
        result = await self.dialogue_manager.start_dialogue(
            player_id, npc_id, self.game_engine.current_session_id
        )
        
        # 2. 이벤트 발행
        await self.event_bus.publish(GameEvent(
            event_type="DIALOGUE_STARTED",
            session_id=self.game_engine.current_session_id,
            source_entity_id=player_id,
            target_entity_id=npc_id,
            data={"dialogue_id": result.dialogue_id}
        ))
        
        return result
    
    async def interact_with_entity(self, player_id: str, target_id: str, action_type: str):
        """엔티티와 상호작용"""
        # 1. 액션 처리
        result = await self.action_handler.execute_action(
            action_type=action_type,
            entity_id=player_id,
            target_id=target_id,
            session_id=self.game_engine.current_session_id
        )
        
        # 2. 이벤트 발행
        await self.event_bus.publish(GameEvent(
            event_type="INTERACTION",
            session_id=self.game_engine.current_session_id,
            source_entity_id=player_id,
            target_entity_id=target_id,
            data={"action_type": action_type, "result": result}
        ))
        
        return result
```

#### 4. NPC Controller (`app/gameplay/npc_controller.py`)
```python
class NPCController:
    """NPC 자동 행동 처리"""
    
    def __init__(self,
                 game_engine: GameEngine,
                 entity_manager: EntityManager,
                 cell_manager: CellManager,
                 event_bus: EventBus):
        self.game_engine = game_engine
        self.entity_manager = entity_manager
        self.cell_manager = cell_manager
        self.event_bus = event_bus
    
    async def process_npc_routines(self):
        """NPC 루틴 처리"""
        # 현재 세션의 모든 NPC 조회
        npcs = await self.get_active_npcs()
        
        for npc in npcs:
            # NPC의 행동 스케줄 확인
            schedule = await self.get_npc_schedule(npc['entity_id'])
            
            # 현재 시간에 맞는 행동 실행
            current_time = await self.get_game_time()
            action = self.get_scheduled_action(schedule, current_time)
            
            if action:
                await self.execute_npc_action(npc, action)
    
    async def execute_npc_action(self, npc: Dict[str, Any], action: Dict[str, Any]):
        """NPC 액션 실행"""
        action_type = action['type']
        
        if action_type == 'move':
            await self.npc_move(npc, action['target_cell_id'])
        elif action_type == 'dialogue':
            await self.npc_dialogue(npc, action['target_entity_id'])
        elif action_type == 'work':
            await self.npc_work(npc, action['work_type'])
        # ...
        
        # 이벤트 발행
        await self.event_bus.publish(GameEvent(
            event_type="NPC_ACTION",
            session_id=self.game_engine.current_session_id,
            source_entity_id=npc['entity_id'],
            data={"action": action}
        ))
```

#### 5. Interaction Orchestrator (`app/gameplay/interaction_orchestrator.py`)
```python
class InteractionOrchestrator:
    """상호작용 오케스트레이션"""
    
    def __init__(self,
                 player_controller: PlayerController,
                 npc_controller: NPCController,
                 event_bus: EventBus):
        self.player_controller = player_controller
        self.npc_controller = npc_controller
        self.event_bus = event_bus
        
        # 이벤트 구독
        self.event_bus.subscribe("CELL_ENTERED", self.on_cell_entered)
        self.event_bus.subscribe("PLAYER_MOVED", self.on_player_moved)
        self.event_bus.subscribe("DIALOGUE_STARTED", self.on_dialogue_started)
    
    async def on_cell_entered(self, event: GameEvent):
        """셀 진입 이벤트 처리"""
        # 셀에 있는 NPC들이 플레이어를 인식
        cell_id = event.target_entity_id
        npcs = await self.get_npcs_in_cell(cell_id)
        
        for npc in npcs:
            # NPC가 플레이어를 인식하면 반응
            if npc['behavior_type'] == 'greeting':
                await self.npc_greet_player(npc['entity_id'], event.source_entity_id)
    
    async def on_player_moved(self, event: GameEvent):
        """플레이어 이동 이벤트 처리"""
        # 이동한 셀의 NPC들이 반응
        ...
    
    async def on_dialogue_started(self, event: GameEvent):
        """대화 시작 이벤트 처리"""
        # 대화 관련 상태 업데이트
        ...
```

---

## 🔄 게임플레이 플로우

### 플레이어 액션 플로우
```
1. 플레이어 입력 (UI/CLI/API)
   ↓
2. PlayerController.enter_cell() / move_player() / start_dialogue()
   ↓
3. Manager 클래스 호출 (EntityManager, CellManager, DialogueManager)
   ↓
4. 이벤트 발행 (EventBus.publish())
   ↓
5. InteractionOrchestrator가 이벤트 수신하여 반응 처리
   ↓
6. 게임 상태 업데이트
```

### NPC 자동 행동 플로우
```
1. GameEngine.game_loop() → process_npc_behaviors()
   ↓
2. NPCController.process_npc_routines()
   ↓
3. NPC 스케줄 확인 및 액션 실행
   ↓
4. 이벤트 발행
   ↓
5. 다른 엔티티들이 반응 (선택적)
```

### 게임 루프 플로우
```
GameEngine.game_loop():
  while is_running:
    1. process_player_actions()      # 플레이어 액션 처리
    2. process_npc_behaviors()       # NPC 자동 행동
    3. update_game_state()           # 게임 상태 업데이트 (시간, 날씨 등)
    4. event_bus.process_events()     # 이벤트 처리
    5. sleep(1/60)                    # 60 FPS
```

---

## 📊 비교 분석

### 현재 구조
```
UI → GameManager → Managers → Repositories → Database
```
**문제점**:
- 게임 루프 없음
- NPC 자동 행동 없음
- 이벤트 시스템 없음
- 플레이어 액션과 NPC 반응 연결 안 됨

### 제안하는 구조
```
GameEngine (게임 루프)
  ├── PlayerController (플레이어 액션)
  │   └── Managers (데이터 접근)
  ├── NPCController (NPC 자동 행동)
  │   └── Managers (데이터 접근)
  └── EventBus (이벤트 시스템)
      └── InteractionOrchestrator (반응 처리)
```
**장점**:
- 게임 루프로 지속적인 상태 업데이트
- NPC 자동 행동
- 이벤트 기반 느슨한 결합
- 확장 가능

---

## ✅ 구현 계획

### Phase 1: 핵심 구조
1. `app/engine/game_engine.py` - 게임 루프
2. `app/engine/event_system.py` - 이벤트 버스
3. `app/gameplay/player_controller.py` - 플레이어 액션 처리

### Phase 2: NPC 시스템
4. `app/gameplay/npc_controller.py` - NPC 자동 행동
5. `app/gameplay/interaction_orchestrator.py` - 상호작용 오케스트레이션

### Phase 3: 통합 및 테스트
6. Manager 클래스와 통합
7. 테스트 작성
8. 성능 최적화

---

## 🎯 결론

**권장 구조**: **옵션 1 (Game Engine + Event System)**

**이유**:
1. 게임 루프로 지속적인 상태 업데이트 가능
2. 이벤트 시스템으로 느슨한 결합
3. 플레이어 액션과 NPC 반응을 자연스럽게 연결
4. 확장 가능하고 테스트 용이
5. Manager 클래스는 그대로 유지 (데이터 접근 계층)

**핵심 원칙**:
- Manager: 데이터 CRUD만 담당
- Gameplay Layer: 게임플레이 로직 담당
- Event System: 컴포넌트 간 통신
- Game Engine: 전체 오케스트레이션

