# [deprecated] 추상화 원칙 위반 Audit 보고서

> **Deprecated 날짜**: 2025-12-28  
> **Deprecated 사유**: 이 Audit 보고서는 특정 시점(2025-10-19)의 검수 결과를 기록한 것으로, 발견된 문제점들이 모두 해결되었습니다. 현재는 추상화 원칙이 올바르게 준수되고 있습니다.

## 📋 **Audit 개요**

**Audit 대상**: `app/` 디렉토리의 모든 매니저 클래스 및 시스템 모듈  
**Audit 목적**: DB에 적재할 수 있는 정적 데이터를 코드에서 하드코딩하고 있는지 확인  
**Audit 기준**: `mvp_schema.sql`의 `game_data` 스키마에 정의된 정적 데이터 테이블들  
**Audit 일시**: 2025-10-19  

## 🎯 **Audit 기준**

### **정적 데이터 테이블 목록 (game_data 스키마)**
- `game_data.world_regions` - 지역 정보
- `game_data.world_locations` - 위치 정보  
- `game_data.world_cells` - 셀 정보
- `game_data.entities` - 엔티티 정보
- `game_data.dialogue_contexts` - 대화 컨텍스트
- `game_data.dialogue_topics` - 대화 주제
- `game_data.dialogue_knowledge` - 대화 지식
- `game_data.entity_behavior_schedules` - 엔티티 행동 스케줄
- `game_data.time_events` - 시간 이벤트
- `game_data.effect_carriers` - 효과 캐리어
- `game_data.base_properties` - 기본 속성
- `game_data.abilities_magic` - 마법 능력
- `game_data.abilities_skills` - 스킬 능력
- `game_data.effects` - 효과
- `game_data.equipment_weapons` - 무기 장비
- `game_data.equipment_armors` - 방어구 장비
- `game_data.items` - 아이템
- `game_data.world_objects` - 월드 오브젝트

## 🚨 **발견된 추상화 원칙 위반 사항**

### **1. 심각한 위반 (Critical Violations)**

#### **1.1 TimeSystem - 시간대별 설정 하드코딩**
**파일**: `app/systems/time_system.py`  
**위반 내용**: 
```python
def _set_default_time_periods(self):
    """기본 시간대 설정"""
    self.time_periods = {
        TimePeriod.DAWN: (6, 8),
        TimePeriod.MORNING: (8, 12),
        TimePeriod.LUNCH: (12, 14),
        TimePeriod.AFTERNOON: (14, 18),
        TimePeriod.EVENING: (18, 20),
        TimePeriod.NIGHT: (20, 22),
        TimePeriod.LATE_NIGHT: (22, 6)
    }
    
    self.interaction_probabilities = {
        TimePeriod.DAWN: 0.1,      # 새벽: 10%
        TimePeriod.MORNING: 0.2,   # 오전: 20%
        TimePeriod.LUNCH: 0.8,     # 점심: 80%
        TimePeriod.AFTERNOON: 0.3, # 오후: 30%
        TimePeriod.EVENING: 0.6,   # 저녁: 60%
        TimePeriod.NIGHT: 0.4,     # 밤: 40%
        TimePeriod.LATE_NIGHT: 0.1 # 밤새: 10%
    }
```

**문제점**: 
- 시간대별 설정이 하드코딩되어 있음
- `game_data.time_events` 테이블을 사용해야 함
- 시간대별 행동 패턴도 하드코딩됨

**해결 방안**: DB에서 `game_data.time_events` 테이블을 조회하여 동적으로 로드

#### **1.2 TimeSystem - 시간대별 행동 패턴 하드코딩**
**파일**: `app/systems/time_system.py`  
**위반 내용**:
```python
def get_time_period_actions(self, period: TimePeriod) -> List[str]:
    """시간대별 가능한 행동 목록 반환 (DB 기반)"""
    # 향후 DB에서 로드할 수 있도록 확장 가능
    actions_by_period = {
        TimePeriod.DAWN: ["wake_up", "prepare", "move_to_work"],
        TimePeriod.MORNING: ["work", "business", "patrol"],
        TimePeriod.LUNCH: ["move_to_square", "socialize", "eat"],
        TimePeriod.AFTERNOON: ["work", "business", "patrol", "explore"],
        TimePeriod.EVENING: ["socialize", "interact", "gather"],
        TimePeriod.NIGHT: ["story_telling", "relax", "prepare_sleep"],
        TimePeriod.LATE_NIGHT: ["sleep", "rest", "return_home"]
    }
```

**문제점**: 
- 시간대별 행동 패턴이 하드코딩되어 있음
- `game_data.entity_behavior_schedules` 테이블을 사용해야 함

**해결 방안**: DB에서 `game_data.entity_behavior_schedules` 테이블을 조회하여 동적으로 로드

#### **1.3 DialogueManager - 대화 템플릿 하드코딩**
**파일**: `app/interaction/dialogue_manager.py`  
**위반 내용**:
```python
self.response_templates = {
    "greeting": [
        "안녕하세요! 무엇을 도와드릴까요?",
        "오, 새로운 얼굴이군요!",
        "여기서 뭘 하고 계신가요?",
        "반갑습니다! 여기 처음 오신 건가요?"
    ],
    "trade": [
        "거래를 원하시는군요. 무엇을 사고 싶으신가요?",
        "상점에 오신 것을 환영합니다!",
        "좋은 물건들이 많이 있습니다.",
        "특별한 할인을 해드릴 수 있습니다."
    ],
    # ... 더 많은 하드코딩된 템플릿들
}
```

