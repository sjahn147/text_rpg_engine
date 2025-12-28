-- Runtime Data: Object States
-- ID 명명 규칙: UUID v4 사용
CREATE TABLE runtime_data.object_states (
    state_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    runtime_object_id UUID NOT NULL,
    current_state JSONB, -- 현재 상태
    current_position JSONB, -- 현재 위치 (이동 가능한 오브젝트의 경우)
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (runtime_object_id) REFERENCES reference_layer.object_references(runtime_object_id)
); 