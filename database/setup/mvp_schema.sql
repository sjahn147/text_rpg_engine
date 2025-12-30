-- =====================================================
-- RPG Engine MVP v2 최종 데이터베이스 스키마
-- 모든 기능을 포함한 완전한 스키마
-- =====================================================

-- UUID 지원을 위한 확장 설치
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- 스키마 생성
-- =====================================================
CREATE SCHEMA IF NOT EXISTS game_data;
CREATE SCHEMA IF NOT EXISTS reference_layer;
CREATE SCHEMA IF NOT EXISTS runtime_data;

COMMENT ON SCHEMA game_data IS '불변의 게임 원본 데이터';
COMMENT ON SCHEMA reference_layer IS '게임 데이터와 런타임 데이터 간의 참조 관계';
COMMENT ON SCHEMA runtime_data IS '실행 중인 게임의 상태 데이터';

-- =====================================================
-- GAME DATA SCHEMA - 게임 월드 및 엔티티 정의
-- =====================================================

-- Default Values (애플리케이션 기본값 관리)
CREATE TABLE game_data.default_values (
    setting_id VARCHAR(50) PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    setting_name VARCHAR(100) NOT NULL,
    setting_value JSONB NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_default_values_category ON game_data.default_values(category);
CREATE INDEX idx_default_values_active ON game_data.default_values(is_active);

COMMENT ON TABLE game_data.default_values IS '애플리케이션 전반에 사용되는 기본 설정값 및 상수 관리';
COMMENT ON COLUMN game_data.default_values.setting_id IS '설정 항목의 고유 키 (예: "CELL_DEFAULT_SIZE", "ENTITY_DEFAULT_POSITION")';
COMMENT ON COLUMN game_data.default_values.setting_value IS '설정 값 (JSONB 형태로 다양한 데이터 타입 저장 가능)';

-- Game World: Regions
-- ID 명명 규칙: REG_[대륙]_[지역]_[일련번호]
CREATE TABLE game_data.world_regions (
    region_id VARCHAR(50) PRIMARY KEY,
    region_name VARCHAR(100) NOT NULL,
    region_description TEXT,
    region_type VARCHAR(50),
    region_properties JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_region_type ON game_data.world_regions(region_type);

COMMENT ON TABLE game_data.world_regions IS '게임 내 최상위 지역 구분';
COMMENT ON COLUMN game_data.world_regions.region_properties IS 'JSONB 구조: {"climate": "temperate", "danger_level": 3, "recommended_level": {"min": 1, "max": 10}, ...}';

-- Game World: Locations
-- ID 명명 규칙: LOC_[지역]_[장소]_[일련번호]
CREATE TABLE game_data.world_locations (
    location_id VARCHAR(50) PRIMARY KEY,
    region_id VARCHAR(50) NOT NULL,
    location_name VARCHAR(100) NOT NULL,
    location_description TEXT,
    location_type VARCHAR(50),
    location_properties JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (region_id) REFERENCES game_data.world_regions(region_id) ON DELETE RESTRICT
);

CREATE INDEX idx_location_region ON game_data.world_locations(region_id);
CREATE INDEX idx_location_type ON game_data.world_locations(location_type);

COMMENT ON TABLE game_data.world_locations IS '게임 내 구체적 장소 정의';
COMMENT ON COLUMN game_data.world_locations.location_properties IS 'JSONB 구조: {"background_music": "peaceful_01", "ambient_effects": ["birds", "wind"], "ownership": {"owner_entity_id": "NPC_OWNER_001", "ownership_type": "private"}, "lore": {"history": "...", "legends": [...]}, "detail_sections": [...]}. SSOT 원칙: ownership.owner_entity_id는 entities 테이블을 참조하며, owner_name은 저장하지 않음 (JOIN으로 조회)';

-- Game World: Cells
-- ID 명명 규칙: CELL_[위치타입]_[세부위치]_[일련번호]
CREATE TABLE game_data.world_cells (
    cell_id VARCHAR(50) PRIMARY KEY,
    location_id VARCHAR(50) NOT NULL,
    cell_name VARCHAR(100),
    matrix_width INTEGER NOT NULL,
    matrix_height INTEGER NOT NULL,
    cell_description TEXT,
    cell_properties JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES game_data.world_locations(location_id) ON DELETE RESTRICT
);

CREATE INDEX idx_cell_location ON game_data.world_cells(location_id);

COMMENT ON TABLE game_data.world_cells IS '게임 내 셀 단위 공간 정의';
COMMENT ON COLUMN game_data.world_cells.cell_properties IS 'JSONB 구조: {"terrain": "grass", "weather": "clear", "ownership": {"owner_entity_id": "NPC_OWNER_001", "is_private": false}, "lore": {"history": "...", "legends": [...]}, "environment": {"terrain": "...", "weather": "...", "lighting": "..."}, "detail_sections": [...]}. SSOT 원칙: ownership.owner_entity_id는 entities 테이블을 참조하며, owner_name은 저장하지 않음 (JOIN으로 조회)';

-- =====================================================
-- 대화 시스템 테이블들 (entities 테이블보다 먼저 생성)
-- =====================================================

-- 대화 컨텍스트 정의
CREATE TABLE game_data.dialogue_contexts (
    dialogue_id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    entity_id VARCHAR(50),                          -- NULL 허용 (모든 entity 해당)
    cell_id VARCHAR(50),                            -- NULL 허용 (모든 위치 해당)
    time_category VARCHAR(20),                      -- NULL 허용 (모든 시간 해당)
    event_id VARCHAR(50),                           -- NULL 허용 (이벤트 무관)
    priority INTEGER DEFAULT 0,
    available_topics JSONB,
    entity_personality TEXT,
    constraints JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dialogue_contexts_composite ON game_data.dialogue_contexts(entity_id, cell_id, time_category, event_id);
CREATE INDEX idx_dialogue_priority ON game_data.dialogue_contexts(priority DESC);

COMMENT ON TABLE game_data.dialogue_contexts IS '대화 컨텍스트와 조건을 통합 관리하는 테이블 (NULL 조건은 해당 조건이 없음을 의미)';
COMMENT ON COLUMN game_data.dialogue_contexts.available_topics IS 'JSONB 구조: {"topics": ["topic1", "topic2"], "default_topic": "greeting", "topic_requirements": {...}}';
COMMENT ON COLUMN game_data.dialogue_contexts.constraints IS 'JSONB 구조: {"max_response_length": 100, "tone": "friendly", "required_keywords": [...]}';

-- 대화 주제 및 추가 정보
CREATE TABLE game_data.dialogue_topics (
    topic_id VARCHAR(50) PRIMARY KEY,
    dialogue_id VARCHAR(50) NOT NULL,
    topic_type VARCHAR(50),
    content TEXT,
    conditions JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dialogue_id) REFERENCES game_data.dialogue_contexts(dialogue_id) ON DELETE CASCADE
);

CREATE INDEX idx_topic_dialogue ON game_data.dialogue_topics(dialogue_id);
CREATE INDEX idx_topic_type ON game_data.dialogue_topics(topic_type);

COMMENT ON TABLE game_data.dialogue_topics IS '대화와 연관된 추가 정보나 분기를 저장하는 테이블';

-- 대화 지식 베이스
CREATE TABLE game_data.dialogue_knowledge (
    knowledge_id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    knowledge_type VARCHAR(50) NOT NULL,
    related_entities JSONB,
    related_topics JSONB,
    knowledge_properties JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_knowledge_type ON game_data.dialogue_knowledge(knowledge_type);

COMMENT ON TABLE game_data.dialogue_knowledge IS '대화 시스템에서 참조할 수 있는 지식 베이스';
COMMENT ON COLUMN game_data.dialogue_knowledge.related_entities IS 'JSONB 구조: {"npcs": ["NPC_001"], "locations": ["LOCATION_001"], ...}';
COMMENT ON COLUMN game_data.dialogue_knowledge.related_topics IS 'JSONB 구조: {"main_topics": ["topic1"], "sub_topics": ["sub1", "sub2"], ...}';
COMMENT ON COLUMN game_data.dialogue_knowledge.knowledge_properties IS 'JSONB 구조: {"importance": 5, "reveal_conditions": {"quest_stage": 2}, ...}';

-- =====================================================
-- 게임 엔티티 및 속성 정의
-- =====================================================

-- Game Entities: Core
-- ID 명명 규칙: [종족]_[직업/역할]_[일련번호]
CREATE TABLE game_data.entities (
    entity_id VARCHAR(50) PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,
    entity_name VARCHAR(100) NOT NULL,
    entity_description TEXT,
    base_stats JSONB,
    default_equipment JSONB,
    default_abilities JSONB,
    default_inventory JSONB,
    entity_properties JSONB,
    dialogue_context_id VARCHAR(50),                -- 대화 컨텍스트 참조
    default_position_3d JSONB,                     -- Entity 기본 위치 (3D 좌표, cell_id 포함)
    entity_size VARCHAR(20) NOT NULL DEFAULT 'medium',  -- Entity 크기 (D&D 스타일)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dialogue_context_id) REFERENCES game_data.dialogue_contexts(dialogue_id) ON DELETE SET NULL,
    CONSTRAINT chk_entity_size CHECK (
        entity_size IN ('tiny', 'small', 'medium', 'large', 'huge', 'gargantuan')
    )
);

CREATE INDEX idx_entities_type ON game_data.entities(entity_type);
CREATE INDEX idx_entities_position_cell ON game_data.entities USING GIN ((default_position_3d -> 'cell_id'));
CREATE INDEX idx_entities_size ON game_data.entities(entity_size);

COMMENT ON TABLE game_data.entities IS '게임 내 모든 엔티티(캐릭터, NPC, 몬스터 등)의 기본 정의';
COMMENT ON COLUMN game_data.entities.base_stats IS 'JSONB 구조: {"hp": 100, "mp": 50, "strength": 10, ...}';
COMMENT ON COLUMN game_data.entities.default_equipment IS 'JSONB 구조: {"weapon": "WEAPON_SWORD_NORMAL_001", "armor": "ARMOR_PLATE_NORMAL_001", ...}';
COMMENT ON COLUMN game_data.entities.default_abilities IS 'JSONB 구조: {"skills": ["SKILL_WARRIOR_SLASH_001"], "magic": ["MAGIC_FIRE_BALL_001"], ...}';
COMMENT ON COLUMN game_data.entities.default_inventory IS 'JSONB 구조: {"items": ["ITEM_POTION_HEAL_001"], "quantities": {"ITEM_POTION_HEAL_001": 5}, ...}';
COMMENT ON COLUMN game_data.entities.entity_properties IS 'JSONB 구조: {"is_hostile": false, "interaction_flags": ["can_trade", "can_talk"], ...}';
COMMENT ON COLUMN game_data.entities.default_position_3d IS '엔티티 기본 위치 (3D 좌표, cell_id 포함). 구조: {"x": 5.0, "y": 4.0, "z": 0.0, "rotation_y": 0, "cell_id": "CELL_MARKET_001"}';
COMMENT ON COLUMN game_data.entities.entity_size IS '엔티티 크기 (D&D 스타일: tiny, small, medium, large, huge, gargantuan). 기본값: medium';

-- Game World: Objects
CREATE TABLE game_data.world_objects (
    object_id VARCHAR(50) PRIMARY KEY,
    object_type VARCHAR(50) NOT NULL,
    object_name VARCHAR(100) NOT NULL,
    object_description TEXT,
    default_cell_id VARCHAR(50),
    default_position JSONB,
    interaction_type VARCHAR(50),
    possible_states JSONB,
    properties JSONB,
    wall_mounted BOOLEAN DEFAULT FALSE,
    passable BOOLEAN DEFAULT FALSE,
    movable BOOLEAN DEFAULT FALSE,
    object_height FLOAT DEFAULT 1.0,
    object_width FLOAT DEFAULT 1.0,
    object_depth FLOAT DEFAULT 1.0,
    object_weight FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (default_cell_id) REFERENCES game_data.world_cells(cell_id) ON DELETE SET NULL,
    CONSTRAINT chk_object_dimensions_positive CHECK (
        object_height > 0 AND object_width > 0 AND object_depth > 0 AND object_weight >= 0
    )
);

CREATE INDEX idx_object_type ON game_data.world_objects(object_type);
CREATE INDEX idx_world_objects_passable ON game_data.world_objects(passable);
CREATE INDEX idx_world_objects_movable ON game_data.world_objects(movable);
CREATE INDEX idx_world_objects_wall_mounted ON game_data.world_objects(wall_mounted);

COMMENT ON TABLE game_data.world_objects IS '게임 내 오브젝트 정의';
COMMENT ON COLUMN game_data.world_objects.object_type IS 'static, interactive, trigger';
COMMENT ON COLUMN game_data.world_objects.interaction_type IS 'none, openable, triggerable';
COMMENT ON COLUMN game_data.world_objects.wall_mounted IS '벽에 부착된 객체인지 여부 (예: 벽걸이, 창문)';
COMMENT ON COLUMN game_data.world_objects.passable IS 'Entity가 통과 가능한지 여부 (예: 문이 열려있을 때, 창문)';
COMMENT ON COLUMN game_data.world_objects.movable IS '이동 가능한 객체인지 여부 (예: 상자, 의자)';
COMMENT ON COLUMN game_data.world_objects.object_height IS '객체 높이 (미터 단위, 충돌 검사용)';
COMMENT ON COLUMN game_data.world_objects.object_width IS '객체 너비 (미터 단위, 충돌 검사용)';
COMMENT ON COLUMN game_data.world_objects.object_depth IS '객체 깊이 (미터 단위, 충돌 검사용)';
COMMENT ON COLUMN game_data.world_objects.object_weight IS '객체 무게 (킬로그램 단위)';

-- Game Entities: Base Properties
-- ID 명명 규칙: PROP_[속성분류]_[세부속성]_[일련번호]
CREATE TABLE game_data.base_properties (
    property_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL,
    base_effects JSONB,
    requirements JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_base_properties_type ON game_data.base_properties(type);

COMMENT ON TABLE game_data.base_properties IS '게임 내 모든 속성들의 기본 정의';
COMMENT ON COLUMN game_data.base_properties.type IS 'equipment, ability, item, effect';
COMMENT ON COLUMN game_data.base_properties.base_effects IS 'JSONB 구조: {"damage": 10, "defense": 5, "duration": 30, ...}';
COMMENT ON COLUMN game_data.base_properties.requirements IS 'JSONB 구조: {"level": 5, "strength": 10, "skills": ["SKILL_WARRIOR_BASIC"], ...}';

-- Game Entities: Abilities - Magic
-- ID 명명 규칙: MAGIC_[속성]_[효과]_[일련번호]
CREATE TABLE game_data.abilities_magic (
    magic_id VARCHAR(50) PRIMARY KEY,
    base_property_id VARCHAR(50) NOT NULL,
    mana_cost INTEGER,
    cast_time INTEGER,
    magic_school VARCHAR(50),
    magic_properties JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (base_property_id) REFERENCES game_data.base_properties(property_id) ON DELETE CASCADE
);

CREATE INDEX idx_magic_school ON game_data.abilities_magic(magic_school);

COMMENT ON TABLE game_data.abilities_magic IS '게임 내 마법 능력 정의';
COMMENT ON COLUMN game_data.abilities_magic.magic_properties IS 'JSONB 구조: {"damage": 50, "area_effect": {"radius": 3, "type": "circle"}, "status_effects": ["burning"], ...}';

-- Game Entities: Abilities - Skills
-- ID 명명 규칙: SKILL_[직업/계열]_[효과]_[일련번호]
CREATE TABLE game_data.abilities_skills (
    skill_id VARCHAR(50) PRIMARY KEY,
    base_property_id VARCHAR(50) NOT NULL,
    cooldown INTEGER,
    skill_type VARCHAR(50),
    skill_properties JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (base_property_id) REFERENCES game_data.base_properties(property_id) ON DELETE CASCADE
);

CREATE INDEX idx_skill_type ON game_data.abilities_skills(skill_type);

COMMENT ON TABLE game_data.abilities_skills IS '게임 내 기술 능력 정의';
COMMENT ON COLUMN game_data.abilities_skills.skill_properties IS 'JSONB 구조: {"damage_multiplier": 1.5, "range": 2, "combo_bonus": {"hits": 3, "damage": 1.2}, ...}';

-- Game Entities: Effects
-- ID 명명 규칙: EFFECT_[효과종류]_[상태]_[일련번호]
CREATE TABLE game_data.effects (
    effect_id VARCHAR(50) PRIMARY KEY,
    base_property_id VARCHAR(50) NOT NULL,
    effect_type VARCHAR(50),
    duration INTEGER,
    effect_properties JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (base_property_id) REFERENCES game_data.base_properties(property_id) ON DELETE CASCADE
);

CREATE INDEX idx_effect_type ON game_data.effects(effect_type);

COMMENT ON TABLE game_data.effects IS '게임 내 상태 효과 정의';
COMMENT ON COLUMN game_data.effects.effect_type IS 'buff, debuff, condition, temporary';
COMMENT ON COLUMN game_data.effects.duration IS '-1 for permanent';
COMMENT ON COLUMN game_data.effects.effect_properties IS 'JSONB 구조: {"strength_mod": 10, "tick_damage": 5, "resist_chance": 20, ...}';

-- Game Entities: Equipment - Weapons
-- ID 명명 규칙: WEAPON_[무기종류]_[등급]_[일련번호]
CREATE TABLE game_data.equipment_weapons (
    weapon_id VARCHAR(50) PRIMARY KEY,
    base_property_id VARCHAR(50) NOT NULL,
    damage INTEGER,
    weapon_type VARCHAR(50),
    durability INTEGER,
    weapon_properties JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (base_property_id) REFERENCES game_data.base_properties(property_id) ON DELETE CASCADE
);

CREATE INDEX idx_weapons_type ON game_data.equipment_weapons(weapon_type);

COMMENT ON TABLE game_data.equipment_weapons IS '게임 내 무기 장비 정의';
COMMENT ON COLUMN game_data.equipment_weapons.weapon_properties IS 'JSONB 구조: {"element": "fire", "critical_chance": 10, "special_effects": ["bleeding"], ...}';

-- Game Entities: Equipment - Armors
-- ID 명명 규칙: ARMOR_[방어구종류]_[등급]_[일련번호]
CREATE TABLE game_data.equipment_armors (
    armor_id VARCHAR(50) PRIMARY KEY,
    base_property_id VARCHAR(50) NOT NULL,
    defense INTEGER,
    armor_type VARCHAR(50),
    weight INTEGER,
    armor_properties JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (base_property_id) REFERENCES game_data.base_properties(property_id) ON DELETE CASCADE
);

CREATE INDEX idx_armors_type ON game_data.equipment_armors(armor_type);

COMMENT ON TABLE game_data.equipment_armors IS '게임 내 방어구 장비 정의';
COMMENT ON COLUMN game_data.equipment_armors.armor_properties IS 'JSONB 구조: {"elemental_resistance": {"fire": 20, "ice": -10}, "special_effects": ["regeneration"], ...}';

-- Game Entities: Items
-- ID 명명 규칙: ITEM_[아이템종류]_[효과]_[일련번호]
CREATE TABLE game_data.items (
    item_id VARCHAR(50) PRIMARY KEY,
    base_property_id VARCHAR(50) NOT NULL,
    item_type VARCHAR(50),
    stack_size INTEGER DEFAULT 1,
    consumable BOOLEAN DEFAULT false,
    item_properties JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (base_property_id) REFERENCES game_data.base_properties(property_id) ON DELETE CASCADE
);

CREATE INDEX idx_items_type ON game_data.items(item_type);

COMMENT ON TABLE game_data.items IS '게임 내 아이템 정의';
COMMENT ON COLUMN game_data.items.item_properties IS 'JSONB 구조: {"healing_amount": 50, "duration": 30, "special_effects": ["poison_cure"], ...}';

-- =====================================================
-- World Editor Tables
-- =====================================================

-- World Roads (지역 간 도로 연결 정보)
CREATE TABLE game_data.world_roads (
    road_id VARCHAR(50) PRIMARY KEY,
    from_region_id VARCHAR(50),
    from_location_id VARCHAR(50),
    to_region_id VARCHAR(50),
    to_location_id VARCHAR(50),
    from_pin_id VARCHAR(50),
    to_pin_id VARCHAR(50),
    road_type VARCHAR(50) NOT NULL DEFAULT 'normal',
    distance DECIMAL(10, 2),
    travel_time INTEGER,
    danger_level INTEGER DEFAULT 1,
    color VARCHAR(7) DEFAULT '#8B4513',
    width INTEGER DEFAULT 2,
    dashed BOOLEAN DEFAULT false,
    road_properties JSONB DEFAULT '{}',
    path_coordinates JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_region_id) REFERENCES game_data.world_regions(region_id) ON DELETE CASCADE,
    FOREIGN KEY (to_region_id) REFERENCES game_data.world_regions(region_id) ON DELETE CASCADE,
    FOREIGN KEY (from_location_id) REFERENCES game_data.world_locations(location_id) ON DELETE CASCADE,
    FOREIGN KEY (to_location_id) REFERENCES game_data.world_locations(location_id) ON DELETE CASCADE
);

CREATE INDEX idx_roads_from_region ON game_data.world_roads(from_region_id);
CREATE INDEX idx_roads_to_region ON game_data.world_roads(to_region_id);
CREATE INDEX idx_roads_from_location ON game_data.world_roads(from_location_id);
CREATE INDEX idx_roads_to_location ON game_data.world_roads(to_location_id);
CREATE INDEX idx_roads_type ON game_data.world_roads(road_type);
CREATE INDEX idx_roads_from_pin ON game_data.world_roads(from_pin_id);
CREATE INDEX idx_roads_to_pin ON game_data.world_roads(to_pin_id);

COMMENT ON TABLE game_data.world_roads IS '지역 간 도로 연결 정보';
COMMENT ON COLUMN game_data.world_roads.path_coordinates IS 'JSONB 배열: [{"x": 100, "y": 200}, ...] - 지도상 경로 좌표';
COMMENT ON COLUMN game_data.world_roads.road_properties IS 'JSONB 구조: {"conditions": [...], "visual": {...}}';
COMMENT ON COLUMN game_data.world_roads.road_type IS '도로 타입: normal, hidden, river, mountain_pass';
COMMENT ON COLUMN game_data.world_roads.from_pin_id IS '시작 핀 ID (핀 기반 연결)';
COMMENT ON COLUMN game_data.world_roads.to_pin_id IS '종료 핀 ID (핀 기반 연결)';

-- Map Metadata (월드 에디터 지도 메타데이터)
CREATE TABLE game_data.map_metadata (
    map_id VARCHAR(50) PRIMARY KEY DEFAULT 'default_map',
    map_name VARCHAR(100) NOT NULL DEFAULT 'World Map',
    background_image VARCHAR(255) DEFAULT 'assets/world_editor/worldmap.png',
    background_color VARCHAR(7) DEFAULT '#FFFFFF',
    width INTEGER NOT NULL DEFAULT 1920,
    height INTEGER NOT NULL DEFAULT 1080,
    grid_enabled BOOLEAN DEFAULT false,
    grid_size INTEGER DEFAULT 50,
    zoom_level DECIMAL(3, 2) DEFAULT 1.0,
    viewport_x INTEGER DEFAULT 0,
    viewport_y INTEGER DEFAULT 0,
    map_level VARCHAR(20) DEFAULT 'world',
    parent_entity_id VARCHAR(50),
    parent_entity_type VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_map_level CHECK (
        map_level IN ('world', 'region', 'location', 'cell')
    ),
    CONSTRAINT chk_parent_entity_type CHECK (
        parent_entity_type IS NULL OR parent_entity_type IN ('region', 'location', 'cell')
    )
);

CREATE INDEX idx_map_metadata_name ON game_data.map_metadata(map_name);
CREATE INDEX idx_map_metadata_level ON game_data.map_metadata(map_level);
CREATE INDEX idx_map_metadata_parent ON game_data.map_metadata(parent_entity_id, parent_entity_type);
CREATE INDEX idx_map_metadata_parent_type ON game_data.map_metadata(parent_entity_type);

COMMENT ON TABLE game_data.map_metadata IS '월드 에디터 지도 메타데이터';
COMMENT ON COLUMN game_data.map_metadata.background_image IS '지도 배경 이미지 경로 (기본값: assets/world_editor/worldmap.png)';
COMMENT ON COLUMN game_data.map_metadata.map_level IS '맵 레벨: world (전역), region (지역), location (장소), cell (셀)';
COMMENT ON COLUMN game_data.map_metadata.parent_entity_id IS '부모 엔티티 ID (예: region_id, location_id, cell_id)';
COMMENT ON COLUMN game_data.map_metadata.parent_entity_type IS '부모 엔티티 타입: region, location, cell';

-- Pin Positions (월드 에디터 핀 위치 정보)
CREATE TABLE game_data.pin_positions (
    pin_id VARCHAR(50) PRIMARY KEY,
    game_data_id VARCHAR(50) NOT NULL,
    pin_type VARCHAR(20) NOT NULL,  -- 'region', 'location', 'cell'
    pin_name VARCHAR(100) NOT NULL DEFAULT '새 핀 01',
    x INTEGER NOT NULL,
    y INTEGER NOT NULL,
    icon_type VARCHAR(50) DEFAULT 'default',
    color VARCHAR(7) DEFAULT '#FF6B9D',
    size INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(game_data_id, pin_type)
);

CREATE INDEX idx_pin_positions_type ON game_data.pin_positions(pin_type);
CREATE INDEX idx_pin_positions_game_data ON game_data.pin_positions(game_data_id);
CREATE INDEX idx_pin_positions_coords ON game_data.pin_positions(x, y);

COMMENT ON TABLE game_data.pin_positions IS '월드 에디터 핀 위치 정보';
COMMENT ON COLUMN game_data.pin_positions.game_data_id IS '연결된 게임 데이터 ID (region_id, location_id, cell_id)';
COMMENT ON COLUMN game_data.pin_positions.pin_type IS '핀 타입: region, location, cell';
COMMENT ON COLUMN game_data.pin_positions.pin_name IS '핀 표시 이름 (사용자 친화적 이름)';
COMMENT ON COLUMN game_data.pin_positions.icon_type IS '아이콘 타입: city, village, dungeon, shop, etc.';

-- Pin과 Road 외래키 연결
ALTER TABLE game_data.world_roads
ADD CONSTRAINT fk_roads_from_pin 
    FOREIGN KEY (from_pin_id) 
    REFERENCES game_data.pin_positions(pin_id) 
    ON DELETE CASCADE;

ALTER TABLE game_data.world_roads
ADD CONSTRAINT fk_roads_to_pin 
    FOREIGN KEY (to_pin_id) 
    REFERENCES game_data.pin_positions(pin_id) 
    ON DELETE CASCADE;

-- =====================================================
-- REFERENCE LAYER SCHEMA - 참조 관계 관리
-- =====================================================

-- Entity References
CREATE TABLE reference_layer.entity_references (
    runtime_entity_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    game_entity_id VARCHAR(50) NOT NULL,
    session_id UUID NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    is_player BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_entity_id) REFERENCES game_data.entities(entity_id) ON DELETE RESTRICT
    -- session/runtime FKs added in idempotent block below
);

CREATE INDEX idx_entity_references_session ON reference_layer.entity_references(session_id);
CREATE INDEX idx_entity_references_type ON reference_layer.entity_references(entity_type);
CREATE INDEX idx_entity_references_player ON reference_layer.entity_references(is_player);

-- 게임 데이터 엔티티 타입 인덱스
CREATE INDEX idx_entity_type ON game_data.entities(entity_type);

COMMENT ON TABLE reference_layer.entity_references IS '게임 데이터 엔티티와 런타임 엔티티 간의 참조 관계';
COMMENT ON COLUMN reference_layer.entity_references.is_player IS '플레이어 엔티티 여부';

-- Cell References
CREATE TABLE reference_layer.cell_references (
    runtime_cell_id UUID PRIMARY KEY,
    game_cell_id VARCHAR(50) NOT NULL,
    session_id UUID NOT NULL,
    cell_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_cell_id) REFERENCES game_data.world_cells(cell_id) ON DELETE RESTRICT
    -- session/runtime FKs added in idempotent block below
);

