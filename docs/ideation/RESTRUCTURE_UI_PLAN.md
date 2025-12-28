# UI 폴더 재구조화 계획

**작성 일자**: 2025-12-28  
**최신화 날짜**: 2025-12-28

## 🎯 목표

1. `app/world_editor/` → `app/ui/`로 이름 변경
2. 기존 PyQt5 코드 제거 (`app/ui/*.py`)
3. 프론트엔드에 `components/`, `screens/` 디렉토리 구조 추가
4. Editor 모드와 Game 모드 통합

---

## 📁 새로운 구조

```
app/ui/
├── frontend/                        # React 프론트엔드
│   ├── src/
│   │   ├── App.tsx                 # 모드 전환 (Editor/Game)
│   │   ├── main.tsx                # 엔트리 포인트
│   │   ├── index.css               # 전역 스타일
│   │   │
│   │   ├── modes/                  # 모드별 메인 컴포넌트
│   │   │   ├── EditorMode.tsx      # Editor 모드
│   │   │   └── GameMode.tsx        # Game 모드
│   │   │
│   │   ├── components/              # 재사용 가능한 컴포넌트
│   │   │   ├── editor/             # Editor 전용 컴포넌트
│   │   │   │   ├── MapCanvas.tsx
│   │   │   │   ├── PinEditor.tsx
│   │   │   │   ├── EntityExplorer.tsx
│   │   │   │   └── ...
│   │   │   ├── game/               # Game 전용 컴포넌트
│   │   │   │   ├── MessageLayer.tsx
│   │   │   │   ├── ChoiceLayer.tsx
│   │   │   │   ├── InfoPanel.tsx
│   │   │   │   └── ...
│   │   │   └── common/             # 공통 컴포넌트
│   │   │       ├── Modal.tsx
│   │   │       ├── Button.tsx
│   │   │       └── ...
│   │   │
│   │   ├── screens/                # 화면 컴포넌트 (전체 화면)
│   │   │   ├── editor/             # Editor 화면
│   │   │   │   ├── MapScreen.tsx
│   │   │   │   ├── EntityScreen.tsx
│   │   │   │   └── ...
│   │   │   └── game/               # Game 화면
│   │   │       ├── GameScreen.tsx
│   │   │       ├── InventoryScreen.tsx
│   │   │       ├── JournalScreen.tsx
│   │   │       └── ...
│   │   │
│   │   ├── services/                # API 서비스
│   │   │   ├── editorApi.ts        # Editor API
│   │   │   └── gameApi.ts          # Gameplay API
│   │   │
│   │   ├── store/                   # 상태 관리 (Zustand)
│   │   │   ├── editorStore.ts
│   │   │   └── gameStore.ts
│   │   │
│   │   ├── hooks/                   # 커스텀 훅
│   │   │   ├── useEditor.ts
│   │   │   └── useGame.ts
│   │   │
│   │   └── types/                   # 타입 정의
│   │       ├── editor.ts
│   │       └── game.ts
│   │
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
└── backend/                         # FastAPI 백엔드
    ├── main.py                      # FastAPI 앱
    └── run_server.py                # 서버 실행 스크립트
```

**참고**: `backend/`는 `app/api/`로 분리할 수도 있음 (기존 구조 유지)

---

## 🔄 마이그레이션 계획

### Phase 1: 폴더 구조 변경

#### 1.1 기존 PyQt5 코드 제거
```bash
# app/ui/ 내의 모든 .py 파일 제거 (PyQt5 기반)
# - app/ui/dashboard.py
# - app/ui/main_window.py
# - app/ui/screens/*.py
# - app/ui/components/*.py
```

#### 1.2 world_editor → ui로 이동
```bash
# world_editor 폴더를 ui로 이름 변경
mv app/world_editor app/ui
```

#### 1.3 디렉토리 구조 생성
```bash
# 프론트엔드 구조 생성
mkdir -p app/ui/frontend/src/{modes,components/{editor,game,common},screens/{editor,game},services,store,hooks,types}
```

---

### Phase 2: 기존 Editor 코드 재구조화

#### 2.1 Editor 컴포넌트 이동
```
기존: app/ui/frontend/src/components/
  ├── MapCanvas.tsx
  ├── PinEditor.tsx
  └── ...

새로운: app/ui/frontend/src/components/editor/
  ├── MapCanvas.tsx
  ├── PinEditor.tsx
  └── ...
```

#### 2.2 Editor 화면 생성
```tsx
// app/ui/frontend/src/screens/editor/MapScreen.tsx
// 기존 App.tsx의 Editor 부분을 화면으로 분리
```

---

### Phase 3: Game 모드 추가

