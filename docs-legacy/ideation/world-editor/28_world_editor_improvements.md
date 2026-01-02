# 월드 에디터 개선 요구사항

> **문서 번호**: 28  
> **작성일**: 2025-12-27  
> **목적**: 월드 에디터의 ID 생성 규칙 준수, 메타데이터 편집, UI 개선 요구사항 문서화

---

## 1. 개요

현재 월드 에디터에서 발견된 문제점과 개선 요구사항을 정리하고, 구현 계획을 수립합니다.

---

## 2. 문제점 분석

### 2.1 ID 생성 규칙 미준수

**현재 문제:**
- Region 생성 시 `pin.game_data_id`를 그대로 사용하거나 임의의 ID 생성
- Location 생성 시 `LOC_${Date.now()}` 형식 사용
- Cell 생성 시 `CELL_${Date.now()}` 형식 사용
- 데이터베이스 스키마에 정의된 ID 명명 규칙을 따르지 않음

**데이터베이스 ID 명명 규칙:**
```sql
-- Region: REG_[대륙]_[지역]_[일련번호]
-- 예시: REG_NORTH_FOREST_001, REG_EAST_DESERT_001

-- Location: LOC_[지역]_[장소]_[일련번호]
-- 예시: LOC_REG_NORTH_FOREST_001_TOWN_001

-- Cell: CELL_[위치타입]_[세부위치]_[일련번호]
-- 예시: CELL_TOWN_TAVERN_001
```

**영향:**
- ID 일관성 부족으로 데이터 관리 어려움
- 다른 시스템과의 호환성 문제
- 데이터베이스 제약 조건 위반 가능성

### 2.2 메타데이터 편집 기능 부재

**현재 문제:**
- `pin_id` 등 핀 메타데이터를 편집할 수 있는 UI 없음
- 핀의 시각적 속성(색상, 크기, 아이콘)만 편집 가능
- 핀과 게임 데이터 간의 연결 정보를 직접 수정 불가

**요구사항:**
- 핀의 메타데이터(pin_id, game_data_id, pin_type 등) 편집 기능
- 핀의 시각적 속성 편집 기능
- 편집 후 즉시 반영

### 2.3 계층 구조 조회 기능 부족

**현재 문제:**
- Region 레벨에서 하위 Location 목록 조회는 가능하나, UI에서 명확하게 표시되지 않음
- Location 레벨에서 하위 Cell 목록 조회 기능은 있으나 접근성이 낮음
- 계층 구조를 한눈에 파악하기 어려움

**요구사항:**
- Region 편집기에서 하위 Location 목록을 명확하게 표시
- Location 편집기에서 하위 Cell 목록을 명확하게 표시
- 계층 구조를 트리 형태로 시각화

### 2.4 D&D 정보 입력 UI 복잡성

**현재 문제:**
- D&D 정보 입력 시 별도의 모드로 전환 (depth 생성)
- 편집기 화면에서 직접 조회/편집 불가
- 사용자 경험 저하

**요구사항:**
- D&D 정보를 편집기 화면에서 직접 조회/편집
- 별도 모드 전환 없이 인라인 편집
- 스크롤 가능한 UI로 모든 정보 표시

### 2.5 UI 기본 기능 누락

**현재 문제:**
- 스크롤 기능이 제대로 구현되지 않음
- 긴 콘텐츠 표시 시 레이아웃 깨짐
- 반응형 디자인 미흡

**요구사항:**
- 모든 패널에 적절한 스크롤 기능 구현
- 콘텐츠 길이에 관계없이 레이아웃 유지
- 반응형 디자인 적용

---

## 3. 요구사항 상세

### 3.1 ID 생성 규칙 준수

#### 3.1.1 Region ID 생성

**규칙:**
- 형식: `REG_[대륙]_[지역]_[일련번호]`
- 예시: `REG_NORTH_FOREST_001`, `REG_EAST_DESERT_001`
- 일련번호는 001부터 시작하여 자동 증가

**구현 방법:**
1. 백엔드에 ID 생성기 함수 구현
2. Region 생성 시 자동으로 규칙에 맞는 ID 생성
3. 사용자가 직접 ID를 입력할 수도 있도록 옵션 제공

