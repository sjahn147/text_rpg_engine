# 전문 게임 개발 도구 수준 UI/UX 요구사항

## 개요

현재 월드 에디터를 Unity, Unreal Engine, Skyrim Creation Kit 수준의 전문적인 게임 개발 도구로 발전시키기 위한 UI/UX 요구사항을 정리합니다.

## 1. 현재 구현 상태

### ✅ 구현 완료
- 기본 지도 편집 (핀 추가/수정/삭제, 도로 그리기)
- 통합 엔티티 탐색기 (트리 구조)
- 엔티티 편집기 (모달 기반)
- 기본 툴바 (도구 선택, 줌, 그리드)
- WebSocket 실시간 동기화

### ❌ 미구현 사항 (이전 설계 문서 기준)
- Phase 4: 리스트/뷰어 모드
- Phase 5: 고급 기능 (검색, 필터링, 컨텍스트 메뉴, 드래그 앤 드롭, 일괄 작업)
- 메뉴바 (MenuBar)
- 상태바 (StatusBar)
- 단축키 시스템
- Undo/Redo 시스템
- 설정/환경설정
- 프로젝트 관리
- 내보내기/가져오기
- 로그/콘솔 창
- 성능 모니터링

## 2. 메뉴바 (MenuBar) 설계

### 2.1 File 메뉴
```
File
├─ New Project...          (Ctrl+N)
├─ Open Project...         (Ctrl+O)
├─ Save Project            (Ctrl+S)
├─ Save Project As...      (Ctrl+Shift+S)
├─ ────────────────────────
├─ Import...
│  ├─ Import Map Image...
│  ├─ Import Entities (JSON)...
│  └─ Import Regions (CSV)...
├─ Export...
│  ├─ Export Map Image...
│  ├─ Export Entities (JSON)...
│  ├─ Export Regions (CSV)...
│  └─ Export Full World Data...
├─ ────────────────────────
├─ Recent Projects
│  ├─ Project 1
│  ├─ Project 2
│  └─ ...
├─ ────────────────────────
└─ Exit                    (Alt+F4)
```

### 2.2 Edit 메뉴
```
Edit
├─ Undo                    (Ctrl+Z)
├─ Redo                    (Ctrl+Y / Ctrl+Shift+Z)
├─ ────────────────────────
├─ Cut                     (Ctrl+X)
├─ Copy                    (Ctrl+C)
├─ Paste                   (Ctrl+V)
├─ Duplicate               (Ctrl+D)
├─ Delete                  (Del)
├─ ────────────────────────
├─ Select All              (Ctrl+A)
├─ Deselect All            (Ctrl+Shift+A)
├─ ────────────────────────
├─ Find...                 (Ctrl+F)
├─ Find in Files...        (Ctrl+Shift+F)
├─ Replace...              (Ctrl+H)
├─ ────────────────────────
└─ Preferences...          (Ctrl+,)
```

### 2.3 View 메뉴
```
View
├─ Toolbars
│  ├─ Main Toolbar         (✓)
│  ├─ Entity Tools         (✓)
│  └─ View Tools           (✓)
├─ ────────────────────────
├─ Panels
│  ├─ Explorer Panel       (Ctrl+Shift+E)
│  ├─ Properties Panel     (Ctrl+Shift+P)
│  ├─ Console Panel        (Ctrl+Shift+C)
│  ├─ Log Panel            (Ctrl+Shift+L)
│  └─ Performance Panel    (Ctrl+Shift+Perf)
├─ ────────────────────────
├─ View Modes
│  ├─ Map View             (Ctrl+1)
│  ├─ List View            (Ctrl+2)
│  ├─ Tree View            (Ctrl+3)
│  └─ Split View           (Ctrl+4)
├─ ────────────────────────
├─ Zoom
│  ├─ Zoom In              (Ctrl+=)
│  ├─ Zoom Out             (Ctrl+-)
│  ├─ Zoom to Fit          (Ctrl+0)
│  └─ Zoom to Selection    (Ctrl+Shift+0)
├─ ────────────────────────
├─ Grid
│  ├─ Show Grid            (Ctrl+G)
│  ├─ Snap to Grid         (Ctrl+Shift+G)
│  └─ Grid Settings...
├─ ────────────────────────
└─ Fullscreen              (F11)
```

