# 데이터 처리 효율 최적화 전략

## 작성일
2026-01-01

## 현재 문제점 분석

### 1. DB I/O 중심 처리의 문제

#### 현재 아키텍처
```
모든 게임 이벤트 → 즉시 DB I/O
- 플레이어 이동 → 즉시 UPDATE entity_states
- NPC 행동 → 즉시 UPDATE entity_states
- 셀 상태 변경 → 즉시 UPDATE runtime_cells
- 모든 셀의 모든 엔티티가 실시간으로 DB에 쓰기
```

#### 문제점
1. **오픈월드 게임의 비현실적 부하**
   - 모든 셀의 모든 엔티티가 실시간 I/O
   - 플레이어가 보지 않는 셀도 계속 업데이트
   - 서버 리소스 낭비

2. **확장성 문제**
   - 엔티티 수 증가 시 DB 부하 급증
   - 동시 접속자 증가 시 연결 풀 고갈
   - 쿼리 성능 저하

3. **성능 병목**
   - 모든 작업이 동기 DB I/O
   - 네트워크 지연 누적
   - 트랜잭션 오버헤드

### 2. 현재 코드의 문제 패턴

#### EntityManager
```python
# app/managers/entity_manager.py
async def update_entity_state(self, entity_id, new_state):
    # 즉시 DB UPDATE
    await conn.execute("""
        UPDATE runtime_data.entity_states
        SET current_stats = $1, ...
        WHERE runtime_entity_id = $2
    """, new_state, entity_id)
```

**문제**: 모든 상태 변경이 즉시 DB에 반영

#### CellManager
```python
# app/managers/cell_manager.py
async def get_cell_contents(self, cell_id):
    # 매번 DB 쿼리
    entities = await conn.fetch("""
        SELECT * FROM runtime_data.entity_states
        WHERE current_position->>'runtime_cell_id' = $1
    """, cell_id)
```

**문제**: 캐시 없이 매번 DB 조회

### 3. 부하 관리 부재

#### 현재 상태
- **캐싱**: 없음
- **배치 처리**: 없음
- **Lazy Loading**: 없음
- **체크포인트**: 없음
- **이벤트 매니저**: 미구현

## 제안된 해결책

### 1. Lazy Loading 정책

#### 원칙
- **플레이어가 있는 셀**: 상세 처리 (실시간)
- **외부 셀**: Lazy Loading (필요 시 로드)

#### 구현 전략
```python
class CellStateManager:
    """셀 상태 관리자 (메모리 기반)"""
    
    def __init__(self):
        self._active_cells: Dict[str, CellState] = {}  # 활성 셀 (메모리)
        self._checkpoint_queue: List[CellUpdate] = []  # 체크포인트 대기열
    
    async def get_cell_state(self, cell_id: str, player_nearby: bool = False):
        """셀 상태 조회 (Lazy Loading)"""
        if player_nearby:
            # 플레이어 근처: 메모리에서 즉시 반환 또는 DB에서 로드
            if cell_id not in self._active_cells:
                await self._load_cell_from_db(cell_id)
            return self._active_cells[cell_id]
        else:
            # 외부 셀: 체크포인트 데이터만 조회
            return await self._get_checkpoint_state(cell_id)
```

### 2. 메모리/캐시 기반 처리

#### 아키텍처
```
┌─────────────────────────────────────┐
│   Game Session (메모리)            │
│   - Active Cells (캐시)             │
│   - Entity States (메모리)          │
│   - Event Queue (메모리)            │
└─────────────────────────────────────┘
           │
           │ 체크포인트 (배치)
           ↓
┌─────────────────────────────────────┐
│   Database (영속성)                  │
│   - Checkpoint Data                 │
│   - Historical Data                 │
└─────────────────────────────────────┘
```

