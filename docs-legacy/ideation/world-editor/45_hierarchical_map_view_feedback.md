# 계층적 맵 뷰 시스템 설계 피드백

**⚠️ 이 문서는 [44. 계층적 맵 뷰 시스템 설계 (최종안)](./44_hierarchical_map_view_design.md)에 통합되었습니다.**

이 문서는 설계 초기 단계의 피드백을 담고 있으며, 최종 결정 사항은 44번 문서를 참조하세요.

## 검토자 관점
- 선임 게임 디자이너
- 선임 게임 개발자

## 전체 평가

### ✅ 강점
1. **명확한 계층 구조**: World → Region → Location → Cell의 계층이 직관적
2. **2D/3D 하이브리드**: 적절한 레벨에서 적절한 뷰 타입 사용
3. **Lego Creator 스타일**: Cell 레벨의 3D 블록 배치는 시각적으로 효과적

### ⚠️ 개선 필요 사항

## 1. 데이터 모델 설계

### 문제점 1: 맵 메타데이터 중복 가능성
**현재 설계**: 각 Region/Location마다 별도 `map_metadata` 레코드
**문제**: 
- Region이 100개면 맵 메타데이터도 100개
- Location이 1000개면 맵 메타데이터도 1000개
- 대부분의 맵이 기본 설정만 사용할 경우 불필요한 데이터

**개선안**:
```sql
-- 옵션 1: 기본값 사용, 커스텀 맵만 별도 저장
CREATE TABLE game_data.map_metadata (
    map_id VARCHAR(50) PRIMARY KEY,
    map_level VARCHAR(20) NOT NULL,
    parent_entity_id VARCHAR(50),
    parent_entity_type VARCHAR(20),
    -- 기본값은 NULL, NULL이면 시스템 기본값 사용
    map_name VARCHAR(100),
    background_image VARCHAR(255),
    width INTEGER,
    height INTEGER,
    -- ...
);

-- 옵션 2: 맵 템플릿 시스템
CREATE TABLE game_data.map_templates (
    template_id VARCHAR(50) PRIMARY KEY,
    template_name VARCHAR(100),
    map_level VARCHAR(20),
    default_settings JSONB
);

-- map_metadata는 템플릿 참조
ALTER TABLE game_data.map_metadata
ADD COLUMN template_id VARCHAR(50) REFERENCES game_data.map_templates(template_id);
```

### 문제점 2: Cell 3D 레이아웃 저장 위치
**현재 설계**: `cell_properties` JSONB 또는 별도 테이블
**문제**:
- JSONB는 검색/인덱싱이 어려움
- 블록이 많아지면 JSONB 크기가 커짐
- 블록별 쿼리가 불가능

**개선안**:
```sql
-- 별도 테이블로 구조화
CREATE TABLE game_data.cell_3d_blocks (
    block_id VARCHAR(50) PRIMARY KEY,
    cell_id VARCHAR(50) NOT NULL,
    block_type VARCHAR(20) NOT NULL,
    position_x DECIMAL(10, 2) NOT NULL,
    position_y DECIMAL(10, 2) NOT NULL,
    position_z DECIMAL(10, 2) NOT NULL,
    rotation_x DECIMAL(5, 2) DEFAULT 0,
    rotation_y DECIMAL(5, 2) DEFAULT 0,
    rotation_z DECIMAL(5, 2) DEFAULT 0,
    size_width DECIMAL(5, 2) DEFAULT 1.0,
    size_height DECIMAL(5, 2) DEFAULT 1.0,
    size_depth DECIMAL(5, 2) DEFAULT 1.0,
    color VARCHAR(7),
    material VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cell_id) REFERENCES game_data.world_cells(cell_id) ON DELETE CASCADE
);

CREATE INDEX idx_cell_3d_blocks_cell ON game_data.cell_3d_blocks(cell_id);
CREATE INDEX idx_cell_3d_blocks_type ON game_data.cell_3d_blocks(block_type);
CREATE INDEX idx_cell_3d_blocks_position ON game_data.cell_3d_blocks(position_x, position_y, position_z);

-- Entity 배치는 기존 entity_properties 사용하되, 3D 좌표 추가
ALTER TABLE game_data.entities
ADD COLUMN IF NOT EXISTS position_3d JSONB;  -- {"x": 0, "y": 0, "z": 0, "rotation_y": 0}
```

### 문제점 3: 핀과 엔티티의 관계 모호
**현재 설계**: 핀은 `game_data_id`로 연결
**문제**:
- Region 핀 → Region 엔티티
- Location 핀 → Location 엔티티
- Cell 핀 → Cell 엔티티
- 하지만 Cell 3D 뷰에서 Entity는 어떻게 연결?

**개선안**:
- 핀은 맵 레벨의 엔티티만 표시
- Cell 3D 뷰의 Entity는 별도 관리 (핀 아님)
- 명확한 구분 필요

## 2. 사용자 경험 (UX)

### 문제점 1: 네비게이션 복잡도
**현재 설계**: Breadcrumb + 전환 버튼
**문제**:
- 4단계 깊이 (World → Region → Location → Cell)
- 사용자가 길을 잃을 수 있음
- 빠른 이동이 어려움

