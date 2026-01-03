# Time System 가이드라인

> **최신화 날짜**: 2026-01-03  
> **적용 범위**: 게임 시간 시스템 및 이벤트 스케줄링 개발 시 필수 읽기

## ⚠️ 중요: mvp_schema.sql 참조 필수

**모든 시간 시스템 관련 작업은 반드시 `database/setup/mvp_schema.sql`을 참조해야 합니다.**

## 1. 개요

Time System은 게임 내 시간 진행, 이벤트 스케줄링, NPC 행동 패턴 관리를 담당하는 핵심 시스템입니다.

### 1.1 시스템 구조

```
app/systems/time_system.py
    ↓
TimeSystem 클래스
    ↓
- 게임 시간 관리 (GameTime)
- 이벤트 스케줄링 (ScheduledEvent)
- 시간 가속 배율 (TimeScale)
- 세션 상태 저장/로드
```

### 1.2 데이터베이스 스키마

**game_data 스키마**:
- `game_data.time_events`: 시간 기반 이벤트 스케줄 (템플릿)

**runtime_data 스키마**:
- `runtime_data.session_states`: 세션별 상태 관리 (게임 시간, 틱 등)
- `runtime_data.triggered_events`: 트리거된 이벤트 기록

## 2. 핵심 개념

### 2.1 GameTime

게임 내 시간 표현:

```python
from app.systems.time_system import GameTime

# 게임 시간 생성
game_time = GameTime(day=1, hour=6, minute=0, second=0)
print(game_time)  # "Day 1, 06:00:00"

# 딕셔너리 변환
time_dict = game_time.to_dict()
# {"day": 1, "hour": 6, "minute": 0, "second": 0}
```

### 2.2 TimeScale

시간 가속 배율:

```python
from app.systems.time_system import TimeScale

# 시간 가속 배율 설정
time_system.set_time_scale(TimeScale.FAST)  # 1:10
time_system.set_time_scale(TimeScale.VERY_FAST)  # 1:100
time_system.set_time_scale(TimeScale.INSTANT)  # 즉시
```

**TimeScale 종류**:
- `REAL_TIME`: 실시간 (1:1)
- `FAST`: 빠름 (1:10)
- `VERY_FAST`: 매우 빠름 (1:100)
- `INSTANT`: 즉시 (무한대)

### 2.3 TimePeriod

게임 내 시간대:

```python
from app.systems.time_system import TimePeriod

# 시간대 확인
time_period = time_system.get_time_period()
# TimePeriod.MORNING, AFTERNOON, EVENING, NIGHT
```

**TimePeriod 종류**:
- `MORNING`: 아침
- `AFTERNOON`: 오후
- `EVENING`: 저녁
- `NIGHT`: 밤

### 2.4 ScheduledEvent

스케줄된 이벤트:

```python
from app.systems.time_system import ScheduledEvent, GameTime

# 이벤트 스케줄링
event_id = await time_system.schedule_event(
    event_name="상점 오픈",
    event_type="shop_open",
    trigger_time=GameTime(day=1, hour=9, minute=0),
    event_data={"shop_id": "SHOP_001", "session_id": session_id},
    handler=shop_open_handler,
    repeat_interval=1440  # 24시간마다 반복 (분 단위)
)
```

## 3. TimeSystem 사용법

### 3.1 초기화 및 시작

```python
from app.systems.time_system import TimeSystem, start_time_system

# TimeSystem 초기화
time_system = TimeSystem()
await time_system.initialize()

# 시간 시스템 시작
await time_system.start(session_id)

# 또는 편의 함수 사용
await start_time_system(session_id)
```

### 3.2 시간 조회 및 설정

```python
# 현재 시간 조회
current_time = time_system.get_current_time()
print(f"현재 시간: {current_time}")

# 시간 설정
new_time = GameTime(day=2, hour=12, minute=30)
time_system.set_time(new_time)

# 시간 수동 진행
await time_system.advance_time(minutes=30)  # 30분 진행
```

### 3.3 이벤트 스케줄링

```python
# 이벤트 스케줄링
event_id = await time_system.schedule_event(
    event_name="NPC 이동",
    event_type="npc_move",
    trigger_time=GameTime(day=1, hour=14, minute=0),
    event_data={
        "npc_id": "NPC_001",
        "target_cell": "CELL_MARKET",
        "session_id": session_id
    },
    handler=npc_move_handler,
    repeat_interval=60  # 1시간마다 반복
)

# 이벤트 취소
success = await time_system.cancel_event(event_id)
```

### 3.4 틱 핸들러 등록

```python
# 틱 핸들러 추가
async def my_tick_handler(current_time: GameTime):
    print(f"틱: {current_time}")
    # 매 틱마다 실행할 로직

time_system.add_tick_handler(my_tick_handler)

# 틱 핸들러 제거
time_system.remove_tick_handler(my_tick_handler)
```

### 3.5 시간 시스템 중지

