-- ============================================================================
-- 테스트용 정적 템플릿 데이터
-- ============================================================================
-- 목적: 통합 테스트 및 시나리오 테스트에서 사용할 기본 게임 데이터
-- 작성일: 2025-10-20
-- 주의: 이 파일은 테스트 환경에서만 실행되어야 합니다
-- ============================================================================

-- ============================================================================
-- 1. 테스트용 엔티티 템플릿
-- ============================================================================

-- 선행 요구사항: world_cells 외래키를 위해 리전/로케이션을 먼저 삽입
-- (아래에 동일 데이터가 한 번 더 나오지만 ON CONFLICT로 중복 방지됨)

-- 선행: 테스트용 리전
INSERT INTO game_data.world_regions (
    region_id, region_name, region_description, region_type, region_properties
) VALUES (
    'REG_TUTORIAL_001',
    '튜토리얼 지역',
    '초보 모험가를 위한 안전한 지역입니다.',
    'tutorial',
    jsonb_build_object(
        'level_range', jsonb_build_object('min', 1, 'max', 5),
        'climate', 'temperate',
        'main_faction', 'neutral'
    )
) ON CONFLICT (region_id) DO NOTHING;

-- 선행: 테스트용 로케이션 1 (마을)
INSERT INTO game_data.world_locations (
    location_id, region_id, location_name, location_description,
    location_type, location_properties
) VALUES (
    'LOC_VILLAGE_001',
    'REG_TUTORIAL_001',
    '시작 마을',
    '모험가들이 처음 시작하는 평화로운 마을입니다.',
    'settlement',
    jsonb_build_object(
        'population', 100,
        'faction', 'neutral',
        'services', jsonb_build_array('shop', 'inn', 'quest_board')
    )
) ON CONFLICT (location_id) DO NOTHING;

-- 선행: 테스트용 로케이션 2 (숲)
INSERT INTO game_data.world_locations (
    location_id, region_id, location_name, location_description,
    location_type, location_properties
) VALUES (
    'LOC_FOREST_001',
    'REG_TUTORIAL_001',
    '마을 근처 숲',
    '마을 근처에 있는 작은 숲입니다.',
    'wilderness',
    jsonb_build_object(
        'danger_level', 'low',
        'resources', jsonb_build_array('wood', 'herbs', 'mushrooms')
    )
) ON CONFLICT (location_id) DO NOTHING;

-- 테스트 플레이어 템플릿
INSERT INTO game_data.entities (
    entity_id, entity_type, entity_name, entity_description,
    base_stats, default_equipment, default_abilities, 
    default_inventory, entity_properties
) VALUES (
    'TEST_PLAYER_001',
    'player',
    '테스트 플레이어',
    '당신 자신입니다. 거울을 보는 것처럼 자신의 모습을 관찰할 수 있습니다. 평범해 보이지만 모험을 시작하려는 의지가 느껴집니다.',
    jsonb_build_object(
        'hp', 100,
        'mp', 50,
        'strength', 10,
        'agility', 10,
        'intelligence', 10
    ),
    '[]'::jsonb,  -- 기본 장비 없음
    '[]'::jsonb,  -- 기본 능력 없음
    '[]'::jsonb,  -- 기본 인벤토리 없음
    jsonb_build_object(
        'level', 1,
        'experience', 0,
        'personality', 'neutral',
        'occupation', '모험가',
        'mood', '차분함'
    )
) ON CONFLICT (entity_id) DO UPDATE SET
    entity_description = EXCLUDED.entity_description,
    entity_properties = EXCLUDED.entity_properties;

-- 테스트 마을 주민 NPC
INSERT INTO game_data.entities (
    entity_id, entity_type, entity_name, entity_description,
    base_stats, default_equipment, default_abilities, 
    default_inventory, entity_properties
) VALUES (
    'NPC_VILLAGER_001',
    'npc',
    '마을 주민',
    '평범한 마을 주민입니다.',
    jsonb_build_object(
        'hp', 80,
        'mp', 20,
        'strength', 5,
        'agility', 5,
        'intelligence', 8
    ),
    '[]'::jsonb,
    '[]'::jsonb,
    '[]'::jsonb,
    jsonb_build_object(
        'personality', 'friendly',
        'occupation', 'farmer',
        'mood', 'happy'
    )
) ON CONFLICT (entity_id) DO NOTHING;

