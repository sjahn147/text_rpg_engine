# 현재 I/O 패턴 분석 및 문제점

## 작성일
2026-01-01

## 현재 코드의 I/O 패턴 분석

### 1. EntityManager의 I/O 패턴

#### 즉시 DB 쓰기 패턴
```python
# app/managers/entity_manager.py
async def update_entity_state(self, entity_id, new_state):
    """엔티티 상태 업데이트 - 즉시 DB 쓰기"""
    pool = await self.db.pool
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE runtime_data.entity_states
            SET current_stats = $1,
                current_position = $2,
                updated_at = NOW()
            WHERE runtime_entity_id = $3
        """, new_state.stats, new_state.position, entity_id)
```

**문제점**:
- 모든 상태 변경이 즉시 DB에 반영
- 플레이어가 보지 않는 NPC도 실시간 업데이트
- 네트워크 지연 누적

### 2. CellManager의 I/O 패턴

#### 매번 DB 조회 패턴
```python
# app/managers/cell_manager.py
async def get_cell_contents(self, cell_id):
    """셀 컨텐츠 조회 - 매번 DB 쿼리"""
    pool = await self.db.pool
    async with pool.acquire() as conn:
        # 엔티티 조회
        entities = await conn.fetch("""
            SELECT * FROM runtime_data.entity_states
            WHERE current_position->>'runtime_cell_id' = $1
        """, cell_id)
        
        # 오브젝트 조회
        objects = await conn.fetch("""
            SELECT * FROM runtime_data.object_states
            WHERE current_cell_id = $1
        """, cell_id)
```

**문제점**:
- 캐시 없이 매번 DB 조회
- 같은 셀을 여러 번 조회해도 매번 쿼리
- 불필요한 네트워크 트래픽

### 3. GameService의 I/O 패턴

#### 게임 시작 시 다중 I/O
```python
# app/services/gameplay/game_service.py
async def start_game(self, player_template_id, start_cell_id):
    """게임 시작 - 다중 즉시 I/O"""
    # 1. 세션 생성 (즉시 DB 쓰기)
    await self.runtime_data_repo.create_session(...)
    
    # 2. 셀 인스턴스 생성 (즉시 DB 쓰기)
    await self.instance_factory.create_cell_instance(...)
    
    # 3. 플레이어 인스턴스 생성 (즉시 DB 쓰기)
    await self.instance_factory.create_player_instance(...)
    
    # 4. 상태 조회 (즉시 DB 읽기)
    entity_state = await self.runtime_data_repo.get_entity_state(...)
```

**문제점**:
- 게임 시작 시 여러 번의 DB I/O
- 트랜잭션 오버헤드
- 응답 시간 지연

### 4. CellService의 I/O 패턴

#### 플레이어 이동 시 즉시 I/O
```python
# app/services/gameplay/cell_service.py
async def move_player(self, session_id, target_cell_id):
    """플레이어 이동 - 즉시 DB 업데이트"""
    # 1. 현재 위치 조회 (DB 읽기)
    current_position = await conn.fetchrow("""
        SELECT current_position FROM runtime_data.entity_states
        WHERE runtime_entity_id = $1
    """, player_id)
    
    # 2. 새 위치로 업데이트 (즉시 DB 쓰기)
    await conn.execute("""
        UPDATE runtime_data.entity_states
        SET current_position = $1, updated_at = NOW()
        WHERE runtime_entity_id = $2
    """, new_position, player_id)
```

**문제점**:
- 이동 시마다 즉시 DB 업데이트
- 짧은 시간 내 여러 이동 시 I/O 폭증
- 배치 처리 없음

## 부하 분석

### 시나리오: 100명의 플레이어, 각각 10개의 NPC가 있는 셀

#### 현재 방식
```
플레이어 100명 × 이동 빈도 1회/초 = 100회/초 DB 쓰기
NPC 1000개 × 행동 빈도 1회/5초 = 200회/초 DB 쓰기
총: 300회/초 DB 쓰기

셀 조회: 플레이어 100명 × 조회 빈도 2회/초 = 200회/초 DB 읽기
총: 500회/초 DB I/O
```

#### 최적화 후 (예상)
```
플레이어 100명: 메모리 업데이트 → 체크포인트 1회/5초 = 20회/초
NPC 1000개: 체크포인트만 (플레이어 근처만 상세) = 50회/초
총: 70회/초 DB 쓰기 (86% 감소)

셀 조회: 캐시 히트율 80% 가정 = 40회/초 DB 읽기
총: 110회/초 DB I/O (78% 감소)
```

## 성능 병목 지점

### 1. DB 연결 풀 고갈
- 현재: 각 작업마다 연결 획득/해제
- 문제: 동시 요청 시 연결 풀 고갈
- 해결: 연결 풀 공유 + 배치 처리

### 2. 트랜잭션 오버헤드
- 현재: 각 업데이트마다 트랜잭션
- 문제: 트랜잭션 시작/커밋 오버헤드
- 해결: 배치 트랜잭션

### 3. 네트워크 지연
- 현재: 각 I/O마다 네트워크 왕복
- 문제: 지연 시간 누적
- 해결: 배치 처리로 왕복 횟수 감소

## 개선 우선순위

### P0 (즉시)
1. **메모리 캐시 레이어 추가**
   - 활성 셀 캐시
   - 엔티티 상태 캐시

2. **체크포인트 시스템 구현**
   - 배치 업데이트
   - 주기적 체크포인트

### P1 (단기)
3. **Lazy Loading 구현**
   - 플레이어 근처 셀만 상세 처리
   - 외부 셀은 체크포인트만

4. **이벤트 매니저 구현**
   - 이벤트 큐 관리
   - 체크포인트 이벤트 처리

### P2 (중기)
5. **기존 코드 리팩토링**
   - EntityManager 메모리 기반으로 변경
   - CellManager 캐시 기반으로 변경

6. **모니터링 및 최적화**
   - 성능 메트릭 수집
   - 캐시 히트율 모니터링

