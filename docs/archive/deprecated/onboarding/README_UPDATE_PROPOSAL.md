# README.md 업데이트 제안

**작성일**: 2025-01-XX  
**목적**: README.md에 World Editor 및 최근 변경사항 반영 제안

---

## 현재 문제점

README.md는 **2025-10-21 기준**으로 작성되었으며, 그 이후의 **World Editor 개발이 거의 반영되지 않았습니다**.

### 누락된 주요 내용
1. World Editor 모듈 전체
2. 계층적 맵 구조 시스템
3. Entity/Dialogue/World Object 편집 기능
4. 프론트엔드 React + Konva.js 구현
5. 텍스트 어드벤처 게임 GUI 통합 계획

---

## 제안하는 업데이트

### 1. 프로젝트 진행 현황 섹션에 추가

```markdown
### ✅ **완료된 작업들** (기존 내용 유지)
- **데이터베이스 아키텍처**: 3계층 구조 (Game Data → Reference Layer → Runtime Data)
- **테이블 생성**: 40개 테이블 완성 (외래 키 제약조건 포함)
- **Effect Carrier 시스템**: 6가지 타입 (skill, buff, item, blessing, curse, ritual) 구현
- **데이터베이스 무결성**: 20개 테스트 모두 통과 (100% 성공률)
- **JSONB 처리**: 모든 JSONB 데이터 타입 문제 해결
- **성능 검증**: 5,000 레코드/초 삽입, 100,000 쿼리/초 조회
- **시나리오 테스트**: 6개 시나리오 모두 통과 (100% 성공률)
- **Phase 2 완료**: 동시 다중 세션, DialogueManager, ActionHandler, 성능 테스트
- **Phase 3 완료**: 100일 마을 시뮬레이션 성공 (228 대화, 833 행동)
- **최종 통합 테스트**: 모든 테스트 100% 통과
- **World Editor 구현**: ✅ 계층적 맵 구조, Entity/Dialogue 편집, 실시간 동기화 (2025-01-XX)

### 🔄 **현재 진행 상황 (2025-01-XX)**
- **Phase 1**: ✅ Entity-Cell 상호작용 완료
- **Phase 2**: ✅ 동시 다중 세션, DialogueManager, ActionHandler, 성능 테스트 완료
- **Phase 3**: ✅ 100일 마을 시뮬레이션 완료
- **Phase 4**: ✅ World Editor 기본 구조 완성 (진행 중)
  - 계층적 맵 뷰 (World → Region → Location → Cell)
  - Entity, World Object, Dialogue 시스템 편집
  - Cell Properties, Entity Properties JSON 편집
  - 실시간 동기화 (WebSocket)
- **Phase 5**: ⏳ 텍스트 어드벤처 게임 GUI 통합 (계획 중)
- **시스템 벤치마크**: ✅ 모든 성능 목표 달성
- **최종 통합 테스트**: ✅ 모든 테스트 통과
```

### 2. 새로운 섹션 추가: World Editor

