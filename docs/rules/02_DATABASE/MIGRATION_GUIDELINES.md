# 데이터베이스 마이그레이션 가이드라인

> **최신화 날짜**: 2026-01-03

## 개요

이 문서는 RPG 게임 엔진의 데이터베이스 스키마 변경을 체계적으로 관리하기 위한 가이드라인입니다.

## 현재 마이그레이션 시스템

### 구조

```
database/
├── migrations/
│   ├── add_jsonb_validation.sql
│   ├── add_enum_types.sql
│   ├── enforce_ssot_cell_occupants.sql
│   └── ...
├── setup/
│   └── mvp_schema.sql (초기 스키마)
└── ...

scripts/
├── run_migration.py (마이그레이션 실행 스크립트)
└── ...
```

### 마이그레이션 실행 방법

```bash
# 단일 마이그레이션 실행
python scripts/run_migration.py database/migrations/add_enum_types.sql

# 또는 스크립트에서 직접 파일명 지정
python scripts/run_migration.py <migration_file>
```

## 마이그레이션 작성 규칙

### 1. 파일 명명 규칙

- 형식: `{목적}_{대상}.sql`
- 예시:
  - `add_enum_types.sql`
  - `enforce_ssot_cell_occupants.sql`
  - `add_jsonb_validation.sql`

### 2. 마이그레이션 파일 구조

```sql
-- =====================================================
-- 마이그레이션 제목
-- =====================================================
-- 목적: 마이그레이션의 목적 설명
-- 작성일: YYYY-MM-DD
-- =====================================================

-- 1. 사전 검증 (선택적)
DO $$
BEGIN
    -- 기존 상태 확인
    IF EXISTS (...) THEN
        RAISE NOTICE '이미 적용된 마이그레이션입니다.';
        RETURN;
    END IF;
END $$;

-- 2. 마이그레이션 실행
-- (실제 변경 작업)

-- 3. 검증 (선택적)
-- (변경 사항 확인)
```

### 3. 안전성 원칙

#### ✅ DO

1. **멱등성 보장**
   - 같은 마이그레이션을 여러 번 실행해도 안전해야 함
   - `IF NOT EXISTS` 또는 `ON CONFLICT` 사용

2. **트랜잭션 사용**
   - `run_migration.py`가 자동으로 트랜잭션 처리
   - 실패 시 롤백 보장

3. **데이터 검증**
   - 기존 데이터와의 호환성 확인
   - 마이그레이션 전 데이터 정리 스크립트 필요 시 별도 작성

4. **백업 권장**
   - 중요한 마이그레이션 전 데이터베이스 백업

#### ❌ DON'T

1. **데이터 손실 위험 작업**
   - 사용자 컨펌 없이 대량 데이터 삭제 금지
   - 스키마 변경 전 데이터 호환성 확인 필수

2. **의존성 무시**
   - 다른 마이그레이션과의 의존성 고려
   - 실행 순서 명시

3. **하드코딩된 값**
   - 환경별로 다른 값이 필요한 경우 변수 사용

## 마이그레이션 유형

### 1. 스키마 변경

- 테이블 생성/삭제
- 컬럼 추가/삭제/변경
- 인덱스 생성/삭제
- 제약조건 추가/삭제

**예시:**
```sql
-- ENUM 타입 생성
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'entity_type_enum') THEN
        CREATE TYPE entity_type_enum AS ENUM ('player', 'npc', 'monster', 'creature');
    END IF;
END $$;

-- 컬럼 타입 변경
ALTER TABLE game_data.entities
ALTER COLUMN entity_type TYPE entity_type_enum 
USING entity_type::entity_type_enum;
```

### 2. 데이터 마이그레이션

- 기존 데이터 변환
- 데이터 정리
- 기본값 설정

**예시:**
```sql
-- JSONB 데이터 정리
UPDATE runtime_data.entity_states
SET inventory = '{}'::jsonb
WHERE inventory = '[]'::jsonb;
```

### 3. 트리거/함수 생성

- 데이터 무결성 보장
- 자동 동기화

**예시:**
```sql
-- SSOT 강제 트리거
CREATE OR REPLACE FUNCTION runtime_data.sync_cell_occupants_from_position()
RETURNS TRIGGER AS $$
BEGIN
    -- 동기화 로직
END;
$$ LANGUAGE plpgsql;
```

## 마이그레이션 실행 프로세스

### 1. 개발 환경

```bash
# 1. 마이그레이션 파일 작성
# database/migrations/new_migration.sql

# 2. 마이그레이션 실행
python scripts/run_migration.py database/migrations/new_migration.sql

# 3. 검증
python scripts/check_enum_types.py  # 예시
```

### 2. 테스트 환경

- 개발 환경에서 검증 완료 후 실행
- 동일한 프로세스 적용

### 3. 프로덕션 환경

- **⚠️ 주의**: 프로덕션 환경에서는 반드시:
  1. 백업 생성
  2. 다운타임 계획 수립 (필요시)
  3. 롤백 계획 수립
  4. 단계적 배포 고려

