# 성능 최적화 구현 로드맵

## 작성일
2026-01-01

## Phase 1: 메모리 캐시 레이어 (1-2주)

### 1.1 InMemoryGameState 구현

**파일**: `app/core/in_memory_game_state.py`

```python
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio

@dataclass
class EntityState:
    entity_id: str
    stats: Dict
    position: Dict
    last_updated: datetime

@dataclass
class CellState:
    cell_id: str
    entities: Dict[str, EntityState]
    objects: List[Dict]
    last_accessed: datetime

class InMemoryGameState:
    """메모리 기반 게임 상태 관리"""
    
    def __init__(self, max_active_cells: int = 9):
        self.active_cells: Dict[str, CellState] = {}
        self.entity_cache: Dict[str, EntityState] = {}
        self.max_active_cells = max_active_cells
        self.checkpoint_queue: List[StateUpdate] = []
    
    async def get_cell_state(self, cell_id: str) -> Optional[CellState]:
        """셀 상태 조회 (캐시 우선)"""
        if cell_id in self.active_cells:
            self.active_cells[cell_id].last_accessed = datetime.now()
            return self.active_cells[cell_id]
        return None
    
    async def update_entity_state(self, entity_id: str, state: EntityState):
        """엔티티 상태 업데이트 (메모리)"""
        self.entity_cache[entity_id] = state
        
        # 체크포인트 대기열에 추가
        self.checkpoint_queue.append(
            StateUpdate(entity_id=entity_id, state=state)
        )
    
    async def evict_old_cells(self):
        """오래된 셀 제거 (LRU)"""
        if len(self.active_cells) <= self.max_active_cells:
            return
        
        # 가장 오래된 셀 제거
        oldest = min(
            self.active_cells.items(),
            key=lambda x: x[1].last_accessed
        )
        await self._checkpoint_cell(oldest[0])
        del self.active_cells[oldest[0]]
```

### 1.2 캐시 정책 구현

**파일**: `app/core/cache_policy.py`

```python
from enum import Enum
from typing import Dict
from datetime import datetime, timedelta

class CachePolicy(Enum):
    LRU = "lru"  # Least Recently Used
    TTL = "ttl"  # Time To Live
    SIZE = "size"  # Size-based

class CacheManager:
    """캐시 관리자"""
    
    def __init__(self, policy: CachePolicy = CachePolicy.LRU):
        self.policy = policy
        self.max_size = 1000
        self.ttl_seconds = 300  # 5분
    
    def should_evict(self, item: Dict, cache_size: int) -> bool:
        """캐시 제거 여부 판단"""
        if self.policy == CachePolicy.SIZE:
            return cache_size > self.max_size
        elif self.policy == CachePolicy.TTL:
            age = datetime.now() - item.get('created_at', datetime.now())
            return age.total_seconds() > self.ttl_seconds
        return False
```

## Phase 2: 체크포인트 시스템 (2-3주)

### 2.1 CheckpointManager 구현

**파일**: `app/core/checkpoint_manager.py`

