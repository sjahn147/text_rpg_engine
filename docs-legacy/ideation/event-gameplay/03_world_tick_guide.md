# World Tick 시스템 가이드

> **문서 버전**: v1.0  
> **작성일**: 2025-10-18  
> **최종 수정**: 2025-10-18

## 🌍 **World Tick 시스템 개요**

World Tick 시스템은 RPG Engine의 핵심 기능으로, 플레이어가 없어도 세계가 계속 작동하는 백그라운드 이벤트 처리 시스템입니다.

### **핵심 철학**
> **"지속적 세계: 플레이어가 없어도 세계는 계속 작동"**

- **백그라운드 진행**: 시간 경과/스케줄 처리(내부 정치, 재난, 관계 변화)
- **비가시 이벤트**: 로그만 남김 → 플레이어가 나중에 "결과"와 조우
- **결정적 난수**: seed로 재현성 확보
- **오프라인 진행**: 마지막 활동 시각 기반 catch‑up

---

## ⏰ **World Tick 실행**

### **World Tick 매니저**

#### **World Tick 실행**
```python
class WorldTickManager:
    def __init__(self):
        self.tick_interval = 3600  # 1시간 (초)
        self.last_tick = None
        self.tick_handlers = {
            'political_change': self.handle_political_change,
            'disaster': self.handle_disaster,
            'relationship_change': self.handle_relationship_change,
            'economic_shift': self.handle_economic_shift,
            'seasonal_event': self.handle_seasonal_event
        }
    
    async def execute_tick(self, session_id: str, tick_interval: int = None):
        """World Tick 실행"""
        
        if tick_interval:
            self.tick_interval = tick_interval
        
        # 현재 시간 확인
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
        
        # 마지막 틱 시간 업데이트
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
                print(f"Error processing {event_type}: {e}")
        
        # 틱 결과 저장
        await self.save_tick_result(session_id, tick_result)
        
        return tick_result
```

### **이벤트 타입별 처리**

#### **1. Political Change (정치적 변화)**
```python
async def handle_political_change(self, session_id: str, tick_number: int):
    """정치적 변화 처리"""
    
    # 정치적 변화 확률 계산
    change_probability = await self.calculate_political_change_probability(session_id)
    
    if random.random() < change_probability:
        # 변화 타입 결정
        change_type = random.choice([
            "leadership_change",
            "policy_change",
            "alliance_shift",
            "conflict_escalation"
        ])
        
        # 변화 실행
        change_result = await self.execute_political_change(session_id, change_type)
        
        # 비가시 이벤트 로그 생성
        await self.log_invisible_event(session_id, {
            "type": "political_change",
            "change_type": change_type,
            "description": change_result["description"],
            "impact": change_result["impact"]
        })
        
        return change_result
    
    return None
```

#### **2. Disaster (재난)**
```python
async def handle_disaster(self, session_id: str, tick_number: int):
    """재난 처리"""
    
    # 재난 확률 계산
    disaster_probability = await self.calculate_disaster_probability(session_id)
    
    if random.random() < disaster_probability:
        # 재난 타입 결정
        disaster_type = random.choice([
            "natural_disaster",
            "plague",
            "famine",
            "war",
            "economic_crisis"
        ])
        
        # 재난 실행
        disaster_result = await self.execute_disaster(session_id, disaster_type)
        
        # 비가시 이벤트 로그 생성
        await self.log_invisible_event(session_id, {
            "type": "disaster",
            "disaster_type": disaster_type,
            "description": disaster_result["description"],
            "severity": disaster_result["severity"],
            "affected_regions": disaster_result["affected_regions"]
        })
        
        return disaster_result
    
    return None
```

#### **3. Relationship Change (관계 변화)**
```python
async def handle_relationship_change(self, session_id: str, tick_number: int):
    """관계 변화 처리"""
    
    # 관계 변화 확률 계산
    relationship_probability = await self.calculate_relationship_change_probability(session_id)
    
    if random.random() < relationship_probability:
        # 변화 타입 결정
        change_type = random.choice([
            "faction_relations",
            "trade_agreements",
            "diplomatic_tensions",
            "cultural_exchange"
        ])
        
        # 관계 변화 실행
        relationship_result = await self.execute_relationship_change(session_id, change_type)
        
        # 비가시 이벤트 로그 생성
        await self.log_invisible_event(session_id, {
            "type": "relationship_change",
            "change_type": change_type,
            "description": relationship_result["description"],
            "affected_factions": relationship_result["affected_factions"]
        })
        
        return relationship_result
    
    return None
```

