-- Dialogue context data insertion

-- 1. Merchant greeting dialogue context
INSERT INTO game_data.dialogue_contexts 
(dialogue_id, title, content, priority, entity_personality, available_topics, constraints) 
VALUES
('MERCHANT_GREETING', 'Merchant Greeting', 'Welcome! How can I help you?', 1, 
 'Friendly and professional merchant with extensive knowledge about weapons.',
 '{"topics": ["shop_items", "local_news", "farewell"], "default_topic": "greeting"}',
 '{"max_response_length": 200, "tone": "friendly"}'),
('MERCHANT_FAREWELL', 'Merchant Farewell', 'Goodbye! Come again!', 1, 
 'Friendly and professional merchant',
 '{"topics": ["farewell"], "default_topic": "farewell"}',
 '{"max_response_length": 100, "tone": "friendly"}');

-- 2. Dialogue topics data
INSERT INTO game_data.dialogue_topics 
(topic_id, dialogue_id, topic_type, content, conditions) 
VALUES
('SHOP_ITEMS_001', 'MERCHANT_GREETING', 'shop_items', 
 'Current weapons for sale: Iron Sword(100 gold), Steel Axe(150 gold), Bronze Dagger(80 gold)',
 '{"player_level": {"min": 1, "max": 10}}'),
('LOCAL_NEWS_001', 'MERCHANT_GREETING', 'world_lore',
 'Strange monsters have been spotted in the forest recently. Be careful.',
 '{"quest_flags": ["forest_investigation"]}');

-- 3. Dialogue knowledge base
INSERT INTO game_data.dialogue_knowledge 
(knowledge_id, title, content, knowledge_type, related_entities, related_topics, knowledge_properties) 
VALUES
('KNOWLEDGE_WEAPONS_001', 'Weapon Knowledge', 'Weapons have different characteristics. Swords provide balanced attack, axes provide powerful attack, and daggers provide fast attack.',
 'weapon_lore',
 '{"npcs": ["TEST_NPC_001"], "locations": ["LOC_FOREST_SHOP_001"]}',
 '{"main_topics": ["weapons"], "sub_topics": ["swords", "axes", "daggers"]}',
 '{"importance": 5, "reveal_conditions": {"quest_stage": 1}}');

SELECT 'Dialogue context data insertion completed!' as message;
