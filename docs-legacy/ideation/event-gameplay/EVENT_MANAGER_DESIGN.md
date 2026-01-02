# 이벤트 매니저 설계 문서

## 문서 정보
- **버전**: v2.0
- **작성일**: 2026-01-01
- **최종 수정**: 2026-01-01
- **기반 문서**: `docs/ideation/03_world_tick_guide.md`, `docs/ideation/12_dev_memo.md`

## 개요

이벤트 매니저는 RPG Engine의 핵심 시스템으로, 플레이어가 없어도 세계가 계속 작동하는 백그라운드 이벤트 처리 시스템입니다.

### 핵심 철학

> **"지속적 세계: 플레이어가 없어도 세계는 계속 작동"**

- **백그라운드 진행**: 시간 경과/스케줄 처리 (내부 정치, 재난, 관계 변화)
- **비가시 이벤트**: 로그만 남김 → 플레이어가 나중에 "결과"와 조우
- **결정적 난수**: seed로 재현성 확보
- **오프라인 진행**: 마지막 활동 시각 기반 catch-up

### 설계 목표

1. **플레이어 근처 셀**: 즉시 처리 (실시간 반응)
2. **외부 셀**: 체크포인트 대기 후 배치 처리
3. **백그라운드**: 플레이어 없이도 세계가 작동 (World Tick 시스템)

## 아키텍처 개요

### 시스템 구성

```
┌─────────────────────────────────────┐
│      EventManager (중앙 관리)        │
├─────────────────────────────────────┤
│  - 이벤트 스케줄링                   │
│  - 즉시 처리 vs 체크포인트 분기      │
│  - 백그라운드 이벤트 루프             │
└─────────────────────────────────────┘
           │
           ├─→ WorldTickManager (주기적 실행)
           ├─→ EventScheduler (예약 이벤트)
           ├─→ InvisibleEventManager (비가시 이벤트)
           └─→ OfflineProgressManager (오프라인 진행)
```

### 데이터 흐름

```
이벤트 발생
    ↓
플레이어 근처 셀?
    ├─ YES → 즉시 처리 → 상태 변화 즉시 반영
    └─ NO  → 체크포인트 큐에 저장
                ↓
        플레이어가 셀 접근 시
                ↓
        배치 처리 → 체크포인트 저장
```

## 핵심 컴포넌트

### 1. EventManager

#### 역할
- 이벤트 스케줄링 및 분기 처리
- 플레이어 근처 셀 vs 외부 셀 판단
- 체크포인트 이벤트 관리

#### 구현

