# Database Utility Scripts

이 디렉토리는 데이터베이스 관련 유틸리티 스크립트를 포함합니다.

## 파일 목록

- `audit_schema.py` - 데이터베이스 스키마 감사 스크립트
- `jsonb_schema_validator.py` - JSONB 스키마 검증 스크립트

## 실행 방법

```bash
# 스키마 감사 실행
python database/utils/scripts/audit_schema.py

# JSONB 검증 실행
python database/utils/scripts/jsonb_schema_validator.py
```

## 출력

스크립트 실행 결과는 `tests/reports/` 디렉토리에 JSON 형식으로 저장됩니다.