CREATE INDEX idx_cell_references_session ON reference_layer.cell_references(session_id);
CREATE INDEX idx_cell_references_type ON reference_layer.cell_references(cell_type);

COMMENT ON TABLE reference_layer.cell_references IS '게임 데이터 셀과 런타임 셀 간의 참조 관계';

-- Object References
CREATE TABLE reference_layer.object_references (
    runtime_object_id UUID PRIMARY KEY,
    game_object_id VARCHAR(50) NOT NULL,
    session_id UUID NOT NULL,
    object_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_object_id) REFERENCES game_data.world_objects(object_id) ON DELETE RESTRICT
    -- session/runtime FKs added in idempotent block below
);

CREATE INDEX idx_object_references_session ON reference_layer.object_references(session_id);
CREATE INDEX idx_object_references_type ON reference_layer.object_references(object_type);

COMMENT ON TABLE reference_layer.object_references IS '게임 데이터 오브젝트와 런타임 오브젝트 간의 참조 관계';

-- =====================================================
-- RUNTIME DATA SCHEMA - 세션 중심 설계
-- =====================================================

-- Active Sessions (세션 중심 설계의 핵심)
CREATE TABLE runtime_data.active_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_name VARCHAR(100) NOT NULL DEFAULT 'Unnamed Session',
    session_state VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP,
    metadata JSONB,
    player_runtime_entity_id UUID                            -- 선택적 플레이어 참조
);