```python
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)

class EventType(Enum):
    """이벤트 타입"""
    ENTITY_MOVE = "entity_move"
    ENTITY_ACTION = "entity_action"
    CELL_STATE_CHANGE = "cell_state_change"
    WORLD_EVENT = "world_event"
    BACKGROUND_EVENT = "background_event"
    POLITICAL_CHANGE = "political_change"
    DISASTER = "disaster"
    RELATIONSHIP_CHANGE = "relationship_change"
    ECONOMIC_SHIFT = "economic_shift"
    SEASONAL_EVENT = "seasonal_event"

@dataclass
class GameEvent:
    """게임 이벤트"""
    event_id: str
    event_type: EventType
    cell_id: str
    entity_id: Optional[str]
    data: Dict
    timestamp: datetime
    is_background: bool = False
    session_id: Optional[str] = None

class EventManager:
    """이벤트 관리자"""
    
    def __init__(self, cell_state_manager, db_connection):
        """
        초기화
        
        Args:
            cell_state_manager: CellStateManager 인스턴스
            db_connection: DatabaseConnection 인스턴스
        """
        self.cell_state_manager = cell_state_manager
        self.db = db_connection
        
        # 이벤트 큐
        self.event_queue: List[GameEvent] = []  # 즉시 처리 대기열
        self.checkpoint_events: Dict[str, List[GameEvent]] = {}  # 셀별 체크포인트 이벤트
        
        # 백그라운드 이벤트
        self.background_event_queue: List[GameEvent] = []
        self._running = False
        
        # 하위 매니저
        self.world_tick_manager = None
        self.event_scheduler = None
        self.invisible_event_manager = None
        self.offline_progress_manager = None
    
    async def start(self):
        """이벤트 매니저 시작"""
        self._running = True
        
        # 하위 매니저 초기화
        from app.managers.world_tick_manager import WorldTickManager
        from app.managers.event_scheduler import EventScheduler
        from app.managers.invisible_event_manager import InvisibleEventManager
        from app.managers.offline_progress_manager import OfflineProgressManager
        
        self.world_tick_manager = WorldTickManager(self.db)
        self.event_scheduler = EventScheduler(self.db)
        self.invisible_event_manager = InvisibleEventManager(self.db)
        self.offline_progress_manager = OfflineProgressManager(self.db)
        
        # 백그라운드 태스크 시작
        asyncio.create_task(self._background_event_loop())
        asyncio.create_task(self._process_event_queue())
        
        logger.info("[EVENT_MANAGER] 이벤트 매니저 시작됨")
    
    async def schedule_event(self, event: GameEvent):
        """
        이벤트 스케줄링
        
        Args:
            event: GameEvent 인스턴스
        """
        # 플레이어 근처 셀: 즉시 처리
        if event.cell_id in self.cell_state_manager.active_cells:
            await self._process_event_immediately(event)
        else:
            # 외부 셀: 체크포인트 대기열에 추가
            if event.cell_id not in self.checkpoint_events:
                self.checkpoint_events[event.cell_id] = []
            self.checkpoint_events[event.cell_id].append(event)
            
            logger.debug(f"[EVENT_MANAGER] 체크포인트 이벤트 추가: {event.cell_id}, {event.event_type}")
    
    async def process_checkpoint_events(self, cell_id: str):
        """
        체크포인트 이벤트 처리 (플레이어가 셀 근처로 이동 시)
        
        Args:
            cell_id: 셀 ID
        """
        if cell_id not in self.checkpoint_events:
            return
        
        events = self.checkpoint_events[cell_id]
        self.checkpoint_events[cell_id] = []
        
        logger.info(f"[EVENT_MANAGER] 체크포인트 이벤트 처리: {cell_id}, {len(events)}개 이벤트")
        
        # 배치 처리
        await self._batch_process_events(events)
        
        # 체크포인트 저장
        await self._save_checkpoint(cell_id, events)
    
    async def _process_event_immediately(self, event: GameEvent):
        """이벤트 즉시 처리 (플레이어 근처)"""
        if event.event_type == EventType.ENTITY_MOVE:
            await self._handle_entity_move(event)
        elif event.event_type == EventType.ENTITY_ACTION:
            await self._handle_entity_action(event)
        elif event.event_type == EventType.CELL_STATE_CHANGE:
            await self._handle_cell_state_change(event)
        
        # DB에 즉시 기록
        await self._save_event_to_db(event)
    
    async def _batch_process_events(self, events: List[GameEvent]):
        """배치 이벤트 처리"""
        # 상태 변화만 집계
        state_changes = {}
        
        for event in events:
            changes = await self._calculate_state_changes(event)
            state_changes.update(changes)
        
        # 배치로 상태 업데이트
        await self._apply_state_changes_batch(state_changes)
    
    async def _background_event_loop(self):
        """백그라운드 이벤트 루프"""
        while self._running:
            await asyncio.sleep(300)  # 5분마다
            await self._process_background_events()
    
    async def _process_background_events(self):
        """백그라운드 이벤트 처리"""
        # World Tick 실행
        if self.world_tick_manager:
            await self.world_tick_manager.execute_tick()
        
        # 예약 이벤트 처리
        if self.event_scheduler:
            await self.event_scheduler.process_scheduled_events(datetime.now())
```

### 2. WorldTickManager

#### 역할
- 주기적 World Tick 실행 (기본 1시간 간격)
- 이벤트 타입별 처리 (정치, 재난, 관계, 경제, 계절)
- 비가시 이벤트 로그 생성

#### 구현

