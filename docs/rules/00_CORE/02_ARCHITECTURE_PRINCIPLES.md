# 아키텍처 설계 원칙

> **최신화 날짜**: 2026-01-03  
> **적용 범위**: 모든 아키텍처 설계 및 시스템 개발 전 필수 읽기

## 1. 개요

이 문서는 RPG Engine의 핵심 아키텍처 설계 원칙을 정의합니다. 모든 시스템 설계는 이 원칙을 준수해야 합니다.

## 2. Reference Layer 우회 금지 원칙

### 2.1 절대 원칙

**Game Data와 Runtime Data 간의 모든 연결은 반드시 Reference Layer를 통해서만 이루어져야 합니다.**

```
✅ 올바른 연결 경로:
game_data.entities 
  → reference_layer.entity_references 
  → runtime_data.entity_states

❌ 금지된 직접 연결:
game_data.entities → runtime_data.entity_states (직접 연결 금지)
```

### 2.2 이유

1. **세션 독립성**: 각 게임 세션은 독립적인 데이터 공간을 가져야 함
2. **확장성**: 여러 세션이 동일한 게임 데이터를 참조할 수 있어야 함
3. **데이터 무결성**: Reference Layer를 통한 연결만이 데이터 일관성을 보장
4. **트랜잭션 안전성**: 세션별 상태 변경이 다른 세션에 영향을 주지 않도록 격리

### 2.3 구현 시 주의사항

- ✅ **DO**: 모든 Manager 클래스는 Reference Layer Repository를 통해 데이터 접근
- ❌ **DO NOT**: 직접 FK를 사용한 Game Data → Runtime Data 연결은 스키마 설계 단계에서 금지
- ❌ **DO NOT**: 코드에서 Game Data ID를 직접 Runtime Data에 저장
- ✅ **DO**: 코드 리뷰 시 Reference Layer 우회 여부를 반드시 확인

### 2.4 예시

```python
# ✅ 올바른 방법: Reference Layer를 통한 연결
async def create_entity_instance(self, game_entity_id: str, session_id: UUID):
    # 1. Reference Layer에 참조 생성
    runtime_entity_id = await self.ref_repo.create_entity_reference(
        session_id=session_id,
        game_entity_id=game_entity_id
    )
    
    # 2. Runtime Data에 상태 초기화
    await self.runtime_repo.create_entity_state(
        runtime_entity_id=runtime_entity_id,
        session_id=session_id
    )
    
    return runtime_entity_id

# ❌ 잘못된 방법: 직접 연결 시도
async def create_entity_instance_wrong(self, game_entity_id: str, session_id: UUID):
    # ❌ Game Data ID를 직접 Runtime Data에 저장 (금지)
    await self.runtime_repo.create_entity_state(
        game_entity_id=game_entity_id,  # ❌ 직접 연결 금지
        session_id=session_id
    )
```

## 3. Factory vs Handler 패턴 사용 원칙

### 3.1 Factory 패턴: 객체 생성

**목적**: 복잡한 객체 생성 로직 캡슐화

**사용 시점**: 데이터 생성 시

**예시**:
```python
# GameDataFactory: 정적 게임 데이터 생성
factory = GameDataFactory(db)
object_id = await factory.create_world_object(
    object_id="OBJ_CHEST_001",
    name="보물 상자",
    object_type="chest",
    properties={"interaction_type": "openable"}
)

# InstanceFactory: 런타임 인스턴스 생성
instance_factory = InstanceFactory(db)
runtime_entity_id = await instance_factory.create_npc_instance(
    session_id=session_id,
    game_entity_id=game_entity_id,
    initial_cell_id=initial_cell_id
)
```

**게임 데이터 제작 시 Factory 사용**:

게임 데이터는 YAML 파일로 정의되며, `UnifiedGameDataLoader`가 기존 Factory를 재사용합니다:

