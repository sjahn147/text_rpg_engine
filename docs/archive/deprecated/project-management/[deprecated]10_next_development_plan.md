# [deprecated] 다음 개발 계획서

> **Deprecated 날짜**: 2025-12-28  
> **Deprecated 이유**: 이 계획서의 대부분 목표가 완료되어 더 이상 진행 중인 작업이 아님. 현재는 Phase 4+ 개발이 진행 중이며, Manager 클래스들은 모두 구현되었음.  
> **문서 버전**: v1.0  
> **작성일**: 2025-10-18  
> **최종 수정**: 2025-10-18  
> **현재 상태**: MVP v2 완성, Effect Carrier 시스템 구현 완료

## 🎯 **현재 상황 분석**

### ✅ **완료된 작업**
- **데이터베이스 아키텍처**: 3계층 구조 완성 (40개 테이블)
- **Effect Carrier 시스템**: 6가지 타입 통일 인터페이스 구현
- **데이터베이스 무결성**: 20개 테스트 100% 통과
- **JSONB 처리**: 모든 데이터 타입 문제 해결
- **인덱스 최적화**: GIN 인덱스로 성능 최적화

### 🚧 **구현이 필요한 Manager 클래스들**

#### **1. Effect Carrier Manager** (우선순위: 높음)
- **현재 상태**: 데이터베이스 스키마만 완성
- **구현 필요**: Python 클래스로 CRUD 기능
- **기능**: Effect Carrier 생성, 조회, 수정, 삭제, 소유 관계 관리

#### **2. Entity Manager** (우선순위: 높음)
- **현재 상태**: 기본 구조만 존재
- **구현 필요**: DB 통합 및 Effect Carrier 연동
- **기능**: 엔티티 생성, 상태 관리, Effect Carrier 적용

#### **3. Cell Manager** (우선순위: 높음)
- **현재 상태**: 기본 구조만 존재
- **구현 필요**: DB 통합 및 엔티티 배치 관리
- **기능**: 셀 생성, 엔티티 배치, 셀 간 이동

#### **4. Dialogue Manager** (우선순위: 중간)
- **현재 상태**: 데이터베이스 스키마만 완성
- **구현 필요**: 대화 시스템 로직
- **기능**: 대화 시작, 진행, 종료, 컨텍스트 관리

#### **5. Action Handler** (우선순위: 중간)
- **현재 상태**: 기본 구조만 존재
- **구현 필요**: 행동 처리 로직
- **기능**: 조사, 대화, 거래, 방문, 대기 행동 처리

## 🚀 **다음 개발 단계**

### **Phase 1: Manager 클래스 구현 (1-2주)**

#### **1.1 Effect Carrier Manager 구현**
```python
# app/effect_carrier/effect_carrier_manager.py
class EffectCarrierManager:
    async def create_effect_carrier(self, name: str, carrier_type: str, 
                                   effect_json: dict, constraints_json: dict = None)
    async def get_effect_carrier(self, effect_id: str)
    async def update_effect_carrier(self, effect_id: str, **kwargs)
    async def delete_effect_carrier(self, effect_id: str)
    async def grant_effect_to_entity(self, session_id: str, entity_id: str, effect_id: str)
    async def revoke_effect_from_entity(self, session_id: str, entity_id: str, effect_id: str)
    async def get_entity_effects(self, session_id: str, entity_id: str)
```

#### **1.2 Entity Manager DB 통합**
```python
# app/entity/entity_manager.py (기존 파일 확장)
class EntityManager:
    async def create_entity(self, name: str, entity_type: str, properties: dict)
    async def get_entity(self, entity_id: str)
    async def update_entity(self, entity_id: str, **kwargs)
    async def delete_entity(self, entity_id: str)
    async def apply_effect_carrier(self, entity_id: str, effect_id: str)
    async def remove_effect_carrier(self, entity_id: str, effect_id: str)
    async def get_entity_effects(self, entity_id: str)
```

#### **1.3 Cell Manager DB 통합**
```python
# app/world/cell_manager.py (기존 파일 확장)
class CellManager:
    async def create_cell(self, name: str, description: str, location_id: str)
    async def get_cell(self, cell_id: str)
    async def place_entity_in_cell(self, entity_id: str, cell_id: str)
    async def move_entity_to_cell(self, entity_id: str, from_cell_id: str, to_cell_id: str)
    async def get_cell_entities(self, cell_id: str)
    async def get_entity_cell(self, entity_id: str)
```

### **Phase 2: Manager 통합 테스트 (1주)**

#### **2.1 Manager 간 연동 테스트**
- **Entity Manager ↔ Effect Carrier Manager**: 엔티티에 Effect Carrier 적용/제거
- **Entity Manager ↔ Cell Manager**: 엔티티를 셀에 배치/이동
- **Cell Manager ↔ Effect Carrier Manager**: 셀 내 엔티티들의 Effect Carrier 관리

#### **2.2 데이터베이스 통합 검증**
- **트랜잭션 테스트**: 여러 Manager가 동시에 작업할 때 데이터 일관성
- **성능 테스트**: 대량 엔티티/Effect Carrier 처리 성능
- **동시성 테스트**: 여러 세션에서 동시 작업 시 충돌 방지

### **Phase 3: 시나리오 테스트 작성 (1-2주)**