CREATE INDEX idx_sessions_state ON runtime_data.active_sessions(session_state);
CREATE INDEX idx_sessions_last_active ON runtime_data.active_sessions(last_active_at);

COMMENT ON TABLE runtime_data.active_sessions IS '게임 세션 관리 테이블 (세션 중심 설계)';
COMMENT ON COLUMN runtime_data.active_sessions.session_state IS '세션 상태: active(활성), paused(일시중지), ending(종료중), closed(종료됨)';
COMMENT ON COLUMN runtime_data.active_sessions.metadata IS 'JSON 구조: {"client_info": {}, "connection_data": {}, "game_settings": {}}';
COMMENT ON COLUMN runtime_data.active_sessions.player_runtime_entity_id IS '선택적 플레이어 참조 (NULL 허용)';

-- Runtime Entities (참조만 저장)
CREATE TABLE runtime_data.runtime_entities (
    runtime_entity_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    game_entity_id VARCHAR(50) NOT NULL,
    session_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_entity_id) REFERENCES game_data.entities(entity_id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES runtime_data.active_sessions(session_id) ON DELETE CASCADE
);

CREATE INDEX idx_runtime_entity_game ON runtime_data.runtime_entities(game_entity_id);
CREATE INDEX idx_runtime_entity_session ON runtime_data.runtime_entities(session_id);