#### 구현 예시
```python
class InMemoryGameState:
    """메모리 기반 게임 상태"""
    
    def __init__(self):
        # 활성 셀 (플레이어가 있는 셀)
        self.active_cells: Dict[str, CellState] = {}
        
        # 엔티티 상태 (메모리)
        self.entity_states: Dict[str, EntityState] = {}
        
        # 이벤트 큐 (배치 처리 대기)
        self.event_queue: List[GameEvent] = []
        
        # 체크포인트 대기열
        self.checkpoint_queue: List[StateUpdate] = []
    
    async def update_entity_state(self, entity_id: str, state: EntityState):
        """엔티티 상태 업데이트 (메모리)"""
        self.entity_states[entity_id] = state
        
        # 체크포인트 대기열에 추가 (즉시 DB 쓰기 X)
        self.checkpoint_queue.append(
            StateUpdate(entity_id=entity_id, state=state, timestamp=now())
        )
    
    async def checkpoint(self):
        """체크포인트: 배치로 DB에 저장"""
        if not self.checkpoint_queue:
            return
        
        # 배치 업데이트
        updates = self.checkpoint_queue
        self.checkpoint_queue = []
        
        await self._batch_update_db(updates)
```

### 3. 체크포인트 기반 배치 입력

#### 체크포인트 전략
```python
class CheckpointManager:
    """체크포인트 관리자"""
    
    def __init__(self):
        self.checkpoint_interval = 5.0  # 5초마다 체크포인트
        self.max_queue_size = 1000  # 최대 대기열 크기
    
    async def schedule_checkpoint(self, updates: List[StateUpdate]):
        """체크포인트 스케줄링"""
        # 큐에 추가
        self.update_queue.extend(updates)
        
        # 큐가 가득 차면 즉시 체크포인트
        if len(self.update_queue) >= self.max_queue_size:
            await self.execute_checkpoint()
    
    async def execute_checkpoint(self):
        """체크포인트 실행 (배치 DB 쓰기)"""
        if not self.update_queue:
            return
        
        # 배치 업데이트 (단일 트랜잭션)
        async with db.transaction():
            await db.executemany("""
                UPDATE runtime_data.entity_states
                SET current_stats = $1, current_position = $2, ...
                WHERE runtime_entity_id = $3
            """, [
                (update.state.stats, update.state.position, update.entity_id)
                for update in self.update_queue
            ])
        
        self.update_queue.clear()
```

### 4. 플레이어 근처 셀만 상세 처리

#### 처리 전략
```python
class CellProcessingManager:
    """셀 처리 관리자"""
    
    def __init__(self):
        self.active_radius = 2  # 플레이어 주변 2셀 반경
        self.active_cells: Set[str] = set()
    
    async def update_player_position(self, player_id: str, cell_id: str):
        """플레이어 위치 업데이트"""
        # 활성 셀 범위 계산
        nearby_cells = await self._get_nearby_cells(cell_id, self.active_radius)
        
        # 활성 셀 업데이트
        self.active_cells = nearby_cells
        
        # 활성 셀의 엔티티만 상세 처리
        for cell_id in self.active_cells:
            await self._process_cell_detailed(cell_id)
        
        # 비활성 셀은 체크포인트만
        await self._process_inactive_cells_checkpoint()
    
    async def _process_cell_detailed(self, cell_id: str):
        """셀 상세 처리 (실시간)"""
        # 메모리에서 상태 조회/업데이트
        cell_state = self.memory_cache.get_cell(cell_id)
        
        # 엔티티 행동 처리
        for entity in cell_state.entities:
            await self._process_entity_behavior(entity)
    
    async def _process_inactive_cells_checkpoint(self):
        """비활성 셀 체크포인트 처리"""
        # 외부 셀의 이벤트를 체크포인트로 처리
        # 쿼리 조건으로 준비된 이벤트를 한꺼번에 처리
        await self._process_checkpoint_events()
```

### 5. 이벤트 매니저 기반 처리

#### 이벤트 매니저 아키텍처
```python
class EventManager:
    """이벤트 관리자 (미구현 → 구현 필요)"""
    
    def __init__(self):
        self.event_queue: List[GameEvent] = []
        self.checkpoint_events: Dict[str, List[Event]] = {}  # 셀별 체크포인트 이벤트
    
    async def schedule_event(self, event: GameEvent, cell_id: str):
        """이벤트 스케줄링"""
        # 플레이어 근처 셀: 즉시 처리
        if cell_id in self.active_cells:
            await self._process_event_immediately(event)
        else:
            # 외부 셀: 체크포인트 대기열에 추가
            if cell_id not in self.checkpoint_events:
                self.checkpoint_events[cell_id] = []
            self.checkpoint_events[cell_id].append(event)
    
    async def process_checkpoint_events(self, cell_id: str):
        """체크포인트 이벤트 처리 (플레이어가 셀 근처로 이동 시)"""
        if cell_id not in self.checkpoint_events:
            return
        
        # 준비된 이벤트를 한꺼번에 처리
        events = self.checkpoint_events[cell_id]
        self.checkpoint_events[cell_id] = []
        
        # 배치 처리
        await self._batch_process_events(events)
        
        # DB에 체크포인트 저장
        await self._save_checkpoint(cell_id, events)
```

