-- Runtime Data: Entity State History
-- ID 명명 규칙: UUID v4 사용
CREATE TABLE runtime_data.entity_state_history (
    history_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    runtime_entity_id UUID NOT NULL,
    change_type VARCHAR(50) NOT NULL,  -- 'position', 'stats', 'effect_applied', 'effect_removed'
    previous_value JSONB NOT NULL,     -- 변경 전 값
    new_value JSONB NOT NULL,          -- 변경 후 값
    reason TEXT,                       -- 변경 사유
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (runtime_entity_id) REFERENCES reference_layer.entity_references(runtime_entity_id)
);

-- 인덱스 생성
CREATE INDEX idx_entity_state_history_entity ON runtime_data.entity_state_history(runtime_entity_id);
CREATE INDEX idx_entity_state_history_type ON runtime_data.entity_state_history(change_type);
CREATE INDEX idx_entity_state_history_time ON runtime_data.entity_state_history(created_at);

COMMENT ON TABLE runtime_data.entity_state_history IS '엔티티 상태 변경 이력';
COMMENT ON COLUMN runtime_data.entity_state_history.change_type IS '변경 유형:
- position: 위치 변경
- stats: 스탯 변경
- effect_applied: 효과 적용
- effect_removed: 효과 제거'; 