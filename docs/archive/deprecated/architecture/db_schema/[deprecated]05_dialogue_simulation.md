# [deprecated] 대화 시스템 시뮬레이션

> **Deprecated 날짜**: 2025-12-28  
> **Deprecated 사유**: 이 문서는 초기 대화 시스템 시뮬레이션 예제 메모로, 현재는 실제 구현이 완료되어 더 이상 참고할 필요가 없습니다.

## 1. 기본 엔티티 데이터 (game_data.entities)
```sql
INSERT INTO game_data.entities (entity_id, entity_type, base_name) VALUES 
(1001, 'npc', '무기상인'),
(1002, 'npc', '여관주인'),
(1003, 'player', '주인공');
```

## 2. 대화 컨텍스트 정의 (game_data.dialogue_contexts)
```sql
INSERT INTO game_data.dialogue_contexts 
(context_id, entity_id, context_type, context_description, available_topics, entity_personality, constraints) VALUES
(
    101,  -- context_id
    1001, -- entity_id (무기상인)
    'shop',
    '무기 상점에서의 기본 대화',
    '{"topics": ["greeting", "shop_items", "weapon_info", "bargain"]}',
    '전문적이고 친절한 성격. 무기에 대한 해박한 지식을 가짐. 상인다운 이익 추구.',
    '{"max_response_length": 100, "tone": "professional", "required_keywords": ["무기", "장비", "가격"]}'
),
(
    102,  -- context_id
    1002, -- entity_id (여관주인)
    'service',
    '여관에서의 기본 대화',
    '{"topics": ["greeting", "room_service", "town_info", "rumors"]}',
    '친근하고 수다스러운 성격. 마을의 소문에 밝음.',
    '{"max_response_length": 150, "tone": "friendly", "required_keywords": ["숙박", "마을", "소문"]}'
);
```

## 3. 대화 지식 베이스 (game_data.dialogue_knowledge)
```sql
INSERT INTO game_data.dialogue_knowledge 
(knowledge_id, context_id, topic, content, conditions, priority) VALUES
(
    201,
    101, -- 무기상인 컨텍스트
    'shop_items',
    '현재 판매 중인 무기 목록:
     - 철검 (100골드)
     - 강철 도끼 (150골드)
     - 청동 단검 (80골드)',
    '{"player_level": {"min": 1, "max": 5}}',
    1
),
(
    202,
    102, -- 여관주인 컨텍스트
    'town_info',
    '최근 마을 소식:
     - 북쪽 숲에서 몬스터 출몰
     - 새로운 대장간 오픈
     - 곧 마을 축제 예정',
    '{"time_of_day": "evening", "player_reputation": {"min": 0}}',
    1
);
```

## 4. 런타임 엔티티 참조 (reference_layer.entity_references)
```sql
INSERT INTO reference_layer.entity_references 
(runtime_entity_id, game_data_entity_id, session_id) VALUES
(5001, 1001, 'SESSION_001'), -- 무기상인
(5002, 1002, 'SESSION_001'), -- 여관주인
(5003, 1003, 'SESSION_001'); -- 플레이어
```

## 5. 대화 상태 (runtime_data.dialogue_states)
```sql
INSERT INTO runtime_data.dialogue_states 
(state_id, session_id, runtime_entity_id, current_context_id, conversation_state, active_topics) VALUES
(
    301,
    'SESSION_001',
    5001, -- 무기상인
    101,  -- 무기상인 컨텍스트
    '{"current_topic": "greeting", "emotion": "neutral", "last_mentioned_item": null}',
    '["shop_items", "weapon_info"]'
);
```

## 6. 대화 히스토리 (runtime_data.dialogue_history)
```sql
INSERT INTO runtime_data.dialogue_history 
(history_id, session_id, runtime_entity_id, context_id, speaker_type, message, relevant_knowledge) VALUES
(
    401,
    'SESSION_001',
    5001, -- 무기상인
    101,  -- 무기상인 컨텍스트
    'npc',
    '어서오세요. 저희 상점에 오신 것을 환영합니다.',
    'null'
),
(
    402,
    'SESSION_001',
    5003, -- 플레이어
    101,  -- 무기상인 컨텍스트
    'player',
    '무기를 좀 보고 싶습니다.',
    'null'
),
(
    403,
    'SESSION_001',
    5001, -- 무기상인
    101,  -- 무기상인 컨텍스트
    'npc',
    '현재 저희 상점에서는 초보자에게 적합한 무기들을 구비하고 있습니다.',
    '{"knowledge_id": 201, "used_content": "level-appropriate weapons"}'
);
```

## 발견된 잠재적 문제점들

1. **외래 키 제약 관련**
   - `dialogue_contexts`의 `entity_id`가 INTEGER로 정의되어 있어 game_data.entities의 entity_id와 타입이 일치해야 함
   - `dialogue_history`와 `dialogue_states`의 runtime_entity_id가 reference_layer.entity_references를 참조하므로 동기화 필요

2. **JSON 필드 구조 표준화 필요**
   - available_topics, constraints, conversation_state 등 JSON 필드들의 구조가 명확히 정의되어야 함
   - relevant_knowledge의 null 처리 방식 통일 필요 ('null' 문자열 vs. NULL 값)

3. **세션 관리**
   - session_id 형식이 통일되어야 함 (현재는 문자열 'SESSION_001' 형식 사용)
   - 세션 종료 시 reference_layer와 runtime_data의 데이터 정리 방안 필요

4. **시간 관리**
   - dialogue_knowledge의 conditions에서 사용하는 time_of_day와 실제 게임 시간 동기화 방안 필요
   - last_updated 타임스탬프의 시간대(timezone) 처리 방안 필요

## 시뮬레이션 시나리오

1. 플레이어가 무기 상점 입장
2. 무기상인이 인사 (greeting context 활성화)
3. 플레이어가 무기 정보 요청
4. 시스템이 플레이어 레벨 확인 후 적절한 무기 정보 제공
5. 대화 내용이 history에 기록
6. 대화 상태가 'shop_items' topic으로 업데이트

이 흐름에서 각 테이블의 데이터가 적절히 연결되어 있으며, 대화 컨텍스트와 지식이 조건에 따라 올바르게 제공되는 것을 확인할 수 있습니다. 