```markdown
## 🗺️ **World Editor**

### 개요
World Editor는 **정적 게임 데이터(Game Data)를 시각적으로 편집하는 도구**입니다.
세션 데이터(Runtime Data)는 우선순위가 낮으며, 게임 세계의 구조와 콘텐츠를 편집하는 데 집중합니다.

### 주요 기능

#### 계층적 맵 구조
- **World Map**: Region 배치 및 관리
- **Region Map**: Location 배치 및 관리
- **Location Map**: Cell 배치 및 관리
- **Cell View**: Entity 및 World Object 관리

#### Entity 편집
- 기본 정보 (이름, 타입, 설명)
- 능력치, 장비, 인벤토리
- Entity Properties (JSON 편집)
- Dialogue Context/Topic 관리
- Effect Carriers 관리

#### World Object 편집
- Object 타입 및 속성
- 위치 및 크기
- 상호작용 타입 (openable, triggerable 등)
- Properties (JSON 편집)

#### Cell 편집
- Cell 정보 및 설명
- Cell Properties (환경, 지형, 조명 등)
- JSON 편집 모드 지원

#### 실시간 동기화
- WebSocket 기반 실시간 업데이트
- 다중 사용자 협업 지원

### 기술 스택
- **백엔드**: FastAPI (Python), PostgreSQL
- **프론트엔드**: React + TypeScript + Vite + Konva.js
- **통신**: REST API + WebSocket
- **포트**: 백엔드 8001, 프론트엔드 3000

### 실행 방법

#### 백엔드 서버 실행
```bash
cd app/world_editor
python run_server.py
# 또는
uvicorn app.world_editor.main:app --host 0.0.0.0 --port 8001 --reload
```

#### 프론트엔드 실행
```bash
cd app/world_editor/frontend
npm install
npm run dev
```

프론트엔드가 http://localhost:3000 에서 실행됩니다.

### 문서
- [World Editor 통합 로드맵](./docs/project-management/01_world_editor_integration_roadmap.md)
- [World Editor 구현 현황](./docs/onboarding/WORLD_EDITOR_IMPLEMENTATION_STATUS.md)
- [프론트엔드 QA 이슈](./docs/world-editor/50_frontend_qa_issues.md)
- [누락된 구현 사항](./docs/world-editor/52_missing_implementation_features.md)
- [Cell Properties 명세](./docs/world-editor/51_cell_properties_specification.md)
```

### 3. 프로젝트 구조 업데이트

```markdown
rpg_engine/
├── app/                      # 애플리케이션 코어
│   ├── core/                # 핵심 게임 로직
│   │   ├── game_manager.py  # 게임 전체 관리
│   │   ├── scenario_loader.py # 시나리오 로더
│   │   ├── scenario_executor.py # 시나리오 실행기
│   │   └── event_bus.py     # 이벤트 시스템
│   │
│   ├── world_editor/        # World Editor 모듈 (신규)
│   │   ├── main.py          # FastAPI 메인 앱
│   │   ├── schemas.py       # Pydantic 스키마
│   │   ├── routes/          # API 라우터
│   │   │   ├── regions.py
│   │   │   ├── locations.py
│   │   │   ├── cells.py
│   │   │   ├── entities.py
│   │   │   ├── dialogue.py
│   │   │   └── map_hierarchy.py
│   │   ├── services/        # 비즈니스 로직
│   │   │   ├── entity_service.py
│   │   │   ├── cell_service.py
│   │   │   ├── dialogue_service.py
│   │   │   ├── collision_service.py
│   │   │   └── map_hierarchy_service.py
│   │   └── frontend/        # React 프론트엔드
│   │       ├── src/
│   │       │   ├── components/
│   │       │   │   ├── HierarchicalMapView.tsx
│   │       │   │   ├── CellEntityManager.tsx
│   │       │   │   ├── EntityEditorModal.tsx
│   │       │   │   └── ...
│   │       │   ├── hooks/
│   │       │   ├── services/
│   │       │   └── types/
│   │       ├── package.json
│   │       └── vite.config.ts
│   │
│   ├── world/               # 게임 월드 관련
│   │   ├── cell.py         # 게임 셀 관리
│   │   ├── map.py          # 맵 시스템
│   │   └── navigation.py    # 이동 및 경로 찾기
│   │
│   ├── entity/             # 엔티티 시스템
│   │   ├── base.py         # 기본 엔티티 클래스
│   │   ├── character.py    # 캐릭터 관련
│   │   ├── npc.py         # NPC 관련
│   │   └── player.py       # 플레이어 관련
│   │
│   ├── interaction/        # 상호작용 시스템
│   │   ├── dialogue.py     # 대화 시스템
│   │   ├── combat.py       # 전투 시스템
│   │   └── trade.py        # 거래 시스템
│   │
│   └── ui/                 # 사용자 인터페이스
│       ├── components/     # UI 컴포넌트
│       └── screens/        # 게임 화면
│
├── database/               # 데이터베이스 관련
│   ├── connection.py       # DB 연결 관리
│   ├── repositories/      # 데이터 접근 계층
│   │   ├── game_data.py   # 게임 데이터 저장소
│   │   ├── runtime_data.py # 런타임 데이터 저장소
│   │   └── reference_layer.py # 참조 레이어 저장소
│   │
│   ├── factories/         # 객체 생성 팩토리
│   │   ├── game_data_factory.py    # 게임 데이터 생성
│   │   ├── instance_factory.py     # 인스턴스 생성
│   │   └── world_data_factory.py   # 계층적 세계 데이터 생성 (신규)
│   │
│   └── setup/             # 데이터베이스 설정
│       ├── mvp_schema.sql # MVP 스키마
│       └── migrations/    # 마이그레이션 스크립트
│           ├── add_entity_position_size.sql
│           ├── add_world_object_properties.sql
│           └── add_map_metadata_hierarchy.sql
```

