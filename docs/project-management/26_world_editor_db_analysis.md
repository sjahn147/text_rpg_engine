# 월드 에디터 DB 구조 분석 및 개선 제안

> **문서 번호**: 26  
> **작성일**: 2025-12-27  
> **목적**: 현재 DB 구조가 설계 요구사항을 충족하는지 분석 및 개선 제안

---

## 1. 현재 DB 구조 분석

### 1.1 계층 구조

```
World (map_metadata)
  └── Region (world_regions)
       └── Location (world_locations)
            └── Cell (world_cells)
```

### 1.2 테이블 구조 비교

#### ✅ 완전히 충족되는 부분

**1. MapMetadata (지도 메타데이터)**
- `map_metadata` 테이블에 모든 필드 존재
- `background_image`, `width`, `height`, `grid_enabled`, `grid_size`, `zoom_level`, `viewport_x`, `viewport_y` 모두 포함

**2. PinData (핀 위치)**
- `pin_positions` 테이블에 모든 필드 존재
- `game_data_id`, `pin_type`, `x`, `y`, `icon_type`, `color`, `size` 모두 포함
- `UNIQUE(game_data_id, pin_type)` 제약으로 중복 방지

**3. D&D 스타일 정보**
- `region_properties`, `location_properties`, `cell_properties` JSONB 필드로 저장 가능
- 모든 D&D 정보 구조를 JSONB에 저장 가능

#### ⚠️ 개선이 필요한 부분

**1. RoadData (도로 데이터)**

**현재 구조:**
```sql
world_roads (
    from_region_id VARCHAR(50),
    from_location_id VARCHAR(50),
    to_region_id VARCHAR(50),
    to_location_id VARCHAR(50),
    ...
)
```

**설계 문서 요구사항:**
```typescript
interface RoadData {
    from_pin_id: string;    // 시작 핀 ID
    to_pin_id: string;      // 종료 핀 ID
    ...
}
```

**문제점:**
- 설계 문서는 핀 ID로 도로를 연결하지만, 현재 DB는 region_id/location_id로 직접 연결
- 핀을 통한 연결이 더 직관적이고 유연함
- 핀 ID로 연결하면 핀 위치 변경 시 도로도 자동으로 업데이트 가능

**2. 도로 시각적 속성**

**설계 문서 요구사항:**
```typescript
interface RoadData {
    color: string;      // 도로 색상
    width: number;      // 도로 너비
    dashed: boolean;    // 점선 여부
}
```

**현재 구조:**
- `road_properties` JSONB에 저장 가능하지만 명시적 필드 없음
- 시각적 속성은 `road_properties.visual`에 저장해야 함

---

## 2. 지도상에서 World/Region/Location/Cell 처리 방식

### 2.1 계층 구조

```
World (전체 지도)
  ├── MapMetadata: 지도 전체 메타데이터
  │   └── background_image: assets/world_editor/worldmap.png
  │
  ├── Regions (최상위 지역)
  │   ├── Pin: 지도상 핀 위치 (pin_positions)
  │   ├── Properties: region_properties JSONB
  │   │   └── dnd_info: D&D 스타일 정보
  │   └── Roads: world_roads (from_region_id/to_region_id)
  │
  ├── Locations (지역 내 구체적 장소)
  │   ├── Pin: 지도상 핀 위치 (pin_positions)
  │   ├── Properties: location_properties JSONB
  │   │   └── dnd_info: D&D 스타일 정보
  │   └── Roads: world_roads (from_location_id/to_location_id)
  │
  └── Cells (위치 내 셀 단위 공간)
      ├── Pin: 지도상 핀 위치 (pin_positions)
      ├── Properties: cell_properties JSONB
      │   └── dnd_info: D&D 스타일 정보
      └── Roads: world_roads (셀 간 연결은 현재 미지원)
```

### 2.2 핀 처리 방식

**핀은 각 계층(Region/Location/Cell)에 대해 하나씩만 존재:**
- `pin_positions` 테이블의 `UNIQUE(game_data_id, pin_type)` 제약
- 같은 `game_data_id`와 `pin_type` 조합은 하나의 핀만 가질 수 있음
- 예: `REG_NORTH_001` region은 하나의 핀만 가짐

**핀 타입별 색상:**
- Region: `#FF6B9D` (핑크)
- Location: `#4ECDC4` (청록)
- Cell: `#95E1D3` (연두)

### 2.3 도로 처리 방식

**현재 구현:**
- Region 간 도로: `from_region_id` ↔ `to_region_id`
- Location 간 도로: `from_location_id` ↔ `to_location_id`
- Cell 간 도로: 현재 미지원 (필요 시 추가 가능)

**경로 좌표:**
- `path_coordinates` JSONB 배열: `[{"x": 100, "y": 200}, ...]`
- 핀 위치가 변경되어도 경로 좌표는 유지됨
- 핀 간 직선 연결 또는 커스텀 경로 지원

---

## 3. 개선 제안

### 3.1 도로 테이블에 핀 ID 필드 추가

**제안 1: 핀 ID 필드 추가 (권장)**

