-- Runtime Data: Event Consequences
-- ID 명명 규칙: UUID v4 사용
CREATE TABLE runtime_data.event_consequences (
    consequence_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    choice_id UUID NOT NULL,
    consequence_type VARCHAR(50) NOT NULL,
    consequence_data JSONB, -- 결과 상세 데이터
    affected_entities JSONB, -- 영향 받은 엔티티들
    affected_objects JSONB, -- 영향 받은 오브젝트들
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (choice_id) REFERENCES runtime_data.player_choices(choice_id)
); 