# 텍스트 어드벤처 UI 제안 (novel_game 스타일)

**작성 일자**: 2025-12-28  
**참고**: `c:\hobby\novel_game` 프로젝트의 UI 스타일

## 🎨 UI 컨셉

### 핵심 철학: "소설책을 읽는 느낌"
**복잡한 백엔드와 로직을 미니멀한 UI 뒤로 숨기기**

- **메인 화면**: 서술 텍스트 + 선택지 버튼만 (소설책처럼 단순)
- **백엔드는 조용히**: 복잡한 쿼리와 로직은 사용자가 느끼지 못하게
- **필수 정보는 접근 가능**: inventory, 시간, 저널 등은 토글/사이드 메뉴로
- **미니멀 디자인**: 불필요한 UI 요소 제거, 텍스트에 집중

### novel_game의 UI 특징
- **부드럽고 세련된 디자인**: Tailwind CSS 기반 모던한 UI
- **텍스트 중심**: 메시지 레이어와 선택지 레이어로 구성
- **레이어 기반 구조**: Background, Character, Message, Choice 레이어 분리
- **애니메이션**: 부드러운 전환 효과
- **반응형**: 다양한 화면 크기 지원
- **미니멀**: 복잡한 UI 요소 없이 텍스트와 선택지만

### RPG 엔진에 적용할 UI
- **텍스트 어드벤처 형식**: 마을을 방문하고 돌아다니는 게임플레이
- **백엔드 쿼리 기반**: 실제 runtime 데이터를 조회하여 표시 (사용자는 모름)
- **선택지 기반 탐험**: 셀 이동, NPC 대화, 상호작용 (간단한 버튼으로)
- **정보는 숨겨두고**: inventory, 시간, 저널은 토글 메뉴로 접근

---

## 🏗️ 제안하는 구조

### 프론트엔드 구조
```
rpg_engine_frontend/
├── src/
│   ├── App.tsx                 # 메인 앱
│   ├── components/
│   │   ├── GameView.tsx        # 게임 뷰 (메인 컨테이너)
│   │   ├── LocationLayer.tsx   # 위치/셀 정보 표시
│   │   ├── MessageLayer.tsx    # 게임 메시지 표시 (narration, dialogue)
│   │   ├── ChoiceLayer.tsx    # 선택지 버튼
│   │   ├── EntityList.tsx      # 현재 셀의 엔티티 목록
│   │   ├── StatusPanel.tsx    # 플레이어 상태 (HP, 위치 등)
│   │   └── HistoryPanel.tsx   # 대화/액션 히스토리
│   ├── services/
│   │   └── gameApi.ts          # 백엔드 API 호출
│   ├── store/
│   │   └── gameStore.ts        # 게임 상태 관리 (Zustand)
│   └── types/
│       └── game.ts             # 타입 정의
├── package.json
└── vite.config.ts
```

### 백엔드 API 구조
```
app/
├── api/
│   ├── routes/
│   │   └── gameplay.py         # 게임플레이 API
│   └── schemas.py              # API 스키마
└── engine/
    └── game_engine.py          # 게임 엔진 (게임 루프)
```

---

## 📋 UI 컴포넌트 상세

### 1. GameView (메인 컨테이너)
```tsx
// 미니멀한 레이아웃 - 소설책을 읽는 느낌
<div className="game-container">
  {/* 메인 화면: 텍스트와 선택지만 */}
  <MessageLayer />        {/* 하단: 게임 메시지 (서술, 대화) */}
  <ChoiceLayer />          {/* 중앙/하단: 선택지 버튼 */}
  
  {/* 숨겨진 정보 패널들 (토글로 열기) */}
  <InfoToggleButton />     {/* 우측 상단: 정보 메뉴 토글 */}
  {isInfoOpen && (
    <>
      <InventoryPanel />   {/* 인벤토리 */}
      <TimePanel />        {/* 현재 시간 */}
      <JournalPanel />     {/* 저널/히스토리 */}
      <StatusPanel />      {/* 플레이어 상태 */}
    </>
  )}
</div>
```

**디자인 원칙**:
- 메인 화면은 **텍스트와 선택지만** 보임
- 복잡한 정보는 **토글 메뉴로 숨김**
- 백엔드 쿼리는 **사용자가 느끼지 못하게** 조용히 실행

