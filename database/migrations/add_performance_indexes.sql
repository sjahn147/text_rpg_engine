-- =====================================================
-- 성능 최적화 인덱스 추가
-- =====================================================

-- Entity 위치 기반 쿼리 최적화
-- default_position_3d JSONB 필드의 cell_id 인덱스 (이미 추가됨)
-- idx_entities_position_cell

-- Entity 크기별 필터링 최적화
CREATE INDEX IF NOT EXISTS idx_entities_size_type ON game_data.entities(entity_size, entity_type);

-- World Objects 위치 기반 쿼리 최적화
-- default_position JSONB 필드의 cell_id 인덱스
CREATE INDEX IF NOT EXISTS idx_world_objects_position_cell ON game_data.world_objects
USING GIN ((default_position -> 'cell_id'));

-- World Objects 타입 및 속성 조합 인덱스
CREATE INDEX IF NOT EXISTS idx_world_objects_type_properties ON game_data.world_objects
(object_type, passable, movable, wall_mounted);

-- Pin Positions 게임 데이터 ID 조회 최적화
-- 이미 idx_pin_positions_game_data가 있지만, pin_type과의 조합 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_pin_positions_game_data_type ON game_data.pin_positions
(game_data_id, pin_type);

-- Map Metadata 계층 구조 조회 최적화
-- 이미 idx_map_metadata_parent가 있지만, map_level과의 조합 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_map_metadata_level_parent ON game_data.map_metadata
(map_level, parent_entity_id, parent_entity_type);

-- Location-Region 조인 최적화
CREATE INDEX IF NOT EXISTS idx_locations_region_type ON game_data.world_locations
(region_id, location_type);

-- Cell-Location 조인 최적화
CREATE INDEX IF NOT EXISTS idx_cells_location_name ON game_data.world_cells
(location_id, cell_name);

-- Entity 참조 조회 최적화 (runtime_entity_id로 game_entity_id 조회)
CREATE INDEX IF NOT EXISTS idx_entity_references_game_entity ON reference_layer.entity_references
(game_entity_id, entity_type);

-- =====================================================
-- 통계 정보 업데이트 (쿼리 플래너 최적화)
-- =====================================================

ANALYZE game_data.entities;
ANALYZE game_data.world_objects;
ANALYZE game_data.pin_positions;
ANALYZE game_data.map_metadata;
ANALYZE game_data.world_locations;
ANALYZE game_data.world_cells;
ANALYZE reference_layer.entity_references;

-- =====================================================
-- 마이그레이션 완료
-- =====================================================

