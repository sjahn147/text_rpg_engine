# Database Setup Archive

이 디렉토리는 데이터베이스 설정 관련 deprecated 파일들을 보관합니다.

## 파일 목록

### 마이그레이션 관련 (완료됨)
- `migrate_to_mvp_v2.py` - MVP v2 마이그레이션 스크립트 (2025-10-18, 완료)
- `migration_plan.md` - 마이그레이션 계획 문서 (2025-10-18, 완료)
- `create_mvp_v2_database.py` - MVP v2 데이터베이스 생성 스크립트 (완료)

### 통합된 스크립트 (mvp_schema.sql에 통합됨)
- `create_missing_tables.sql` - 누락된 테이블 생성 SQL (mvp_schema.sql에 통합)
- `setup_missing_tables.py` - 누락된 테이블 생성 Python 스크립트 (mvp_schema.sql에 통합)
- `create_default_values_table.py` - 기본값 테이블 생성 스크립트 (mvp_schema.sql에 통합)
- `default_values_schema.sql` - 기본값 스키마 (mvp_schema.sql에 통합)

## 정리 일자
2025-12-27

## ⚠️ 중요 참고사항
**이 파일들은 영구 삭제되었습니다. Git 저장소는 존재하지만 커밋이 되지 않은 상태이므로 복구가 불가능합니다.**

**현재 상태**: Git 커밋 없음 → 복구 불가능

**Git을 사용하려면:**
1. 파일들을 스테이징: `git add .`
2. 커밋: `git commit -m "Initial commit"`
3. 이후부터는 Git 히스토리에서 복구 가능

현재 사용 중인 파일은 `database/setup/` 디렉토리에 남아있습니다.