```python
import asyncio
from typing import List
from datetime import datetime
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)

class CheckpointManager:
    """체크포인트 관리자"""
    
    def __init__(self, db_connection, interval: float = 5.0, batch_size: int = 100):
        self.db = db_connection
        self.interval = interval  # 체크포인트 간격 (초)
        self.batch_size = batch_size
        self.update_queue: List[StateUpdate] = []
        self._running = False
    
    async def start(self):
        """체크포인트 백그라운드 태스크 시작"""
        self._running = True
        asyncio.create_task(self._checkpoint_loop())
    
    async def _checkpoint_loop(self):
        """체크포인트 루프"""
        while self._running:
            await asyncio.sleep(self.interval)
            if self.update_queue:
                await self.execute_checkpoint()
    
    async def schedule_update(self, update: StateUpdate):
        """업데이트 스케줄링"""
        self.update_queue.append(update)
        
        # 큐가 가득 차면 즉시 체크포인트
        if len(self.update_queue) >= self.batch_size * 10:
            await self.execute_checkpoint()
    
    async def execute_checkpoint(self):
        """체크포인트 실행 (배치 DB 쓰기)"""
        if not self.update_queue:
            return
        
        start_time = datetime.now()
        updates = self.update_queue[:self.batch_size * 10]  # 최대 1000개
        self.update_queue = self.update_queue[len(updates):]
        
        logger.info(f"[CHECKPOINT] 시작: {len(updates)}개 업데이트")
        
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                async with conn.transaction():
                    # 배치 업데이트
                    with tqdm(total=len(updates), desc="Checkpoint DB Write") as pbar:
                        for i in range(0, len(updates), self.batch_size):
                            batch = updates[i:i+self.batch_size]
                            await self._batch_update(conn, batch)
                            pbar.update(len(batch))
            
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"[CHECKPOINT] 완료: {len(updates)}개 업데이트, {elapsed:.2f}초")
        
        except Exception as e:
            logger.error(f"[CHECKPOINT] 실패: {str(e)}")
            # 실패한 업데이트를 큐 앞에 다시 추가
            self.update_queue = updates + self.update_queue
    
    async def _batch_update(self, conn, updates: List[StateUpdate]):
        """배치 업데이트 실행"""
        await conn.executemany("""
            UPDATE runtime_data.entity_states
            SET current_stats = $1::jsonb,
                current_position = $2::jsonb,
                updated_at = NOW()
            WHERE runtime_entity_id = $3
        """, [
            (update.state.stats, update.state.position, update.entity_id)
            for update in updates
        ])
```

## Phase 3: Lazy Loading 구현 (2-3주)

### 3.1 CellStateManager 구현

**파일**: `app/managers/cell_state_manager.py`

```python
from typing import Dict, Set, Optional
from app.core.in_memory_game_state import InMemoryGameState
from app.core.checkpoint_manager import CheckpointManager

class CellStateManager:
    """셀 상태 관리자 (Lazy Loading)"""
    
    def __init__(self, db_connection, memory_state: InMemoryGameState):
        self.db = db_connection
        self.memory_state = memory_state
        self.active_radius = 2  # 플레이어 주변 2셀
        self.active_cells: Set[str] = set()
    
    async def get_cell_state(self, cell_id: str, player_nearby: bool = False):
        """셀 상태 조회 (Lazy Loading)"""
        if player_nearby:
            # 플레이어 근처: 메모리에서 조회 또는 DB에서 로드
            cell_state = await self.memory_state.get_cell_state(cell_id)
            if cell_state is None:
                cell_state = await self._load_cell_from_db(cell_id)
                await self.memory_state.add_cell(cell_id, cell_state)
            return cell_state
        else:
            # 외부 셀: 체크포인트 데이터만 조회
            return await self._get_checkpoint_state(cell_id)
    
    async def update_player_position(self, player_id: str, cell_id: str):
        """플레이어 위치 업데이트 (활성 셀 범위 재계산)"""
        # 활성 셀 범위 계산
        nearby_cells = await self._get_nearby_cells(cell_id, self.active_radius)
        
        # 활성 셀 업데이트
        old_active = self.active_cells
        self.active_cells = nearby_cells
        
        # 새로 활성화된 셀 로드
        for cell_id in self.active_cells - old_active:
            await self._load_cell_from_db(cell_id)
        
        # 비활성화된 셀 체크포인트
        for cell_id in old_active - self.active_cells:
            await self._checkpoint_cell(cell_id)
    
    async def _get_checkpoint_state(self, cell_id: str):
        """체크포인트 상태 조회 (최적화된 쿼리)"""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # 마지막 체크포인트 이후 변경사항만 조회
            return await conn.fetchrow("""
                SELECT 
                    cell_id,
                    last_checkpoint_time,
                    entity_count,
                    checkpoint_data
                FROM runtime_data.cell_checkpoints
                WHERE cell_id = $1
                ORDER BY last_checkpoint_time DESC
                LIMIT 1
            """, cell_id)
```

