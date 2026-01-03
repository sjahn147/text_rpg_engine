# 데이터베이스 스키마 설계 가이드라인

> **최신화 날짜**: 2026-01-03  
> **적용 범위**: 데이터베이스 스키마 설계 및 수정 시 필수 읽기

## ⚠️ 중요: mvp_schema.sql 참조 필수

**모든 데이터베이스 관련 작업은 반드시 `database/setup/mvp_schema.sql`을 참조해야 합니다.**

### 참조가 필요한 시점

- ✅ 새로운 테이블/컬럼 추가 전
- ✅ FK 관계 설계 시
- ✅ 인덱스 설계 시
- ✅ JSONB 필드 구조 설계 시
- ✅ Manager/Repository 구현 시
- ✅ Dialogue Manager 등 시스템 구현 시

### 참조 방법

```bash
# 스키마 파일 위치
database/setup/mvp_schema.sql

# 특정 테이블 확인
cat database/setup/mvp_schema.sql | grep -A 20 "CREATE TABLE game_data.dialogue_contexts"

# 대화 시스템 관련 테이블 확인
grep -E "dialogue|Dialogue" database/setup/mvp_schema.sql
```

### 스키마 파일의 역할

1. **SSOT (Single Source of Truth)**: 스키마 파일이 데이터베이스 구조의 단일 진실원
2. **일관성 보장**: 코드와 스키마 간 일관성 보장
3. **타입 안전성**: 스키마에 정의된 타입과 제약조건 준수
4. **마이그레이션 기준**: 스키마 변경 시 마이그레이션 계획 수립

**⚠️ 경고**: 스키마 파일을 참조하지 않고 코드를 작성하면 타입 불일치, FK 오류, 데이터 무결성 문제가 발생할 수 있습니다.

## 1. 개요

이 문서는 RPG 엔진의 데이터베이스 스키마 설계 원칙과 가이드라인을 정의합니다.

## 2. 핵심 설계 원칙

### 2.1 Data-Centric Development (데이터 중심 개발)

- **데이터베이스 스키마가 SSOT (Single Source of Truth)**
- 비즈니스 로직은 데이터 구조 위에서 정의
- 코드가 데이터에 맞춰 적응해야지, 데이터가 코드에 종속되어서는 안 됨

### 2.2 3계층 스키마 구조

```
┌─────────────────────────────────────┐
│   game_data                         │  ← 불변의 게임 원본 데이터
│   (정적 데이터, 템플릿)              │
├─────────────────────────────────────┤
│   reference_layer                   │  ← 게임 데이터와 런타임 데이터 간 참조
│   (참조 관계)                        │
├─────────────────────────────────────┤
│   runtime_data                      │  ← 실행 중인 게임의 상태 데이터
│   (런타임 데이터, 세션별)            │
└─────────────────────────────────────┘
```

### 2.3 SSOT (Single Source of Truth) 원칙

각 데이터는 **단일 소스**에서만 관리되어야 합니다:

- **위치 정보**: `runtime_data.entity_states.current_position`이 SSOT
  - `runtime_data.cell_occupants`는 트리거로 자동 동기화 (직접 쓰기 금지)
- **엔티티 참조**: `reference_layer.entity_references`가 SSOT
- **오브젝트 상태**: `runtime_data.object_states`가 SSOT

## 3. 외래키 (FK) 설계 원칙

### 3.1 FK 사용 원칙

**✅ 권장**: 명시적 FK 제약조건 사용

```sql
-- ✅ 좋은 예: FK 제약조건으로 명시
ALTER TABLE game_data.equipment_weapons
ADD COLUMN effect_carrier_id UUID,
ADD CONSTRAINT fk_weapons_effect_carrier
    FOREIGN KEY (effect_carrier_id)
    REFERENCES game_data.effect_carriers(effect_id)
    ON DELETE SET NULL;

CREATE INDEX idx_weapons_effect_carrier 
ON game_data.equipment_weapons(effect_carrier_id);
```

