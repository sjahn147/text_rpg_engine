-- World data setup

-- 1. Regions
INSERT INTO game_data.world_regions 
(region_id, region_name, region_description, region_type, region_properties) 
VALUES
('REG_NORTH_FOREST_001', 'North Forest', 'Peaceful forest region', 'forest', 
 '{"climate": "temperate", "danger_level": 2, "recommended_level": {"min": 1, "max": 10}}'),
('REG_EAST_DESERT_001', 'East Desert', 'Dry desert region', 'desert', 
 '{"climate": "arid", "danger_level": 4, "recommended_level": {"min": 15, "max": 25}}'),
('REG_WEST_MOUNTAIN_001', 'West Mountains', 'Rugged mountain region', 'mountain', 
 '{"climate": "cold", "danger_level": 5, "recommended_level": {"min": 20, "max": 30}}'),
('REG_SOUTH_COAST_001', 'South Coast', 'Mild coastal region', 'coast', 
 '{"climate": "mild", "danger_level": 1, "recommended_level": {"min": 1, "max": 5}}');

-- 2. Locations
INSERT INTO game_data.world_locations 
(location_id, region_id, location_name, location_description, location_type, location_properties) 
VALUES
('LOC_FOREST_VILLAGE_001', 'REG_NORTH_FOREST_001', 'Forest Village', 'Peaceful village in the forest', 'village', 
 '{"background_music": "peaceful_village", "ambient_effects": ["birds", "wind"]}'),
('LOC_FOREST_SHOP_001', 'REG_NORTH_FOREST_001', 'Village Shop', 'Weapon and armor shop', 'shop', 
 '{"background_music": "shop_theme", "ambient_effects": ["indoor"]}');

-- 3. Cells
INSERT INTO game_data.world_cells 
(cell_id, location_id, cell_name, matrix_width, matrix_height, cell_description, cell_properties) 
VALUES
('CELL_VILLAGE_CENTER_001', 'LOC_FOREST_VILLAGE_001', 'Village Center', 20, 20, 'Central square of the village', 
 '{"terrain": "stone", "weather": "clear"}'),
('CELL_SHOP_INTERIOR_001', 'LOC_FOREST_SHOP_001', 'Shop Interior', 10, 8, 'Interior of the shop', 
 '{"terrain": "wooden_floor", "lighting": "bright"}');

-- 4. Objects
INSERT INTO game_data.world_objects 
(object_id, object_type, object_name, object_description, default_cell_id, default_position, interaction_type, possible_states, properties) 
VALUES
('OBJ_SHOP_COUNTER_001', 'static', 'Shop Counter', 'Counter displaying weapons', 'CELL_SHOP_INTERIOR_001', 
 '{"x": 5, "y": 4}', 'none', '["intact"]', 
 '{"material": "wood", "durability": 100}'),
('OBJ_CHEST_STORAGE_001', 'interactive', 'Storage Chest', 'Chest storing merchant items', 'CELL_SHOP_INTERIOR_001', 
 '{"x": 8, "y": 7}', 'openable', '["closed", "open"]', 
 '{"material": "wood", "locked": false, "contents": ["WEAPON_SWORD_001", "ARMOR_LEATHER_001"]}');

SELECT 'World data setup completed!' as message;
