# NPC Behavior System 가이드라인

> **최신화 날짜**: 2026-01-03  
> **적용 범위**: NPC 자동 행동 시스템 개발 시 필수 읽기

## ⚠️ 중요: mvp_schema.sql 참조 필수

**모든 NPC 행동 시스템 관련 작업은 반드시 `database/setup/mvp_schema.sql`을 참조해야 합니다.**

## 1. 개요

NPC Behavior System은 NPC의 자동 행동을 관리하는 시스템으로, 시간대별 행동 패턴을 실행하고 DB 기반 스케줄을 사용합니다.

### 1.1 시스템 구조

```
app/systems/npc_behavior.py
    ↓
NPCBehavior 클래스
    ↓
- EntityManager (엔티티 관리)
- CellManager (셀 이동)
- DialogueManager (대화 처리)
- ActionHandler (행동 실행)
- TimeSystem (시간 시스템)
```

### 1.2 데이터베이스 스키마

**game_data 스키마**:
- `game_data.entity_behavior_schedules`: 엔티티 행동 스케줄 (템플릿)

**스키마 구조**:
```sql
CREATE TABLE game_data.entity_behavior_schedules (
    schedule_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id VARCHAR(50) NOT NULL,
    time_period VARCHAR(20) NOT NULL,  -- 'morning', 'afternoon', 'evening', 'night'
    action_type VARCHAR(50) NOT NULL,  -- 'work', 'rest', 'socialize', 'patrol', 'sleep'
    action_priority INTEGER DEFAULT 1,
    conditions JSONB,  -- 행동 조건
    action_data JSONB,  -- 행동 세부 데이터
    FOREIGN KEY (entity_id) REFERENCES game_data.entities(entity_id) ON DELETE CASCADE
);
```

## 2. 핵심 개념

### 2.1 행동 스케줄

NPC의 시간대별 행동 패턴을 정의합니다:

```python
# DB에 저장된 행동 스케줄 예시
{
    "entity_id": "NPC_MERCHANT_001",
    "time_period": "morning",
    "action_type": "work",
    "action_priority": 1,
    "conditions": {
        "min_energy": 20,
        "weather": "clear"
    },
    "action_data": {
        "duration": 2,
        "location": "shop",
        "target_entity": "merchant"
    }
}
```

### 2.2 시간대별 행동

NPC는 시간대에 따라 다른 행동을 수행합니다:

- **MORNING**: 아침 활동 (일 시작, 상점 오픈 등)
- **AFTERNOON**: 오후 활동 (일상 업무, 휴식 등)
- **EVENING**: 저녁 활동 (저녁 식사, 대화 등)
- **NIGHT**: 밤 활동 (수면, 경비 등)

### 2.3 행동 우선순위

`action_priority`가 낮을수록 우선순위가 높습니다:

```python
# 우선순위 1: 가장 먼저 실행
{
    "action_type": "work",
    "action_priority": 1
}

# 우선순위 2: 그 다음 실행
{
    "action_type": "rest",
    "action_priority": 2
}
```

## 3. NPCBehavior 사용법

### 3.1 초기화

```python
from app.systems.npc_behavior import NPCBehavior
from app.managers.entity_manager import EntityManager
from app.managers.cell_manager import CellManager
from app.managers.dialogue_manager import DialogueManager
from app.handlers.action_handler import ActionHandler
from app.systems.time_system import TimeSystem
from database.connection import DatabaseConnection

# 의존성 초기화
db = DatabaseConnection()
entity_manager = EntityManager(...)
cell_manager = CellManager(...)
dialogue_manager = DialogueManager(...)
action_handler = ActionHandler(...)
time_system = TimeSystem()

# NPCBehavior 초기화
npc_behavior = NPCBehavior(
    db_connection=db,
    entity_manager=entity_manager,
    cell_manager=cell_manager,
    dialogue_manager=dialogue_manager,
    action_handler=action_handler,
    time_system=time_system
)
```

### 3.2 행동 스케줄 로드

```python
# DB에서 NPC 행동 스케줄 로드
success = await npc_behavior.load_npc_behavior_schedules(session_id)

if success:
    print(f"로드된 NPC 수: {len(npc_behavior.npc_routines)}")
```

### 3.3 셀 매핑 설정

```python
# 셀 ID 매핑 설정 (game_cell_id → runtime_cell_id)
cell_mapping = {
    "CELL_SHOP": "runtime_cell_uuid_1",
    "CELL_MARKET": "runtime_cell_uuid_2",
    "CELL_INN": "runtime_cell_uuid_3"
}

npc_behavior.set_cell_mapping(cell_mapping)
```

### 3.4 일과 실행

```python
# NPC의 하루 일과 실행
success = await npc_behavior.execute_daily_routine("NPC_MERCHANT_001")

if success:
    print("일과 실행 완료")
else:
    print("일과 실행 실패")
```

### 3.5 NPC 간 상호작용

```python
# 같은 셀에 있는 다른 NPC와 상호작용
success = await npc_behavior.interact_with_others(
    npc_id="NPC_MERCHANT_001",
    current_cell_id="runtime_cell_uuid_1"
)
```

## 4. 행동 스케줄 데이터 구조

### 4.1 conditions (행동 조건)

```json
{
    "min_energy": 20,      // 최소 에너지
    "max_energy": 100,     // 최대 에너지
    "weather": "clear",    // 날씨 조건
    "mood": "happy",       // 기분 조건
    "location": "shop"     // 위치 조건
}
```

### 4.2 action_data (행동 세부 데이터)

