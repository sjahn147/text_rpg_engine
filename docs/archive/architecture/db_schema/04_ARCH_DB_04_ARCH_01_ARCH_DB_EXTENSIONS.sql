-- UUID 지원을 위한 확장 설치
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 스키마 생성
CREATE SCHEMA IF NOT EXISTS game_data;
CREATE SCHEMA IF NOT EXISTS reference_layer;
CREATE SCHEMA IF NOT EXISTS runtime_data;

COMMENT ON SCHEMA game_data IS '불변의 게임 원본 데이터';
COMMENT ON SCHEMA reference_layer IS '게임 데이터와 런타임 데이터 간의 참조 관계';
COMMENT ON SCHEMA runtime_data IS '실행 중인 게임의 상태 데이터'; 