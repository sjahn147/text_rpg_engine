# 코드베이스 재구조화 계획

> **생성일**: 2025-12-28  
> **목적**: interface, manager, config, handler, repository로 명확하게 구분된 구조로 재구조화

---

## 📋 현재 문제점

### 1. **구조적 중복**
- `app/world_editor/services/`에 비즈니스 로직이 중복 정의됨
- `app/entity/entity_manager.py`와 `app/world_editor/services/entity_service.py`가 유사한 기능 수행
- `app/world/cell_manager.py`와 `app/world_editor/services/cell_service.py`가 유사한 기능 수행

### 2. **책임 분리 부족**
- Service와 Manager의 역할이 모호함
- Repository 패턴이 일부만 적용됨
- Interface/Protocol 정의가 없어 의존성 주입이 어려움

### 3. **의존성 주입 위반**
- Manager 클래스들이 인자 없이 생성됨 (`GameManager()`, `CellManager()`)
- 의존성이 하드코딩되어 테스트 어려움

### 4. **계층 구조 불명확**
- UI Layer, Business Logic Layer, Data Layer의 경계가 모호함
- World Editor가 독립적인 구조로 분리되어 있음

---

## 🎯 목표 구조

### **계층별 역할 정의**

```
┌─────────────────────────────────────────────────────────┐
│                    UI Layer                              │
│  - app/ui/ (PyQt5 GUI)                                   │
│  - app/world_editor/frontend/ (React)                    │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Business Logic Layer                       │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Handlers (액션 처리)                               │  │
│  │  - app/handlers/action_handler.py                  │  │
│  │  - app/handlers/dialogue_handler.py                │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Managers (비즈니스 로직)                           │  │
│  │  - app/managers/entity_manager.py                  │  │
│  │  - app/managers/cell_manager.py                    │  │
│  │  - app/managers/dialogue_manager.py                │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Services (도메인 서비스)                           │  │
│  │  - app/services/world_editor_service.py            │  │
│  │  - app/services/simulation_service.py               │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Data Access Layer                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Repositories (데이터 접근)                         │  │
│  │  - database/repositories/game_data.py             │  │
│  │  - database/repositories/runtime_data.py           │  │
│  │  - database/repositories/reference_layer.py        │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Factories (객체 생성)                              │  │
│  │  - database/factories/game_data_factory.py        │  │
│  │  - database/factories/instance_factory.py          │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Infrastructure Layer                       │
│  - database/connection.py                               │
│  - common/config/settings.py                            │
│  - common/utils/                                        │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 제안하는 디렉토리 구조

```
app/
├── interfaces/                    # NEW: 인터페이스 정의
│   ├── __init__.py
│   ├── managers.py                # Manager 인터페이스
│   ├── repositories.py            # Repository 인터페이스
│   ├── handlers.py                # Handler 인터페이스
│   └── services.py                # Service 인터페이스
│
├── managers/                      # RENAME: app/entity, app/world → app/managers
│   ├── __init__.py
│   ├── entity_manager.py          # MOVE: app/entity/entity_manager.py
│   ├── cell_manager.py            # MOVE: app/world/cell_manager.py
│   ├── dialogue_manager.py        # MOVE: app/interaction/dialogue_manager.py
│   ├── effect_carrier_manager.py  # MOVE: app/effect_carrier/effect_carrier_manager.py
│   └── instance_manager.py        # MOVE: app/entity/instance_manager.py
│
├── handlers/                      # RENAME: app/interaction → app/handlers
│   ├── __init__.py
│   ├── action_handler.py          # MOVE: app/interaction/action_handler.py
│   └── dialogue_handler.py        # NEW: dialogue_manager의 일부 기능 분리
│
├── services/                      # NEW: 도메인 서비스
│   ├── __init__.py
│   ├── world_editor_service.py    # MERGE: app/world_editor/services/* → 통합
│   ├── simulation_service.py      # NEW: 시뮬레이션 로직
│   └── game_session_service.py    # NEW: 게임 세션 관리
│
├── config/                        # NEW: 설정 관리
│   ├── __init__.py
│   ├── app_config.py              # 앱 설정
│   ├── db_config.py               # DB 설정
│   └── game_config.py             # 게임 설정
│
├── core/                          # KEEP: 핵심 게임 로직
│   ├── game_manager.py            # 게임 전체 관리
│   ├── scenario_executor.py       # 시나리오 실행
│   ├── scenario_loader.py         # 시나리오 로드
│   └── framework_manager.py       # 프레임워크 관리
│
├── systems/                       # KEEP: 시스템 레벨 기능
│   ├── time_system.py
│   └── npc_behavior.py
│
├── ui/                            # KEEP: PyQt5 GUI
│   ├── main_window.py
│   ├── dashboard.py
│   └── screens/
│
└── api/                           # NEW: API 레이어 (World Editor 포함)
    ├── __init__.py
    ├── routes/                    # MOVE: app/world_editor/routes → app/api/routes
    │   ├── entities.py
    │   ├── cells.py
    │   ├── locations.py
    │   └── ...
    ├── schemas.py                 # MOVE: app/world_editor/schemas.py
    ├── main.py                    # MOVE: app/world_editor/main.py
    └── websocket.py               # NEW: WebSocket 핸들러 분리
