# [deprecated] 대화 시스템 동기화 이슈

> **Deprecated 날짜**: 2025-12-28  
> **Deprecated 사유**: 이 문서에서 분석한 대화 시스템 동기화 이슈들이 모두 해결되었습니다. 현재는 DialogueManager가 완전히 구현되어 안정적으로 작동합니다.

## 1. 데이터 타입 동기화 문제

### 1.1 엔티티 ID 타입 불일치
```sql
-- game_data.entities
entity_id VARCHAR(50)  -- 예상되는 정의

-- game_data.dialogue_contexts
entity_id INTEGER      -- 현재 정의
```
- **문제점**: 외래 키 제약 조건 위반 가능성
- **해결방안**: 
  - 모든 ID 타입을 VARCHAR(50)으로 통일
  - ID 형식에 대한 명확한 규칙 수립 (예: 'ENT_001', 'NPC_001' 등)

### 1.2 JSON 필드 구조 불일치
```json
// dialogue_contexts.available_topics
{
    "topics": ["greeting", "shop_items"]  // 배열을 포함한 객체
}

// dialogue_states.active_topics
["shop_items", "weapon_info"]  // 단순 배열
```
- **문제점**: 일관성 없는 JSON 구조로 인한 파싱 오류 가능성
- **해결방안**: 
  - JSON 스키마 정의 및 문서화
  - 각 JSON 필드의 구조 표준화

## 2. 런타임 동기화 문제

### 2.1 세션 데이터 관리
```sql
-- reference_layer.entity_references
session_id VARCHAR(100)

-- runtime_data.dialogue_states
session_id VARCHAR(100)

-- runtime_data.dialogue_history
session_id VARCHAR(100)
```
- **문제점**:
  - 세션 종료 시 데이터 정리 누락 가능성
  - 고아 레코드(orphaned records) 발생 위험
- **해결방안**:
  - 세션 관리 테이블 도입
  - 캐스케이드 삭제 규칙 설정
  - 세션 정리 트리거 구현

### 2.2 상태 변경 전파
```sql
-- runtime_data.dialogue_states
conversation_state JSON
last_updated TIMESTAMP

-- runtime_data.dialogue_history
timestamp TIMESTAMP
```
- **문제점**:
  - 상태 변경 시 관련 테이블 동기화 누락 가능성
  - 타임스탬프 불일치 발생 가능성
- **해결방안**:
  - 상태 변경 트리거 구현
  - 트랜잭션 관리 강화
  - 타임스탬프 자동 업데이트 설정

## 3. 조건부 데이터 동기화

### 3.1 시간 기반 조건
```json
// dialogue_knowledge.conditions
{
    "time_of_day": "evening",
    "player_reputation": {"min": 0}
}
```
- **문제점**:
  - 게임 내 시간과 실제 시간의 동기화
  - 여러 시간대(timezone) 처리
- **해결방안**:
  - 게임 시간 관리 시스템 도입
  - UTC 기준 시간 사용
  - 시간 변환 유틸리티 구현

### 3.2 상태 기반 조건
```json
// dialogue_knowledge.conditions
{
    "player_level": {"min": 1, "max": 5}
}
```
- **문제점**:
  - 플레이어 상태 변경 시 대화 조건 재평가 필요
  - 조건 평가 성능 이슈
- **해결방안**:
  - 상태 변경 이벤트 시스템 구현
  - 조건 캐싱 메커니즘 도입
  - 인덱싱 전략 수립

## 4. NULL 처리 표준화

### 4.1 JSON NULL 처리
```sql
-- dialogue_history.relevant_knowledge
'null'  -- 문자열
NULL    -- SQL NULL
```
- **문제점**:
  - NULL 표현 방식 불일치
  - 쿼리 결과 불일치 가능성
- **해결방안**:
  - NULL 처리 정책 수립
  - JSON NULL과 SQL NULL 매핑 규칙 정의
  - 일관된 NULL 체크 함수 구현

## 5. 구현 권장사항

1. **트랜잭션 관리**
   ```sql
   BEGIN TRANSACTION;
     -- 대화 상태 업데이트
     UPDATE runtime_data.dialogue_states ...
     -- 히스토리 기록
     INSERT INTO runtime_data.dialogue_history ...
   COMMIT;
   ```

2. **트리거 구현**
   ```sql
   CREATE TRIGGER dialogue_state_update
   AFTER UPDATE ON runtime_data.dialogue_states
   FOR EACH ROW
   BEGIN
     -- 관련 테이블 동기화
   END;
   ```

3. **세션 정리 프로시저**
   ```sql
   CREATE PROCEDURE cleanup_session(session_id VARCHAR(100))
   BEGIN
     -- 순서대로 데이터 정리
     DELETE FROM runtime_data.dialogue_history ...
     DELETE FROM runtime_data.dialogue_states ...
     DELETE FROM reference_layer.entity_references ...
   END;
   ```

4. **상태 검증 함수**
   ```sql
   CREATE FUNCTION validate_dialogue_state(state_json JSON)
   RETURNS BOOLEAN
   BEGIN
     -- JSON 구조 검증
     -- 필수 필드 확인
     -- 타입 검증
   END;
   ``` 