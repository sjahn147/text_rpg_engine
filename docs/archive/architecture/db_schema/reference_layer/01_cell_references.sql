-- Reference Layer: Cell References
CREATE TABLE reference_layer.cell_references (
    runtime_cell_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    game_cell_id VARCHAR(50) NOT NULL,      -- Game DB의 cell_id
    session_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_cell_id) REFERENCES game_data.world_cells(cell_id)
); 