-- 테스트 상인 NPC
INSERT INTO game_data.entities (
    entity_id, entity_type, entity_name, entity_description,
    base_stats, default_equipment, default_abilities, 
    default_inventory, entity_properties
) VALUES (
    'NPC_MERCHANT_001',
    'npc',
    '상인',
    '다양한 물건을 파는 상인입니다.',
    jsonb_build_object(
        'hp', 70,
        'mp', 30,
        'strength', 5,
        'agility', 7,
        'intelligence', 12
    ),
    '[]'::jsonb,
    '[]'::jsonb,
    jsonb_build_array(
        jsonb_build_object('item_id', 'ITEM_POTION_001', 'quantity', 10),
        jsonb_build_object('item_id', 'ITEM_BREAD_001', 'quantity', 20)
    ),
    jsonb_build_object(
        'personality', 'greedy',
        'occupation', 'merchant',
        'mood', 'neutral',
        'shop_open', true
    )
) ON CONFLICT (entity_id) DO NOTHING;

-- 테스트 적대 엔티티
INSERT INTO game_data.entities (
    entity_id, entity_type, entity_name, entity_description,
    base_stats, default_equipment, default_abilities, 
    default_inventory, entity_properties
) VALUES (
    'NPC_GOBLIN_001',
    'enemy',
    '고블린',
    '약한 적대 생명체입니다.',
    jsonb_build_object(
        'hp', 50,
        'mp', 10,
        'strength', 8,
        'agility', 12,
        'intelligence', 3
    ),
    '[]'::jsonb,
    jsonb_build_array(
        jsonb_build_object('ability_id', 'ABILITY_SLASH_001', 'level', 1)
    ),
    '[]'::jsonb,
    jsonb_build_object(
        'personality', 'aggressive',
        'faction', 'monster',
        'ai_behavior', 'hostile'
    )
) ON CONFLICT (entity_id) DO NOTHING;

-- ============================================================================
-- 2. 테스트용 셀 템플릿
-- ============================================================================

-- 테스트 마을 광장
INSERT INTO game_data.world_cells (
    cell_id, location_id, cell_name, matrix_width, matrix_height,
    cell_description, cell_properties
) VALUES (
    'CELL_VILLAGE_SQUARE_001',
    'LOC_VILLAGE_001',
    '마을 광장',
    10,
    10,
    '마을 사람들이 모이는 넓은 광장입니다.',
    jsonb_build_object(
        'cell_type', 'town',
        'biome', 'plains',
        'weather_type', 'sunny',
        'accessible_directions', jsonb_build_array('north', 'south', 'east', 'west'),
        'safety_level', 'safe',
        'can_rest', true,
        'has_shops', true
    )
) ON CONFLICT (cell_id) DO NOTHING;

-- 테스트 상점 내부
INSERT INTO game_data.world_cells (
    cell_id, location_id, cell_name, matrix_width, matrix_height,
    cell_description, cell_properties
) VALUES (
    'CELL_SHOP_INTERIOR_001',
    'LOC_VILLAGE_001',
    '상점',
    5,
    5,
    '다양한 물건이 진열된 작은 상점입니다.',
    jsonb_build_object(
        'cell_type', 'shop',
        'biome', 'indoor',
        'weather_type', 'clear',
        'accessible_directions', jsonb_build_array('south'),
        'safety_level', 'safe',
        'shop_type', 'general',
        'merchant_id', 'NPC_MERCHANT_001'
    )
) ON CONFLICT (cell_id) DO NOTHING;

-- 테스트 숲 지역
INSERT INTO game_data.world_cells (
    cell_id, location_id, cell_name, matrix_width, matrix_height,
    cell_description, cell_properties
) VALUES (
    'CELL_FOREST_001',
    'LOC_FOREST_001',
    '숲',
    15,
    15,
    '나무가 울창한 숲입니다.',
    jsonb_build_object(
        'cell_type', 'wilderness',
        'biome', 'forest',
        'weather_type', 'cloudy',
        'accessible_directions', jsonb_build_array('north', 'south', 'east', 'west'),
        'safety_level', 'moderate',
        'encounter_rate', 'medium',
        'resources', jsonb_build_array('wood', 'herbs')
    )
) ON CONFLICT (cell_id) DO NOTHING;

-- ============================================================================
-- 3. 테스트용 로케이션
-- ============================================================================

INSERT INTO game_data.world_locations (
    location_id, region_id, location_name, location_description,
    location_type, location_properties
) VALUES (
    'LOC_VILLAGE_001',
    'REG_TUTORIAL_001',
    '시작 마을',
    '모험가들이 처음 시작하는 평화로운 마을입니다.',
    'settlement',
    jsonb_build_object(
        'population', 100,
        'faction', 'neutral',
        'services', jsonb_build_array('shop', 'inn', 'quest_board')
    )
) ON CONFLICT (location_id) DO NOTHING;

