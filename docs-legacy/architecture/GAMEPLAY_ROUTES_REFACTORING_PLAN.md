# Gameplay Routes 리팩토링 계획

**작성일**: 2025-12-28  
**목적**: `app/ui/backend/routes/gameplay.py` (1597줄)를 `app/services/gameplay`로 분리하여 구조 개선

---

## 현재 문제점

1. **단일 파일 과다**: `gameplay.py`가 1597줄로 너무 큼
2. **책임 혼재**: API 라우트 정의와 비즈니스 로직이 혼재
3. **테스트 어려움**: 단일 파일에 모든 로직이 있어 단위 테스트 어려움
4. **재사용 불가**: 다른 곳에서 게임플레이 로직 재사용 불가

---

## 목표 구조

```
app/
├── services/
│   └── gameplay/                    # 신규: 게임플레이 서비스
│       ├── __init__.py
│       ├── game_service.py          # 게임 시작/상태 관리
│       ├── cell_service.py           # 셀 조회/이동
│       ├── dialogue_service.py      # 대화 처리
│       ├── interaction_service.py   # 상호작용 처리
│       ├── inventory_service.py     # 인벤토리 관리
│       └── action_service.py        # 액션 처리
│
└── ui/
    └── backend/
        └── routes/
            └── gameplay.py          # API 라우트만 (200줄 이하)
```

---

## 분리 계획

### Phase 1: 서비스 모듈 생성

#### 1.1 `app/services/gameplay/__init__.py`
```python
"""
게임플레이 서비스 모듈
"""
from app.services.gameplay.game_service import GameService
from app.services.gameplay.cell_service import CellService
from app.services.gameplay.dialogue_service import DialogueService
from app.services.gameplay.interaction_service import InteractionService
from app.services.gameplay.inventory_service import InventoryService
from app.services.gameplay.action_service import ActionService

__all__ = [
    'GameService',
    'CellService',
    'DialogueService',
    'InteractionService',
    'InventoryService',
    'ActionService',
]
```

#### 1.2 `app/services/gameplay/game_service.py`
**책임**: 게임 시작, 상태 조회
- `start_game(player_template_id, start_cell_id)`
- `get_game_state(session_id)`
- `get_player_inventory(session_id)`

**현재 위치**: `gameplay.py:118-212`

#### 1.3 `app/services/gameplay/cell_service.py`
**책임**: 셀 조회, 이동
- `get_current_cell(session_id)`
- `move_player(session_id, target_cell_id)`

**현재 위치**: `gameplay.py:215-479`

#### 1.4 `app/services/gameplay/dialogue_service.py`
**책임**: 대화 처리
- `start_dialogue(session_id, npc_id)`
- `process_dialogue_choice(session_id, dialogue_id, choice_id)`

**현재 위치**: `gameplay.py:480-536`

#### 1.5 `app/services/gameplay/interaction_service.py`
**책임**: 상호작용 처리
- `interact_with_entity(session_id, entity_id, action_type)`
- `interact_with_object(session_id, object_id, action_type)`
- `pickup_from_object(session_id, object_id, item_id)`
- `combine_items(session_id, item_ids)`

**현재 위치**: `gameplay.py:537-1271`

#### 1.6 `app/services/gameplay/action_service.py`
**책임**: 사용 가능한 액션 조회
- `get_available_actions(session_id)`

**현재 위치**: `gameplay.py:1049-1174`

---

### Phase 2: 라우트 파일 간소화

#### 2.1 `app/ui/backend/routes/gameplay.py` (리팩토링 후)
```python
"""
게임플레이 API 라우트 (간소화)
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.services.gameplay import (
    GameService,
    CellService,
    DialogueService,
    InteractionService,
    ActionService
)

router = APIRouter(prefix="/api/gameplay", tags=["gameplay"])

# 서비스 인스턴스 (싱글톤 또는 의존성 주입)
_game_service = None
_cell_service = None
_dialogue_service = None
_interaction_service = None
_action_service = None

def get_game_service() -> GameService:
    global _game_service
    if _game_service is None:
        _game_service = GameService()
    return _game_service

# ... (다른 서비스 getter들)

# 요청/응답 스키마
class StartGameRequest(BaseModel):
    player_template_id: str
    start_cell_id: Optional[str] = None

# API 엔드포인트 (서비스 호출만)
@router.post("/start")
async def start_game(request: StartGameRequest):
    service = get_game_service()
    return await service.start_game(
        request.player_template_id,
        request.start_cell_id
    )

@router.get("/state/{session_id}")
async def get_current_state(session_id: str):
    service = get_game_service()
    return await service.get_game_state(session_id)

# ... (다른 엔드포인트들도 동일한 패턴)
```

---

## 서비스 클래스 구조

### 기본 서비스 패턴
```python
"""
게임플레이 서비스 베이스 클래스
"""
from typing import Optional
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from app.handlers.action_handler import ActionHandler
from app.managers.entity_manager import EntityManager
from app.managers.cell_manager import CellManager
from common.utils.logger import logger

class BaseGameplayService:
    """게임플레이 서비스 베이스 클래스"""
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        self.db = db_connection or DatabaseConnection()
        self.game_data_repo = GameDataRepository(self.db)
        self.runtime_data_repo = RuntimeDataRepository(self.db)
        self.reference_layer_repo = ReferenceLayerRepository(self.db)
        self.logger = logger
        
        # Managers 초기화
        self.entity_manager = EntityManager(
            self.db,
            self.game_data_repo,
            self.runtime_data_repo,
            self.reference_layer_repo
        )
        self.cell_manager = CellManager(
            self.db,
            self.game_data_repo,
            self.runtime_data_repo,
            self.reference_layer_repo,
            self.entity_manager
        )
        
        # ActionHandler 초기화 (필요한 서비스만)
        # ...
```

---

## 마이그레이션 단계

### Step 1: 서비스 모듈 생성
1. `app/services/gameplay/` 디렉토리 생성
2. 각 서비스 파일 생성 (빈 클래스)
3. `__init__.py` 작성

### Step 2: 로직 이동
1. `gameplay.py`에서 각 서비스로 로직 이동
2. 의존성 주입 구조 설정
3. 테스트 작성

### Step 3: 라우트 간소화
1. `gameplay.py`를 서비스 호출만 하도록 수정
2. 요청/응답 스키마는 라우트에 유지
3. 에러 핸들링은 서비스에서 처리

### Step 4: 테스트 및 검증
1. 기존 API 테스트 실행
2. 통합 테스트 작성
3. 성능 테스트

---

## 예상 효과

1. **가독성 향상**: 각 서비스가 단일 책임
2. **테스트 용이**: 서비스 단위 테스트 가능
3. **재사용성**: 다른 곳에서 서비스 재사용 가능
4. **유지보수성**: 변경 시 영향 범위 명확

---

## 참고: World Editor 서비스 구조

`app/services/world_editor/`의 구조를 참고:
- 각 도메인별 서비스 분리 (cell_service, entity_service, etc.)
- Repository 패턴 사용
- 명확한 책임 분리

---

## 다음 단계

1. ✅ 리팩토링 계획 문서 작성
2. ⏳ 서비스 모듈 생성
3. ⏳ 로직 이동
4. ⏳ 라우트 간소화
5. ⏳ 테스트 작성

