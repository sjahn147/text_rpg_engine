# UI 리디자인 구현 TODO

> **최신화 날짜**: 2026-01-03  
> **참고 문서**: `docs/design/UI_REDESIGN_BG3_STYLE.md`, `docs/design/UI_REDESIGN_BG3_STYLE_FEASIBILITY_REVIEW.md`, `docs/design/UI_REDESIGN_BG3_STYLE_SYSTEM_INTEGRATION.md`

## ⚠️ 중요: 구현 전 필수 읽기

- `00_CORE/01_PHILOSOPHY.md`: 핵심 개발 철학
- `00_CORE/02_ARCHITECTURE_PRINCIPLES.md`: 아키텍처 설계 원칙
- `01_TYPE_SAFETY/UUID_GUIDELINES.md`: UUID 사용법 (uuid_helper.py 필수)
- `01_TYPE_SAFETY/TRANSACTION_GUIDELINES.md`: 트랜잭션 사용법
- `03_SYSTEMS/EFFECT_CARRIER_GUIDELINES.md`: Effect Carrier 시스템
- `03_SYSTEMS/ABILITIES_SYSTEM_GUIDELINES.md`: 스킬/주문 시스템
- `database/setup/mvp_schema.sql`: 데이터베이스 스키마 참조 필수

## 1. 백엔드 API 엔드포인트 추가

### 1.1 캐릭터 관련 API

- [ ] `/api/gameplay/character/stats/{session_id}`: 캐릭터 능력치 조회
- [ ] `/api/gameplay/character/inventory/{session_id}`: 인벤토리 및 장착 아이템 조회 (Effect Carrier 포함)
  - **참고**: `03_SYSTEMS/EFFECT_CARRIER_GUIDELINES.md` - 아이템 기반 Effect Carrier
  - **주의**: `items.effect_carrier_id` FK 확인 필요 (스키마에 없을 수 있음)
- [ ] `/api/gameplay/character/equipped/{session_id}`: 장착 아이템 조회 (Effect Carrier 포함)
- [ ] `/api/gameplay/character/applied-effects/{session_id}`: 적용 중인 Effect Carrier 조회
  - **참고**: `reference_layer.entity_effect_ownership` 테이블 활용
  - **참고**: `03_SYSTEMS/EFFECT_CARRIER_GUIDELINES.md` - 적용 중인 Effect Carrier
- [ ] `/api/gameplay/character/abilities/{session_id}`: 엔티티의 스킬/주문 목록 조회
  - **참고**: `entities.default_abilities` JSONB 필드 파싱
  - **참고**: `03_SYSTEMS/ABILITIES_SYSTEM_GUIDELINES.md`
- [ ] `/api/gameplay/character/spells/{session_id}`: 주문 목록 조회 (`abilities_magic` 테이블 기반)

### 1.2 오브젝트 관련 API

- [ ] `/api/gameplay/object/{object_id}/state`: 오브젝트 상태 조회
  - **참고**: `ObjectStateManager` 활용
  - **주의**: 상태 아이콘 매핑 규칙 정의 필요
- [ ] `/api/gameplay/object/{object_id}/actions`: 가능한 액션 조회 (상태 기반)
  - **주의**: 상태 전이 버튼 표시 로직 정의 필요

### 1.3 액션 관련 API

- [ ] `/api/gameplay/actions/categorized/{session_id}`: 카테고리별 액션 조회
  - **주의**: ActionType 카테고리화 로직 정의 필요
  - **주의**: 카테고리별 아이콘 매핑 규칙 정의 필요

### 1.4 퀘스트 관련 API

- [ ] `/api/gameplay/quests/{session_id}`: 퀘스트 목록 조회
  - **주의**: `runtime_data.quests` 테이블 생성 필요 (현재 스키마에 없을 수 있음)
  - **참고**: `triggered_events` 테이블의 `event_type='quest'` 활용 가능
- [ ] `/api/gameplay/quests/{session_id}/events`: 퀘스트 이벤트 조회
  - **참고**: `triggered_events` 테이블, `event_type LIKE 'QUEST_%'` 필터링

### 1.5 저널 관련 API (신규)

- [ ] `/api/gameplay/journal/{session_id}`: 저널 데이터 조회 (통합)
- [ ] `/api/gameplay/journal/story/{session_id}`: 이야기 히스토리 조회
  - **참고**: `triggered_events`, `action_logs` 테이블 활용
- [ ] `/api/gameplay/journal/discoveries/{session_id}`: 발견한 정보 조회
  - **참고**: `discoveredObjects`, `discoveredCells` Set 활용