**이유**:
1. **타입 안전성**: FK 제약조건으로 타입 안전성 보장
2. **데이터 무결성**: 참조 무결성 보장 (존재하지 않는 레코드 참조 방지)
3. **쿼리 효율성**: JOIN 쿼리가 쉬움, 인덱스 활용 가능
4. **명확성**: 스키마만 봐도 관계가 명확함

**❌ 비권장**: JSONB 필드에 ID 저장

```sql
-- ❌ 나쁜 예: JSONB 필드에 ID 저장
ALTER TABLE game_data.equipment_weapons
ADD COLUMN properties JSONB;  -- {"effect_carrier_id": "uuid-string"}

-- 문제점:
-- 1. FK 제약조건 불가능
-- 2. 타입 안전성 없음
-- 3. 쿼리 어려움
-- 4. 인덱스 활용 어려움
```

### 3.2 FK 삭제 정책

- **ON DELETE SET NULL**: 선택적 관계 (NULL 허용)
- **ON DELETE CASCADE**: 강제 관계 (부모 삭제 시 자식도 삭제)
- **ON DELETE RESTRICT**: 제한 관계 (자식이 있으면 부모 삭제 불가)

**선택 기준**:
- 선택적 관계: `ON DELETE SET NULL` (예: 아이템의 Effect Carrier)
- 필수 관계: `ON DELETE CASCADE` (예: 세션 삭제 시 엔티티 삭제)
- 보호 관계: `ON DELETE RESTRICT` (예: 엔티티가 있으면 게임 데이터 삭제 불가)

## 4. UUID 타입 사용

### 4.1 UUID 컬럼 정의

**✅ 권장**: PostgreSQL `UUID` 타입 사용

```sql
CREATE TABLE runtime_data.runtime_entities (
    runtime_entity_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    game_entity_id VARCHAR(50) NOT NULL,
    session_id UUID NOT NULL,
    ...
);
```

**이유**:
- 타입 안정성 보장
- 인덱스 효율성
- asyncpg 자동 변환

**❌ 비권장**: `VARCHAR(36)` 사용

```sql
-- ❌ 나쁜 예
CREATE TABLE runtime_data.runtime_entities (
    runtime_entity_id VARCHAR(36) PRIMARY KEY,  -- 타입 안정성 없음
    ...
);
```

### 4.2 JSONB 필드 내 UUID 저장

**✅ 권장**: JSONB는 문자열로 저장 (JSON 표준)

```sql
CREATE TABLE runtime_data.entity_states (
    current_position JSONB,  -- {"x": 5.0, "y": 4.0, "runtime_cell_id": "uuid-string"}
    ...
);
```

**이유**:
- JSON 표준 준수
- 직렬화/역직렬화 안정성

**❌ 비권장**: JSONB에 UUID 객체 저장 시도

```python
# ❌ 나쁜 예: UUID 객체를 JSONB에 저장 시도
position = {'runtime_cell_id': uuid.uuid4()}  # UUID 객체
json.dumps(position)  # TypeError 발생
```

## 5. 인덱스 설계 원칙

### 5.1 인덱스 생성 규칙

**✅ 권장**: FK 컬럼에 인덱스 생성

```sql
-- FK 컬럼에 인덱스 생성
CREATE INDEX idx_weapons_effect_carrier 
ON game_data.equipment_weapons(effect_carrier_id);
```

**이유**: JOIN 쿼리 성능 향상

### 5.2 JSONB 인덱스

**✅ 권장**: GIN 인덱스 사용 (JSONB 쿼리 최적화)

```sql
-- JSONB 컬럼에 GIN 인덱스
CREATE INDEX idx_entity_properties 
ON game_data.entities USING GIN (entity_properties);
```

**주의**: JSONB 내 UUID는 인덱스 불필요 (조회용)

## 6. ENUM 타입 사용

### 6.1 ENUM 정의

**✅ 권장**: PostgreSQL ENUM 타입 사용

```sql
-- ENUM 타입 정의
CREATE TYPE entity_type_enum AS ENUM (
    'player',
    'npc',
    'monster',
    'creature'
);

-- ENUM 사용
CREATE TABLE game_data.entities (
    entity_id VARCHAR(50) PRIMARY KEY,
    entity_type entity_type_enum NOT NULL,
    ...
);
```