**문제점**: 
- 대화 템플릿이 하드코딩되어 있음
- `game_data.dialogue_contexts`와 `game_data.dialogue_topics` 테이블을 사용해야 함

**해결 방안**: DB에서 `game_data.dialogue_contexts`와 `game_data.dialogue_topics` 테이블을 조회하여 동적으로 로드

### **2. 중간 수준 위반 (Medium Violations)**

#### **2.1 CellManager - 기본값 하드코딩**
**파일**: `app/world/cell_manager.py`  
**위반 내용**:
```python
cell_data = CellData(
    cell_id=cell_id,
    name=row['cell_name'],
    description=row['cell_description'],
    location_id=row['location_id'],
    properties=cell_properties or {},
    status=CellStatus.ACTIVE,  # 기본값
    cell_type=CellType.INDOOR,  # 기본값
    size={"width": row['matrix_width'], "height": row['matrix_height']},
    created_at=datetime.now(),  # 기본값
    updated_at=datetime.now()  # 기본값
)
```

**문제점**: 
- `CellStatus.ACTIVE`와 `CellType.INDOOR`가 하드코딩됨
- DB에서 셀의 실제 상태와 타입을 조회해야 함

**해결 방안**: DB에서 셀의 실제 상태와 타입 정보를 조회

#### **2.2 ActionHandler - 응답 템플릿 하드코딩**
**파일**: `app/interaction/action_handler.py`  
**위반 내용**:
```python
responses = {
    "greeting": [
        f"{target.name}: 안녕하세요! 무엇을 도와드릴까요?",
        f"{target.name}: 오, 새로운 얼굴이군요!",
        f"{target.name}: 여기서 뭘 하고 계신가요?",
        f"{target.name}: 반갑습니다! 여기 처음 오신 건가요?"
    ],
    # ... 더 많은 하드코딩된 응답들
}
```

**문제점**: 
- 액션별 응답 템플릿이 하드코딩되어 있음
- `game_data.dialogue_contexts` 테이블을 사용해야 함

**해결 방안**: DB에서 `game_data.dialogue_contexts` 테이블을 조회하여 동적으로 로드

### **3. 경미한 위반 (Minor Violations)**

#### **3.1 기본값 하드코딩**
**파일**: 여러 파일  
**위반 내용**: 
- `CellData`의 기본 크기: `{"width": 20, "height": 20}`
- `EntityData`의 기본 위치: `{"x": 0.0, "y": 0.0}`
- 기본 상태값들: `EntityStatus.ACTIVE`, `CellStatus.ACTIVE`

**문제점**: 
- 기본값들이 하드코딩되어 있음
- DB에서 기본값을 조회할 수 있음

**해결 방안**: DB에서 기본값을 조회하거나 설정 테이블을 별도로 관리

## 📊 **위반 사항 요약**

| 위반 유형 | 심각도 | 파일 수 | 위반 사항 수 |
|-----------|--------|---------|-------------|
| 시간대별 설정 하드코딩 | Critical | 1 | 2 |
| 대화 템플릿 하드코딩 | Critical | 1 | 1 |
| 기본값 하드코딩 | Medium | 2 | 2 |
| 응답 템플릿 하드코딩 | Medium | 1 | 1 |
| 기타 기본값 하드코딩 | Minor | 3 | 3 |

**총 위반 사항**: 9개  
**Critical**: 3개  
**Medium**: 3개  
**Minor**: 3개  

## 🔧 **권장 해결 방안**

### **1. 즉시 수정 필요 (Critical)**
1. **TimeSystem 추상화**: `game_data.time_events` 테이블에서 시간대별 설정 로드
2. **DialogueManager 추상화**: `game_data.dialogue_contexts`와 `game_data.dialogue_topics` 테이블에서 대화 템플릿 로드
3. **NPC 행동 패턴 추상화**: `game_data.entity_behavior_schedules` 테이블에서 행동 패턴 로드

### **2. 단기 수정 필요 (Medium)**
1. **CellManager 기본값**: DB에서 셀의 실제 상태와 타입 조회
2. **ActionHandler 응답**: DB에서 액션별 응답 템플릿 로드

### **3. 장기 개선 필요 (Minor)**
1. **기본값 관리**: 설정 테이블을 별도로 생성하여 기본값 관리
2. **템플릿 시스템**: 모든 템플릿을 DB에서 관리하는 시스템 구축

## 📝 **결론**

현재 `app/` 디렉토리의 매니저 클래스들에서 **9개의 추상화 원칙 위반 사항**이 발견되었습니다. 특히 **TimeSystem**과 **DialogueManager**에서 심각한 하드코딩 문제가 발견되어 즉시 수정이 필요합니다.

모든 정적 데이터는 `game_data` 스키마의 해당 테이블에서 동적으로 로드하도록 수정해야 하며, 이를 통해 진정한 추상화 원칙을 준수할 수 있습니다.