COMMENT ON TABLE runtime_data.runtime_entities IS '런타임 엔티티 참조 (게임 데이터와 세션 연결)';
COMMENT ON COLUMN runtime_data.runtime_entities.game_entity_id IS '게임 데이터 엔티티 참조';
COMMENT ON COLUMN runtime_data.runtime_entities.session_id IS '세션 참조';

-- Runtime Cells (참조만 저장)
CREATE TABLE runtime_data.runtime_cells (
    runtime_cell_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    game_cell_id VARCHAR(50) NOT NULL,
    session_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    cell_type VARCHAR(50) NOT NULL DEFAULT 'indoor',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_cell_id) REFERENCES game_data.world_cells(cell_id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES runtime_data.active_sessions(session_id) ON DELETE CASCADE
);

CREATE INDEX idx_runtime_cell_game ON runtime_data.runtime_cells(game_cell_id);
CREATE INDEX idx_runtime_cell_session ON runtime_data.runtime_cells(session_id);

COMMENT ON TABLE runtime_data.runtime_cells IS '런타임 셀 참조 (게임 데이터와 세션 연결)';
COMMENT ON COLUMN runtime_data.runtime_cells.game_cell_id IS '게임 데이터 셀 참조';
COMMENT ON COLUMN runtime_data.runtime_cells.session_id IS '세션 참조';

-- Runtime Objects (참조만 저장)
CREATE TABLE runtime_data.runtime_objects (
    runtime_object_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    game_object_id VARCHAR(50) NOT NULL,
    session_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_object_id) REFERENCES game_data.world_objects(object_id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES runtime_data.active_sessions(session_id) ON DELETE CASCADE
);

CREATE INDEX idx_runtime_object_game ON runtime_data.runtime_objects(game_object_id);
CREATE INDEX idx_runtime_object_session ON runtime_data.runtime_objects(session_id);

COMMENT ON TABLE runtime_data.runtime_objects IS '런타임 오브젝트 참조 (게임 데이터와 세션 연결)';
COMMENT ON COLUMN runtime_data.runtime_objects.game_object_id IS '게임 데이터 오브젝트 참조';
COMMENT ON COLUMN runtime_data.runtime_objects.session_id IS '세션 참조';

-- Cell-Entity Relationships
CREATE TABLE runtime_data.runtime_cell_entities (
    runtime_cell_id UUID NOT NULL,
    runtime_entity_id UUID NOT NULL,
    position JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (runtime_cell_id, runtime_entity_id),
    FOREIGN KEY (runtime_cell_id) REFERENCES runtime_data.runtime_cells(runtime_cell_id) ON DELETE CASCADE,
    FOREIGN KEY (runtime_entity_id) REFERENCES runtime_data.runtime_entities(runtime_entity_id) ON DELETE CASCADE
);

COMMENT ON TABLE runtime_data.runtime_cell_entities IS '셀-엔티티 관계 (위치 정보 포함)';

-- Cell Occupants (셀 내 엔티티 위치 정보)
CREATE TABLE runtime_data.cell_occupants (
    runtime_cell_id UUID NOT NULL,
    runtime_entity_id UUID NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    position JSONB,
    entered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (runtime_cell_id, runtime_entity_id),
    FOREIGN KEY (runtime_cell_id) REFERENCES runtime_data.runtime_cells(runtime_cell_id) ON DELETE CASCADE,
    FOREIGN KEY (runtime_entity_id) REFERENCES runtime_data.runtime_entities(runtime_entity_id) ON DELETE CASCADE
);

-- 인덱스 생성
CREATE INDEX idx_cell_occupants_cell_id ON runtime_data.cell_occupants(runtime_cell_id);
CREATE INDEX idx_cell_occupants_entity_id ON runtime_data.cell_occupants(runtime_entity_id);
CREATE INDEX idx_cell_occupants_entered_at ON runtime_data.cell_occupants(entered_at);

-- 코멘트 추가
COMMENT ON TABLE runtime_data.cell_occupants IS '셀 내 엔티티 위치 정보';
COMMENT ON COLUMN runtime_data.cell_occupants.runtime_cell_id IS '런타임 셀 ID';
COMMENT ON COLUMN runtime_data.cell_occupants.runtime_entity_id IS '런타임 엔티티 ID';
COMMENT ON COLUMN runtime_data.cell_occupants.entity_type IS '엔티티 타입';
COMMENT ON COLUMN runtime_data.cell_occupants.position IS '셀 내 위치 (JSONB)';
COMMENT ON COLUMN runtime_data.cell_occupants.entered_at IS '진입 시간';
-- SSOT: 위치의 기록/갱신은 runtime_data.entity_states.current_position이 단일 진실원;
-- cell_occupants는 조회 편의를 위한 파생 테이블로 서비스 로직만이 갱신하도록 제한한다.

-- Cell-Object Relationships
CREATE TABLE runtime_data.runtime_cell_objects (
    runtime_cell_id UUID NOT NULL,
    runtime_object_id UUID NOT NULL,
    position JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (runtime_cell_id, runtime_object_id),
    FOREIGN KEY (runtime_cell_id) REFERENCES runtime_data.runtime_cells(runtime_cell_id) ON DELETE CASCADE,
    FOREIGN KEY (runtime_object_id) REFERENCES runtime_data.runtime_objects(runtime_object_id) ON DELETE CASCADE
);