```json
{
    "duration": 2,              // 행동 지속 시간 (시간 단위)
    "location": "shop",          // 목표 위치
    "target_entity": "merchant", // 대상 엔티티
    "interaction_type": "talk"   // 상호작용 타입
}
```

### 4.3 action_type (행동 타입)

**일반 행동**:
- `work`: 일하기
- `rest`: 휴식
- `sleep`: 수면
- `patrol`: 순찰
- `socialize`: 사교 활동

**특수 행동**:
- `move`: 이동
- `talk`: 대화
- `trade`: 거래
- `craft`: 제작

## 5. 데이터베이스 연동

### 5.1 행동 스케줄 조회

NPCBehavior는 자동으로 DB에서 행동 스케줄을 조회합니다:

```python
# load_npc_behavior_schedules() 내부 쿼리
SELECT 
    ebs.entity_id,
    ebs.time_period,
    ebs.action_type,
    ebs.action_priority,
    ebs.conditions,
    ebs.action_data,
    e.entity_name,
    e.entity_type
FROM game_data.entity_behavior_schedules ebs
JOIN game_data.entities e ON ebs.entity_id = e.entity_id
WHERE e.entity_type = 'npc'
ORDER BY ebs.entity_id, ebs.time_period, ebs.action_priority
```

### 5.2 행동 스케줄 생성 예시

```sql
-- 상인 NPC의 아침 행동 스케줄
INSERT INTO game_data.entity_behavior_schedules (
    entity_id,
    time_period,
    action_type,
    action_priority,
    conditions,
    action_data
) VALUES (
    'NPC_MERCHANT_001',
    'morning',
    'work',
    1,
    '{"min_energy": 20, "weather": "clear"}'::jsonb,
    '{"duration": 4, "location": "shop"}'::jsonb
);

-- 상인 NPC의 저녁 행동 스케줄
INSERT INTO game_data.entity_behavior_schedules (
    entity_id,
    time_period,
    action_type,
    action_priority,
    conditions,
    action_data
) VALUES (
    'NPC_MERCHANT_001',
    'evening',
    'rest',
    1,
    '{}'::jsonb,
    '{"duration": 2, "location": "inn"}'::jsonb
);
```

## 6. 사용 원칙

### 6.1 필수 원칙

1. **스케줄 로드 필수**: `load_npc_behavior_schedules()` 호출 필수
2. **셀 매핑 설정**: `set_cell_mapping()` 호출 필수
3. **TimeSystem 연동**: TimeSystem과 연동하여 시간대 확인
4. **트랜잭션 관리**: 행동 실행은 트랜잭션 내에서 수행
5. **에러 처리**: 모든 예외를 명시적으로 처리

### 6.2 권장 사항

1. **우선순위 설계**: 중요한 행동은 낮은 우선순위 설정
2. **조건 명시**: 행동 조건을 명확히 정의
3. **행동 데이터 상세화**: `action_data`에 필요한 모든 정보 포함
4. **로깅**: 행동 실행 시 적절한 로깅

### 6.3 금지 사항

1. **❌ 직접 DB 수정**: `entity_behavior_schedules` 테이블 직접 수정 금지 (게임 데이터 제작 가이드라인 참조)
2. **❌ 무한 루프**: 행동 실행에서 무한 루프 생성 금지
3. **❌ 동기 작업**: 행동 실행에서 동기 I/O 작업 금지
4. **❌ 추측 로직**: 조건 확인 시 추측 로직 금지 (불확정성 불허 원칙)

## 7. 자주 발생하는 에러 및 해결

### 7.1 행동 스케줄 로드 실패

**에러**: `Failed to load NPC behavior schedules`

**해결**:
- `entity_behavior_schedules` 테이블 존재 확인
- `entity_id`가 올바른지 확인
- JSONB 필드 형식 확인

### 7.2 셀 이동 실패

**에러**: `Failed to move NPC to cell`

**해결**:
- 셀 매핑이 올바른지 확인
- `runtime_cell_id`가 존재하는지 확인
- CellManager의 `enter_cell()` 메서드 확인

### 7.3 행동 실행 실패

**에러**: `Failed to execute action`

**해결**:
- `action_type`이 올바른지 확인
- `action_data` 형식 확인
- ActionHandler의 `execute_action()` 메서드 확인

## 8. 체크리스트

NPC Behavior System 사용 전 확인사항:

- [ ] `mvp_schema.sql`의 `entity_behavior_schedules` 테이블 확인
- [ ] NPC 행동 스케줄이 DB에 정의되어 있는지 확인
- [ ] 셀 매핑이 올바르게 설정되었는지 확인
- [ ] TimeSystem이 초기화되어 있는지 확인
- [ ] EntityManager, CellManager, DialogueManager, ActionHandler가 올바르게 초기화되었는지 확인
- [ ] 행동 조건이 올바르게 정의되었는지 확인

## 9. 참고 문서

- `00_CORE/02_ARCHITECTURE_PRINCIPLES.md`: 아키텍처 원칙
- `01_TYPE_SAFETY/UUID_GUIDELINES.md`: UUID 처리 가이드라인
- `01_TYPE_SAFETY/TRANSACTION_GUIDELINES.md`: 트랜잭션 가이드라인
- `02_DATABASE/GAME_DATA_PRODUCTION_GUIDELINES.md`: 게임 데이터 제작 가이드라인
- `03_SYSTEMS/TIME_SYSTEM_GUIDELINES.md`: Time System 가이드라인
- `03_SYSTEMS/DIALOGUE_SYSTEM_GUIDELINES.md`: 대화 시스템 가이드라인
- `database/setup/mvp_schema.sql`: **데이터베이스 스키마 (필수 참조)**
- `app/systems/npc_behavior.py`: NPC Behavior System 구현