### 4. 버전 업데이트 로그에 추가

```markdown
#### **v0.5.0** (2025-01-XX) - **World Editor 구현**
- **World Editor 기본 구조 완성**
  - 계층적 맵 뷰 시스템 (World → Region → Location → Cell)
  - Entity, World Object, Dialogue 시스템 편집
  - Cell Properties, Entity Properties JSON 편집
  - 실시간 동기화 (WebSocket)

- **데이터베이스 마이그레이션**
  - Entity 위치/크기 필드 추가 (`default_position_3d`, `entity_size`)
  - World Objects properties 필드 추가 (`wall_mounted`, `passable`, `movable`, dimensions, weight)
  - Map Metadata 계층 구조 필드 추가 (`map_level`, `parent_entity_id`, `parent_entity_type`)
  - Dialogue Context/Topic 시스템 완성

- **Factory 패턴 확장**
  - `WorldDataFactory` 구현
  - 계층적 데이터 일괄 생성 지원 (`create_region_with_children()`)
  - 레크레스타 상세 데이터 생성 (14 Locations, 16 Cells, 22 Entities, 21 World Objects)

- **프론트엔드 구현**
  - React + TypeScript + Konva.js 기반 맵 에디터
  - Entity Explorer, Entity Editor, Cell Editor
  - 계층적 네비게이션 및 브레드크럼
  - 핀 드래그, 레이어 분리, 실시간 동기화

- **서비스 레이어 구현**
  - `EntityService`, `CellService`, `DialogueService`
  - `CollisionService` (충돌 검사)
  - `MapHierarchyService` (계층적 맵 관리)

#### **v0.6.0** (예정) - **텍스트 어드벤처 게임 GUI**
- **게임 세션 API**
  - 세션 생성/조회/저장/복구
  - 액션 실행 API (`observe`, `investigate`, `examine` 등)
  - 게임 상태 관리

- **Novel Game Adventure GUI**
  - 텍스트 패널 (스토리 표시)
  - 액션 패널 (버튼 목록)
  - 상태 패널 (플레이어 상태, 위치 등)

- **Query Service**
  - 셀 관찰 (`observe_cell`)
  - 엔티티 조사 (`investigate_entity`)
  - 오브젝트 검사 (`examine_object`)
  - 가능한 액션 목록 조회
```

### 5. 다음 단계 섹션 업데이트

```markdown
### 🚀 다음 단계
- **World Editor 완성**: 메뉴 기능 구현, Entity Behavior Schedules 관리
- **텍스트 어드벤처 게임 GUI**: Novel game adventure 스타일 인터페이스
  - 관찰, 조사 등의 액션을 통한 세계 탐험
  - SELECT 쿼리 또는 API를 통한 결과값 받아오기
  - World Editor에서 편집한 데이터를 게임에서 즉시 사용
- **게임 세션 API**: World Editor 데이터를 게임에서 사용
- **액션 시스템**: ActionHandler와 통합하여 액션 결과를 텍스트 형식으로 변환
```

---

## 업데이트 우선순위

1. **높음**: World Editor 섹션 추가, 버전 로그 업데이트
2. **중간**: 프로젝트 구조 업데이트, 다음 단계 섹션 업데이트
3. **낮음**: 상세 기능 설명 추가

---

## 참고 문서

- [World Editor 구현 현황](./WORLD_EDITOR_IMPLEMENTATION_STATUS.md)
- [World Editor 통합 로드맵](../project-management/01_world_editor_integration_roadmap.md)
- [프론트엔드 QA 이슈](../world-editor/50_frontend_qa_issues.md)