#### **4. Economic Shift (경제 변화)**
```python
async def handle_economic_shift(self, session_id: str, tick_number: int):
    """경제 변화 처리"""
    
    # 경제 변화 확률 계산
    economic_probability = await self.calculate_economic_shift_probability(session_id)
    
    if random.random() < economic_probability:
        # 변화 타입 결정
        shift_type = random.choice([
            "trade_route_change",
            "resource_discovery",
            "market_crash",
            "inflation",
            "deflation"
        ])
        
        # 경제 변화 실행
        economic_result = await self.execute_economic_shift(session_id, shift_type)
        
        # 비가시 이벤트 로그 생성
        await self.log_invisible_event(session_id, {
            "type": "economic_shift",
            "shift_type": shift_type,
            "description": economic_result["description"],
            "impact": economic_result["impact"]
        })
        
        return economic_result
    
    return None
```

#### **5. Seasonal Event (계절 이벤트)**
```python
async def handle_seasonal_event(self, session_id: str, tick_number: int):
    """계절 이벤트 처리"""
    
    # 현재 계절 확인
    current_season = await self.get_current_season(session_id)
    
    # 계절별 이벤트 확률 계산
    seasonal_probability = await self.calculate_seasonal_event_probability(session_id, current_season)
    
    if random.random() < seasonal_probability:
        # 계절별 이벤트 타입 결정
        event_type = await self.get_seasonal_event_type(current_season)
        
        # 계절 이벤트 실행
        seasonal_result = await self.execute_seasonal_event(session_id, event_type)
        
        # 비가시 이벤트 로그 생성
        await self.log_invisible_event(session_id, {
            "type": "seasonal_event",
            "season": current_season,
            "event_type": event_type,
            "description": seasonal_result["description"]
        })
        
        return seasonal_result
    
    return None
```

---

## 📅 **이벤트 스케줄링**

### **예약 이벤트**

#### **이벤트 스케줄링**
```python
class EventScheduler:
    def __init__(self):
        self.scheduled_events = {}
        self.event_queue = []
    
    async def schedule_event(self, event_type: str, trigger_time: datetime, 
                           parameters: dict, session_id: str = None):
        """이벤트 스케줄링"""
        
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
                # 이벤트 실행
                result = await self.execute_scheduled_event(event)
                processed_events.append(result)
                
                # 이벤트 상태 업데이트
                event["status"] = "executed"
                await self.update_scheduled_event(event)
                
            except Exception as e:
                print(f"Error executing scheduled event {event['event_id']}: {e}")
                event["status"] = "failed"
                await self.update_scheduled_event(event)
        
        return processed_events
```

### **이벤트 타입별 스케줄링**

#### **정치적 변화 스케줄링**
```python
async def schedule_political_change(self, session_id: str, change_type: str, 
                                  trigger_time: datetime, parameters: dict):
    """정치적 변화 스케줄링"""
    
    event_id = await self.schedule_event(
        event_type="political_change",
        trigger_time=trigger_time,
        parameters={
            "change_type": change_type,
            "faction": parameters.get("faction"),
            "severity": parameters.get("severity", "medium"),
            "description": parameters.get("description")
        },
        session_id=session_id
    )
    
    return event_id

# 예시: 정치적 변화 스케줄링
await scheduler.schedule_political_change(
    session_id="session_001",
    change_type="leadership_change",
    trigger_time=datetime.now() + timedelta(hours=2),
    parameters={
        "faction": "northern_kingdom",
        "severity": "high",
        "description": "북부 왕국의 지도자 교체"
    }
)
```

#### **재난 스케줄링**
```python
async def schedule_disaster(self, session_id: str, disaster_type: str, 
                           trigger_time: datetime, parameters: dict):
    """재난 스케줄링"""
    
    event_id = await self.schedule_event(
        event_type="disaster",
        trigger_time=trigger_time,
        parameters={
            "disaster_type": disaster_type,
            "severity": parameters.get("severity", "medium"),
            "affected_regions": parameters.get("affected_regions", []),
            "description": parameters.get("description")
        },
        session_id=session_id
    )
    
    return event_id

# 예시: 재난 스케줄링
await scheduler.schedule_disaster(
    session_id="session_001",
    disaster_type="natural_disaster",
    trigger_time=datetime.now() + timedelta(hours=4),
    parameters={
        "severity": "high",
        "affected_regions": ["REG_NORTH_FOREST_001"],
        "description": "북부 숲 지역에 대규모 홍수 발생"
    }
)
```

