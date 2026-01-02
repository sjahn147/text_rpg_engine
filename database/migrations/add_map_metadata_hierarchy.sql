-- =====================================================
-- Map Metadata 계층 구조 필드 추가 마이그레이션
-- =====================================================
-- Phase 1.3: Map Metadata 확장
-- 
-- 추가 필드:
-- - map_level: VARCHAR(20) - 맵 레벨 (world, region, location, cell)
-- - parent_entity_id: VARCHAR(50) - 부모 엔티티 ID
-- - parent_entity_type: VARCHAR(20) - 부모 엔티티 타입 (region, location, cell)
-- =====================================================

-- 1. Map Metadata 계층 구조 필드 추가
ALTER TABLE game_data.map_metadata
ADD COLUMN IF NOT EXISTS map_level VARCHAR(20) DEFAULT 'world',
ADD COLUMN IF NOT EXISTS parent_entity_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS parent_entity_type VARCHAR(20);

-- 2. map_level 제약조건 추가
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_map_level' 
        AND conrelid = 'game_data.map_metadata'::regclass
    ) THEN
        ALTER TABLE game_data.map_metadata
        ADD CONSTRAINT chk_map_level CHECK (
            map_level IN ('world', 'region', 'location', 'cell')
        );
    END IF;
END $$;

-- 3. parent_entity_type 제약조건 추가
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_parent_entity_type' 
        AND conrelid = 'game_data.map_metadata'::regclass
    ) THEN
        ALTER TABLE game_data.map_metadata
        ADD CONSTRAINT chk_parent_entity_type CHECK (
            parent_entity_type IS NULL OR parent_entity_type IN ('region', 'location', 'cell')
        );
    END IF;
END $$;

-- 4. 기존 데이터에 기본값 설정 (world 레벨)
UPDATE game_data.map_metadata
SET map_level = 'world'
WHERE map_level IS NULL;

-- 5. 코멘트 추가
COMMENT ON COLUMN game_data.map_metadata.map_level IS '맵 레벨: world (전역), region (지역), location (장소), cell (셀)';
COMMENT ON COLUMN game_data.map_metadata.parent_entity_id IS '부모 엔티티 ID (예: region_id, location_id, cell_id)';
COMMENT ON COLUMN game_data.map_metadata.parent_entity_type IS '부모 엔티티 타입: region, location, cell';

-- 6. 인덱스 추가 (계층 구조 쿼리 최적화)
CREATE INDEX IF NOT EXISTS idx_map_metadata_level ON game_data.map_metadata(map_level);
CREATE INDEX IF NOT EXISTS idx_map_metadata_parent ON game_data.map_metadata(parent_entity_id, parent_entity_type);
CREATE INDEX IF NOT EXISTS idx_map_metadata_parent_type ON game_data.map_metadata(parent_entity_type);

-- 7. 외래키 제약조건 (선택사항 - 참조 무결성 보장)
-- 주의: 이 부분은 기존 데이터에 영향을 줄 수 있으므로 주의해서 실행
-- 필요시 별도 스크립트로 실행

-- Region 참조
-- ALTER TABLE game_data.map_metadata
-- ADD CONSTRAINT IF NOT EXISTS fk_map_metadata_region 
-- FOREIGN KEY (parent_entity_id) REFERENCES game_data.world_regions(region_id) ON DELETE CASCADE
-- WHERE parent_entity_type = 'region';

-- Location 참조
-- ALTER TABLE game_data.map_metadata
-- ADD CONSTRAINT IF NOT EXISTS fk_map_metadata_location 
-- FOREIGN KEY (parent_entity_id) REFERENCES game_data.world_locations(location_id) ON DELETE CASCADE
-- WHERE parent_entity_type = 'location';

-- Cell 참조
-- ALTER TABLE game_data.map_metadata
-- ADD CONSTRAINT IF NOT EXISTS fk_map_metadata_cell 
-- FOREIGN KEY (parent_entity_id) REFERENCES game_data.world_cells(cell_id) ON DELETE CASCADE
-- WHERE parent_entity_type = 'cell';

-- =====================================================
-- 마이그레이션 완료
-- =====================================================