## Phase 4: 이벤트 매니저 구현 (3-4주)

### 4.1 EventManager 구현

**파일**: `app/managers/event_manager.py`

```python
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class EventType(Enum):
    ENTITY_MOVE = "entity_move"
    ENTITY_ACTION = "entity_action"
    CELL_STATE_CHANGE = "cell_state_change"
    WORLD_EVENT = "world_event"

@dataclass
class GameEvent:
    event_type: EventType
    cell_id: str
    entity_id: Optional[str]
    data: Dict
    timestamp: datetime

class EventManager:
    """이벤트 관리자"""
    
    def __init__(self, cell_state_manager: CellStateManager):
        self.cell_state_manager = cell_state_manager
        self.event_queue: List[GameEvent] = []
        self.checkpoint_events: Dict[str, List[GameEvent]] = {}
    
    async def schedule_event(self, event: GameEvent):
        """이벤트 스케줄링"""
        # 플레이어 근처 셀: 즉시 처리
        if event.cell_id in self.cell_state_manager.active_cells:
            await self._process_event_immediately(event)
        else:
            # 외부 셀: 체크포인트 대기열에 추가
            if event.cell_id not in self.checkpoint_events:
                self.checkpoint_events[event.cell_id] = []
            self.checkpoint_events[event.cell_id].append(event)
    
    async def process_checkpoint_events(self, cell_id: str):
        """체크포인트 이벤트 처리 (플레이어가 셀 근처로 이동 시)"""
        if cell_id not in self.checkpoint_events:
            return
        
        events = self.checkpoint_events[cell_id]
        self.checkpoint_events[cell_id] = []
        
        logger.info(f"[EVENT] 체크포인트 이벤트 처리: {cell_id}, {len(events)}개 이벤트")
        
        # 배치 처리
        with tqdm(total=len(events), desc=f"Processing events for {cell_id}") as pbar:
            for event in events:
                await self._process_event(event)
                pbar.update(1)
        
        # 체크포인트 저장
        await self._save_checkpoint(cell_id, events)
    
    async def _process_event_immediately(self, event: GameEvent):
        """이벤트 즉시 처리 (플레이어 근처)"""
        if event.event_type == EventType.ENTITY_MOVE:
            await self._handle_entity_move(event)
        elif event.event_type == EventType.ENTITY_ACTION:
            await self._handle_entity_action(event)
        # ...
```

## Phase 5: 기존 코드 리팩토링 (4-6주)

### 5.1 EntityManager 리팩토링

**변경 전**:
```python
async def update_entity_state(self, entity_id, new_state):
    # 즉시 DB 쓰기
    await conn.execute("UPDATE ...", ...)
```

**변경 후**:
```python
async def update_entity_state(self, entity_id, new_state):
    # 메모리 업데이트
    await self.memory_state.update_entity_state(entity_id, new_state)
    
    # 체크포인트 스케줄링
    await self.checkpoint_manager.schedule_update(
        StateUpdate(entity_id=entity_id, state=new_state)
    )
```

### 5.2 CellManager 리팩토링

**변경 전**:
```python
async def get_cell_contents(self, cell_id):
    # 매번 DB 쿼리
    return await conn.fetch("SELECT ...", cell_id)
```

**변경 후**:
```python
async def get_cell_contents(self, cell_id, player_nearby: bool = False):
    # 캐시 우선 조회
    cell_state = await self.cell_state_manager.get_cell_state(
        cell_id, player_nearby
    )
    if cell_state:
        return cell_state
    
    # 캐시 미스 시 DB 조회
    return await self._load_from_db(cell_id)
```

## 테스트 전략

### 1. 성능 테스트