```python
class WorldTickManager:
    """World Tick 관리자"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.tick_interval = 3600  # 1시간 (초)
        self.last_tick = None
        
        # 이벤트 타입별 핸들러
        self.tick_handlers = {
            'political_change': self.handle_political_change,
            'disaster': self.handle_disaster,
            'relationship_change': self.handle_relationship_change,
            'economic_shift': self.handle_economic_shift,
            'seasonal_event': self.handle_seasonal_event
        }
    
    async def execute_tick(self, session_id: str = None, tick_interval: int = None):
        """
        World Tick 실행
        
        Args:
            session_id: 세션 ID (선택사항)
            tick_interval: 틱 간격 (초, 선택사항)
        
        Returns:
            Dict: 틱 처리 결과
        """
        if tick_interval:
            self.tick_interval = tick_interval
        
        current_time = datetime.now()
        
        # 마지막 틱 이후 경과 시간 계산
        if self.last_tick:
            elapsed_time = (current_time - self.last_tick).total_seconds()
            ticks_to_process = int(elapsed_time // self.tick_interval)
        else:
            ticks_to_process = 1
        
        # 틱 처리
        tick_results = []
        for i in range(ticks_to_process):
            tick_result = await self.process_single_tick(session_id, i)
            tick_results.append(tick_result)
        
        self.last_tick = current_time
        
        return {
            "ticks_processed": ticks_to_process,
            "results": tick_results,
            "next_tick": current_time + timedelta(seconds=self.tick_interval)
        }
    
    async def process_single_tick(self, session_id: str, tick_number: int):
        """단일 틱 처리"""
        tick_result = {
            "tick_number": tick_number,
            "timestamp": datetime.now(),
            "events": [],
            "changes": {}
        }
        
        # 각 이벤트 타입별 처리
        for event_type, handler in self.tick_handlers.items():
            try:
                event_result = await handler(session_id, tick_number)
                if event_result:
                    tick_result["events"].append({
                        "type": event_type,
                        "result": event_result
                    })
            except Exception as e:
                logger.error(f"[WORLD_TICK] {event_type} 처리 실패: {str(e)}")
        
        # 틱 결과 저장
        await self.save_tick_result(session_id, tick_result)
        
        return tick_result
    
    async def handle_political_change(self, session_id: str, tick_number: int):
        """정치적 변화 처리"""
        # 정치적 변화 확률 계산
        change_probability = await self.calculate_political_change_probability(session_id)
        
        if random.random() < change_probability:
            change_type = random.choice([
                "leadership_change",
                "policy_change",
                "alliance_shift",
                "conflict_escalation"
            ])
            
            change_result = await self.execute_political_change(session_id, change_type)
            
            # 비가시 이벤트 로그 생성
            await self.invisible_event_manager.log_invisible_event(session_id, {
                "type": "political_change",
                "change_type": change_type,
                "description": change_result["description"],
                "impact": change_result["impact"]
            })
            
            return change_result
        
        return None
    
    async def handle_disaster(self, session_id: str, tick_number: int):
        """재난 처리"""
        disaster_probability = await self.calculate_disaster_probability(session_id)
        
        if random.random() < disaster_probability:
            disaster_type = random.choice([
                "natural_disaster",
                "plague",
                "famine",
                "war",
                "economic_crisis"
            ])
            
            disaster_result = await self.execute_disaster(session_id, disaster_type)
            
            # 비가시 이벤트 로그 생성
            await self.invisible_event_manager.log_invisible_event(session_id, {
                "type": "disaster",
                "disaster_type": disaster_type,
                "description": disaster_result["description"],
                "severity": disaster_result["severity"],
                "affected_regions": disaster_result["affected_regions"]
            })
            
            return disaster_result
        
        return None
    
    # ... (다른 핸들러들도 유사한 패턴)
```

### 3. EventScheduler

#### 역할
- 예약 이벤트 관리
- 시간 기반 이벤트 트리거
- 이벤트 큐 관리

#### 구현

```python
class EventScheduler:
    """이벤트 스케줄러"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.scheduled_events = {}
        self.event_queue = []
    
    async def schedule_event(self, event_type: str, trigger_time: datetime, 
                           parameters: dict, session_id: str = None):
        """
        이벤트 스케줄링
        
        Args:
            event_type: 이벤트 타입
            trigger_time: 트리거 시간
            parameters: 이벤트 파라미터
            session_id: 세션 ID (선택사항)
        
        Returns:
            str: 이벤트 ID
        """
        event_id = str(uuid.uuid4())
        scheduled_event = {
            "event_id": event_id,
            "event_type": event_type,
            "trigger_time": trigger_time,
            "parameters": parameters,
            "session_id": session_id,
            "status": "scheduled",
            "created_at": datetime.now()
        }
        
        # 이벤트 큐에 추가
        self.event_queue.append(scheduled_event)
        
        # 시간순 정렬
        self.event_queue.sort(key=lambda x: x["trigger_time"])
        
        # 데이터베이스에 저장
        await self.save_scheduled_event(scheduled_event)
        
        return event_id
    
    async def process_scheduled_events(self, current_time: datetime):
        """예약된 이벤트 처리"""
        processed_events = []
        
        # 현재 시간 이전의 이벤트들 처리
        while self.event_queue and self.event_queue[0]["trigger_time"] <= current_time:
            event = self.event_queue.pop(0)
            
            try:
                result = await self.execute_scheduled_event(event)
                processed_events.append(result)
                
                event["status"] = "executed"
                await self.update_scheduled_event(event)
            except Exception as e:
                logger.error(f"[EVENT_SCHEDULER] 이벤트 실행 실패 {event['event_id']}: {str(e)}")
                event["status"] = "failed"
                await self.update_scheduled_event(event)
        
        return processed_events
```

