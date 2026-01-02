# 가상 마을 시뮬레이션 설계

> **설계일**: 2025-10-18  
> **목표**: 자동화된 마을 시뮬레이션 시스템 구현  
> **핵심**: 엔티티 자동 행동 + 시간대별 반복 + 상호작용

## 🏘️ **가상 마을 구성**

### **마을 구조**
```
레크로스타 마을 (REG_NORTH_FOREST_001)
├── 마을 광장 (LOC_FOREST_VILLAGE_001)
│   ├── 광장 중심 (CELL_VILLAGE_CENTER_001)
│   └── 분수대 (CELL_VILLAGE_FOUNTAIN_001)
├── 상점가 (LOC_FOREST_SHOP_001)
│   ├── 무기상 (CELL_SHOP_WEAPON_001)
│   └── 잡화상 (CELL_SHOP_GENERAL_001)
└── 주거지 (LOC_FOREST_HOUSING_001)
    ├── 상인 집 (CELL_MERCHANT_HOUSE_001)
    └── 농부 집 (CELL_FARMER_HOUSE_001)
```

### **엔티티 구성 (5명)**
1. **상인 토마스** (MERCHANT_THOMAS_001)
   - 타입: NPC
   - 직업: 무기상
   - 위치: CELL_SHOP_WEAPON_001
   - 성격: 친근하고 상업적

2. **농부 존** (FARMER_JOHN_001)
   - 타입: NPC
   - 직업: 농부
   - 위치: CELL_FARMER_HOUSE_001
   - 성격: 소박하고 정직

3. **여관주인 마리아** (INNKEEPER_MARIA_001)
   - 타입: NPC
   - 직업: 여관주인
   - 위치: CELL_VILLAGE_CENTER_001
   - 성격: 따뜻하고 관대

4. **수호병 알렉스** (GUARD_ALEX_001)
   - 타입: NPC
   - 직업: 마을 수호병
   - 위치: CELL_VILLAGE_CENTER_001
   - 성격: 책임감 있고 엄격

5. **여행자 엘라** (TRAVELER_ELLA_001)
   - 타입: NPC
   - 직업: 여행자
   - 위치: CELL_VILLAGE_FOUNTAIN_001
   - 성격: 호기심 많고 모험적

## ⏰ **시간 시스템**

### **하루 사이클 (24시간)**
```
06:00 - 08:00  | 새벽 (Dawn)     | 농부 존 일어나기, 상인 토마스 상점 준비
08:00 - 12:00  | 오전 (Morning)  | 상점 영업, 농부 일하기, 여관주인 마리아 준비
12:00 - 14:00  | 점심 (Lunch)     | 모든 NPC 점심 시간, 광장에서 만남
14:00 - 18:00  | 오후 (Afternoon)| 상점 영업, 농부 일하기, 수호병 알렉스 순찰
18:00 - 20:00  | 저녁 (Evening)  | 상점 마감, 농부 귀가, 여관주인 마리아 저녁 준비
20:00 - 22:00  | 밤 (Night)      | 모든 NPC 저녁 시간, 광장에서 대화
22:00 - 06:00  | 밤새 (Late Night)| 모든 NPC 잠자리, 여행자 엘라 야간 탐험
```

### **시간 진행 시스템**
```python
class TimeSystem:
    def __init__(self):
        self.current_time = 6  # 06:00 시작
        self.day = 1
        self.time_speed = 1  # 1분 = 1시간
    
    async def tick(self):
        """시간 틱 (1시간씩 진행)"""
        self.current_time += 1
        if self.current_time >= 24:
            self.current_time = 0
            self.day += 1
    
    def get_time_period(self) -> str:
        """현재 시간대 반환"""
        if 6 <= self.current_time < 8:
            return "dawn"
        elif 8 <= self.current_time < 12:
            return "morning"
        elif 12 <= self.current_time < 14:
            return "lunch"
        elif 14 <= self.current_time < 18:
            return "afternoon"
        elif 18 <= self.current_time < 20:
            return "evening"
        elif 20 <= self.current_time < 22:
            return "night"
        else:
            return "late_night"
```

## 🤖 **엔티티 자동 행동 시스템**

### **행동 타입 정의**
```python
class EntityActionType(str, Enum):
    WAKE_UP = "wake_up"           # 일어나기
    MOVE = "move"                 # 이동
    WORK = "work"                 # 일하기
    EAT = "eat"                   # 식사
    TALK = "talk"                 # 대화
    TRADE = "trade"               # 거래
    SLEEP = "sleep"              # 잠자기
    PATROL = "patrol"             # 순찰
    EXPLORE = "explore"           # 탐험
    REST = "rest"                 # 휴식
```

### **엔티티별 행동 패턴**

#### **상인 토마스 (MERCHANT_THOMAS_001)**
```python
merchant_schedule = {
    "dawn": [EntityActionType.WAKE_UP, EntityActionType.MOVE],
    "morning": [EntityActionType.WORK, EntityActionType.TRADE],
    "lunch": [EntityActionType.EAT, EntityActionType.TALK],
    "afternoon": [EntityActionType.WORK, EntityActionType.TRADE],
    "evening": [EntityActionType.MOVE, EntityActionType.REST],
    "night": [EntityActionType.TALK, EntityActionType.EAT],
    "late_night": [EntityActionType.SLEEP]
}
```

