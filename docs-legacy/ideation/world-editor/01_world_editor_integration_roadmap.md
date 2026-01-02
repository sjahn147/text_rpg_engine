# World Editor 통합 및 확장 로드맵

## 프로젝트 개요

World Editor API와 Factory를 동기화하고, 계층별 맵 구조를 완전히 구현하며, Cell 엔티티 수준의 DB 구조를 재설계하는 종합 프로젝트입니다.

## 현재 상태 분석

### ✅ 완료된 작업

1. **World Editor 기본 구조**
   - Regions, Locations, Cells, Entities API 구현
   - World Objects, Effect Carriers, Items API 구현
   - Pin, Road, Map Metadata API 구현
   - 기본 프론트엔드 (World Map - Region 배치)

2. **설계 문서**
   - 계층적 맵 뷰 시스템 설계 (44번 문서)
   - Entity 위치/크기 시스템 설계 (47, 48번 문서)
   - World Objects 특성 시스템 설계 (49번 문서)
   - World Data Factory 설계 (51번 문서)

### ⚠️ 미완성 작업

1. **Factory 동기화**
   - `GameDataFactory`가 World Editor의 새로운 필드 미지원
   - `default_position_3d`, `entity_size` 미지원
   - World Objects의 새로운 properties 미지원
   - 계층적 구조 일괄 생성 미지원

2. **DB 마이그레이션**
   - `default_position_3d` 컬럼 미추가
   - `entity_size` 컬럼 미추가
   - World Objects properties 컬럼들 미추가
   - `map_metadata` 계층 구조 필드 미추가

3. **계층별 맵 구조**
   - Region Map (Location 배치) 미구현
   - Location Map (Cell 배치) 미구현
   - Cell 내 Entity 관리 UI 미완성

4. **Cell 엔티티 DB 구조**
   - Entity 위치 충돌 검사 로직 미구현
   - Entity 크기 기반 충돌 계산 미구현
   - World Objects와 Entity 간 상호작용 로직 미구현

## 프로젝트 목표

### 목표 1: Factory와 World Editor API 동기화
- Factory가 World Editor의 모든 필드 지원
- 계층적 구조 일괄 생성 지원
- ID 생성 규칙 통일

### 목표 2: DB 스키마 완성
- 모든 설계된 필드 마이그레이션
- 제약조건 및 인덱스 추가
- 데이터 무결성 보장

### 목표 3: 계층별 맵 구조 구현
- Region Map (Location 배치) 프론트엔드/API
- Location Map (Cell 배치) 프론트엔드/API
- Cell 내 Entity 관리 UI 완성

### 목표 4: Cell 엔티티 수준 DB 구조 재설계
- Entity 위치/크기 기반 충돌 검사
- World Objects와 Entity 상호작용
- 위치 기반 쿼리 최적화

## 작업 분류

### Phase 1: DB 스키마 마이그레이션 (기반 작업)
**우선순위: 최우선**  
**예상 기간: 1-2일**

#### 작업 1.1: Entity 필드 추가
- [ ] `default_position_3d` JSONB 컬럼 추가
- [ ] `entity_size` VARCHAR(20) 컬럼 추가 (제약조건 포함)
- [ ] 기본값 설정 및 기존 데이터 마이그레이션
- [ ] 인덱스 추가 (cell_id 기반 쿼리 최적화)

#### 작업 1.2: World Objects 필드 추가
- [ ] `wall_mounted`, `passable`, `movable` BOOLEAN 컬럼 추가
- [ ] `object_height`, `object_width`, `object_depth`, `object_weight` FLOAT 컬럼 추가
- [ ] 기본값 설정 및 타입별 기본값 로직

#### 작업 1.3: Map Metadata 확장
- [ ] `map_level` VARCHAR(20) 컬럼 추가
- [ ] `parent_entity_id`, `parent_entity_type` 컬럼 추가
- [ ] 인덱스 추가

#### 작업 1.4: 마이그레이션 스크립트 작성
- [ ] 롤백 가능한 마이그레이션 스크립트
- [ ] 데이터 검증 로직
- [ ] 마이그레이션 테스트

**산출물:**
- `database/setup/migrations/add_entity_position_size.sql`
- `database/setup/migrations/add_world_object_properties.sql`
- `database/setup/migrations/add_map_metadata_hierarchy.sql`
- `database/setup/migrations/run_all_migrations.py`

---

### Phase 2: Factory 업데이트 및 동기화
**우선순위: 높음**  
**예상 기간: 2-3일**

