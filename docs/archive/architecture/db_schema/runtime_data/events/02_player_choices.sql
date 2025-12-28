-- Runtime Data: Player Choices
-- ID 명명 규칙: UUID v4 사용
CREATE TABLE runtime_data.player_choices (
    choice_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID NOT NULL,
    choice_type VARCHAR(50) NOT NULL,
    choice_data JSONB, -- 선택 상세 데이터
    made_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES runtime_data.triggered_events(event_id)
); 