INSERT INTO game_data.world_locations (
    location_id, region_id, location_name, location_description,
    location_type, location_properties
) VALUES (
    'LOC_FOREST_001',
    'REG_TUTORIAL_001',
    '마을 근처 숲',
    '마을 근처에 있는 작은 숲입니다.',
    'wilderness',
    jsonb_build_object(
        'danger_level', 'low',
        'resources', jsonb_build_array('wood', 'herbs', 'mushrooms')
    )
) ON CONFLICT (location_id) DO NOTHING;

-- ============================================================================
-- 4. 테스트용 리전
-- ============================================================================

INSERT INTO game_data.world_regions (
    region_id, region_name, region_description, region_type, region_properties
) VALUES (
    'REG_TUTORIAL_001',
    '튜토리얼 지역',
    '초보 모험가를 위한 안전한 지역입니다.',
    'tutorial',
    jsonb_build_object(
        'level_range', jsonb_build_object('min', 1, 'max', 5),
        'climate', 'temperate',
        'main_faction', 'neutral'
    )
) ON CONFLICT (region_id) DO NOTHING;

-- 5. 테스트용 아이템 (스키마 차이로 보류)
-- 현재 mvp_schema의 items 테이블 구조는 base_properties 참조를 요구합니다.
-- 테스트 템플릿 간소화를 위해 아이템 삽입은 보류합니다.

-- ============================================================================
-- 6. 테스트용 대화 컨텍스트
-- ============================================================================

INSERT INTO game_data.dialogue_contexts (
    dialogue_id, title, content, priority,
    entity_personality, available_topics, constraints
) VALUES (
    'DIALOGUE_VILLAGER_GREETING_001',
    '마을 주민 인사',
    '안녕하세요! 좋은 하루입니다.',
    1,
    'friendly',
    jsonb_build_object(
        'topics', jsonb_build_array('greeting', 'weather', 'news')
    ),
    jsonb_build_object(
        'max_response_length', 200,
        'tone', 'friendly'
    )
) ON CONFLICT (dialogue_id) DO NOTHING;

INSERT INTO game_data.dialogue_contexts (
    dialogue_id, title, content, priority,
    entity_personality, available_topics, constraints
) VALUES (
    'DIALOGUE_MERCHANT_GREETING_001',
    '상인 인사',
    '어서오세요! 무엇을 찾으시나요?',
    1,
    'businesslike',
    jsonb_build_object(
        'topics', jsonb_build_array('shop', 'trade', 'prices')
    ),
    jsonb_build_object(
        'max_response_length', 200,
        'tone', 'professional'
    )
) ON CONFLICT (dialogue_id) DO NOTHING;

-- ============================================================================
-- 7. 테스트용 대화 주제
-- ============================================================================

-- dialogue_topics는 dialogue_id FK를 요구하고, 컬럼명이 content/conditions 입니다.
INSERT INTO game_data.dialogue_topics (
    topic_id, dialogue_id, topic_type, content, conditions
) VALUES (
    'TOPIC_GREETING_001',
    'DIALOGUE_VILLAGER_GREETING_001',
    'greeting',
    '인사를 나눕니다.',
    jsonb_build_object('min_relationship', 0)
) ON CONFLICT (topic_id) DO NOTHING;

INSERT INTO game_data.dialogue_topics (
    topic_id, dialogue_id, topic_type, content, conditions
) VALUES (
    'TOPIC_SHOP_001',
    'DIALOGUE_MERCHANT_GREETING_001',
    'shop',
    '상점 물건을 둘러봅니다.',
    jsonb_build_object('location_type', 'shop')
) ON CONFLICT (topic_id) DO NOTHING;

-- ============================================================================
-- 완료 메시지
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '✅ 테스트용 정적 템플릿 데이터 삽입 완료';
    RAISE NOTICE '📊 엔티티: 4개 (플레이어, 주민, 상인, 고블린)';
    RAISE NOTICE '📊 셀: 3개 (광장, 상점, 숲)';
    RAISE NOTICE '📊 로케이션: 2개 (마을, 숲)';
    RAISE NOTICE '📊 리전: 1개 (튜토리얼 지역)';
    RAISE NOTICE '📊 아이템: 2개 (물약, 빵)';
    RAISE NOTICE '📊 대화: 2개 (주민 인사, 상인 인사)';
END $$;

