# [deprecated] 엔티티 위치 정보 및 3D 뷰 토론

> **Deprecated 날짜**: 2025-12-28  
> **Deprecated 사유**: 이 문서는 [44. 계층적 맵 뷰 시스템 설계 (최종안)](./44_hierarchical_map_view_design.md)에 통합되었습니다. 설계 초기 단계의 토론 내용을 담고 있으며, 최종 결정 사항은 44번 문서를 참조하세요.

**⚠️ 이 문서는 [44. 계층적 맵 뷰 시스템 설계 (최종안)](./44_hierarchical_map_view_design.md)에 통합되었습니다.**

이 문서는 설계 초기 단계의 토론 내용을 담고 있으며, 최종 결정 사항은 44번 문서를 참조하세요.

## 현재 엔티티 위치 정보 저장 구조

### 확인된 위치 정보 저장 위치

#### 1. Game Data 레벨 (game_data.entities)
- **위치**: `entity_properties` JSONB 필드
- **구조**: `{"cell_id": "CELL_XXX", ...}`
- **특징**: 
  - 엔티티가 속한 Cell ID만 저장
  - Cell 내 구체적 위치(x, y, z)는 저장하지 않음
  - 기본 템플릿 정보만 저장

#### 2. Runtime Data 레벨 (런타임 위치)
- **`runtime_data.cell_occupants`**: 
  - `position JSONB` - 셀 내 위치 정보
  - 예: `{"x": 5, "y": 4}` 또는 `{"x": 5, "y": 4, "z": 0}`
  
- **`runtime_data.runtime_cell_entities`**:
  - `position JSONB` - 셀 내 엔티티 위치
  
- **`runtime_data.entity_states`**:
  - `current_position JSONB` - 현재 위치 정보

#### 3. World Objects
- **`game_data.world_objects`**: 
  - `default_position JSONB` - 기본 위치
  - 예: `{"x": 5, "y": 4}`

### 문제점 분석

#### 현재 구조의 문제
1. **Game Data 레벨에서 위치 정보 부재**
   - `game_data.entities`에는 `cell_id`만 있고 구체적 위치(x, y, z) 없음
   - 기본 위치를 설정할 수 없음

2. **런타임 데이터에만 위치 정보 존재**
   - 게임 실행 중에만 위치 정보가 있음
   - 에디터에서 기본 위치를 설정하기 어려움

3. **위치 정보 구조 불일치**
   - 일부는 `{"x": 0.0, "y": 0.0}` (2D)
   - 일부는 `{"x": 5, "y": 4, "z": 0}` (3D 가능)
   - z 좌표가 있는지 없는지 불명확

## 제안: 3D 뷰 토글 방식

### 사용자 제안
> "3d는 정말 필요시에만 렌더링하도록 켜고 끄기가 있으면 되지 않을까요? 기본적으로 꺼져있고."

### 장점
1. **성능 최적화**: 3D 렌더링은 무거우므로 필요할 때만 사용
2. **사용자 선택권**: 3D가 필요 없는 사용자는 사용하지 않음
3. **점진적 로딩**: 3D 뷰를 켤 때만 Three.js 로드

### 구현 방안

#### 옵션 1: Cell 편집기 내 토글 버튼
```
Cell 편집기
├─ 기본 정보 (2D)
├─ [3D 뷰 토글] 버튼
└─ 3D 뷰 패널 (토글 시 표시)
    ├─ 블록 배치
    ├─ Entity 배치
    └─ World Object 배치
```

#### 옵션 2: 별도 탭/모달
```
Cell 편집기
├─ 탭 1: 기본 정보
├─ 탭 2: 엔티티 목록
└─ 탭 3: 3D 레이아웃 (토글 가능)
```

#### 옵션 3: 오른쪽 패널 전환
```
기본: Cell 편집기 (2D 정보)
토글: 3D 레이아웃 에디터 (전체 화면 또는 패널)
```

## 위치 정보 저장 구조 개선 제안

### Game Data 레벨에 위치 정보 추가

#### 옵션 1: entity_properties에 추가
```json
{
  "cell_id": "CELL_MARKET_001",
  "default_position": {
    "x": 5.0,
    "y": 4.0,
    "z": 0.0,
    "rotation_y": 90
  }
}
```

#### 옵션 2: 별도 필드 추가 (권장)
```sql
ALTER TABLE game_data.entities
ADD COLUMN IF NOT EXISTS default_position_3d JSONB;

-- 구조:
-- {
--   "x": 5.0,
--   "y": 4.0,
--   "z": 0.0,
--   "rotation_y": 90,
--   "cell_id": "CELL_MARKET_001"
-- }
```

