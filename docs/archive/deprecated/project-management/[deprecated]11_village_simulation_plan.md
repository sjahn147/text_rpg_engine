# [deprecated] 마을 시뮬레이션 구현 기획서

> **Deprecated 날짜**: 2025-12-28  
> **Deprecated 이유**: 마을 시뮬레이션이 Phase 3에서 완료되어 더 이상 진행 중인 작업이 아님. 100일 마을 시뮬레이션이 성공적으로 완료되었으며 (228 대화, 833 행동), 현재는 Phase 4+ 개발이 진행 중임.  
> **작성일**: 2025-10-18  
> **목표**: 기존 Manager 클래스들을 활용한 마을 주민 자동 행동 시스템  
> **핵심**: DB 트랜잭션을 통한 모든 상호작용 추적 및 누적

## 🎯 **핵심 철학**

- **시뮬레이션 = 테스트**: 우리 관점의 시뮬레이션은 실제로는 테스트 코드
- **DB 관점 = 런타임 데이터**: DB에서는 단순히 런타임 데이터가 누적됨
- **기존 매니저 활용**: 새로운 시뮬레이션 모듈이 아닌 기존 Manager 클래스들 조합
- **미시적 추적**: 셀 이동 수준까지 모든 행동을 DB에 기록

## 🏘️ **마을 구성**

### **마을 구조**
```
레크로스타 마을
├── 마을 광장 (LOC_VILLAGE_SQUARE_001)
│   ├── 광장 중심 (CELL_SQUARE_CENTER_001)
│   └── 분수대 (CELL_SQUARE_FOUNTAIN_001)
├── 상점가 (LOC_SHOP_DISTRICT_001)
│   ├── 무기상 (CELL_WEAPON_SHOP_001)
│   └── 잡화상 (CELL_GENERAL_SHOP_001)
└── 주거지 (LOC_HOUSING_DISTRICT_001)
    ├── 상인 집 (CELL_MERCHANT_HOUSE_001)
    └── 농부 집 (CELL_FARMER_HOUSE_001)
```

### **NPC 구성 (5명)**
1. **상인 토마스** (MERCHANT_THOMAS_001)
   - 직업: 무기상
   - 기본 위치: CELL_WEAPON_SHOP_001
   - 성격: 친근하고 상업적

2. **농부 존** (FARMER_JOHN_001)
   - 직업: 농부
   - 기본 위치: CELL_FARMER_HOUSE_001
   - 성격: 소박하고 정직

3. **여관주인 마리아** (INNKEEPER_MARIA_001)
   - 직업: 여관주인
   - 기본 위치: CELL_SQUARE_CENTER_001
   - 성격: 따뜻하고 관대

4. **수호병 알렉스** (GUARD_ALEX_001)
   - 직업: 마을 수호병
   - 기본 위치: CELL_SQUARE_CENTER_001
   - 성격: 책임감 있고 엄격

5. **여행자 엘라** (TRAVELER_ELLA_001)
   - 직업: 여행자
   - 기본 위치: CELL_SQUARE_FOUNTAIN_001
   - 성격: 호기심 많고 모험적

## ⏰ **시간 시스템 (추상화된 시스템 모듈)**

### **시간 진행 규칙**
- **1시간 = 1초**: 실제 시간 1초당 게임 시간 1시간
- **24시간 사이클**: 하루가 완료되면 다시 00:00부터 시작
- **시간대별 행동**: 각 시간대에 따른 고정된 행동 패턴

### **시간대별 행동 패턴**
```
06:00-08:00  | 새벽     | 농부 일어나기, 상인 상점 준비
08:00-12:00  | 오전     | 상점 영업, 농부 일하기, 여관주인 준비
12:00-14:00  | 점심     | 모든 NPC 광장에서 만남, 대화
14:00-18:00  | 오후     | 각자 업무, 셀 이동
18:00-20:00  | 저녁     | 상호작용 시간, 대화
20:00-22:00  | 밤       | 이야기 시간, 셀 이동
22:00-06:00  | 밤새     | 각자 집으로 돌아가기, 휴식
```

## 🎭 **NPC 행동 패턴 (기존 Manager 조합)**

### **1. 상인 토마스 (MERCHANT_THOMAS_001)**
**사용 매니저**: `EntityManager`, `CellManager`, `ActionHandler`, `DialogueManager`

