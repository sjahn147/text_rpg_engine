# 텍스트 어드벤처 UI 통합 계획

**작성 일자**: 2025-12-28  
**최신화 날짜**: 2025-12-28

## 🎯 현재 상황

### 기존 인프라
- ✅ **World Editor 프론트엔드**: React + TypeScript + Tailwind CSS (Vite)
- ✅ **World Editor 백엔드**: FastAPI (FastAPI)
- ✅ **데이터베이스**: PostgreSQL (game_data + runtime_data)
- ✅ **Manager 클래스들**: EntityManager, CellManager, DialogueManager 등
- ✅ **Repository 패턴**: GameDataRepository, RuntimeDataRepository

### 통합 포인트
- **같은 스택**: React + TypeScript + Tailwind CSS
- **같은 DB**: PostgreSQL (game_data는 World Editor가, runtime_data는 게임플레이가 사용)
- **같은 백엔드**: FastAPI 기반

---

## 🏗️ 통합 구조 제안

### 옵션 1: 단일 앱 내 모드 전환 (권장)

```
app/ui/                              # world_editor → ui로 통합
├── frontend/
│   ├── src/
│   │   ├── App.tsx                 # 모드 전환 (Editor/Game)
│   │   ├── modes/
│   │   │   ├── EditorMode.tsx      # 기존 World Editor
│   │   │   └── GameMode.tsx        # 새 텍스트 어드벤처 UI
│   │   ├── components/              # 공통 컴포넌트
│   │   │   ├── editor/             # Editor 전용 컴포넌트
│   │   │   │   ├── MapCanvas.tsx
│   │   │   │   ├── PinEditor.tsx
│   │   │   │   └── ...
│   │   │   └── game/               # Game 전용 컴포넌트
│   │   │       ├── GameView.tsx
│   │   │       ├── MessageLayer.tsx
│   │   │       ├── ChoiceLayer.tsx
│   │   │       └── InfoPanel.tsx
│   │   ├── screens/                 # 화면 컴포넌트
│   │   │   ├── editor/             # Editor 화면
│   │   │   │   ├── MapScreen.tsx
│   │   │   │   ├── EntityScreen.tsx
│   │   │   │   └── ...
│   │   │   └── game/               # Game 화면
│   │   │       ├── GameScreen.tsx
│   │   │       ├── InventoryScreen.tsx
│   │   │       ├── JournalScreen.tsx
│   │   │       └── ...
│   │   └── services/
│   │       ├── editorApi.ts        # 기존 Editor API
│   │       └── gameApi.ts          # 새 Gameplay API
│   └── package.json
│
└── backend/                         # FastAPI 백엔드 (또는 app/api/로 분리 가능)
    └── main.py                      # FastAPI 앱
        ├── /api/editor/*           # 기존 Editor API
        └── /api/gameplay/*         # 새 Gameplay API
```

**장점**:
- 코드 공유 (스타일, 유틸리티)
- 단일 빌드/배포
- 모드 전환 간단 (URL 파라미터 또는 메뉴)

**단점**:
- 번들 크기 증가 (하지만 코드 스플리팅 가능)

---

### 옵션 2: 별도 앱으로 분리

```
rpg_engine/
├── app/
│   ├── world_editor/               # 기존 World Editor
│   └── gameplay/                   # 새 Gameplay 앱
│       ├── frontend/
│       └── backend/
│
└── app/api/
    ├── routes/
    │   ├── editor.py               # 기존 Editor API
    │   └── gameplay.py             # 새 Gameplay API
```

**장점**:
- 완전 분리
- 독립적 배포 가능

**단점**:
- 코드 중복
- 유지보수 복잡

---

## 💡 권장: 옵션 1 (단일 앱 내 모드 전환)

### Phase 1: 백엔드 API 추가

