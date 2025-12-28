# 통합 엔티티 탐색기 및 에디터 설계

## 개요

스카이림 Creation Kit과 유사한 구조의 통합 엔티티 관리 시스템을 설계합니다. 모든 게임 엔티티(지역, 위치, 셀, 인물, 오브젝트, 이펙트, 장비 등)를 트리 구조로 탐색하고 관리할 수 있는 UI를 제공합니다.

## 1. 전체 UI 구조

### 1.1 레이아웃

```
┌─────────────────────────────────────────────────────────────────┐
│  Toolbar (도구 모음)                                            │
├──────────┬──────────────────────────────────────┬──────────────┤
│          │                                      │              │
│  탐색기  │         메인 작업 영역                │   속성 패널  │
│  패널    │      (지도 / 리스트 / 뷰어)          │              │
│          │                                      │              │
│ (250px)  │         (Flexible)                   │   (350px)    │
│          │                                      │              │
└──────────┴──────────────────────────────────────┴──────────────┘
```

### 1.2 탐색기 패널 (왼쪽)

**계층 구조:**
```
📁 게임 데이터
  ├─ 📁 지역 (Regions)
  │   ├─ 📍 아르보이아 해 (REG_CONTINENT_ARBOYA_001)
  │   │   ├─ 📁 위치 (Locations)
  │   │   │   ├─ 📍 그라로로스 섬 (LOC_ARBOYA_GRALOROS_001)
  │   │   │   │   ├─ 📁 셀 (Cells)
  │   │   │   │   │   ├─ 📍 항구 (CELL_PORT_MAIN_001)
  │   │   │   │   │   │   ├─ 👤 인물 (Entities)
  │   │   │   │   │   │   │   ├─ 👤 선장 존 (NPC_CAPTAIN_JOHN_001)
  │   │   │   │   │   │   │   └─ 👤 상인 마리아 (NPC_MERCHANT_MARIA_001)
  │   │   │   │   │   │   └─ 📦 오브젝트 (World Objects)
  │   │   │   │   │   │       ├─ 📦 보물 상자 (OBJ_CHEST_TREASURE_001)
  │   │   │   │   │   │       └─ 📦 문 (OBJ_DOOR_MAIN_001)
  │   │   │   │   │   └─ 📍 시장 (CELL_MARKET_MAIN_001)
  │   │   │   │   └─ 📍 헬라로스 (LOC_ARBOYA_HELAROS_001)
  │   │   │   └─ 📍 ...
  │   │   └─ 📍 ...
  │   └─ 📍 ...
  │
  ├─ 📁 인물 (Entities) [전체 목록]
  │   ├─ 👤 선장 존 (NPC_CAPTAIN_JOHN_001)
  │   ├─ 👤 상인 마리아 (NPC_MERCHANT_MARIA_001)
  │   └─ ...
  │
  ├─ 📁 오브젝트 (World Objects) [전체 목록]
  │   ├─ 📦 보물 상자 (OBJ_CHEST_TREASURE_001)
  │   ├─ 📦 문 (OBJ_DOOR_MAIN_001)
  │   └─ ...
  │
  ├─ 📁 이펙트 (Effect Carriers) [전체 목록]
  │   ├─ ⚡ 힘의 축복 (EFFECT_BLESSING_STRENGTH_001)
  │   ├─ ⚡ 치유의 물약 (EFFECT_POTION_HEAL_001)
  │   └─ ...
  │
  ├─ 📁 장비 (Items) [전체 목록]
  │   ├─ ⚔️ 철검 (ITEM_SWORD_IRON_001)
  │   ├─ 🛡️ 가죽 갑옷 (ITEM_ARMOR_LEATHER_001)
  │   └─ ...
  │
  └─ 📁 도로 (Roads)
      ├─ 🛣️ 아르보이아 → 그라로로스
      └─ ...
```

### 1.3 메인 작업 영역 (중앙)

**모드별 표시:**