- [ ] `/api/gameplay/journal/characters/{session_id}`: 만난 NPC 목록 및 대화 히스토리
  - **참고**: `dialogue_history` 테이블 활용
- [ ] `/api/gameplay/journal/locations/{session_id}`: 방문한 셀/위치 목록
  - **참고**: `discoveredCells` Set 활용

### 1.6 맵 관련 API (신규)

- [ ] `/api/gameplay/map/{session_id}`: 맵 데이터 조회 (계층적 구조: 지역 → 위치 → 셀)
- [ ] `/api/gameplay/map/discovered/{session_id}`: 발견한 셀 목록 조회
  - **참고**: `discoveredCells` Set 활용

### 1.7 탐험 관련 API (신규)

- [ ] `/api/gameplay/exploration/{session_id}`: 탐험 진행도 조회
  - **참고**: 발견한 셀 수 / 전체 셀 수 계산

### 1.8 시간 관련 API (신규)

- [ ] `/api/gameplay/time/{session_id}`: 현재 게임 시간 조회
  - **참고**: `TimeSystem` 연동
  - **참고**: `03_SYSTEMS/TIME_SYSTEM_GUIDELINES.md`

### 1.9 3D 공간 및 물리 관련 API (신규, 향후)

- [ ] `/api/gameplay/move/keyboard`: 키보드 이동 처리
- [ ] `/api/gameplay/npc/movement/{session_id}`: NPC 이동 상태 조회
- [ ] `/api/gameplay/collision/check`: 충돌 감지
- [ ] `/api/gameplay/collision/constraints/{session_id}`: 충돌 제약 조회
- [ ] `/api/gameplay/npc/interaction/check`: NPC 상호작용 가능 여부 확인
- [ ] `/api/gameplay/npc/interaction/trigger`: NPC 주도 상호작용 트리거

### 1.10 전투 관련 API (향후)

- [ ] `/api/gameplay/combat/{session_id}`: 전투 관련 API (향후 구현)

## 2. Service Layer 추가

### 2.1 필수 Service

- [ ] `CharacterService` 생성 (`app/services/gameplay/character_service.py`)
  - **참고**: `00_CORE/02_ARCHITECTURE_PRINCIPLES.md` - Service 계층 원칙
  - **참고**: `BaseGameplayService` 상속
  - **기능**: 캐릭터 능력치, 인벤토리, 장착 아이템, Effect Carrier, 스킬/주문 조회

- [ ] `JournalService` 생성 (`app/services/gameplay/journal_service.py`)
  - **기능**: 저널 데이터 통합 조회 (퀘스트/이야기/발견/인물/장소)

- [ ] `MapService` 생성 (`app/services/gameplay/map_service.py`)
  - **기능**: 맵 데이터 조회, 발견한 셀 목록 조회

- [ ] `ExplorationService` 생성 (`app/services/gameplay/exploration_service.py`)
  - **기능**: 탐험 진행도 계산

### 2.2 향후 Service

- [ ] `PhysicsService` 생성 (3D 공간 및 물리 시스템)
- [ ] `NPCMovementService` 생성 (NPC 이동 관리)

## 3. 데이터베이스 스키마 추가

### 3.1 필수 스키마

- [ ] `runtime_data.quests` 테이블 생성
  - **참고**: `docs/design/UI_REDESIGN_BG3_STYLE.md` - 퀘스트 저장 구조
  - **참고**: `triggered_events` 테이블의 `event_type='quest'` 활용 가능
  - **주의**: `mvp_schema.sql` 참조 필수

- [ ] `items.effect_carrier_id` FK 추가 (스키마에 없을 경우)
  - **참고**: `docs/design/UI_REDESIGN_BG3_STYLE_FEASIBILITY_REVIEW.md` - 아이템/장비와 Effect Carrier 연결 방식
  - **주의**: Data-Centric Development 원칙 준수

- [ ] `equipment_weapons.effect_carrier_id` FK 추가 (스키마에 없을 경우)
- [ ] `equipment_armors.effect_carrier_id` FK 추가 (스키마에 없을 경우)

### 3.2 향후 스키마

- [ ] `game_data.character_classes`: 캐릭터 클래스 (D&D 스타일)
- [ ] `game_data.skills`: 스킬 정의 (D&D 5e 스킬)
- [ ] `game_data.spells`: 주문 정의 (D&D 스타일)
- [ ] `game_data.quest_templates`: 퀘스트 템플릿 (정적 데이터)
- [ ] `runtime_data.character_progression`: 레벨 및 경험치