#### 3.1 Game 컴포넌트 생성
```tsx
// app/ui/frontend/src/components/game/
// - MessageLayer.tsx
// - ChoiceLayer.tsx
// - InfoPanel.tsx
```

#### 3.2 Game 화면 생성
```tsx
// app/ui/frontend/src/screens/game/
// - GameScreen.tsx
// - InventoryScreen.tsx
// - JournalScreen.tsx
```

---

### Phase 4: 모드 전환 구현

#### 4.1 App.tsx 수정
```tsx
// app/ui/frontend/src/App.tsx
import { EditorMode } from './modes/EditorMode';
import { GameMode } from './modes/GameMode';

function App() {
  const [mode, setMode] = useState<'editor' | 'game'>('editor');
  // ...
}
```

---

## 📋 파일 이동 매핑

### Editor 컴포넌트
```
기존 → 새로운
app/ui/frontend/src/components/MapCanvas.tsx
  → app/ui/frontend/src/components/editor/MapCanvas.tsx

app/ui/frontend/src/components/PinEditor.tsx
  → app/ui/frontend/src/components/editor/PinEditor.tsx

app/ui/frontend/src/components/EntityExplorer.tsx
  → app/ui/frontend/src/components/editor/EntityExplorer.tsx
```

### Editor 화면
```
기존 App.tsx의 Editor 부분
  → app/ui/frontend/src/screens/editor/MapScreen.tsx
```

### Game 컴포넌트 (신규)
```
app/ui/frontend/src/components/game/MessageLayer.tsx
app/ui/frontend/src/components/game/ChoiceLayer.tsx
app/ui/frontend/src/components/game/InfoPanel.tsx
```

### Game 화면 (신규)
```
app/ui/frontend/src/screens/game/GameScreen.tsx
app/ui/frontend/src/screens/game/InventoryScreen.tsx
app/ui/frontend/src/screens/game/JournalScreen.tsx
```

---

## 🗑️ 제거할 파일

### PyQt5 기반 파일 (제거)
```
app/ui/dashboard.py
app/ui/main_window.py
app/ui/screens/inventory_screen.py
app/ui/screens/map_screen.py
app/ui/screens/dialogue_screen.py
app/ui/components/*.py (PyQt5 기반)
```

**참고**: 이 파일들은 PyQt5 기반이므로 React로 재구현 필요

---

## ✅ 체크리스트

### Phase 1: 구조 변경
- [ ] `app/world_editor/` → `app/ui/` 이름 변경
- [ ] 기존 PyQt5 파일 제거
- [ ] 디렉토리 구조 생성 (`components/`, `screens/`)

### Phase 2: Editor 재구조화
- [ ] Editor 컴포넌트를 `components/editor/`로 이동
- [ ] Editor 화면을 `screens/editor/`로 분리
- [ ] EditorMode.tsx 생성

### Phase 3: Game 모드 추가
- [ ] Game 컴포넌트 생성 (`components/game/`)
- [ ] Game 화면 생성 (`screens/game/`)
- [ ] GameMode.tsx 생성

### Phase 4: 통합
- [ ] App.tsx에 모드 전환 추가
- [ ] import 경로 수정
- [ ] 테스트 및 확인

---

## 🔧 기술적 고려사항

### Import 경로
```tsx
// 기존
import { MapCanvas } from '../components/MapCanvas';

// 새로운
import { MapCanvas } from '../components/editor/MapCanvas';
```

### 코드 스플리팅
```tsx
// 모드별로 코드 스플리팅 (선택적)
const EditorMode = lazy(() => import('./modes/EditorMode'));
const GameMode = lazy(() => import('./modes/GameMode'));
```

### 공통 컴포넌트
```tsx
// components/common/ - Editor와 Game 모두 사용
import { Modal } from '../components/common/Modal';
import { Button } from '../components/common/Button';
```

---

## 📊 예상 소요 시간

- **Phase 1**: 1일 (폴더 구조 변경)
- **Phase 2**: 2일 (Editor 재구조화)
- **Phase 3**: 3일 (Game 모드 추가)
- **Phase 4**: 1일 (통합 및 테스트)

**총 예상 시간**: 1주

---

## ✅ 결론

**새로운 구조**:
- `app/ui/` - 통합 UI 폴더
- `frontend/` - React 프론트엔드
- `components/` - 재사용 가능한 컴포넌트
- `screens/` - 전체 화면 컴포넌트
- `backend/` - FastAPI 백엔드

**제거**:
- PyQt5 기반 코드 (`app/ui/*.py`)

**통합**:
- Editor 모드와 Game 모드를 하나의 앱으로 통합