**이유**:
- 타입 안전성 보장
- 허용 값 제한
- 쿼리 효율성

### 6.2 ENUM vs VARCHAR

**ENUM 사용 권장 케이스**:
- 값의 목록이 고정되어 있음
- 타입 안전성이 중요함
- 쿼리 성능이 중요함

**VARCHAR 사용 권장 케이스**:
- 값의 목록이 자주 변경됨
- 확장성이 중요함

## 7. JSONB 필드 설계

### 7.1 JSONB 사용 원칙

**✅ 권장**: 구조화된 데이터 저장

```sql
CREATE TABLE game_data.entities (
    base_stats JSONB,  -- {"hp": 100, "mp": 50, "strength": 10}
    default_abilities JSONB,  -- {"skills": ["SKILL_001"], "magic": ["MAGIC_001"]}
    ...
);
```

**주의사항**:
- JSONB 내 UUID는 반드시 문자열로 저장
- JSONB 구조는 문서화 필수
- JSONB 필드에 인덱스가 필요한 경우 GIN 인덱스 사용

### 7.2 JSONB 구조 검증

**✅ 권장**: CHECK 제약조건으로 구조 검증

```sql
CREATE TABLE runtime_data.entity_states (
    current_position JSONB,
    CONSTRAINT chk_position_structure CHECK (
        current_position IS NULL OR
        (
            jsonb_typeof(current_position -> 'x') IN ('number', 'null') AND
            jsonb_typeof(current_position -> 'y') IN ('number', 'null')
        )
    )
);
```

## 8. 마이그레이션 원칙

### 8.1 스키마 변경 시 필수 사항

1. **사용자 컨펌 요청**: 위험한 작업(삭제, 수정, 스키마 변경) 시 반드시 사용자 컨펌
2. **백업 생성**: 데이터베이스 조작 전 자동 백업 생성
3. **롤백 계획**: 마이그레이션 실패 시 롤백 방법 명시

### 8.2 마이그레이션 스크립트 작성

**✅ 권장**: Idempotent 마이그레이션

```sql
-- ✅ 좋은 예: Idempotent 마이그레이션
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_weapons_effect_carrier'
    ) THEN
        ALTER TABLE game_data.equipment_weapons
        ADD COLUMN effect_carrier_id UUID,
        ADD CONSTRAINT fk_weapons_effect_carrier
            FOREIGN KEY (effect_carrier_id)
            REFERENCES game_data.effect_carriers(effect_id)
            ON DELETE SET NULL;
        
        CREATE INDEX idx_weapons_effect_carrier 
        ON game_data.equipment_weapons(effect_carrier_id);
    END IF;
END $$;
```

**이유**: 여러 번 실행해도 안전함

## 9. 금지 사항

### 9.1 스키마 설계 금지 사항

- ❌ **추측 로직**: "아마도 이 형식일 것이다"와 같은 추측에 의존하는 설계
- ❌ **타입 추측**: VARCHAR로 UUID 저장 후 코드에서 UUID라고 추측
- ❌ **기본값으로 에러 은폐**: NULL 허용으로 에러 상황 은폐
- ❌ **FK 없이 관계 표현**: JSONB 필드에만 ID 저장

### 9.2 마이그레이션 금지 사항

- ❌ **사용자 컨펌 없이 스키마 변경**: 위험한 작업 시 반드시 컨펌 요청
- ❌ **백업 없이 데이터 변경**: 데이터 삭제/수정 전 백업 필수
- ❌ **롤백 계획 없이 마이그레이션**: 실패 시 롤백 방법 명시 필수

## 10. 미구현 및 추가 필요 사항

### 10.1 Effect Carrier 연결을 위한 FK 추가 (기획 필요)

- [ ] **아이템/장비 테이블에 `effect_carrier_id` FK 추가**
  - [ ] `items.effect_carrier_id` FK 추가 (스키마 확인 후 필요 시)
  - [ ] `equipment_weapons.effect_carrier_id` FK 추가 (스키마 확인 후 필요 시)
  - [ ] `equipment_armors.effect_carrier_id` FK 추가 (스키마 확인 후 필요 시)
  - [ ] 인덱스 추가 (쿼리 성능 향상)
  - **참고**: `03_SYSTEMS/EFFECT_CARRIER_GUIDELINES.md` - 4.1 스키마 설계
  - **주의**: `mvp_schema.sql` 참조 필수, 사용자 컨펌 요청 필수
  - **주의**: Data-Centric Development 원칙 준수