COMMENT ON TABLE runtime_data.runtime_cell_objects IS '셀-오브젝트 관계 (위치 정보 포함)';

-- FK backfills (idempotent, after runtime_data tables exist)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_entity_references_session'
    ) THEN
        ALTER TABLE reference_layer.entity_references
        ADD CONSTRAINT fk_entity_references_session
        FOREIGN KEY (session_id) REFERENCES runtime_data.active_sessions(session_id) ON DELETE CASCADE;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_entity_references_runtime'
    ) THEN
        ALTER TABLE reference_layer.entity_references
        ADD CONSTRAINT fk_entity_references_runtime
        FOREIGN KEY (runtime_entity_id) REFERENCES runtime_data.runtime_entities(runtime_entity_id) ON DELETE CASCADE;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_cell_references_session'
    ) THEN
        ALTER TABLE reference_layer.cell_references
        ADD CONSTRAINT fk_cell_references_session
        FOREIGN KEY (session_id) REFERENCES runtime_data.active_sessions(session_id) ON DELETE CASCADE;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_cell_references_runtime'
    ) THEN
        ALTER TABLE reference_layer.cell_references
        ADD CONSTRAINT fk_cell_references_runtime
        FOREIGN KEY (runtime_cell_id) REFERENCES runtime_data.runtime_cells(runtime_cell_id) ON DELETE CASCADE;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_object_references_session'
    ) THEN
        ALTER TABLE reference_layer.object_references
        ADD CONSTRAINT fk_object_references_session
        FOREIGN KEY (session_id) REFERENCES runtime_data.active_sessions(session_id) ON DELETE CASCADE;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_object_references_runtime'
    ) THEN
        ALTER TABLE reference_layer.object_references
        ADD CONSTRAINT fk_object_references_runtime
        FOREIGN KEY (runtime_object_id) REFERENCES runtime_data.runtime_objects(runtime_object_id) ON DELETE CASCADE;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_active_sessions_player'
    ) THEN
        ALTER TABLE runtime_data.active_sessions
        ADD CONSTRAINT fk_active_sessions_player
        FOREIGN KEY (player_runtime_entity_id) REFERENCES runtime_data.runtime_entities(runtime_entity_id) ON DELETE SET NULL;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_entity_references_session_entity'
    ) THEN
        ALTER TABLE reference_layer.entity_references
        ADD CONSTRAINT uq_entity_references_session_entity UNIQUE (session_id, game_entity_id);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_cell_references_session_cell'
    ) THEN
        ALTER TABLE reference_layer.cell_references
        ADD CONSTRAINT uq_cell_references_session_cell UNIQUE (session_id, game_cell_id);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace 
        WHERE c.relname = 'idx_entity_states_session_entity' AND n.nspname = 'runtime_data'
    ) THEN
        CREATE INDEX idx_entity_states_session_entity 
        ON runtime_data.entity_states(session_id, runtime_entity_id);
    END IF;
END $$;

-- Validation helpers (run manually as needed before/after migration)
-- 1) Detect bad runtime_cell_id strings before generated column cast:
-- SELECT state_id, current_position FROM runtime_data.entity_states
-- WHERE NOT (
--     jsonb_typeof(current_position -> 'runtime_cell_id') = 'string'
--     AND (current_position->>'runtime_cell_id') ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
-- ) AND current_position IS NOT NULL;
--
-- 2) Cell occupants CASCADE sanity (should delete occupant when runtime_cell is removed):
-- WITH _c AS (
--   INSERT INTO runtime_data.runtime_cells (runtime_cell_id, game_cell_id, session_id) VALUES (uuid_generate_v4(), 'CELL_VILLAGE_CENTER_001', uuid_generate_v4()) RETURNING runtime_cell_id
-- ), _e AS (
--   INSERT INTO runtime_data.runtime_entities (runtime_entity_id, game_entity_id, session_id) SELECT uuid_generate_v4(), 'NPC_VILLAGER_001', uuid_generate_v4() RETURNING runtime_entity_id
-- )
-- INSERT INTO runtime_data.cell_occupants SELECT _c.runtime_cell_id, _e.runtime_entity_id, 'npc', '{}'::jsonb, now() FROM _c,_e;
-- SELECT COUNT(*) FROM runtime_data.cell_occupants WHERE runtime_cell_id IN (SELECT runtime_cell_id FROM _c);
-- DELETE FROM runtime_data.runtime_cells WHERE runtime_cell_id IN (SELECT runtime_cell_id FROM _c);
-- SELECT COUNT(*) FROM runtime_data.cell_occupants WHERE runtime_cell_id IN (SELECT runtime_cell_id FROM _c);
--
-- 3) Session delete cascading reference_layer rows:
-- DELETE FROM runtime_data.active_sessions WHERE session_id = '<test-session-uuid>';

-- Runtime Events
CREATE TABLE runtime_data.runtime_events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    runtime_cell_id UUID NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    conditions JSONB,
    consequences JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (runtime_cell_id) REFERENCES runtime_data.runtime_cells(runtime_cell_id) ON DELETE CASCADE
);

CREATE INDEX idx_runtime_event_cell ON runtime_data.runtime_events(runtime_cell_id);
CREATE INDEX idx_runtime_event_type ON runtime_data.runtime_events(event_type);
CREATE INDEX idx_runtime_event_active ON runtime_data.runtime_events(is_active);

COMMENT ON TABLE runtime_data.runtime_events IS '런타임 이벤트 데이터';
COMMENT ON COLUMN runtime_data.runtime_events.conditions IS 'JSONB 구조: 이벤트 발생 조건';
COMMENT ON COLUMN runtime_data.runtime_events.consequences IS 'JSONB 구조: 이벤트 결과';

-- Dialogue History
CREATE TABLE runtime_data.dialogue_history (
    history_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL,
    runtime_entity_id UUID NOT NULL,
    context_id VARCHAR(50) NOT NULL,
    speaker_type VARCHAR(50),
    message TEXT,
    relevant_knowledge JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (runtime_entity_id) REFERENCES runtime_data.runtime_entities(runtime_entity_id),
    FOREIGN KEY (context_id) REFERENCES game_data.dialogue_contexts(dialogue_id),
    FOREIGN KEY (session_id) REFERENCES runtime_data.active_sessions(session_id)
);

CREATE INDEX idx_dialogue_history_session ON runtime_data.dialogue_history(session_id);
CREATE INDEX idx_dialogue_history_entity ON runtime_data.dialogue_history(runtime_entity_id);
CREATE INDEX idx_dialogue_history_timestamp ON runtime_data.dialogue_history(timestamp);

COMMENT ON TABLE runtime_data.dialogue_history IS '대화 기록 테이블';
COMMENT ON COLUMN runtime_data.dialogue_history.speaker_type IS 'player, npc, system';
COMMENT ON COLUMN runtime_data.dialogue_history.relevant_knowledge IS 'JSONB 구조: {"knowledge_id": 123, "used_content": "content", "context_flags": ["flag1", "flag2"]}';

-- Dialogue States
CREATE TABLE runtime_data.dialogue_states (
    state_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL,
    runtime_entity_id UUID NOT NULL,
    current_context_id VARCHAR(50),
    conversation_state JSONB,
    active_topics JSONB,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (runtime_entity_id) REFERENCES runtime_data.runtime_entities(runtime_entity_id),
    FOREIGN KEY (current_context_id) REFERENCES game_data.dialogue_contexts(dialogue_id),
    FOREIGN KEY (session_id) REFERENCES runtime_data.active_sessions(session_id)
);

CREATE INDEX idx_dialogue_states_session ON runtime_data.dialogue_states(session_id);
CREATE INDEX idx_dialogue_states_entity ON runtime_data.dialogue_states(runtime_entity_id);

COMMENT ON TABLE runtime_data.dialogue_states IS '대화 상태 테이블';
COMMENT ON COLUMN runtime_data.dialogue_states.conversation_state IS 'JSONB 구조: {"current_topic": "topic", "emotion": "neutral", "last_mentioned_item": null, "context_memory": [...]}';
COMMENT ON COLUMN runtime_data.dialogue_states.active_topics IS 'JSONB 구조: {"current_topics": ["topic1"], "available_topics": ["topic2", "topic3"], "locked_topics": []}';

-- Action Logs
CREATE TABLE runtime_data.action_logs (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL,
    player_id VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    success BOOLEAN NOT NULL,
    message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES runtime_data.active_sessions(session_id)
);

CREATE INDEX idx_action_logs_session ON runtime_data.action_logs(session_id);
CREATE INDEX idx_action_logs_player ON runtime_data.action_logs(player_id);
CREATE INDEX idx_action_logs_timestamp ON runtime_data.action_logs(timestamp);

COMMENT ON TABLE runtime_data.action_logs IS '플레이어 행동 기록';
COMMENT ON COLUMN runtime_data.action_logs.action IS 'investigate, dialogue, trade, visit, wait, move, attack, use_item';