#### 1.1 Gameplay API 라우트 생성
```python
# app/api/routes/gameplay.py
from fastapi import APIRouter, Depends
from app.engine.game_engine import GameEngine
from app.gameplay.player_controller import PlayerController

router = APIRouter(prefix="/api/gameplay", tags=["gameplay"])

@router.post("/start")
async def start_game(player_template_id: str):
    """새 게임 시작"""
    # GameEngine.start_game() 호출
    pass

@router.get("/current-state")
async def get_current_state(session_id: str):
    """현재 게임 상태 조회"""
    # 현재 셀, 엔티티, 액션 조회
    pass

@router.post("/move")
async def move_player(session_id: str, target_cell_id: str):
    """플레이어 이동"""
    # PlayerController.move_player() 호출
    pass

@router.post("/dialogue/start")
async def start_dialogue(session_id: str, npc_id: str):
    """대화 시작"""
    # PlayerController.start_dialogue() 호출
    pass

@router.post("/action")
async def execute_action(session_id: str, action_type: str, target_id: str = None):
    """액션 실행"""
    # PlayerController.interact_with_entity() 호출
    pass
```

#### 1.2 main.py에 라우트 추가
```python
# app/ui/backend/main.py (또는 app/api/main.py)
from app.api.routes import gameplay  # 새로 추가

# 기존 코드...
app.include_router(gameplay.router)  # 새로 추가
```

---

### Phase 2: 프론트엔드 구조 확장

#### 2.1 App.tsx에 모드 전환 추가
```tsx
// app/ui/frontend/src/App.tsx
import { useState } from 'react';
import { EditorMode } from './modes/EditorMode';
import { GameMode } from './modes/GameMode';

function App() {
  const [mode, setMode] = useState<'editor' | 'game'>('editor');
  
  // URL 파라미터로 모드 확인
  const urlParams = new URLSearchParams(window.location.search);
  const urlMode = urlParams.get('mode') as 'editor' | 'game' | null;
  const currentMode = urlMode || mode;
  
  return (
    <div className="app-container">
      {/* 모드 전환 버튼 (개발용) */}
      <div className="fixed top-4 left-4 z-50">
        <button
          onClick={() => setMode(currentMode === 'editor' ? 'game' : 'editor')}
          className="px-4 py-2 bg-white/20 text-black rounded-lg"
        >
          {currentMode === 'editor' ? '게임 모드' : '에디터 모드'}
        </button>
      </div>
      
      {currentMode === 'editor' ? <EditorMode /> : <GameMode />}
    </div>
  );
}
```

#### 2.2 GameMode 컴포넌트 생성
```tsx
// app/ui/frontend/src/modes/GameMode.tsx
import { GameScreen } from '../screens/game/GameScreen';
import { useGameStore } from '../store/gameStore';

export const GameMode: React.FC = () => {
  return (
    <div className="game-mode-container">
      <GameScreen />
    </div>
  );
};
```

#### 2.3 Game Screen 생성
```tsx
// app/ui/frontend/src/screens/game/GameScreen.tsx
import { MessageLayer } from '../../components/game/MessageLayer';
import { ChoiceLayer } from '../../components/game/ChoiceLayer';
import { InfoPanel } from '../../components/game/InfoPanel';

export const GameScreen: React.FC = () => {
  const [isInfoOpen, setIsInfoOpen] = useState(false);
  
  return (
    <div className="game-container">
      {/* 메인 화면: 텍스트 + 선택지 */}
      <MessageLayer />
      <ChoiceLayer />
      
      {/* 정보 패널 토글 버튼 */}
      <button
        onClick={() => setIsInfoOpen(!isInfoOpen)}
        className="fixed top-4 right-4 z-30"
      >
        정보
      </button>
      
      {/* 정보 패널 (토글) */}
      {isInfoOpen && <InfoPanel onClose={() => setIsInfoOpen(false)} />}
    </div>
  );
};
```

