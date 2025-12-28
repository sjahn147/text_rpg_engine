# [deprecated] 매니저 클래스 스키마 준수 검수 보고서

> **Deprecated 날짜**: 2025-12-28  
> **Deprecated 사유**: 이 검수 보고서는 특정 시점(2025-10-19)의 검수 결과를 기록한 것으로, 발견된 문제점들이 모두 해결되었습니다. 현재는 모든 Manager 클래스가 스키마를 올바르게 준수하며, 더 최신 정보는 `docs/architecture/MANAGER_ARCHITECTURE_COMPARISON.md`를 참조하세요.

> **작성일**: 2025-10-19  
> **검수 대상**: `app/` 폴더의 모든 매니저 클래스  
> **기준 스키마**: `database/setup/mvp_schema.sql`  
> **검수자**: AI Assistant  

## 📋 검수 개요

이 문서는 `app/` 폴더의 매니저 클래스들이 `mvp_schema.sql`의 설계 원칙과 스키마 구조를 올바르게 따르고 있는지 검수한 결과를 담고 있습니다.

## 🎯 설계 원칙 (mvp_schema.sql 기준)

### 1. 3계층 아키텍처
- **game_data**: 정적 불변 데이터 (템플릿)
- **reference_layer**: 게임 데이터와 런타임 데이터 간의 참조 관계
- **runtime_data**: 실행 중인 게임의 상태 데이터

### 2. 데이터 분리 원칙
- **정적 데이터**: `game_data` 스키마에 저장 (CELL_*, NPC_* 패턴)
- **런타임 데이터**: `runtime_data` 스키마에 저장 (UUID)
- **매핑**: `reference_layer` 스키마에서 관리

### 3. 세션 중심 설계
- 모든 런타임 데이터는 `session_id`로 연결
- `runtime_data.active_sessions`가 핵심 테이블

## 🔍 검수 결과

### ❌ **심각한 위반 사항들**

#### 1. **EntityManager** - 설계 원칙 위반

**문제점:**
- `create_entity()` 메서드가 UUID를 생성하여 `game_data.entities`에 직접 저장 (327-348번째 줄)
- 정적 데이터와 런타임 데이터를 구분하지 않음
- `_load_entities_from_db()` 메서드가 존재하지 않는 컬럼들을 조회 (433-434번째 줄)

**위반 코드:**
```python
# 잘못된 구현 - UUID를 game_data에 저장
await conn.execute("""
    INSERT INTO game_data.entities 
    (entity_id, entity_type, entity_name, ...)
    VALUES ($1, $2, $3, ...)
""", entity.entity_id, ...)  # UUID를 game_data에 저장

# 잘못된 쿼리 - 존재하지 않는 컬럼들
SELECT entity_id, name, entity_type, status, properties, position, created_at, updated_at
FROM runtime_data.runtime_entities  # 이 테이블에는 name, status, properties 컬럼이 없음
```

**올바른 설계:**
- `game_data.entities`: 정적 엔티티 템플릿 (NPC_MERCHANT_001 등)
- `runtime_data.runtime_entities`: 런타임 엔티티 인스턴스 (UUID)
- `reference_layer.entity_references`: 매핑 테이블

#### 2. **CellManager** - 부분적 수정됨

**이전 문제점 (수정됨):**
- `create_cell()` 메서드가 UUID를 `game_data.world_cells`에 저장
- 정적 템플릿과 런타임 인스턴스를 구분하지 않음

**현재 상태:**
- ✅ 수정됨: 정적 템플릿에서 런타임 인스턴스 생성하도록 변경
- ✅ 수정됨: 올바른 테이블 구조 사용

#### 3. **ActionHandler** - 스키마 불일치

**문제점:**
- `_log_action()` 메서드가 잘못된 컬럼명 사용 (496-507번째 줄)
- `runtime_data.action_logs` 테이블의 실제 스키마와 불일치

**위반 코드:**
```python
# 잘못된 컬럼명 사용
INSERT INTO runtime_data.action_logs 
(session_id, player_id, action, success, message, timestamp)
# 실제 스키마: log_id, session_id, player_id, action, success, message, timestamp
```

#### 4. **DialogueManager** - 스키마 불일치

**문제점:**
- `_save_dialogue_history()` 메서드가 잘못된 컬럼명 사용 (451-465번째 줄)
- `runtime_data.dialogue_history` 테이블의 실제 스키마와 불일치

**위반 코드:**
```python
# 잘못된 컬럼명과 구조
INSERT INTO runtime_data.dialogue_history
(history_id, session_id, player_id, npc_id, dialogue_context_id, topic_id, player_message, npc_response, timestamp)
# 실제 스키마: history_id, session_id, runtime_entity_id, context_id, speaker_type, message, relevant_knowledge, timestamp
```

### ⚠️ **중간 수준 위반 사항들**

#### 1. **하드코딩된 세션 ID**
- 모든 매니저에서 `"550e8400-e29b-41d4-a716-446655440000"` 하드코딩
- 세션 중심 설계를 무시

#### 2. **잘못된 테이블 조회**
- `EntityManager._load_entities_from_db()`: 존재하지 않는 컬럼들 조회
- `CellManager._load_cells_from_db()`: 존재하지 않는 컬럼들 조회

#### 3. **JSONB 데이터 처리 불일치**
- 일부 매니저에서 JSONB 데이터를 문자열로 처리
- 스키마에서는 JSONB 타입으로 정의됨

### ✅ **올바르게 구현된 부분들**

#### 1. **CellManager** (수정 후)
- 정적 템플릿에서 런타임 인스턴스 생성
- 올바른 테이블 구조 사용
- 매핑 테이블 활용

#### 2. **의존성 주입 패턴**
- 모든 매니저가 올바른 의존성 주입 사용
- Repository 패턴 적용

## 📊 위반 사항 요약

| 매니저 | 심각도 | 위반 사항 수 | 주요 문제 |
|--------|--------|-------------|-----------|
| EntityManager | 🔴 높음 | 3개 | 설계 원칙 위반, 잘못된 쿼리 |
| ActionHandler | 🟡 중간 | 2개 | 스키마 불일치 |
| DialogueManager | 🟡 중간 | 2개 | 스키마 불일치 |
| CellManager | ✅ 수정됨 | 0개 | 이전 문제 해결됨 |

## 🎯 수정 우선순위

### 1순위 (즉시 수정 필요)
- **EntityManager**: 설계 원칙 위반 수정
- **ActionHandler**: 스키마 불일치 수정
- **DialogueManager**: 스키마 불일치 수정

### 2순위 (개선 필요)
- 하드코딩된 세션 ID 제거
- JSONB 데이터 처리 통일
- 에러 처리 개선

## 📝 결론

현재 매니저 클래스들은 `mvp_schema.sql`의 설계 원칙을 완전히 따르지 못하고 있습니다. 특히 **EntityManager**는 심각한 설계 원칙 위반을 보이고 있으며, **ActionHandler**와 **DialogueManager**는 스키마 불일치 문제가 있습니다.

**CellManager**는 이미 수정되어 올바른 설계를 따르고 있으므로, 다른 매니저들도 동일한 패턴으로 수정해야 합니다.

---

**다음 단계**: 이 검수 결과를 바탕으로 TODO 리스트를 생성하고 순차적으로 수정 작업을 진행합니다.
