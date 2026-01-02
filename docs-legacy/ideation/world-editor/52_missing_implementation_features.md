# World Editor 누락된 구현 사항 분석

## 개요
기존 게임 시스템(`app/core`, `app/entity`, `app/interaction`, `app/systems`, `app/world` 등)에서 사용하는 기능 중 World Editor에서 아직 구현되지 않은 항목들을 정리합니다.

---

## 1. Entity (인물) 관련 누락 사항

### 1.1 Entity Status (엔티티 상태)
**위치**: `app/entity/entity_manager.py` - `EntityStatus` Enum
- **누락 필드**: `status` (ACTIVE, INACTIVE, DEAD, HIDDEN)
- **현재 상태**: EntityEditorModal에서 편집 불가
- **영향**: 게임에서 엔티티 활성화/비활성화 관리 불가
- **우선순위**: 중

### 1.2 Entity Behavior Schedules (엔티티 행동 스케줄)
**위치**: `app/systems/npc_behavior.py`, `database/setup/mvp_schema.sql` - `entity_behavior_schedules` 테이블
- **누락 기능**: 시간대별 NPC 행동 스케줄 관리
- **테이블 구조**:
  - `schedule_id` (UUID)
  - `entity_id` (VARCHAR) - FK to entities
  - `time_period` (VARCHAR) - 'morning', 'afternoon', 'evening', 'night'
  - `action_type` (VARCHAR) - 'work', 'rest', 'socialize', 'patrol', 'sleep'
  - `action_priority` (INTEGER)
  - `conditions` (JSONB) - 행동 조건 (날씨, 에너지, 기분 등)
  - `action_data` (JSONB) - 행동 세부 데이터
- **현재 상태**: World Editor에서 완전히 미구현
- **영향**: NPC의 시간대별 자동 행동 패턴 설정 불가
- **우선순위**: 높음

### 1.3 Entity Position (3D 위치)
**위치**: `app/entity/entity_manager.py` - `EntityData.position`
- **누락 필드**: `default_position_3d`는 있지만, `position` 필드가 EntityEditorModal에서 직접 편집 불가
- **현재 상태**: `default_position_3d`는 조회되지만 편집 UI 없음
- **영향**: 셀 내 엔티티 위치 직접 편집 불가
- **우선순위**: 중

---

## 2. Dialogue (대화) 관련 누락 사항

### 2.1 Dialogue Knowledge (대화 지식)
**위치**: `app/interaction/dialogue_manager.py` - `DialogueKnowledge` 모델, `game_data.dialogue_knowledge` 테이블
- **누락 기능**: 대화 지식 베이스 관리
- **테이블 구조**:
  - `knowledge_id` (VARCHAR)
  - `title` (VARCHAR)
  - `content` (TEXT)
  - `knowledge_type` (VARCHAR)
  - `related_entities` (JSONB) - 관련 엔티티 목록
  - `related_topics` (JSONB) - 관련 주제 목록
  - `knowledge_properties` (JSONB) - 지식 속성
- **현재 상태**: World Editor에서 완전히 미구현
- **영향**: NPC가 알고 있는 지식 정보 관리 불가
- **우선순위**: 중

### 2.2 Dialogue Context 추가 필드
**위치**: `database/setup/mvp_schema.sql` - `dialogue_contexts` 테이블
- **누락 필드**:
  - `entity_id` (VARCHAR) - 특정 Entity에 연결 (현재는 EntityEditorModal에서만 설정)
  - `cell_id` (VARCHAR) - 특정 Cell에서만 사용 가능한 대화
  - `time_category` (VARCHAR) - 시간대별 대화 (morning, afternoon, evening, night)
  - `event_id` (VARCHAR) - 특정 이벤트 발생 시 대화
- **현재 상태**: DialogueService에는 있지만, EntityEditorModal의 Dialogue 관리 UI에서 편집 불가
- **영향**: 조건부 대화 컨텍스트 설정 불가
- **우선순위**: 중

### 2.3 Dialogue Topic Conditions (대화 주제 조건)
**위치**: `app/interaction/dialogue_manager.py` - `DialogueTopic.conditions`
- **누락 필드**: `conditions` (JSONB) - 주제 활성화 조건
- **현재 상태**: EntityEditorModal에서 Topic 생성 시 `conditions: {}`로만 설정, 편집 UI 없음
- **영향**: 조건부 대화 주제 설정 불가
- **우선순위**: 낮음

---

## 3. Cell (셀) 관련 누락 사항

### 3.1 Cell Status (셀 상태)
**위치**: `app/world/cell_manager.py` - `CellStatus` Enum
- **누락 필드**: `status` (ACTIVE, INACTIVE, LOCKED, DANGEROUS)
- **현재 상태**: CellEditorModal에서 편집 불가
- **영향**: 셀 활성화/잠금/위험 상태 관리 불가
- **우선순위**: 중

### 3.2 Cell Type (셀 타입)
**위치**: `app/world/cell_manager.py` - `CellType` Enum
- **누락 필드**: `cell_type` (INDOOR, OUTDOOR, DUNGEON, SHOP, TAVERN, TEMPLE)
- **현재 상태**: CellEditorModal에서 편집 불가
- **영향**: 셀 타입별 특수 기능 활용 불가
- **우선순위**: 중