#### 2.4 Game API 서비스 생성
```tsx
// app/ui/frontend/src/services/gameApi.ts
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export class GameApi {
  private client = axios.create({
    baseURL: API_BASE_URL,
    headers: { 'Content-Type': 'application/json' },
  });

  async startGame(playerTemplateId: string) {
    const response = await this.client.post('/api/gameplay/start', null, {
      params: { player_template_id: playerTemplateId },
    });
    return response.data;
  }

  async getCurrentState(sessionId: string) {
    const response = await this.client.get('/api/gameplay/current-state', {
      params: { session_id: sessionId },
    });
    return response.data;
  }

  async movePlayer(sessionId: string, targetCellId: string) {
    const response = await this.client.post('/api/gameplay/move', {
      session_id: sessionId,
      target_cell_id: targetCellId,
    });
    return response.data;
  }

  async startDialogue(sessionId: string, npcId: string) {
    const response = await this.client.post('/api/gameplay/dialogue/start', {
      session_id: sessionId,
      npc_id: npcId,
    });
    return response.data;
  }

  async executeAction(sessionId: string, actionType: string, targetId?: string) {
    const response = await this.client.post('/api/gameplay/action', {
      session_id: sessionId,
      action_type: actionType,
      target_id: targetId,
    });
    return response.data;
  }
}

export const gameApi = new GameApi();
```

---

### Phase 3: 게임 엔진 통합

#### 3.1 GameEngine 생성 (기존 Manager 활용)
```python
# app/engine/game_engine.py
from app.managers.entity_manager import EntityManager
from app.managers.cell_manager import CellManager
from app.managers.dialogue_manager import DialogueManager
from app.handlers.action_handler import ActionHandler

class GameEngine:
    def __init__(self,
                 entity_manager: EntityManager,
                 cell_manager: CellManager,
                 dialogue_manager: DialogueManager,
                 action_handler: ActionHandler):
        self.entity_manager = entity_manager
        self.cell_manager = cell_manager
        self.dialogue_manager = dialogue_manager
        self.action_handler = action_handler
        
        self.is_running = False
        self.current_session_id: Optional[str] = None
    
    async def start_game(self, player_template_id: str) -> str:
        """게임 시작"""
        # 세션 생성
        # 플레이어 생성
        # 시작 셀 설정
        pass
    
    async def get_current_state(self, session_id: str) -> Dict[str, Any]:
        """현재 게임 상태 조회"""
        # 현재 셀 정보
        # 셀 내 엔티티 목록
        # 사용 가능한 액션
        pass
```

#### 3.2 PlayerController 생성
```python
# app/gameplay/player_controller.py
from app.engine.game_engine import GameEngine
from app.managers.entity_manager import EntityManager
from app.managers.cell_manager import CellManager

class PlayerController:
    def __init__(self,
                 game_engine: GameEngine,
                 entity_manager: EntityManager,
                 cell_manager: CellManager):
        self.game_engine = game_engine
        self.entity_manager = entity_manager
        self.cell_manager = cell_manager
    
    async def move_player(self, session_id: str, target_cell_id: str):
        """플레이어 이동"""
        # CellManager.move_entity_between_cells() 호출
        pass
    
    async def start_dialogue(self, session_id: str, npc_id: str):
        """대화 시작"""
        # DialogueManager.start_dialogue() 호출
        pass
    
    async def interact_with_entity(self, session_id: str, target_id: str, action_type: str):
        """엔티티와 상호작용"""
        # ActionHandler.execute_action() 호출
        pass
```

---

## 📊 데이터 흐름

### 게임 시작
```
1. 프론트엔드: POST /api/gameplay/start
   ↓
2. 백엔드: GameEngine.start_game()
   - 세션 생성 (runtime_data.active_sessions)
   - 플레이어 생성 (EntityManager.create_entity())
   - 시작 셀 설정 (CellManager.create_cell())
   ↓
3. 백엔드: 현재 상태 조회
   - CellManager.get_cell()
   - EntityManager.get_entities_in_cell()
   - ActionHandler.get_available_actions()
   ↓
4. 백엔드: 텍스트 변환
   - 셀 정보 → 서술문: "당신은 마을 광장에 도착했습니다."
   - 엔티티 목록 → 선택지: "상점 주인과 대화하기"
   ↓
5. 프론트엔드: UI 업데이트
   - MessageLayer: 서술문 표시
   - ChoiceLayer: 선택지 버튼 표시
```