1. **지도 모드** (기존 MapCanvas)
   - 지도 위에 핀 표시
   - 핀 클릭/드래그
   - 도로 그리기

2. **리스트 모드** (새로 추가)
   - 선택된 카테고리의 모든 엔티티를 테이블로 표시
   - 정렬, 필터링, 검색 기능
   - 일괄 선택 및 작업

3. **뷰어 모드** (새로 추가)
   - 선택된 엔티티의 상세 정보를 읽기 전용으로 표시
   - 관계도 시각화 (어떤 셀에 속하는지, 어떤 인물이 있는지 등)

### 1.4 속성 패널 (오른쪽)

- 선택된 엔티티의 편집 폼
- 기존 PinEditor와 유사하지만 모든 엔티티 타입 지원
- 탭 구조로 정보 분류

## 2. 컴포넌트 설계

### 2.1 EntityExplorer (탐색기)

```typescript
interface EntityExplorerProps {
  onEntitySelect: (entityType: string, entityId: string) => void;
  selectedEntityType?: string;
  selectedEntityId?: string;
}

// 기능:
// - 트리 구조 표시
// - 확장/축소
// - 검색
// - 필터링 (타입별)
// - 컨텍스트 메뉴 (우클릭)
//   - 새로 만들기
//   - 복사
//   - 삭제
//   - 이름 변경
//   - 속성 보기
```

**트리 노드 타입:**
- `RegionNode`: 지역
- `LocationNode`: 위치
- `CellNode`: 셀
- `EntityNode`: 인물
- `WorldObjectNode`: 오브젝트
- `EffectCarrierNode`: 이펙트
- `ItemNode`: 장비
- `RoadNode`: 도로

### 2.2 EntityEditor (통합 편집기)

```typescript
interface EntityEditorProps {
  entityType: 'region' | 'location' | 'cell' | 'entity' | 'world_object' | 'effect_carrier' | 'item' | 'road';
  entityId: string | null;
  onSave: (entityType: string, entityId: string, data: any) => Promise<void>;
  onDelete: (entityType: string, entityId: string) => Promise<void>;
  onClose: () => void;
}

// 기능:
// - 엔티티 타입에 따라 다른 편집 폼 표시
// - 기존 모달들 재사용 (LocationEditorModal, CellEditorModal, EntityEditorModal 등)
// - 공통 UI 컴포넌트 활용
```

### 2.3 EntityListView (리스트 뷰)

```typescript
interface EntityListViewProps {
  entityType: string;
  entities: any[];
  onEntitySelect: (entityId: string) => void;
  onEntityEdit: (entityId: string) => void;
  onEntityDelete: (entityId: string) => void;
}

// 기능:
// - 테이블 형태로 엔티티 목록 표시
// - 컬럼: ID, 이름, 타입, 설명, 생성일, 수정일
// - 정렬 (컬럼 클릭)
// - 필터링 (검색창)
// - 일괄 선택
// - 페이지네이션
```

### 2.4 EntityViewer (뷰어)

```typescript
interface EntityViewerProps {
  entityType: string;
  entityId: string;
}

// 기능:
// - 엔티티 정보 읽기 전용 표시
// - 관계도 시각화
//   - 부모-자식 관계
//   - 참조 관계 (어떤 셀에 있는지, 어떤 인물이 소유하는지 등)
// - JSON 뷰어 (고급 사용자용)
```

## 3. 데이터 구조

### 3.1 트리 노드 데이터

```typescript
interface TreeNode {
  id: string;
  type: 'region' | 'location' | 'cell' | 'entity' | 'world_object' | 'effect_carrier' | 'item' | 'road' | 'folder';
  label: string;
  icon: string;
  children?: TreeNode[];
  data?: any; // 실제 엔티티 데이터
  expanded?: boolean;
  selected?: boolean;
}
```

### 3.2 엔티티 타입별 아이콘

- 📁 폴더: `folder`
- 📍 지역: `region`
- 📍 위치: `location`
- 📍 셀: `cell`
- 👤 인물: `entity`
- 📦 오브젝트: `world_object`
- ⚡ 이펙트: `effect_carrier`
- ⚔️ 장비: `item`
- 🛣️ 도로: `road`