### 2. MessageLayer (게임 메시지)
```tsx
// 소설책을 읽는 느낌 - 미니멀하고 깔끔한 텍스트 표시
<div className="message-layer">
  {/* Narration (서술) - 소설책의 서술문처럼 */}
  <div className="narration-message">
    당신은 마을 광장에 도착했습니다. 
    주변에는 상점과 여관이 보입니다.
    {/* 백엔드에서 조회한 셀 정보가 자연스럽게 텍스트로 변환됨 */}
  </div>
  
  {/* Dialogue (대화) - 대화문처럼 */}
  <div className="dialogue-message">
    <span className="speaker">상점 주인</span>
    <span className="text">어서오세요! 무엇을 도와드릴까요?</span>
    {/* 백엔드에서 조회한 NPC 대화가 자연스럽게 표시됨 */}
  </div>
</div>
```

**핵심**: 
- 복잡한 데이터 구조는 **텍스트로 자연스럽게 변환**
- 사용자는 **소설책을 읽는 것처럼** 텍스트만 읽음
- 백엔드 쿼리 결과는 **사용자가 느끼지 못하게** 처리

### 3. ChoiceLayer (선택지)
```tsx
// 부드러운 버튼 스타일
<div className="choice-layer">
  <button className="choice-button">
    상점으로 이동
  </button>
  <button className="choice-button">
    여관으로 이동
  </button>
  <button className="choice-button">
    NPC와 대화하기
  </button>
</div>
```

### 4. InfoPanel (정보 패널 - 토글로 숨김)
```tsx
// 정보는 토글 메뉴로 숨겨두고 필요시에만 표시
<div className="info-panel" style={{ display: isInfoOpen ? 'block' : 'none' }}>
  {/* 현재 위치 정보 */}
  <div className="location-info">
    <div className="location-name">마을 광장</div>
    <div className="location-description">
      마을의 중심부입니다. 많은 사람들이 오고 갑니다.
    </div>
  </div>
  
  {/* 인벤토리 */}
  <div className="inventory">
    <h3>인벤토리</h3>
    {/* 백엔드에서 조회한 아이템 목록 */}
  </div>
  
  {/* 현재 시간 */}
  <div className="time-info">
    <h3>시간</h3>
    <div>Day 1, 14:30</div>
  </div>
  
  {/* 저널/히스토리 */}
  <div className="journal">
    <h3>저널</h3>
    {/* 지금까지의 대화/이벤트 기록 */}
  </div>
</div>
```

**핵심**: 
- **메인 화면은 깔끔하게** 유지
- 정보는 **토글 버튼으로 접근**
- 사용자가 **원할 때만** 정보 확인

---

## 🔄 게임플레이 플로우

### 1. 게임 시작
```
1. 프론트엔드: POST /api/gameplay/start
   ↓
2. 백엔드: GameEngine.start_game()
   - 세션 생성
   - 플레이어 생성
   - 시작 셀 설정
   ↓
3. 프론트엔드: GET /api/gameplay/current-state
   - 현재 셀 정보
   - 셀 내 엔티티 목록
   - 사용 가능한 액션
   ↓
4. UI 업데이트
   - LocationLayer: 현재 위치 표시
   - MessageLayer: 시작 메시지 표시
   - ChoiceLayer: 사용 가능한 액션 버튼 표시
```

### 2. 셀 이동
```
1. 플레이어: "상점으로 이동" 선택
   ↓
2. 프론트엔드: POST /api/gameplay/move
   { action: "move", target_cell_id: "CELL_SHOP_001" }
   ↓
3. 백엔드: PlayerController.move_player()
   - 셀 이동 처리
   - 이벤트 발행 (CELL_ENTERED)
   ↓
4. 백엔드: 현재 셀 정보 조회
   - 셀 설명
   - 셀 내 엔티티
   - 사용 가능한 액션
   ↓
5. 프론트엔드: UI 업데이트
   - MessageLayer: "상점에 도착했습니다."
   - LocationLayer: 상점 정보 표시
   - ChoiceLayer: 상점에서 가능한 액션 표시
```