### 2.4 Entity 메뉴
```
Entity
├─ New Entity...
│  ├─ Region...
│  ├─ Location...
│  ├─ Cell...
│  ├─ Character (NPC)...
│  ├─ World Object...
│  ├─ Effect Carrier...
│  └─ Item...
├─ ────────────────────────
├─ Duplicate Entity        (Ctrl+D)
├─ Delete Entity           (Del)
├─ ────────────────────────
├─ Entity Properties...    (Enter)
├─ Entity Relationships...
├─ ────────────────────────
└─ Batch Operations...
    ├─ Batch Edit...
    ├─ Batch Delete...
    └─ Batch Export...
```

### 2.5 Tools 메뉴
```
Tools
├─ Validation
│  ├─ Validate All Entities...
│  ├─ Check for Orphans...
│  └─ Check for Duplicates...
├─ ────────────────────────
├─ Data Management
│  ├─ Clean Unused Data...
│  ├─ Optimize Database...
│  └─ Backup Database...
├─ ────────────────────────
├─ Import/Export
│  ├─ Import from JSON...
│  ├─ Export to JSON...
│  ├─ Import from CSV...
│  └─ Export to CSV...
├─ ────────────────────────
├─ Scripts
│  ├─ Run Script...
│  └─ Script Manager...
├─ ────────────────────────
└─ Settings...             (Ctrl+,)
```

### 2.6 Window 메뉴
```
Window
├─ New Window
├─ ────────────────────────
├─ Layouts
│  ├─ Default Layout
│  ├─ Compact Layout
│  ├─ Wide Layout
│  └─ Save Current Layout...
├─ ────────────────────────
├─ Dock Panels
│  ├─ Dock Left
│  ├─ Dock Right
│  ├─ Dock Top
│  ├─ Dock Bottom
│  └─ Float
├─ ────────────────────────
└─ Reset Layout
```

### 2.7 Help 메뉴
```
Help
├─ Documentation           (F1)
├─ Keyboard Shortcuts...
├─ Tutorials
│  ├─ Getting Started
│  ├─ Creating Entities
│  └─ Advanced Features
├─ ────────────────────────
├─ About World Editor...
├─ Check for Updates...
└─ Report Issue...
```

## 3. 상태바 (StatusBar) 설계

### 3.1 상태바 구성
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [Ready] │ Selected: Region (REG_001) │ Position: (1234, 5678) │ Zoom: 100% │
│         │                            │                        │            │
│ [Status]│ [Selection Info]           │ [Coordinates]          │ [View Info]│
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 상태바 섹션
1. **상태 표시기**
   - Ready / Loading / Saving / Error
   - 연결 상태 (WebSocket)
   - 자동 저장 상태

2. **선택 정보**
   - 현재 선택된 엔티티 타입 및 ID
   - 선택된 엔티티 개수 (일괄 선택 시)

3. **좌표 정보**
   - 마우스 커서 위치 (지도 좌표)
   - 선택된 핀/오브젝트 위치
   - 그리드 스냅 상태

4. **뷰 정보**
   - 현재 줌 레벨
   - 뷰포트 크기
   - FPS (성능 모니터링)

## 4. 고급 기능 요구사항

### 4.1 Undo/Redo 시스템
- **구현 범위**: 모든 편집 작업 (엔티티 생성/수정/삭제, 핀 이동, 도로 그리기 등)
- **스택 크기**: 최소 50단계, 설정에서 조정 가능
- **저장 방식**: 메모리 기반 (성능 최적화)
- **단축키**: Ctrl+Z (Undo), Ctrl+Y (Redo)

### 4.2 단축키 시스템
- **구현 방식**: 전역 단축키 매니저
- **설정 가능**: 사용자 정의 단축키
- **충돌 검사**: 단축키 충돌 감지 및 경고
- **카테고리별 분류**: 편집, 뷰, 엔티티, 도구 등

### 4.3 검색 및 필터링
- **통합 검색**: 모든 엔티티 타입에서 검색
- **고급 필터**: 타입, 속성, 날짜 범위 등
- **검색 결과 하이라이트**: 트리/리스트에서 하이라이트
- **검색 히스토리**: 최근 검색어 저장

### 4.4 컨텍스트 메뉴 (우클릭)
- **트리 노드 우클릭**:
  - 새로 만들기
  - 복사
  - 붙여넣기
  - 삭제
  - 이름 변경
  - 속성 보기
  - 관계 보기
  - 내보내기

