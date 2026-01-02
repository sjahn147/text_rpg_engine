# 월드 에디터 PinEditor 와이어프레임

> **문서 번호**: 29  
> **작성일**: 2025-12-27  
> **목적**: 전문적이고 미니멀한 작업용 패널 와이어프레임 설계

---

## 1. 디자인 원칙

### 1.1 핵심 원칙
- **미니멀리즘**: 불필요한 장식 제거, 정보 중심
- **고밀도 정보**: 작은 글씨로 많은 정보 표시
- **전문성**: 작업 효율성 우선
- **일관성**: 통일된 스타일과 간격

### 1.2 타이포그래피
- **제목**: 11px, Bold, #333
- **본문**: 10px, Regular, #666
- **라벨**: 9px, Medium, #999
- **입력 필드**: 10px, Regular, #000
- **버튼 텍스트**: 9px, Medium, #fff

### 1.3 간격 시스템
- **최소 간격**: 4px
- **기본 간격**: 8px
- **섹션 간격**: 12px
- **패널 패딩**: 12px

### 1.4 색상 팔레트
- **배경**: #FFFFFF (메인), #F8F9FA (섹션)
- **테두리**: #E0E0E0 (기본), #D0D0D0 (강조)
- **텍스트**: #333333 (주요), #666666 (보조), #999999 (라벨)
- **액센트**: #2196F3 (링크/액션), #4CAF50 (성공), #F44336 (경고)

---

## 2. 전체 레이아웃