#### 작업 2.1: GameDataFactory 확장
- [ ] `create_entity()` 메서드에 `default_position_3d`, `entity_size` 지원
- [ ] `create_world_object()` 메서드에 새로운 properties 지원
- [ ] 기존 메서드들 업데이트 (하위 호환성 유지)

#### 작업 2.2: WorldDataFactory 구현
- [ ] `WorldDataFactory` 클래스 생성
- [ ] `create_region_with_children()` 메서드 구현
  - Region 생성
  - Location들 일괄 생성
  - Cell들 일괄 생성
  - Character들 일괄 생성
  - World Objects 일괄 생성
- [ ] 트랜잭션 처리 (전체 성공 또는 전체 롤백)
- [ ] ID 생성 규칙 자동 적용

#### 작업 2.3: world_design.md 파서 구현
- [ ] Markdown 파서 (Region 구조 추출)
- [ ] 설정 데이터 구조 변환
- [ ] 검증 로직

#### 작업 2.4: Factory 테스트
- [ ] 단위 테스트 (각 메서드)
- [ ] 통합 테스트 (계층적 생성)
- [ ] world_design.md 실제 데이터로 테스트

**산출물:**
- `database/factories/world_data_factory.py`
- `database/factories/parsers/world_design_parser.py`
- `tests/database/factories/test_world_data_factory.py`
- `tests/database/factories/test_world_design_parser.py`

---

### Phase 3: Cell 엔티티 수준 DB 구조 재설계
**우선순위: 높음**  
**예상 기간: 2-3일**

#### 작업 3.1: Entity 위치 충돌 검사 로직
- [ ] `check_position_collision()` 함수 구현
- [ ] Entity 크기 기반 충돌 반경 계산
- [ ] 같은 Cell 내 다른 Entity들과의 충돌 검사
- [ ] World Objects와의 충돌 검사

#### 작업 3.2: 위치 기반 쿼리 최적화
- [ ] Cell 내 Entity 목록 조회 (위치 정렬)
- [ ] 특정 영역 내 Entity 조회
- [ ] 인덱스 최적화 (GIN 인덱스 for JSONB)

#### 작업 3.3: World Objects와 Entity 상호작용
- [ ] `can_entity_pass_through()` 로직
- [ ] `can_entity_move_object()` 로직
- [ ] `validate_wall_mounted_placement()` 로직

#### 작업 3.4: API 엔드포인트 추가
- [ ] `POST /api/entities/check-collision` - 충돌 검사
- [ ] `GET /api/entities/cell/{cell_id}/by-position` - 위치 기반 조회
- [ ] `PUT /api/entities/{id}/position` - 위치 업데이트 (충돌 검사 포함)

**산출물:**
- `app/world_editor/services/collision_service.py`
- `app/world_editor/services/position_service.py`
- `app/world_editor/routes/entity_position.py`
- `tests/world_editor/test_collision_service.py`

---

### Phase 4: 계층별 맵 구조 API 구현
**우선순위: 중간**  
**예상 기간: 3-4일**

#### 작업 4.1: Region Map API
- [ ] `GET /api/maps/region/{region_id}` - Region Map 메타데이터 조회
- [ ] `GET /api/maps/region/{region_id}/locations` - Region 내 Location 목록 (위치 포함)
- [ ] `POST /api/maps/region/{region_id}/locations` - Location 배치
- [ ] `PUT /api/maps/region/{region_id}/locations/{location_id}/position` - Location 위치 업데이트

#### 작업 4.2: Location Map API
- [ ] `GET /api/maps/location/{location_id}` - Location Map 메타데이터 조회
- [ ] `GET /api/maps/location/{location_id}/cells` - Location 내 Cell 목록 (위치 포함)
- [ ] `POST /api/maps/location/{location_id}/cells` - Cell 배치
- [ ] `PUT /api/maps/location/{location_id}/cells/{cell_id}/position` - Cell 위치 업데이트

#### 작업 4.3: Map Metadata 서비스 확장
- [ ] 계층 구조 지원 (`map_level`, `parent_entity_id`)
- [ ] 맵 레벨별 메타데이터 관리
- [ ] 기본 맵 설정 (커스텀 맵 없을 때)

**산출물:**
- `app/world_editor/services/map_hierarchy_service.py`
- `app/world_editor/routes/map_hierarchy.py`
- `tests/world_editor/test_map_hierarchy.py`

---

### Phase 5: 계층별 맵 구조 프론트엔드 구현
**우선순위: 중간**  
**예상 기간: 4-5일**

#### 작업 5.1: Region Map UI
- [ ] Region 선택 시 Region Map 뷰로 전환
- [ ] Location 핀 배치 및 드래그
- [ ] Location 정보 패널
- [ ] Location 간 연결선 (Road)

