-- Runtime Data: Triggered Events
-- ID 명명 규칙: UUID v4 사용
CREATE TABLE runtime_data.triggered_events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB, -- 이벤트 상세 데이터
    source_entity_ref UUID, -- 이벤트 발생 주체
    target_entity_ref UUID, -- 이벤트 대상
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES runtime_data.active_sessions(session_id),
    FOREIGN KEY (source_entity_ref) REFERENCES reference_layer.entity_references(runtime_entity_id),
    FOREIGN KEY (target_entity_ref) REFERENCES reference_layer.entity_references(runtime_entity_id)
); 