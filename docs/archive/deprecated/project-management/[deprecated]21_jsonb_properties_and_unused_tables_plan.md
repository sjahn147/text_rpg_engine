# [deprecated] JSONB Properties 및 미사용 테이블 활용 기획서

> **Deprecated 날짜**: 2025-12-28  
> **Deprecated 이유**: JSONB Properties 체계화 작업이 완료되어 더 이상 진행 중인 작업이 아님. 현재는 Phase 4+ 개발이 진행 중이며, 이 기획서의 목표들은 대부분 달성되었음.  
**작성일**: 2025-10-19  
**프로젝트**: RPG Engine - Story Engine  
**버전**: v0.4.0  
**목표**: JSONB Properties 체계화 및 미사용 테이블 활용 방안

## 🎯 **요구사항 분석**

### **1. JSONB Properties 체계화**
- 현재 JSONB 컬럼들의 properties 구조가 일관성 없음
- 콘텐츠 개발 시 properties 타입 안전성 부족
- Factory 패턴으로 properties 생성 보장 필요

### **2. 미사용 테이블 활용**
- DB 스키마에 41개 테이블 중 일부가 Manager에서 활용되지 않음
- 준비된 테이블들의 잠재적 활용 방안 필요

## 📋 **현재 JSONB Properties 현황 분석**

### **1. 주요 JSONB 컬럼 및 Properties 구조**

#### **Entity Properties (entities.entity_properties)**
```json
{
  "personality": "string",
  "alignment": "string", 
  "background": "string",
  "position": {"x": "number", "y": "number"},
  "status": "string",
  "level": "number",
  "experience": "number"
}
```

#### **Cell Properties (world_cells.cell_properties)**
```json
{
  "terrain": "string",
  "lighting": "string", 
  "temperature": "number",
  "humidity": "number",
  "accessibility": "boolean",
  "special_properties": ["string"]
}
```

#### **Effect Properties (effect_carriers.effect_json)**
```json
{
  "effect_type": "string",
  "magnitude": "number",
  "duration": "number",
  "target": "string",
  "conditions": ["string"]
}
```

#### **Dialogue Properties (dialogue_contexts.available_topics)**
```json
{
  "topics": ["string"],
  "default_topic": "string",
  "priority": "number"
}
```

### **2. 현재 Factory 패턴 분석**
- `GameDataFactory`: 정적 데이터 생성
- `InstanceFactory`: 런타임 인스턴스 생성
- Properties 검증 로직 부족

## 📊 **미사용 테이블 분석**

### **1. 현재 활용되지 않는 테이블들**

#### **game_data 스키마**
- `abilities_magic` - 마법 능력 (Manager 미활용)
- `abilities_skills` - 스킬 능력 (Manager 미활용)  
- `equipment_armors` - 방어구 (Manager 미활용)
- `equipment_weapons` - 무기 (Manager 미활용)
- `items` - 아이템 (Manager 미활용)
- `events` - 이벤트 (Manager 미활용)
- `time_events` - 시간 이벤트 (Manager 미활용)
- `dialogue_knowledge` - 대화 지식 (Manager 미활용)

#### **runtime_data 스키마**
- `entity_states` - 엔티티 상태 (부분적 활용)
- `object_states` - 오브젝트 상태 (미활용)
- `event_consequences` - 이벤트 결과 (미활용)
- `player_choices` - 플레이어 선택 (미활용)
- `session_states` - 세션 상태 (미활용)

### **2. 잠재적 활용 방안**

#### **A. 능력 시스템 (Abilities)**
- `abilities_magic`, `abilities_skills` → `AbilityManager` 구현
- 마법/스킬 시스템 통합

#### **B. 장비 시스템 (Equipment)**
- `equipment_armors`, `equipment_weapons` → `EquipmentManager` 구현
- 인벤토리 시스템 확장

#### **C. 이벤트 시스템 (Events)**
- `events`, `time_events` → `EventManager` 구현
- 스케줄링 시스템 통합

#### **D. 지식 시스템 (Knowledge)**
- `dialogue_knowledge` → `KnowledgeManager` 구현
- 대화 시스템 확장

## 🛠️ **구현 방안**

### **Phase 1: JSONB Properties 체계화 (1주)**

#### **1.1 Properties 스키마 정의**
```python
# Properties 타입 정의
class EntityProperties(BaseModel):
    personality: str
    alignment: Optional[str] = None
    background: Optional[str] = None
    position: Position
    status: str = "active"
    level: int = 1
    experience: int = 0

class CellProperties(BaseModel):
    terrain: str
    lighting: str
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    accessibility: bool = True
    special_properties: List[str] = []
```

#### **1.2 Properties Factory 구현**
```python
class PropertiesFactory:
    @staticmethod
    def create_entity_properties(
        personality: str,
        position: Position,
        **kwargs
    ) -> EntityProperties:
        """엔티티 속성 생성"""
        return EntityProperties(
            personality=personality,
            position=position,
            **kwargs
        )
    
    @staticmethod
    def create_cell_properties(
        terrain: str,
        lighting: str,
        **kwargs
    ) -> CellProperties:
        """셀 속성 생성"""
        return CellProperties(
            terrain=terrain,
            lighting=lighting,
            **kwargs
        )
```

