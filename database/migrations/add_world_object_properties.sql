-- =====================================================
-- World Objects 기본 특성 필드 추가 마이그레이션
-- =====================================================
-- Phase 1.2: World Objects 필드 추가
-- 
-- 추가 필드:
-- - wall_mounted: BOOLEAN - 벽에 부착된 객체인지 여부
-- - passable: BOOLEAN - Entity가 통과 가능한지 여부
-- - movable: BOOLEAN - 이동 가능한 객체인지 여부
-- - object_height: FLOAT - 객체 높이 (충돌 검사용)
-- - object_width: FLOAT - 객체 너비 (충돌 검사용)
-- - object_depth: FLOAT - 객체 깊이 (충돌 검사용)
-- - object_weight: FLOAT - 객체 무게
-- =====================================================

-- 1. World Objects 기본 특성 필드 추가
ALTER TABLE game_data.world_objects
ADD COLUMN IF NOT EXISTS wall_mounted BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS passable BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS movable BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS object_height FLOAT DEFAULT 1.0,
ADD COLUMN IF NOT EXISTS object_width FLOAT DEFAULT 1.0,
ADD COLUMN IF NOT EXISTS object_depth FLOAT DEFAULT 1.0,
ADD COLUMN IF NOT EXISTS object_weight FLOAT DEFAULT 0.0;

-- 2. 제약조건 추가 (물리적 크기는 양수여야 함)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_object_dimensions_positive' 
        AND conrelid = 'game_data.world_objects'::regclass
    ) THEN
        ALTER TABLE game_data.world_objects
        ADD CONSTRAINT chk_object_dimensions_positive CHECK (
            object_height > 0 AND object_width > 0 AND object_depth > 0 AND object_weight >= 0
        );
    END IF;
END $$;

-- 3. 코멘트 추가
COMMENT ON COLUMN game_data.world_objects.wall_mounted IS '벽에 부착된 객체인지 여부 (예: 벽걸이, 창문)';
COMMENT ON COLUMN game_data.world_objects.passable IS 'Entity가 통과 가능한지 여부 (예: 문이 열려있을 때, 창문)';
COMMENT ON COLUMN game_data.world_objects.movable IS '이동 가능한 객체인지 여부 (예: 상자, 의자)';
COMMENT ON COLUMN game_data.world_objects.object_height IS '객체 높이 (미터 단위, 충돌 검사용)';
COMMENT ON COLUMN game_data.world_objects.object_width IS '객체 너비 (미터 단위, 충돌 검사용)';
COMMENT ON COLUMN game_data.world_objects.object_depth IS '객체 깊이 (미터 단위, 충돌 검사용)';
COMMENT ON COLUMN game_data.world_objects.object_weight IS '객체 무게 (킬로그램 단위)';

-- 4. 인덱스 추가 (passable, movable 필터링 최적화)
CREATE INDEX IF NOT EXISTS idx_world_objects_passable ON game_data.world_objects(passable);
CREATE INDEX IF NOT EXISTS idx_world_objects_movable ON game_data.world_objects(movable);
CREATE INDEX IF NOT EXISTS idx_world_objects_wall_mounted ON game_data.world_objects(wall_mounted);

-- =====================================================
-- 객체 타입별 기본값 업데이트 (선택사항)
-- =====================================================
-- 주의: 이 부분은 기존 데이터에 영향을 줄 수 있으므로 주의해서 실행
-- 필요시 별도 스크립트로 실행

-- 문 (door) 기본값
-- UPDATE game_data.world_objects
-- SET wall_mounted = TRUE, passable = FALSE, movable = FALSE,
--     object_height = 2.0, object_width = 1.0, object_depth = 0.2
-- WHERE object_type = 'door' AND (wall_mounted IS NULL OR passable IS NULL);

-- 창문 (window) 기본값
-- UPDATE game_data.world_objects
-- SET wall_mounted = TRUE, passable = FALSE, movable = FALSE,
--     object_height = 1.5, object_width = 1.0, object_depth = 0.1
-- WHERE object_type = 'window' AND (wall_mounted IS NULL OR passable IS NULL);

-- 상자 (chest) 기본값
-- UPDATE game_data.world_objects
-- SET wall_mounted = FALSE, passable = FALSE, movable = TRUE,
--     object_height = 0.8, object_width = 1.0, object_depth = 0.8, object_weight = 50.0
-- WHERE object_type = 'chest' AND (wall_mounted IS NULL OR passable IS NULL);

-- =====================================================
-- 마이그레이션 완료
-- =====================================================