```python
# UnifiedGameDataLoader: YAML → Factory → DB
from database.game_data.unified_loader import UnifiedGameDataLoader

loader = UnifiedGameDataLoader()
# 내부적으로 WorldDataFactory를 사용하여 데이터 생성
results = await loader.load_all(data_dir)
```

**핵심 원칙**:
- ✅ Factory는 **객체 생성**에만 사용
- ✅ Reference Layer를 통한 연결 보장
- ✅ 복잡한 생성 로직 캡슐화
- ✅ 게임 데이터 제작 시 기존 Factory 재사용
- ❌ **행동 실행**에는 사용하지 않음

**게임 데이터 제작 가이드라인**: `02_DATABASE/GAME_DATA_PRODUCTION_GUIDELINES.md` 참조

### 3.2 Handler 패턴: 행동 실행

**목적**: 게임 행동 실행 및 Manager 조합

**사용 시점**: 게임플레이 중

**예시**:
```python
# ActionHandler: 게임 행동 실행
handler = ActionHandler(entity_manager, cell_manager, dialogue_manager)
result = await handler.execute_action(
    action_type=ActionType.INVESTIGATE,
    entity_id=player_id,
    target_id=object_id
)
```

**핵심 원칙**:
- ✅ Handler는 **행동 실행**에만 사용
- ✅ 여러 Manager를 조합하여 사용
- ✅ 모든 행동이 동일한 인터페이스 사용
- ❌ **객체 생성**에는 사용하지 않음

### 3.3 비교표

| 구분 | Factory | Handler |
|------|---------|---------|
| **목적** | 객체 생성 | 행동 실행 |
| **입력** | 생성 파라미터 | 행동 타입 + 대상 |
| **출력** | 생성된 객체 | 행동 결과 |
| **사용 시점** | 데이터 생성 시 | 게임플레이 중 |
| **의존성** | Repository | Manager |
| **예시** | `create_world_object()` | `execute_action()` |

## 4. Service 계층 원칙

### 4.1 Service의 역할

Service는 API 레이어와 Manager 사이의 래퍼 역할을 하며, 비즈니스 로직을 조합합니다:

- **GameService**: 게임 시작 및 상태 관리
- **CellService**: 셀 조회 및 이동
- **DialogueService**: 대화 처리
- **InteractionService**: 상호작용 처리
- **ActionService**: 액션 조회 및 상태 전이 검증
- **IntegrityService**: 데이터 무결성 검증

### 4.2 Service vs Manager vs Handler

| 계층 | 역할 | 사용 시점 | 예시 |
|------|------|-----------|------|
| **Service** | API 래퍼, 비즈니스 로직 조합 | API 엔드포인트에서 호출 | `CellService.get_current_cell()` |
| **Manager** | 도메인별 상태 관리 | Service나 Handler에서 호출 | `CellManager.get_cell_contents()` |
| **Handler** | 행동 실행 | Service나 Manager에서 호출 | `ActionHandler.execute_action()` |

### 4.3 BaseGameplayService 패턴

모든 게임플레이 서비스는 `BaseGameplayService`를 상속받아야 합니다:

```python
from app.services.gameplay.base_service import BaseGameplayService

class MyService(BaseGameplayService):
    """내 서비스"""
    
    async def my_method(self, session_id: str):
        # Manager 지연 초기화 (property로 접근)
        cell_contents = await self.cell_manager.get_cell_contents(cell_id)
        
        # Repository 직접 접근 가능
        entity = await self.game_data_repo.get_entity(entity_id)
        
        # ActionHandler 사용
        result = await self.action_handler.execute_action(...)
```

**BaseGameplayService 제공 기능**:
- `self.db`: DatabaseConnection
- `self.game_data_repo`: GameDataRepository
- `self.runtime_data_repo`: RuntimeDataRepository
- `self.reference_layer_repo`: ReferenceLayerRepository
- `self.entity_manager`: EntityManager (지연 초기화)
- `self.cell_manager`: CellManager (지연 초기화)
- `self.inventory_manager`: InventoryManager (지연 초기화)
- `self.effect_carrier_manager`: EffectCarrierManager (지연 초기화)
- `self.object_state_manager`: ObjectStateManager (지연 초기화)
- `self.action_handler`: ActionHandler (지연 초기화)