```
┌─────────────────────────────────────────────────────────────┐
│  PinEditor Panel (350px width, 100vh height)                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ HEADER (고정, 40px)                                    │  │
│  │ ┌─────────────────────────────────────────────────┐ │  │
│  │ │ [×] Region Editor                    [⋮]        │ │  │
│  │ │ PIN_ABC123                           [Collapse] │ │  │
│  │ └─────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ CONTENT (스크롤 가능, flex: 1)                         │  │
│  │                                                         │  │
│  │ ┌─ METADATA SECTION ───────────────────────────────┐  │  │
│  │ │ ▼ Metadata                              [Edit]   │  │  │
│  │ │ ┌─────────────────────────────────────────────┐ │  │  │
│  │ │ │ Pin ID:        [PIN_ABC123        ] [Copy] │ │  │  │
│  │ │ │ Game Data ID:  [REG_NORTH_001    ] [Copy] │ │  │  │
│  │ │ │ Pin Type:      [region ▼]                  │ │  │  │
│  │ │ │ Position:      X:[100] Y:[200]             │ │  │  │
│  │ │ │ Icon:          [default ▼] Size:[10]      │ │  │  │
│  │ │ │ Color:         [#FF6B9D] [Pick]            │ │  │  │
│  │ │ └─────────────────────────────────────────────┘ │  │  │
│  │ └───────────────────────────────────────────────────┘  │  │
│  │                                                         │  │
│  │ ┌─ REGION SECTION ──────────────────────────────────┐  │  │
│  │ │ ▼ Region Info                          [Edit]   │  │  │
│  │ │ ┌─────────────────────────────────────────────┐ │  │  │
│  │ │ │ ID:          REG_NORTH_001        [Copy]   │ │  │  │
│  │ │ │ Name:        [Northern Forest    ]         │ │  │  │
│  │ │ │ Type:        [wilderness ▼]                │ │  │  │
│  │ │ │ Description: [A vast forest...   ]         │ │  │  │
│  │ │ │             [                    ]         │ │  │  │
│  │ │ └─────────────────────────────────────────────┘ │  │  │
│  │ └───────────────────────────────────────────────────┘  │  │
│  │                                                         │  │
│  │ ┌─ LOCATIONS SECTION ────────────────────────────────┐  │  │
│  │ │ ▼ Locations (3)                        [+ Add]   │  │  │
│  │ │ ┌─────────────────────────────────────────────┐ │  │  │
│  │ │ │ ▶ LOC_REG_NORTH_001_TOWN_001               │ │  │  │
│  │ │ │   Town Square                              │ │  │  │
│  │ │ │   Type: town | Cells: 5                    │ │  │  │
│  │ │ │ ┌───────────────────────────────────────┐ │ │  │  │
│  │ │ │ │ ▶ CELL_TOWN_SQUARE_001                 │ │ │  │  │
│  │ │ │ │   Central Plaza                        │ │ │  │  │
│  │ │ │ │   Size: 10x10                          │ │ │  │  │
│  │ │ │ └───────────────────────────────────────┘ │ │  │  │
│  │ │ │ ▶ LOC_REG_NORTH_001_DUNGEON_001           │ │  │  │
│  │ │ │   Dark Cave                               │ │  │  │
│  │ │ │   Type: dungeon | Cells: 3                │ │  │  │
│  │ │ │ ▶ LOC_REG_NORTH_001_FOREST_001            │ │  │  │
│  │ │ │   Deep Woods                              │ │  │  │
│  │ │ │   Type: wilderness | Cells: 8            │ │  │  │
│  │ │ └─────────────────────────────────────────────┘ │  │  │
│  │ └───────────────────────────────────────────────────┘  │  │
│  │                                                         │  │
│  │ ┌─ D&D STATS SECTION ────────────────────────────────┐  │  │
│  │ │ ▼ D&D 통계 정보                          [Edit]   │  │  │
│  │ │ ┌─────────────────────────────────────────────┐ │  │  │
│  │ │ │ Climate:      [temperate ▼]                 │ │  │  │
│  │ │ │ Danger Level: [3] [1-10]                    │ │  │  │
│  │ │ │ Rec. Level:   Min:[1] Max:[10]              │ │  │  │
│  │ │ │ BGM:          [peaceful_01 ▼]              │ │  │  │
│  │ │ │ Ambient:      [birds, wind]                │ │  │  │
│  │ │ └─────────────────────────────────────────────┘ │  │  │
│  │ └───────────────────────────────────────────────────┘  │  │
│  │                                                         │  │
│  │ ┌─ DETAIL SECTION ──────────────────────────────────┐  │  │
│  │ │ ▼ 상세 정보                            [Edit]   │  │  │
│  │ │ ┌─────────────────────────────────────────────┐ │  │  │
│  │ │ │ [섹션 추가]                                  │ │  │  │
│  │ │ │                                             │ │  │  │
│  │ │ │ ▶ 외관                                      │ │  │  │
│  │ │ │   [아르보이아 해는 마치 거대한 사파이어...] │ │  │  │
│  │ │ │   [                    ]                 │ │  │  │
│  │ │ │                                             │ │  │  │
│  │ │ │ ▶ 광원                                      │ │  │  │
│  │ │ │   [이 바다의 빛깔은 정말 믿기 어려울...]   │ │  │  │
│  │ │ │                                             │ │  │  │
│  │ │ │ ▶ 공기                                      │ │  │  │
│  │ │ │   [아르보이아 해의 공기는 마법처럼...]     │ │  │  │
│  │ │ │                                             │ │  │  │
│  │ │ │ ▶ 소리                                      │ │  │  │
│  │ │ │   [이 바다에는 고요함과 활기참이...]       │ │  │  │
│  │ │ │                                             │ │  │  │
│  │ │ │ ▶ 역사                                      │ │  │  │
│  │ │ │   [아르보이아 해에는 수많은 전설과...]     │ │  │  │
│  │ │ │                                             │ │  │  │
│  │ │ │ ▶ 주요 장소                                │ │  │  │
│  │ │ │   • 용의 굴: 전설 속 용이 잠들어...        │ │  │  │
│  │ │ │   • 고대 문명의 유적지: 바닷가 절벽...      │ │  │  │
│  │ │ │   [+ 항목 추가]                            │ │  │  │
│  │ │ │                                             │ │  │  │
│  │ │ │ ▶ 숨겨진 사실                              │ │  │  │
│  │ │ │   [나는 한때 이 바다의 한 섬에서...]       │ │  │  │
│  │ │ │   [                    ]                 │ │  │  │
│  │ │ └─────────────────────────────────────────────┘ │  │  │
│  │ └───────────────────────────────────────────────────┘  │  │
│  │                                                         │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ FOOTER (고정, 36px)                                    │  │
│  │ ┌─────────────────────────────────────────────────┐ │  │
│  │ │ [Save All] [Reset] [Delete Pin]                 │ │  │
│  │ └─────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 섹션별 상세 설계

### 3.1 Header (40px 고정)

```
┌─────────────────────────────────────────────────────┐
│ [×]  Region Editor                    [⋮] [▼]      │
│ PIN_ABC123 | REG_NORTH_001                           │
└─────────────────────────────────────────────────────┘
```

**요소:**
- 왼쪽: 닫기 버튼 (×), 제목 (Pin Type + "Editor")
- 오른쪽: 메뉴 버튼 (⋮), 접기 버튼 (▼)
- 하단: Pin ID, Game Data ID (작은 글씨, 회색)

**스타일:**
- 높이: 40px
- 배경: #FFFFFF
- 테두리 하단: 1px solid #E0E0E0
- 패딩: 8px 12px

### 3.2 Metadata Section

```
┌─ Metadata ──────────────────────────────── [Edit] ─┐
│ Pin ID:        [PIN_ABC123        ] [Copy]          │
│ Game Data ID:  [REG_NORTH_001    ] [Copy]          │
│ Pin Type:      [region ▼]                          │
│ Position:      X:[100] Y:[200]                     │
│ Icon:          [default ▼] Size:[10]               │
│ Color:         [#FF6B9D] [Pick]                    │
└─────────────────────────────────────────────────────┘
```

**레이아웃:**
- 2열 그리드: 라벨 (80px) | 입력 필드 (flex: 1)
- 입력 필드 높이: 24px
- 행 간격: 6px
- 섹션 패딩: 8px

**입력 필드 스타일:**
- 높이: 24px
- 폰트: 10px
- 패딩: 4px 8px
- 테두리: 1px solid #E0E0E0
- border-radius: 2px

### 3.3 Region Section

```
┌─ Region Info ──────────────────────────── [Edit] ─┐
│ ID:          REG_NORTH_001        [Copy]            │
│ Name:        [Northern Forest    ]                 │
│ Type:        [wilderness ▼]                        │
│ Description: [A vast forest...   ]                 │
│             [                    ]                 │
│             [                    ]                 │
└─────────────────────────────────────────────────────┘
```

**레이아웃:**
- 2열 그리드: 라벨 (80px) | 입력 필드 (flex: 1)
- Description: textarea, 3줄 (60px)
- ID 필드: 읽기 전용, Copy 버튼 포함

### 3.4 Locations Section (계층 구조)

```
┌─ Locations (3) ────────────────────────── [+ Add] ─┐
│ ▶ LOC_REG_NORTH_001_TOWN_001                       │
│   Town Square                                      │
│   Type: town | Cells: 5                            │
│   ┌─────────────────────────────────────────────┐ │
│   │ ▶ CELL_TOWN_SQUARE_001                       │ │
│   │   Central Plaza                              │ │
│   │   Size: 10x10                                │ │
│   │ ▶ CELL_TOWN_SQUARE_002                       │ │
│   │   Market Stalls                               │ │
│   │   Size: 8x8                                  │ │
│   └─────────────────────────────────────────────┘ │
│ ▶ LOC_REG_NORTH_001_DUNGEON_001                    │
│   Dark Cave                                        │
│   Type: dungeon | Cells: 3                         │
│ ▶ LOC_REG_NORTH_001_FOREST_001                    │
│   Deep Woods                                       │
│   Type: wilderness | Cells: 8                      │
└─────────────────────────────────────────────────────┘
```

**계층 구조 표시:**
- Location: ▶ 아이콘, ID, Name, Type, Cell 개수
- Cell (하위): 들여쓰기 (12px), 작은 글씨 (9px)
- 접기/펼치기: ▶/▼ 토글
- 호버: 배경색 #F5F5F5
- 선택: 배경색 #E3F2FD, 테두리 #2196F3

**인터랙션:**
- Location 클릭: 상세 정보 표시
- Cell 클릭: Cell 편집기로 전환
- 우클릭: 컨텍스트 메뉴 (Edit, Delete, Duplicate)

### 3.5 D&D Stats Section (D&D 통계 정보)

```
┌─ D&D 통계 정보 ──────────────────────── [Edit] ─┐
│ Climate:      [temperate ▼]                         │
│ Danger Level: [3] [1-10]                           │
│ Rec. Level:   Min:[1] Max:[10]                     │
│ BGM:          [peaceful_01 ▼]                      │
│ Ambient:      [birds, wind]                        │
└─────────────────────────────────────────────────────┘
```

**레이아웃:**
- 2열 그리드: 라벨 (100px) | 입력 필드 (flex: 1)
- Danger Level: 슬라이더 + 숫자 입력
- Rec. Level: Min/Max 두 개의 숫자 입력
- Ambient: 태그 입력 (쉼표로 구분)

**저장 위치:**
- `region_properties.dnd_stats` 또는 `location_properties.dnd_stats`

**중요:** 이 섹션은 기존 D&D 통계 정보를 유지하며, 상세 정보 섹션과 별도로 존재합니다.

### 3.6 Detail Section (상세 정보)

```
┌─ 상세 정보 ──────────────────────────── [Edit] ─┐
│ [섹션 추가 ▼]                                      │
│                                                   │
│ ▶ 외관                                            │
│   [아르보이아 해는 마치 거대한 사파이어를...]   │
│   [                    ]                         │
│   [×]                                             │
│                                                   │
│ ▶ 광원                                            │
│   [이 바다의 빛깔은 정말 믿기 어려울 정도로...] │
│   [×]                                             │
│                                                   │
│ ▶ 주요 장소                                        │
│   • 용의 굴: 전설 속 용이 잠들어 있다는 동굴.    │
│   • 고대 문명의 유적지: 바닷가 절벽 위에...      │
│   [+ 항목 추가]                                    │
│   [×]                                             │
└─────────────────────────────────────────────────────┘
```

**레이아웃:**
- 섹션 기반 구조: 각 섹션은 제목 + 본문으로 구성
- 섹션 타입:
  - **텍스트 섹션**: 제목 + textarea (여러 문단 가능)
  - **리스트 섹션**: 제목 + 리스트 항목들 (• 또는 번호)
- 섹션 추가: 드롭다운에서 타입 선택
- 섹션 삭제: 각 섹션 우측 [×] 버튼
- 섹션 접기/펼치기: ▶/▼ 토글
- 섹션 순서 변경: 드래그 앤 드롭

**섹션 타입:**
1. **텍스트 섹션**: 자유 형식의 여러 문단 텍스트 (긴 묘사 지원)
2. **리스트 섹션**: 불릿 또는 번호 리스트
3. **구조화된 섹션**: 제목 + 세부 항목들 (템플릿 기반)
4. **제목 섹션**: 제목만 있는 구분선 역할

**지원하는 템플릿 카테고리 (15개):**
1. 기본 식별 정보 (Identity)
2. 지리 · 환경 (Geography & Environment)
3. 역사 (History)
4. 정치 · 행정 (Government & Politics)
5. 군사 · 치안 (Military & Security)
6. 경제 · 산업 (Economy & Industry)
7. 사회 · 문화 (Society & Culture)
8. 종교 · 신앙 (Religion)
9. 마법 요소 (Magic)
10. 주요 장소 (Locations)
11. 주요 인물 (NPCs)
12. 갈등 · 플롯 훅 (Conflicts & Plot Hooks)
13. 여행 · 접근성 (Travel & Logistics)
14. 메타 정보 (GM용)
15. 요약 블록 (Quick Reference)

**입력 필드:**
- 섹션 제목: 10px, Bold, 최대 100자
- 본문: textarea, 10px, 최소 5줄, 자동 확장 (무제한 길이)
- 구조화된 섹션: 제목 + 세부 항목 입력 필드들
  - 각 세부 항목: 라벨 + 입력 필드 (텍스트/리스트/긴 텍스트)
- 리스트 항목: 10px, 각 항목은 별도 입력 필드 (긴 텍스트 가능)

**구조화된 섹션 예시:**
```
▶ 기본 식별 정보
  이름 (공식명): [헬라로스                    ]
  이름 (통칭):   [항구 도시                    ]
  정착지 유형:   [대도시 ▼]                   
  규모 (인구):   [50만 명                      ]
  물리적 크기:   [약 45km²                    ]
  설립 시기:     [고대 아누스 제국 시절        ]
  소속:          [안브레티아 제국, 그노페티샤르 후작령]
  상징:          [문장: 파란 바다 위의 등대    ]
  슬로건:        ["바다의 관문"                ]
  [상세 설명:                                  ]
  [헬라로스는 안브레티아 제국의 수도 아발룸과...]
  [                    ]                      ]
  [×]