## 마이그레이션 체크리스트

### 작성 시

- [ ] 파일명이 명확한가?
- [ ] 목적과 변경 사항이 주석으로 명시되어 있는가?
- [ ] 멱등성이 보장되는가?
- [ ] 기존 데이터와의 호환성이 확인되었는가?
- [ ] 트랜잭션으로 안전하게 실행되는가?

### 실행 전

- [ ] 개발 환경에서 테스트 완료
- [ ] 데이터베이스 백업 (중요한 변경의 경우)
- [ ] 의존성 마이그레이션 확인
- [ ] 롤백 계획 수립

### 실행 후

- [ ] 마이그레이션 성공 확인
- [ ] 데이터 무결성 검증
- [ ] 애플리케이션 테스트
- [ ] 문서 업데이트

## 현재 마이그레이션 목록

### 완료된 마이그레이션

#### 1. add_jsonb_validation.sql
**목적**: JSONB 필드 구조 검증을 위한 CHECK 제약조건 추가

**변경 사항**:
- `runtime_data.entity_states` 테이블:
  - `chk_position_structure`: `current_position` 구조 검증
  - `chk_inventory_structure`: `inventory` 구조 검증
  - `chk_stats_structure`: `current_stats` 구조 검증
- `runtime_data.object_states` 테이블:
  - `chk_object_state_structure`: `object_state` 구조 검증
  - `chk_object_position_structure`: `position` 구조 검증

**실행 방법**:
```bash
python scripts/run_migration.py database/migrations/add_jsonb_validation.sql
```

**주의 사항**:
- 기존 데이터가 제약조건을 위반하는 경우 마이그레이션 전 데이터 정리 필요
- `scripts/fix_jsonb_data_before_migration.py` 실행 권장

---

#### 2. enforce_ssot_cell_occupants.sql
**목적**: `cell_occupants` 테이블의 SSOT(Single Source of Truth) 강제

**변경 사항**:
- `prevent_cell_occupants_direct_write()`: 직접 쓰기 방지 트리거 함수
- `trg_prevent_cell_occupants_direct_write`: INSERT/UPDATE/DELETE 차단 트리거
- `sync_cell_occupants_from_position()`: 자동 동기화 트리거 함수
- `trg_sync_cell_occupants_from_position`: `entity_states.current_position` 변경 시 자동 동기화

**실행 방법**:
```bash
python scripts/run_migration.py database/migrations/enforce_ssot_cell_occupants.sql
```

**주의 사항**:
- 마이그레이션 후 `CellManager` 코드가 SSOT를 준수하는지 확인 필요
- 직접 `cell_occupants`에 쓰는 코드는 모두 수정 필요

---

#### 3. add_enum_types.sql
**목적**: VARCHAR + CHECK 제약조건을 ENUM 타입으로 변경하여 타입 안전성 향상

**변경 사항**:
- ENUM 타입 생성:
  - `entity_type_enum`: player, npc, monster, creature
  - `carrier_type_enum`: skill, buff, item, blessing, curse, ritual
  - `effect_type_enum`: damage, heal, buff, debuff, status
- 컬럼 타입 변경:
  - `game_data.entities.entity_type` → `entity_type_enum`
  - `reference_layer.entity_references.entity_type` → `entity_type_enum`
  - `runtime_data.cell_occupants.entity_type` → `entity_type_enum`
  - `game_data.effect_carriers.carrier_type` → `carrier_type_enum`

**실행 방법**:
```bash
python scripts/run_migration.py database/migrations/add_enum_types.sql
```

**주의 사항**:
- Python 코드의 `EntityType` Enum이 데이터베이스 ENUM과 일치하는지 확인 필요
- 기존 데이터가 ENUM 값과 일치하는지 확인 필요

## 향후 개선 사항

### Alembic 도입 (선택적)

현재는 SQL 파일 기반 마이그레이션을 사용하지만, 향후 Alembic 도입을 고려할 수 있습니다.

**장점:**
- 버전 관리 자동화
- 마이그레이션 순서 관리
- 롤백 지원

**단점:**
- 초기 설정 복잡도
- SQL 직접 작성의 유연성 감소

**결정 기준:**
- 마이그레이션 빈도가 높아지면 고려
- 팀 규모가 커지면 고려
- 복잡한 마이그레이션이 많아지면 고려

## 참고 문서

- `docs/rules/01_PHILOSOPHY.md`: 핵심 개발 철학
- `docs/rules/DATABASE_SCHEMA_DESIGN_GUIDELINES.md`: 데이터베이스 스키마 설계 가이드라인
- `docs/rules/TYPE_SAFETY_GUIDELINES.md`: 타입 안전성 종합 가이드라인

## 외부 참고

- PostgreSQL 문서: https://www.postgresql.org/docs/current/ddl-alter.html
- Alembic 문서: https://alembic.sqlalchemy.org/
- 현재 마이그레이션 스크립트: `scripts/run_migration.py`

