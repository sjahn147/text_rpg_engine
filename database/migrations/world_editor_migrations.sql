-- =====================================================
-- 월드 에디터 확장 스키마
-- 작성일: 2025-12-27
-- 목적: 월드 에디터 기능을 위한 추가 테이블
-- =====================================================

-- =====================================================
-- 1. 도로 정보 테이블
-- =====================================================

CREATE TABLE IF NOT EXISTS game_data.world_roads (
    road_id VARCHAR(50) PRIMARY KEY,
    from_region_id VARCHAR(50),
    from_location_id VARCHAR(50),
    to_region_id VARCHAR(50),
    to_location_id VARCHAR(50),
    road_type VARCHAR(50) NOT NULL DEFAULT 'normal',
    distance DECIMAL(10, 2),
    travel_time INTEGER,
    danger_level INTEGER DEFAULT 1,
    road_properties JSONB DEFAULT '{}',
    path_coordinates JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_region_id) REFERENCES game_data.world_regions(region_id) ON DELETE CASCADE,
    FOREIGN KEY (to_region_id) REFERENCES game_data.world_regions(region_id) ON DELETE CASCADE,
    FOREIGN KEY (from_location_id) REFERENCES game_data.world_locations(location_id) ON DELETE CASCADE,
    FOREIGN KEY (to_location_id) REFERENCES game_data.world_locations(location_id) ON DELETE CASCADE
);

CREATE INDEX idx_roads_from_region ON game_data.world_roads(from_region_id);
CREATE INDEX idx_roads_to_region ON game_data.world_roads(to_region_id);
CREATE INDEX idx_roads_from_location ON game_data.world_roads(from_location_id);
CREATE INDEX idx_roads_to_location ON game_data.world_roads(to_location_id);
CREATE INDEX idx_roads_type ON game_data.world_roads(road_type);

COMMENT ON TABLE game_data.world_roads IS '지역 간 도로 연결 정보';
COMMENT ON COLUMN game_data.world_roads.path_coordinates IS 'JSONB 배열: [{"x": 100, "y": 200}, ...] - 지도상 경로 좌표';
COMMENT ON COLUMN game_data.world_roads.road_properties IS 'JSONB 구조: {"conditions": [...], "visual": {...}}';
COMMENT ON COLUMN game_data.world_roads.road_type IS '도로 타입: normal, hidden, river, mountain_pass';

-- =====================================================
-- 2. 지도 메타데이터 테이블
-- =====================================================

CREATE TABLE IF NOT EXISTS game_data.map_metadata (
    map_id VARCHAR(50) PRIMARY KEY DEFAULT 'default_map',
    map_name VARCHAR(100) NOT NULL DEFAULT 'World Map',
    background_image VARCHAR(255) DEFAULT 'assets/world_editor/worldmap.png',
    background_color VARCHAR(7) DEFAULT '#FFFFFF',
    width INTEGER NOT NULL DEFAULT 1920,
    height INTEGER NOT NULL DEFAULT 1080,
    grid_enabled BOOLEAN DEFAULT false,
    grid_size INTEGER DEFAULT 50,
    zoom_level DECIMAL(3, 2) DEFAULT 1.0,
    viewport_x INTEGER DEFAULT 0,
    viewport_y INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_map_metadata_name ON game_data.map_metadata(map_name);

COMMENT ON TABLE game_data.map_metadata IS '월드 에디터 지도 메타데이터';
COMMENT ON COLUMN game_data.map_metadata.background_image IS '지도 배경 이미지 경로 (기본값: assets/world_editor/worldmap.png)';

-- =====================================================
-- 3. 핀 위치 정보 테이블
-- =====================================================

CREATE TABLE IF NOT EXISTS game_data.pin_positions (
    pin_id VARCHAR(50) PRIMARY KEY,
    game_data_id VARCHAR(50) NOT NULL,
    pin_type VARCHAR(20) NOT NULL,  -- 'region', 'location', 'cell'
    x INTEGER NOT NULL,
    y INTEGER NOT NULL,
    icon_type VARCHAR(50) DEFAULT 'default',
    color VARCHAR(7) DEFAULT '#FF6B9D',
    size INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(game_data_id, pin_type)
);

CREATE INDEX idx_pin_positions_type ON game_data.pin_positions(pin_type);
CREATE INDEX idx_pin_positions_game_data ON game_data.pin_positions(game_data_id);
CREATE INDEX idx_pin_positions_coords ON game_data.pin_positions(x, y);

COMMENT ON TABLE game_data.pin_positions IS '월드 에디터 핀 위치 정보';
COMMENT ON COLUMN game_data.pin_positions.game_data_id IS '연결된 게임 데이터 ID (region_id, location_id, cell_id)';
COMMENT ON COLUMN game_data.pin_positions.pin_type IS '핀 타입: region, location, cell';
COMMENT ON COLUMN game_data.pin_positions.icon_type IS '아이콘 타입: city, village, dungeon, shop, etc.';

-- =====================================================
-- 4. 도로 테이블 개선 (핀 ID 필드 추가)
-- =====================================================

-- 핀 ID 필드 추가
ALTER TABLE game_data.world_roads
ADD COLUMN IF NOT EXISTS from_pin_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS to_pin_id VARCHAR(50);

-- 외래키 추가
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

-- 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_roads_from_pin ON game_data.world_roads(from_pin_id);
CREATE INDEX IF NOT EXISTS idx_roads_to_pin ON game_data.world_roads(to_pin_id);

-- 도로 시각적 속성 필드 추가
ALTER TABLE game_data.world_roads
ADD COLUMN IF NOT EXISTS color VARCHAR(7) DEFAULT '#8B4513',
ADD COLUMN IF NOT EXISTS width INTEGER DEFAULT 2,
ADD COLUMN IF NOT EXISTS dashed BOOLEAN DEFAULT false;

COMMENT ON COLUMN game_data.world_roads.from_pin_id IS '시작 핀 ID (핀 기반 연결)';
COMMENT ON COLUMN game_data.world_roads.to_pin_id IS '종료 핀 ID (핀 기반 연결)';
COMMENT ON COLUMN game_data.world_roads.color IS '도로 색상 (기본: #8B4513)';
COMMENT ON COLUMN game_data.world_roads.width IS '도로 너비 (픽셀, 기본: 2)';
COMMENT ON COLUMN game_data.world_roads.dashed IS '점선 여부 (기본: false)';

-- =====================================================
-- 5. 기본 지도 메타데이터 초기화
-- =====================================================

INSERT INTO game_data.map_metadata (
    map_id, map_name, background_image, width, height
) VALUES (
    'default_map',
    'World Map',
    'assets/world_editor/worldmap.png',
    1920,
    1080
) ON CONFLICT (map_id) DO UPDATE
SET 
    background_image = EXCLUDED.background_image,
    updated_at = CURRENT_TIMESTAMP;

