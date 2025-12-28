# RPG Engine Architecture & RPG-Specific Standards

> **최신화 날짜**: 2025-12-28

본 문서는 RPG Engine의 아키텍처 원칙과 RPG 특화 운영 규약을 정의합니다. 인간 가독성을 위해 한국어로 작성하되, 표기 정확성을 위해 일부 용어는 영어를 병기합니다.

## 1. Architectural Principles

- Layered Architecture (3-Tier)
  - UI Layer → Business Logic → Data Layer
  - 상위→하위 단방향 의존, 인터페이스 의존 및 생성자 주입 권장

- Dependency Direction
  - UI는 Business Logic에만 의존, Data Layer는 인터페이스로 노출
  - 전역 상태 금지, 의존성 주입으로 테스트 가능성 확보

- Data Flow
  - Input → Validation → Domain Logic → Persistence → Output
  - 출력은 직렬화 가능한 DTO로 수렴, 외부로는 불변 스냅샷을 노출

- Priority & Scope (요약)
  - MUST: 타입 안전, 비동기 I/O, 테스트 선행, DB 안전(백업/컨펌)
  - SHOULD: Enum/Literal 제한, CI 자동화, 구조화 로깅
  - MAY: 고급 최적화/정적 분석 확장
  - Scope: runtime | tooling | both

참조: `docs/rules/01_RULES_03_RULES_CODING_CONVENTIONS.md`, `docs/rules/03_DECISION_TREE.md`, `docs/rules/04_QUALITY_RULES.yml`

## 2. RPG-Specific Standards

### 2.1 Game Loop (Tick/Frame)

- Tick 경계 규약
  - Tick 내부: 성능이 임계인 hot path는 “제어된 지역 가변(local mutation)” 허용
  - Tick 종료: 외부로 노출되는 상태는 불변 스냅샷(immutable snapshot)으로 커밋
  - 프레임 예산: 기본 16ms@60fps(가이드). 초과 시 경고 로그와 디그레이드 경로 선택

- 상태 업데이트 순서 예시
  1) 입력 수집 → 2) 검증 → 3) 도메인 업데이트 → 4) 이벤트/체인지셋 생성 → 5) 스냅샷 생성/커밋 → 6) UI/네트워크 반영

- 동시성
  - 동일 Tick 내 공유 데이터 접근은 파인 그레인 락/세마포어 혹은 단일 스레드 업데이트 큐로 일관성 확보

### 2.2 State Propagation (World → UI → Network)

- 단방향 데이터 흐름
  - World(도메인) → ViewModel/DTO → UI/Network
  - UI/Network는 명시적인 커맨드/이벤트로만 도메인을 간접 제어

- 스냅샷 동기화
  - 스냅샷 ID와 버전으로 적용/롤백 관리
  - 부분 적용 실패 시 이전 스냅샷으로 롤백 가능해야 함

### 2.3 Performance Policy

- GC/할당
  - 프레임 내 힙 할당 상한 권고, 단기 객체는 풀(Object Pool) 사용 고려(MAY)
  - 구조적 공유(Structural Sharing) 가능한 불변 자료구조 선호, 불가 시 Tick 내부 지역 가변

- 캐시 전략
  - 엔티티 인덱스: 이름/영역/셀/타입별 인덱스 유지
  - AI/경로 탐색: LRU 캐시, TTL, 배치 업데이트
  - 공간 인덱싱: 그리드/쿼드트리 등 선택

- 측정과 가드레일
  - 핵심 시스템에 타이머/카운터 삽입, SLA 초과 시 경고 및 fallbacks 활성화

### 2.4 Resource Management (Texture/Audio/Script)

- 로딩 정책
  - 비동기 프리페치, 콘텐츠 주소(해시) 기반 캐싱, 중복 로딩 방지
  - Dev: 핫리로드 허용, Prod: 해시 확인 후 교체

- 수명주기
  - 참조 카운팅 또는 명시적 언로드 API로 메모리 회수

### 2.5 Save/Load (Snapshot Integrity & Versioning)

- 무결성
  - 원자적 쓰기: 임시 파일 → fsync → 스왑
  - 체크섬/해시로 파일 손상 탐지

- 버전 호환
  - 스키마 버전 포함, 마이그레이션 파이프라인 제공(tooling 범위)
  - 부분 복구 전략: 손상 세그먼트 무시, 기본값 대치, 로그 보고

## 3. Runtime vs Tooling Split

- Runtime (frame/tick-bound)
  - 메모리 우선, DB 접근 금지(사전 프리로드/캐시 사용)
  - 불변성: 외부 경계에서 강제, Tick 내부는 지역 가변 허용
  - 테스트: 시뮬레이션/프로퍼티/골든 스냅샷 테스트를 1급 시민으로 인정

- Tooling (editor/data/DB)
  - 스키마 선행, 백업/컨펌 MUST, 문자열 SQL 금지
  - 100% 타입 안전 + TDD 엄격 적용

## 4. Testing Guidance for RNG/AI/Simulation

- Determinism Options
  - Fixed seed per test case (document seed); reproduce failures by logging seed
  - Golden snapshot comparison for aggregate/observable outcomes
  - Property-based tests for invariants (e.g., health ≥ 0, resource conservation)

- Statistical/Simulation Tests
  - Run N simulations (e.g., N ≥ 1,000) and assert distributions within tolerance
  - Use confidence intervals or KS-test where applicable (MAY)
  - Record summary metrics (mean/variance/percentiles) to detect regressions

- Scenario Tests
  - Decide pass/fail on observable outcomes; avoid coupling to internal steps
  - Prefer DTO/snapshot assertions over internal mutable state

- Logging & Reproducibility
  - Log test metadata: seed, RNG engine version, scenario id
  - Store failing snapshots for triage; attach to CI artifacts

참조: `docs/rules/02_WORKFLOW_TDD.md`

## 5. Governance & Links

- 차단(Blocking) 기준은 MUST만 해당: `docs/rules/04_QUALITY_RULES.yml`
- 충돌 해결 트리: `docs/rules/03_DECISION_TREE.md`
- 코딩 규약 요약: `docs/CONVENTION.md`