---

## 🔍 **비가시 이벤트 처리**

### **비가시 이벤트 로그**

#### **비가시 이벤트 조회**
```python
class InvisibleEventManager:
    def __init__(self):
        self.event_logs = {}
    
    async def get_invisible_events(self, session_id: str, since: datetime = None):
        """비가시 이벤트 조회"""
        
        if since is None:
            since = datetime.now() - timedelta(days=7)  # 최근 7일
        
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
        """비가시 이벤트 로그 생성"""
        
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
```

### **이벤트 가시화**

#### **이벤트 가시화 처리**
```python
async def make_event_visible(self, session_id: str, event_id: str, 
                           visibility_trigger: str):
    """이벤트 가시화"""
    
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

---

## 🔄 **오프라인 진행 처리**

### **Catch-up 시스템**

#### **오프라인 진행 처리**
```python
class OfflineProgressManager:
    def __init__(self):
        self.catchup_handlers = {
            'political': self.catchup_political_events,
            'disaster': self.catchup_disaster_events,
            'relationship': self.catchup_relationship_events,
            'economic': self.catchup_economic_events,
            'seasonal': self.catchup_seasonal_events
        }
    
    async def process_offline_progress(self, session_id: str, 
                                     last_activity: datetime):
        """오프라인 진행 처리"""
        
        current_time = datetime.now()
        offline_duration = current_time - last_activity
        
        # 오프라인 시간 계산
        offline_hours = offline_duration.total_seconds() / 3600
        
        # 최대 오프라인 시간 제한 (예: 24시간)
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
                print(f"Error processing {event_type} catchup: {e}")
                catchup_results[event_type] = {"error": str(e)}
        
        # 오프라인 진행 요약 생성
        summary = await self.generate_offline_summary(session_id, catchup_results)
        
        return {
            "offline_duration": offline_hours,
            "catchup_results": catchup_results,
            "summary": summary
        }
    
    async def catchup_political_events(self, session_id: str, offline_hours: float):
        """정치적 이벤트 catch-up"""
        
        # 오프라인 시간 동안의 정치적 변화 계산
        political_changes = await self.calculate_political_changes(
            session_id, offline_hours
        )
        
        # 변화 적용
        for change in political_changes:
            await self.apply_political_change(session_id, change)
        
        return {
            "changes_applied": len(political_changes),
            "changes": political_changes
        }
    
    async def catchup_disaster_events(self, session_id: str, offline_hours: float):
        """재난 이벤트 catch-up"""
        
        # 오프라인 시간 동안의 재난 계산
        disasters = await self.calculate_disasters(session_id, offline_hours)
        
        # 재난 적용
        for disaster in disasters:
            await self.apply_disaster(session_id, disaster)
        
        return {
            "disasters_applied": len(disasters),
            "disasters": disasters
        }
```

### **오프라인 진행 UI**
```
┌─────────────────────────────────────────────────────────────┐
│                    🔄 Offline Progress                      │
├─────────────────────────────────────────────────────────────┤
│ 📅 오프라인 시간: 12시간 30분                              │
│ 🕐 마지막 활동: 2025-10-17 14:30                           │
│ 🕐 현재 시간: 2025-10-18 03:00                             │
│                                                             │
│ 📋 오프라인 진행 요약:                                      │
│                                                             │
│ 🏛️ 정치적 변화 (3건)                                       │
│ • 북부 왕국 지도자 교체                                    │
│ • 동부 연합 정책 변경                                      │
│ • 남부 도시 자치권 확대                                    │
│                                                             │
│ 🌪️ 재난 이벤트 (1건)                                       │
│ • 북부 숲 지역 홍수 발생                                    │
│                                                             │
│ 💰 경제 변화 (2건)                                          │
│ • 무역로 변경                                               │
│ • 자원 가격 변동                                            │
│                                                             │
│ [상세 보기] [변화 적용] [무시]                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎲 **결정적 난수 시스템**

### **Seed 기반 재현성**

