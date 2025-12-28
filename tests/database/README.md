# Database Tests

이 디렉토리는 데이터베이스 관련 테스트 파일을 포함합니다.

## 파일 목록

- `test_time_system.py` - TimeSystem 데이터베이스 테스트
- `test_error_handling.py` - 에러 처리 테스트
- `test_framework_stabilization.py` - 프레임워크 안정화 테스트
- `audit_schema.py` - 스키마 감사 스크립트
- `jsonb_schema_validator.py` - JSONB 스키마 검증기

## 실행 방법

```bash
# 개별 테스트 실행
pytest tests/database/test_time_system.py -v

# 모든 데이터베이스 테스트 실행
pytest tests/database/ -v
```