- **지도 우클릭**:
  - 핀 추가
  - 도로 시작
  - 줌 인/아웃
  - 그리드 스냅 토글

### 4.5 드래그 앤 드롭
- **트리 내 이동**: 엔티티 계층 구조 변경
- **파일 드롭**: 이미지, JSON 파일 등
- **엔티티 복사**: Ctrl+드래그로 복사

### 4.6 일괄 작업
- **일괄 선택**: Ctrl+클릭, Shift+클릭, 박스 선택
- **일괄 편집**: 여러 엔티티 동시 수정
- **일괄 삭제**: 선택된 모든 엔티티 삭제
- **일괄 내보내기**: 선택된 엔티티만 내보내기

### 4.7 리스트 뷰 모드
- **테이블 형태**: 컬럼 정렬, 필터링, 검색
- **컬럼 구성**: ID, 이름, 타입, 설명, 생성일, 수정일
- **페이지네이션**: 대량 데이터 처리
- **가상 스크롤**: 성능 최적화

### 4.8 뷰어 모드
- **읽기 전용 상세 정보**: 엔티티 전체 정보 표시
- **관계도 시각화**: 부모-자식 관계, 참조 관계 그래프
- **JSON 뷰어**: 고급 사용자용 원시 데이터 보기
- **인쇄/PDF 내보내기**: 문서화용

## 5. 성능 최적화 요구사항

### 5.1 가상 스크롤링
- **대상**: 트리 탐색기, 리스트 뷰
- **라이브러리**: `react-window` 또는 `react-virtualized`
- **목표**: 10,000+ 엔티티도 부드럽게 스크롤

### 5.2 메모이제이션
- **트리 렌더링**: React.memo, useMemo 활용
- **편집 폼**: 불필요한 리렌더링 방지
- **지도 캔버스**: Konva 레이어 최적화

### 5.3 지연 로딩
- **트리 노드**: 확장 시에만 자식 데이터 로드
- **이미지**: 지도 이미지 지연 로드
- **편집 폼**: 탭 전환 시 데이터 로드

### 5.4 디바운싱/스로틀링
- **검색 입력**: 300ms 디바운싱
- **자동 저장**: 2초 디바운싱
- **스크롤 이벤트**: 스로틀링

## 6. 설정/환경설정

### 6.1 설정 카테고리
1. **일반 (General)**
   - 언어 설정
   - 테마 (Light/Dark)
   - 자동 저장 간격
   - 최근 프로젝트 개수

2. **편집 (Editing)**
   - 기본 엔티티 타입
   - 자동 완성 활성화
   - 그리드 스냅 기본값
   - Undo/Redo 스택 크기

3. **뷰 (View)**
   - 기본 줌 레벨
   - 그리드 표시 기본값
   - 패널 기본 레이아웃
   - 폰트 크기

4. **단축키 (Shortcuts)**
   - 모든 단축키 설정
   - 단축키 충돌 검사
   - 단축키 내보내기/가져오기

5. **성능 (Performance)**
   - 가상 스크롤 임계값
   - 캐시 크기
   - 자동 최적화 활성화

6. **고급 (Advanced)**
   - 디버그 모드
   - 로그 레벨
   - API 엔드포인트 설정

## 7. 프로젝트 관리

### 7.1 프로젝트 구조
```
project_name/
├── world_data/
│   ├── regions.json
│   ├── locations.json
│   ├── entities.json
│   └── ...
├── assets/
│   ├── maps/
│   ├── images/
│   └── ...
├── exports/
│   └── ...
├── backups/
│   └── ...
└── project.json (메타데이터)
```

### 7.2 프로젝트 메타데이터
```json
{
  "name": "My World",
  "version": "1.0.0",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "author": "User Name",
  "description": "World description",
  "settings": {
    "map_image": "assets/maps/worldmap.png",
    "default_zoom": 1.0,
    "grid_size": 50
  }
}
```

## 8. 로그/콘솔 시스템

### 8.1 콘솔 패널
- **로그 레벨**: Error, Warning, Info, Debug
- **필터링**: 레벨별, 타입별 필터
- **검색**: 로그 내용 검색
- **내보내기**: 로그 파일 저장