```

**긴 텍스트 입력 지원:**
- 모든 텍스트 필드는 textarea로 구현
- 최소 높이: 5줄 (약 100px)
- 자동 확장: 내용에 따라 높이 증가
- 최대 높이: 없음 (스크롤 지원)
- 스크롤바: 각 textarea 내부 스크롤

**중요:** 이 섹션은 D&D 통계 정보와 별도로 존재하며, 제공된 긴 텍스트 형식의 상세 정보(외관, 광원, 공기, 소리, 역사, 주요 장소, 숨겨진 사실 등)를 담습니다.

### 3.7 Footer (36px 고정)

```
┌─────────────────────────────────────────────────────┐
│ [Save All] [Reset] [Delete Pin]                     │
└─────────────────────────────────────────────────────┘
```

**버튼 스타일:**
- 높이: 28px
- 폰트: 9px, Medium
- 패딩: 6px 12px
- 간격: 8px
- Save All: #4CAF50 배경, #fff 텍스트
- Reset: #999999 배경, #fff 텍스트
- Delete Pin: #F44336 배경, #fff 텍스트

---

## 4. 컴포넌트 스펙

### 4.1 CollapsibleSection

```typescript
interface CollapsibleSectionProps {
  title: string;
  count?: number;  // 예: "Locations (3)"
  defaultExpanded?: boolean;
  actionButton?: React.ReactNode;  // 예: [+ Add]
  children: React.ReactNode;
}
```

**스타일:**
- 헤더 높이: 32px
- 배경: #F8F9FA
- 테두리: 1px solid #E0E0E0
- border-radius: 2px
- 패딩: 8px

### 4.2 FormField

```typescript
interface FormFieldProps {
  label: string;
  labelWidth?: number;  // 기본 80px
  required?: boolean;
  error?: string;
  children: React.ReactNode;
}
```

**레이아웃:**
- 2열 그리드
- 라벨: 고정 너비, 오른쪽 정렬
- 입력: flex: 1

### 4.3 InputField

```typescript
interface InputFieldProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  readOnly?: boolean;
  copyButton?: boolean;
  type?: 'text' | 'number' | 'select' | 'color' | 'textarea';
  options?: string[];  // select용
}
```

**스타일:**
- 높이: 24px (textarea 제외)
- 폰트: 10px
- 패딩: 4px 8px
- 테두리: 1px solid #E0E0E0
- border-radius: 2px

### 4.4 DetailSectionEditor

```typescript
interface DetailSectionEditorProps {
  sections: DetailSection[];
  onChange: (sections: DetailSection[]) => void;
  readOnly?: boolean;
}