### 셀 이동
```
1. 플레이어: "상점으로 이동" 버튼 클릭
   ↓
2. 프론트엔드: POST /api/gameplay/move
   { session_id, target_cell_id: "CELL_SHOP_001" }
   ↓
3. 백엔드: PlayerController.move_player()
   - CellManager.move_entity_between_cells()
   - 이벤트 발행 (선택적)
   ↓
4. 백엔드: 새 셀 정보 조회
   - CellManager.get_cell("CELL_SHOP_001")
   - EntityManager.get_entities_in_cell()
   ↓
5. 백엔드: 텍스트 변환
   - 셀 description → 서술문
   - 엔티티 목록 → 선택지
   ↓
6. 프론트엔드: UI 업데이트
   - MessageLayer: "상점에 도착했습니다."
   - ChoiceLayer: 새 선택지 버튼 표시
```

---

## 🎯 구현 단계

### Phase 1: 백엔드 API (1-2일)
1. `app/api/routes/gameplay.py` 생성
2. `app/engine/game_engine.py` 생성 (기존 Manager 활용)
3. `app/gameplay/player_controller.py` 생성
4. `app/world_editor/main.py`에 라우트 추가
5. API 테스트

### Phase 2: 프론트엔드 기본 구조 (2-3일)
1. `app/world_editor/frontend/src/modes/GameMode.tsx` 생성
2. `app/world_editor/frontend/src/components/game/` 폴더 생성
3. `app/world_editor/frontend/src/services/gameApi.ts` 생성
4. `app/world_editor/frontend/src/App.tsx`에 모드 전환 추가
5. 기본 레이아웃 테스트

### Phase 3: 게임 컴포넌트 (3-4일)
1. `MessageLayer.tsx` - 텍스트 표시
2. `ChoiceLayer.tsx` - 선택지 버튼
3. `InfoPanel.tsx` - 정보 패널 (토글)
4. `GameView.tsx` - 메인 컨테이너
5. 스타일링 (novel_game 스타일)

### Phase 4: 게임플레이 통합 (3-4일)
1. 게임 시작 기능
2. 셀 이동 기능
3. NPC 대화 기능
4. 액션 실행 기능
5. 통합 테스트

### Phase 5: UI 개선 (2-3일)
1. 애니메이션 추가
2. 정보 패널 (inventory, 시간, 저널)
3. 히스토리 기능
4. 최종 테스트

---

## 🔧 기술적 고려사항

### 코드 공유
- **스타일**: Tailwind CSS 설정 공유
- **유틸리티**: 공통 유틸리티 함수
- **타입**: 공통 타입 정의

### 번들 크기
- **코드 스플리팅**: Editor/Game 모드별로 분리
- **Lazy Loading**: Game 컴포넌트는 필요할 때만 로드

### API 공유
- **같은 백엔드**: FastAPI 앱 하나로 관리
- **CORS**: 이미 설정되어 있음
- **인증**: 필요시 추가

---

## ✅ 결론

**권장 구조**: **옵션 1 (단일 앱 내 모드 전환)**

**이유**:
1. 기존 인프라 활용 (같은 스택, 같은 DB)
2. 코드 공유 가능 (스타일, 유틸리티)
3. 단일 빌드/배포
4. 모드 전환 간단 (URL 파라미터)

**핵심 원칙**:
- 기존 World Editor는 그대로 유지
- Game 모드는 새로 추가
- Manager 클래스는 그대로 활용
- 백엔드는 API만 추가

**예상 소요 시간**: 2-3주 (단계별 구현)

