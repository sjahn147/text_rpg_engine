# [deprecated] Phase 3 개발 계획서

> **Deprecated 날짜**: 2025-12-28  
> **Deprecated 이유**: Phase 3가 완료되어 더 이상 진행 중인 작업이 아님. 현재는 Phase 4+ 개발이 진행 중이며, Phase 1-3은 모두 완료되었음.  
> **시작일**: 2025-10-18  
> **목표**: 실제 동작하는 MVP 구현 (3주차)  
> **근거**: 비판적 검토 결과, 실제 플레이 가능한 시스템 필요

## 🚨 **비판적 검토 결과**

### **현재 문제점**
1. **Mock 구현**: 모든 Manager가 실제 DB 연동 없음
2. **UI 부재**: 계기판 UI가 구현되지 않음
3. **게임 로직 부재**: 핵심 행동 처리 미구현
4. **Dev Mode 부재**: MVP 핵심 기능 미구현
5. **데이터 영속성 부재**: 실제 데이터 저장/로드 불가능

### **위험 요소**
- **기술 부채**: Mock 구현이 누적되어 실제 구현 시 대규모 리팩토링 필요
- **사용자 경험**: 실제 플레이할 수 있는 시스템이 없음
- **MVP 목표 달성 불가**: 현재 상태로는 MVP 수용 기준 달성 불가능

## 🎯 **Phase 3 목표**

### **핵심 목표**
1. **실제 데이터베이스 연동**: Mock → 실제 DB 구현
2. **계기판 UI 구현**: 완전한 사용자 인터페이스
3. **핵심 게임 로직**: 행동 처리 및 게임 루프
4. **Dev Mode 구현**: Runtime → Game Data 승격
5. **실제 플레이 가능**: 100회 연속 무오류 플레이

### **수용 기준**
- [ ] 실제 DB에 데이터 저장/로드 가능
- [ ] 계기판 UI로 플레이 가능
- [ ] 조사/대화/거래/방문/대기 행동 모두 동작
- [ ] Dev Mode에서 NPC 생성 후 다음 세션에서 정상 노출
- [ ] 100회 연속 무오류 플레이 가능

## 📋 **구체적 작업 계획**

### **3.1 데이터베이스 연동 (1-2일)**
- [ ] EntityManager 실제 DB 연동
  - `runtime_data.runtime_entities` 테이블 연동
  - CRUD 작업 실제 구현
- [ ] CellManager 실제 DB 연동
  - `game_data.world_cells` 테이블 연동
  - 셀 컨텐츠 로딩 구현
- [ ] GameManager 실제 DB 연동
  - `runtime_data.active_sessions` 테이블 연동
  - 세션 관리 실제 구현

### **3.2 계기판 UI 구현 (2-3일)**
- [ ] 기존 `main_window.py` 완전 재구현
- [ ] 상단바: Region/Location/Cell, 시간, 날씨
- [ ] 좌측 패널: 행동 버튼 (조사/대화/거래/방문/대기)
- [ ] 중앙 패널: 월드 로그 (실시간 게임 정보)
- [ ] 우측 패널: 정보 탭 (인벤토리/자산/관계/로어)
- [ ] 하단 패널: 명령 입력

### **3.3 핵심 게임 로직 (2-3일)**
- [ ] ActionHandler 구현
  - `app/interaction/action_handler.py`
  - 조사/대화/거래/방문/대기 행동 처리
- [ ] DialogueManager 구현
  - `app/interaction/dialogue_manager.py`
  - 대화 시스템 및 NPC 응답
- [ ] 게임 루프 구현
  - 행동 → 결과 → 로그 → UI 업데이트

### **3.4 Dev Mode 구현 (1-2일)**
- [ ] Dev Mode UI 구현
  - `app/ui/screens/dev_mode.py`
  - 실시간 데이터 편집
- [ ] Runtime → Game Data 승격
  - `app/core/dev_mode_manager.py`
  - 1-click promote 기능
- [ ] 데이터 검증 및 승격 로직

### **3.5 통합 테스트 (1일)**
- [ ] 실제 DB 연동 테스트
- [ ] UI 통합 테스트
- [ ] 게임 플로우 테스트
- [ ] Dev Mode 테스트
- [ ] 100회 연속 무오류 테스트

## 🔧 **구현 우선순위**

### **1순위: 데이터베이스 연동**
```python
# EntityManager 실제 구현 예시
async def _save_entity_to_db(self, entity: EntityData) -> None:
    async with self.db.pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO runtime_data.runtime_entities 
            (entity_id, name, entity_type, status, properties, position, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """, entity.entity_id, entity.name, entity.entity_type, entity.status,
            json.dumps(entity.properties), json.dumps(entity.position),
            entity.created_at, entity.updated_at)
```

### **2순위: 계기판 UI**
```python
# MVP 계기판 UI 구조
class DashboardUI(QMainWindow):
    def __init__(self):
        # 상단바, 좌측패널, 중앙패널, 우측패널, 하단패널
        self.setup_dashboard_layout()
    
    def setup_dashboard_layout(self):
        # MVP 계기판 레이아웃 구현
        pass
```

### **3순위: 게임 로직**
```python
# ActionHandler 구현
class ActionHandler:
    async def investigate(self, player_id: str, cell_id: str) -> ActionResult:
        # 조사 행동 처리
        pass
    
    async def dialogue(self, player_id: str, target_id: str) -> ActionResult:
        # 대화 행동 처리
        pass
```

## 📊 **성공 지표**

### **기술적 지표**
- [ ] 실제 DB 연동: 100% Mock 제거
- [ ] UI 완성도: 모든 MVP UI 컴포넌트 구현
- [ ] 게임 로직: 5가지 핵심 행동 모두 동작
- [ ] Dev Mode: Runtime → Game Data 승격 가능
- [ ] 테스트: 100회 연속 무오류 플레이

### **사용자 경험 지표**
- [ ] 직관적인 계기판 UI
- [ ] 반응성 있는 게임 플레이
- [ ] 명확한 피드백 (로그, 상태 업데이트)
- [ ] Dev Mode로 세계 확장 가능

## ⚠️ **리스크 관리**

### **기술적 리스크**
- **DB 스키마 불일치**: 실제 테이블 구조와 코드 불일치 가능성
- **성능 이슈**: 실제 DB 연동 시 성능 저하 가능성
- **UI 복잡성**: PyQt5 기반 UI 구현의 복잡성

### **완화 방안**
- **점진적 구현**: Mock → 실제 구현 단계별 전환
- **성능 모니터링**: DB 쿼리 최적화 및 캐시 활용
- **UI 프로토타입**: 간단한 버전부터 시작하여 점진적 개선

## 🎯 **Phase 3 완료 기준**

1. **실제 플레이 가능**: 계기판 UI로 게임 플레이 가능
2. **데이터 영속성**: 게임 상태가 실제 DB에 저장/로드
3. **핵심 기능 동작**: 모든 MVP 기능이 실제로 동작
4. **Dev Mode 활용**: 개발자가 세계를 확장할 수 있음
5. **안정성**: 100회 연속 무오류 플레이 가능

---

**결론**: 현재까지의 작업은 견고한 기반을 구축했지만, **실제 동작하는 시스템**이 필요합니다. Phase 3에서는 Mock 구현을 실제 구현으로 전환하고, 사용자가 실제로 플레이할 수 있는 MVP를 완성해야 합니다.
