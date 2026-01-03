# Dialogue System 가이드라인

> **최신화 날짜**: 2026-01-03  
> **적용 범위**: Dialogue Manager 시스템 사용 전 필수 읽기

## ⚠️ 중요: mvp_schema.sql 참조 필수

**Dialogue Manager 시스템 구현 및 사용 시 반드시 `database/setup/mvp_schema.sql`을 참조해야 합니다.**

### 필수 참조 테이블

다음 테이블들의 구조를 반드시 확인하세요:

1. **`game_data.dialogue_contexts`**: 대화 컨텍스트 정의
   - `dialogue_id`, `title`, `content`
   - `entity_id`, `cell_id`, `time_category`, `event_id` (조건)
   - `priority`, `available_topics`, `entity_personality`, `constraints`

2. **`game_data.dialogue_topics`**: 대화 주제 정의
   - `topic_id`, `dialogue_id`, `topic_type`, `content`
   - `conditions` (JSONB)

3. **`game_data.dialogue_knowledge`**: 대화 지식 베이스
   - `knowledge_id`, `title`, `content`, `knowledge_type`
   - `related_entities`, `related_topics`, `knowledge_properties`

4. **`runtime_data.dialogue_history`**: 대화 기록
   - `history_id`, `session_id`, `runtime_entity_id`, `context_id`
   - `speaker_type`, `message`, `relevant_knowledge`, `timestamp`

5. **`runtime_data.dialogue_states`**: 대화 상태
   - `state_id`, `session_id`, `runtime_entity_id`, `current_context_id`
   - `conversation_state`, `active_topics`, `last_updated`

## 1. 개요

Dialogue Manager는 RPG Engine의 대화 시스템을 관리하는 핵심 Manager입니다. 이 문서는 Dialogue Manager의 사용법과 주의사항을 설명합니다.

## 2. Dialogue Manager의 역할

### 2.1 주요 기능

- **대화 시작**: `start_dialogue()` - 플레이어와 NPC 간 대화 시작
- **대화 계속**: `continue_dialogue()` - 대화 주제 변경 및 계속
- **대화 종료**: `end_dialogue()` - 대화 종료
- **대화 기록 조회**: `get_dialogue_history()` - 대화 기록 조회

### 2.2 데이터 흐름

```
1. 대화 시작 요청 (runtime_entity_id 사용)
   ↓
2. EntityManager를 통해 NPC 엔티티 조회
   ↓
3. Reference Layer를 통해 game_entity_id 변환
   ↓
4. GameDataRepository를 통해 dialogue_contexts 조회
   ↓
5. GameDataRepository를 통해 dialogue_topics 조회
   ↓
6. NPC 응답 생성
   ↓
7. RuntimeDataRepository를 통해 dialogue_history 저장
   ↓
8. RuntimeDataRepository를 통해 dialogue_states 업데이트
```

## 3. ID 변환 (중요)

### 3.1 문제 상황

Dialogue Manager는 두 가지 ID 형식을 다룹니다:

- **`runtime_entity_id`**: UUID 형식 (Runtime Data에서 사용)
- **`game_entity_id`**: VARCHAR(50) 형식 (Game Data에서 사용)

### 3.2 올바른 변환 방법

**✅ Reference Layer를 통한 명시적 변환**:

```python
async def _get_game_entity_id(self, runtime_entity_id: str, session_id: str) -> str:
    """
    runtime_entity_id를 game_entity_id로 변환
    Reference Layer를 통한 명시적 변환 (추측 금지)
    """
    # Reference Layer를 통해 변환
    entity_ref = await self.reference_layer.get_entity_reference(
        runtime_entity_id=runtime_entity_id,
        session_id=session_id
    )
    
    if not entity_ref:
        raise ValueError(f"Entity reference not found: {runtime_entity_id}")
    
    return entity_ref.game_entity_id
```

**❌ 잘못된 방법 (추측 로직 금지)**:

```python
# ❌ 잘못된 방법: 타입 추측
async def _get_game_entity_id_wrong(self, entity_id: str) -> str:
    # ❌ UUID 형식인지 VARCHAR 형식인지 추측 (금지)
    if len(entity_id) == 36:  # UUID라고 추측
        # 변환 로직
        ...
    else:  # VARCHAR라고 추측
        return entity_id
```

### 3.3 불확정성 불허 원칙

Dialogue Manager는 **불확정성 불허 원칙**을 엄격히 준수합니다:

- ❌ **추측 로직 금지**: ID 형식을 추측하는 코드는 절대 금지
- ✅ **명시적 처리 필수**: 모든 ID 변환은 Reference Layer를 통해서만
- ✅ **에러 우선 처리**: 변환 실패 시 기본값으로 대체하지 않고 명시적 에러 발생

## 4. Dialogue Manager 사용법

### 4.1 초기화

```python
from app.managers.dialogue_manager import DialogueManager
from app.managers.entity_manager import EntityManager
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository

# Repository 초기화
game_data_repo = GameDataRepository(db)
runtime_data_repo = RuntimeDataRepository(db)
reference_layer_repo = ReferenceLayerRepository(db)

# EntityManager 초기화
entity_manager = EntityManager(
    db_connection=db,
    game_data_repo=game_data_repo,
    runtime_data_repo=runtime_data_repo,
    reference_layer_repo=reference_layer_repo
)

# DialogueManager 초기화
dialogue_manager = DialogueManager(
    db_connection=db,
    game_data_repo=game_data_repo,
    runtime_data_repo=runtime_data_repo,
    reference_layer_repo=reference_layer_repo,
    entity_manager=entity_manager
)
```

