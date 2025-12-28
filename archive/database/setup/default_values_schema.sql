-- =====================================================
-- 기본값 관리 테이블 스키마
-- 모든 하드코딩된 기본값을 DB에서 관리
-- =====================================================

-- 기본값 설정 테이블
CREATE TABLE IF NOT EXISTS game_data.default_values (
    setting_id VARCHAR(50) PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    setting_name VARCHAR(100) NOT NULL,
    setting_value JSONB NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_default_values_category ON game_data.default_values(category);
CREATE INDEX IF NOT EXISTS idx_default_values_active ON game_data.default_values(is_active);

-- 코멘트
COMMENT ON TABLE game_data.default_values IS '시스템 기본값 설정 테이블';
COMMENT ON COLUMN game_data.default_values.setting_id IS '설정 고유 ID';
COMMENT ON COLUMN game_data.default_values.category IS '설정 카테고리 (cell, entity, dialogue, time 등)';
COMMENT ON COLUMN game_data.default_values.setting_name IS '설정 이름';
COMMENT ON COLUMN game_data.default_values.setting_value IS '설정 값 (JSONB)';
COMMENT ON COLUMN game_data.default_values.description IS '설정 설명';

-- 기본값 데이터 삽입
INSERT INTO game_data.default_values (setting_id, category, setting_name, setting_value, description) VALUES
-- 셀 관련 기본값
('CELL_DEFAULT_SIZE', 'cell', 'default_size', '{"width": 20, "height": 20}', '셀 기본 크기'),
('CELL_DEFAULT_STATUS', 'cell', 'default_status', '"active"', '셀 기본 상태'),
('CELL_DEFAULT_TYPE', 'cell', 'default_type', '"indoor"', '셀 기본 타입'),

-- 엔티티 관련 기본값
('ENTITY_DEFAULT_POSITION', 'entity', 'default_position', '{"x": 0.0, "y": 0.0}', '엔티티 기본 위치'),
('ENTITY_DEFAULT_STATUS', 'entity', 'default_status', '"active"', '엔티티 기본 상태'),
('ENTITY_DEFAULT_TYPE', 'entity', 'default_type', '"npc"', '엔티티 기본 타입'),

-- 시간 시스템 기본값
('TIME_DEFAULT_PERIODS', 'time', 'default_periods', '{
    "dawn": {"start": 6, "end": 8},
    "morning": {"start": 8, "end": 12},
    "lunch": {"start": 12, "end": 14},
    "afternoon": {"start": 14, "end": 18},
    "evening": {"start": 18, "end": 20},
    "night": {"start": 20, "end": 22},
    "late_night": {"start": 22, "end": 6}
}', '시간대별 기본 설정'),

('TIME_DEFAULT_INTERACTION_PROBABILITIES', 'time', 'default_interaction_probabilities', '{
    "dawn": 0.1,
    "morning": 0.2,
    "lunch": 0.8,
    "afternoon": 0.3,
    "evening": 0.6,
    "night": 0.4,
    "late_night": 0.1
}', '시간대별 상호작용 확률'),

-- 대화 시스템 기본값
('DIALOGUE_DEFAULT_TEMPLATES', 'dialogue', 'default_templates', '{
    "greeting": [
        "안녕하세요! 무엇을 도와드릴까요?",
        "오, 새로운 얼굴이군요!",
        "여기서 뭘 하고 계신가요?",
        "반갑습니다! 여기 처음 오신 건가요?"
    ],
    "trade": [
        "거래를 원하시는군요. 무엇을 사고 싶으신가요?",
        "상점에 오신 것을 환영합니다!",
        "좋은 물건들이 많이 있습니다.",
        "특별한 할인을 해드릴 수 있습니다."
    ],
    "lore": [
        "아, 그 이야기를 알고 싶으시군요.",
        "오래된 이야기입니다만...",
        "이곳의 전설을 말씀드리겠습니다.",
        "비밀스러운 이야기인데..."
    ],
    "quest": [
        "도움이 필요하신가요?",
        "특별한 일이 있으시군요.",
        "제가 도울 수 있는 일이 있다면...",
        "위험한 일이지만 도와드리겠습니다."
    ],
    "farewell": [
        "안녕히 가세요!",
        "또 만나요!",
        "조심히 가세요!",
        "행운을 빕니다!"
    ]
}', '대화 기본 템플릿'),

-- 액션 시스템 기본값
('ACTION_DEFAULT_RESPONSES', 'action', 'default_responses', '{
    "greeting": [
        "안녕하세요! 무엇을 도와드릴까요?",
        "오, 새로운 얼굴이군요!",
        "여기서 뭘 하고 계신가요?"
    ],
    "trade": [
        "거래를 원하시는군요. 무엇을 사고 싶으신가요?",
        "상점에 오신 것을 환영합니다!",
        "좋은 물건들이 많이 있습니다."
    ],
    "farewell": [
        "안녕히 가세요!",
        "또 만나요!",
        "조심히 가세요!"
    ]
}', '액션 기본 응답'),

-- 시간대별 행동 패턴 기본값
('TIME_DEFAULT_ACTIONS', 'time', 'default_actions', '{
    "dawn": ["wake_up", "prepare", "move_to_work"],
    "morning": ["work", "business", "patrol"],
    "lunch": ["move_to_square", "socialize", "eat"],
    "afternoon": ["work", "business", "patrol", "explore"],
    "evening": ["socialize", "interact", "gather"],
    "night": ["story_telling", "relax", "prepare_sleep"],
    "late_night": ["sleep", "rest", "return_home"]
}', '시간대별 기본 행동 패턴')

ON CONFLICT (setting_id) DO UPDATE SET
    setting_value = EXCLUDED.setting_value,
    updated_at = CURRENT_TIMESTAMP;