**API 변경:**
```python
# app/world_editor/services/id_generator.py
class IDGenerator:
    @staticmethod
    async def generate_region_id(continent: str, region_name: str) -> str:
        """Region ID 생성"""
        # 기존 Region 조회하여 일련번호 결정
        # REG_[대륙]_[지역]_[일련번호] 형식 반환
        pass
```

#### 3.1.2 Location ID 생성

**규칙:**
- 형식: `LOC_[지역]_[장소]_[일련번호]`
- 예시: `LOC_REG_NORTH_FOREST_001_TOWN_001`
- 상위 Region ID를 포함하여 생성

**구현 방법:**
1. 상위 Region ID를 기반으로 Location ID 생성
2. 장소 타입(TOWN, DUNGEON 등)을 포함
3. 일련번호 자동 증가

#### 3.1.3 Cell ID 생성

**규칙:**
- 형식: `CELL_[위치타입]_[세부위치]_[일련번호]`
- 예시: `CELL_TOWN_TAVERN_001`
- 상위 Location 정보를 참조하여 생성

**구현 방법:**
1. 상위 Location 정보를 기반으로 Cell ID 생성
2. 위치 타입과 세부 위치 정보 포함
3. 일련번호 자동 증가

### 3.2 메타데이터 편집기

#### 3.2.1 핀 메타데이터 편집

**편집 가능한 필드:**
- `pin_id`: 핀 고유 ID
- `game_data_id`: 연결된 게임 데이터 ID
- `pin_type`: 핀 타입 (region, location, cell)
- `x`, `y`: 핀 위치 좌표
- `icon_type`: 아이콘 타입
- `color`: 핀 색상
- `size`: 핀 크기

**UI 구성:**
- 메타데이터 섹션을 PinEditor 상단에 배치
- 각 필드를 입력 필드로 표시
- 저장 버튼으로 변경사항 적용
- 유효성 검증 (ID 중복 체크 등)

#### 3.2.2 게임 데이터 메타데이터 편집

**Region 편집:**
- `region_id`: Region ID (읽기 전용 또는 편집 가능)
- `region_name`: Region 이름
- `region_description`: Region 설명
- `region_type`: Region 타입

**Location 편집:**
- `location_id`: Location ID
- `location_name`: Location 이름
- `location_description`: Location 설명
- `location_type`: Location 타입
- `region_id`: 상위 Region ID

**Cell 편집:**
- `cell_id`: Cell ID
- `cell_name`: Cell 이름
- `cell_description`: Cell 설명
- `location_id`: 상위 Location ID
- `matrix_width`, `matrix_height`: Cell 크기

### 3.3 계층 구조 조회

#### 3.3.1 Region 편집기

**표시 내용:**
- Region 기본 정보 (이름, 설명, 타입)
- 하위 Location 목록 (트리 형태)
  - Location 이름, ID
  - Location 타입
  - Location 설명 (요약)
- Location 추가 버튼
- Location 선택 시 상세 정보 표시

**UI 구성:**
- Region 정보 섹션
- 하위 Location 목록 섹션 (접기/펼치기 가능)
- Location 추가 폼
- 선택된 Location 상세 정보 패널

#### 3.3.2 Location 편집기

**표시 내용:**
- Location 기본 정보
- 상위 Region 정보 (링크)
- 하위 Cell 목록 (트리 형태)
  - Cell 이름, ID
  - Cell 크기 (matrix_width x matrix_height)
  - Cell 설명 (요약)
- Cell 추가 버튼
- Cell 선택 시 상세 정보 표시

**UI 구성:**
- Location 정보 섹션
- 상위 Region 정보 섹션
- 하위 Cell 목록 섹션 (접기/펼치기 가능)
- Cell 추가 폼
- 선택된 Cell 상세 정보 패널

### 3.4 D&D 통계 정보 및 상세 정보 입력 UI

#### 3.4.1 D&D 통계 정보 (기존 유지)

**기존 기능 유지:**
- Climate (기후)
- Danger Level (위험도)
- Recommended Level (권장 레벨)
- Background Music (배경 음악)
- Ambient Effects (환경 효과)

**저장 위치:**
- `region_properties.dnd_stats` 또는 `location_properties.dnd_stats`