**일과**:
- 06:00-07:00: 집에서 일어나기 (`EntityManager.update_entity`)
- 07:00-08:00: 상점으로 이동 (`CellManager.enter_cell`)
- 08:00-12:00: 상점 영업 (`ActionHandler.handle_trade`)
- 12:00-14:00: 광장으로 이동, 다른 NPC와 대화 (`DialogueManager.start_dialogue`)
- 14:00-18:00: 상점으로 돌아가서 영업 (`ActionHandler.handle_trade`)
- 18:00-20:00: 광장에서 상호작용 (`DialogueManager.continue_dialogue`)
- 20:00-22:00: 집으로 이동 (`CellManager.enter_cell`)
- 22:00-06:00: 휴식 (`EntityManager.update_entity`)

**DB 추적 데이터**:
- 셀 이동 기록: `runtime_data.cell_occupants`
- 대화 기록: `runtime_data.dialogue_sessions`
- 액션 기록: `runtime_data.action_logs`
- 엔티티 상태: `runtime_data.runtime_entities`

### **2. 농부 존 (FARMER_JOHN_001)**
**사용 매니저**: `EntityManager`, `CellManager`, `ActionHandler`

**일과**:
- 06:00-08:00: 집에서 일어나기, 농장 준비
- 08:00-12:00: 농장에서 일하기 (`ActionHandler.handle_work`)
- 12:00-14:00: 광장으로 이동, 다른 NPC와 대화
- 14:00-18:00: 농장으로 돌아가서 일하기
- 18:00-20:00: 광장에서 상호작용
- 20:00-22:00: 집으로 이동
- 22:00-06:00: 휴식

**DB 추적 데이터**:
- 작업 기록: `runtime_data.action_logs`
- 위치 변경: `runtime_data.cell_occupants`
- 상태 변화: `runtime_data.runtime_entities`

### **3. 여관주인 마리아 (INNKEEPER_MARIA_001)**
**사용 매니저**: `EntityManager`, `CellManager`, `DialogueManager`, `ActionHandler`

**일과**:
- 06:00-08:00: 여관 준비 (`ActionHandler.handle_prepare`)
- 08:00-12:00: 여관 영업 (`ActionHandler.handle_service`)
- 12:00-14:00: 광장에서 다른 NPC와 대화
- 14:00-18:00: 여관으로 돌아가서 영업
- 18:00-20:00: 광장에서 상호작용
- 20:00-22:00: 여관으로 이동
- 22:00-06:00: 휴식

### **4. 수호병 알렉스 (GUARD_ALEX_001)**
**사용 매니저**: `EntityManager`, `CellManager`, `ActionHandler`

**일과**:
- 06:00-08:00: 순찰 시작 (`ActionHandler.handle_patrol`)
- 08:00-12:00: 마을 순찰 (여러 셀 이동)
- 12:00-14:00: 광장에서 다른 NPC와 대화
- 14:00-18:00: 순찰 계속
- 18:00-20:00: 광장에서 상호작용
- 20:00-22:00: 순찰 마무리
- 22:00-06:00: 휴식

### **5. 여행자 엘라 (TRAVELER_ELLA_001)**
**사용 매니저**: `EntityManager`, `CellManager`, `DialogueManager`, `ActionHandler`

**일과**:
- 06:00-08:00: 분수대에서 일어나기
- 08:00-12:00: 마을 탐험 (여러 셀 이동)
- 12:00-14:00: 광장에서 다른 NPC와 대화
- 14:00-18:00: 마을 탐험 계속
- 18:00-20:00: 광장에서 상호작용
- 20:00-22:00: 분수대로 이동
- 22:00-06:00: 휴식

## 🔄 **상호작용 패턴**

### **점심시간 (12:00-14:00) 상호작용**
- **확률**: 80% 확률로 대화 발생
- **참여자**: 광장에 있는 모든 NPC
- **대화 주제**: 
  - 상인 토마스: 거래, 소문
  - 농부 존: 잡담, 도움
  - 여관주인 마리아: 인사, 이야기
  - 수호병 알렉스: 소문, 도움
  - 여행자 엘라: 이야기, 소문

### **저녁시간 (18:00-20:00) 상호작용**
- **확률**: 60% 확률로 대화 발생
- **참여자**: 광장에 있는 NPC들
- **대화 주제**: 하루 일과, 소문, 이야기

## 📊 **DB 추적 데이터**

### **필수 추적 항목**
1. **셀 이동**: `runtime_data.cell_occupants` 테이블
2. **대화 기록**: `runtime_data.dialogue_sessions` 테이블
3. **액션 기록**: `runtime_data.action_logs` 테이블
4. **엔티티 상태**: `runtime_data.runtime_entities` 테이블
5. **이벤트 기록**: `runtime_data.runtime_events` 테이블

