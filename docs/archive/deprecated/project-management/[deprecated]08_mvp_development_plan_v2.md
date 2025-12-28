# [deprecated] MVP 개발 목표 (버전 2)

> **Deprecated 날짜**: 2025-12-28  
> **Deprecated 이유**: MVP v2 개발이 완료되어 더 이상 진행 중인 작업이 아님. 현재는 Phase 4+ 개발이 진행 중이며, MVP v2의 핵심 기능들은 모두 구현되었음.  
> **계획 수립일**: 2025-10-18  
> **기반**: 데이터베이스 연결 성공 확인  
> **목표**: 실제 작동하는 게임 시스템 구현  
> **핵심**: DB 연동 기반 실제 게임 플로우 완성

## 🎯 **MVP v2 핵심 목표**

### **1. 실제 작동하는 게임 시스템**
- **데이터베이스 연동**: PostgreSQL과 완전 연동된 게임 시스템
- **실제 플레이 가능**: 플레이어가 실제로 게임을 플레이할 수 있는 상태
- **데이터 영속성**: 게임 상태가 실제로 데이터베이스에 저장/로드
- **엔티티 자동 행동**: NPC들이 실제로 시간에 따라 행동

### **2. "Story Engine" 철학 구현**
- **플레이가 곧 세계의 작성 행위**: 플레이어의 행동이 실제로 세계를 변화시킴
- **지속적인 세계**: 플레이어 없이도 세계가 계속 발전
- **데이터 중심 설계**: 모든 게임 상태가 데이터베이스에 반영

### **3. MVP 수용 기준 달성**
- **100회 연속 무오류 플레이**: 자동화된 테스트로 시스템 안정성 검증
- **DevMode 승격**: 생성한 NPC가 다음 세션에서 템플릿으로 노출
- **룰 기반 플레이**: LLM 없이도 완전한 게임 플레이 가능

## 🏗️ **기술적 기반 현황**

### **✅ 완성된 기반 (80%)**
1. **데이터베이스 아키텍처**: 3-tier 스키마 완벽 구현
2. **Manager 시스템**: EntityManager, CellManager, ActionHandler, DialogueManager
3. **데이터베이스 연결**: PostgreSQL 연결 성공 확인
4. **UI 구조**: 계기판 UI 컴포넌트 완성
5. **코딩 컨벤션**: 안전성 지침 및 품질 가이드 완성

### **❌ 해결 필요한 문제 (20%)**
1. **이벤트 루프 충돌**: pytest-asyncio와 DB 연결 풀 충돌
2. **게임 플로우 불완성**: 실제 플레이어 생성 및 게임 시작 로직 부재
3. **통합 테스트 부족**: 전체 시스템 동작 검증 부족

## 📋 **MVP v2 개발 계획**

### **Phase 1: 이벤트 루프 문제 해결 (1일)**

#### **1.1 pytest-asyncio 설정 최적화**
```python
# pytest.ini
[tool:pytest]
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function

# conftest.py
import pytest
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    """세션 스코프 이벤트 루프 생성"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
```

#### **1.2 데이터베이스 연결 풀 생명주기 관리**
```python
# database/connection.py
class DatabaseConnection:
    def __init__(self):
        self._pool = None
        self._pool_lock = asyncio.Lock()
    
    async def get_pool(self):
        """지연 초기화된 연결 풀 반환"""
        if self._pool is None:
            async with self._pool_lock:
                if self._pool is None:
                    self._pool = await self._create_pool()
        return self._pool
    
    async def close_pool(self):
        """연결 풀 종료"""
        if self._pool:
            await self._pool.close()
            self._pool = None
```

#### **1.3 테스트 환경 격리**
```python
# tests/conftest.py
@pytest.fixture(scope="function")
async def db_connection():
    """테스트용 데이터베이스 연결"""
    db = DatabaseConnection()
    await db.initialize()
    yield db
    await db.close_pool()
```

### **Phase 2: 게임 플로우 완성 (1일)**