### 3. NPC 대화
```
1. 플레이어: "NPC와 대화하기" 선택
   ↓
2. 프론트엔드: POST /api/gameplay/dialogue/start
   { npc_id: "NPC_MERCHANT_001" }
   ↓
3. 백엔드: PlayerController.start_dialogue()
   - 대화 시작
   - 이벤트 발행 (DIALOGUE_STARTED)
   ↓
4. 백엔드: 대화 컨텍스트 조회
   - NPC 인사말
   - 사용 가능한 주제
   ↓
5. 프론트엔드: UI 업데이트
   - MessageLayer: NPC 대화 표시
   - ChoiceLayer: 대화 주제 선택지 표시
```

### 4. NPC 자동 행동 (백그라운드)
```
1. GameEngine.game_loop() 실행 중
   ↓
2. NPCController.process_npc_routines()
   - NPC 스케줄 확인
   - 자동 행동 실행 (이동, 작업 등)
   ↓
3. 이벤트 발행 (NPC_ACTION)
   ↓
4. 프론트엔드: WebSocket 또는 Polling으로 이벤트 수신
   ↓
5. UI 업데이트 (선택적)
   - MessageLayer: "상점 주인이 물건을 정리하고 있습니다."
```

---

## 🎨 UI 스타일 (novel_game 참고)

### 색상 팔레트
```css
/* 라이트 테마 (부드럽고 세련된 느낌) */
--bg-primary: #fafafa;
--bg-secondary: #f8f9fa;
--bg-tertiary: #f0f7fa;
--text-primary: #000000;
--text-secondary: rgba(0, 0, 0, 0.6);
--accent: rgba(255, 255, 255, 0.25);
--accent-hover: rgba(255, 255, 255, 0.35);
--surface: rgba(255, 255, 255, 0.15);
--border: rgba(0, 0, 0, 0.1);
```

### 타이포그래피
```css
/* 부드러운 폰트 */
font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
font-size: 16px;
line-height: 1.6;
letter-spacing: 0.5px;
```

### 애니메이션
```css
/* 부드러운 전환 */
.transition-smooth {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 페이드 인 */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
```

---

## 🔌 백엔드 API 설계

### 게임플레이 API (`app/api/routes/gameplay.py`)

```python
from fastapi import APIRouter, Depends
from app.engine.game_engine import GameEngine
from app.gameplay.player_controller import PlayerController

router = APIRouter(prefix="/api/gameplay", tags=["gameplay"])

@router.post("/start")
async def start_game(player_template_id: str):
    """새 게임 시작"""
    session_id = await game_engine.start_game(player_template_id)
    return {"session_id": session_id}

@router.get("/current-state")
async def get_current_state(session_id: str):
    """현재 게임 상태 조회"""
    # 현재 셀 정보
    # 셀 내 엔티티 목록
    # 사용 가능한 액션
    return {
        "current_cell": {...},
        "entities": [...],
        "available_actions": [...]
    }

@router.post("/move")
async def move_player(
    session_id: str,
    target_cell_id: str
):
    """플레이어 이동"""
    result = await player_controller.move_player(
        session_id, target_cell_id
    )
    return result

@router.post("/dialogue/start")
async def start_dialogue(
    session_id: str,
    npc_id: str
):
    """대화 시작"""
    result = await player_controller.start_dialogue(
        session_id, npc_id
    )
    return result

@router.post("/action")
async def execute_action(
    session_id: str,
    action_type: str,
    target_id: Optional[str] = None
):
    """액션 실행"""
    result = await player_controller.interact_with_entity(
        session_id, target_id, action_type
    )
    return result
```

---

## 📊 데이터 흐름

### 현재 상태 조회
```
프론트엔드 → GET /api/gameplay/current-state
  ↓
백엔드: GameEngine.get_current_state()
  ↓
Manager 클래스들 호출
  - CellManager.get_cell()
  - EntityManager.get_entities_in_cell()
  - ActionHandler.get_available_actions()
  ↓
응답: JSON
{
  "current_cell": {
    "cell_id": "CELL_SHOP_001",
    "name": "상점",
    "description": "다양한 물건을 판매하는 상점입니다."
  },
  "entities": [
    {
      "entity_id": "NPC_MERCHANT_001",
      "name": "상점 주인",
      "type": "npc"
    }
  ],
  "available_actions": [
    {"type": "move", "target": "CELL_TAVERN_001", "label": "여관으로 이동"},
    {"type": "dialogue", "target": "NPC_MERCHANT_001", "label": "상점 주인과 대화"},
    {"type": "investigate", "target": "CELL_SHOP_001", "label": "상점 조사"}
  ]
}
```