### 4. InvisibleEventManager

#### 역할
- 비가시 이벤트 로그 관리
- 이벤트 가시화 처리
- 플레이어 조우 시 이벤트 노출

#### 구현

```python
class InvisibleEventManager:
    """비가시 이벤트 관리자"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.event_logs = {}
    
    async def get_invisible_events(self, session_id: str, since: datetime = None):
        """
        비가시 이벤트 조회
        
        Args:
            session_id: 세션 ID
            since: 조회 시작 시간 (기본: 최근 7일)
        
        Returns:
            Dict: 분류된 이벤트 목록
        """
        if since is None:
            since = datetime.now() - timedelta(days=7)
        
        # 데이터베이스에서 이벤트 조회
        events = await self.load_invisible_events(session_id, since)
        
        # 이벤트 분류
        classified_events = {
            "political": [],
            "disaster": [],
            "relationship": [],
            "economic": [],
            "seasonal": []
        }
        
        for event in events:
            event_type = event["type"]
            if event_type in classified_events:
                classified_events[event_type].append(event)
        
        return classified_events
    
    async def log_invisible_event(self, session_id: str, event_data: dict):
        """
        비가시 이벤트 로그 생성
        
        Args:
            session_id: 세션 ID
            event_data: 이벤트 데이터
        
        Returns:
            Dict: 로그 엔트리
        """
        log_entry = {
            "session_id": session_id,
            "event_type": event_data["type"],
            "description": event_data["description"],
            "timestamp": datetime.now(),
            "data": event_data,
            "visible": False
        }
        
        # 데이터베이스에 저장
        await self.save_invisible_event_log(log_entry)
        
        return log_entry
    
    async def make_event_visible(self, session_id: str, event_id: str, 
                               visibility_trigger: str):
        """
        이벤트 가시화
        
        Args:
            session_id: 세션 ID
            event_id: 이벤트 ID
            visibility_trigger: 가시화 트리거
        
        Returns:
            Dict: 처리 결과
        """
        # 이벤트 조회
        event = await self.get_invisible_event(event_id)
        if not event:
            raise ValueError(f"Event not found: {event_id}")
        
        # 가시화 조건 확인
        if not await self.check_visibility_conditions(session_id, event, visibility_trigger):
            return {"success": False, "message": "Visibility conditions not met"}
        
        # 이벤트 가시화
        await self.update_event_visibility(event_id, True)
        
        # 플레이어에게 이벤트 알림
        await self.notify_player(session_id, {
            "type": "world_event",
            "event": event,
            "trigger": visibility_trigger
        })
        
        return {"success": True, "event": event}
```

### 5. OfflineProgressManager

#### 역할
- 오프라인 진행 처리 (Catch-up)
- 마지막 활동 시각 기반 계산
- 오프라인 진행 요약 생성

#### 구현

```python
class OfflineProgressManager:
    """오프라인 진행 관리자"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.catchup_handlers = {
            'political': self.catchup_political_events,
            'disaster': self.catchup_disaster_events,
            'relationship': self.catchup_relationship_events,
            'economic': self.catchup_economic_events,
            'seasonal': self.catchup_seasonal_events
        }
    
    async def process_offline_progress(self, session_id: str, 
                                     last_activity: datetime):
        """
        오프라인 진행 처리
        
        Args:
            session_id: 세션 ID
            last_activity: 마지막 활동 시간
        
        Returns:
            Dict: 오프라인 진행 결과
        """
        current_time = datetime.now()
        offline_duration = current_time - last_activity
        
        # 오프라인 시간 계산
        offline_hours = offline_duration.total_seconds() / 3600
        
        # 최대 오프라인 시간 제한 (24시간)
        max_offline_hours = 24
        if offline_hours > max_offline_hours:
            offline_hours = max_offline_hours
        
        # 오프라인 진행 처리
        catchup_results = {}
        for event_type, handler in self.catchup_handlers.items():
            try:
                result = await handler(session_id, offline_hours)
                catchup_results[event_type] = result
            except Exception as e:
                logger.error(f"[OFFLINE_PROGRESS] {event_type} catchup 실패: {str(e)}")
                catchup_results[event_type] = {"error": str(e)}
        
        # 오프라인 진행 요약 생성
        summary = await self.generate_offline_summary(session_id, catchup_results)
        
        return {
            "offline_duration": offline_hours,
            "catchup_results": catchup_results,
            "summary": summary
        }
```

## 데이터베이스 스키마

### 기존 구현된 테이블