### 10.2 퀘스트 시스템 스키마 추가 (기획 필요)

- [ ] **`runtime_data.quests` 테이블 생성**
  - [ ] 퀘스트 상태 관리 테이블 설계
  - [ ] 퀘스트 템플릿 테이블 설계 (`game_data.quest_templates` - 향후)
  - [ ] 퀘스트 이벤트 추적 방법 결정 (`triggered_events` 활용 vs 별도 테이블)
  - **참고**: `03_SYSTEMS/QUEST_SYSTEM_GUIDELINES.md` - 데이터베이스 구조
  - **참고**: `docs/design/UI_REDESIGN_BG3_STYLE_CORRECTIONS.md` - 퀘스트 저장 구조
  - **주의**: `mvp_schema.sql` 참조 필수, 사용자 컨펌 요청 필수

### 10.3 스킬/주문 시스템 스키마 검증 (검증 필요)

- [ ] **스키마 확인 및 검증**
  - [ ] `abilities_skills` 테이블 구조 확인 (`mvp_schema.sql` 참조)
  - [ ] `abilities_magic` 테이블 구조 확인 (`mvp_schema.sql` 참조)
  - [ ] `entities.default_abilities` JSONB 필드 구조 확인
  - [ ] 스키마와 코드 간 일관성 검증
  - **참고**: `03_SYSTEMS/ABILITIES_SYSTEM_GUIDELINES.md` - 데이터베이스 구조

### 10.4 향후 스키마 추가 (기획 필요)

- [ ] **캐릭터 클래스 시스템**
  - [ ] `game_data.character_classes` 테이블 설계
  - [ ] 클래스별 스킬/주문 연결 방법 정의
  - [ ] 클래스별 능력치 보너스 정의

- [ ] **레벨 및 경험치 시스템**
  - [ ] `runtime_data.character_progression` 테이블 설계
  - [ ] 레벨업 시스템 설계
  - [ ] 경험치 획득/소모 로직 정의

- [ ] **퀘스트 템플릿 시스템**
  - [ ] `game_data.quest_templates` 테이블 설계
  - [ ] 퀘스트 템플릿 구조 정의
  - [ ] 퀘스트 템플릿과 런타임 퀘스트 연결 방법 정의

### 10.5 정책 결정 필요

- [ ] **FK 추가 정책**
  - [ ] 기존 데이터 마이그레이션 방법 결정
  - [ ] FK 추가 시 NULL 허용 여부 결정
  - [ ] FK 추가 시 기존 데이터 검증 방법 결정

- [ ] **스키마 변경 승인 프로세스**
  - [ ] 스키마 변경 요청 프로세스 정의
  - [ ] 스키마 변경 검토 기준 정의
  - [ ] 스키마 변경 롤백 계획 수립 방법 정의

## 11. 참고 문서

- `docs/rules/01_PHILOSOPHY.md`: 핵심 개발 철학
- `docs/rules/MIGRATION_GUIDELINES.md`: 마이그레이션 가이드라인
- `docs/rules/TYPE_SAFETY_GUIDELINES.md`: 타입 안전성 가이드라인
- `docs/architecture/01_ARCH_DB_SCHEMA_README.md`: 데이터베이스 스키마 아키텍처
- `database/setup/mvp_schema.sql`: MVP 스키마 정의 ⭐ **필수 참조**
- `03_SYSTEMS/EFFECT_CARRIER_GUIDELINES.md`: Effect Carrier 시스템
- `03_SYSTEMS/ABILITIES_SYSTEM_GUIDELINES.md`: 스킬/주문 시스템
- `03_SYSTEMS/QUEST_SYSTEM_GUIDELINES.md`: 퀘스트 시스템
- `04_DEVELOPMENT/UI_REDESIGN_TODO.md`: UI 리디자인 TODO