#### **농부 존 (FARMER_JOHN_001)**
```python
farmer_schedule = {
    "dawn": [EntityActionType.WAKE_UP, EntityActionType.MOVE],
    "morning": [EntityActionType.WORK, EntityActionType.WORK],
    "lunch": [EntityActionType.EAT, EntityActionType.TALK],
    "afternoon": [EntityActionType.WORK, EntityActionType.WORK],
    "evening": [EntityActionType.MOVE, EntityActionType.REST],
    "night": [EntityActionType.TALK, EntityActionType.EAT],
    "late_night": [EntityActionType.SLEEP]
}
```

#### **여관주인 마리아 (INNKEEPER_MARIA_001)**
```python
innkeeper_schedule = {
    "dawn": [EntityActionType.WAKE_UP, EntityActionType.MOVE],
    "morning": [EntityActionType.WORK, EntityActionType.TALK],
    "lunch": [EntityActionType.EAT, EntityActionType.TALK],
    "afternoon": [EntityActionType.WORK, EntityActionType.TALK],
    "evening": [EntityActionType.WORK, EntityActionType.TALK],
    "night": [EntityActionType.TALK, EntityActionType.EAT],
    "late_night": [EntityActionType.SLEEP]
}
```

#### **수호병 알렉스 (GUARD_ALEX_001)**
```python
guard_schedule = {
    "dawn": [EntityActionType.WAKE_UP, EntityActionType.PATROL],
    "morning": [EntityActionType.PATROL, EntityActionType.TALK],
    "lunch": [EntityActionType.EAT, EntityActionType.TALK],
    "afternoon": [EntityActionType.PATROL, EntityActionType.PATROL],
    "evening": [EntityActionType.PATROL, EntityActionType.TALK],
    "night": [EntityActionType.TALK, EntityActionType.EAT],
    "late_night": [EntityActionType.SLEEP]
}
```

#### **여행자 엘라 (TRAVELER_ELLA_001)**
```python
traveler_schedule = {
    "dawn": [EntityActionType.SLEEP, EntityActionType.SLEEP],
    "morning": [EntityActionType.WAKE_UP, EntityActionType.EXPLORE],
    "lunch": [EntityActionType.EAT, EntityActionType.TALK],
    "afternoon": [EntityActionType.EXPLORE, EntityActionType.TALK],
    "evening": [EntityActionType.TALK, EntityActionType.EAT],
    "night": [EntityActionType.TALK, EntityActionType.EAT],
    "late_night": [EntityActionType.EXPLORE, EntityActionType.EXPLORE]
}
```

## 🔄 **상호작용 시스템**

### **상호작용 타입**
```python
class InteractionType(str, Enum):
    GREETING = "greeting"         # 인사
    SMALL_TALK = "small_talk"     # 잡담
    TRADE = "trade"               # 거래
    GOSSIP = "gossip"             # 소문
    HELP = "help"                 # 도움
    STORY = "story"              # 이야기
    GOODBYE = "goodbye"           # 작별
```

### **상호작용 규칙**
1. **같은 셀에 있는 엔티티들만 상호작용 가능**
2. **시간대별 상호작용 확률**
   - 점심시간 (12:00-14:00): 80% 확률로 대화
   - 저녁시간 (18:00-20:00): 60% 확률로 대화
   - 밤시간 (20:00-22:00): 40% 확률로 대화
3. **엔티티별 상호작용 선호도**
   - 상인 토마스: 거래, 소문
   - 농부 존: 잡담, 도움
   - 여관주인 마리아: 인사, 이야기
   - 수호병 알렉스: 소문, 도움
   - 여행자 엘라: 이야기, 소문

## 📊 **시뮬레이션 메트릭스**

### **성공 지표**
1. **100회 연속 실행**: 시뮬레이션 100회 연속 성공
2. **엔티티 행동**: 각 엔티티가 시간대별 행동 수행
3. **상호작용**: 엔티티 간 의미 있는 상호작용 발생
4. **데이터 일관성**: DB 데이터 무결성 유지
5. **성능**: 100회 실행 시간 < 10분

### **모니터링 데이터**
```python
class SimulationMetrics:
    def __init__(self):
        self.total_actions = 0
        self.successful_actions = 0
        self.failed_actions = 0
        self.interactions = 0
        self.errors = []
        self.execution_time = 0
        self.memory_usage = 0
```

## 🧪 **테스트 계획**

### **1. 단위 기능 테스트**
- **엔티티 행동 테스트**: 각 행동 타입별 테스트
- **시간 시스템 테스트**: 시간 진행 및 시간대 변경 테스트
- **상호작용 테스트**: 엔티티 간 상호작용 로직 테스트

### **2. 시나리오 테스트**
- **하루 시나리오**: 24시간 시뮬레이션
- **특정 상황 시나리오**: 점심시간, 저녁시간 집중 테스트
- **엔티티별 시나리오**: 각 엔티티의 하루 일과 테스트

### **3. 통합 테스트**
- **전체 시스템 테스트**: 모든 모듈 연동 테스트
- **성능 테스트**: 100회 연속 실행 성능 테스트
- **데이터 무결성 테스트**: DB 데이터 일관성 테스트

### **4. 마을 시뮬레이션**
- **100회 반복 실행**: 자동화된 시뮬레이션
- **결과 분석**: 각 실행 결과 분석 및 리포트
- **최적화**: 성능 및 안정성 최적화