### 4.4 Service 사용 원칙

1. **BaseGameplayService 상속**: 모든 게임플레이 서비스는 `BaseGameplayService` 상속
2. **Manager 조합**: 여러 Manager를 조합하여 비즈니스 로직 구현
3. **Handler 위임**: 행동 실행은 Handler에 위임
4. **에러 처리**: 모든 예외를 명시적으로 처리하고 로깅
5. **타입 안전성**: UUID는 `uuid_helper.py` 사용

### 4.5 데이터 무결성 검증 (IntegrityService)

데이터 삭제 전에는 반드시 `IntegrityService`를 사용하여 참조 검증을 수행해야 합니다:

```python
from app.services.integrity_service import IntegrityService

integrity_service = IntegrityService()

# 엔티티 삭제 전 검증
result = await integrity_service.can_delete_entity(entity_id)
if not result.can_delete:
    # 차단 참조 정보 출력
    for blocking in result.blocking_references:
        print(f"{blocking['type']}: {blocking['message']}")
    raise ValueError("삭제할 수 없습니다: 참조가 존재합니다.")

# 셀 삭제 전 검증
result = await integrity_service.can_delete_cell(cell_id)
if not result.can_delete:
    raise ValueError(f"삭제할 수 없습니다: {result.error_message}")
```

**무결성 검증 원칙**:
- ✅ 삭제 전 반드시 검증 수행
- ✅ JSONB 필드에서 참조 검색 (SSOT 원칙 준수)
- ✅ 차단 참조 정보를 명확히 제공
- ❌ 검증 없이 삭제 금지

### 4.6 상태 전이 검증 (ActionService)

오브젝트 상태 전이는 `ActionService`의 검증 로직을 사용해야 합니다:

```python
from app.services.gameplay.action_service import ActionService

action_service = ActionService()

# 상태 전이 가능 여부 확인
can_transition = action_service._can_transition_state(
    current_state="closed",
    target_state="open",
    possible_states=["closed", "open", "locked"],
    state_transitions={"closed": ["open"], "open": ["closed"]}
)

# 액션 수행 가능 여부 확인
can_perform = action_service._check_action_conditions(
    action_config={
        "required_state": "closed",
        "target_state": "open",
        "forbidden_states": ["locked"]
    },
    current_state="closed",
    possible_states=["closed", "open", "locked"]
)
```

**상태 전이 원칙**:
- ✅ 명시적 전이 규칙 우선 사용
- ✅ `possible_states` 기반 자동 전이 규칙 (인접 상태만 허용)
- ✅ `required_state`, `forbidden_states` 검증
- ❌ 추측 로직 금지 (불확정성 불허 원칙)

## 5. Manager 계층 원칙

### 5.1 Manager의 역할

Manager는 도메인별 상태 관리와 비즈니스 로직을 담당합니다:

- **EntityManager**: 엔티티 상태 관리
- **CellManager**: 셀 및 위치 관리
- **DialogueManager**: 대화 시스템 관리
- **EffectCarrierManager**: Effect Carrier 관리

### 5.2 Manager 사용 원칙

1. **단일 책임**: 각 Manager는 하나의 도메인만 담당
2. **Repository 의존**: Manager는 Repository를 통해 데이터 접근
3. **Reference Layer 준수**: 모든 데이터 접근은 Reference Layer를 통해서만
4. **트랜잭션 관리**: 상태 변경 작업은 트랜잭션 내에서 수행

### 5.3 Manager 간 통신

Manager는 다른 Manager를 직접 호출할 수 있지만, 순환 참조를 피해야 합니다:

```python
# ✅ 올바른 방법: Manager 간 통신
class CellManager:
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager
    
    async def move_entity(self, entity_id: UUID, target_cell_id: UUID):
        # EntityManager를 통해 엔티티 조회
        entity_result = await self.entity_manager.get_entity(entity_id)
        # 이동 로직 수행
        ...
```

## 6. Repository 계층 원칙

### 6.1 Repository의 역할

Repository는 데이터 접근 계층으로, 데이터베이스 쿼리를 캡슐화합니다:

- **GameDataRepository**: Game Data 스키마 접근
- **RuntimeDataRepository**: Runtime Data 스키마 접근
- **ReferenceLayerRepository**: Reference Layer 스키마 접근

### 6.2 Repository 사용 원칙

1. **스키마 분리**: 각 Repository는 하나의 스키마만 담당
2. **타입 안전성**: 모든 쿼리는 타입 힌트로 명시
3. **트랜잭션 지원**: 트랜잭션 내에서 실행 가능
4. **에러 처리**: 명시적 에러 처리 및 로깅

## 7. 데이터베이스 스키마 참조 필수

### 7.1 mvp_schema.sql 참조 필수

**⚠️ 중요**: 모든 데이터베이스 관련 작업은 반드시 `database/setup/mvp_schema.sql`을 참조해야 합니다.

**이유**:
1. **SSOT**: 스키마 파일이 데이터베이스 구조의 단일 진실원
2. **일관성**: 코드와 스키마 간 일관성 보장
3. **타입 안전성**: 스키마에 정의된 타입과 제약조건 준수
4. **마이그레이션**: 스키마 변경 시 마이그레이션 계획 수립

**참조 시점**:
- ✅ 새로운 테이블/컬럼 추가 전
- ✅ FK 관계 설계 시
- ✅ 인덱스 설계 시
- ✅ JSONB 필드 구조 설계 시
- ✅ Manager/Repository 구현 시

**참조 방법**:
```bash
# 스키마 파일 위치
database/setup/mvp_schema.sql

# 스키마 확인
cat database/setup/mvp_schema.sql | grep -A 20 "CREATE TABLE game_data.dialogue_contexts"
```

### 7.2 스키마 변경 시 주의사항

1. **마이그레이션 필수**: 스키마 변경 시 반드시 마이그레이션 스크립트 작성
2. **Idempotent**: 마이그레이션은 반복 실행 가능해야 함
3. **롤백 계획**: 롤백 계획 수립
4. **문서 업데이트**: 관련 문서 업데이트

자세한 내용은 `02_DATABASE/MIGRATION_GUIDELINES.md`를 참조하세요.

## 8. Dialogue Manager 시스템 이해

### 8.1 Dialogue Manager의 역할

DialogueManager는 대화 시스템의 핵심 관리자로, 다음을 담당합니다:

- **대화 시작/계속/종료**: 플레이어와 NPC 간 대화 관리
- **대화 컨텍스트 로드**: `game_data.dialogue_contexts`에서 대화 컨텍스트 조회
- **대화 주제 관리**: `game_data.dialogue_topics`에서 주제별 정보 조회
- **대화 기록 저장**: `runtime_data.dialogue_history`에 대화 기록 저장
- **대화 상태 관리**: `runtime_data.dialogue_states`에 대화 상태 저장

### 8.2 Dialogue Manager 데이터 흐름