#### **Seed 관리**
```python
class DeterministicRandom:
    def __init__(self):
        self.seeds = {}
        self.random_generators = {}
    
    async def get_session_seed(self, session_id: str):
        """세션별 시드 조회"""
        
        if session_id not in self.seeds:
            # 새 시드 생성
            self.seeds[session_id] = random.randint(0, 2**32 - 1)
            await self.save_session_seed(session_id, self.seeds[session_id])
        
        return self.seeds[session_id]
    
    async def get_random_generator(self, session_id: str):
        """세션별 난수 생성기 조회"""
        
        if session_id not in self.random_generators:
            seed = await self.get_session_seed(session_id)
            self.random_generators[session_id] = random.Random(seed)
        
        return self.random_generators[session_id]
    
    async def generate_deterministic_random(self, session_id: str, 
                                          min_value: float = 0, 
                                          max_value: float = 1):
        """결정적 난수 생성"""
        
        rng = await self.get_random_generator(session_id)
        return rng.uniform(min_value, max_value)
```

### **재현성 테스트**

#### **재현성 검증**
```python
async def test_deterministic_reproduction(self, session_id: str):
    """결정적 재현성 테스트"""
    
    # 첫 번째 실행
    results_1 = []
    for i in range(10):
        result = await self.generate_deterministic_random(session_id)
        results_1.append(result)
    
    # 시드 리셋
    await self.reset_session_seed(session_id)
    
    # 두 번째 실행
    results_2 = []
    for i in range(10):
        result = await self.generate_deterministic_random(session_id)
        results_2.append(result)
    
    # 결과 비교
    for i in range(10):
        assert abs(results_1[i] - results_2[i]) < 1e-10, f"Non-deterministic result at index {i}"
    
    return True
```

---

## 🧪 **테스트 및 검증**

### **World Tick 테스트**

#### **기능 테스트**
```python
class WorldTickTest:
    def __init__(self):
        self.test_results = []
    
    async def test_world_tick_execution(self):
        """World Tick 실행 테스트"""
        
        # World Tick 실행
        tick_result = await world_tick_manager.execute_tick(
            session_id="test_session",
            tick_interval=3600
        )
        
        assert tick_result["ticks_processed"] > 0
        assert len(tick_result["results"]) > 0
        
        return True
    
    async def test_invisible_events(self):
        """비가시 이벤트 테스트"""
        
        # 비가시 이벤트 생성
        await invisible_event_manager.log_invisible_event(
            session_id="test_session",
            event_data={
                "type": "political_change",
                "description": "테스트 정치적 변화"
            }
        )
        
        # 비가시 이벤트 조회
        events = await invisible_event_manager.get_invisible_events(
            session_id="test_session"
        )
        
        assert len(events["political"]) > 0
        
        return True
    
    async def test_offline_progress(self):
        """오프라인 진행 테스트"""
        
        # 오프라인 진행 처리
        catchup_result = await offline_progress_manager.process_offline_progress(
            session_id="test_session",
            last_activity=datetime.now() - timedelta(hours=12)
        )
        
        assert catchup_result["offline_duration"] > 0
        assert "catchup_results" in catchup_result
        
        return True
```

---

## 📋 **구현 체크리스트**

### **World Tick 시스템**
- [ ] World Tick 실행 로직
- [ ] 이벤트 타입별 처리
- [ ] 비가시 이벤트 로그
- [ ] 오프라인 진행 처리

### **이벤트 스케줄링**
- [ ] 예약 이벤트 시스템
- [ ] 이벤트 큐 관리
- [ ] 이벤트 실행 로직

### **결정적 난수**
- [ ] Seed 관리 시스템
- [ ] 재현성 보장
- [ ] 테스트 및 검증

### **성능 최적화**
- [ ] 이벤트 처리 최적화
- [ ] 메모리 사용량 최적화
- [ ] 데이터베이스 쿼리 최적화

---

## 🚀 **다음 단계**

1. **World Tick 시스템 구현**: 백그라운드 이벤트 처리 로직
2. **이벤트 스케줄링 구현**: 예약 이벤트 시스템
3. **비가시 이벤트 시스템**: 이벤트 로그 및 가시화
4. **오프라인 진행 시스템**: Catch-up 메커니즘
5. **결정적 난수 시스템**: Seed 기반 재현성

---

**문서 작성자**: RPG Engine Development Team  
**최종 검토**: 2025-10-18  
**다음 검토 예정**: 2025-11-18