-- Player Choices
CREATE TABLE runtime_data.player_choices (
    choice_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL,
    player_id VARCHAR(50) NOT NULL,
    choice_type VARCHAR(50) NOT NULL,
    choice_data JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES runtime_data.active_sessions(session_id)
);

CREATE INDEX idx_player_choices_session ON runtime_data.player_choices(session_id);
CREATE INDEX idx_player_choices_player ON runtime_data.player_choices(player_id);
CREATE INDEX idx_player_choices_type ON runtime_data.player_choices(choice_type);

COMMENT ON TABLE runtime_data.player_choices IS '플레이어 선택 기록';
COMMENT ON COLUMN runtime_data.player_choices.choice_data IS 'JSONB 구조: 선택 세부 정보';

-- Triggered Events
CREATE TABLE runtime_data.triggered_events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB,
    source_entity_ref UUID,
    target_entity_ref UUID,
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES runtime_data.active_sessions(session_id),
    FOREIGN KEY (source_entity_ref) REFERENCES reference_layer.entity_references(runtime_entity_id),
    FOREIGN KEY (target_entity_ref) REFERENCES reference_layer.entity_references(runtime_entity_id)
);

CREATE INDEX idx_triggered_events_session ON runtime_data.triggered_events(session_id);
CREATE INDEX idx_triggered_events_type ON runtime_data.triggered_events(event_type);
CREATE INDEX idx_triggered_events_triggered_at ON runtime_data.triggered_events(triggered_at);

COMMENT ON TABLE runtime_data.triggered_events IS '트리거 이벤트 테이블';
COMMENT ON COLUMN runtime_data.triggered_events.event_data IS 'JSONB 구조: 이벤트 세부 데이터';

-- Event Consequences
CREATE TABLE runtime_data.event_consequences (
    consequence_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID NOT NULL,
    consequence_type VARCHAR(50) NOT NULL,
    consequence_data JSONB,
    affected_entities JSONB,
    affected_objects JSONB,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES runtime_data.triggered_events(event_id) ON DELETE CASCADE
);

CREATE INDEX idx_event_consequences_event ON runtime_data.event_consequences(event_id);
CREATE INDEX idx_event_consequences_type ON runtime_data.event_consequences(consequence_type);

COMMENT ON TABLE runtime_data.event_consequences IS '이벤트 결과 테이블';
COMMENT ON COLUMN runtime_data.event_consequences.consequence_data IS 'JSONB 구조: 결과 세부 데이터';

-- =====================================================
-- GAME DATA에 시뮬레이션 관련 템플릿 추가
-- =====================================================

-- 엔티티 행동 스케줄 (시간대별 행동 정의) - 게임 데이터 템플릿
CREATE TABLE game_data.entity_behavior_schedules (
    schedule_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id VARCHAR(50) NOT NULL,
    time_period VARCHAR(20) NOT NULL,  -- 'morning', 'afternoon', 'evening', 'night'
    action_type VARCHAR(50) NOT NULL,  -- 'work', 'rest', 'socialize', 'patrol', 'sleep'
    action_priority INTEGER DEFAULT 1,
    conditions JSONB,  -- 행동 조건 (날씨, 에너지, 기분 등)
    action_data JSONB,  -- 행동 세부 데이터
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (entity_id) REFERENCES game_data.entities(entity_id) ON DELETE CASCADE
);

CREATE INDEX idx_behavior_schedule_entity ON game_data.entity_behavior_schedules(entity_id);
CREATE INDEX idx_behavior_schedule_time ON game_data.entity_behavior_schedules(time_period);
CREATE INDEX idx_behavior_schedule_action ON game_data.entity_behavior_schedules(action_type);

COMMENT ON TABLE game_data.entity_behavior_schedules IS '엔티티의 시간대별 행동 스케줄 정의 (템플릿)';
COMMENT ON COLUMN game_data.entity_behavior_schedules.conditions IS 'JSONB 구조: {"min_energy": 20, "weather": "clear", "mood": "happy"}';
COMMENT ON COLUMN game_data.entity_behavior_schedules.action_data IS 'JSONB 구조: {"duration": 2, "location": "shop", "target_entity": "merchant"}';

-- 시간 이벤트 스케줄 (게임 데이터 템플릿)
CREATE TABLE game_data.time_events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_name VARCHAR(100) NOT NULL,
    event_type VARCHAR(50) NOT NULL,  -- 'daily', 'weekly', 'monthly', 'yearly', 'custom'
    trigger_day INTEGER,  -- 특정 날짜 (NULL이면 매일)
    trigger_hour INTEGER,  -- 0-23
    trigger_minute INTEGER DEFAULT 0,  -- 0-59
    event_data JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_time_events_type ON game_data.time_events(event_type);
CREATE INDEX idx_time_events_active ON game_data.time_events(is_active);

COMMENT ON TABLE game_data.time_events IS '시간 기반 이벤트 스케줄 (템플릿)';
COMMENT ON COLUMN game_data.time_events.event_data IS 'JSONB 구조: {"description": "상점 오픈", "affected_entities": ["merchant_001"], "world_changes": {"shop_open": true}}';

-- =====================================================
-- 기존 테이블과의 연동을 위한 추가 컬럼
-- =====================================================

-- runtime_data.active_sessions에 시뮬레이션 관련 컬럼 추가
ALTER TABLE runtime_data.active_sessions 
ADD COLUMN IF NOT EXISTS simulation_mode BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS time_acceleration DECIMAL(3,1) DEFAULT 1.0;

-- Session States (세션별 상태 관리)
CREATE TABLE runtime_data.session_states (
    session_id UUID PRIMARY KEY,
    current_day INTEGER DEFAULT 1,
    current_hour INTEGER DEFAULT 6,
    current_minute INTEGER DEFAULT 0,
    last_tick TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES runtime_data.active_sessions(session_id) ON DELETE CASCADE
);

CREATE INDEX idx_session_states_time ON runtime_data.session_states(current_day, current_hour, last_tick);

COMMENT ON TABLE runtime_data.session_states IS '세션별 상태 관리 (게임 시간, 틱 등)';