### 4.2 대화 시작

```python
# 대화 시작
result = await dialogue_manager.start_dialogue(
    player_id=player_runtime_entity_id,  # UUID 형식
    npc_id=npc_runtime_entity_id,       # UUID 형식
    session_id=session_id,               # UUID 형식
    initial_topic="greeting"             # 기본 주제
)

if result.success:
    print(f"NPC 응답: {result.npc_response}")
    print(f"사용 가능한 주제: {result.available_topics}")
else:
    print(f"대화 시작 실패: {result.message}")
```

### 4.3 대화 계속

```python
# 대화 계속
result = await dialogue_manager.continue_dialogue(
    player_id=player_runtime_entity_id,
    npc_id=npc_runtime_entity_id,
    topic="trade",                       # 주제 변경
    session_id=session_id,
    player_message="무기를 구매하고 싶습니다."
)

if result.success:
    print(f"NPC 응답: {result.npc_response}")
```

### 4.4 대화 종료

```python
# 대화 종료
result = await dialogue_manager.end_dialogue(
    player_id=player_runtime_entity_id,
    npc_id=npc_runtime_entity_id,
    session_id=session_id
)

if result.success:
    print(f"대화 종료: {result.message}")
```

## 5. 대화 컨텍스트 로드

### 5.1 대화 컨텍스트 조회

Dialogue Manager는 다음 조건으로 대화 컨텍스트를 조회합니다:

- `entity_id`: NPC의 game_entity_id
- `cell_id`: 현재 셀의 game_cell_id (선택적)
- `time_category`: 시간대 (선택적)
- `event_id`: 이벤트 ID (선택적)

**우선순위**: `priority` 필드가 높은 순서대로 선택

### 5.2 대화 주제 조회

대화 주제는 `dialogue_topics` 테이블에서 다음 조건으로 조회:

- `dialogue_id`: 대화 컨텍스트 ID
- `conditions`: JSONB 조건 (플레이어 레벨, 퀘스트 진행도 등)

## 6. 트랜잭션 사용

### 6.1 트랜잭션이 필요한 작업

다음 작업들은 반드시 트랜잭션 내에서 수행해야 합니다:

- ✅ 대화 기록 저장 (`dialogue_history`)
- ✅ 대화 상태 업데이트 (`dialogue_states`)

### 6.2 트랜잭션 사용 예시

```python
from app.common.decorators.transaction import with_transaction

class DialogueService:
    @with_transaction
    async def save_dialogue(self, dialogue_data: dict, conn=None):
        """대화 기록 저장 (트랜잭션 내)"""
        await dialogue_manager.continue_dialogue(...)
        # 트랜잭션 내에서 자동으로 dialogue_history와 dialogue_states 업데이트
```

## 7. 자주 발생하는 에러 및 해결

### 7.1 ID 변환 실패

**에러**: `ValueError: Entity reference not found`

**원인**: `runtime_entity_id`가 Reference Layer에 존재하지 않음

**해결**:
```python
# Reference Layer에 엔티티 참조가 있는지 확인
entity_ref = await reference_layer_repo.get_entity_reference(
    runtime_entity_id=runtime_entity_id,
    session_id=session_id
)

if not entity_ref:
    # 엔티티 참조 생성 필요
    await reference_layer_repo.create_entity_reference(...)
```

### 7.2 대화 컨텍스트 없음

**에러**: 대화 컨텍스트를 찾을 수 없음

**원인**: `game_data.dialogue_contexts`에 해당 NPC의 대화 컨텍스트가 없음

**해결**:
- `mvp_schema.sql`을 참조하여 대화 컨텍스트 구조 확인
- 필요한 대화 컨텍스트를 `game_data.dialogue_contexts`에 추가

### 7.3 타입 불일치

**에러**: UUID와 VARCHAR 타입 불일치

**원인**: ID 형식을 잘못 사용

**해결**:
- `runtime_entity_id`는 항상 UUID 형식
- `game_entity_id`는 항상 VARCHAR(50) 형식
- Reference Layer를 통한 명시적 변환만 사용

## 8. 체크리스트

Dialogue Manager 사용 전 확인사항:

- [ ] `mvp_schema.sql`의 대화 관련 테이블 구조 확인
- [ ] `runtime_entity_id`와 `game_entity_id` 차이 이해
- [ ] Reference Layer를 통한 ID 변환 방법 이해
- [ ] 트랜잭션 사용 필요 여부 확인
- [ ] 대화 컨텍스트가 `game_data.dialogue_contexts`에 존재하는지 확인
- [ ] 대화 주제가 `game_data.dialogue_topics`에 존재하는지 확인

## 9. 참고 문서

- `00_CORE/01_PHILOSOPHY.md`: 핵심 개발 철학 (불확정성 불허 원칙)
- `00_CORE/02_ARCHITECTURE_PRINCIPLES.md`: 아키텍처 설계 원칙
- `02_DATABASE/DATABASE_SCHEMA_DESIGN.md`: 데이터베이스 스키마 설계 가이드라인
- `database/setup/mvp_schema.sql`: **데이터베이스 스키마 (필수 참조)**
- `app/managers/dialogue_manager.py`: Dialogue Manager 구현
- `docs/architecture/08_architecture_guide.md`: 전체 아키텍처 가이드

