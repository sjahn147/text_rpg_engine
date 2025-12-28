-- 누락된 테이블 생성
-- runtime_data.cell_occupants 테이블 생성

CREATE TABLE IF NOT EXISTS runtime_data.cell_occupants (
    cell_id VARCHAR(255) NOT NULL,
    entity_id VARCHAR(255) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    position JSONB,
    entered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (cell_id, entity_id),
    FOREIGN KEY (cell_id) REFERENCES runtime_data.runtime_cells(cell_id) ON DELETE CASCADE,
    FOREIGN KEY (entity_id) REFERENCES runtime_data.runtime_entities(entity_id) ON DELETE CASCADE
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_cell_occupants_cell_id ON runtime_data.cell_occupants(cell_id);
CREATE INDEX IF NOT EXISTS idx_cell_occupants_entity_id ON runtime_data.cell_occupants(entity_id);
CREATE INDEX IF NOT EXISTS idx_cell_occupants_entered_at ON runtime_data.cell_occupants(entered_at);

-- 코멘트 추가
COMMENT ON TABLE runtime_data.cell_occupants IS '셀 내 엔티티 위치 정보';
COMMENT ON COLUMN runtime_data.cell_occupants.cell_id IS '셀 ID';
COMMENT ON COLUMN runtime_data.cell_occupants.entity_id IS '엔티티 ID';
COMMENT ON COLUMN runtime_data.cell_occupants.entity_type IS '엔티티 타입';
COMMENT ON COLUMN runtime_data.cell_occupants.position IS '셀 내 위치 (JSONB)';
COMMENT ON COLUMN runtime_data.cell_occupants.entered_at IS '진입 시간';
