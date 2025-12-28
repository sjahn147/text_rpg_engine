-- 대화 컨텍스트 데이터 삽입

-- 1. 상인 인사 대화 컨텍스트
INSERT INTO game_data.dialogue_contexts 
(dialogue_id, title, content, priority, entity_personality, available_topics, constraints) 
VALUES
('MERCHANT_GREETING', '상인 인사', '어서오세요! 무엇을 도와드릴까요?', 1, 
 '친절하고 전문적인 상인. 무기에 대한 해박한 지식을 가지고 있음.',
 '{"topics": ["shop_items", "local_news", "farewell"], "default_topic": "greeting"}',
 '{"max_response_length": 200, "tone": "friendly"}'),
('MERCHANT_FAREWELL', '상인 작별', '안녕히 가세요! 또 오세요!', 1, 
 '친절하고 전문적인 상인',
 '{"topics": ["farewell"], "default_topic": "farewell"}',
 '{"max_response_length": 100, "tone": "friendly"}');

-- 2. 대화 주제 데이터
INSERT INTO game_data.dialogue_topics 
(topic_id, dialogue_id, topic_type, content, conditions) 
VALUES
('SHOP_ITEMS_001', 'MERCHANT_GREETING', 'shop_items', 
 '현재 판매 중인 무기 목록: 철검(100골드), 강철도끼(150골드), 청동단검(80골드)',
 '{"player_level": {"min": 1, "max": 10}}'),
('LOCAL_NEWS_001', 'MERCHANT_GREETING', 'world_lore',
 '최근 숲에서 이상한 몬스터들이 목격되고 있습니다. 조심하세요.',
 '{"quest_flags": ["forest_investigation"]}');

-- 3. 대화 지식 베이스
INSERT INTO game_data.dialogue_knowledge 
(knowledge_id, title, content, knowledge_type, related_entities, related_topics, knowledge_properties) 
VALUES
('KNOWLEDGE_WEAPONS_001', '무기 상식', '무기들은 각각 다른 특성을 가지고 있습니다. 검은 균형잡힌 공격력을, 도끼는 강력한 공격력을, 단검은 빠른 공격을 제공합니다.',
 'weapon_lore',
 '{"npcs": ["TEST_NPC_001"], "locations": ["LOC_FOREST_SHOP_001"]}',
 '{"main_topics": ["weapons"], "sub_topics": ["swords", "axes", "daggers"]}',
 '{"importance": 5, "reveal_conditions": {"quest_stage": 1}}');

SELECT '대화 컨텍스트 데이터 삽입 완료!' as message;