#### **2.1 GameManager 실제 구현**
```python
# app/core/game_manager.py
class GameManager:
    async def start_new_game(self, player_template_id: str, start_cell_id: str) -> str:
        """실제 게임 시작"""
        # 1. 플레이어 엔티티 생성
        player_entity = await self.entity_manager.create_entity(
            name="Player",
            entity_type=EntityType.PLAYER,
            properties={"level": 1, "gold": 100},
            is_runtime=True
        )
        
        # 2. 게임 세션 생성
        session_id = await self.runtime_data_repo.create_game_session(
            player_id=player_entity.entity_id,
            current_cell_id=start_cell_id
        )
        
        # 3. 플레이어를 시작 셀에 배치
        await self.cell_manager.enter_cell(start_cell_id, player_entity.entity_id)
        
        return session_id
```

#### **2.2 UI 연동 완성**
```python
# app/ui/dashboard.py
class MainWindow:
    async def start_new_game(self):
        """새 게임 시작 버튼"""
        try:
            session_id = await self.game_manager.start_new_game(
                "player_template_001", 
                "CELL_VILLAGE_CENTER_001"
            )
            self.current_session_id = session_id
            self.update_ui_state()
            self.log_message("새 게임이 시작되었습니다!")
        except Exception as e:
            self.log_error(f"게임 시작 실패: {str(e)}")
```

#### **2.3 행동 시스템 연동**
```python
# app/ui/dashboard.py
async def handle_investigate(self):
    """조사 버튼"""
    result = await self.action_handler.handle_action(
        self.current_player_id,
        ActionType.INVESTIGATE,
        self.current_cell_id
    )
    self.log_message(result.message)

async def handle_dialogue(self, npc_id: str):
    """대화 버튼"""
    result = await self.dialogue_manager.start_dialogue(
        self.current_player_id,
        npc_id
    )
    self.log_message(result.npc_response)
```

### **Phase 3: 가상 마을 시뮬레이션 구현 (1일)**

#### **3.1 엔티티 자동 행동 시스템**
```python
# app/simulation/entity_behavior.py
class EntityBehavior:
    async def execute_daily_routine(self):
        """하루 일과 실행"""
        for hour in range(24):
            time_period = self.get_time_period(hour)
            actions = self.get_actions_for_time_period(time_period)
            
            for action in actions:
                await self.execute_action(action)
                await asyncio.sleep(0.1)  # 행동 간 대기
```

#### **3.2 시간 시스템 구현**
```python
# app/simulation/time_system.py
class TimeSystem:
    async def run_simulation(self, days: int):
        """시뮬레이션 실행"""
        for day in range(1, days + 1):
            for hour in range(24):
                await self.tick_hour()
                await self.process_entity_actions()
                await asyncio.sleep(0.01)  # 시뮬레이션 속도 조절
```

#### **3.3 마을 시뮬레이션 통합**
```python
# app/simulation/village_simulation.py
class VillageSimulation:
    async def run_100_day_simulation(self):
        """100일 시뮬레이션 실행"""
        await self.initialize_village()
        await self.time_system.run_simulation(days=100)
        await self.analyze_results()
```

### **Phase 4: Dev Mode 구현 (1일)**

#### **4.1 Runtime → Game Data 승격**
```python
# app/core/dev_mode.py
class DevModeManager:
    async def promote_entity_to_game_data(self, entity_id: str) -> bool:
        """런타임 엔티티를 게임 데이터로 승격"""
        # 1. 런타임 엔티티 조회
        runtime_entity = await self.entity_manager.get_entity(entity_id, is_runtime=True)
        
        # 2. 게임 데이터로 변환
        game_entity = self._convert_to_game_data(runtime_entity)
        
        # 3. 게임 데이터 저장
        await self.game_data_repo.create_entity(game_entity)
        
        # 4. 참조 레이어 업데이트
        await self.reference_layer_repo.create_entity_reference(
            entity_id, game_entity.entity_id
        )
        
        return True
```

#### **4.2 Dev Mode UI**
```python
# app/ui/dev_mode.py
class DevModeWindow:
    async def promote_entity(self, entity_id: str):
        """엔티티 승격 버튼"""
        result = await self.dev_mode_manager.promote_entity_to_game_data(entity_id)
        if result:
            self.log_message(f"엔티티 {entity_id}가 게임 데이터로 승격되었습니다!")
```

### **Phase 5: 통합 테스트 및 최적화 (1일)**

