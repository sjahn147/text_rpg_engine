# [deprecated] 대화 시스템 JSON 스키마 정의

> **Deprecated 날짜**: 2025-12-28  
> **Deprecated 사유**: 이 문서는 초기 JSON 스키마 정의 메모로, 현재는 실제 구현에서 사용되는 스키마가 다를 수 있습니다. 최신 스키마는 `docs/architecture/db_schema/01_ARCH_DB_SCHEMA_README.md`를 참조하세요.

## 1. 대화 컨텍스트 관련 (dialogue_contexts)

### 1.1 available_topics
```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["topics"],
    "properties": {
        "topics": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": [
                    "greeting",
                    "shop_items",
                    "weapon_info",
                    "bargain",
                    "quest_info",
                    "town_info",
                    "rumors",
                    "farewell"
                ]
            }
        },
        "default_topic": {
            "type": "string",
            "description": "시작 시 기본 주제"
        },
        "topic_requirements": {
            "type": "object",
            "patternProperties": {
                "^[a-zA-Z_]+$": {
                    "type": "object",
                    "properties": {
                        "required_topics": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "required_flags": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                }
            }
        }
    }
}
```

### 1.2 constraints
```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "max_response_length": {
            "type": "integer",
            "minimum": 1
        },
        "tone": {
            "type": "string",
            "enum": ["friendly", "professional", "mysterious", "aggressive"]
        },
        "required_keywords": {
            "type": "array",
            "items": {"type": "string"}
        },
        "forbidden_keywords": {
            "type": "array",
            "items": {"type": "string"}
        },
        "emotion_range": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": ["happy", "neutral", "sad", "angry", "surprised"]
            }
        }
    }
}
```

## 2. 대화 상태 관련 (dialogue_states)

### 2.1 active_topics
```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["current_topics", "available_topics"],
    "properties": {
        "current_topics": {
            "type": "array",
            "items": {"type": "string"}
        },
        "available_topics": {
            "type": "array",
            "items": {"type": "string"}
        },
        "locked_topics": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}
```

### 2.2 conversation_state
```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["current_topic", "emotion"],
    "properties": {
        "current_topic": {
            "type": "string"
        },
        "emotion": {
            "type": "string",
            "enum": ["happy", "neutral", "sad", "angry", "surprised"]
        },
        "last_mentioned_item": {
            "type": ["string", "null"]
        },
        "context_memory": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string"},
                    "timestamp": {"type": "string", "format": "date-time"},
                    "summary": {"type": "string"}
                }
            },
            "maxItems": 5
        }
    }
}
```

## 3. 대화 히스토리 관련 (dialogue_history)

### 3.1 relevant_knowledge
```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "knowledge_id": {
            "type": ["integer", "null"]
        },
        "used_content": {
            "type": ["string", "null"]
        },
        "context_flags": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}
```

## 사용 예시

### available_topics 예시
```json
{
    "topics": ["greeting", "shop_items", "weapon_info"],
    "default_topic": "greeting",
    "topic_requirements": {
        "weapon_info": {
            "required_topics": ["greeting"],
            "required_flags": ["shop_entered"]
        }
    }
}
```

### active_topics 예시
```json
{
    "current_topics": ["shop_items"],
    "available_topics": ["weapon_info", "bargain"],
    "locked_topics": ["quest_info"]
}
```

### conversation_state 예시
```json
{
    "current_topic": "shop_items",
    "emotion": "neutral",
    "last_mentioned_item": "철검",
    "context_memory": [
        {
            "topic": "greeting",
            "timestamp": "2024-03-15T14:30:00Z",
            "summary": "상점 입장 인사"
        }
    ]
}
```

## 구현 시 주의사항

1. **NULL 처리**
   - JSON에서는 `null`
   - 데이터베이스에서는 SQL `NULL`
   - 문자열 'null' 사용 금지

2. **날짜/시간 형식**
   - ISO 8601 형식 사용 (예: "2024-03-15T14:30:00Z")
   - UTC 기준으로 저장

3. **배열 제한**
   - context_memory: 최대 5개 항목
   - topics: 중복 항목 불가

4. **유효성 검사**
   - 모든 JSON 데이터는 저장 전 스키마 검증 필수
   - 열거형(enum) 값은 정의된 값만 사용