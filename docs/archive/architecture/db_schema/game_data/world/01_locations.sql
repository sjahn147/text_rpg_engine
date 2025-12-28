-- Game World: Locations
-- ID 명명 규칙: LOC_[지역]_[장소]_[일련번호]
-- 예시:
--   - LOC_FOREST_CLEARING_001 (숲 속 빈터)
--   - LOC_TOWN_SQUARE_001 (마을 광장)
--   - LOC_DUNGEON_ENTRANCE_001 (던전 입구)
--   - LOC_CASTLE_GARDEN_001 (성 정원)
CREATE TABLE game_data.world_locations (
    location_id VARCHAR(50) PRIMARY KEY,
    region_id VARCHAR(50) NOT NULL,
    location_name VARCHAR(100) NOT NULL,
    location_description TEXT,
    location_type VARCHAR(50),
    location_properties JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 장소 타입 인덱스
CREATE INDEX idx_location_type ON game_data.world_locations(location_type);

-- Foreign Key 제약조건 추가
ALTER TABLE game_data.world_locations
ADD CONSTRAINT fk_location_region
FOREIGN KEY (region_id) 
REFERENCES game_data.world_regions(region_id);

COMMENT ON TABLE game_data.world_locations IS '게임 내 구체적 장소 정의';
COMMENT ON COLUMN game_data.world_locations.location_properties IS 'JSONB 구조: {"background_music": "peaceful_01", "ambient_effects": ["birds", "wind"], ...}'; 