#### 1. triggered_events 테이블 (구현됨)

**위치**: `database/setup/mvp_schema.sql` (라인 907-925)

```sql
CREATE TABLE runtime_data.triggered_events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB,
    source_entity_ref UUID,
    target_entity_ref UUID,
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES runtime_data.active_sessions(session_id),
    FOREIGN KEY (source_entity_ref) REFERENCES reference_layer.entity_references(runtime_entity_id),
    FOREIGN KEY (target_entity_ref) REFERENCES reference_layer.entity_references(runtime_entity_id)
);

CREATE INDEX idx_triggered_events_session ON runtime_data.triggered_events(session_id);
CREATE INDEX idx_triggered_events_type ON runtime_data.triggered_events(event_type);
CREATE INDEX idx_triggered_events_triggered_at ON runtime_data.triggered_events(triggered_at);
```

**사용처**:
- `app/systems/time_system.py`: `_log_event()` 메서드에서 이벤트 기록
- `app/core/game_manager.py`: 게임 이벤트 기록
- `app/core/game_session.py`: 세션 이벤트 기록

#### 2. entity_behavior_schedules 테이블 (구현됨)

**위치**: `database/setup/mvp_schema.sql` (라인 950-969)

```sql
CREATE TABLE game_data.entity_behavior_schedules (
    schedule_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id VARCHAR(50) NOT NULL,
    time_period VARCHAR(20) NOT NULL,  -- 'morning', 'afternoon', 'evening', 'night'
    action_type VARCHAR(50) NOT NULL,  -- 'work', 'rest', 'socialize', 'patrol', 'sleep'
    action_priority INTEGER DEFAULT 1,
    conditions JSONB,  -- 행동 조건 (날씨, 에너지, 기분 등)
    action_data JSONB,  -- 행동 세부 데이터
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (entity_id) REFERENCES game_data.entities(entity_id) ON DELETE CASCADE
);

CREATE INDEX idx_behavior_schedule_entity ON game_data.entity_behavior_schedules(entity_id);
CREATE INDEX idx_behavior_schedule_time ON game_data.entity_behavior_schedules(time_period);
CREATE INDEX idx_behavior_schedule_action ON game_data.entity_behavior_schedules(action_type);
CREATE INDEX idx_entity_behavior_schedules_composite 
    ON game_data.entity_behavior_schedules(entity_id, time_period, action_priority);
CREATE INDEX idx_entity_behavior_schedules_conditions_gin 
    ON game_data.entity_behavior_schedules USING GIN (conditions);
CREATE INDEX idx_entity_behavior_schedules_action_data_gin 
    ON game_data.entity_behavior_schedules USING GIN (action_data);
```

**JSONB 구조**:
- `conditions`: `{"min_energy": 20, "weather": "clear", "mood": "happy"}`
- `action_data`: `{"duration": 2, "location": "shop", "target_entity": "merchant"}`

**API**: `app/api/routes/behavior_schedules.py`
- `GET /api/behavior-schedules/entity/{entity_id}`: 엔티티별 스케줄 조회
- `GET /api/behavior-schedules/{schedule_id}`: 특정 스케줄 조회
- `POST /api/behavior-schedules/`: 스케줄 생성
- `PUT /api/behavior-schedules/{schedule_id}`: 스케줄 업데이트
- `DELETE /api/behavior-schedules/{schedule_id}`: 스케줄 삭제

**서비스**: `app/services/world_editor/behavior_schedule_service.py`

#### 3. time_events 테이블 (구현됨)

**위치**: `database/setup/mvp_schema.sql` (라인 972-989)

```sql
CREATE TABLE game_data.time_events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_name VARCHAR(100) NOT NULL,
    event_type VARCHAR(50) NOT NULL,  -- 'daily', 'weekly', 'monthly', 'yearly', 'custom'
    trigger_day INTEGER,  -- 특정 날짜 (NULL이면 매일)
    trigger_hour INTEGER,  -- 0-23
    trigger_minute INTEGER DEFAULT 0,  -- 0-59
    event_data JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_time_events_type ON game_data.time_events(event_type);
CREATE INDEX idx_time_events_active ON game_data.time_events(is_active);
CREATE INDEX idx_time_events_trigger_time ON game_data.time_events(trigger_day, trigger_hour, trigger_minute);
```

**JSONB 구조**:
- `event_data`: `{"description": "상점 오픈", "affected_entities": ["merchant_001"], "world_changes": {"shop_open": true}}`

#### 4. session_states 테이블 (구현됨)

**위치**: `database/setup/mvp_schema.sql` (라인 1001-1014)