-- Entity States (엔티티별 상태 관리)
CREATE TABLE runtime_data.entity_states (
    state_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    runtime_entity_id UUID NOT NULL,
    session_id UUID,
    current_stats JSONB,
    current_position JSONB,
    active_effects JSONB,
    inventory JSONB,
    equipped_items JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    current_cell_id UUID GENERATED ALWAYS AS (
        CASE 
            WHEN jsonb_typeof(current_position -> 'runtime_cell_id') = 'string'
                 AND (current_position->>'runtime_cell_id') ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
            THEN (current_position->>'runtime_cell_id')::uuid
            ELSE NULL
        END
    ) STORED,
    FOREIGN KEY (runtime_entity_id) REFERENCES runtime_data.runtime_entities(runtime_entity_id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES runtime_data.active_sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (current_cell_id) REFERENCES runtime_data.runtime_cells(runtime_cell_id) ON DELETE SET NULL
);

CREATE INDEX idx_entity_states_entity ON runtime_data.entity_states(runtime_entity_id);

COMMENT ON TABLE runtime_data.entity_states IS '엔티티별 상태 관리 (HP, MP, 위치, 인벤토리 등)';

-- Object States (오브젝트별 상태 관리)
CREATE TABLE runtime_data.object_states (
    state_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    runtime_object_id UUID NOT NULL,
    current_state JSONB,
    current_position JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (runtime_object_id) REFERENCES runtime_data.runtime_objects(runtime_object_id) ON DELETE CASCADE
);

CREATE INDEX idx_object_states_object ON runtime_data.object_states(runtime_object_id);

COMMENT ON TABLE runtime_data.object_states IS '오브젝트별 상태 관리 (내용물, 상태, 위치 등)';

-- =====================================================
-- MVP v2 핵심 기능을 위한 함수 및 프로시저
-- =====================================================

-- 시간 틱 처리 함수 (기존 session_states 활용)
CREATE OR REPLACE FUNCTION runtime_data.process_time_tick(
    p_session_id UUID
) RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    v_session_state RECORD;
    v_entity_id VARCHAR(50);
    v_action_results JSONB;
    v_total_results JSONB := '[]'::JSONB;
BEGIN
    -- 현재 세션 상태 조회
    SELECT * INTO v_session_state FROM runtime_data.session_states WHERE session_id = p_session_id;
    
    IF v_session_state IS NULL THEN
        -- 초기 시간 설정
        INSERT INTO runtime_data.session_states (session_id, current_day, current_hour, current_minute) 
        VALUES (p_session_id, 1, 6, 0);
        RETURN '{"status": "initialized", "time": "Day 1, 06:00"}'::JSONB;
    END IF;
    
    -- 모든 활성 엔티티에 대해 행동 실행
    FOR v_entity_id IN 
        SELECT DISTINCT runtime_entity_id FROM reference_layer.entity_references 
        WHERE session_id = p_session_id
    LOOP
        -- 엔티티 행동 실행 (애플리케이션 레벨에서 처리)
        v_action_results := jsonb_build_object(
            'entity_id', v_entity_id,
            'executed_at', v_session_state.last_tick + INTERVAL '1 hour',
            'success', true
        );
        v_total_results := v_total_results || v_action_results;
    END LOOP;
    
    -- 시간 업데이트
    UPDATE runtime_data.session_states 
    SET 
        current_hour = (current_hour + 1) % 24,
        current_day = CASE WHEN current_hour = 23 THEN current_day + 1 ELSE current_day END,
        last_tick = CURRENT_TIMESTAMP,
        updated_at = CURRENT_TIMESTAMP
    WHERE session_id = p_session_id;
    
    RETURN jsonb_build_object(
        'status', 'processed',
        'time', format('Day %s, %02d:00', v_session_state.current_day, v_session_state.current_hour),
        'actions_executed', jsonb_array_length(v_total_results)
    );
END;
$$;

-- =====================================================
-- MVP v2 수용 기준 검증을 위한 뷰 (기존 테이블 활용)
-- =====================================================

-- 세션별 성능 메트릭스 뷰 (기존 테이블 활용)
CREATE VIEW runtime_data.session_performance_metrics AS
SELECT 
    s.session_id,
    s.session_name,
    s.created_at as session_start,
    s.updated_at as session_last_activity,
    COUNT(DISTINCT er.runtime_entity_id) as total_entities,
    COUNT(DISTINCT te.event_id) as total_events,
    COUNT(DISTINCT dh.history_id) as total_dialogues,
    CASE 
        WHEN s.updated_at > s.created_at 
        THEN EXTRACT(EPOCH FROM (s.updated_at - s.created_at)) / 3600
        ELSE 0 
    END as session_duration_hours
FROM runtime_data.active_sessions s
LEFT JOIN reference_layer.entity_references er ON s.session_id = er.session_id
LEFT JOIN runtime_data.triggered_events te ON s.session_id = te.session_id
LEFT JOIN runtime_data.dialogue_history dh ON s.session_id = dh.session_id
WHERE s.session_state = 'active'
GROUP BY s.session_id, s.session_name, s.created_at, s.updated_at;

-- 시뮬레이션 모드 세션 성능 뷰
CREATE VIEW runtime_data.simulation_performance_metrics AS
SELECT 
    s.session_id,
    s.session_name,
    s.simulation_mode,
    s.time_acceleration,
    ss.current_day,
    ss.current_hour,
    COUNT(DISTINCT er.runtime_entity_id) as total_entities,
    COUNT(DISTINCT te.event_id) as total_events,
    COUNT(DISTINCT pc.choice_id) as total_player_choices,
    CASE 
        WHEN s.updated_at > s.created_at 
        THEN EXTRACT(EPOCH FROM (s.updated_at - s.created_at)) / 3600
        ELSE 0 
    END as simulation_duration_hours
FROM runtime_data.active_sessions s
LEFT JOIN runtime_data.session_states ss ON s.session_id = ss.session_id
LEFT JOIN reference_layer.entity_references er ON s.session_id = er.session_id
LEFT JOIN runtime_data.triggered_events te ON s.session_id = te.session_id
LEFT JOIN runtime_data.player_choices pc ON s.session_id = pc.session_id
WHERE s.simulation_mode = true
GROUP BY s.session_id, s.session_name, s.simulation_mode, s.time_acceleration, 
         ss.current_day, ss.current_hour, s.created_at, s.updated_at;

COMMENT ON VIEW runtime_data.session_performance_metrics IS '세션별 성능 메트릭스 뷰';
COMMENT ON VIEW runtime_data.simulation_performance_metrics IS '시뮬레이션 모드 세션 성능 뷰';

-- =====================================================
-- 인덱스 최적화
-- =====================================================

-- JSONB 컬럼 인덱스 (GIN)
CREATE INDEX idx_entity_properties ON game_data.entities USING GIN (entity_properties);
CREATE INDEX idx_object_properties ON game_data.world_objects USING GIN (properties);
-- JSONB properties 인덱스는 해당 컬럼이 존재할 때만 생성

-- 대화 관련 인덱스
CREATE INDEX idx_dialogue_topics ON game_data.dialogue_topics USING GIN (conditions);
CREATE INDEX idx_dialogue_available_topics ON game_data.dialogue_contexts USING GIN (available_topics);

-- 게임 데이터 행동 스케줄 조회 최적화
CREATE INDEX idx_entity_behavior_schedules_composite 
ON game_data.entity_behavior_schedules(entity_id, time_period, action_priority);

-- JSONB 컬럼 인덱스 (GIN)
CREATE INDEX idx_entity_behavior_schedules_conditions_gin 
ON game_data.entity_behavior_schedules USING GIN (conditions);

CREATE INDEX idx_entity_behavior_schedules_action_data_gin 
ON game_data.entity_behavior_schedules USING GIN (action_data);

-- 세션 상태 조회 최적화 (이미 위에서 생성됨)

-- =====================================================
-- Effect Carrier 시스템 (핵심 MVP 기능)
-- =====================================================

-- Effect Carriers (모든 효과의 통일된 관리)
CREATE TABLE game_data.effect_carriers (
    effect_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    carrier_type VARCHAR(20) NOT NULL CHECK (carrier_type IN ('skill', 'buff', 'item', 'blessing', 'curse', 'ritual')),
    effect_json JSONB NOT NULL,
    constraints_json JSONB DEFAULT '{}'::jsonb,
    source_entity_id VARCHAR(50),
    tags TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_entity_id) REFERENCES game_data.entities(entity_id) ON DELETE SET NULL
);

CREATE INDEX idx_effect_carriers_type ON game_data.effect_carriers(carrier_type);
CREATE INDEX idx_effect_carriers_effect_json ON game_data.effect_carriers USING GIN (effect_json);
CREATE INDEX idx_effect_carriers_constraints_json ON game_data.effect_carriers USING GIN (constraints_json);
CREATE INDEX idx_effect_carriers_tags ON game_data.effect_carriers USING GIN (tags);

COMMENT ON TABLE game_data.effect_carriers IS '모든 효과의 통일된 관리 (스킬, 버프, 아이템, 축복, 저주, 의식)';
COMMENT ON COLUMN game_data.effect_carriers.carrier_type IS '효과 타입: skill, buff, item, blessing, curse, ritual';
COMMENT ON COLUMN game_data.effect_carriers.effect_json IS 'JSONB 구조: 효과의 세부 데이터 (데미지, 지속시간, 조건 등)';
COMMENT ON COLUMN game_data.effect_carriers.constraints_json IS 'JSONB 구조: 사용 조건 및 제약사항';
COMMENT ON COLUMN game_data.effect_carriers.source_entity_id IS '효과의 출처 엔티티 (신격, 마법사 등)';

-- Entity Effect Ownership (엔티티가 소유한 효과)
CREATE TABLE reference_layer.entity_effect_ownership (
    session_id UUID NOT NULL,
    runtime_entity_id UUID NOT NULL,
    effect_id UUID NOT NULL,
    acquired_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (session_id, runtime_entity_id, effect_id),
    FOREIGN KEY (session_id) REFERENCES runtime_data.active_sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (runtime_entity_id) REFERENCES runtime_data.runtime_entities(runtime_entity_id) ON DELETE CASCADE,
    FOREIGN KEY (effect_id) REFERENCES game_data.effect_carriers(effect_id) ON DELETE CASCADE
);

CREATE INDEX idx_entity_effect_ownership_session ON reference_layer.entity_effect_ownership(session_id);
CREATE INDEX idx_entity_effect_ownership_entity ON reference_layer.entity_effect_ownership(runtime_entity_id);
CREATE INDEX idx_entity_effect_ownership_effect ON reference_layer.entity_effect_ownership(effect_id);
CREATE INDEX idx_entity_effect_ownership_active ON reference_layer.entity_effect_ownership(is_active);
CREATE INDEX idx_entity_effect_ownership_expires ON reference_layer.entity_effect_ownership(expires_at);

COMMENT ON TABLE reference_layer.entity_effect_ownership IS '엔티티가 소유한 Effect Carrier 관계';
COMMENT ON COLUMN reference_layer.entity_effect_ownership.source IS '효과 획득 경로 (quest, loot, spell, etc.)';
COMMENT ON COLUMN reference_layer.entity_effect_ownership.expires_at IS '효과 만료 시간 (NULL이면 영구)';

-- =====================================================
-- MVP 샘플 데이터 삽입
-- =====================================================

-- 샘플 Effect Carriers (핵심 MVP 기능)
INSERT INTO game_data.effect_carriers (name, carrier_type, effect_json, constraints_json, tags)
VALUES 
-- 스킬 효과
('Fireball', 'skill', 
 '{"damage": 50, "range": 3, "cooldown": 5, "mana_cost": 10, "target_type": "enemy", "area_of_effect": false}',
 '{"level_required": 5, "class_required": ["mage", "wizard"], "mana_required": 10}',
 ARRAY['combat', 'magic', 'fire']),

-- 버프 효과  
('Strength Boost', 'buff',
 '{"stat_modifier": {"strength": 5}, "duration": 300, "stackable": false, "removable": true}',
 '{"max_stacks": 1, "conflicts_with": ["weakness"]}',
 ARRAY['temporary', 'stat_boost']),