**중요:** 이 섹션은 기존 기능을 그대로 유지하며, 상세 정보 섹션과 별도로 존재합니다.

#### 3.4.2 상세 정보 섹션 기반 편집 (신규 추가)

**변경 사항:**
- 고정된 필드 구조 대신 자유로운 섹션 기반 구조
- 각 섹션은 제목과 본문으로 구성
- 섹션 타입: 텍스트 섹션, 리스트 섹션, 제목 섹션
- 별도의 편집 모드 없이 인라인 편집

**UI 구성:**
- 상세 정보 섹션 (기본적으로 접힘)
- 섹션 목록:
  - 각 섹션은 제목과 본문/리스트로 구성
  - 섹션 추가 버튼으로 새 섹션 생성
  - 섹션 삭제 버튼으로 섹션 제거
  - 섹션 순서 변경 (드래그 앤 드롭)
- 섹션 타입:
  - **텍스트 섹션**: 제목 + 여러 문단의 자유 텍스트
  - **리스트 섹션**: 제목 + 불릿/번호 리스트
  - **제목 섹션**: 제목만 있는 구분선
- 각 섹션 접기/펼치기 가능
- 자동 저장 (onBlur)

#### 3.4.3 데이터 구조

**저장 형식:**
```json
{
  "dnd_stats": {
    "climate": "temperate",
    "danger_level": 3,
    "recommended_level": {"min": 1, "max": 10},
    "bgm": "peaceful_01",
    "ambient_effects": ["birds", "wind"]
  },
  "detail_sections": [
    {
      "id": "section_1",
      "type": "text",
      "title": "외관",
      "content": "아르보이아 해는 마치 거대한 사파이어를 땅에 박아놓은 듯한 모습이다..."
    },
    {
      "id": "section_2",
      "type": "list",
      "title": "주요 장소",
      "items": [
        "용의 굴: 전설 속 용이 잠들어 있다는 동굴.",
        "고대 문명의 유적지: 바닷가 절벽 위에 우뚝 서 있는 신전의 폐허."
      ]
    }
  ]
}
```

**저장 위치:**
- `region_properties.dnd_stats`: D&D 통계 정보 (기존 유지)
- `region_properties.detail_sections`: 상세 정보 섹션들 (신규 추가)
- `location_properties.dnd_stats`: D&D 통계 정보 (기존 유지)
- `location_properties.detail_sections`: 상세 정보 섹션들 (신규 추가)

**구현:**
- D&D 통계 정보 섹션: 기존 기능 유지
- 상세 정보 섹션: `region_properties.detail_sections` 또는 `location_properties.detail_sections`에 저장
- 섹션 기반 편집기 컴포넌트 구현
- 스크롤 지원으로 긴 콘텐츠 표시

**중요:** D&D 통계 정보와 상세 정보는 별도의 섹션으로 모두 지원되며, 서로를 대체하지 않습니다.

### 3.5 UI 기본 기능 개선

#### 3.5.1 스크롤 기능

**적용 대상:**
- PinEditor 전체 패널
- 각 섹션별 스크롤
- D&D 정보 섹션
- Location/Cell 목록

**구현:**
- CSS `overflow-y: auto` 적용
- 최대 높이 설정
- 스크롤바 스타일링

#### 3.5.2 레이아웃 개선

**개선 사항:**
- 고정 높이 패널에 스크롤 적용
- 섹션별 접기/펼치기 기능
- 반응형 디자인 적용
- 모바일 환경 고려

#### 3.5.3 사용자 경험 개선

**개선 사항:**
- 로딩 상태 표시
- 저장 상태 표시
- 에러 메시지 표시
- 성공 메시지 표시
- 입력 필드 유효성 검증

---

## 4. 구현 계획

### 4.1 Phase 1: ID 생성 규칙 준수

**작업 내용:**
1. ID 생성기 서비스 구현 (`app/world_editor/services/id_generator.py`)
2. Region/Location/Cell 생성 시 ID 생성기 사용
3. 프론트엔드에서 ID 생성 규칙에 맞는 입력 폼 제공

**예상 소요 시간:** 2-3시간

### 4.2 Phase 2: 메타데이터 편집기

