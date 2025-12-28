-- Runtime Data: Entity States
-- ID 명명 규칙: UUID v4 사용
CREATE TABLE runtime_data.entity_states (
    state_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    runtime_entity_id UUID NOT NULL,
    runtime_cell_id UUID NOT NULL,
    current_stats JSONB, -- 현재 상태 (HP, MP 등)
    current_position JSONB, -- 현재 위치
    active_effects JSONB, -- 적용 중인 효과들
    inventory JSONB, -- 보유 아이템
    equipped_items JSONB, -- 장착 중인 장비
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (runtime_entity_id) REFERENCES reference_layer.entity_references(runtime_entity_id),
    FOREIGN KEY (runtime_cell_id) REFERENCES reference_layer.cell_references(runtime_cell_id)
); 