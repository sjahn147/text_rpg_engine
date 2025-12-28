-- Game World: Regions
-- ID 명명 규칙: REG_[대륙]_[지역]_[일련번호]
-- 예시:
--   - REG_NORTH_FOREST_001 (북부 숲)
--   - REG_EAST_DESERT_001 (동부 사막)
--   - REG_WEST_MOUNTAIN_001 (서부 산맥)
--   - REG_SOUTH_COAST_001 (남부 해안)
CREATE TABLE game_data.world_regions (
    region_id VARCHAR(50) PRIMARY KEY,
    region_name VARCHAR(100) NOT NULL,
    region_description TEXT,
    region_type VARCHAR(50),
    region_properties JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 지역 타입 인덱스
CREATE INDEX idx_region_type ON game_data.world_regions(region_type);

COMMENT ON TABLE game_data.world_regions IS '게임 내 최상위 지역 구분';
COMMENT ON COLUMN game_data.world_regions.region_properties IS 'JSONB 구조: {"climate": "temperate", "danger_level": 3, "recommended_level": {"min": 1, "max": 10}, ...}'; 