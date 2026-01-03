-- =====================================================
-- 퀘스트 시스템 테이블 추가
-- =====================================================
-- 목적: runtime_data.quests 테이블 생성 (퀘스트 상태 관리)
-- 작성일: 2026-01-04
-- =====================================================

-- 사전 검증: 테이블이 이미 존재하는지 확인
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_schema = 'runtime_data' 
        AND table_name = 'quests'
    ) THEN
        RAISE NOTICE 'runtime_data.quests 테이블이 이미 존재합니다. 마이그레이션을 건너뜁니다.';
        RETURN;
    END IF;
END $$;

-- runtime_data.quests 테이블 생성
CREATE TABLE IF NOT EXISTS runtime_data.quests (
    quest_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL,
    quest_template_id VARCHAR(50),  -- 향후 game_data.quest_templates 참조용 (현재는 NULL 허용)
    quest_status VARCHAR(50) NOT NULL DEFAULT 'active',  -- 'active', 'completed', 'failed', 'abandoned'
    quest_title VARCHAR(200) NOT NULL,
    quest_description TEXT,
    quest_data JSONB DEFAULT '{}'::jsonb,  -- 퀘스트 정보, 목표, 진행도 등
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    failed_at TIMESTAMP,
    abandoned_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES runtime_data.active_sessions(session_id) ON DELETE CASCADE,
    CONSTRAINT chk_quest_status CHECK (quest_status IN ('active', 'completed', 'failed', 'abandoned')),
    CONSTRAINT chk_quest_data_structure CHECK (
        quest_data IS NULL OR
        (
            jsonb_typeof(quest_data) = 'object' AND
            (
                NOT (quest_data ? 'objectives') OR
                jsonb_typeof(quest_data -> 'objectives') = 'array'
            ) AND
            (
                NOT (quest_data ? 'progress') OR
                jsonb_typeof(quest_data -> 'progress') = 'object'
            )
        )
    )
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_quests_session ON runtime_data.quests(session_id);
CREATE INDEX IF NOT EXISTS idx_quests_status ON runtime_data.quests(quest_status);
CREATE INDEX IF NOT EXISTS idx_quests_template ON runtime_data.quests(quest_template_id);
CREATE INDEX IF NOT EXISTS idx_quests_started_at ON runtime_data.quests(started_at);
CREATE INDEX IF NOT EXISTS idx_quests_data ON runtime_data.quests USING GIN (quest_data);

-- 코멘트 추가
COMMENT ON TABLE runtime_data.quests IS '퀘스트 상태 관리 테이블 (런타임 데이터)';
COMMENT ON COLUMN runtime_data.quests.quest_id IS '퀘스트 고유 ID';
COMMENT ON COLUMN runtime_data.quests.session_id IS '게임 세션 ID';
COMMENT ON COLUMN runtime_data.quests.quest_template_id IS '퀘스트 템플릿 ID (향후 game_data.quest_templates 참조)';
COMMENT ON COLUMN runtime_data.quests.quest_status IS '퀘스트 상태: active(진행중), completed(완료), failed(실패), abandoned(포기)';
COMMENT ON COLUMN runtime_data.quests.quest_title IS '퀘스트 제목';
COMMENT ON COLUMN runtime_data.quests.quest_description IS '퀘스트 설명';
COMMENT ON COLUMN runtime_data.quests.quest_data IS 'JSONB 구조: {"objectives": [...], "progress": {...}, "rewards": [...], "requirements": {...}}';
COMMENT ON COLUMN runtime_data.quests.started_at IS '퀘스트 시작 시간';
COMMENT ON COLUMN runtime_data.quests.completed_at IS '퀘스트 완료 시간 (NULL이면 미완료)';
COMMENT ON COLUMN runtime_data.quests.failed_at IS '퀘스트 실패 시간 (NULL이면 실패하지 않음)';
COMMENT ON COLUMN runtime_data.quests.abandoned_at IS '퀘스트 포기 시간 (NULL이면 포기하지 않음)';

-- 검증: 테이블이 정상적으로 생성되었는지 확인
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_schema = 'runtime_data' 
        AND table_name = 'quests'
    ) THEN
        RAISE EXCEPTION 'runtime_data.quests 테이블 생성 실패';
    END IF;
    
    RAISE NOTICE 'runtime_data.quests 테이블이 성공적으로 생성되었습니다.';
END $$;

