# Database Setup

이 디렉토리는 데이터베이스 초기 설정 및 마이그레이션 파일을 포함합니다.

## 현재 사용 중인 파일

### 핵심 스키마 파일
- **`mvp_schema.sql`** ⭐⭐⭐ - 메인 데이터베이스 스키마 (필수)
  - 3계층 구조: game_data, reference_layer, runtime_data
  - 모든 테이블, 인덱스, 제약조건 정의
  - **사용법**: `psql -U postgres -d rpg_engine -f database/setup/mvp_schema.sql`

- **`world_editor_migrations.sql`** - 월드 에디터 마이그레이션
  - 월드 에디터 관련 테이블 (map_metadata, pin_positions, world_roads)
  - **사용법**: `python scripts/apply_world_editor_migrations.py`

### 테스트 데이터
- **`test_templates.sql`** - 테스트용 템플릿 데이터
  - 엔티티, 셀 등 테스트에 필요한 기본 데이터
  - **사용법**: `psql -U postgres -d rpg_engine -f database/setup/test_templates.sql`
  - **참고**: `tests/active/conftest.py`에서 사용됨

### 유틸리티 스크립트
- **`reset_database.py`** - 데이터베이스 리셋 스크립트
  - 기존 스키마 삭제 (개발/테스트용)
  - **주의**: 프로덕션 환경에서 사용 금지

- **`insert_test_data.py`** - 테스트 데이터 삽입 스크립트
  - 샘플 엔티티, 셀, NPC 행동 스케줄 등 삽입
  - **사용법**: `python database/setup/insert_test_data.py`

## 초기 설정 순서

### 1. 데이터베이스 생성
```bash
createdb -U postgres rpg_engine
```

### 2. 메인 스키마 적용
```bash
psql -U postgres -d rpg_engine -f database/setup/mvp_schema.sql
```

### 3. 월드 에디터 마이그레이션 적용
```bash
python scripts/apply_world_editor_migrations.py
```

### 4. 테스트 템플릿 데이터 삽입
```bash
psql -U postgres -d rpg_engine -f database/setup/test_templates.sql
```

### 5. (선택) 추가 테스트 데이터 삽입
```bash
python database/setup/insert_test_data.py
```

## 파일 설명

### mvp_schema.sql
- **크기**: 56KB, 1,137 lines
- **내용**: 전체 데이터베이스 스키마 정의
- **중요도**: ⭐⭐⭐ 최고 (프로젝트의 핵심)

### world_editor_migrations.sql
- **크기**: 6.9KB, 162 lines
- **내용**: 월드 에디터 관련 테이블
- **사용**: 월드 에디터 기능 사용 시 필요

### test_templates.sql
- **크기**: 13KB, 385 lines
- **내용**: 테스트용 기본 데이터
- **사용**: 테스트 실행 시 필요

### reset_database.py
- **용도**: 개발/테스트 환경에서 데이터베이스 초기화
- **주의**: 모든 데이터 삭제

### insert_test_data.py
- **용도**: 추가 테스트 데이터 삽입
- **내용**: 샘플 엔티티, 셀, NPC 행동 스케줄 등

## Deprecated 파일

다음 파일들은 `archive/database/setup/` 디렉토리로 이동되었습니다:
- `migrate_to_mvp_v2.py` - MVP v2 마이그레이션 (완료)
- `migration_plan.md` - 마이그레이션 계획 (완료)
- `create_mvp_v2_database.py` - MVP v2 생성 (완료)
- `create_missing_tables.sql` - mvp_schema.sql에 통합됨
- `setup_missing_tables.py` - mvp_schema.sql에 통합됨
- `create_default_values_table.py` - mvp_schema.sql에 통합됨
- `default_values_schema.sql` - mvp_schema.sql에 통합됨

## 참고 문서

- `docs/onboarding/README.md` - 초기 설정 가이드
- `docs/onboarding/HANDOVER_2025-10-21.md` - 프로젝트 인수인계서