#### **3.1 기본 시나리오 (5개)**
1. **엔티티 생성 시나리오**
   - 플레이어 엔티티 생성
   - NPC 엔티티 생성
   - Effect Carrier 적용

2. **셀 이동 시나리오**
   - 엔티티를 셀에 배치
   - 셀 간 이동
   - 셀 내 엔티티 조회

3. **Effect Carrier 적용 시나리오**
   - 스킬 Effect Carrier 생성 및 적용
   - 버프 Effect Carrier 생성 및 적용
   - 아이템 Effect Carrier 생성 및 적용

4. **대화 시스템 시나리오**
   - 플레이어와 NPC 간 대화 시작
   - 대화 진행 및 종료
   - 대화 기록 저장

5. **행동 처리 시나리오**
   - 조사 행동
   - 대화 행동
   - 거래 행동

#### **3.2 고급 시나리오 (5개)**
6. **복합 Effect Carrier 시나리오**
   - 여러 Effect Carrier 동시 적용
   - Effect Carrier 간 상호작용
   - Effect Carrier 제거 및 교체

7. **세션 관리 시나리오**
   - 게임 세션 생성
   - 세션 내 엔티티 관리
   - 세션 종료 및 정리

8. **월드 탐험 시나리오**
   - 여러 셀을 순차적으로 탐험
   - 셀 간 이동 시 상태 유지
   - 셀별 특수 이벤트 처리

9. **NPC 행동 시나리오**
   - NPC 자동 행동
   - NPC 간 상호작용
   - NPC 상태 변화

10. **통합 게임 플레이 시나리오**
    - 플레이어가 NPC와 대화
    - Effect Carrier를 사용한 행동
    - 셀 간 이동하며 탐험
    - 게임 상태 저장 및 복원

## 📋 **구현 체크리스트**

### **Manager 클래스 구현**
- [ ] Effect Carrier Manager 구현
- [ ] Entity Manager DB 통합
- [ ] Cell Manager DB 통합
- [ ] Dialogue Manager 구현
- [ ] Action Handler 구현

### **DB 통합 검증**
- [ ] Manager 간 연동 테스트
- [ ] 트랜잭션 테스트
- [ ] 성능 테스트
- [ ] 동시성 테스트

### **시나리오 테스트**
- [ ] 기본 시나리오 5개 작성
- [ ] 고급 시나리오 5개 작성
- [ ] 시나리오 실행 테스트
- [ ] 시나리오 성능 테스트

## 🎯 **예상 완료 시간**

| 단계 | 예상 시간 | 주요 작업 |
|------|-----------|-----------|
| **Phase 1** | 1-2주 | Manager 클래스 구현 |
| **Phase 2** | 1주 | Manager 통합 테스트 |
| **Phase 3** | 1-2주 | 시나리오 테스트 작성 |
| **총 예상 시간** | **3-5주** | **전체 개발 완료** |

## 🚀 **즉시 시작 가능한 작업**

### **1. Effect Carrier Manager 구현**
```python
# 우선 구현할 핵심 기능
async def create_skill_effect(self, name: str, damage: int, range: int, cooldown: int)
async def create_buff_effect(self, name: str, stat_modifier: dict, duration: int)
async def create_item_effect(self, name: str, heal_amount: int, consumable: bool)
async def apply_effect_to_entity(self, entity_id: str, effect_id: str)
async def get_entity_active_effects(self, entity_id: str)
```

### **2. Entity Manager 확장**
```python
# 기존 EntityManager에 추가할 기능
async def apply_effect_carrier(self, entity_id: str, effect_id: str)
async def remove_effect_carrier(self, entity_id: str, effect_id: str)
async def get_entity_effects(self, entity_id: str)
async def update_entity_stats(self, entity_id: str, stats: dict)
```

### **3. 첫 번째 시나리오 작성**
```python
# tests/scenarios/basic_entity_creation.py
async def test_entity_creation_scenario():
    """엔티티 생성 및 Effect Carrier 적용 시나리오"""
    # 1. 플레이어 엔티티 생성
    # 2. 스킬 Effect Carrier 생성
    # 3. Effect Carrier를 엔티티에 적용
    # 4. 적용 결과 검증
```

## 📊 **성공 지표**

### **기술적 지표**
- **Manager 클래스 구현**: 5개 클래스 100% 구현
- **DB 통합 테스트**: 모든 Manager 간 연동 테스트 통과
- **시나리오 테스트**: 10개 시나리오 100% 통과
- **성능 지표**: 대량 데이터 처리 시 성능 유지

### **기능적 지표**
- **엔티티 관리**: 생성, 조회, 수정, 삭제 완전 구현
- **Effect Carrier 시스템**: 6가지 타입 모두 동작
- **셀 관리**: 엔티티 배치 및 이동 완전 구현
- **대화 시스템**: 기본 대화 플로우 구현

## 🎉 **완료 후 다음 단계**

### **Phase 4: 계기판 UI 구현**
- 텍스트 기반 사용자 인터페이스
- 월드맵 표시 (리스트 형태)
- Region → Location → Cell 전환
- 핵심 행동 버튼 (조사/대화/거래/방문/대기)

### **Phase 5: 게임 루프 구현**
- 플레이어 행동 처리
- NPC 자동 행동
- 이벤트 시스템
- 게임 상태 저장/복원

---

**문서 작성자**: RPG Engine Development Team  
**최종 검토**: 2025-10-18  
**다음 검토 예정**: 2025-11-01
