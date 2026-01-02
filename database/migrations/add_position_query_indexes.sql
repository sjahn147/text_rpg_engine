-- =====================================================
-- 위치 기반 쿼리 최적화를 위한 인덱스 추가
-- =====================================================
-- Phase 3.2: 위치 기반 쿼리 최적화
-- 
-- 추가 인덱스:
-- - default_position_3d의 x, y, z 좌표 기반 쿼리 최적화
-- - default_position의 x, y 좌표 기반 쿼리 최적화
-- =====================================================

-- 1. Entity 위치 좌표 인덱스 (x, y, z 기반 쿼리 최적화)
-- JSONB 필드의 특정 키에 대한 인덱스는 표현식 인덱스로 생성
CREATE INDEX IF NOT EXISTS idx_entities_position_x ON game_data.entities 
USING BTREE (((default_position_3d->>'x')::float));

CREATE INDEX IF NOT EXISTS idx_entities_position_y ON game_data.entities 
USING BTREE (((default_position_3d->>'y')::float));

CREATE INDEX IF NOT EXISTS idx_entities_position_z ON game_data.entities 
USING BTREE (((default_position_3d->>'z')::float));

-- 복합 인덱스 (x, y, z 조합 쿼리 최적화)
CREATE INDEX IF NOT EXISTS idx_entities_position_xyz ON game_data.entities 
USING BTREE (
    ((default_position_3d->>'x')::float),
    ((default_position_3d->>'y')::float),
    ((default_position_3d->>'z')::float)
);

-- 2. World Object 위치 좌표 인덱스
CREATE INDEX IF NOT EXISTS idx_world_objects_position_x ON game_data.world_objects 
USING BTREE (((default_position->>'x')::float));

CREATE INDEX IF NOT EXISTS idx_world_objects_position_y ON game_data.world_objects 
USING BTREE (((default_position->>'y')::float));

-- 복합 인덱스 (x, y 조합 쿼리 최적화)
CREATE INDEX IF NOT EXISTS idx_world_objects_position_xy ON game_data.world_objects 
USING BTREE (
    ((default_position->>'x')::float),
    ((default_position->>'y')::float)
);

-- 3. Cell ID와 위치 조합 인덱스 (가장 자주 사용되는 쿼리 패턴)
-- Cell 내 위치 기반 조회 최적화
CREATE INDEX IF NOT EXISTS idx_entities_cell_position ON game_data.entities 
USING GIN (
    (default_position_3d -> 'cell_id'),
    ((default_position_3d->>'x')::float),
    ((default_position_3d->>'y')::float)
);

CREATE INDEX IF NOT EXISTS idx_world_objects_cell_position ON game_data.world_objects 
USING BTREE (
    default_cell_id,
    ((default_position->>'x')::float),
    ((default_position->>'y')::float)
);

-- =====================================================
-- 인덱스 추가 완료
-- =====================================================

COMMENT ON INDEX idx_entities_position_x IS 'Entity x 좌표 기반 쿼리 최적화';
COMMENT ON INDEX idx_entities_position_y IS 'Entity y 좌표 기반 쿼리 최적화';
COMMENT ON INDEX idx_entities_position_z IS 'Entity z 좌표 기반 쿼리 최적화';
COMMENT ON INDEX idx_entities_position_xyz IS 'Entity x, y, z 좌표 복합 쿼리 최적화';
COMMENT ON INDEX idx_world_objects_position_x IS 'World Object x 좌표 기반 쿼리 최적화';
COMMENT ON INDEX idx_world_objects_position_y IS 'World Object y 좌표 기반 쿼리 최적화';
COMMENT ON INDEX idx_world_objects_position_xy IS 'World Object x, y 좌표 복합 쿼리 최적화';
COMMENT ON INDEX idx_entities_cell_position IS 'Cell ID와 위치 조합 쿼리 최적화';
COMMENT ON INDEX idx_world_objects_cell_position IS 'Cell ID와 위치 조합 쿼리 최적화';