```python
import time
from tqdm import tqdm

async def test_performance():
    """성능 테스트"""
    # 현재 방식
    start = time.time()
    for i in tqdm(range(1000), desc="Current (DB I/O)"):
        await entity_manager.update_entity_state(...)
    current_time = time.time() - start
    
    # 최적화 후
    start = time.time()
    for i in tqdm(range(1000), desc="Optimized (Memory)"):
        await memory_state.update_entity_state(...)
    await checkpoint_manager.execute_checkpoint()
    optimized_time = time.time() - start
    
    print(f"개선율: {(current_time - optimized_time) / current_time * 100:.1f}%")
```

### 2. 부하 테스트

```python
async def test_load():
    """부하 테스트"""
    # 1000개 엔티티 동시 업데이트
    tasks = [
        entity_manager.update_entity_state(f"entity_{i}", state)
        for i in range(1000)
    ]
    
    with tqdm(total=1000, desc="Load Test") as pbar:
        await asyncio.gather(*tasks)
        pbar.update(1000)
```

## 모니터링 및 로깅

### 1. 성능 메트릭 수집

```python
class PerformanceMonitor:
    """성능 모니터"""
    
    def __init__(self):
        self.metrics = {
            'db_io_count': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'checkpoint_count': 0,
            'checkpoint_duration': []
        }
    
    def record_db_io(self):
        self.metrics['db_io_count'] += 1
    
    def record_cache_hit(self):
        self.metrics['cache_hits'] += 1
    
    def record_cache_miss(self):
        self.metrics['cache_misses'] += 1
    
    def get_cache_hit_rate(self) -> float:
        total = self.metrics['cache_hits'] + self.metrics['cache_misses']
        if total == 0:
            return 0.0
        return self.metrics['cache_hits'] / total * 100
```

### 2. 상세 로깅

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
        logger.debug(f"[CHECKPOINT] 큐 상태: {len(self.update_queue)}개 대기 중")
        
        try:
            with tqdm(total=update_count, desc="Checkpoint DB Write", 
                     bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]') as pbar:
                # 배치 처리
                await self._batch_update_db(self.update_queue)
                pbar.update(update_count)
            
            elapsed = time.time() - start_time
            throughput = update_count / elapsed if elapsed > 0 else 0
            
            logger.info(f"[CHECKPOINT] 완료: {update_count}개 업데이트, {elapsed:.2f}초, {throughput:.1f}개/초")
            logger.debug(f"[CHECKPOINT] 메모리 사용: {self._get_memory_usage()}MB")
        
        except Exception as e:
            logger.error(f"[CHECKPOINT] 실패: {str(e)}", exc_info=True)
```

## 예상 성능 개선

### Before (현재)
- DB I/O: 500회/초
- 응답 시간: 100-200ms
- 동시 접속자: 10-20명
- 메모리 사용: 낮음
- CPU 사용: 높음 (DB I/O)

### After (최적화 후)
- DB I/O: 70-110회/초 (78-86% 감소)
- 응답 시간: 10-50ms (50-75% 개선)
- 동시 접속자: 100-200명 (10배 증가)
- 메모리 사용: 중간 (캐시)
- CPU 사용: 낮음 (배치 처리)

## 구현 우선순위

### 즉시 시작 (P0)
1. ✅ InMemoryGameState 기본 구조
2. ✅ CheckpointManager 기본 구조
3. ✅ 성능 모니터링 도구

### 단기 (P1, 1-2개월)
4. ✅ CellStateManager 구현
5. ✅ Lazy Loading 적용
6. ✅ EntityManager 리팩토링

### 중기 (P2, 3-6개월)
7. ✅ EventManager 구현
8. ✅ 전체 시스템 리팩토링
9. ✅ 부하 테스트 및 최적화

## 결론

현재 시스템은 **모든 처리를 DB I/O로 수행**하여 오픈월드 게임에 부적합합니다.

**근본적인 해결책**을 단계적으로 적용하여:
- ✅ **성능**: 50-75% 개선
- ✅ **확장성**: 10배 이상 증가
- ✅ **효율성**: 78-86% I/O 감소

를 달성할 수 있습니다.

