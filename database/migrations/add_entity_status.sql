-- Entity Status 필드 추가 마이그레이션
-- World Editor에서 Entity의 상태를 관리할 수 있도록 함

-- 1. entity_status 필드 추가
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'game_data' 
        AND table_name = 'entities' 
        AND column_name = 'entity_status'
    ) THEN
        ALTER TABLE game_data.entities
        ADD COLUMN entity_status VARCHAR(20) DEFAULT 'active'
        CHECK (entity_status IN ('active', 'inactive', 'dead', 'hidden'));
        
        COMMENT ON COLUMN game_data.entities.entity_status IS '엔티티 상태 (active, inactive, dead, hidden)';
    END IF;
END $$;

-- 2. 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_entity_status ON game_data.entities(entity_status);