interface DetailSection {
  id: string;
  type: 'text' | 'list' | 'structured' | 'title';
  title: string;
  content?: string;  // 텍스트 섹션용 (긴 텍스트)
  items?: string[];  // 리스트 섹션용 (각 항목도 긴 텍스트 가능)
  fields?: StructuredField[];  // 구조화된 섹션용
  expanded?: boolean;
}

interface StructuredField {
  id: string;
  label: string;
  type: 'text' | 'longtext' | 'select' | 'list';
  value: string | string[];
  options?: string[];  // select용
}

interface DetailSectionEditorState {
  sections: DetailSection[];
  editingSectionId: string | null;
  addingSection: boolean;
  templateCategories: TemplateCategory[];
}

interface TemplateCategory {
  id: string;
  name: string;
  description: string;
  fields: TemplateField[];
}

interface TemplateField {
  label: string;
  type: 'text' | 'longtext' | 'select' | 'list';
  options?: string[];  // select용
  placeholder?: string;
}
```

**기능:**
- 섹션 추가: 
  - 드롭다운에서 타입 선택 (텍스트/리스트/구조화된/제목)
  - 템플릿 카테고리 선택 시 구조화된 섹션 자동 생성
  - 빈 섹션 생성 후 자유롭게 편집
- 섹션 편집: 
  - 제목/본문/리스트 항목 편집
  - 구조화된 섹션: 각 세부 항목별 편집
  - 긴 텍스트: textarea로 무제한 입력
- 섹션 삭제: [×] 버튼 클릭
- 섹션 순서 변경: 드래그 앤 드롭
- 섹션 접기/펼치기: ▶/▼ 토글
- 자동 저장: onBlur 시 저장
- 템플릿 적용: 템플릿 카테고리 선택 시 해당 구조로 섹션 생성

**템플릿 카테고리 정의:**
- 15개 주요 카테고리 각각에 대한 템플릿 필드 정의
- 사용자는 템플릿을 선택하거나 자유롭게 편집 가능
- 템플릿은 초기 구조만 제공, 이후 자유 편집 가능

**스타일:**
- 섹션 간격: 12px
- 섹션 패딩: 8px
- 섹션 배경: #F8F9FA
- 섹션 테두리: 1px solid #E0E0E0
- textarea 높이: 최소 100px (5줄), 자동 확장, 최대 높이 없음
- 구조화된 필드: 2열 그리드 (라벨 120px | 입력 flex: 1)
- 긴 텍스트 textarea: 최소 150px, 스크롤 지원

### 4.5 HierarchyTree

```typescript
interface HierarchyTreeProps {
  items: HierarchyItem[];
  onSelect: (item: HierarchyItem) => void;
  onExpand: (itemId: string) => void;
  expandedItems: Set<string>;
}

