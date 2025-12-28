-- =====================================================
-- Entity 위치 및 크기 필드 추가 마이그레이션
-- =====================================================
-- Phase 1.1: Entity 필드 추가
-- 
-- 추가 필드:
-- - default_position_3d: JSONB - Entity 기본 위치 (3D 좌표, cell_id 포함)
-- - entity_size: VARCHAR(20) - Entity 크기 (D&D 스타일)
-- =====================================================

-- 1. Entity 기본 위치 필드 추가
ALTER TABLE game_data.entities
ADD COLUMN IF NOT EXISTS default_position_3d JSONB;

COMMENT ON COLUMN game_data.entities.default_position_3d IS '엔티티 기본 위치 (3D 좌표, cell_id 포함). 구조: {"x": 5.0, "y": 4.0, "z": 0.0, "rotation_y": 0, "cell_id": "CELL_MARKET_001"}';

-- 2. Entity 크기 필드 추가
ALTER TABLE game_data.entities
ADD COLUMN IF NOT EXISTS entity_size VARCHAR(20);

-- 3. Entity 크기 제약조건 추가 (D&D 5e 크기 시스템)
-- 제약조건이 이미 존재하는지 확인 후 추가
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_entity_size' 
        AND conrelid = 'game_data.entities'::regclass
    ) THEN
        ALTER TABLE game_data.entities
        ADD CONSTRAINT chk_entity_size CHECK (
            entity_size IS NULL OR entity_size IN ('tiny', 'small', 'medium', 'large', 'huge', 'gargantuan')
        );
    END IF;
END $$;

-- 4. Entity 크기 기본값 설정
ALTER TABLE game_data.entities
ALTER COLUMN entity_size SET DEFAULT 'medium';

-- 5. 기존 데이터에 기본값 설정
UPDATE game_data.entities
SET entity_size = 'medium'
WHERE entity_size IS NULL;

-- 6. Entity 크기 NOT NULL 제약조건 추가
-- 컬럼이 이미 NOT NULL이 아닌 경우에만 설정
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'game_data' 
        AND table_name = 'entities' 
        AND column_name = 'entity_size' 
        AND is_nullable = 'YES'
    ) THEN
        ALTER TABLE game_data.entities
        ALTER COLUMN entity_size SET NOT NULL;
    END IF;
END $$;

COMMENT ON COLUMN game_data.entities.entity_size IS '엔티티 크기 (D&D 스타일: tiny, small, medium, large, huge, gargantuan). 기본값: medium';

-- 7. 인덱스 추가 (cell_id 기반 쿼리 최적화를 위한 GIN 인덱스)
-- default_position_3d의 cell_id를 빠르게 조회하기 위한 인덱스
CREATE INDEX IF NOT EXISTS idx_entities_position_cell ON game_data.entities 
USING GIN ((default_position_3d -> 'cell_id'));

-- 8. entity_size 인덱스 추가 (크기별 필터링 최적화)
CREATE INDEX IF NOT EXISTS idx_entities_size ON game_data.entities(entity_size);

-- =====================================================
-- 마이그레이션 완료
-- =====================================================

