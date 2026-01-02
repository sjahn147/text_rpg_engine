# 🚀 세계관 이식 빠른 시작 가이드

> **문서 버전**: v1.0  
> **작성일**: 2025-10-21  
> **최종 수정**: 2025-10-21

---

## 🎯 **즉시 시작할 수 있는 작업**

### **1단계: 레크로스타 기본 구조 (1주일)**

#### **Day 1-2: 데이터베이스 설정**
```sql
-- 레크로스타 지역 생성
INSERT INTO game_data.world_cells (cell_id, name, cell_type, description, location_data) VALUES
('REKROSTA_PALACE', '황궁', 'building', '안브레티아 제국의 정치적 중심지', '{"region": "레크로스타", "importance": "highest"}'),
('REKROSTA_MARKET', '대시장', 'building', '제국의 경제적 중심지', '{"region": "레크로스타", "importance": "high"}'),
('REKROSTA_TEMPLE', '신전구역', 'area', '종교적 중심지', '{"region": "레크로스타", "importance": "high"}'),
('REKROSTA_SLUMS', '하층민 구역', 'area', '도시의 하층민들이 거주하는 지역', '{"region": "레크로스타", "importance": "medium"}');
```

#### **Day 3-4: 핵심 NPC 생성**
```sql
-- 에이레/루시아 생성
INSERT INTO game_data.entities (entity_id, name, entity_type, description, entity_data) VALUES
('EIRE_LUCIA', '루시아', 'deity', '에이레의 화신, 치유와 예언의 신', '{"bloodline": "nuhan", "powers": ["healing", "prophecy"], "appearance": "human_female"}'),
('KEKOWARI', '케코와리', 'npc', '누한 왕족, 불사 존재', '{"bloodline": "nuhan", "immortal": true, "beauty": "absolute"}'),
('LIGHT_HIGH_PRIEST', '빛의 신전 대사제', 'npc', 'The Light Faith의 최고 지도자', '{"religion": "light_faith", "authority": "highest"}');
```

#### **Day 5-7: 기본 대화 시스템**
```python
# 루시아와의 대화 구현
dialogue_contexts = {
    "lucia_greeting": {
        "context": "루시아와의 첫 만남",
        "topics": ["healing", "prophecy", "bloodline", "future"],
        "responses": {
            "healing": "치유는 마음의 평화에서 시작됩니다.",
            "prophecy": "미래는 선택에 따라 달라집니다.",
            "bloodline": "진정한 피는 마음에서 나옵니다."
        }
    }
}
```

### **2단계: 살아있는 NPC 시스템 (2주일)**

#### **Week 1: 기본 욕구 시스템**
```python
class NPCNeedsSystem:
    def __init__(self):
        self.needs = {
            'hunger': {'current': 50, 'decay_rate': 0.1},
            'safety': {'current': 50, 'decay_rate': 0.05},
            'social': {'current': 50, 'decay_rate': 0.08},
            'purpose': {'current': 50, 'decay_rate': 0.02}
        }
    
    def update_needs(self, npc_id: str):
        """NPC의 욕구 업데이트"""
        for need, data in self.needs.items():
            data['current'] = max(0, data['current'] - data['decay_rate'])
            
        # 가장 시급한 욕구 확인
        urgent_need = min(self.needs.keys(), 
                         key=lambda x: self.needs[x]['current'])
        return urgent_need
```

#### **Week 2: 일상 루틴 시스템**
```python
class NPCDailyRoutine:
    def __init__(self):
        self.routines = {
            'morning': ['wake_up', 'prayer', 'breakfast'],
            'afternoon': ['work', 'social_interaction'],
            'evening': ['dinner', 'family_time', 'rest']
        }
    
    def get_current_activity(self, npc_id: str, time_of_day: str) -> str:
        """현재 시간대의 활동 반환"""
        return self.routines.get(time_of_day, ['idle'])[0]
```

### **3단계: 역사적 추적 시스템 (3주일)**

#### **Week 1: 사건 기록 시스템**
```python
class HistoricalTracker:
    def __init__(self):
        self.events = []
        self.relationships = {}
    
    def record_event(self, event_type: str, participants: List[str], 
                    description: str, consequences: Dict[str, Any]):
        """사건 기록"""
        event = {
            'timestamp': datetime.now(),
            'type': event_type,
            'participants': participants,
            'description': description,
            'consequences': consequences
        }
        self.events.append(event)
    
    def get_historical_context(self, npc_id: str) -> List[Dict]:
        """NPC의 역사적 맥락 반환"""
        return [event for event in self.events 
                if npc_id in event['participants']]
```

#### **Week 2: 플레이어 행동 추적**
```python
class PlayerActionTracker:
    def __init__(self):
        self.player_actions = []
        self.consequences = {}
    
    def track_action(self, action: str, target: str, result: str):
        """플레이어 행동 추적"""
        action_record = {
            'timestamp': datetime.now(),
            'action': action,
            'target': target,
            'result': result
        }
        self.player_actions.append(action_record)
        
        # 결과 추적
        self._update_consequences(action, target, result)
```

#### **Week 3: 동적 역사 생성**
```python
class DynamicHistoryGenerator:
    def __init__(self):
        self.history_templates = {}
        self.current_events = []
    
    def generate_historical_event(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """맥락에 따른 역사적 사건 생성"""
        # 플레이어 행동을 바탕으로 새로운 사건 생성
        event = {
            'type': 'historical_event',
            'trigger': context['player_action'],
            'participants': context['affected_npcs'],
            'consequences': self._calculate_consequences(context)
        }
        return event
```