## 구현 계획

### Phase 1: 메모리 캐시 레이어 추가

#### 1.1 InMemoryGameState 구현
- [ ] `InMemoryGameState` 클래스 생성
- [ ] 활성 셀 캐시 구현
- [ ] 엔티티 상태 메모리 관리
- [ ] 이벤트 큐 구현

#### 1.2 캐시 정책 정의
- [ ] LRU 캐시 정책
- [ ] 캐시 만료 정책
- [ ] 캐시 크기 제한

### Phase 2: 체크포인트 시스템 구현

#### 2.1 CheckpointManager 구현
- [ ] 체크포인트 스케줄링
- [ ] 배치 업데이트 로직
- [ ] 트랜잭션 최적화

#### 2.2 체크포인트 전략
- [ ] 시간 기반 체크포인트 (5초 간격)
- [ ] 큐 크기 기반 체크포인트 (1000개)
- [ ] 플레이어 이동 시 체크포인트

### Phase 3: Lazy Loading 구현

#### 3.1 CellStateManager 구현
- [ ] 활성 셀 관리
- [ ] Lazy Loading 로직
- [ ] 체크포인트 데이터 조회

#### 3.2 셀 로딩 전략
- [ ] 플레이어 근처 셀: 즉시 로드
- [ ] 외부 셀: 체크포인트만 조회
- [ ] 셀 언로드 정책

### Phase 4: 이벤트 매니저 구현

#### 4.1 EventManager 구현
- [ ] 이벤트 큐 관리
- [ ] 체크포인트 이벤트 관리
- [ ] 배치 이벤트 처리

#### 4.2 이벤트 처리 전략
- [ ] 플레이어 근처: 즉시 처리
- [ ] 외부 셀: 체크포인트 대기
- [ ] 셀 접근 시 배치 처리

### Phase 5: 기존 코드 리팩토링

#### 5.1 EntityManager 리팩토링
- [ ] 메모리 기반 상태 관리로 변경
- [ ] 즉시 DB 쓰기 제거
- [ ] 체크포인트 기반 쓰기로 변경

#### 5.2 CellManager 리팩토링
- [ ] 캐시 기반 조회로 변경
- [ ] Lazy Loading 적용
- [ ] 체크포인트 데이터 조회 지원

## 성능 최적화 전략

### 1. 메모리 사용 최적화

#### 캐시 크기 제한
```python
class InMemoryGameState:
    MAX_ACTIVE_CELLS = 9  # 3x3 그리드 (플레이어 중심)
    MAX_ENTITY_CACHE = 1000  # 최대 엔티티 캐시 수
    
    def _evict_cache(self):
        """캐시 제거 (LRU)"""
        if len(self.active_cells) > self.MAX_ACTIVE_CELLS:
            # 가장 오래된 셀 제거
            oldest_cell = min(self.active_cells.items(), key=lambda x: x[1].last_accessed)
            await self._checkpoint_cell(oldest_cell[0])
            del self.active_cells[oldest_cell[0]]
```

### 2. DB I/O 최적화

#### 배치 업데이트
```python
async def batch_update_entities(self, updates: List[EntityUpdate]):
    """배치 엔티티 업데이트"""
    # 단일 트랜잭션으로 배치 업데이트
    async with db.transaction():
        await db.executemany("""
            UPDATE runtime_data.entity_states
            SET current_stats = $1, current_position = $2, updated_at = NOW()
            WHERE runtime_entity_id = $3
        """, [
            (u.stats, u.position, u.entity_id) for u in updates
        ])
```