-- 아이템 효과
('Healing Potion', 'item',
 '{"heal_amount": 50, "instant": true, "consumable": true, "stack_size": 10}',
 '{"use_in_combat": true, "use_out_of_combat": true}',
 ARRAY['consumable', 'healing']),

-- 축복 효과
('Divine Protection', 'blessing',
 '{"damage_reduction": 0.2, "duration": 3600, "divine_source": "temple_priest", "removable": false}',
 '{"requires_faith": 50, "conflicts_with": ["curse"]}',
 ARRAY['divine', 'protection', 'long_term']),

-- 저주 효과
('Weakness', 'curse',
 '{"stat_modifier": {"strength": -3}, "duration": 1800, "removable": true, "curable": true}',
 '{"requires_curse_removal": true, "conflicts_with": ["blessing"]}',
 ARRAY['negative', 'temporary', 'curable']),

-- 의식 효과
('Summoning Ritual', 'ritual',
 '{"summon_entity": "ENTITY_SUMMONED_DEMON_001", "duration": 600, "requires_components": ["candle", "incense", "chalk"], "ritual_time": 300}',
 '{"requires_ritual_space": true, "requires_darkness": true, "level_required": 10}',
 ARRAY['ritual', 'summoning', 'complex']);

-- 샘플 Region
INSERT INTO game_data.world_regions (region_id, region_name, region_description, region_type, region_properties)
VALUES 
('REG_NORTH_FOREST_001', '북부 숲', '평화로운 숲 지역', 'forest', 
 '{"climate": "temperate", "danger_level": 2, "recommended_level": {"min": 1, "max": 10}}');

-- 샘플 Location
INSERT INTO game_data.world_locations (location_id, region_id, location_name, location_description, location_type, location_properties)
VALUES 
('LOC_FOREST_VILLAGE_001', 'REG_NORTH_FOREST_001', '숲의 마을', '평화로운 마을', 'village',
 '{"background_music": "peaceful_village", "ambient_effects": ["birds", "wind"]}'),
('LOC_FOREST_SHOP_001', 'REG_NORTH_FOREST_001', '마을 상점', '무기와 방어구를 판매하는 상점', 'shop',
 '{"background_music": "shop_theme", "ambient_effects": ["indoor"]}');

-- 샘플 Cell
INSERT INTO game_data.world_cells (cell_id, location_id, cell_name, matrix_width, matrix_height, cell_description, cell_properties)
VALUES 
('CELL_VILLAGE_CENTER_001', 'LOC_FOREST_VILLAGE_001', '마을 광장', 20, 20, '마을의 중심 광장', '{"terrain": "stone", "weather": "clear"}'),
('CELL_SHOP_INTERIOR_001', 'LOC_FOREST_SHOP_001', '상점 내부', 10, 8, '상점 안쪽', '{"terrain": "wooden_floor", "lighting": "bright"}');

-- 샘플 Entity (NPC)
INSERT INTO game_data.entities (entity_id, entity_type, entity_name, entity_description, base_stats, default_equipment, default_abilities, default_inventory, entity_properties)
VALUES 
('NPC_MERCHANT_001', 'npc', '상인 토마스', '친근한 상인', 
 '{"hp": 100, "mp": 50, "strength": 10, "intelligence": 15, "charisma": 18}',
 '{"weapon": "WEAPON_STAFF_001", "armor": "ARMOR_ROBE_001"}',
 '{"skills": ["SKILL_TRADE_001"], "magic": ["MAGIC_HEAL_001"]}',
 '{"items": ["ITEM_POTION_HEAL_001", "ITEM_SCROLL_001"], "quantities": {"ITEM_POTION_HEAL_001": 10, "ITEM_SCROLL_001": 5}}',
 '{"personality": "friendly", "gold": 1000, "interaction_flags": ["can_trade", "can_talk"], "is_hostile": false}'),
('NPC_VILLAGER_001', 'npc', '마을 주민', '평범한 마을 주민',
 '{"hp": 80, "mp": 30, "strength": 8, "intelligence": 12, "charisma": 14}',
 '{"weapon": "WEAPON_PITCHFORK_001", "armor": "ARMOR_CLOTH_001"}',
 '{"skills": ["SKILL_FARM_001"]}',
 '{"items": ["ITEM_BREAD_001"], "quantities": {"ITEM_BREAD_001": 3}}',
 '{"personality": "neutral", "knowledge": ["local_news", "village_history"], "interaction_flags": ["can_talk"], "is_hostile": false}');

-- 샘플 Object
INSERT INTO game_data.world_objects (object_id, object_type, object_name, object_description, default_cell_id, default_position, interaction_type, possible_states, properties)
VALUES 
('OBJ_SHOP_COUNTER_001', 'static', '상점 카운터', '무기를 전시하는 카운터', 'CELL_SHOP_INTERIOR_001',
 '{"x": 5, "y": 4}', 'none', '["intact"]', '{"material": "wood", "durability": 100}'),
('OBJ_CHEST_STORAGE_001', 'interactive', '보관 상자', '상인의 물품을 보관하는 상자', 'CELL_SHOP_INTERIOR_001',
 '{"x": 8, "y": 7}', 'openable', '["closed", "open"]', '{"material": "wood", "locked": false, "contents": ["WEAPON_SWORD_001", "ARMOR_LEATHER_001"]}');

-- 샘플 Dialogue Context
INSERT INTO game_data.dialogue_contexts (dialogue_id, title, content, priority, entity_personality, available_topics, constraints)
VALUES 
('MERCHANT_GREETING', '상인 인사', '어서오세요! 무엇을 도와드릴까요?', 1,
 '친근하고 전문적인 상인. 무기에 대한 광범위한 지식을 가지고 있습니다.',
 '{"topics": ["shop_items", "local_news", "farewell"], "default_topic": "greeting"}',
 '{"max_response_length": 200, "tone": "friendly"}');

-- 샘플 Dialogue Topic
INSERT INTO game_data.dialogue_topics (topic_id, dialogue_id, topic_type, content, conditions)
VALUES 
('SHOP_ITEMS_001', 'MERCHANT_GREETING', 'shop_items',
 '현재 판매 중인 무기: 철검 (100 골드), 강철 도끼 (150 골드), 청동 단검 (80 골드)',
 '{"player_level": {"min": 1, "max": 10}}');

-- 샘플 Dialogue Knowledge
INSERT INTO game_data.dialogue_knowledge (knowledge_id, title, content, knowledge_type, related_entities, related_topics, knowledge_properties)
VALUES 
('FOREST_MONSTERS_LORE', '숲 괴물 목격담', '최근 북부 숲에서 공격적인 괴물 활동이 증가했다는 보고가 있습니다.', 'lore',
 '{"locations": ["REG_NORTH_FOREST_001"]}', '{"main_topics": ["local_news"]}', '{"importance": 3}');

-- 샘플 Default Values (애플리케이션 기본값)
INSERT INTO game_data.default_values (setting_id, category, setting_name, setting_value, description)
VALUES 
('CELL_DEFAULT_SIZE', 'cell', 'default_size', 
 '{"width": 20, "height": 20}', '셀 기본 크기'),
('CELL_DEFAULT_STATUS', 'cell', 'default_status', 
 '"active"', '셀 기본 상태'),
('CELL_DEFAULT_TYPE', 'cell', 'default_type', 
 '"indoor"', '셀 기본 타입'),
('ENTITY_DEFAULT_POSITION', 'entity', 'default_position', 
 '{"x": 0.0, "y": 0.0}', '엔티티 기본 위치'),
('ENTITY_DEFAULT_STATUS', 'entity', 'default_status', 
 '"active"', '엔티티 기본 상태'),
('ENTITY_DEFAULT_TYPE', 'entity', 'default_type', 
 '"npc"', '엔티티 기본 타입'),
('DIALOGUE_DEFAULT_PRIORITY', 'dialogue', 'default_priority', 
 '1', '대화 기본 우선순위'),
('DIALOGUE_DEFAULT_TOPICS', 'dialogue', 'default_topics', 
 '["greeting", "trade", "lore", "quest", "farewell"]', '기본 대화 주제 목록');

-- =====================================================
-- 완료 메시지
-- =====================================================
SELECT 'MVP v2 최종 데이터베이스 스키마 생성 완료!' AS message;

-- 스키마별 테이블 수 확인
SELECT 
    'game_data' as schema_name, 
    COUNT(*) as table_count 
FROM information_schema.tables 
WHERE table_schema = 'game_data'
UNION ALL
SELECT 
    'reference_layer' as schema_name, 
    COUNT(*) as table_count 
FROM information_schema.tables 
WHERE table_schema = 'reference_layer'
UNION ALL
SELECT 
    'runtime_data' as schema_name, 
    COUNT(*) as table_count 
FROM information_schema.tables 
WHERE table_schema = 'runtime_data'
UNION ALL
SELECT 
    'simulation_data' as schema_name, 
    COUNT(*) as table_count 
FROM information_schema.tables 
WHERE table_schema = 'simulation_data';
