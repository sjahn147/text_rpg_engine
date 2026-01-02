# World Editor 구현 현황 및 향후 계획

> **최신화 날짜**: 2025-12-28

**작성일**: 2025-01-XX  
**목적**: World Editor의 현재 구현 상태와 텍스트 어드벤처 게임 GUI 통합 계획 정리  
**현재 상태**: World Editor 80% 완료 (계층적 맵 뷰, Entity/Dialogue 편집, 실시간 동기화)

---

## 📋 목차

1. [World Editor 개요](#1-world-editor-개요)
2. [현재 구현 상태](#2-현재-구현-상태)
3. [누락된 기능](#3-누락된-기능)
4. [텍스트 어드벤처 게임 GUI 통합 계획](#4-텍스트-어드벤처-게임-gui-통합-계획)
5. [README.md 업데이트 필요 사항](#5-readmemd-업데이트-필요-사항)

---

## 1. World Editor 개요

### 1.1 목적
**World Editor는 정적 게임 데이터(Game Data)를 개발하는 도구**입니다.
- 세션 데이터(Runtime Data)는 우선순위가 낮음
- 게임 세계의 구조와 콘텐츠를 시각적으로 편집
- 계층적 맵 구조 (World → Region → Location → Cell) 관리

### 1.2 기술 스택
- **백엔드**: FastAPI (Python), PostgreSQL
- **프론트엔드**: React + TypeScript + Vite + Konva.js
- **통신**: REST API + WebSocket (실시간 동기화)
- **포트**: 백엔드 8001, 프론트엔드 3000

---

## 2. 현재 구현 상태

### 2.1 ✅ 완료된 기능

#### 백엔드 (FastAPI)
1. **기본 CRUD API**
   - Regions, Locations, Cells, Entities, World Objects
   - Pins, Roads, Map Metadata
   - Effect Carriers, Items

2. **계층적 맵 구조 API**
   - `GET /api/maps/region/{region_id}` - Region Map 조회
   - `GET /api/maps/region/{region_id}/locations` - Location 목록
   - `GET /api/maps/location/{location_id}` - Location Map 조회
   - `GET /api/maps/location/{location_id}/cells` - Cell 목록
   - `POST/PUT /api/maps/.../position` - 위치 업데이트

3. **Entity 관리 API**
   - Entity CRUD (기본 정보, 능력치, 장비, 인벤토리)
   - Entity Properties 편집 (cell_id, occupation, dialogue 등)
   - Entity 위치 관리 (default_position_3d, entity_size)
   - Dialogue Context/Topic 관리

4. **Cell Properties API**
   - `GET /api/cells/{cell_id}/properties` - Cell Properties 조회
   - `PUT /api/cells/{cell_id}/properties` - Cell Properties 업데이트
   - JSONB 기반 유연한 속성 관리

5. **Dialogue 시스템 API**
   - Dialogue Contexts CRUD
   - Dialogue Topics CRUD
   - Entity와 Dialogue 연결

6. **서비스 레이어**
   - `EntityService`, `CellService`, `DialogueService`
   - `CollisionService` (충돌 검사)
   - `MapHierarchyService` (계층적 맵 관리)

#### 프론트엔드 (React)
1. **계층적 맵 뷰**
   - World Map (Region 배치)
   - Region Map (Location 배치)
   - Location Map (Cell 배치)
   - Cell View (Entity 관리)
   - 브레드크럼 네비게이션

2. **핀 관리**
   - 핀 추가/수정/삭제
   - 핀 드래그 (중간 클릭으로 이동)
   - 핀 타입별 색상 구분
   - 레이어 분리 (레벨별 핀 표시)

3. **Entity Explorer**
   - Region/Location/Cell/Entity 트리 뷰
   - 컨텍스트 메뉴 (맵에 핀 추가)
   - Entity 개수 표시

4. **Entity Editor**
   - 기본 정보 편집
   - 능력치, 장비, 인벤토리 편집
   - Entity Properties 편집 (JSON Form)
   - Dialogue 시스템 관리
   - Effect Carriers 관리

5. **Cell Editor**
   - Cell 정보 편집
   - Cell Properties 편집 (Form/JSON 모드)
   - 이미지 없을 때 플레이스홀더 표시

6. **World Object Editor**
   - World Object CRUD
   - Properties 편집

7. **UI 컴포넌트**
   - Modal, CollapsibleSection, FormField
   - JsonFormField (동적 폼 생성)
   - InputField (text, textarea, select, color)

#### 데이터베이스
1. **마이그레이션 완료**
   - `default_position_3d` (JSONB) - Entity 3D 위치
   - `entity_size` (VARCHAR) - Entity 크기 (tiny, small, medium, large, huge, gargantuan)
   - `dialogue_context_id` (VARCHAR) - Entity 대화 컨텍스트 연결
   - World Objects properties (wall_mounted, passable, movable, dimensions, weight)
   - Map Metadata 계층 구조 (map_level, parent_entity_id, parent_entity_type)

2. **Factory 패턴**
   - `GameDataFactory` - 기본 게임 데이터 생성
   - `WorldDataFactory` - 계층적 세계 데이터 생성
   - `create_region_with_children()` - Region + Locations + Cells + Entities 일괄 생성

3. **테스트 데이터**
   - 16개 Region (마을) 생성
   - 레크레스타 상세 구현 (14 Locations, 16 Cells, 22 Entities, 21 World Objects)

---

### 2.2 ⚠️ 부분 구현 / 미완성 기능

#### 프론트엔드
1. **메뉴 기능** (50_frontend_qa_issues.md 참조)
   - 많은 메뉴 항목이 `alert`/`prompt`로 임시 구현
   - API는 있으나 UI 미구현
   - 문구 불일치

2. **Entity Behavior Schedules**
   - 시간대별 NPC 행동 스케줄 관리 UI 없음
   - API 미구현

3. **Dialogue Knowledge**
   - 대화 지식 베이스 관리 UI 없음
   - API 미구현

4. **Cell 내 Entity 관리**
   - 2D 그리드 기반 위치 편집 미완성
   - 충돌 검사 시각화 없음

5. **World Object 상호작용**
   - World Object와 Entity 간 상호작용 로직 UI 없음

---

### 2.3 📊 구현 통계

| 카테고리 | 완료 | 부분 구현 | 미구현 | 비율 |
|---------|------|---------|--------|------|
| 백엔드 API | 15 | 3 | 2 | 75% |
| 프론트엔드 UI | 12 | 8 | 10 | 40% |
| 데이터베이스 | 8 | 0 | 0 | 100% |
| Factory | 5 | 1 | 0 | 83% |

---

## 3. 누락된 기능

### 3.1 높은 우선순위

1. **Entity Behavior Schedules 관리**
   - 시간대별 NPC 행동 패턴 설정
   - 조건(conditions) 및 행동 데이터(action_data) 편집
   - 참조: `docs/world-editor/52_missing_implementation_features.md`

2. **프론트엔드 메뉴 기능 완성**
   - 임시 구현(`alert`/`prompt`) 제거
   - 실제 UI 구현
   - 참조: `docs/world-editor/50_frontend_qa_issues.md`

### 3.2 중간 우선순위

1. **Entity Status 필드** (ACTIVE, INACTIVE, DEAD, HIDDEN)
2. **Cell Status 및 Cell Type 필드**
3. **Dialogue Context 조건 필드** (cell_id, time_category, event_id)
4. **Dialogue Knowledge 관리**

### 3.3 낮은 우선순위

1. **Dialogue Topic Conditions 편집**
2. **Effect Carrier Tags 확인**
3. **World Object Properties 구조화 편집**

---

## 4. 텍스트 어드벤처 게임 GUI 통합 계획

### 4.1 목표

**World Editor에서 편집한 정적 데이터를 기반으로 텍스트 어드벤처 게임을 플레이할 수 있는 GUI 구현**

- 관찰, 조사 등의 액션을 통해 게임 세계 탐험
- SELECT 쿼리 또는 미리 정의된 API를 통해 결과값 받아오기
- Novel game adventure GUI 스타일의 인터페이스

### 4.2 아키텍처 설계

```
┌─────────────────────────────────────────────────────────┐
│                    Game Client (Novel GUI)              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Text Panel  │  │ Action Panel │  │ Status Panel │  │
│  │  (스토리)    │  │  (액션 버튼) │  │  (상태 정보) │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                        ↓ API 호출
┌─────────────────────────────────────────────────────────┐
│              Game Session API (FastAPI)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Action Handler│  │ Query Service│  │ State Manager│  │
│  │  (액션 처리)  │  │  (DB 쿼리)   │  │  (상태 관리) │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│              Database (PostgreSQL)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Game Data   │  │ Runtime Data  │  │ Reference    │  │
│  │  (정적 데이터)│  │  (세션 데이터)│  │  (매핑)      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 4.3 핵심 기능

#### 4.3.1 액션 시스템
```typescript
// 액션 타입
type GameAction = 
  | 'observe'      // 관찰
  | 'investigate'  // 조사
  | 'examine'      // 검사
  | 'talk'         // 대화
  | 'move'         // 이동
  | 'interact'     // 상호작용
  | 'inventory'    // 인벤토리
  | 'save'         // 저장
  | 'load'         // 불러오기

// 액션 실행
async function executeAction(
  action: GameAction,
  target?: string,
  parameters?: Record<string, any>
): Promise<ActionResult> {
  // API 호출 또는 직접 DB 쿼리
  const response = await api.post('/api/game/action', {
    session_id: currentSessionId,
    action_type: action,
    target: target,
    parameters: parameters
  });
  return response.data;
}
```

#### 4.3.2 쿼리 서비스
```python
# app/game_session/query_service.py
class QueryService:
    """게임 액션에 대한 DB 쿼리 서비스"""
    
    async def observe_cell(self, cell_id: str, session_id: str) -> Dict:
        """셀 관찰 - 셀의 모든 정보 조회"""
        query = """
        SELECT 
            c.cell_id,
            c.cell_name,
            c.cell_description,
            c.cell_properties,
            -- Entities in cell
            (SELECT json_agg(e.*) FROM ...) as entities,
            -- World Objects in cell
            (SELECT json_agg(wo.*) FROM ...) as world_objects
        FROM game_data.world_cells c
        WHERE c.cell_id = $1
        """
        # ...
    
    async def investigate_entity(self, entity_id: str, session_id: str) -> Dict:
        """엔티티 조사 - 엔티티의 상세 정보 조회"""
        # ...
    
    async def examine_object(self, object_id: str, session_id: str) -> Dict:
        """오브젝트 검사 - 오브젝트의 상세 정보 조회"""
        # ...
```

#### 4.3.3 Novel GUI 컴포넌트
```typescript
// app/game_client/components/NovelGameView.tsx
interface NovelGameViewProps {
  sessionId: string;
}

const NovelGameView: React.FC<NovelGameViewProps> = ({ sessionId }) => {
  const [currentText, setCurrentText] = useState<string>('');
  const [availableActions, setAvailableActions] = useState<GameAction[]>([]);
  const [gameState, setGameState] = useState<GameState | null>(null);
  
  // 액션 실행
  const handleAction = async (action: GameAction, target?: string) => {
    const result = await executeAction(action, target);
    setCurrentText(result.description);
    setAvailableActions(result.available_actions);
    setGameState(result.game_state);
  };
  
  return (
    <div className="novel-game-view">
      {/* 스토리 텍스트 영역 */}
      <div className="text-panel">
        <div className="story-text">{currentText}</div>
      </div>
      
      {/* 액션 버튼 영역 */}
      <div className="action-panel">
        {availableActions.map(action => (
          <button 
            key={action.type}
            onClick={() => handleAction(action.type, action.target)}
          >
            {action.label}
          </button>
        ))}
      </div>
      
      {/* 상태 정보 영역 */}
      <div className="status-panel">
        <StatusDisplay gameState={gameState} />
      </div>
    </div>
  );
};
```

### 4.4 구현 단계

#### Phase 1: 게임 세션 API 구현 (1-2주)
1. **Game Session API**
   - `POST /api/game/sessions` - 세션 생성
   - `GET /api/game/sessions/{session_id}` - 세션 조회
   - `POST /api/game/sessions/{session_id}/actions` - 액션 실행
   - `GET /api/game/sessions/{session_id}/state` - 게임 상태 조회

2. **Query Service 구현**
   - `observe_cell()` - 셀 관찰
   - `investigate_entity()` - 엔티티 조사
   - `examine_object()` - 오브젝트 검사
   - `get_available_actions()` - 가능한 액션 목록

3. **Action Handler 통합**
   - 기존 `ActionHandler`와 연동
   - 액션 결과를 텍스트 형식으로 변환

#### Phase 2: Novel GUI 프론트엔드 구현 (2-3주)
1. **Novel Game View 컴포넌트**
   - 텍스트 패널 (스토리 표시)
   - 액션 패널 (버튼 목록)
   - 상태 패널 (플레이어 상태, 위치 등)

2. **액션 시스템**
   - 액션 버튼 동적 생성
   - 액션 실행 및 결과 표시
   - 상태 업데이트

3. **세션 관리**
   - 세션 생성/불러오기
   - 세션 저장/복구
   - 세션 목록 관리

#### Phase 3: 통합 및 테스트 (1주)
1. **통합 테스트**
   - World Editor → Game Client 전체 플로우
   - 액션 실행 및 결과 검증
   - 세션 저장/복구 테스트

2. **성능 최적화**
   - 쿼리 최적화
   - 프론트엔드 렌더링 최적화

3. **문서화**
   - 사용자 가이드
   - 개발자 가이드

### 4.5 기술 스택

#### 게임 클라이언트
- **프론트엔드**: React + TypeScript (기존 World Editor와 통합 또는 별도 앱)
- **스타일링**: CSS Modules 또는 Styled Components
- **상태 관리**: React Context 또는 Zustand
- **API 통신**: Axios

#### 게임 세션 API
- **백엔드**: FastAPI (기존 World Editor와 통합)
- **데이터베이스**: PostgreSQL (기존 스키마 활용)
- **서비스**: `GameSession`, `QueryService`, `ActionHandler` 통합

### 4.6 예상 결과

1. **World Editor에서 편집한 데이터를 즉시 게임에서 사용 가능**
2. **텍스트 기반 어드벤처 게임 경험 제공**
3. **관찰, 조사 등의 액션을 통한 세계 탐험**
4. **세션 저장/복구로 게임 진행 관리**

---

## 5. README.md 업데이트 필요 사항

### 5.1 현재 README.md 상태

README.md는 **2025-10-21 기준**으로 작성되었으며, 그 이후의 **World Editor 개발이 거의 반영되지 않았습니다**.

### 5.2 추가해야 할 내용

#### 5.2.1 World Editor 섹션 추가
```markdown
## 🗺️ World Editor

### 개요
World Editor는 정적 게임 데이터(Game Data)를 시각적으로 편집하는 도구입니다.

### 기능
- 계층적 맵 구조 관리 (World → Region → Location → Cell)
- Entity, World Object, Dialogue 시스템 편집
- 실시간 동기화 (WebSocket)
- Cell Properties, Entity Properties JSON 편집

### 실행 방법
```bash
# 백엔드 서버 실행
cd app/world_editor
python run_server.py

# 프론트엔드 실행 (별도 터미널)
cd app/world_editor/frontend
npm run dev
```

### 문서
- [World Editor 통합 로드맵](./docs/project-management/01_world_editor_integration_roadmap.md)
- [프론트엔드 QA 이슈](./docs/world-editor/50_frontend_qa_issues.md)
- [누락된 구현 사항](./docs/world-editor/52_missing_implementation_features.md)
```

#### 5.2.2 최근 업데이트 로그에 추가
```markdown
#### **v0.5.0** (2025-01-XX) - **World Editor 구현**
- **World Editor 기본 구조 완성**
  - 계층적 맵 뷰 시스템 (World → Region → Location → Cell)
  - Entity, World Object, Dialogue 시스템 편집
  - Cell Properties, Entity Properties JSON 편집
  - 실시간 동기화 (WebSocket)

- **데이터베이스 마이그레이션**
  - Entity 위치/크기 필드 추가 (default_position_3d, entity_size)
  - World Objects properties 필드 추가
  - Map Metadata 계층 구조 필드 추가
  - Dialogue Context/Topic 시스템 완성

- **Factory 패턴 확장**
  - WorldDataFactory 구현
  - 계층적 데이터 일괄 생성 지원
  - 레크레스타 상세 데이터 생성

- **프론트엔드 구현**
  - React + TypeScript + Konva.js 기반 맵 에디터
  - Entity Explorer, Entity Editor, Cell Editor
  - 계층적 네비게이션 및 브레드크럼
```

#### 5.2.3 프로젝트 구조 업데이트
```markdown
├── app/
│   ├── world_editor/          # World Editor 모듈 (신규)
│   │   ├── main.py            # FastAPI 메인 앱
│   │   ├── routes/            # API 라우터
│   │   ├── services/          # 비즈니스 로직
│   │   └── frontend/          # React 프론트엔드
│   │       ├── src/
│   │       │   ├── components/
│   │       │   ├── hooks/
│   │       │   └── services/
│   │       └── package.json
```

#### 5.2.4 다음 단계 업데이트
```markdown
### 🚀 다음 단계
- **World Editor 완성**: 메뉴 기능 구현, Entity Behavior Schedules 관리
- **텍스트 어드벤처 게임 GUI**: Novel game adventure 스타일 인터페이스
- **게임 세션 API**: World Editor 데이터를 게임에서 사용
- **액션 시스템**: 관찰, 조사 등의 액션을 통한 세계 탐험
```

---

## 6. 최근 변경사항 (2025-01-XX 이후)

### 6.1 SSOT (Single Source of Truth) 구현

#### Phase 1: owner_name 제거 및 JOIN으로 해결
- **문제**: `location_properties`와 `cell_properties`의 JSONB에 `owner_name`이 중복 저장되어 SSOT 원칙 위반
- **해결**: 
  - `owner_name`을 JSONB에서 제거
  - API에서 `LEFT JOIN game_data.entities`를 통해 `owner_name` 동적 조회
  - `LocationResponse`, `CellResponse` 스키마에 `owner_name: Optional[str]` 추가

#### Phase 2: 참조 무결성 검증
- **구현**: Entity/Cell 삭제 시 참조 검증 로직 추가
  - `LocationService.validate_entity_references()`: Location에서 Entity 참조 확인
  - `CellService.validate_cell_references()`: Cell에서 Cell 참조 확인
  - `EntityService.delete_entity()`: 삭제 전 참조 검증 수행

#### Phase 3: 데이터 마이그레이션
- **마이그레이션 스크립트**:
  - `remove_owner_name_ssot.sql`: JSONB에서 `owner_name` 제거
  - `cleanup_orphan_references_ssot.sql`: 고아 참조 정리
- **테스트**: `test_ssot_migration.py`로 마이그레이션 검증

#### Phase 4: Resolved API 추가
- **새로운 엔드포인트**:
  - `GET /api/locations/{location_id}/resolved`: 모든 참조를 해결한 Location 데이터 반환
  - `GET /api/cells/{cell_id}/resolved`: 모든 참조를 해결한 Cell 데이터 반환
- **스키마**: `LocationResolvedResponse`, `CellResolvedResponse` 추가
  - `owner_entity`: 완전한 Entity 객체
  - `quest_giver_entities`: 완전한 Entity 배열
  - `entry_point_cells`, `exit_cells`, `entrance_cells`, `connection_cells`: 완전한 Cell 배열

### 6.2 Location/Cell 정보 탭 개선

#### 편집 가능한 정보 탭
- **변경 전**: 조건부 표시, 읽기 전용
- **변경 후**: 
  - 모든 필드를 항상 표시 (속성이 없어도 빈 필드로 표시)
  - 편집 가능한 필드: 소유권, 로어, 상세 정보, 환경 (Cell)
  - 읽기 전용 필드: 기본 정보 (이름, 설명, 타입 등), 주인 이름 (SSOT)

#### Entity 선택 UI 개선
- **변경 전**: 직접 입력 (텍스트 필드)
- **변경 후**: 
  - `EntityPickerModal` 컴포넌트 추가
  - 검색 기능 포함 (이름 또는 ID로 검색)
  - Entity 목록에서 선택
  - 주인 Entity ID는 읽기 전용 필드 + 검색 버튼
  - 주인 이름은 완전히 읽기 전용 (SSOT 원칙)

### 6.3 데이터베이스 스키마 업데이트

#### 주석 및 문서화
- `mvp_schema.sql`에 SSOT 관련 주석 추가
- `location_properties`, `cell_properties`의 `ownership.owner_entity_id` 필드 설명 보강
- 참조 무결성 제약조건 명시

---

## 7. 참고 문서

1. **World Editor 통합 로드맵**: `docs/project-management/01_world_editor_integration_roadmap.md`
2. **프론트엔드 QA 이슈**: `docs/world-editor/50_frontend_qa_issues.md`
3. **누락된 구현 사항**: `docs/world-editor/52_missing_implementation_features.md`
4. **Cell Properties 명세**: `docs/world-editor/51_cell_properties_specification.md`
5. **계층적 맵 뷰 설계**: `docs/world-editor/44_hierarchical_map_view_design.md`
6. **SSOT 분석**: `docs/world-editor/54_location_cell_properties_ssot_analysis.md`

---

## 8. 결론

World Editor는 **정적 게임 데이터 개발 도구**로서 현재 약 **80% 구현 완료** 상태입니다. 
SSOT 원칙을 적용하여 데이터 일관성을 개선하고, Location/Cell 정보 탭을 편집 가능하게 개선했습니다.

**우선순위**:
1. ✅ World Editor 핵심 기능 완성 (진행 중)
2. ✅ SSOT 구현 및 데이터 일관성 개선 (완료)
3. 🔄 텍스트 어드벤처 게임 GUI 구현 (다음 단계)
4. ⏳ 게임 세션 API 및 Query Service 구현
5. ⏳ 통합 및 테스트