### World Objects도 동일하게
```sql
-- 이미 default_position이 있지만, z 좌표와 rotation 추가 필요
-- 현재: {"x": 5, "y": 4}
-- 개선: {"x": 5, "y": 4, "z": 0, "rotation_y": 0}
```

## 3D 뷰의 실제 목적 재정의

### 원래 목적
> "셀 단위 엔티티는 x,y,z 정보 저장하고 있지 않았나요? 이걸 편집하기 어려우니까 3d를 생각한 거에요."

### 재정의된 목적
1. **Entity 위치 편집**: Cell 내 Entity의 x, y, z 좌표를 시각적으로 편집
2. **World Object 위치 편집**: World Object의 위치 편집
3. **블록 배치는 부가 기능**: 필요시 블록으로 구조물 생성 (선택적)

### 핵심 기능
- ✅ Entity를 3D 공간에 배치하고 위치(x, y, z) 편집
- ✅ World Object를 3D 공간에 배치하고 위치 편집
- ⚠️ 블록 배치는 선택적 기능 (필요시만)

## 토론 포인트

### 1. 위치 정보 저장 위치
**질문**: Game Data 레벨에 기본 위치를 저장해야 할까요?
- **장점**: 에디터에서 기본 위치 설정 가능
- **단점**: Game Data와 Runtime Data의 역할 혼재

**제안**: 
- Game Data: 기본 위치 템플릿 저장 (`default_position_3d`)
- Runtime Data: 실제 게임 실행 시 위치 저장 (`current_position`)

### 2. 3D 뷰 범위
**질문**: 블록 배치 기능이 정말 필요한가요?
- **사용자 의도**: Entity 위치 편집이 주 목적
- **블록 배치**: 부가 기능일 수 있음

**제안**:
- Phase 1: Entity/World Object 위치 편집만 (블록 없이)
- Phase 2: 필요시 블록 배치 기능 추가

### 3. 3D 뷰 UI 방식
**질문**: 토글 방식으로 어떻게 구현할까요?
- **옵션 A**: Cell 편집기 내 패널로 표시 (권장)
- **옵션 B**: 별도 모달로 표시
- **옵션 C**: 오른쪽 패널 전체 전환

**제안**: 옵션 A (Cell 편집기 내 패널)
- 기본: 2D 정보 표시
- "3D 레이아웃 편집" 버튼 클릭 시 3D 뷰 패널 표시
- 3D 뷰는 지연 로딩 (필요할 때만 Three.js 로드)

### 4. 위치 정보 구조 통일
**질문**: x, y, z를 항상 포함할까요?
- **현재**: 일부는 2D (x, y만), 일부는 3D (x, y, z)
- **제안**: 항상 3D 구조 사용 (z 기본값 0)

```json
{
  "x": 5.0,
  "y": 4.0,
  "z": 0.0,
  "rotation_y": 0
}
```

## 수정된 설계 제안

### Cell 3D 뷰 (재정의)

#### 목적
1. **주 목적**: Entity와 World Object의 위치(x, y, z) 시각적 편집
2. **부 목적**: 블록 배치 (선택적, 나중에 추가 가능)

#### UI 구조
```
Cell 편집기
├─ 기본 정보 탭
├─ 엔티티 탭
│   └─ [3D 레이아웃 편집] 버튼 (토글)
│       └─ 3D 뷰 패널 (토글 시 표시)
│           ├─ Entity 배치 (드래그 앤 드롭)
│           ├─ World Object 배치
│           └─ [블록 모드] 버튼 (선택적)
└─ World Objects 탭
```

#### 데이터 저장
- **Entity 기본 위치**: `game_data.entities.default_position_3d` (새 필드)
- **World Object 기본 위치**: `game_data.world_objects.default_position` (z, rotation 추가)
- **블록 배치**: `game_data.world_cells.cell_properties->'3d_blocks'` (선택적)

#### 성능 최적화
- 3D 뷰는 토글 시에만 렌더링
- Three.js는 동적 임포트 (필요할 때만 로드)
- Entity/Object가 많을 경우 LOD 적용

## 다음 단계

1. **위치 정보 구조 확정**: Game Data에 기본 위치 저장 방식 결정
2. **3D 뷰 범위 확정**: 블록 배치 포함 여부 결정
3. **UI 방식 확정**: 토글 방식 구체화
4. **데이터 모델 확정**: 필요한 필드 추가 계획