```sql
CREATE TABLE runtime_data.session_states (
    session_id UUID PRIMARY KEY,
    current_day INTEGER DEFAULT 1,
    current_hour INTEGER DEFAULT 6,
    current_minute INTEGER DEFAULT 0,
    last_tick TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES runtime_data.active_sessions(session_id) ON DELETE CASCADE
);

CREATE INDEX idx_session_states_time ON runtime_data.session_states(current_day, current_hour, last_tick);
```

**사용처**:
- `app/systems/time_system.py`: `_load_session_state()`, `_save_time_state()` 메서드에서 게임 시간 관리

#### 5. active_sessions 테이블 (시뮬레이션 관련 컬럼 추가됨)

**위치**: `database/setup/mvp_schema.sql` (라인 569-587, 996-998)

```sql
CREATE TABLE runtime_data.active_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_name VARCHAR(100) NOT NULL DEFAULT 'Unnamed Session',
    session_state VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP,
    metadata JSONB,
    player_runtime_entity_id UUID,
    simulation_mode BOOLEAN DEFAULT false,
    time_acceleration DECIMAL(3,1) DEFAULT 1.0
);
```

### 미구현 테이블 (Event Manager 구현 시 필요)

#### 1. scheduled_events 테이블 (미구현)

```sql
CREATE TABLE runtime_data.scheduled_events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    trigger_time TIMESTAMP NOT NULL,
    parameters JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'scheduled',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    executed_at TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES runtime_data.active_sessions(session_id) ON DELETE CASCADE
);

CREATE INDEX idx_scheduled_events_trigger_time ON runtime_data.scheduled_events(trigger_time);
CREATE INDEX idx_scheduled_events_status ON runtime_data.scheduled_events(status);
CREATE INDEX idx_scheduled_events_session ON runtime_data.scheduled_events(session_id);
```

**용도**: 런타임에서 스케줄링된 이벤트 관리 (게임 데이터의 `time_events`와는 별도)

#### 2. invisible_event_logs 테이블 (미구현)

```sql
CREATE TABLE runtime_data.invisible_event_logs (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    description TEXT,
    event_data JSONB NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    visible BOOLEAN DEFAULT FALSE,
    visibility_trigger TEXT,
    FOREIGN KEY (session_id) REFERENCES runtime_data.active_sessions(session_id) ON DELETE CASCADE
);

CREATE INDEX idx_invisible_logs_session ON runtime_data.invisible_event_logs(session_id);
CREATE INDEX idx_invisible_logs_visible ON runtime_data.invisible_event_logs(visible);
CREATE INDEX idx_invisible_logs_timestamp ON runtime_data.invisible_event_logs(timestamp);
```

**용도**: 플레이어가 보지 못한 백그라운드 이벤트 로그

#### 3. cell_checkpoints 테이블 (미구현)

```sql
CREATE TABLE runtime_data.cell_checkpoints (
    cell_id VARCHAR(50) PRIMARY KEY,
    session_id UUID NOT NULL,
    checkpoint_data JSONB NOT NULL,
    last_checkpoint_time TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (session_id) REFERENCES runtime_data.active_sessions(session_id) ON DELETE CASCADE
);

CREATE INDEX idx_cell_checkpoints_time ON runtime_data.cell_checkpoints(last_checkpoint_time);
CREATE INDEX idx_cell_checkpoints_session ON runtime_data.cell_checkpoints(session_id);
```

**용도**: 외부 셀의 상태 체크포인트 저장

## 성능 최적화

### 1. 이벤트 필터링

- 플레이어 근처 셀만 상세 처리
- 외부 셀은 상태 변화만 기록
- 백그라운드 이벤트는 주기적으로만 확인 (5분 간격)

### 2. 배치 처리

- 체크포인트 이벤트는 배치로 처리
- 상태 변화를 집계하여 한 번에 적용
- 트랜잭션 오버헤드 최소화

### 3. 조건 기반 실행

- 이벤트 발생 조건을 미리 필터링
- 불필요한 이벤트 처리 방지
- 쿨다운으로 중복 실행 방지

### 4. 결정적 난수 시스템

```python
class DeterministicRandom:
    """결정적 난수 생성기"""
    
    def __init__(self):
        self.seeds = {}
        self.random_generators = {}
    
    async def get_session_seed(self, session_id: str):
        """세션별 시드 조회"""
        if session_id not in self.seeds:
            self.seeds[session_id] = random.randint(0, 2**32 - 1)
            await self.save_session_seed(session_id, self.seeds[session_id])
        
        return self.seeds[session_id]
    
    async def get_random_generator(self, session_id: str):
        """세션별 난수 생성기 조회"""
        if session_id not in self.random_generators:
            seed = await self.get_session_seed(session_id)
            self.random_generators[session_id] = random.Random(seed)
        
        return self.random_generators[session_id]
```