---

## 🛠️ **즉시 사용 가능한 코드 템플릿**

### **세계관 데이터 로더**
```python
class WorldbuildingDataLoader:
    def __init__(self, db_connection):
        self.db = db_connection
    
    async def load_rekrosta_data(self):
        """레크로스타 데이터 로드"""
        # 지역 데이터
        regions = await self.db.fetch_all("""
            SELECT * FROM game_data.world_cells 
            WHERE location_data->>'region' = '레크로스타'
        """)
        
        # NPC 데이터
        npcs = await self.db.fetch_all("""
            SELECT * FROM game_data.entities 
            WHERE entity_type IN ('npc', 'deity')
        """)
        
        return {
            'regions': regions,
            'npcs': npcs
        }
    
    async def load_historical_events(self):
        """역사적 사건 데이터 로드"""
        events = await self.db.fetch_all("""
            SELECT * FROM game_data.historical_events 
            ORDER BY event_date DESC
        """)
        return events
```

### **NPC 상호작용 시스템**
```python
class NPCInteractionSystem:
    def __init__(self, dialogue_manager, action_handler):
        self.dialogue_manager = dialogue_manager
        self.action_handler = action_handler
    
    async def interact_with_npc(self, player_id: str, npc_id: str, 
                               interaction_type: str) -> Dict[str, Any]:
        """NPC와의 상호작용"""
        if interaction_type == 'dialogue':
            return await self.dialogue_manager.start_dialogue(
                player_id, npc_id
            )
        elif interaction_type == 'trade':
            return await self.action_handler.handle_trade(
                player_id, npc_id
            )
        elif interaction_type == 'quest':
            return await self.action_handler.handle_quest_request(
                player_id, npc_id
            )
```

### **세계 상태 모니터**
```python
class WorldStateMonitor:
    def __init__(self):
        self.world_state = {}
        self.change_log = []
    
    def update_world_state(self, change_type: str, 
                          affected_entities: List[str], 
                          change_data: Dict[str, Any]):
        """세계 상태 업데이트"""
        change = {
            'timestamp': datetime.now(),
            'type': change_type,
            'affected_entities': affected_entities,
            'data': change_data
        }
        self.change_log.append(change)
        
        # 세계 상태 업데이트
        self._apply_change(change)
    
    def get_world_summary(self) -> Dict[str, Any]:
        """현재 세계 상태 요약"""
        return {
            'total_entities': len(self.world_state),
            'recent_changes': self.change_log[-10:],
            'active_events': self._get_active_events()
        }
```

---

## 📋 **첫 주 작업 체크리스트**

### **Day 1: 환경 설정**
- [ ] 데이터베이스 연결 확인
- [ ] 기본 테스트 데이터 로드
- [ ] 개발 환경 설정

### **Day 2: 레크로스타 기본 구조**
- [ ] 황궁 Cell 생성
- [ ] 대시장 Cell 생성
- [ ] 신전구역 Cell 생성
- [ ] 하층민 구역 Cell 생성

### **Day 3: 핵심 NPC 생성**
- [ ] 루시아 (에이레의 화신) 생성
- [ ] 케코와리 (누한 왕족) 생성
- [ ] 빛의 신전 대사제 생성
- [ ] 기본 대화 컨텍스트 설정

### **Day 4: 기본 상호작용**
- [ ] 플레이어-NPC 대화 시스템
- [ ] 기본 행동 (조사, 대화, 이동)
- [ ] 간단한 이벤트 시스템

### **Day 5: 테스트 및 검증**
- [ ] 전체 시스템 통합 테스트
- [ ] 버그 수정 및 최적화
- [ ] 사용자 경험 개선

---

## 🎯 **성공 기준**

### **1주일 후 목표**
- [ ] 레크로스타에서 자유롭게 이동 가능
- [ ] 3-5명의 NPC와 대화 가능
- [ ] 기본적인 세계 탐험 가능
- [ ] 플레이어 행동이 기록됨

### **1개월 후 목표**
- [ ] 전체 레크로스타 구현 완료
- [ ] 10-20명의 NPC와 상호작용
- [ ] 기본적인 퀘스트와 이벤트
- [ ] NPC들의 일상 루틴

### **3개월 후 목표**
- [ ] 전체 세계의 기본 구조
- [ ] 살아있는 NPC 시스템
- [ ] 역사적 추적 시스템
- [ ] 복잡한 사회적 상호작용

---

## 🚨 **주의사항**

### **데이터 일관성**
- [ ] 모든 설정이 DB에 정확히 저장되는지 확인
- [ ] NPC 간 관계가 올바르게 설정되는지 확인
- [ ] 역사적 사건의 시간순 정렬 확인

### **성능 최적화**
- [ ] 대량의 NPC 처리 시 성능 모니터링
- [ ] 데이터베이스 쿼리 최적화
- [ ] 메모리 사용량 관리

### **사용자 경험**
- [ ] 직관적인 인터페이스
- [ ] 명확한 피드백
- [ ] 매끄러운 상호작용

---

**마지막 업데이트**: 2025-10-21  
**다음 업데이트 예정**: 2025-10-28  
**빠른 시작 가이드 작성자**: AI Assistant