**작업 내용:**
1. PinEditor에 메타데이터 편집 섹션 추가
2. 핀 메타데이터 편집 API 구현
3. 게임 데이터 메타데이터 편집 기능 강화

**예상 소요 시간:** 3-4시간

### 4.3 Phase 3: 계층 구조 조회

**작업 내용:**
1. Region 편집기에 하위 Location 목록 표시
2. Location 편집기에 하위 Cell 목록 표시
3. 트리 형태 UI 구현

**예상 소요 시간:** 2-3시간

### 4.4 Phase 4: D&D 통계 정보 및 상세 정보 입력 UI

**작업 내용:**
1. D&D 통계 정보 섹션 유지 (기존 기능)
2. 상세 정보 섹션 기반 편집기 컴포넌트 구현 (신규)
3. 섹션 추가/삭제/순서 변경 기능
4. 텍스트/리스트 섹션 타입 지원
5. 자동 저장 및 스크롤 기능 추가

**예상 소요 시간:** 3-4시간

**중요:** D&D 통계 정보는 기존 기능을 유지하고, 상세 정보 섹션을 추가로 구현합니다.

### 4.5 Phase 5: UI 기본 기능 개선

**작업 내용:**
1. 스크롤 기능 구현
2. 레이아웃 개선
3. 사용자 경험 개선

**예상 소요 시간:** 2-3시간

**총 예상 소요 시간:** 11-16시간

---

## 5. 기술 스택

### 5.1 백엔드

- Python 3.12
- FastAPI
- PostgreSQL (asyncpg)
- Pydantic

### 5.2 프론트엔드

- React 18
- TypeScript
- Konva.js
- CSS

---

## 6. 테스트 계획

### 6.1 단위 테스트

- ID 생성기 함수 테스트
- 메타데이터 편집 API 테스트
- 계층 구조 조회 API 테스트

### 6.2 통합 테스트

- ID 생성 규칙 준수 테스트
- 메타데이터 편집 E2E 테스트
- 계층 구조 조회 E2E 테스트

### 6.3 UI 테스트

- 스크롤 기능 테스트
- 레이아웃 반응형 테스트
- 사용자 경험 테스트

---

## 7. 참고 자료

- [데이터베이스 스키마](../database/setup/mvp_schema.sql)
- [월드 에디터 설계 문서](./25_world_editor_design.md)
- [월드 에디터 DB 분석](./26_world_editor_db_analysis.md)
- [월드 에디터 테스트 리포트](./27_world_editor_test_report.md)

---

## 8. 체크리스트

### 8.1 ID 생성 규칙 준수
- [ ] ID 생성기 서비스 구현
- [ ] Region ID 생성 규칙 적용
- [ ] Location ID 생성 규칙 적용
- [ ] Cell ID 생성 규칙 적용
- [ ] 프론트엔드 ID 입력 폼 개선

### 8.2 메타데이터 편집기
- [ ] 핀 메타데이터 편집 UI 구현
- [ ] 핀 메타데이터 편집 API 구현
- [ ] 게임 데이터 메타데이터 편집 UI 강화
- [ ] 유효성 검증 구현

### 8.3 계층 구조 조회
- [ ] Region 편집기에 하위 Location 목록 표시
- [ ] Location 편집기에 하위 Cell 목록 표시
- [ ] 트리 형태 UI 구현
- [ ] 접기/펼치기 기능 구현

### 8.4 D&D 통계 정보 및 상세 정보 입력 UI
- [ ] D&D 통계 정보 섹션 유지 (기존 기능)
- [ ] 상세 정보 섹션 기반 편집기 컴포넌트 구현
- [ ] 섹션 추가/삭제/순서 변경 기능
- [ ] 텍스트/리스트 섹션 타입 지원
- [ ] 자동 저장 및 스크롤 기능 추가
- [ ] 두 섹션이 별도로 작동하는지 확인

### 8.5 UI 기본 기능 개선
- [ ] 스크롤 기능 구현
- [ ] 레이아웃 개선
- [ ] 반응형 디자인 적용
- [ ] 사용자 경험 개선

---

**문서 작성 완료일:** 2025-12-27  
**다음 단계:** 개발 진행