## 4. 프론트엔드 컴포넌트 구현

### 4.1 Phase 1: 레이아웃 구조 재구성

- [ ] `ActionBar` 컴포넌트 생성 (하단 액션 바)
- [ ] `CharacterStatusPanel` 컴포넌트 생성 (캐릭터 상태 패널)
- [ ] `DialoguePanel` 컴포넌트 생성 (대화 패널 재구성)
- [ ] `MinimapPanel` 컴포넌트 생성 (미니맵 패널)
- [ ] 기존 사이드바 제거 및 정보 통합

### 4.2 Phase 2: D&D 기능 추가

- [ ] 캐릭터 시트 구현 (능력치, 스킬, 레벨)
- [ ] 스킬 시스템 UI 통합 (`default_abilities.skills` 기반)
  - **참고**: `03_SYSTEMS/ABILITIES_SYSTEM_GUIDELINES.md`
- [ ] 주문 시스템 UI 통합 (`default_abilities.magic` 기반)
  - **참고**: `03_SYSTEMS/ABILITIES_SYSTEM_GUIDELINES.md`
- [ ] 퀘스트 저널 구현
  - **참고**: `runtime_data.quests` 테이블 또는 `triggered_events` 테이블 활용

### 4.3 Phase 3: UX 개선

- [ ] 퀵슬롯 시스템 구현
- [ ] 인벤토리 개선
- [ ] 미니맵 개선
- [ ] 전투 시스템 UI 구현

### 4.4 Phase 4: 스토리텔링 강화

- [ ] 저널 시스템 구현
  - [ ] 저널 패널 (퀘스트/이야기/발견/인물/장소 탭)
  - [ ] 검색/필터 기능
- [ ] 맵 시스템 구현
  - [ ] 전체 맵 뷰
  - [ ] 발견한 셀 표시
  - [ ] 퀘스트 마커
- [ ] 시간/날짜 UI 통합
  - **참고**: `TimeSystem` 연동
  - **참고**: `03_SYSTEMS/TIME_SYSTEM_GUIDELINES.md`
- [ ] 탐험/발견 시스템 구현
  - [ ] 탐험 진행도 표시
  - [ ] 발견한 정보 추적 및 시각화

### 4.5 Phase 5: 접근성 및 편의 기능

- [ ] 키보드 단축키 통합
- [ ] 툴팁 시스템 구현
- [ ] 설정 메뉴 통합
- [ ] 세이브/로드 UI 통합

### 4.6 Phase 6: 3D 공간 및 물리 (향후)

- [ ] Three.js 도입 검토
- [ ] 3D 렌더링 구현
- [ ] 키보드 이동 처리
- [ ] NPC 실시간 이동 표시
- [ ] 충돌 시스템 통합
- [ ] NPC 주도 상호작용 구현

## 5. Effect Carrier UI 통합

### 5.1 데이터 구조 정의

- [ ] Effect Carrier의 `effect_json` 구조 스키마 정의
- [ ] Effect Carrier 표시 데이터 구조 정의
- [ ] UI 표시를 위한 API 응답 형식 정의

### 5.2 UI 통합

- [ ] 아이템 기반 Effect Carrier 표시 (인벤토리/장착 아이템)
- [ ] 적용 중인 Effect Carrier 표시 (`entity_effect_ownership` 테이블)
- [ ] Effect Carrier 아이콘 매핑 규칙 정의

## 6. Object State Manager UI 통합

### 6.1 API 엔드포인트

- [ ] 오브젝트 상태 조회 API 엔드포인트 명시 (이미 TODO에 포함)

### 6.2 UI 통합

- [ ] 상태 아이콘 매핑 규칙 정의
- [ ] 상태 전이 버튼 표시 로직 정의
- [ ] 상태 조건 표시 로직 정의

## 7. ActionType 카테고리화 로직

### 7.1 카테고리 정의

- [ ] ActionType 카테고리 정의 및 매핑 규칙
- [ ] 카테고리별 아이콘 매핑 규칙
- [ ] 액션 바에서 카테고리별 그룹화 방법

## 8. 프론트엔드 상태 관리 확장

### 8.1 Zustand Store 확장