#### **1.3 Properties 검증 시스템**
```python
class PropertiesValidator:
    def validate_entity_properties(self, data: Dict[str, Any]) -> bool:
        """엔티티 속성 검증"""
        try:
            EntityProperties(**data)
            return True
        except ValidationError:
            return False
    
    def validate_cell_properties(self, data: Dict[str, Any]) -> bool:
        """셀 속성 검증"""
        try:
            CellProperties(**data)
            return True
        except ValidationError:
            return False
```

### **Phase 2: 미사용 테이블 활용 (2주)**

#### **2.1 AbilityManager 구현**
```python
class AbilityManager:
    """능력 시스템 관리"""
    
    async def create_magic_ability(
        self,
        magic_id: str,
        name: str,
        mana_cost: int,
        cast_time: int,
        magic_school: str,
        properties: Dict[str, Any]
    ) -> str:
        """마법 능력 생성"""
        pass
    
    async def create_skill_ability(
        self,
        skill_id: str,
        name: str,
        skill_type: str,
        properties: Dict[str, Any]
    ) -> str:
        """스킬 능력 생성"""
        pass
```

#### **2.2 EquipmentManager 구현**
```python
class EquipmentManager:
    """장비 시스템 관리"""
    
    async def create_armor(
        self,
        armor_id: str,
        name: str,
        defense: int,
        armor_type: str,
        properties: Dict[str, Any]
    ) -> str:
        """방어구 생성"""
        pass
    
    async def create_weapon(
        self,
        weapon_id: str,
        name: str,
        damage: int,
        weapon_type: str,
        properties: Dict[str, Any]
    ) -> str:
        """무기 생성"""
        pass
```

#### **2.3 EventManager 구현**
```python
class EventManager:
    """이벤트 시스템 관리"""
    
    async def create_event(
        self,
        event_id: str,
        name: str,
        event_type: str,
        properties: Dict[str, Any]
    ) -> str:
        """이벤트 생성"""
        pass
    
    async def schedule_time_event(
        self,
        event_name: str,
        trigger_day: int,
        trigger_hour: int,
        event_data: Dict[str, Any]
    ) -> str:
        """시간 이벤트 스케줄링"""
        pass
```

#### **2.4 KnowledgeManager 구현**
```python
class KnowledgeManager:
    """지식 시스템 관리"""
    
    async def create_knowledge(
        self,
        knowledge_id: str,
        title: str,
        content: str,
        knowledge_type: str,
        related_entities: List[str],
        properties: Dict[str, Any]
    ) -> str:
        """지식 생성"""
        pass
```

### **Phase 3: 통합 및 최적화 (1주)**

#### **3.1 Manager 통합**
- 모든 Manager를 통합하는 `GameSystemManager` 구현
- Manager 간 상호작용 로직 구현

#### **3.2 Properties 검증 강화**
- 런타임 Properties 검증
- 스키마 일관성 검사

#### **3.3 성능 최적화**
- Properties 캐싱
- 쿼리 최적화

## 📈 **예상 효과**

### **1. JSONB Properties 체계화 효과**
- **타입 안전성**: Pydantic 모델로 런타임 검증
- **일관성**: Factory 패턴으로 표준화된 Properties 생성
- **확장성**: 새로운 Properties 타입 쉽게 추가

### **2. 미사용 테이블 활용 효과**
- **기능 확장**: 능력, 장비, 이벤트, 지식 시스템 추가
- **게임 깊이**: 더 풍부한 게임플레이 요소
- **시스템 통합**: Manager 간 상호작용 강화

## 🎯 **구현 우선순위**

### **즉시 시작 (1주차)**
1. JSONB Properties 스키마 정의
2. PropertiesFactory 구현
3. PropertiesValidator 구현

### **단기 목표 (2-3주차)**
1. AbilityManager 구현
2. EquipmentManager 구현
3. EventManager 구현

### **중기 목표 (4주차)**
1. KnowledgeManager 구현
2. Manager 통합
3. 성능 최적화

## 📋 **성공 지표**

### **기술적 지표**
- **Properties 검증**: 100% 타입 안전성
- **Manager 활용**: 미사용 테이블 80% 이상 활용
- **성능**: Properties 생성/검증 < 10ms

### **기능적 지표**
- **시스템 통합**: 모든 Manager 간 상호작용
- **확장성**: 새로운 Properties 타입 추가 용이성
- **일관성**: Factory 패턴으로 표준화된 생성

## 🚀 **다음 단계**

### **즉시 시작**
1. JSONB Properties 스키마 정의
2. PropertiesFactory 기본 구현
3. PropertiesValidator 구현

### **단기 목표 (2주)**
1. AbilityManager 구현
2. EquipmentManager 구현
3. EventManager 구현

### **중기 목표 (1개월)**
1. 모든 미사용 테이블 활용
2. Manager 통합 완성
3. 성능 최적화

**이 기획을 통해 "Story Engine" 철학에 맞는 체계적인 Properties 관리와 풍부한 게임 시스템을 구축할 수 있습니다.**