### **미시적 추적 예시**
```sql
-- 셀 이동 추적
INSERT INTO runtime_data.cell_occupants (cell_id, entity_id, entity_type, entered_at)
VALUES ('CELL_SQUARE_CENTER_001', 'MERCHANT_THOMAS_001', 'NPC', NOW());

-- 대화 시작 추적
INSERT INTO runtime_data.dialogue_sessions (session_id, player_id, npc_id, started_at)
VALUES ('SESSION_001', 'MERCHANT_THOMAS_001', 'FARMER_JOHN_001', NOW());

-- 액션 실행 추적
INSERT INTO runtime_data.action_logs (log_id, entity_id, action_type, target_id, result, timestamp)
VALUES ('LOG_001', 'MERCHANT_THOMAS_001', 'move', 'CELL_SQUARE_CENTER_001', 'success', NOW());
```

## 🧪 **테스트 구현 계획**

### **1. 시간 시스템 모듈** (`app/systems/time_system.py`)
```python
class TimeSystem:
    """게임 시간 관리 시스템"""
    async def tick_hour(self) -> None:
        """1시간 진행"""
        pass
    
    async def get_current_time(self) -> int:
        """현재 시간 반환 (0-23)"""
        pass
    
    async def get_time_period(self, hour: int) -> str:
        """시간대 반환 (dawn, morning, lunch, afternoon, evening, night)"""
        pass
```

### **2. NPC 행동 시스템** (`app/systems/npc_behavior.py`)
```python
class NPCBehavior:
    """NPC 자동 행동 시스템"""
    async def execute_daily_routine(self, npc_id: str) -> None:
        """NPC의 하루 일과 실행"""
        pass
    
    async def move_to_cell(self, npc_id: str, cell_id: str) -> None:
        """NPC 셀 이동"""
        pass
    
    async def interact_with_others(self, npc_id: str, current_cell_id: str) -> None:
        """다른 NPC와 상호작용"""
        pass
```

### **3. 마을 시뮬레이션 테스트** (`tests/simulation/test_village_simulation.py`)
```python
class TestVillageSimulation:
    """마을 시뮬레이션 테스트"""
    
    async def test_100_day_simulation(self):
        """100일 시뮬레이션 실행"""
        pass
    
    async def test_npc_daily_routine(self):
        """NPC 하루 일과 테스트"""
        pass
    
    async def test_interactions(self):
        """NPC 상호작용 테스트"""
        pass
```

## 🎯 **성공 지표**

### **기능적 지표**
1. **100회 연속 실행**: 시뮬레이션 100회 연속 성공
2. **엔티티 행동**: 각 NPC가 시간대별 행동 수행
3. **상호작용**: NPC 간 의미 있는 상호작용 발생
4. **데이터 일관성**: DB 데이터 무결성 유지

### **성능 지표**
1. **실행 시간**: 100회 실행 시간 < 10분
2. **메모리 사용량**: 안정적인 메모리 사용
3. **DB 성능**: 트랜잭션 처리 시간 < 100ms

### **데이터 지표**
1. **셀 이동 기록**: 모든 셀 이동이 DB에 기록
2. **대화 기록**: 모든 대화가 DB에 기록
3. **액션 기록**: 모든 액션이 DB에 기록
4. **상태 변화**: 모든 상태 변화가 DB에 기록

## 🚀 **구현 순서**

### **Phase 1: 시간 시스템 구현**
1. `app/systems/time_system.py` 구현
2. 시간 진행 및 시간대 관리
3. 시간 시스템 테스트

### **Phase 2: NPC 행동 시스템 구현**
1. `app/systems/npc_behavior.py` 구현
2. 기존 Manager 클래스들 조합
3. NPC 행동 테스트

### **Phase 3: 마을 시뮬레이션 테스트**
1. `tests/simulation/test_village_simulation.py` 구현
2. 100회 연속 실행 테스트
3. DB 데이터 누적 확인

### **Phase 4: 최적화 및 모니터링**
1. 성능 최적화
2. 메모리 사용량 모니터링
3. DB 성능 모니터링

---

**핵심**: 기존 Manager 클래스들을 조합하여 마을 주민들의 자동 행동을 구현하고, 모든 상호작용을 DB에 기록하여 누적되는 것을 확인하는 것이 목표입니다.