```
1. 대화 시작 요청
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

### 8.3 Dialogue Manager 사용 시 주의사항

**⚠️ 필수 이해 사항**:

1. **ID 변환**: DialogueManager는 `runtime_entity_id` (UUID)를 `game_entity_id` (VARCHAR)로 변환해야 함
   - Reference Layer를 통한 변환 필수
   - 추측 로직 금지 (명시적 변환만 허용)

2. **스키마 참조**: 대화 시스템 구현 시 반드시 `mvp_schema.sql`의 다음 테이블 참조:
   - `game_data.dialogue_contexts`: 대화 컨텍스트 정의
   - `game_data.dialogue_topics`: 대화 주제 정의
   - `game_data.dialogue_knowledge`: 대화 지식 베이스
   - `runtime_data.dialogue_history`: 대화 기록
   - `runtime_data.dialogue_states`: 대화 상태

3. **Reference Layer 준수**: 
   - Game Data 접근은 GameDataRepository를 통해서만
   - Runtime Data 접근은 RuntimeDataRepository를 통해서만
   - Reference Layer를 통한 ID 변환 필수

4. **트랜잭션 사용**: 대화 기록 저장 및 상태 업데이트는 트랜잭션 내에서 수행

### 8.4 Dialogue Manager 구현 예시

```python
# ✅ 올바른 DialogueManager 사용
dialogue_manager = DialogueManager(
    db_connection=db,
    game_data_repo=game_data_repo,
    runtime_data_repo=runtime_data_repo,
    reference_layer_repo=reference_layer_repo,
    entity_manager=entity_manager
)

# 대화 시작
result = await dialogue_manager.start_dialogue(
    player_id=player_runtime_entity_id,  # UUID
    npc_id=npc_runtime_entity_id,         # UUID
    session_id=session_id,                # UUID
    initial_topic="greeting"
)

# 대화 계속
result = await dialogue_manager.continue_dialogue(
    player_id=player_runtime_entity_id,
    npc_id=npc_runtime_entity_id,
    topic="trade",
    session_id=session_id,
    player_message="무기를 구매하고 싶습니다."
)
```

### 8.5 Dialogue Manager 관련 문서

- **시스템 가이드라인**: `03_SYSTEMS/DIALOGUE_SYSTEM_GUIDELINES.md`
- **스키마 참조**: `database/setup/mvp_schema.sql` (필수 참조)
- **아키텍처 가이드**: `docs/architecture/08_architecture_guide.md`

## 9. 참고 문서

```
┌─────────────────────────────────────┐
│   Presentation Layer                │  ← API, UI
│   (FastAPI Routes, React)           │
├─────────────────────────────────────┤
│   Business Logic Layer              │  ← Manager, Handler
│   (EntityManager, DialogueManager)  │
├─────────────────────────────────────┤
│   Data Access Layer                 │  ← Repository, Factory
│   (GameDataRepository, Factory)      │
├─────────────────────────────────────┤
│   Database Layer                    │  ← PostgreSQL
│   (game_data, reference_layer,      │
│    runtime_data)                    │
└─────────────────────────────────────┘
```

### 9.2 계층 간 통신 원칙

1. **상위 → 하위**: 상위 계층은 하위 계층만 의존
2. **하위 → 상위**: 하위 계층은 상위 계층을 모름
3. **계층 우회 금지**: 계층을 건너뛰는 직접 접근 금지

## 9. 참고 문서

- `00_CORE/01_PHILOSOPHY.md`: 핵심 개발 철학
- `00_CORE/03_ACTION_HANDLER_GUIDELINES.md`: Action Handler 시스템 가이드라인
- `02_DATABASE/DATABASE_SCHEMA_DESIGN.md`: 데이터베이스 스키마 설계 가이드라인
- `02_DATABASE/GAME_DATA_PRODUCTION_GUIDELINES.md`: 게임 데이터 제작 가이드라인
- `02_DATABASE/MIGRATION_GUIDELINES.md`: 마이그레이션 가이드라인
- `03_SYSTEMS/DIALOGUE_SYSTEM_GUIDELINES.md`: 대화 시스템 가이드라인
- `docs/architecture/08_architecture_guide.md`: 전체 아키텍처 가이드
- `docs/architecture/ARCHITECTURE_DISCUSSION.md`: 아키텍처 토론 문서
- `database/setup/mvp_schema.sql`: **데이터베이스 스키마 (필수 참조)**
- `database/game_data/unified_loader.py`: 통합 게임 데이터 로더

