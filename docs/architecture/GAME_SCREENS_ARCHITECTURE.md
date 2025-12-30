# 게임 화면 아키텍처 기획서

**작성일**: 2025-12-29  
**목적**: 텍스트 어드벤처 게임에 필요한 화면 구조 및 네비게이션 기획  
**스타일**: 미니멀한 소설 읽기 느낌 유지

---

## 목차

1. [현재 구조 분석](#1-현재-구조-분석)
2. [화면 계층 구조](#2-화면-계층-구조)
3. [필요한 화면 목록](#3-필요한-화면-목록)
4. [화면별 상세 기획](#4-화면별-상세-기획)
5. [네비게이션 구조](#5-네비게이션-구조)
6. [구현 우선순위](#6-구현-우선순위)

---

## 1. 현재 구조 분석

### 1.1 현재 파일 구조

```
screens/game/
  └── GameScreen.tsx (11줄) - 단순히 GameView를 렌더링

components/game/
  ├── GameView.tsx (747줄) - 모든 게임 로직 집중 ⚠️
  ├── IntroScreen.tsx - 인트로 화면
  ├── InfoPanel.tsx - 정보 패널 (모달)
  ├── SaveLoadMenu.tsx - 저장/로드 메뉴 (모달)
  └── ... (레이어 컴포넌트들)
```

### 1.2 문제점

1. **GameView.tsx가 너무 큼** (747줄)
   - 게임 초기화 로직
   - 액션 처리 로직
   - 상태 관리
   - UI 렌더링
   - 모든 것이 한 파일에 집중

2. **화면과 모달의 구분이 불명확**
   - InfoPanel은 모달이지만 실제로는 별도 화면이어야 할 수도 있음
   - SaveLoadMenu는 모달이지만 전체 화면으로 보여줄 수도 있음

3. **화면 전환 로직이 없음**
   - 모든 것이 GameView 내부에서 상태로 관리됨
   - 화면 간 전환이 명확하지 않음

---

## 2. 화면 계층 구조

### 2.1 화면 분류

#### **Full Screen (전체 화면)**
- 사용자가 게임 플레이를 중단하고 전환하는 화면
- 예: 인벤토리, 캐릭터 정보, 저널, 지도, 설정

#### **Overlay Screen (오버레이 화면)**
- 게임 플레이를 계속하면서 정보를 확인하는 화면
- 예: 인벤토리 (빠른 확인), HUD

#### **Modal (모달)**
- 단순한 확인/선택을 위한 작은 팝업
- 예: 아이템 상세 정보, 확인 다이얼로그

### 2.2 제안하는 구조

```
screens/game/
  ├── IntroScreen.tsx          - 인트로 화면 (전체 화면)
  ├── MainGameScreen.tsx       - 메인 게임 플레이 (전체 화면)
  ├── InventoryScreen.tsx      - 인벤토리 화면 (전체 화면)
  ├── CharacterScreen.tsx      - 캐릭터 정보 화면 (전체 화면)
  ├── JournalScreen.tsx        - 저널 화면 (전체 화면)
  ├── MapScreen.tsx            - 지도 화면 (전체 화면)
  ├── SettingsScreen.tsx       - 설정 화면 (전체 화면)
  ├── SaveLoadScreen.tsx       - 저장/로드 화면 (전체 화면)
  └── GameOverScreen.tsx       - 게임 오버/엔딩 화면 (전체 화면)

components/game/
  ├── GameView.tsx             - 게임 뷰 (MainGameScreen에서 사용)
  ├── InventoryPanel.tsx       - 인벤토리 패널 (오버레이, 빠른 확인용)
  ├── CharacterPanel.tsx       - 캐릭터 패널 (오버레이, HUD)
  └── ... (기존 레이어 컴포넌트들)

modals/
  ├── ItemDetailModal.tsx      - 아이템 상세 정보 모달
  ├── ConfirmModal.tsx         - 확인 다이얼로그
  └── ... (기타 모달들)
```

---

## 3. 필요한 화면 목록

### 3.1 필수 화면 (우선순위 높음)

| 화면 | 타입 | 설명 | 현재 상태 |
|------|------|------|----------|
| **IntroScreen** | Full Screen | 게임 시작 인트로 | ✅ 구현됨 |
| **MainGameScreen** | Full Screen | 메인 게임 플레이 | ⚠️ GameView로 구현됨 |
| **InventoryScreen** | Full Screen | 인벤토리 관리 (아이템 사용, 장착, 조합) | ❌ 없음 (InfoPanel에 일부) |
| **CharacterScreen** | Full Screen | 캐릭터 정보 (스탯, 상태, 장비) | ❌ 없음 |
| **JournalScreen** | Full Screen | 저널 (이벤트 기록, 퀘스트) | ❌ 없음 (InfoPanel에 일부) |
| **MapScreen** | Full Screen | 지도 (현재 위치, 연결된 셀) | ❌ 없음 (InfoPanel에 일부) |
| **SaveLoadScreen** | Full Screen | 저장/로드 | ⚠️ 모달로 구현됨 |

### 3.2 선택 화면 (우선순위 중간)

| 화면 | 타입 | 설명 | 현재 상태 |
|------|------|------|----------|
| **SettingsScreen** | Full Screen | 게임 설정 | ❌ 없음 |
| **GameOverScreen** | Full Screen | 게임 오버/엔딩 | ❌ 없음 |
| **QuestScreen** | Full Screen | 퀘스트 목록 | ❌ 없음 |

### 3.3 오버레이 패널 (빠른 확인용)

| 패널 | 타입 | 설명 | 현재 상태 |
|------|------|------|----------|
| **InventoryPanel** | Overlay | 인벤토리 빠른 확인 | ⚠️ InfoPanel에 일부 |
| **CharacterPanel** | Overlay | 캐릭터 상태 HUD | ❌ 없음 |
| **LocationPanel** | Overlay | 현재 위치 정보 | ✅ LocationLayer로 구현됨 |

---

## 4. 화면별 상세 기획

### 4.1 IntroScreen (인트로 화면)

**목적**: 게임 시작 시 스토리 소개

**구현 상태**: ✅ 완료

**기능**:
- 스토리 텍스트 표시
- 자동 진행 또는 클릭으로 넘어가기
- 게임 시작 버튼

**네비게이션**:
- 완료 시 → `MainGameScreen`

---

### 4.2 MainGameScreen (메인 게임 화면)

**목적**: 실제 게임 플레이

**구현 상태**: ⚠️ GameView로 구현됨 (리팩토링 필요)

**기능**:
- 게임 월드 렌더링
- 메시지/대화 표시
- 선택지 표시
- 오브젝트/엔티티 상호작용
- HUD 표시 (위치, 시간, HP/MP)

**네비게이션**:
- `I` 키 → `InventoryScreen`
- `C` 키 → `CharacterScreen`
- `J` 키 → `JournalScreen`
- `M` 키 → `MapScreen`
- `Esc` → 설정 메뉴 또는 게임 일시정지

**리팩토링 계획**:
- `GameView.tsx`를 `components/game/GameView.tsx`로 유지 (렌더링만)
- 게임 로직을 hooks로 분리:
  - `useGameInitialization.ts`
  - `useGameActions.ts`
  - `useGameKeyboard.ts`
- `MainGameScreen.tsx`에서 hooks 사용

---

### 4.3 InventoryScreen (인벤토리 화면)

**목적**: 아이템 관리

**구현 상태**: ❌ 없음 (InfoPanel에 기본 리스트만)

**기능**:
- 아이템 목록 표시 (그리드 또는 리스트)
- 아이템 상세 정보 (클릭 시 모달)
- 아이템 사용/장착/버리기
- 아이템 조합
- 장착 슬롯 표시 (무기, 방어구 등)
- 필터/정렬 기능

**UI 구성**:
```
┌─────────────────────────────────────┐
│ 인벤토리                    [닫기] │
├─────────────────────────────────────┤
│ [전체] [장비] [소비] [기타]         │
├─────────────────────────────────────┤
│                                     │
│  [아이템1]  [아이템2]  [아이템3]   │
│  [아이템4]  [아이템5]  [아이템6]   │
│                                     │
│  장착 슬롯:                         │
│  [무기] [방어구] [악세서리]         │
│                                     │
└─────────────────────────────────────┘
```

**네비게이션**:
- `Esc` 또는 닫기 버튼 → `MainGameScreen`
- 아이템 클릭 → `ItemDetailModal`

---

### 4.4 CharacterScreen (캐릭터 정보 화면)

**목적**: 캐릭터 상태 및 능력치 확인

**구현 상태**: ❌ 없음

**기능**:
- 기본 정보 (이름, 레벨, 경험치)
- 스탯 표시 (HP/MP, 힘, 민첩, 지능 등)
- 장착 중인 장비
- 현재 상태 효과 (버프/디버프)
- 스킬 목록 (선택 사항)

**UI 구성**:
```
┌─────────────────────────────────────┐
│ 캐릭터 정보                [닫기]   │
├─────────────────────────────────────┤
│ [캐릭터 이미지]                     │
│                                     │
│ 이름: 플레이어                      │
│ 레벨: 1                             │
│                                     │
│ HP: ████████░░ 80/100              │
│ MP: ██████░░░░ 60/100              │
│                                     │
│ 능력치:                             │
│ 힘: 10  민첩: 8  지능: 12          │
│                                     │
│ 장착:                               │
│ 무기: [검]                          │
│ 방어구: [갑옷]                      │
│                                     │
│ 상태 효과:                          │
│ [힘 +2] [독 -5]                    │
└─────────────────────────────────────┘
```

**네비게이션**:
- `Esc` 또는 닫기 버튼 → `MainGameScreen`

---

### 4.5 JournalScreen (저널 화면)

**목적**: 게임 이벤트 기록 및 퀘스트 확인

**구현 상태**: ❌ 없음 (InfoPanel에 기본 리스트만)

**기능**:
- 이벤트 기록 목록 (시간순)
- 카테고리별 필터 (이벤트, 대화, 발견 등)
- 검색 기능
- 퀘스트 목록 (진행 중, 완료)
- 상세 정보 보기

**UI 구성**:
```
┌─────────────────────────────────────┐
│ 저널                        [닫기]   │
├─────────────────────────────────────┤
│ [전체] [이벤트] [대화] [퀘스트]      │
│ [검색...]                            │
├─────────────────────────────────────┤
│                                     │
│ 2025-12-29 10:30                   │
│ 여관에 도착했습니다.                │
│                                     │
│ 2025-12-29 10:25                   │
│ 레크로스타에 도착했습니다.           │
│                                     │
│ 퀘스트:                             │
│ [ ] 여관 방 찾기                    │
│ [✓] 레크로스타 도착                 │
│                                     │
└─────────────────────────────────────┘
```

**네비게이션**:
- `Esc` 또는 닫기 버튼 → `MainGameScreen`

---

### 4.6 MapScreen (지도 화면)

**목적**: 현재 위치 및 월드 탐색

**구현 상태**: ❌ 없음 (InfoPanel에 텍스트만)

**기능**:
- 현재 위치 표시
- 연결된 셀 표시
- 방문한 장소 표시
- 지도 확대/축소
- 장소 클릭으로 이동 (선택 사항)

**UI 구성**:
```
┌─────────────────────────────────────┐
│ 지도                        [닫기]   │
├─────────────────────────────────────┤
│ [확대] [축소] [전체보기]            │
├─────────────────────────────────────┤
│                                     │
│         [여관]                      │
│           │                         │
│      [거리]                         │
│           │                         │
│      [상점]                         │
│                                     │
│ 현재 위치: 여관 내 방               │
│                                     │
└─────────────────────────────────────┘
```

**네비게이션**:
- `Esc` 또는 닫기 버튼 → `MainGameScreen`

---

### 4.7 SaveLoadScreen (저장/로드 화면)

**목적**: 게임 진행 상황 저장/불러오기

**구현 상태**: ⚠️ 모달로 구현됨 (전체 화면으로 변경 권장)

**기능**:
- 저장 슬롯 목록
- 저장 슬롯 정보 (날짜, 시간, 위치, 썸네일)
- 저장하기
- 불러오기
- 삭제하기

**UI 구성**:
```
┌─────────────────────────────────────┐
│ 저장/불러오기              [닫기]   │
├─────────────────────────────────────┤
│ [저장] [불러오기]                   │
├─────────────────────────────────────┤
│                                     │
│ 슬롯 1: 2025-12-29 10:30           │
│ 여관 내 방                          │
│ [불러오기] [삭제]                   │
│                                     │
│ 슬롯 2: (비어있음)                  │
│ [저장]                              │
│                                     │
└─────────────────────────────────────┘
```

**네비게이션**:
- `Esc` 또는 닫기 버튼 → `MainGameScreen`

---

### 4.8 SettingsScreen (설정 화면)

**목적**: 게임 설정 변경

**구현 상태**: ❌ 없음

**기능**:
- 음향 설정 (볼륨, 효과음)
- 화면 설정 (해상도, 전체화면)
- 게임 설정 (자동 진행 속도, 텍스트 속도)
- 키보드 단축키 설정
- 언어 설정

**네비게이션**:
- `Esc` 또는 닫기 버튼 → `MainGameScreen`

---

### 4.9 GameOverScreen (게임 오버/엔딩 화면)

**목적**: 게임 종료 시 표시

**구현 상태**: ❌ 없음

**기능**:
- 게임 오버 메시지
- 엔딩 메시지
- 통계 표시 (플레이 시간, 방문한 장소 등)
- 다시 시작 / 메인 메뉴로

**네비게이션**:
- 다시 시작 → `IntroScreen` 또는 `MainGameScreen`
- 메인 메뉴 → (추후 구현)

---

## 5. 네비게이션 구조

### 5.1 화면 전환 흐름

```
IntroScreen
    ↓
MainGameScreen (메인 게임 플레이)
    ├─ I 키 → InventoryScreen
    ├─ C 키 → CharacterScreen
    ├─ J 키 → JournalScreen
    ├─ M 키 → MapScreen
    ├─ Esc → SettingsScreen (또는 일시정지 메뉴)
    └─ Ctrl+S → SaveLoadScreen
```

### 5.2 화면 전환 관리

**제안하는 구조**:

```typescript
// screens/game/GameScreen.tsx
type GameScreenType = 
  | 'intro'
  | 'main'
  | 'inventory'
  | 'character'
  | 'journal'
  | 'map'
  | 'saveLoad'
  | 'settings'
  | 'gameOver';

const GameScreen: React.FC = () => {
  const [currentScreen, setCurrentScreen] = useState<GameScreenType>('intro');
  
  return (
    <>
      {currentScreen === 'intro' && <IntroScreen onComplete={() => setCurrentScreen('main')} />}
      {currentScreen === 'main' && <MainGameScreen onNavigate={setCurrentScreen} />}
      {currentScreen === 'inventory' && <InventoryScreen onClose={() => setCurrentScreen('main')} />}
      {currentScreen === 'character' && <CharacterScreen onClose={() => setCurrentScreen('main')} />}
      {currentScreen === 'journal' && <JournalScreen onClose={() => setCurrentScreen('main')} />}
      {currentScreen === 'map' && <MapScreen onClose={() => setCurrentScreen('main')} />}
      {currentScreen === 'saveLoad' && <SaveLoadScreen onClose={() => setCurrentScreen('main')} />}
      {currentScreen === 'settings' && <SettingsScreen onClose={() => setCurrentScreen('main')} />}
      {currentScreen === 'gameOver' && <GameOverScreen onRestart={() => setCurrentScreen('intro')} />}
    </>
  );
};
```

### 5.3 키보드 단축키

| 키 | 동작 | 화면 |
|----|------|------|
| `I` | 인벤토리 열기 | InventoryScreen |
| `C` | 캐릭터 정보 열기 | CharacterScreen |
| `J` | 저널 열기 | JournalScreen |
| `M` | 지도 열기 | MapScreen |
| `Esc` | 현재 화면 닫기 / 설정 열기 | MainGameScreen / SettingsScreen |
| `Ctrl+S` | 저장/로드 열기 | SaveLoadScreen |

---

## 6. 구현 우선순위

### Phase 1: 필수 화면 (즉시 구현)

1. **MainGameScreen 리팩토링**
   - GameView 로직을 hooks로 분리
   - 화면 전환 로직 추가

2. **InventoryScreen**
   - 기본 아이템 목록
   - 아이템 사용/장착/버리기

3. **CharacterScreen**
   - 기본 스탯 표시
   - HP/MP 표시

4. **SaveLoadScreen**
   - 모달에서 전체 화면으로 변경
   - 저장/로드 기능

### Phase 2: 개선 화면 (1주 내)

5. **JournalScreen**
   - 이벤트 기록 표시
   - 검색/필터 기능

6. **MapScreen**
   - 지도 시각화
   - 연결된 셀 표시

### Phase 3: 추가 기능 (2주 내)

7. **SettingsScreen**
   - 기본 설정 변경

8. **GameOverScreen**
   - 게임 오버 처리

---

## 7. 파일 구조 제안

```
screens/game/
  ├── GameScreen.tsx              - 화면 라우터 (상태 관리)
  ├── IntroScreen.tsx             - 인트로 화면
  ├── MainGameScreen.tsx          - 메인 게임 화면
  ├── InventoryScreen.tsx         - 인벤토리 화면
  ├── CharacterScreen.tsx         - 캐릭터 정보 화면
  ├── JournalScreen.tsx           - 저널 화면
  ├── MapScreen.tsx               - 지도 화면
  ├── SaveLoadScreen.tsx          - 저장/로드 화면
  ├── SettingsScreen.tsx         - 설정 화면
  └── GameOverScreen.tsx          - 게임 오버 화면

components/game/
  ├── GameView.tsx               - 게임 뷰 (렌더링만)
  ├── InventoryPanel.tsx         - 인벤토리 패널 (오버레이)
  ├── CharacterPanel.tsx          - 캐릭터 패널 (HUD)
  └── ... (기존 레이어 컴포넌트들)

hooks/game/
  ├── useGameInitialization.ts   - 게임 초기화 로직
  ├── useGameActions.ts          - 액션 처리 로직
  ├── useGameKeyboard.ts         - 키보드 단축키 로직
  ├── useGameNavigation.ts       - 화면 전환 로직
  └── useGameState.ts            - 게임 상태 관리

modals/
  ├── ItemDetailModal.tsx        - 아이템 상세 정보
  ├── ConfirmModal.tsx           - 확인 다이얼로그
  └── ... (기타 모달들)
```

---

## 8. 다음 단계

1. **GameScreen.tsx 리팩토링**
   - 화면 전환 로직 추가
   - MainGameScreen 분리

2. **MainGameScreen 구현**
   - GameView 로직을 hooks로 분리
   - 키보드 단축키로 화면 전환

3. **InventoryScreen 구현**
   - 기본 UI 구성
   - 아이템 목록 표시
   - 아이템 사용/장착 기능

4. **CharacterScreen 구현**
   - 스탯 표시
   - HP/MP 표시

이 기획서를 바탕으로 단계적으로 구현을 진행하시면 됩니다.