**개선안**:
1. **미니맵 네비게이션**: 상단에 전체 계층 구조 표시
2. **빠른 이동**: 키보드 단축키 (Ctrl+↑ 상위, Ctrl+↓ 하위)
3. **히스토리**: 뒤로가기/앞으로가기 지원
4. **즐겨찾기**: 자주 가는 맵 북마크

### 문제점 2: Cell 3D 뷰 전환
**현재 설계**: Cell 선택 시 3D 뷰로 전환
**문제**:
- 2D 맵에서 3D 뷰로 전환이 갑작스러움
- 컨텍스트 손실 가능

**개선안**:
1. **모달/패널 방식**: 3D 뷰를 오른쪽 패널이나 모달로 표시
2. **탭 방식**: Location Map과 Cell 3D 뷰를 탭으로 전환
3. **분할 화면**: 2D 맵과 3D 뷰 동시 표시

### 문제점 3: 블록 배치 워크플로우
**현재 설계**: 블록 타입 선택 → 배치
**문제**:
- 블록이 많아지면 선택이 어려움
- 자주 사용하는 블록 찾기 어려움
- 배치 후 수정이 번거로움

**개선안**:
1. **블록 팔레트**: 카테고리별 그룹화 (벽, 바닥, 가구 등)
2. **즐겨찾기 블록**: 자주 사용하는 블록 상단 고정
3. **블록 검색**: 이름으로 검색
4. **다중 선택**: 여러 블록 동시 선택/이동/삭제
5. **복사/붙여넣기**: 블록 그룹 복사
6. **스냅 그리드**: 정확한 배치를 위한 그리드 스냅

## 3. 성능 고려사항

### 문제점 1: 맵 로딩 성능
**현재 설계**: 각 레벨마다 별도 맵 로드
**문제**:
- Region 100개, Location 1000개면 맵 메타데이터 1100개
- 초기 로딩 시간 증가
- 메모리 사용량 증가

**개선안**:
1. **지연 로딩**: 필요한 맵만 로드
2. **캐싱**: 최근 사용한 맵 캐시
3. **배치 로딩**: 현재 레벨 + 상위 레벨만 로드
4. **가상화**: 많은 핀을 가진 맵의 경우 가상 스크롤

### 문제점 2: Cell 3D 뷰 렌더링 성능
**현재 설계**: Three.js로 모든 블록 렌더링
**문제**:
- 블록이 1000개 이상이면 성능 저하
- Entity, World Object까지 포함하면 더 복잡

**개선안**:
1. **LOD (Level of Detail)**: 거리에 따라 블록 디테일 조절
2. **Frustum Culling**: 화면에 보이는 블록만 렌더링
3. **인스턴싱**: 같은 타입의 블록은 인스턴스로 렌더링
4. **오클루전 컬링**: 가려진 블록 렌더링 생략
5. **청크 시스템**: 큰 셀을 청크로 나눠 필요시만 로드

### 문제점 3: 데이터베이스 쿼리 성능
**현재 설계**: 각 레벨마다 별도 쿼리
**문제**:
- Region 맵: Location 목록 조회
- Location 맵: Cell 목록 조회
- Cell 3D: 블록, Entity, World Object 조회
- 여러 쿼리로 인한 지연

**개선안**:
1. **JOIN 최적화**: 필요한 데이터를 한 번에 조회
2. **인덱스 최적화**: 자주 조회하는 컬럼 인덱스
3. **캐싱**: Redis 등으로 자주 조회하는 데이터 캐시
4. **페이지네이션**: 많은 데이터는 페이지 단위로 로드

## 4. 게임 디자인 관점

### 문제점 1: 맵 이미지 관리
**현재 설계**: 각 Region/Location마다 맵 이미지
**문제**:
- 이미지 파일 관리 복잡
- 용량 증가
- 버전 관리 어려움

**개선안**:
1. **이미지 CDN**: 이미지를 CDN에 저장
2. **이미지 최적화**: WebP, 압축 등
3. **타일 시스템**: 큰 맵을 타일로 나눠 필요시만 로드
4. **프로시저럴 생성**: 기본 맵은 자동 생성, 커스텀만 이미지

### 문제점 2: Cell 3D 블록 시스템 확장성
**현재 설계**: 고정된 블록 타입
**문제**:
- 새로운 블록 타입 추가가 어려움
- 블록 속성 확장이 제한적

**개선안**:
1. **블록 템플릿 시스템**: 블록을 데이터로 정의
2. **커스텀 블록**: 사용자가 블록 생성 가능
3. **블록 프리셋**: 자주 사용하는 블록 조합 저장
4. **블록 라이브러리**: 공유 가능한 블록 라이브러리

### 문제점 3: 협업 및 버전 관리
**현재 설계**: 단일 사용자 중심
**문제**:
- 여러 디자이너가 동시 작업 시 충돌
- 변경 이력 추적 어려움