#### 작업 5.2: Location Map UI
- [ ] Location 선택 시 Location Map 뷰로 전환
- [ ] Cell 핀 배치 및 드래그
- [ ] Cell 정보 패널
- [ ] Cell 간 연결선

#### 작업 5.3: Cell 내 Entity 관리 UI
- [ ] Cell 선택 시 Entity 목록 표시
- [ ] Entity 위치 편집 (2D 그리드)
- [ ] Entity 크기 표시 및 편집
- [ ] 충돌 경고 표시
- [ ] World Objects 위치 편집

#### 작업 5.4: 네비게이션 UI
- [ ] 계층 구조 브레드크럼
- [ ] 상위 레벨로 돌아가기 버튼
- [ ] 현재 레벨 표시

**산출물:**
- `app/world_editor/frontend/src/components/RegionMapView.tsx`
- `app/world_editor/frontend/src/components/LocationMapView.tsx`
- `app/world_editor/frontend/src/components/CellEntityManager.tsx`
- `app/world_editor/frontend/src/components/MapNavigation.tsx`

---

### Phase 6: 통합 및 테스트
**우선순위: 높음**  
**예상 기간: 2-3일**

#### 작업 6.1: 통합 테스트
- [ ] Factory → API → DB 전체 플로우 테스트
- [ ] 계층적 맵 구조 전체 플로우 테스트
- [ ] Cell 엔티티 관리 전체 플로우 테스트

#### 작업 6.2: 성능 최적화
- [ ] 쿼리 최적화 (인덱스 활용)
- [ ] 프론트엔드 렌더링 최적화
- [ ] 대용량 데이터 처리 테스트

#### 작업 6.3: 문서화
- [ ] API 문서 업데이트
- [ ] 사용자 가이드 작성
- [ ] 개발자 가이드 작성

**산출물:**
- `tests/integration/test_world_editor_full_flow.py`
- `docs/world-editor/API_REFERENCE.md`
- `docs/world-editor/USER_GUIDE.md`

---

## 의존성 관계

```
Phase 1 (DB 마이그레이션)
    ↓
Phase 2 (Factory 업데이트) ← Phase 3 (Cell 엔티티 DB 구조) (병렬 가능)
    ↓                           ↓
Phase 4 (계층별 맵 API) ←────────┘
    ↓
Phase 5 (프론트엔드)
    ↓
Phase 6 (통합 및 테스트)
```

## 최적의 로드맵

### Week 1: 기반 작업
- **Day 1-2**: Phase 1 완료 (DB 마이그레이션)
- **Day 3-5**: Phase 2 시작 (Factory 업데이트)

### Week 2: 핵심 기능 구현
- **Day 1-3**: Phase 2 완료 (Factory 완성)
- **Day 4-5**: Phase 3 시작 (Cell 엔티티 DB 구조)

### Week 3: 계층 구조 구현
- **Day 1-3**: Phase 3 완료 (Cell 엔티티 DB 구조)
- **Day 4-5**: Phase 4 시작 (계층별 맵 API)

### Week 4: 프론트엔드 및 통합
- **Day 1-3**: Phase 4 완료 (계층별 맵 API)
- **Day 4-5**: Phase 5 시작 (프론트엔드)

### Week 5: 완성 및 테스트
- **Day 1-3**: Phase 5 완료 (프론트엔드)
- **Day 4-5**: Phase 6 완료 (통합 및 테스트)

**총 예상 기간: 5주 (25일)**

## 리스크 관리

### 리스크 1: DB 마이그레이션 실패
- **대응**: 롤백 스크립트 준비, 단계별 마이그레이션

### 리스크 2: world_design.md 파싱 복잡성
- **대응**: 점진적 파싱 (Region → Location → Cell 순서)

### 리스크 3: 프론트엔드 성능 이슈
- **대응**: 가상화 스크롤, 레이지 로딩 적용

### 리스크 4: 충돌 검사 로직 복잡성
- **대응**: 단순화된 충돌 검사부터 시작, 점진적 개선

## 성공 기준

1. ✅ Factory가 World Editor의 모든 필드 지원
2. ✅ world_design.md를 파싱하여 DB에 일괄 생성 가능
3. ✅ Region → Location → Cell 계층 구조 완전 구현
4. ✅ Cell 내 Entity 위치 관리 및 충돌 검사 작동
5. ✅ 모든 기능에 대한 테스트 커버리지 80% 이상

## 다음 단계

1. Phase 1 작업 시작 (DB 마이그레이션)
2. 각 Phase별 상세 설계 문서 작성
3. 일일 스탠드업 및 진행 상황 추적

