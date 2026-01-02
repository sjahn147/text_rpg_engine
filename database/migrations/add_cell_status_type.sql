-- Cell Status 및 Cell Type 필드 추가 마이그레이션
-- World Editor에서 Cell의 상태와 타입을 관리할 수 있도록 함

-- 1. cell_status 필드 추가
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'game_data' 
        AND table_name = 'world_cells' 
        AND column_name = 'cell_status'
    ) THEN
        ALTER TABLE game_data.world_cells
        ADD COLUMN cell_status VARCHAR(20) DEFAULT 'active'
        CHECK (cell_status IN ('active', 'inactive', 'locked', 'dangerous'));
        
        COMMENT ON COLUMN game_data.world_cells.cell_status IS '셀 상태 (active, inactive, locked, dangerous)';
    END IF;
END $$;

-- 2. cell_type 필드 추가
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'game_data' 
        AND table_name = 'world_cells' 
        AND column_name = 'cell_type'
    ) THEN
        ALTER TABLE game_data.world_cells
        ADD COLUMN cell_type VARCHAR(20) DEFAULT 'indoor'
        CHECK (cell_type IN ('indoor', 'outdoor', 'dungeon', 'shop', 'tavern', 'temple'));
        
        COMMENT ON COLUMN game_data.world_cells.cell_type IS '셀 타입 (indoor, outdoor, dungeon, shop, tavern, temple)';
    END IF;
END $$;

-- 3. 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_cell_status ON game_data.world_cells(cell_status);
CREATE INDEX IF NOT EXISTS idx_cell_type ON game_data.world_cells(cell_type);