```

---

## 🔄 마이그레이션 계획

### **Phase 1: 인터페이스 정의** (1-2일)

1. **`app/interfaces/` 생성**
   ```python
   # app/interfaces/managers.py
   from abc import ABC, abstractmethod
   from typing import Dict, List, Optional, Any
   
   class IEntityManager(ABC):
       @abstractmethod
       async def create_entity(self, ...) -> str:
           pass
       
       @abstractmethod
       async def get_entity(self, ...) -> Dict[str, Any]:
           pass
   
   class ICellManager(ABC):
       @abstractmethod
       async def create_cell(self, ...) -> str:
           pass
   ```

2. **Repository 인터페이스 정의**
   ```python
   # app/interfaces/repositories.py
   class IGameDataRepository(ABC):
       @abstractmethod
       async def get_entity(self, entity_id: str) -> Optional[Dict]:
           pass
   ```

### **Phase 2: Manager 통합** (2-3일)

1. **`app/managers/` 생성 및 파일 이동**
   - `app/entity/entity_manager.py` → `app/managers/entity_manager.py`
   - `app/world/cell_manager.py` → `app/managers/cell_manager.py`
   - `app/interaction/dialogue_manager.py` → `app/managers/dialogue_manager.py`
   - `app/effect_carrier/effect_carrier_manager.py` → `app/managers/effect_carrier_manager.py`

2. **인터페이스 구현**
   - 각 Manager가 해당 인터페이스를 구현하도록 수정

3. **의존성 주입 적용**
   ```python
   # Before
   class GameSession:
       def __init__(self, session_id: str):
           self.cell_manager = CellManager()  # ❌
   
   # After
   class GameSession:
       def __init__(self, session_id: str, cell_manager: ICellManager):
           self.cell_manager = cell_manager  # ✅
   ```

### **Phase 3: Service 통합** (3-4일)

1. **World Editor Services 통합**
   - `app/world_editor/services/*` → `app/services/world_editor_service.py`
   - 각 Service를 Manager를 사용하도록 리팩토링
   ```python
   # Before
   class EntityService:
       async def get_entities_by_cell(self, cell_id: str):
           # 직접 DB 쿼리
   
   # After
   class WorldEditorService:
       def __init__(self, entity_manager: IEntityManager):
           self.entity_manager = entity_manager
       
       async def get_entities_by_cell(self, cell_id: str):
           # Manager를 통해 접근
   ```

2. **Handler 분리**
   - `app/interaction/action_handler.py` → `app/handlers/action_handler.py`
   - Dialogue 관련 Handler 분리

### **Phase 4: API 레이어 재구성** (2-3일)

1. **`app/api/` 생성**
   - `app/world_editor/routes/` → `app/api/routes/`
   - `app/world_editor/schemas.py` → `app/api/schemas.py`
   - `app/world_editor/main.py` → `app/api/main.py`

2. **Route → Service → Manager 흐름**
   ```python
   # app/api/routes/entities.py
   @router.get("/entities")
   async def get_entities(
       service: WorldEditorService = Depends(get_world_editor_service)
   ):
       return await service.get_entities()
   
   # app/services/world_editor_service.py
   class WorldEditorService:
       def __init__(self, entity_manager: IEntityManager):
           self.entity_manager = entity_manager
   ```

### **Phase 5: Config 분리** (1일)

1. **`app/config/` 생성**
   - `common/config/settings.py` → `app/config/app_config.py`
   - DB 설정 분리
   - 게임 설정 분리

### **Phase 6: 테스트 및 검증** (2-3일)

1. **의존성 주입 테스트**
2. **통합 테스트**
3. **성능 테스트**

---

## 📝 상세 설계

### **1. Interface 정의**

```python
# app/interfaces/managers.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class IEntityManager(ABC):
    """엔티티 관리자 인터페이스"""
    
    @abstractmethod
    async def create_entity(
        self, 
        entity_template_id: str,
        session_id: str,
        runtime_cell_id: str,
        position: Dict[str, float]
    ) -> str:
        """엔티티 생성"""
        pass
    
    @abstractmethod
    async def get_entity(self, runtime_entity_id: str) -> Optional[Dict[str, Any]]:
        """엔티티 조회"""
        pass
    
    @abstractmethod
    async def update_entity(self, runtime_entity_id: str, updates: Dict[str, Any]) -> bool:
        """엔티티 업데이트"""
        pass
    
    @abstractmethod
    async def delete_entity(self, runtime_entity_id: str) -> bool:
        """엔티티 삭제"""
        pass

class ICellManager(ABC):
    """셀 관리자 인터페이스"""
    
    @abstractmethod
    async def create_cell(
        self,
        static_cell_id: str,
        session_id: str
    ) -> str:
        """셀 생성"""
        pass
    
    @abstractmethod
    async def get_cell(self, runtime_cell_id: str) -> Optional[Dict[str, Any]]:
        """셀 조회"""
        pass
    
    @abstractmethod
    async def get_cell_contents(self, runtime_cell_id: str) -> Dict[str, Any]:
        """셀 컨텐츠 조회"""
        pass
```

### **2. Manager 구현**

```python
# app/managers/entity_manager.py
from app.interfaces.managers import IEntityManager
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository

class EntityManager(IEntityManager):
    """엔티티 관리자 구현"""
    
    def __init__(
        self,
        db_connection: DatabaseConnection,
        game_data_repo: GameDataRepository,
        runtime_data_repo: RuntimeDataRepository,
        reference_layer_repo: ReferenceLayerRepository
    ):
        self.db = db_connection
        self.game_data = game_data_repo
        self.runtime_data = runtime_data_repo
        self.reference_layer = reference_layer_repo
    
    async def create_entity(self, ...) -> str:
        # 구현
        pass
```

### **3. Service 구현**

```python
# app/services/world_editor_service.py
from app.interfaces.managers import IEntityManager, ICellManager
from app.interfaces.services import IWorldEditorService

class WorldEditorService(IWorldEditorService):
    """World Editor 서비스"""
    
    def __init__(
        self,
        entity_manager: IEntityManager,
        cell_manager: ICellManager
    ):
        self.entity_manager = entity_manager
        self.cell_manager = cell_manager
    
    async def get_entities_by_cell(self, cell_id: str) -> List[Dict]:
        # Manager를 통해 접근
        return await self.entity_manager.get_entities_in_cell(cell_id)
```

### **4. API Route**

```python
# app/api/routes/entities.py
from fastapi import APIRouter, Depends
from app.services.world_editor_service import WorldEditorService
from app.api.schemas import EntityResponse

router = APIRouter()

def get_world_editor_service() -> WorldEditorService:
    # 의존성 주입
    entity_manager = get_entity_manager()
    cell_manager = get_cell_manager()
    return WorldEditorService(entity_manager, cell_manager)

@router.get("/entities", response_model=List[EntityResponse])
async def get_entities(
    service: WorldEditorService = Depends(get_world_editor_service)
):
    return await service.get_all_entities()
```

---

## ⚠️ 주의사항

### **1. 점진적 마이그레이션**
- 한 번에 모든 것을 변경하지 말고 단계적으로 진행
- 각 Phase마다 테스트 통과 확인

### **2. 하위 호환성**
- 기존 코드가 작동하는 동안 새 구조로 점진적 전환
- 임시 어댑터 패턴 사용 가능

### **3. 의존성 주입 컨테이너**
- FastAPI의 `Depends` 활용
- 또는 별도의 DI 컨테이너 구현

### **4. 테스트 전략**
- 각 계층별 단위 테스트
- Mock을 사용한 통합 테스트
- E2E 테스트

---

## 📊 예상 효과

### **1. 코드 품질**
- ✅ 명확한 책임 분리
- ✅ 테스트 용이성 향상
- ✅ 의존성 관리 개선

### **2. 유지보수성**
- ✅ 중복 코드 제거
- ✅ 변경 영향 범위 축소
- ✅ 코드 재사용성 향상

### **3. 확장성**
- ✅ 새로운 기능 추가 용이
- ✅ 플러그인 구조 지원
- ✅ 마이크로서비스 전환 가능

---

## 🚀 실행 순서

1. **레거시 코드 백업** ✅ (완료)
2. **인터페이스 정의** (Phase 1)
3. **Manager 통합** (Phase 2)
4. **Service 통합** (Phase 3)
5. **API 레이어 재구성** (Phase 4)
6. **Config 분리** (Phase 5)
7. **테스트 및 검증** (Phase 6)

---

## 📅 예상 일정

- **총 소요 시간**: 12-16일
- **Phase 1-2**: 3-5일 (인터페이스 + Manager)
- **Phase 3**: 3-4일 (Service 통합)
- **Phase 4**: 2-3일 (API 재구성)
- **Phase 5**: 1일 (Config)
- **Phase 6**: 2-3일 (테스트)

