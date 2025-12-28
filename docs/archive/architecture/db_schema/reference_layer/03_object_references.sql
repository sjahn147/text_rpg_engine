-- Reference Layer: Object References
CREATE TABLE reference_layer.object_references (
    runtime_object_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    game_object_id VARCHAR(50) NOT NULL,    -- Game DB의 object_id
    session_id VARCHAR(100) NOT NULL,
    object_type VARCHAR(50) NOT NULL,   -- 'static', 'interactive'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_object_id) REFERENCES game_data.world_objects(object_id)
); 