## 4. API 통합

### 4.1 필요한 API 엔드포인트

**이미 구현됨:**
- ✅ Regions: `/api/regions`
- ✅ Locations: `/api/locations`
- ✅ Cells: `/api/cells`
- ✅ Entities: `/api/entities`
- ✅ World Objects: `/api/world-objects`
- ✅ Effect Carriers: `/api/effect-carriers`
- ✅ Roads: `/api/roads`

**추가 필요:**
- ❌ Items: `/api/items` (장비 관리)
- ❌ 통합 검색: `/api/search?q=...&type=...`
- ❌ 관계 조회: `/api/entities/{id}/relationships`

### 4.2 데이터 로딩 전략

1. **초기 로드**: 최상위 레벨만 로드 (Regions, 전체 목록)
2. **지연 로드**: 트리 노드 확장 시 자식 데이터 로드
3. **캐싱**: 로드한 데이터는 메모리에 캐시
4. **실시간 업데이트**: WebSocket으로 변경사항 동기화

## 5. 사용자 워크플로우

### 5.1 엔티티 생성

1. 탐색기에서 부모 노드 선택
2. 우클릭 → "새로 만들기" → 엔티티 타입 선택
3. 모달 창에서 정보 입력
4. 저장 → 트리에 자동 추가

### 5.2 엔티티 편집

1. 탐색기에서 엔티티 선택
2. 속성 패널에 편집 폼 표시
3. 수정 후 저장

### 5.3 엔티티 삭제

1. 탐색기에서 엔티티 선택
2. 우클릭 → "삭제" 또는 Delete 키
3. 확인 대화상자
4. 삭제 → 트리에서 제거

### 5.4 엔티티 검색

1. 탐색기 상단 검색창에 키워드 입력
2. 실시간 필터링
3. 결과 하이라이트

## 6. 구현 단계

### Phase 1: 탐색기 기본 구조
- [ ] EntityExplorer 컴포넌트 생성
- [ ] 트리 노드 렌더링
- [ ] 확장/축소 기능
- [ ] 기본 선택 기능

### Phase 2: 데이터 통합
- [ ] 모든 엔티티 타입 데이터 로드
- [ ] 계층 구조 구성
- [ ] 지연 로딩 구현

### Phase 3: 편집기 통합
- [ ] EntityEditor 컴포넌트 생성
- [ ] 기존 모달들 통합
- [ ] 엔티티 타입별 편집 폼

### Phase 4: 리스트/뷰어 모드
- [ ] EntityListView 컴포넌트
- [ ] EntityViewer 컴포넌트
- [ ] 모드 전환 기능

### Phase 5: 고급 기능
- [ ] 검색 및 필터링
- [ ] 컨텍스트 메뉴
- [ ] 드래그 앤 드롭 (계층 변경)
- [ ] 일괄 작업

## 7. UI/UX 고려사항

### 7.1 성능
- 가상 스크롤링 (대량 데이터)
- 디바운싱 (검색 입력)
- 메모이제이션 (트리 렌더링)

### 7.2 접근성
- 키보드 네비게이션 (화살표 키로 트리 탐색)
- 스크린 리더 지원
- 포커스 관리

### 7.3 사용성
- 직관적인 아이콘
- 명확한 레이블
- 빠른 피드백 (로딩, 성공, 에러)
- 되돌리기/다시하기 (Undo/Redo)

## 8. 기술 스택

- **트리 컴포넌트**: `react-treeview` 또는 커스텀 구현
- **아이콘**: `react-icons` 또는 커스텀 SVG
- **가상 스크롤**: `react-window` (필요시)
- **드래그 앤 드롭**: `react-beautiful-dnd` (필요시)

## 9. 참고 자료

- Skyrim Creation Kit UI 구조
- Unity Editor Hierarchy View
- Blender Outliner
- VS Code Explorer