```python
# 시간 시스템 중지
await time_system.stop()

# 또는 편의 함수 사용
await stop_time_system()
```

## 4. 데이터베이스 연동

### 4.1 세션 상태 저장/로드

TimeSystem은 자동으로 세션 상태를 저장하고 로드합니다:

```python
# 세션 시작 시 자동 로드
await time_system.start(session_id)
# → runtime_data.session_states에서 시간 상태 로드

# 매 틱마다 자동 저장
# → runtime_data.session_states에 시간 상태 업데이트
```

**session_states 테이블 구조**:
```sql
CREATE TABLE runtime_data.session_states (
    session_id UUID PRIMARY KEY,
    current_day INTEGER DEFAULT 1,
    current_hour INTEGER DEFAULT 6,
    current_minute INTEGER DEFAULT 0,
    last_tick TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.2 이벤트 로깅

트리거된 이벤트는 자동으로 `runtime_data.triggered_events`에 기록됩니다:

```sql
CREATE TABLE runtime_data.triggered_events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB,
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.3 시간 이벤트 템플릿

게임 데이터에 시간 이벤트 템플릿을 정의할 수 있습니다:

```sql
CREATE TABLE game_data.time_events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_name VARCHAR(100) NOT NULL,
    event_type VARCHAR(50) NOT NULL,  -- 'daily', 'weekly', 'monthly', 'yearly', 'custom'
    trigger_day INTEGER,  -- 특정 날짜 (NULL이면 매일)
    trigger_hour INTEGER,  -- 0-23
    trigger_minute INTEGER DEFAULT 0,  -- 0-59
    event_data JSONB,
    is_active BOOLEAN DEFAULT true
);
```

## 5. 사용 원칙

### 5.1 필수 원칙

1. **세션별 TimeSystem 인스턴스**: 각 세션마다 별도의 TimeSystem 인스턴스 사용
2. **초기화 필수**: `initialize()` 호출 후 사용
3. **정리 필수**: `cleanup()` 또는 `stop()` 호출로 정리
4. **트랜잭션 관리**: 시간 상태 저장은 트랜잭션 내에서 수행
5. **에러 처리**: 모든 예외를 명시적으로 처리

### 5.2 권장 사항

1. **시간 가속 배율 조절**: 게임 상황에 맞게 적절한 배율 설정
2. **이벤트 반복 간격**: 반복 이벤트는 적절한 간격 설정
3. **틱 핸들러 최소화**: 틱 핸들러는 가벼운 작업만 수행
4. **이벤트 핸들러 분리**: 복잡한 로직은 별도 핸들러로 분리

### 5.3 금지 사항

1. **❌ 직접 DB 수정**: `session_states` 테이블 직접 수정 금지
2. **❌ 시간 역행**: 시간을 과거로 설정하지 않음
3. **❌ 무한 루프**: 틱 핸들러에서 무한 루프 생성 금지
4. **❌ 동기 작업**: 틱 핸들러에서 동기 I/O 작업 금지

## 6. 자주 발생하는 에러 및 해결

### 6.1 세션 상태 로드 실패

**에러**: `세션 상태 로드 실패`

**해결**:
- `session_id`가 올바른지 확인
- `runtime_data.session_states` 테이블 존재 확인
- UUID 형식 확인 (`uuid_helper.py` 사용)

### 6.2 이벤트 트리거 실패

**에러**: `이벤트 실행 실패`

**해결**:
- 이벤트 핸들러가 올바른지 확인
- `event_data` 형식 확인
- 이벤트 핸들러에서 예외 처리 확인

### 6.3 시간 정규화 오류

**에러**: 시간이 올바르게 정규화되지 않음

**해결**:
- `_normalize_time()` 메서드가 자동 호출되는지 확인
- 시간 값이 유효 범위 내인지 확인 (0-23 시간, 0-59 분/초)

## 7. 체크리스트

Time System 사용 전 확인사항:

- [ ] `mvp_schema.sql`의 `session_states`, `triggered_events`, `time_events` 테이블 확인
- [ ] TimeSystem 초기화 및 정리 로직 확인
- [ ] 세션 ID가 올바른 UUID 형식인지 확인
- [ ] 이벤트 핸들러가 비동기 함수인지 확인
- [ ] 시간 가속 배율이 적절한지 확인
- [ ] 틱 핸들러가 가벼운 작업만 수행하는지 확인

## 8. 참고 문서

- `00_CORE/02_ARCHITECTURE_PRINCIPLES.md`: 아키텍처 원칙
- `01_TYPE_SAFETY/UUID_GUIDELINES.md`: UUID 처리 가이드라인
- `01_TYPE_SAFETY/TRANSACTION_GUIDELINES.md`: 트랜잭션 가이드라인
- `03_SYSTEMS/NPC_BEHAVIOR_GUIDELINES.md`: NPC 행동 시스템 가이드라인
- `database/setup/mvp_schema.sql`: **데이터베이스 스키마 (필수 참조)**
- `app/systems/time_system.py`: Time System 구현

