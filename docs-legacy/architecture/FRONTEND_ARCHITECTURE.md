# 프론트엔드 아키텍처 설계 문서

**작성일**: 2025-12-31  
**최신화**: 2026-01-01  
**목적**: EditorMode 컴포넌트 분리 및 프론트엔드 구조 개선

## 현재 상태 분석

### EditorMode.tsx 현황
- **파일 크기**: 1685줄 (2026-01-01 확인)
- **상태 변수**: 커스텀 훅으로 대부분 추출됨
- **주요 기능**:
  1. 지도 편집 (MapCanvas, HierarchicalMapView)
  2. 핀 편집 (PinEditor, PinTreeView)
  3. 엔티티 탐색 (EntityExplorer, EntityEditor)
  4. 셀 관리 (CellEntityManager)
  5. 도로 그리기
  6. 검색 기능
  7. 백업/복원
  8. 설정 관리
  9. WebSocket 동기화
  10. Undo/Redo 시스템

### 문제점
1. **단일 책임 원칙 위반**: 하나의 컴포넌트가 너무 많은 책임을 가짐
2. **상태 관리 복잡도**: 20개 이상의 상태 변수가 한 곳에 집중
3. **테스트 어려움**: 거대한 컴포넌트는 단위 테스트가 어려움
4. **재사용성 부족**: 로직이 컴포넌트에 강하게 결합됨
5. **유지보수 어려움**: 변경 시 사이드 이펙트 파악이 어려움

## 목표 아키텍처

### 원칙
1. **단일 책임 원칙**: 각 컴포넌트는 하나의 명확한 책임만 가짐
2. **관심사 분리**: UI, 상태 관리, 비즈니스 로직 분리
3. **재사용성**: 공통 로직은 커스텀 훅으로 추출
4. **테스트 가능성**: 각 컴포넌트와 훅을 독립적으로 테스트 가능
5. **확장성**: 새로운 기능 추가 시 기존 코드에 최소한의 영향

### 현재 구조 (2026-01-01 기준)

**참고**: 아래 구조는 이미 대부분 구현되어 있습니다.

```
app/ui/frontend/src/
├── modes/
│   ├── EditorMode.tsx (메인, 1685줄 - 리팩토링 진행 중)
│   └── GameMode.tsx ✅
│
├── components/
│   └── editor/
│       ├── layout/ ✅ (구현 완료)
│       │   ├── EditorLayout.tsx ✅
│       │   ├── EditorSidebar.tsx ✅
│       │   └── EditorMainArea.tsx ✅
│       │
│       ├── map/ ✅ (구현 완료)
│       │   └── MapEditor.tsx ✅
│       │
│       ├── MapCanvas.tsx ✅ (기존)
│       ├── HierarchicalMapView.tsx ✅ (기존)
│       │
│       ├── PinEditorNew.tsx ✅ (기존)
│       ├── PinTreeView.tsx ✅ (기존)
│       │
│       ├── EntityExplorer.tsx ✅ (기존)
│       ├── EntityEditor.tsx ✅ (기존)
│       │
│       ├── CellEntityManager.tsx ✅ (기존)
│       │
│       ├── SearchResultsModal.tsx ✅ (기존)
│       │
│       └── ... (다양한 편집 컴포넌트들) ✅
│
├── hooks/
│   └── editor/ ✅ (구현 완료)
│       ├── useEditorState.ts ✅
│       ├── useMapEditor.ts ✅
│       ├── useRoadDrawing.ts ✅
│       ├── useEditorSearch.ts ✅
│       ├── useEditorBackup.ts ✅
│       ├── useEditorModals.ts ✅
│       └── useMapControls.ts ✅
│
├── screens/
│   └── game/ ✅ (구현 완료)
│       ├── GameScreen.tsx ✅
│       ├── InventoryScreen.tsx ✅
│       ├── JournalScreen.tsx ✅
│       └── ... (다양한 게임 화면들) ✅
│
└── App.tsx ✅ (모드 전환 구현 완료)
```

## 리팩토링 진행 상태 (2026-01-01 기준)

### ✅ Phase 1: 상태 관리 추출 (완료)

1. ✅ **useEditorState.ts** - 구현 완료
   - 전역 에디터 상태 (explorerMode, selectedEntityType 등)
   - 상태 변경 함수들

2. ✅ **useMapEditor.ts** - 구현 완료
   - 지도 관련 상태 (mapViewMode, currentMapLevel 등)
   - 지도 조작 함수들

3. ✅ **useRoadDrawing.ts** - 구현 완료
   - 도로 그리기 상태 (roadDrawingState)
   - 도로 그리기 로직

