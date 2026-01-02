# 현재 I/O 문제점 상세 분석

## 작성일
2026-01-01

## 문제 인식

> "오픈월드 게임을 개발하는데 모든 월드에서 실시간으로 io하고 있으면 컴퓨터가 죽잖아요."

**정확한 지적입니다.** 현재 시스템은 오픈월드 게임에 부적합한 아키텍처입니다.

## 현재 코드의 문제 패턴

### 1. 모든 처리가 동기 DB I/O

#### EntityManager
```python
# app/managers/entity_manager.py
async def update_entity_state(self, entity_id, new_state):
    """즉시 DB 쓰기 - 문제 패턴"""
    pool = await self.db.pool
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE runtime_data.entity_states
            SET current_stats = $1, current_position = $2, updated_at = NOW()
            WHERE runtime_entity_id = $3
        """, new_state.stats, new_state.position, entity_id)
```

**문제**:
- NPC가 행동할 때마다 즉시 DB 업데이트
- 플레이어가 보지 않는 셀의 NPC도 실시간 업데이트
- 1000개 NPC × 1회/5초 = 200회/초 DB 쓰기

### 2. 캐시 없이 매번 DB 조회

#### CellManager
```python
# app/managers/cell_manager.py
async def get_cell_contents(self, cell_id):
    """매번 DB 쿼리 - 문제 패턴"""
    pool = await self.db.pool
    async with pool.acquire() as conn:
        # 매번 쿼리 (캐시 없음)
        entities = await conn.fetch("""
            SELECT * FROM runtime_data.entity_states
            WHERE current_position->>'runtime_cell_id' = $1
        """, cell_id)
```

**문제**:
- 같은 셀을 1초에 10번 조회해도 매번 DB 쿼리
- 불필요한 네트워크 트래픽
- DB 부하 증가

### 3. 배치 처리 부재

#### 현재 패턴
```python
# 플레이어 이동 시
for entity in nearby_entities:
    await update_entity_state(entity.id, new_state)  # 각각 즉시 DB 쓰기

# 10개 엔티티 업데이트 = 10번의 DB 쓰기
```

**문제**:
- 배치 처리 없음
- 트랜잭션 오버헤드 누적
- 네트워크 왕복 횟수 증가

### 4. 부하 관리 부재

#### 현재 상태
- **캐싱**: 없음
- **배치 처리**: 없음
- **Lazy Loading**: 없음
- **체크포인트**: 없음
- **이벤트 큐**: 없음

## 오픈월드 게임의 현실

### 시나리오: 1000개 셀, 각 셀에 10개 NPC

#### 현재 방식 (비현실적)
```
1000개 셀 × 10개 NPC = 10,000개 NPC
10,000개 NPC × 행동 빈도 1회/5초 = 2,000회/초 DB 쓰기

플레이어 100명 × 셀 조회 2회/초 = 200회/초 DB 읽기

총: 2,200회/초 DB I/O
→ 서버 다운
```

#### 최적화 후 (현실적)
```
활성 셀 (플레이어 근처): 9개 셀 (3×3 그리드)
9개 셀 × 10개 NPC = 90개 NPC (상세 처리)
90개 NPC × 행동 빈도 1회/5초 = 18회/초 (메모리 업데이트)

체크포인트: 5초마다 배치 저장 = 18회/5초 = 3.6회/초 DB 쓰기

외부 셀: 체크포인트만 (플레이어 접근 시 처리)
→ DB 쓰기 거의 없음

총: 약 4회/초 DB 쓰기 (99.8% 감소)
```

## 부하 관리가 필요한 부분

### 1. EntityManager
- **현재**: 모든 엔티티 상태 변경이 즉시 DB 쓰기
- **필요**: 메모리 업데이트 + 체크포인트 배치 쓰기

### 2. CellManager
- **현재**: 매번 DB 조회
- **필요**: 캐시 기반 조회 + Lazy Loading

### 3. GameService
- **현재**: 게임 시작 시 다중 즉시 I/O
- **필요**: 배치 트랜잭션

### 4. 이벤트 처리 (미구현)
- **현재**: 이벤트 매니저 없음
- **필요**: 이벤트 큐 + 체크포인트 이벤트 처리

## 성능 병목 지점

### 1. DB 연결 풀 고갈
- 각 작업마다 연결 획득/해제
- 동시 요청 시 연결 풀 고갈
- **해결**: 연결 풀 공유 + 배치 처리

### 2. 트랜잭션 오버헤드
- 각 업데이트마다 트랜잭션
- 트랜잭션 시작/커밋 오버헤드
- **해결**: 배치 트랜잭션

### 3. 네트워크 지연
- 각 I/O마다 네트워크 왕복
- 지연 시간 누적
- **해결**: 배치 처리로 왕복 횟수 감소

### 4. 불필요한 처리
- 플레이어가 보지 않는 셀도 실시간 업데이트
- **해결**: Lazy Loading + 체크포인트

## 결론

현재 시스템은 **오픈월드 게임에 부적합**합니다.

**근본적인 문제**:
1. 모든 처리가 DB I/O로 수행
2. 부하 관리 부재
3. 확장성 문제

**필요한 해결책**:
1. ✅ 메모리/캐시 기반 처리
2. ✅ 체크포인트 배치 입력
3. ✅ Lazy Loading
4. ✅ 이벤트 매니저 구현

자세한 구현 계획은 `docs/architecture/PERFORMANCE_OPTIMIZATION_STRATEGY.md`와 `docs/architecture/IMPLEMENTATION_ROADMAP.md` 참조