**개선안**:
1. **락 시스템**: 편집 중인 맵/셀 잠금
2. **변경 이력**: Git-like 버전 관리
3. **충돌 해결**: 동시 편집 시 충돌 해결 UI
4. **권한 관리**: 읽기/쓰기 권한 분리

## 5. 기술적 구현 복잡도

### 문제점 1: 3D 엔진 선택
**현재 설계**: Three.js + React Three Fiber
**고려사항**:
- Three.js는 무겁고 학습 곡선이 있음
- 대안: Babylon.js, PlayCanvas 등

**권장안**:
- **Three.js + React Three Fiber**: React 생태계와 잘 통합
- **Drei**: 유용한 유틸리티 제공
- **Zustand/Jotai**: 3D 상태 관리

### 문제점 2: 상태 관리 복잡도
**현재 설계**: 각 레벨별 다른 상태
**문제**:
- 4단계 깊이의 상태 관리
- 상태 동기화 복잡

**개선안**:
1. **Context API**: 맵 레벨별 Context
2. **Zustand**: 전역 상태 관리
3. **상태 정규화**: Redux-like 정규화된 상태

### 문제점 3: 실시간 동기화
**현재 설계**: WebSocket으로 동기화
**문제**:
- 3D 블록 배치는 데이터량이 많음
- 실시간 동기화 시 성능 이슈

**개선안**:
1. **디바운싱**: 빠른 변경은 디바운싱 후 전송
2. **차등 동기화**: 변경된 부분만 전송
3. **오프라인 모드**: 오프라인에서 작업 후 동기화

## 6. 데이터 일관성

### 문제점 1: 계층 구조 무결성
**현재 설계**: 외래키로 관계 유지
**문제**:
- Region 삭제 시 하위 Location/Location Map 처리
- Location 삭제 시 하위 Cell/Cell 3D 레이아웃 처리

**개선안**:
1. **CASCADE 정책 명확화**: 삭제 시 하위 데이터 처리 방식 정의
2. **소프트 삭제**: 실제 삭제 대신 비활성화
3. **삭제 확인**: 중요한 데이터 삭제 시 다단계 확인

### 문제점 2: 핀과 엔티티 동기화
**현재 설계**: 핀의 `game_data_id`로 연결
**문제**:
- 엔티티 삭제 시 핀 처리
- 핀 삭제 시 엔티티 처리

**개선안**:
1. **트리거**: DB 트리거로 자동 동기화
2. **애플리케이션 레벨**: 서비스 레이어에서 처리
3. **옵션 제공**: 사용자가 선택 (핀만 삭제, 엔티티도 삭제 등)

## 7. 워크플로우 효율성

### 문제점 1: 맵 생성 워크플로우
**현재 설계**: Region/Location 생성 시 맵 자동 생성
**문제**:
- 불필요한 맵이 생성될 수 있음
- 맵 설정이 나중에 어려움

**개선안**:
1. **지연 생성**: 맵이 실제로 필요할 때 생성
2. **템플릿 선택**: 맵 생성 시 템플릿 선택
3. **일괄 생성**: 여러 맵을 한 번에 생성

### 문제점 2: 블록 배치 효율성
**현재 설계**: 하나씩 배치
**문제**:
- 큰 구조물 생성 시 시간 소요
- 반복 작업이 많음

**개선안**:
1. **브러시 도구**: 영역을 선택해 한 번에 배치
2. **패턴 배치**: 패턴을 정의해 반복 배치
3. **스크립트**: 자동화 스크립트 지원
4. **임포트/익스포트**: 블록 레이아웃 파일로 저장/불러오기

## 8. 우선순위 재조정

### Phase 1 (필수)
1. ✅ 데이터 모델 확장 (맵 레벨 필드)
2. ✅ Region Map 구현 (Location 배치)
3. ✅ Location Map 구현 (Cell 배치)

### Phase 2 (중요)
4. ⚠️ Cell 3D 뷰 기본 구현 (블록 배치)
5. ⚠️ 블록 시스템 데이터 모델 (별도 테이블)
6. ⚠️ 네비게이션 개선 (Breadcrumb, 빠른 이동)

### Phase 3 (개선)
7. 🔄 성능 최적화 (LOD, 캐싱)
8. 🔄 블록 팔레트 및 워크플로우 개선
9. 🔄 협업 기능 (락, 버전 관리)

### Phase 4 (선택)
10. 🔮 고급 기능 (프로시저럴 생성, 커스텀 블록)

## 결론 및 권장사항

### 즉시 개선 필요
1. **블록 데이터 모델**: JSONB 대신 별도 테이블 사용
2. **맵 메타데이터 최적화**: 기본값 사용, 커스텀만 저장
3. **네비게이션 개선**: 미니맵, 빠른 이동 추가

### 단계적 개선
1. **Phase 1-2 완료 후**: 성능 프로파일링 및 최적화
2. **사용자 피드백 수집**: 실제 사용 패턴 분석
3. **점진적 기능 추가**: 우선순위에 따라 단계적 구현

### 장기적 고려사항
1. **확장성**: 대규모 월드 지원
2. **협업**: 멀티 유저 편집
3. **모듈화**: 플러그인 시스템