```sql
ALTER TABLE game_data.world_roads
ADD COLUMN from_pin_id VARCHAR(50),
ADD COLUMN to_pin_id VARCHAR(50);

-- 외래키 추가
ALTER TABLE game_data.world_roads
ADD CONSTRAINT fk_roads_from_pin 
    FOREIGN KEY (from_pin_id) REFERENCES game_data.pin_positions(pin_id) ON DELETE CASCADE,
ADD CONSTRAINT fk_roads_to_pin 
    FOREIGN KEY (to_pin_id) REFERENCES game_data.pin_positions(pin_id) ON DELETE CASCADE;

-- 인덱스 추가
CREATE INDEX idx_roads_from_pin ON game_data.world_roads(from_pin_id);
CREATE INDEX idx_roads_to_pin ON game_data.world_roads(to_pin_id);
```

**장점:**
- 핀 기반 연결로 더 직관적
- 핀 위치 변경 시 도로도 자동 업데이트 가능
- 기존 region_id/location_id 필드와 호환 가능

**제안 2: 도로 시각적 속성 명시적 필드 추가**

```sql
ALTER TABLE game_data.world_roads
ADD COLUMN color VARCHAR(7) DEFAULT '#8B4513',
ADD COLUMN width INTEGER DEFAULT 2,
ADD COLUMN dashed BOOLEAN DEFAULT false;
```

**장점:**
- 시각적 속성을 명시적으로 관리
- 쿼리 성능 향상 (JSONB 파싱 불필요)
- 타입 안전성 향상

### 3.2 마이그레이션 스크립트

```sql
-- =====================================================
-- 월드 에디터 DB 구조 개선 마이그레이션
-- =====================================================

-- 1. 도로 테이블에 핀 ID 필드 추가
ALTER TABLE game_data.world_roads
ADD COLUMN IF NOT EXISTS from_pin_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS to_pin_id VARCHAR(50);

-- 2. 외래키 추가
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_roads_from_pin'
    ) THEN
        ALTER TABLE game_data.world_roads
        ADD CONSTRAINT fk_roads_from_pin 
            FOREIGN KEY (from_pin_id) 
            REFERENCES game_data.pin_positions(pin_id) 
            ON DELETE CASCADE;
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_roads_to_pin'
    ) THEN
        ALTER TABLE game_data.world_roads
        ADD CONSTRAINT fk_roads_to_pin 
            FOREIGN KEY (to_pin_id) 
            REFERENCES game_data.pin_positions(pin_id) 
            ON DELETE CASCADE;
    END IF;
END $$;

-- 3. 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_roads_from_pin ON game_data.world_roads(from_pin_id);
CREATE INDEX IF NOT EXISTS idx_roads_to_pin ON game_data.world_roads(to_pin_id);

-- 4. 도로 시각적 속성 필드 추가
ALTER TABLE game_data.world_roads
ADD COLUMN IF NOT EXISTS color VARCHAR(7) DEFAULT '#8B4513',
ADD COLUMN IF NOT EXISTS width INTEGER DEFAULT 2,
ADD COLUMN IF NOT EXISTS dashed BOOLEAN DEFAULT false;

-- 5. 기존 데이터 마이그레이션 (선택사항)
-- 기존 region_id/location_id로 핀을 찾아서 from_pin_id/to_pin_id 채우기
UPDATE game_data.world_roads r
SET from_pin_id = (
    SELECT pin_id FROM game_data.pin_positions p
    WHERE (r.from_region_id IS NOT NULL AND p.game_data_id = r.from_region_id AND p.pin_type = 'region')
       OR (r.from_location_id IS NOT NULL AND p.game_data_id = r.from_location_id AND p.pin_type = 'location')
    LIMIT 1
),
to_pin_id = (
    SELECT pin_id FROM game_data.pin_positions p
    WHERE (r.to_region_id IS NOT NULL AND p.game_data_id = r.to_region_id AND p.pin_type = 'region')
       OR (r.to_location_id IS NOT NULL AND p.game_data_id = r.to_location_id AND p.pin_type = 'location')
    LIMIT 1
)
WHERE from_pin_id IS NULL OR to_pin_id IS NULL;
```

---

## 4. 결론

### ✅ 충족되는 요구사항

1. **MapMetadata**: 모든 필드 완벽 지원
2. **PinData**: 모든 필드 완벽 지원
3. **D&D 정보**: JSONB로 완벽 지원
4. **계층 구조**: World → Region → Location → Cell 완벽 지원

### ⚠️ 개선 권장 사항

1. **도로 테이블에 핀 ID 필드 추가**: 더 직관적이고 유연한 연결
2. **도로 시각적 속성 명시적 필드 추가**: 성능 및 타입 안전성 향상

### 📝 권장 조치

1. 마이그레이션 스크립트 실행 (제안 3.2)
2. RoadService 업데이트: 핀 ID 기반 연결 우선 사용
3. 프론트엔드 업데이트: 핀 ID 기반 도로 그리기

---

**작성일**: 2025-12-27  
**버전**: 1.0.0