---

## 🎯 구현 계획

### Phase 1: 프론트엔드 기본 구조
1. Vite + React + TypeScript 프로젝트 생성
2. Tailwind CSS 설정
3. 기본 레이아웃 (GameView, MessageLayer, ChoiceLayer)
4. API 서비스 (gameApi.ts)

### Phase 2: 백엔드 API
1. `app/api/routes/gameplay.py` 생성
2. GameEngine과 PlayerController 연동
3. API 스키마 정의

### Phase 3: 게임플레이 통합
1. 셀 이동 기능
2. NPC 대화 기능
3. 액션 실행 기능

### Phase 4: UI 개선
1. 애니메이션 추가
2. 히스토리 패널
3. 상태 패널

---

## 💡 핵심 아이디어

### "소설책을 읽는 느낌" - 미니멀 UI 철학

#### 1. 복잡함을 숨기기
- **백엔드는 조용히**: 복잡한 쿼리와 로직은 사용자가 느끼지 못하게
- **데이터는 텍스트로**: 복잡한 데이터 구조를 자연스러운 서술문으로 변환
- **선택지만 보임**: 사용자는 간단한 버튼만 클릭

#### 2. 미니멀 디자인
- **메인 화면**: 텍스트 + 선택지 버튼만 (소설책처럼)
- **정보는 숨김**: inventory, 시간, 저널은 토글 메뉴로
- **불필요한 UI 제거**: 복잡한 패널, 상태 표시 등 최소화

#### 3. 텍스트 어드벤처 형식
- **서술 중심**: "당신은 마을 광장에 도착했습니다."
- **선택지 기반**: 버튼으로 액션 선택
- **대화 시스템**: NPC와의 대화를 텍스트로 표시

#### 4. 백엔드 쿼리 기반 (사용자는 모름)
- **실시간 데이터**: 모든 정보는 runtime_data에서 조회
- **동적 콘텐츠**: 셀, 엔티티, 액션이 모두 동적으로 생성
- **이벤트 기반**: NPC 행동은 백그라운드에서 처리
- **자연스러운 변환**: 쿼리 결과를 소설책의 서술문처럼 변환

#### 5. 부드럽고 세련된 UI
- **novel_game 스타일**: 라이트 테마 (하얀색 배경), 부드러운 애니메이션
- **레이어 구조**: 각 요소를 레이어로 분리
- **반응형**: 다양한 화면 크기 지원

---

## ✅ 결론

### 제안하는 구조
1. **프론트엔드**: React + TypeScript + Tailwind CSS (novel_game 스타일)
2. **백엔드 API**: FastAPI 기반 게임플레이 API
3. **게임 엔진**: GameEngine + PlayerController + EventBus
4. **데이터**: Manager 클래스들을 통한 runtime 데이터 조회

### 핵심 원칙: "소설책을 읽는 느낌"

#### UI 철학
- **미니멀**: 메인 화면은 텍스트와 선택지만
- **복잡함 숨기기**: 백엔드 로직은 사용자가 느끼지 못하게
- **정보 접근**: inventory, 시간, 저널은 토글 메뉴로
- **자연스러운 변환**: 데이터를 소설책의 서술문처럼 표시

#### 기술 원칙
- **UI는 표시만**: 게임 로직은 백엔드
- **모든 게임 상태는 백엔드에서 관리**
- **프론트엔드는 API 호출로 상태 조회 및 업데이트**
- **이벤트 기반으로 실시간 업데이트** (선택적)

#### 사용자 경험
- **소설책을 읽는 것처럼**: 텍스트에 집중
- **간단한 선택지만**: 복잡한 UI 없이 버튼만 클릭
- **필요할 때만 정보 확인**: 토글 메뉴로 접근
- **부드러운 전환**: 애니메이션으로 자연스러운 흐름

