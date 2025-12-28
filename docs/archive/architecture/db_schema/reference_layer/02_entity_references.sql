-- Reference Layer: Entity References
CREATE TABLE reference_layer.entity_references (
    runtime_entity_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    game_entity_id VARCHAR(50) NOT NULL,    -- Game DB의 entity_id
    session_id VARCHAR(100) NOT NULL,       -- 세션 식별자
    entity_type VARCHAR(50) NOT NULL,   -- 'player', 'npc', 'monster'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- session_id 컬럼을 UUID 타입으로 변경하는 ALTER 문
ALTER TABLE reference_layer.entity_references
    ALTER COLUMN session_id TYPE UUID USING session_id::UUID;

-- Foreign Key 제약조건 추가
ALTER TABLE reference_layer.entity_references
ADD CONSTRAINT fk_entity_game_entity
FOREIGN KEY (game_entity_id) 
REFERENCES game_data.entities(entity_id);

ALTER TABLE reference_layer.entity_references
ADD CONSTRAINT fk_entity_session
FOREIGN KEY (session_id) 
REFERENCES runtime_data.active_sessions(session_id);

-- 참조 업데이트 시 세션 활성 시간 갱신 트리거
CREATE OR REPLACE FUNCTION reference_layer.update_session_activity()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE runtime_data.active_sessions
    SET last_active_at = CURRENT_TIMESTAMP
    WHERE session_id = NEW.session_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;