### 8.2 로그 타입
- **시스템 로그**: 앱 시작/종료, 에러
- **편집 로그**: 엔티티 생성/수정/삭제
- **API 로그**: API 요청/응답
- **성능 로그**: 렌더링 시간, 메모리 사용량

## 9. 성능 모니터링

### 9.1 성능 패널
- **FPS**: 실시간 프레임 레이트
- **메모리 사용량**: 힙 메모리, DOM 노드 수
- **렌더링 시간**: 컴포넌트별 렌더링 시간
- **네트워크**: API 요청 시간, WebSocket 지연

### 9.2 성능 경고
- **낮은 FPS**: 30fps 미만 시 경고
- **높은 메모리**: 500MB 초과 시 경고
- **느린 API**: 1초 초과 시 경고

## 10. 내보내기/가져오기

### 10.1 내보내기 형식
- **JSON**: 전체 데이터 또는 선택된 엔티티
- **CSV**: 테이블 형태 데이터
- **PNG/SVG**: 지도 이미지
- **PDF**: 문서화용 리포트

### 10.2 가져오기 형식
- **JSON**: 엔티티 데이터
- **CSV**: 대량 데이터 일괄 입력
- **이미지**: 지도 배경 이미지

## 11. 테마 및 커스터마이징

### 11.1 테마
- **Light Theme**: 밝은 배경
- **Dark Theme**: 어두운 배경
- **High Contrast**: 접근성 향상
- **커스텀 테마**: 사용자 정의 색상

### 11.2 레이아웃 커스터마이징
- **패널 위치**: 드래그로 재배치
- **패널 크기**: 리사이즈 가능
- **레이아웃 저장**: 여러 레이아웃 저장 및 전환

## 12. 접근성 (Accessibility)

### 12.1 키보드 네비게이션
- **트리 탐색**: 화살표 키
- **포커스 관리**: Tab 순서
- **단축키**: 모든 기능 키보드 접근 가능

### 12.2 스크린 리더 지원
- **ARIA 레이블**: 모든 UI 요소에 레이블
- **상태 알림**: 변경사항 음성 안내
- **키보드 힌트**: 단축키 표시

## 13. 구현 우선순위

### Phase 1: 필수 기능 (High Priority)
1. ✅ 메뉴바 구현
2. ✅ 상태바 구현
3. ✅ 단축키 시스템
4. ✅ Undo/Redo 시스템
5. ✅ 설정/환경설정

### Phase 2: 고급 기능 (Medium Priority)
6. ✅ 검색 및 필터링 고도화
7. ✅ 컨텍스트 메뉴
8. ✅ 드래그 앤 드롭
9. ✅ 일괄 작업
10. ✅ 리스트 뷰 모드

### Phase 3: 최적화 및 부가 기능 (Low Priority)
11. ✅ 뷰어 모드
12. ✅ 성능 모니터링
13. ✅ 로그/콘솔 시스템
14. ✅ 프로젝트 관리
15. ✅ 내보내기/가져오기 고도화

## 14. 참고 자료

### 게임 개발 도구 UI 패턴
- **Unity Editor**: 계층 구조, 인스펙터, 씬 뷰
- **Unreal Engine**: 월드 아웃라이너, 디테일 패널
- **Skyrim Creation Kit**: 오브젝트 윈도우, 렌더 윈도우
- **Blender**: 아웃라이너, 속성 패널, 뷰포트

### UI 라이브러리
- **React DnD**: 드래그 앤 드롭
- **React Window**: 가상 스크롤링
- **React Hotkeys**: 단축키 관리
- **React Context Menu**: 컨텍스트 메뉴

## 15. 기술 스택 추가

### 필요한 라이브러리
```json
{
  "dependencies": {
    "react-window": "^1.8.10",
    "react-hotkeys-hook": "^4.4.1",
    "react-contextmenu": "^2.14.0",
    "react-dnd": "^16.0.1",
    "react-dnd-html5-backend": "^16.0.1",
    "react-json-view": "^1.21.3",
    "file-saver": "^2.0.5",
    "papaparse": "^5.4.1"
  }
}
```

## 16. 다음 단계

1. **메뉴바 컴포넌트 구현**
2. **상태바 컴포넌트 구현**
3. **단축키 시스템 구현**
4. **Undo/Redo 시스템 구현**
5. **설정 시스템 구현**
6. **고급 기능 단계적 구현**

