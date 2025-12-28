-- Game World: Cells
-- ID 명명 규칙: CELL_[위치타입]_[세부위치]_[일련번호]
-- 예시:
--   - CELL_SHOP_WEAPON_001 (무기 상점)
--   - CELL_INN_ROOM_001 (여관 객실)
--   - CELL_DUNGEON_BOSS_001 (던전 보스룸)
--   - CELL_FIELD_PATH_001 (야외 길)
CREATE TABLE game_data.world_cells (
    cell_id VARCHAR(50) PRIMARY KEY,
    location_id VARCHAR(50) NOT NULL,
    cell_name VARCHAR(100),
    matrix_width INTEGER NOT NULL,
    matrix_height INTEGER NOT NULL,
    cell_description TEXT,
    cell_properties JSONB, -- 셀의 특수 속성 (지형, 날씨 등)
    FOREIGN KEY (location_id) REFERENCES game_data.world_locations(location_id)
);

-- Foreign Key 제약조건 추가
ALTER TABLE game_data.world_cells
ADD CONSTRAINT fk_cell_location
FOREIGN KEY (location_id) 
REFERENCES game_data.world_locations(location_id); 