# 프론트엔드 화면 기획서

**작성일**: 2025-12-28  
**목적**: RPG 게임에 필요한 기본 화면들의 UI/UX 기획  
**스타일**: 미니멀한 소설 읽기 느낌 유지

---

## 목차

1. [현재 구현 상태](#1-현재-구현-상태)
2. [필요한 화면 목록](#2-필요한-화면-목록)
3. [화면별 상세 기획](#3-화면별-상세-기획)
4. [API 연동 계획](#4-api-연동-계획)
5. [디자인 가이드라인](#5-디자인-가이드라인)

---

## 1. 현재 구현 상태

### 1.1 구현된 화면

| 화면 | 상태 | 비고 |
|------|------|------|
| **IntroScreen** | ✅ 완료 | 인트로 화면 |
| **GameView** | ✅ 완료 | 메인 게임 뷰 |
| **InfoPanel** | ⚠️ 부분 구현 | 탭 구조만 있고 내용 미완성 |
| **MessageLayer** | ✅ 완료 | 메시지 표시 |
| **ChoiceLayer** | ✅ 완료 | 선택지 표시 |
| **InteractionLayer** | ✅ 완료 | 상호작용 레이어 |
| **SaveLoadMenu** | ✅ 완료 | 저장/로드 메뉴 |

### 1.2 InfoPanel 현재 상태

- **인벤토리 탭**: 기본 리스트만 표시 (아이템 상세 정보, 사용, 장착 기능 없음)
- **지도 탭**: 현재 위치만 표시 (지도 시각화, 탐색 기능 없음)
- **저널 탭**: history 기반 표시 (DB 연동 없음, 검색/필터 기능 없음)
- **시간 탭**: 플레이 시간만 표시 (게임 내 시간, 날짜 표시 없음)

---

## 2. 필요한 화면 목록

### 2.1 우선순위 높음 (필수)

1. **인벤토리 화면** (개선)
   - 아이템 상세 정보
   - 아이템 사용/장착/버리기
   - 아이템 조합
   - 장비 슬롯 표시

2. **스탯 화면** (신규)
   - HP/MP 표시
   - 기본 능력치 (힘, 민첩, 지능 등)
   - 현재 상태 효과 (버프/디버프)

3. **스킬 화면** (신규)
   - 보유 스킬 목록
   - 스킬 상세 정보
   - 스킬 사용

4. **저널 화면** (개선)
   - DB 연동
   - 검색/필터 기능
   - 카테고리별 분류

5. **상자 인벤토리** (신규)
   - 오브젝트 contents 표시
   - 아이템 획득/놓기

### 2.2 우선순위 중간 (권장)

6. **마을 탐색/지도** (개선)
   - 지도 시각화
   - 연결된 셀 표시
   - 이동 경로 표시

7. **장비 화면** (신규)
   - 장착 중인 장비 표시
   - 장비 교체
   - 장비 상세 정보

8. **게임 내 시간** (개선)
   - 가상 날짜/시간 표시
   - 시간대 표시 (아침, 점심, 저녁 등)

### 2.3 우선순위 낮음 (선택)

9. **퀘스트 화면** (신규)
   - 진행 중인 퀘스트
   - 완료된 퀘스트

10. **아이템 상세 모달** (신규)
    - 아이템 상세 정보
    - 효과 설명

---

## 3. 화면별 상세 기획

### 3.1 인벤토리 화면 (개선)

#### 현재 문제점
- 아이템 상세 정보 없음
- 아이템 사용/장착 기능 없음
- 장비 슬롯 표시 없음
- 아이템 분류 없음

#### 개선 계획

**레이아웃**:
```
┌─────────────────────────────────┐
│ 인벤토리              [닫기] ✕  │
├─────────────────────────────────┤
│ [전체] [아이템] [장비] [소비품] │ ← 탭
├─────────────────────────────────┤
│ 장착 중                          │
│ ┌─────┐ ┌─────┐ ┌─────┐        │
│ │무기 │ │방어구│ │악세│        │ ← 장비 슬롯 (미니멀)
│ │[검] │ │[갑옷]│ │[반지]│       │
│ └─────┘ └─────┘ └─────┘        │
├─────────────────────────────────┤
│ 보유 아이템 (12/50)              │
│ ┌─────────────────────────────┐ │
│ │ 회복 물약              x5   │ │
│ │ [사용] [상세]                │ │
│ └─────────────────────────────┘ │
│ ┌─────────────────────────────┐ │
│ │ 철검                    x1   │ │
│ │ [장착] [상세]               │ │
│ └─────────────────────────────┘ │
│ ...                              │
└─────────────────────────────────┘
```

**기능**:
- 아이템 카테고리별 필터링 (전체, 아이템, 장비, 소비품)
- 아이템 클릭 시 상세 정보 표시
- 아이템 사용/장착/버리기 버튼
- 장비 슬롯 표시 (무기, 방어구, 악세서리)
- 인벤토리 용량 표시 (현재/최대)

**API 연동**:
- `GET /api/gameplay/inventory/{session_id}` - 인벤토리 조회
- `POST /api/gameplay/interact` - 아이템 사용
- `POST /api/gameplay/combine` - 아이템 조합
- (신규 필요) `GET /api/gameplay/stats/{session_id}` - 스탯 조회 (장착 아이템 포함)

**디자인**:
- 미니멀한 리스트 스타일
- 흰색 배경, 검은색 텍스트
- 부드러운 애니메이션
- 호버 시 약간의 배경색 변화

---

### 3.2 스탯 화면 (신규)

#### 목적
플레이어의 현재 상태와 능력치를 한눈에 확인

#### 레이아웃
```
┌─────────────────────────────────┐
│ 스탯                  [닫기] ✕  │
├─────────────────────────────────┤
│ 상태                             │
│ HP: ████████░░ 80/100           │
│ MP: ██████░░░░ 50/80            │
├─────────────────────────────────┤
│ 기본 능력치                       │
│ 힘: 12    민첩: 10              │
│ 지능: 8   체력: 15              │
│ 지혜: 9   매력: 11              │
├─────────────────────────────────┤
│ 현재 효과                         │
│ [🔥 불타는 손] +5 힘 (5분 남음) │
│ [❄️ 냉기 저항] +10 냉기 저항    │
└─────────────────────────────────┘
```

**기능**:
- HP/MP 바 표시
- 기본 능력치 표시 (힘, 민첩, 지능, 체력, 지혜, 매력)
- 현재 적용 중인 효과 표시 (버프/디버프)
- 효과 상세 정보 (호버 시)

**API 연동**:
- (신규 필요) `GET /api/gameplay/stats/{session_id}` - 스탯 조회
  - `current_stats`: HP, MP, 기본 능력치
  - `active_effects`: 현재 적용 중인 효과 목록
  - `equipped_items`: 장착 중인 장비 (능력치 보너스 포함)

**데이터 구조**:
```typescript
interface PlayerStats {
  current_stats: {
    hp: number;
    max_hp: number;
    mp: number;
    max_mp: number;
    strength: number;
    dexterity: number;
    intelligence: number;
    constitution: number;
    wisdom: number;
    charisma: number;
  };
  active_effects: Array<{
    effect_id: string;
    name: string;
    icon?: string;
    description: string;
    duration?: number;
    remaining_time?: number;
  }>;
  equipped_items: {
    weapon?: EquipmentInfo;
    armor?: EquipmentInfo;
    accessories?: EquipmentInfo[];
  };
}
```

**디자인**:
- 깔끔한 숫자 표시
- 진행 바는 미니멀한 스타일
- 효과는 작은 아이콘과 함께 표시

---

### 3.3 스킬 화면 (신규)

#### 목적
보유 스킬 목록과 상세 정보 확인, 스킬 사용

#### 레이아웃
```
┌─────────────────────────────────┐
│ 스킬                  [닫기] ✕  │
├─────────────────────────────────┤
│ [전체] [전투] [마법] [생활]     │ ← 탭
├─────────────────────────────────┤
│ 보유 스킬 (5)                    │
│ ┌─────────────────────────────┐ │
│ │ [스킬 아이콘] 슬래시         │ │
│ │ MP: 10  쿨타임: 3초         │ │
│ │ 물리 공격 +50%              │ │
│ │ [사용] [상세]               │ │
│ └─────────────────────────────┘ │
│ ...                              │
└─────────────────────────────────┘
```

**기능**:
- 스킬 카테고리별 필터링 (전체, 전투, 마법, 생활)
- 스킬 상세 정보 표시
- 스킬 사용 (MP, 쿨타임 확인)
- 스킬 레벨/경험치 표시 (있는 경우)

**API 연동**:
- (신규 필요) `GET /api/gameplay/skills/{session_id}` - 보유 스킬 조회
- (신규 필요) `POST /api/gameplay/skills/use` - 스킬 사용

**데이터 구조**:
```typescript
interface Skill {
  skill_id: string;
  name: string;
  description: string;
  skill_type: 'combat' | 'magic' | 'craft' | 'other';
  mana_cost: number;
  cooldown: number;
  current_cooldown?: number;
  level?: number;
  experience?: number;
  properties: {
    damage?: number;
    range?: number;
    area_effect?: any;
    [key: string]: any;
  };
}
```

**디자인**:
- 카드 스타일 리스트
- 스킬 타입별 색상 구분 (미묘하게)
- 쿨타운 중인 스킬은 반투명 처리

---

### 3.4 저널 화면 (개선)

#### 현재 문제점
- DB 연동 없음 (history만 사용)
- 검색/필터 기능 없음
- 카테고리 분류 없음
- 시간순 정렬만 가능

#### 개선 계획

**레이아웃**:
```
┌─────────────────────────────────┐
│ 저널                  [닫기] ✕  │
├─────────────────────────────────┤
│ [검색...]  [전체] [퀘스트] [이벤트]│
├─────────────────────────────────┤
│ 항목 (15)                        │
│ ┌─────────────────────────────┐ │
│ │ 2025-01-15 14:30            │ │
│ │ [퀘스트] 마을의 부탁        │ │
│ │ "NPC가 도움을 요청했습니다" │ │
│ └─────────────────────────────┘ │
│ ...                              │
└─────────────────────────────────┘
```

**기능**:
- DB에서 저널 항목 조회
- 검색 기능 (텍스트 검색)
- 카테고리 필터 (전체, 퀘스트, 이벤트, 대화, 발견)
- 시간순 정렬 (최신순/과거순)
- 항목 클릭 시 상세 정보 표시

**API 연동**:
- (신규 필요) `GET /api/gameplay/journal/{session_id}` - 저널 조회
  - Query params: `category?`, `search?`, `sort?`
- (신규 필요) `POST /api/gameplay/journal` - 저널 항목 추가 (자동)

**데이터 구조**:
```typescript
interface JournalEntry {
  entry_id: string;
  timestamp: string;
  category: 'quest' | 'event' | 'dialogue' | 'discovery' | 'other';
  title: string;
  content: string;
  related_entity_id?: string;
  related_object_id?: string;
  tags?: string[];
}
```

**디자인**:
- 타임라인 스타일
- 카테고리별 아이콘
- 날짜/시간 표시
- 읽기 편한 텍스트 레이아웃

---

### 3.5 상자 인벤토리 (신규)

#### 목적
오브젝트(상자, 서랍 등)의 contents를 표시하고 아이템 획득/놓기

#### 레이아웃
```
┌─────────────────────────────────┐
│ 상자 인벤토리        [닫기] ✕  │
├─────────────────────────────────┤
│ [상자 이름]                      │
│ "오래된 나무 상자입니다"         │
├─────────────────────────────────┤
│ 내용물 (3)                       │
│ ┌─────────────────────────────┐ │
│ │ [아이콘] 회복 물약          │ │
│ │              x2  [획득]     │ │
│ └─────────────────────────────┘ │
│ ...                              │
├─────────────────────────────────┤
│ 내 인벤토리에서 놓기            │
│ [아이템 선택...]                │
└─────────────────────────────────┘
```

**기능**:
- 오브젝트의 contents 표시
- 아이템 획득 (pickup)
- 인벤토리에서 아이템 놓기 (place)
- 오브젝트 설명 표시

**API 연동**:
- `GET /api/gameplay/cell/{session_id}` - 셀 정보 조회 (오브젝트 contents 포함)
- `POST /api/gameplay/interact/object/pickup` - 아이템 획득
- (신규 필요) `POST /api/gameplay/interact/object/place` - 아이템 놓기

**디자인**:
- 모달 스타일
- 상단에 오브젝트 정보
- 하단에 내 인벤토리에서 선택하여 놓기 기능

---

### 3.6 마을 탐색/지도 (개선)

#### 현재 문제점
- 현재 위치만 텍스트로 표시
- 지도 시각화 없음
- 연결된 셀 정보 없음
- 이동 경로 표시 없음

#### 개선 계획

**레이아웃**:
```
┌─────────────────────────────────┐
│ 지도                  [닫기] ✕  │
├─────────────────────────────────┤
│ 현재 위치: 여관, 내 방          │
│ 지역: 리크로스타                │
├─────────────────────────────────┤
│ [지도 시각화 영역]              │
│                                 │
│     [방1] ── [방2]              │
│      │                          │
│    [복도] ── [계단]             │
│      │                          │
│    [로비]                       │
│      ● (현재 위치)              │
│                                 │
├─────────────────────────────────┤
│ 연결된 장소                      │
│ → 복도                          │
│ → 계단                          │
└─────────────────────────────────┘
```

**기능**:
- 현재 위치 표시
- 연결된 셀 목록 표시
- 셀 클릭 시 이동 (선택사항)
- 지역/위치 계층 구조 표시

**API 연동**:
- `GET /api/gameplay/cell/{session_id}` - 셀 정보 조회
  - `connected_cells`: 연결된 셀 목록
  - `location_name`, `region_name`: 위치 정보

**디자인**:
- 미니멀한 노드 그래프 스타일
- 현재 위치는 강조 표시
- 연결선은 얇은 선

---

### 3.7 장비 화면 (신규)

#### 목적
장착 중인 장비 확인 및 교체

#### 레이아웃
```
┌─────────────────────────────────┐
│ 장비                  [닫기] ✕  │
├─────────────────────────────────┤
│ 장착 슬롯                        │
│ ┌─────┐ ┌─────┐ ┌─────┐        │
│ │무기 │ │방어구│ │악세│        │
│ │[검] │ │[갑옷]│ │[반지]│       │
│ └─────┘ └─────┘ └─────┘        │
├─────────────────────────────────┤
│ 무기: 철검                       │
│ 공격력: +15                      │
│ 내구도: 80/100                   │
│ [해제] [상세]                    │
├─────────────────────────────────┤
│ 방어구: 가죽 갑옷                │
│ 방어력: +8                       │
│ 내구도: 60/80                    │
│ [해제] [상세]                    │
└─────────────────────────────────┘
```

**기능**:
- 장착 슬롯 표시 (무기, 방어구, 악세서리)
- 장비 상세 정보 표시
- 장비 해제
- 인벤토리에서 장비 장착 (연동)

**API 연동**:
- (신규 필요) `GET /api/gameplay/equipment/{session_id}` - 장착 장비 조회
- (신규 필요) `POST /api/gameplay/equipment/equip` - 장비 장착
- (신규 필요) `POST /api/gameplay/equipment/unequip` - 장비 해제

**데이터 구조**:
```typescript
interface Equipment {
  weapon?: {
    item_id: string;
    name: string;
    damage: number;
    durability: number;
    max_durability: number;
    properties: any;
  };
  armor?: {
    item_id: string;
    name: string;
    defense: number;
    durability: number;
    max_durability: number;
    properties: any;
  };
  accessories?: Array<{
    item_id: string;
    name: string;
    properties: any;
  }>;
}
```

**디자인**:
- 슬롯 기반 레이아웃
- 장착된 장비는 아이콘/이름 표시
- 빈 슬롯은 회색 배경

---

### 3.8 게임 내 시간 (개선)

#### 현재 문제점
- 플레이 시간만 표시 (실제 시간)
- 게임 내 가상 시간 없음
- 시간대 표시 없음

#### 개선 계획

**레이아웃**:
```
┌─────────────────────────────────┐
│ 시간                  [닫기] ✕  │
├─────────────────────────────────┤
│ 게임 내 시간                     │
│ 2025년 1월 15일 (화)            │
│ 오후 2시 30분                   │
│ [🌅 오후]                       │
├─────────────────────────────────┤
│ 플레이 시간                      │
│ 1시간 23분                      │
└─────────────────────────────────┘
```

**기능**:
- 게임 내 가상 날짜/시간 표시
- 시간대 표시 (새벽, 아침, 점심, 오후, 저녁, 밤)
- 플레이 시간 표시

**API 연동**:
- (신규 필요) `GET /api/gameplay/time/{session_id}` - 게임 내 시간 조회
  - `virtual_date`: 가상 날짜 (TimeSystem에서 조회)
  - `virtual_time`: 가상 시간 (TimeSystem에서 조회)
  - `time_period`: 시간대 (dawn, morning, lunch, afternoon, evening, night, late_night)
  - `play_time`: 플레이 시간 (초 단위)

**데이터 구조**:
```typescript
interface GameTime {
  day: number;        // 게임 내 일수 (Day 1, Day 2, ...)
  hour: number;       // 시간 (0-23)
  minute: number;     // 분 (0-59)
  second: number;     // 초 (0-59)
  time_period: 'morning' | 'afternoon' | 'evening' | 'night'; // TimeSystem.TimePeriod
  play_time: number;  // 플레이 시간 (초 단위)
}
```

**디자인**:
- 큰 숫자로 날짜/시간 표시
- 시간대별 아이콘/색상 (미묘하게)

---

## 4. API 연동 계획

### 4.1 신규 API 엔드포인트 필요

| 엔드포인트 | 메서드 | 설명 | 우선순위 |
|-----------|--------|------|----------|
| `/api/gameplay/stats/{session_id}` | GET | 플레이어 스탯 조회 | 높음 |
| `/api/gameplay/skills/{session_id}` | GET | 보유 스킬 조회 | 높음 |
| `/api/gameplay/skills/use` | POST | 스킬 사용 | 높음 |
| `/api/gameplay/journal/{session_id}` | GET | 저널 조회 | 높음 |
| `/api/gameplay/equipment/{session_id}` | GET | 장착 장비 조회 | 중간 |
| `/api/gameplay/equipment/equip` | POST | 장비 장착 | 중간 |
| `/api/gameplay/equipment/unequip` | POST | 장비 해제 | 중간 |
| `/api/gameplay/interact/object/place` | POST | 오브젝트에 아이템 놓기 | 높음 |
| `/api/gameplay/time/{session_id}` | GET | 게임 내 시간 조회 | 중간 |

### 4.2 기존 API 활용

- `GET /api/gameplay/inventory/{session_id}` - 인벤토리 조회 (개선 필요)
- `GET /api/gameplay/cell/{session_id}` - 셀 정보 조회 (connected_cells 추가 필요)
- `POST /api/gameplay/interact/object/pickup` - 아이템 획득
- `POST /api/gameplay/combine` - 아이템 조합

---

## 5. 디자인 가이드라인

### 5.1 전체 원칙

1. **미니멀리즘**: 불필요한 요소 제거
2. **소설 읽기 느낌**: 텍스트 중심, 여백 활용
3. **부드러운 애니메이션**: framer-motion 활용
4. **일관된 색상**: 흰색 배경, 검은색 텍스트, 미묘한 강조색

### 5.2 공통 컴포넌트

#### 패널 헤더
```tsx
<div className="p-6 border-b border-black/10">
  <div className="flex items-center justify-between mb-4">
    <h2 className="text-2xl font-light text-black/90">제목</h2>
    <button className="text-black/60 hover:text-black/90">✕</button>
  </div>
</div>
```

#### 탭 네비게이션
```tsx
<div className="flex gap-2">
  {tabs.map(tab => (
    <button className="px-4 py-2 text-sm font-light transition-colors">
      {tab.label}
    </button>
  ))}
</div>
```

#### 리스트 아이템
```tsx
<div className="p-3 bg-black/5 rounded text-sm text-black/80 hover:bg-black/10 transition-colors">
  {/* 내용 */}
</div>
```

### 5.3 색상 팔레트

- **배경**: `bg-white/95` (반투명 흰색)
- **텍스트**: `text-black/90` (주요), `text-black/60` (보조)
- **강조**: `bg-black/10` (호버), `bg-blue-600` (액션 버튼)
- **경계**: `border-black/10` (얇은 경계선)

### 5.4 타이포그래피

- **제목**: `text-2xl font-light`
- **부제목**: `text-lg font-light`
- **본문**: `text-sm font-light`
- **숫자**: `font-normal` (가독성)

### 5.5 애니메이션

- **패널 열기/닫기**: `x: 400 → 0` (슬라이드)
- **탭 전환**: `opacity: 0 → 1, y: 10 → 0`
- **리스트 아이템**: 호버 시 `bg-black/5 → bg-black/10`

---

## 6. 구현 우선순위

### Phase 1: 필수 화면 (1주)
1. ✅ 인벤토리 화면 개선
2. ✅ 스탯 화면 신규
3. ✅ 상자 인벤토리 신규

### Phase 2: 중요 화면 (1주)
4. ✅ 스킬 화면 신규
5. ✅ 저널 화면 개선
6. ✅ 장비 화면 신규

### Phase 3: 개선 화면 (1주)
7. ✅ 마을 탐색/지도 개선
8. ✅ 게임 내 시간 개선

---

## 7. 기술 스택

- **프레임워크**: React + TypeScript
- **스타일링**: Tailwind CSS
- **애니메이션**: Framer Motion
- **상태 관리**: Zustand (gameStore)
- **API 통신**: Axios (gameApi)

---

## 8. 참고 사항

### 8.1 DB 스키마 활용

- `runtime_data.entity_states`:
  - `current_stats`: HP, MP, 기본 능력치
  - `equipped_items`: 장착 중인 장비
  - `inventory`: 인벤토리
  - `active_effects`: 현재 효과

- `reference_layer.entity_effect_ownership`:
  - 보유 스킬/마법 조회

- `game_data.abilities_skills`, `game_data.abilities_magic`:
  - 스킬/마법 템플릿 정보

### 8.2 기존 컴포넌트 재사용

- `InfoPanel`: 탭 구조 재사용
- `Modal`: 모달 컴포넌트 재사용
- `Tabs`: 탭 컴포넌트 재사용

---

## 결론

현재 API와 DB 구조를 기반으로 8개의 화면을 기획했습니다. 모든 화면은 미니멀한 소설 읽기 느낌을 유지하며, 텍스트 중심의 깔끔한 디자인을 적용합니다.

**다음 단계**:
1. API 엔드포인트 구현 (백엔드)
2. 화면별 컴포넌트 구현 (프론트엔드)
3. 통합 테스트