4. ✅ **useEditorSearch.ts** - 구현 완료
5. ✅ **useEditorBackup.ts** - 구현 완료
6. ✅ **useEditorModals.ts** - 구현 완료
7. ✅ **useMapControls.ts** - 구현 완료

### ✅ Phase 2: 기능별 컴포넌트 분리 (부분 완료)

1. ✅ **MapEditor 컴포넌트** - 구현 완료
   - `components/editor/map/MapEditor.tsx` 존재

2. ✅ **EntityExplorer 컴포넌트** - 이미 분리됨
   - EntityExplorer, EntityEditor 존재

3. ✅ **CellEntityManager 컴포넌트** - 이미 분리됨

### ✅ Phase 3: 레이아웃 구조화 (완료)

1. ✅ **EditorLayout.tsx** - 구현 완료
   - 전체 레이아웃 구조
   - 사이드바, 메인 영역 배치

2. ✅ **EditorSidebar.tsx** - 구현 완료
   - 사이드바 영역
   - 탐색기, 트리 뷰 등

3. ✅ **EditorMainArea.tsx** - 구현 완료
   - 메인 편집 영역
   - 지도, 편집기 등

### ⚠️ Phase 4: 컨텍스트 도입 (미구현)

1. ❌ **EditorContext.tsx** - 미구현
   - 현재는 커스텀 훅으로 상태 관리
   - 컨텍스트 도입은 선택적

### 🔄 남은 작업

**EditorMode.tsx 추가 리팩토링 필요:**
- 현재 1685줄로 여전히 큰 파일
- 일부 로직을 추가 컴포넌트로 분리 가능
- 하지만 이미 많은 부분이 훅으로 추출되어 가독성 향상됨

## 구현 우선순위

### 높은 우선순위
1. **Phase 1: 상태 관리 추출**
   - 즉시 효과: 코드 가독성 향상
   - 낮은 리스크: 기존 컴포넌트 구조 유지

2. **Phase 2: MapEditor 분리**
   - 가장 복잡한 기능
   - 독립적으로 테스트 가능

### 중간 우선순위
3. **Phase 2: PinEditor 분리**
   - 핀 편집 로직 분리

4. **Phase 2: EntityExplorer 통합**
   - 엔티티 관련 기능 통합

### 낮은 우선순위
5. **Phase 3: 레이아웃 구조화**
   - UI 구조 개선

6. **Phase 4: 컨텍스트 도입**
   - 전역 상태 관리 개선

## 각 컴포넌트 책임 정의

### EditorMode.tsx (메인)
- **책임**: 전체 에디터 조율, 레이아웃 배치
- **상태**: 최소한의 전역 상태만 관리
- **크기**: ~200줄 이하

### MapEditor.tsx
- **책임**: 지도 편집 기능
- **상태**: 지도 관련 상태 (useMapEditor 훅 사용)
- **의존성**: MapCanvas, HierarchicalMapView, MapToolbar

### PinEditor.tsx
- **책임**: 핀 편집 기능
- **상태**: 핀 관련 상태 (usePinEditor 훅 사용)
- **의존성**: PinEditorNew, PinTreeView

### EntityExplorer.tsx
- **책임**: 엔티티 탐색 및 편집
- **상태**: 엔티티 관련 상태 (useEntityEditor 훅 사용)
- **의존성**: EntityEditor, EntityTree

## 마이그레이션 전략

### 점진적 리팩토링
1. **기존 코드 유지**: 리팩토링 중에도 기존 코드가 동작하도록
2. **단계별 테스트**: 각 Phase 완료 후 테스트
3. **역호환성**: 기존 API와 인터페이스 유지

### 테스트 전략
1. **기능 테스트**: 각 기능이 정상 동작하는지 확인
2. **통합 테스트**: 컴포넌트 간 상호작용 확인
3. **회귀 테스트**: 기존 기능이 깨지지 않았는지 확인

## 예상 효과

### 코드 품질
- **가독성**: 각 컴포넌트가 명확한 책임을 가짐
- **유지보수성**: 변경 시 영향 범위가 명확함
- **테스트 가능성**: 각 컴포넌트를 독립적으로 테스트 가능

### 개발 생산성
- **재사용성**: 공통 로직을 훅으로 재사용
- **확장성**: 새로운 기능 추가가 용이
- **협업**: 여러 개발자가 동시에 작업 가능

## 참고 자료
- React 공식 문서: Component Composition
- React 공식 문서: Custom Hooks
- Clean Code: Single Responsibility Principle