interface HierarchyItem {
  id: string;
  name: string;
  type: 'location' | 'cell';
  metadata: {
    type?: string;
    cellCount?: number;
    size?: string;
  };
  children?: HierarchyItem[];
}
```

**스타일:**
- 아이템 높이: 28px
- 들여쓰기: 12px per level
- 폰트: 10px (Location), 9px (Cell)
- 호버: #F5F5F5
- 선택: #E3F2FD, 테두리 #2196F3

---

## 5. 반응형 및 스크롤

### 5.1 스크롤 영역

```css
.content-area {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 12px;
}

.content-area::-webkit-scrollbar {
  width: 6px;
}

.content-area::-webkit-scrollbar-track {
  background: #F5F5F5;
}

.content-area::-webkit-scrollbar-thumb {
  background: #CCCCCC;
  border-radius: 3px;
}

.content-area::-webkit-scrollbar-thumb:hover {
  background: #999999;
}
```

### 5.2 고정 영역

- Header: `position: sticky; top: 0; z-index: 10;`
- Footer: `position: sticky; bottom: 0; z-index: 10;`

### 5.3 최소/최대 높이

- 섹션 최소 높이: 40px
- 섹션 최대 높이: 없음 (스크롤)
- 전체 패널: 100vh

---

## 6. 상태 표시

### 6.1 로딩 상태

```
┌─ Region Info ──────────────────────────── [Edit] ─┐
│ [Loading...]                                        │
└─────────────────────────────────────────────────────┘
```

### 6.2 저장 상태

```
┌─ Region Info ──────────────────────────── [Saved] ─┐
│ ID:          REG_NORTH_001        [Copy]            │
│ Name:        [Northern Forest    ] ✓               │
└─────────────────────────────────────────────────────┘
```

### 6.3 에러 상태

```
┌─ Region Info ──────────────────────────── [Edit] ─┐
│ ID:          REG_NORTH_001        [Copy]            │
│ Name:        [Northern Forest    ]                │
│              ⚠ ID already exists                   │
└─────────────────────────────────────────────────────┘
```

---

## 7. 인터랙션 플로우

### 7.1 Location 추가

1. [+ Add] 버튼 클릭
2. Location 추가 폼 표시 (인라인 또는 모달)
3. Location 정보 입력
4. [Create] 버튼 클릭
5. Location 목록에 추가, 자동 선택

### 7.2 Cell 추가

1. Location 선택
2. Location 하위에 [+ Add Cell] 버튼 표시
3. Cell 추가 폼 표시
4. Cell 정보 입력
5. [Create] 버튼 클릭
6. Cell 목록에 추가

### 7.3 편집 모드

1. [Edit] 버튼 클릭
2. 해당 섹션의 모든 필드 편집 가능 상태로 전환
3. [Save] / [Cancel] 버튼 표시
4. 변경사항 저장 또는 취소

---

## 8. 접근성

### 8.1 키보드 네비게이션

- Tab: 다음 필드로 이동
- Shift+Tab: 이전 필드로 이동
- Enter: 편집 모드 활성화/저장 (textarea 내에서는 줄바꿈)
- Escape: 편집 취소/패널 닫기
- Arrow Up/Down: 목록 항목 선택
- Ctrl+Enter: 섹션 추가 (빠른 추가)
- Delete: 선택된 섹션 삭제

### 8.2 포커스 표시

- 포커스 링: 2px solid #2196F3
- 포커스 배경: #F5F5F5

---

## 9. 구현 우선순위

### Phase 1: 기본 레이아웃
1. Header/Footer 고정
2. Content 영역 스크롤
3. 기본 섹션 구조

### Phase 2: 메타데이터 편집
1. Metadata Section
2. Region Section
3. FormField 컴포넌트

### Phase 3: 계층 구조
1. Locations Section
2. HierarchyTree 컴포넌트
3. Cell 표시

### Phase 4: D&D 통계 정보 및 상세 정보
1. D&D Stats Section (기존 통계 정보 유지)
2. Detail Section (섹션 기반 편집기) - 추가
3. 섹션 추가/삭제/순서 변경
4. 텍스트/리스트 섹션 타입 지원
5. 자동 저장 및 스크롤 지원

**중요:** D&D 통계 정보와 상세 정보는 별도의 섹션으로 모두 지원됩니다.

### Phase 5: 인터랙션
1. 편집 모드
2. 추가/삭제 기능
3. 상태 표시

---

**문서 작성 완료일:** 2025-12-27  
**다음 단계:** 컴포넌트 구현