## 기존 구현 현황

### 구현된 컴포넌트

#### 1. TimeSystem (`app/systems/time_system.py`)

**기능**:
- 게임 시간 관리 (`session_states` 테이블 활용)
- 이벤트 스케줄링 (메모리 기반)
- 틱 루프 실행
- 이벤트 로깅 (`triggered_events` 테이블)

**주요 메서드**:
- `start(session_id)`: 시간 시스템 시작
- `schedule_event()`: 이벤트 스케줄링
- `_check_scheduled_events()`: 스케줄된 이벤트 확인 및 실행
- `_log_event()`: `triggered_events` 테이블에 이벤트 기록

**제한사항**:
- 스케줄된 이벤트가 메모리에만 저장됨 (세션 종료 시 손실)
- `scheduled_events` 테이블 미사용

#### 2. BehaviorScheduleService (`app/services/world_editor/behavior_schedule_service.py`)

**기능**:
- `entity_behavior_schedules` 테이블 CRUD
- 엔티티별 행동 스케줄 관리

**API**: `app/api/routes/behavior_schedules.py`

#### 3. Entity Behavior Schedules 테이블

**용도**: 엔티티의 시간대별 행동 패턴 정의 (템플릿)

**Event Manager 활용 방안**:
- WorldTickManager가 `entity_behavior_schedules`를 조회하여 NPC 행동 결정
- 현재 게임 시간(`session_states`)과 `time_period` 매칭
- `conditions` JSONB로 행동 조건 확인
- `action_data` JSONB로 행동 실행

### 미구현 컴포넌트

#### 1. EventManager (중앙 관리자)
- 이벤트 큐 관리
- 즉시 처리 vs 체크포인트 분기
- 백그라운드 이벤트 루프

#### 2. WorldTickManager
- 주기적 World Tick 실행
- 이벤트 타입별 핸들러 (정치, 재난, 관계, 경제, 계절)
- `entity_behavior_schedules` 통합

#### 3. EventScheduler
- `scheduled_events` 테이블 활용
- 영구 저장된 이벤트 스케줄링

#### 4. InvisibleEventManager
- `invisible_event_logs` 테이블 활용
- 비가시 이벤트 관리

#### 5. OfflineProgressManager
- 오프라인 진행 처리

## 구현 우선순위

### Phase 1: 기본 이벤트 큐 및 기존 시스템 통합 (2-3주)
- [ ] EventManager 기본 구조
- [ ] TimeSystem과 통합
- [ ] `entity_behavior_schedules` 활용 로직
- [ ] 즉시 처리 로직
- [ ] 체크포인트 큐 관리

### Phase 2: World Tick 시스템 (2-3주)
- [ ] WorldTickManager 구현
- [ ] `entity_behavior_schedules` 기반 NPC 행동 처리
- [ ] `time_events` 기반 시간 이벤트 처리
- [ ] 이벤트 타입별 핸들러 (정치, 재난, 관계, 경제, 계절)
- [ ] 틱 실행 로직
- [ ] 틱 결과 저장 (`triggered_events`)

### Phase 3: 이벤트 스케줄링 (1-2주)
- [ ] `scheduled_events` 테이블 생성
- [ ] EventScheduler 구현
- [ ] TimeSystem의 메모리 기반 스케줄링을 DB 기반으로 전환
- [ ] 시간 기반 트리거

### Phase 4: 비가시 이벤트 (1-2주)
- [ ] `invisible_event_logs` 테이블 생성
- [ ] InvisibleEventManager 구현
- [ ] 비가시 이벤트 로그
- [ ] 이벤트 가시화 처리

### Phase 5: 오프라인 진행 (1-2주)
- [ ] OfflineProgressManager 구현
- [ ] Catch-up 메커니즘
- [ ] 오프라인 진행 요약

### Phase 6: 결정적 난수 (1주)
- [ ] DeterministicRandom 구현
- [ ] Seed 관리
- [ ] 재현성 테스트

## 테스트 전략

### 1. 단위 테스트

```python
async def test_event_scheduling():
    """이벤트 스케줄링 테스트"""
    event = GameEvent(
        event_id="test_event_001",
        event_type=EventType.POLITICAL_CHANGE,
        cell_id="CELL_TEST_001",
        entity_id=None,
        data={"change_type": "leadership_change"},
        timestamp=datetime.now()
    )
    
    await event_manager.schedule_event(event)
    
    # 체크포인트 큐에 추가되었는지 확인
    assert "CELL_TEST_001" in event_manager.checkpoint_events
```