#### **5.1 자동화된 테스트**
```python
# tests/integration/test_full_game_flow.py
async def test_100_consecutive_plays():
    """100회 연속 플레이 테스트"""
    for i in range(100):
        # 1. 새 게임 시작
        session_id = await game_manager.start_new_game("player_template_001", "CELL_VILLAGE_CENTER_001")
        
        # 2. 플레이어 행동
        await action_handler.handle_action(player_id, ActionType.INVESTIGATE, cell_id)
        await dialogue_manager.start_dialogue(player_id, npc_id)
        
        # 3. 게임 저장
        await game_manager.save_game(session_id)
        
        # 4. 게임 로드
        await game_manager.load_game(session_id)
        
        assert session_id is not None
```

#### **5.2 성능 최적화**
```python
# database/connection.py
class DatabaseConnection:
    async def _create_pool(self):
        """최적화된 연결 풀 생성"""
        return await asyncpg.create_pool(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            min_size=5,
            max_size=20,
            command_timeout=30,
            server_settings={
                'jit': 'off'  # 성능 최적화
            }
        )
```

## 📅 **상세 일정표**

### **Day 1 (2025-10-19): 이벤트 루프 문제 해결**
- **오전**: pytest-asyncio 설정 최적화
- **오후**: 데이터베이스 연결 풀 생명주기 관리

### **Day 2 (2025-10-20): 게임 플로우 완성**
- **오전**: GameManager 실제 구현
- **오후**: UI 연동 및 행동 시스템 연동

### **Day 3 (2025-10-21): 가상 마을 시뮬레이션**
- **오전**: 엔티티 자동 행동 시스템
- **오후**: 시간 시스템 및 마을 시뮬레이션 통합

### **Day 4 (2025-10-22): Dev Mode 구현**
- **오전**: Runtime → Game Data 승격
- **오후**: Dev Mode UI 및 데이터 검증

### **Day 5 (2025-10-23): 통합 테스트 및 최적화**
- **오전**: 자동화된 테스트 및 100회 연속 플레이
- **오후**: 성능 최적화 및 최종 버그 수정

## 🎯 **MVP v2 수용 기준**

### **기술적 수용 기준**
- ✅ **데이터베이스 연결**: PostgreSQL과 완전 연동
- ✅ **게임 플로우**: 실제 플레이어가 게임을 플레이할 수 있음
- ✅ **데이터 영속성**: 게임 상태가 데이터베이스에 저장/로드
- ✅ **엔티티 자동 행동**: NPC들이 시간에 따라 자동 행동

### **기능적 수용 기준**
- ✅ **100회 연속 무오류 플레이**: 자동화된 테스트 통과
- ✅ **DevMode 승격**: 생성한 NPC가 다음 세션에서 템플릿으로 노출
- ✅ **룰 기반 플레이**: LLM 없이도 완전한 게임 플레이 가능
- ✅ **가상 마을 시뮬레이션**: 5명의 NPC가 24시간 자동 행동

### **사용자 경험 수용 기준**
- ✅ **직관적 UI**: 계기판 스타일의 명확한 인터페이스
- ✅ **실시간 피드백**: 모든 행동에 대한 즉시 반응
- ✅ **데이터 투명성**: 게임 상태가 데이터베이스에 명확히 반영
- ✅ **개발자 친화적**: Dev Mode를 통한 실시간 세계 편집

## 🚀 **즉시 시작할 작업**

### **1. 이벤트 루프 문제 해결 (2시간)**
```python
# pytest.ini 생성
[tool:pytest]
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function

# conftest.py 생성
import pytest
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
```

### **2. GameManager 실제 구현 (3시간)**
```python
# app/core/game_manager.py 수정
async def start_new_game(self, player_template_id: str, start_cell_id: str) -> str:
    # 실제 플레이어 엔티티 생성
    # 게임 세션 생성
    # 시작 셀 배치
```

### **3. UI 연동 완성 (2시간)**
```python
# app/ui/dashboard.py 수정
async def start_new_game(self):
    # 실제 게임 시작 로직
    # UI 상태 업데이트
    # 행동 버튼 연동
```

**예상 완성 시점**: 2025-10-23 (5일 후)  
**현재 완성도**: 80% → **목표 완성도**: 100%  
**핵심 차이점**: 실제 작동하는 게임 시스템 구현