- [ ] `characterStats`: 능력치, 스킬, 레벨
- [ ] `spells`: 주문 목록 및 슬롯
- [ ] `quests`: 퀘스트 목록 및 진행도
- [ ] `quickSlots`: 퀵슬롯 아이템
- [ ] `journal`: 저널 데이터 (퀘스트, 이야기, 발견, 인물, 장소)
- [ ] `discoveredCells`: 발견한 셀 Set
- [ ] `discoveredEntities`: 발견한 엔티티 Set
- [ ] `storyHistory`: 이야기 히스토리 (주요 이벤트, 선택한 분기)
- [ ] `mapData`: 전체 맵 데이터 (계층적 구조)
- [ ] `currentLocation`: 현재 위치 정보
- [ ] `gameTime`: 현재 게임 시간 (`TimeSystem` 연동)
- [ ] `explorationProgress`: 탐험 진행도 (발견한 셀 수 / 전체 셀 수)

### 8.2 API 연동

- [ ] `gameApi.ts`에 새로운 API 메서드 추가
- [ ] 모든 새로운 API 엔드포인트 연동

## 9. 테스트

### 9.1 백엔드 테스트

- [ ] 모든 새로운 API 엔드포인트 테스트
- [ ] Service Layer 테스트
- [ ] Effect Carrier 통합 테스트
- [ ] 스킬/주문 시스템 통합 테스트
- [ ] 퀘스트 시스템 통합 테스트
- [ ] 저널 시스템 통합 테스트
- [ ] 맵 시스템 통합 테스트
- [ ] 시간 시스템 UI 통합 테스트
- [ ] 탐험 시스템 통합 테스트

### 9.2 프론트엔드 테스트

- [ ] 모든 새로운 컴포넌트 렌더링 테스트
- [ ] 상태 관리 테스트
- [ ] API 연동 테스트
- [ ] 사용자 플로우 테스트

## 10. 문서화

### 10.1 가이드라인 문서

- [ ] `03_SYSTEMS/QUEST_SYSTEM_GUIDELINES.md` 생성 (퀘스트 시스템 가이드라인)
- [ ] `03_SYSTEMS/JOURNAL_SYSTEM_GUIDELINES.md` 생성 (저널 시스템 가이드라인)
- [ ] `03_SYSTEMS/MAP_SYSTEM_GUIDELINES.md` 생성 (맵 시스템 가이드라인)
- [ ] `03_SYSTEMS/EXPLORATION_SYSTEM_GUIDELINES.md` 생성 (탐험 시스템 가이드라인)
- [ ] `04_DEVELOPMENT/UI_COMPONENT_GUIDELINES.md` 생성 (UI 컴포넌트 개발 가이드라인)
- [ ] `04_DEVELOPMENT/API_DESIGN_GUIDELINES.md` 생성 (API 설계 가이드라인)

### 10.2 기존 문서 업데이트

- [ ] `03_SYSTEMS/EFFECT_CARRIER_GUIDELINES.md`: Effect Carrier UI 통합 방법 추가
- [ ] `03_SYSTEMS/ABILITIES_SYSTEM_GUIDELINES.md`: 스킬/주문 UI 통합 방법 추가

## 11. 우선순위별 구현 계획

### 우선순위 1 (즉시 구현)

1. ✅ 하단 액션 바 생성
2. ✅ 사이드바 제거 및 정보 통합
3. ✅ 캐릭터 상태 패널 (기본)
4. ✅ 대화 패널 재구성
5. ✅ 미니맵 패널 (기본)

### 우선순위 2 (기능 확장)

1. 캐릭터 시트 구현
2. 스킬 시스템 구현
3. 주문 시스템 구현
4. 퀘스트 저널 구현

### 우선순위 3 (UX 개선)

1. 퀵슬롯 시스템
2. 인벤토리 개선
3. 미니맵 개선
4. 전투 시스템 구현

### 우선순위 4 (스토리텔링 강화)

1. 저널 시스템
2. 맵 시스템
3. 시간/날짜 UI
4. 탐험/발견 시스템

### 우선순위 5 (접근성 및 편의 기능)

1. 키보드 단축키 통합
2. 툴팁 시스템
3. 설정 메뉴 통합
4. 세이브/로드 UI 통합

## 12. 참고 문서

- `docs/design/UI_REDESIGN_BG3_STYLE.md`: 전체 기획안
- `docs/design/UI_REDESIGN_BG3_STYLE_FEASIBILITY_REVIEW.md`: 타당성 검토
- `docs/design/UI_REDESIGN_BG3_STYLE_SYSTEM_INTEGRATION.md`: 시스템 통합 가이드
- `docs/design/UI_REDESIGN_BG3_STYLE_CORRECTIONS.md`: 수정 사항
- `docs/design/UI_REDESIGN_BG3_STYLE_GAME_DESIGNER_REVIEW.md`: 게임 디자이너 검토