### 2. 통합 테스트

```python
async def test_world_tick_execution():
    """World Tick 실행 테스트"""
    result = await world_tick_manager.execute_tick(
        session_id="test_session",
        tick_interval=3600
    )
    
    assert result["ticks_processed"] > 0
    assert len(result["results"]) > 0
```

### 3. 성능 테스트

```python
async def test_background_event_performance():
    """백그라운드 이벤트 성능 테스트"""
    start_time = time.time()
    
    # 100개 이벤트 처리
    for i in range(100):
        await event_manager._process_background_events()
    
    elapsed = time.time() - start_time
    assert elapsed < 10.0  # 10초 이내
```

## 기존 API 및 서비스 활용

### Behavior Schedule API

**엔드포인트**: `/api/behavior-schedules/`

**사용 예시**:
```python
# 엔티티별 스케줄 조회
GET /api/behavior-schedules/entity/{entity_id}

# 응답 예시
[
    {
        "schedule_id": "uuid",
        "entity_id": "NPC_MERCHANT_001",
        "time_period": "morning",
        "action_type": "work",
        "action_priority": 1,
        "conditions": {"min_energy": 20},
        "action_data": {"location": "shop", "duration": 2}
    }
]
```

### TimeSystem 활용

**현재 구현**: `app/systems/time_system.py`

**Event Manager 통합 방안**:
```python
# TimeSystem과 EventManager 통합
from app.systems.time_system import time_system

class EventManager:
    def __init__(self, ...):
        self.time_system = time_system
    
    async def process_entity_behaviors(self, session_id: str):
        """엔티티 행동 처리"""
        current_time = self.time_system.get_current_time()
        time_period = self._get_time_period(current_time.hour)
        
        # entity_behavior_schedules 조회
        schedules = await self._get_schedules_for_period(time_period)
        
        for schedule in schedules:
            if await self._check_conditions(schedule.conditions):
                await self._execute_action(schedule.action_data)
```

## 데이터 흐름 예시

### 1. NPC 행동 처리 (entity_behavior_schedules 활용)

```
WorldTickManager.execute_tick()
    ↓
현재 게임 시간 확인 (session_states)
    ↓
time_period 결정 (morning/afternoon/evening/night)
    ↓
entity_behavior_schedules 조회 (time_period 매칭)
    ↓
conditions 확인 (JSONB)
    ↓
action_data 실행 (JSONB)
    ↓
triggered_events에 기록
```

### 2. 시간 이벤트 처리 (time_events 활용)

```
TimeSystem._check_scheduled_events()
    ↓
현재 게임 시간 확인 (session_states)
    ↓
time_events 조회 (trigger_day, trigger_hour, trigger_minute 매칭)
    ↓
is_active 확인
    ↓
event_data 실행 (JSONB)
    ↓
triggered_events에 기록
```

## 결론

이벤트 매니저는 다음을 담당합니다:

1. **플레이어 근처 셀**: 즉시 처리로 실시간 반응
2. **외부 셀**: 체크포인트 대기 후 배치 처리
3. **백그라운드**: World Tick 시스템으로 플레이어 없이도 세계가 작동

**기존 구현 활용**:
- `entity_behavior_schedules`: NPC 행동 패턴 정의
- `time_events`: 시간 기반 이벤트 템플릿
- `session_states`: 게임 시간 관리
- `triggered_events`: 이벤트 기록
- `TimeSystem`: 시간 시스템 기반

**추가 구현 필요**:
- `scheduled_events`: 런타임 이벤트 스케줄링
- `invisible_event_logs`: 비가시 이벤트 로그
- `cell_checkpoints`: 외부 셀 체크포인트

이를 통해 "플레이어가 보지 않는 곳에서도 세계가 돌아가는" 디앤디 뱀파이어 캠페인 스타일의 경험을 제공할 수 있습니다.

## 참고 문서

- `docs/ideation/03_world_tick_guide.md`: World Tick 시스템 상세 가이드
- `docs/ideation/12_dev_memo.md`: 원본 설계 의도
- `docs/architecture/PERFORMANCE_OPTIMIZATION_STRATEGY.md`: 성능 최적화 전략
- `app/systems/time_system.py`: 기존 시간 시스템 구현
- `app/services/world_editor/behavior_schedule_service.py`: 행동 스케줄 서비스
- `database/setup/mvp_schema.sql`: 데이터베이스 스키마