---

## 4. Effect Carrier 관련 누락 사항

### 4.1 Effect Carrier Tags
**위치**: `app/effect_carrier/effect_carrier_manager.py` - `EffectCarrierData.tags`
- **누락 필드**: `tags` (List[str])
- **현재 상태**: EffectCarrierEditorModal에서 편집 가능한지 확인 필요
- **영향**: Effect Carrier 태그 기반 검색/필터링 불가
- **우선순위**: 낮음

---

## 5. World Object 관련 누락 사항

### 5.1 World Object Properties 상세 편집
**위치**: `app/world_editor/services/world_object_service.py`
- **현재 상태**: `properties` 필드는 있지만, 구조화된 편집 UI 없음 (JSON만 가능)
- **영향**: World Object의 특수 속성 편집이 어려움
- **우선순위**: 낮음

---

## 6. Game Session 관련 누락 사항

### 6.1 Runtime Entity State 관리
**위치**: `app/game_session.py`, `runtime_data.entity_states` 테이블
- **누락 기능**: 런타임 엔티티 상태 관리 UI
- **테이블 구조**:
  - `current_stats` (JSONB) - 현재 능력치
  - `current_position` (JSONB) - 현재 위치
  - `active_effects` (JSONB) - 활성 이펙트
  - `inventory` (JSONB) - 인벤토리
  - `equipped_items` (JSONB) - 장착 아이템
- **현재 상태**: World Editor는 정적 게임 데이터만 편집, 런타임 상태는 미구현
- **영향**: 게임 세션 중 엔티티 상태 확인/수정 불가
- **우선순위**: 낮음 (런타임 데이터이므로)

---

## 7. Action Handler 관련 누락 사항

### 7.1 Action Type 정의
**위치**: `app/interaction/action_handler.py` - `ActionType` Enum
- **액션 타입들**: INVESTIGATE, DIALOGUE, TRADE, VISIT, WAIT, MOVE, ATTACK, USE_ITEM
- **현재 상태**: World Editor에서 액션 타입 참조는 있지만, 직접 관리 UI 없음
- **영향**: Entity Behavior Schedules에서 사용하는 action_type 검증 어려움
- **우선순위**: 낮음

---

## 우선순위별 구현 권장 사항

### 높음 (High Priority)
1. **Entity Behavior Schedules 관리**
   - EntityEditorModal에 "행동 스케줄" 섹션 추가
   - 시간대별 행동 스케줄 CRUD UI
   - 조건(conditions) 및 행동 데이터(action_data) 편집 UI

### 중 (Medium Priority)
2. **Entity Status 필드 추가**
   - EntityEditorModal에 Status 선택 필드 추가
3. **Cell Status 및 Cell Type 필드 추가**
   - CellEditorModal에 Status 및 Type 선택 필드 추가
4. **Dialogue Context 조건 필드 편집**
   - EntityEditorModal의 Dialogue 관리 UI에 cell_id, time_category, event_id 편집 추가
5. **Dialogue Knowledge 관리**
   - 새로운 DialogueKnowledgeEditorModal 생성
   - EntityEditorModal에서 연결 가능하도록 통합

### 낮음 (Low Priority)
6. **Dialogue Topic Conditions 편집**
   - EntityEditorModal의 Topic 목록에서 conditions 편집 UI 추가
7. **Effect Carrier Tags 확인 및 개선**
   - EffectCarrierEditorModal에서 tags 편집 가능 여부 확인
8. **World Object Properties 구조화 편집**
   - WorldObjectEditorModal에 properties 구조화 편집 UI 추가

---

## 구현 시 고려사항

1. **Entity Behavior Schedules**:
   - 시간대별 행동을 시각적으로 표현하는 UI 필요
   - 조건(conditions) JSONB 편집을 위한 구조화된 폼 필요
   - 행동 데이터(action_data) JSONB 편집 UI 필요

2. **Dialogue Knowledge**:
   - 지식 베이스는 독립적인 관리 화면이 필요할 수 있음
   - Entity와의 연결은 다대다 관계일 수 있음

3. **Status 및 Type 필드**:
   - Enum 타입이므로 드롭다운 선택 UI로 구현
   - 기존 JsonFormField에 enum 타입 추가 고려

4. **조건부 필드들**:
   - JSONB 조건 필드들은 구조화된 편집 UI가 필요
   - 예: `{"min_energy": 20, "weather": "clear"}` 같은 조건을 쉽게 편집할 수 있는 폼

---

## 참고 파일

- `app/entity/entity_manager.py` - EntityStatus, EntityData
- `app/systems/npc_behavior.py` - Entity Behavior Schedules 사용
- `app/world/cell_manager.py` - CellStatus, CellType
- `app/interaction/dialogue_manager.py` - DialogueKnowledge
- `database/setup/mvp_schema.sql` - entity_behavior_schedules, dialogue_knowledge 테이블 정의
- `app/game_session.py` - Runtime Entity State 사용 예시

