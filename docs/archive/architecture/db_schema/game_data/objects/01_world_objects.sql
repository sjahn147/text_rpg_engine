-- Game World: Objects
CREATE TABLE game_data.world_objects (
    object_id VARCHAR(50) PRIMARY KEY,
    object_type VARCHAR(50) NOT NULL, -- static, interactive, trigger
    object_name VARCHAR(100) NOT NULL,
    object_description TEXT,
    default_cell_id VARCHAR(50), -- 기본 생성 위치 (런타임에서 변경 가능)
    default_position JSON, -- 기본 위치 정보 {x, y, z} or {row, col}
    interaction_type VARCHAR(50), -- none, openable, triggerable
    possible_states JSON, -- 가능한 상태들의 정의
    properties JSON, -- 타입별 특수 속성
    FOREIGN KEY (default_cell_id) REFERENCES game_data.world_cells(cell_id)
); 