#### 인덱스 최적화
```sql
-- 체크포인트 조회를 위한 인덱스
CREATE INDEX idx_entity_states_checkpoint 
ON runtime_data.entity_states(updated_at) 
WHERE updated_at < NOW() - INTERVAL '1 minute';

-- 활성 셀 조회를 위한 인덱스
CREATE INDEX idx_cell_occupants_active 
ON runtime_data.cell_occupants(runtime_cell_id, entered_at);
```

### 3. 쿼리 최적화

#### 체크포인트 데이터 조회
```python
async def get_checkpoint_state(self, cell_id: str):
    """체크포인트 상태 조회 (최적화된 쿼리)"""
    # 마지막 체크포인트 이후 변경사항만 조회
    checkpoint_time = await self._get_last_checkpoint_time(cell_id)
    
    return await conn.fetch("""
        SELECT 
            runtime_entity_id,
            current_stats,
            current_position
        FROM runtime_data.entity_states
        WHERE current_position->>'runtime_cell_id' = $1
          AND updated_at > $2
        ORDER BY updated_at DESC
        LIMIT 100
    """, cell_id, checkpoint_time)
```

## 테스트 및 모니터링

### 1. 성능 메트릭

#### 모니터링 항목
- DB I/O 횟수 (초당)
- 메모리 사용량
- 캐시 히트율
- 체크포인트 지연 시간
- 이벤트 처리 시간

### 2. 로깅 개선

#### tqdm을 사용한 진행 상황 표시
```python
from tqdm import tqdm

async def process_checkpoint_batch(self, updates: List[StateUpdate]):
    """체크포인트 배치 처리 (진행 상황 표시)"""
    with tqdm(total=len(updates), desc="Checkpoint") as pbar:
        batch_size = 100
        for i in range(0, len(updates), batch_size):
            batch = updates[i:i+batch_size]
            await self._process_batch(batch)
            pbar.update(len(batch))
```

#### 상세 로깅
```python
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)

class CheckpointManager:
    async def execute_checkpoint(self):
        """체크포인트 실행 (상세 로깅)"""
        start_time = time.time()
        update_count = len(self.update_queue)
        
        logger.info(f"[CHECKPOINT] 시작: {update_count}개 업데이트")
        
        with tqdm(total=update_count, desc="Checkpoint DB Write") as pbar:
            # 배치 처리
            await self._batch_update_db(self.update_queue)
            pbar.update(update_count)
        
        elapsed = time.time() - start_time
        logger.info(f"[CHECKPOINT] 완료: {update_count}개 업데이트, {elapsed:.2f}초")
```

## 마이그레이션 전략

### 1. 점진적 적용

#### Step 1: 메모리 캐시 레이어 추가 (기존 코드 유지)
- InMemoryGameState 구현
- 기존 코드와 병행 운영
- 캐시 히트율 모니터링

#### Step 2: 선택적 적용
- 플레이어 이동만 메모리 기반으로 변경
- 나머지는 기존 방식 유지
- 성능 비교

#### Step 3: 전체 적용
- 모든 엔티티 업데이트를 메모리 기반으로 변경
- 체크포인트 시스템 활성화
- 기존 즉시 쓰기 코드 제거

### 2. 롤백 계획

- 기존 코드 백업
- 기능 플래그로 전환 가능
- 성능 저하 시 즉시 롤백

## 예상 효과

### 성능 개선
- **DB I/O 감소**: 90% 이상 감소 예상
- **응답 시간**: 50% 이상 개선 예상
- **동시 접속자**: 10배 이상 증가 가능

### 리소스 사용
- **메모리**: 증가 (캐시 사용)
- **CPU**: 감소 (DB I/O 감소)
- **네트워크**: 감소 (배치 처리)

## 결론

현재 시스템은 **모든 처리를 DB I/O로 수행**하여 오픈월드 게임에 부적합합니다.

**근본적인 해결책**:
1. ✅ **Lazy Loading**: 플레이어 근처 셀만 상세 처리
2. ✅ **메모리/캐시 기반 처리**: 즉시 DB 쓰기 제거
3. ✅ **체크포인트 배치 입력**: 주기적 배치 저장
4. ✅ **이벤트 매니저**: 외부 이벤트를 체크포인트로 관리

이를 통해 **확장 가능하고 효율적인 오픈월드 게임 시스템**을 구축할 수 있습니다.

