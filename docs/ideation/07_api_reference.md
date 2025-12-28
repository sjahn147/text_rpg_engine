# [deprecated] RPG Engine API 레퍼런스

> **Deprecated 날짜**: 2025-12-28  
> **Deprecated 사유**: API 레퍼런스 내용이 구현 완료되었으며, 실제 API 구조와 다릅니다. 현재는 World Editor FastAPI 기반 REST API가 주로 사용되며, 실제 API는 코드베이스를 참조해야 합니다.

> **최신화 날짜**: 2025-12-28  
> **문서 버전**: v1.1  
> **작성일**: 2025-10-18  
> **최종 수정**: 2025-12-28  
> **현재 상태**: 모든 Manager 클래스 API 구현 완료, World Editor API 80% 완료

## 📚 **API 개요**

RPG Engine의 모든 API는 비동기 기반으로 설계되었으며, PostgreSQL 데이터베이스와 연동됩니다.

### **핵심 철학**
이 API는 단순한 게임 엔진이 아니라 **"서사 기반 세계의 시뮬레이션 구조체"**를 위한 인터페이스입니다.

- **트랜잭션 기반 서사**: 모든 상호작용이 DB 트랜잭션으로 기록됨
- **세계 적재 시스템**: 접근하면 세계가 동적으로 적재됨
- **AI 기반 해석**: LLM이 상황을 해석하고 서사를 생성
- **지속적 세계**: 플레이어가 없어도 세계는 계속 작동
- **Effect Carrier 시스템**: 통일 인터페이스로 모든 효과 관리
- **EventBus 시스템**: 비동기 이벤트 처리 및 백그라운드 세계 진행

### **기본 설정**
```python
import asyncio
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
```

---

## 🗄️ **데이터베이스 연결 API**

### **DatabaseConnection**

#### **연결 생성**
```python
db = DatabaseConnection()
pool = await db.pool
```

#### **연결 사용**
```python
async with pool.acquire() as conn:
    async with conn.transaction():
        # 데이터베이스 작업
        pass
```

#### **연결 종료**
```python
await db.close()
```

---

## 🎮 **게임 데이터 API**

### **GameDataRepository**

#### **엔티티 조회**
```python
# 엔티티 ID로 조회
entity = await game_data.get_entity("PLAYER_001")

# 엔티티 타입으로 조회
entities = await game_data.get_entities_by_type("npc")

# 모든 엔티티 조회
all_entities = await game_data.get_all_entities()
```

#### **월드 데이터 조회**
```python
# 지역 조회
regions = await game_data.get_regions()

# 장소 조회
locations = await game_data.get_locations_by_region("REG_NORTH_001")

# 셀 조회
cells = await game_data.get_cells_by_location("LOC_VILLAGE_001")
```

#### **대화 데이터 조회**
```python
# 대화 컨텍스트 조회
context = await game_data.get_dialogue_context("MERCHANT_GREETING")

# 대화 주제 조회
topics = await game_data.get_dialogue_topics("MERCHANT_GREETING")

# 지식 베이스 조회
knowledge = await game_data.get_dialogue_knowledge("WEAPONS_001")
```

---

## 🎯 **런타임 데이터 API**

### **RuntimeDataRepository**

#### **세션 관리**
```python
# 세션 생성
session_id = await runtime_data.create_session({
    "player_name": "TestPlayer",
    "difficulty": "normal"
})

# 세션 조회
session = await runtime_data.get_session(session_id)

# 세션 상태 업데이트
await runtime_data.update_session_state(session_id, "active")

# 세션 종료
await runtime_data.close_session(session_id)
```

#### **엔티티 상태 관리**
```python
# 엔티티 상태 조회
state = await runtime_data.get_entity_state(runtime_entity_id)

# 엔티티 상태 업데이트
await runtime_data.update_entity_state(runtime_entity_id, {
    "current_stats": {"hp": 80, "mp": 40},
    "current_position": {"x": 60, "y": 60}
})

# 엔티티 이동
await runtime_data.move_entity(runtime_entity_id, new_cell_id)
```

#### **대화 상태 관리**
```python
# 대화 상태 조회
dialogue_state = await runtime_data.get_dialogue_state(session_id, npc_entity_id)

# 대화 상태 업데이트
await runtime_data.update_dialogue_state(session_id, npc_entity_id, {
    "current_topic": "greeting",
    "emotion": "friendly"
})

# 대화 기록 추가
await runtime_data.add_dialogue_history(session_id, npc_entity_id, {
    "speaker": "npc",
    "message": "안녕하세요!",
    "context": "greeting"
})
```

---

## 🔗 **참조 레이어 API**

### **ReferenceLayerRepository**

#### **엔티티 참조 관리**
```python
# 엔티티 참조 생성
runtime_entity_id = await reference_layer.create_entity_reference(
    game_entity_id="PLAYER_001",
    session_id=session_id,
    entity_type="player",
    is_player=True
)

# 엔티티 참조 조회
entity_ref = await reference_layer.get_entity_reference(runtime_entity_id)

# 세션의 모든 엔티티 조회
entities = await reference_layer.get_session_entities(session_id)
```

#### **셀 참조 관리**
```python
# 셀 참조 생성
runtime_cell_id = await reference_layer.create_cell_reference(
    game_cell_id="CELL_VILLAGE_CENTER_001",
    session_id=session_id
)

# 셀 참조 조회
cell_ref = await reference_layer.get_cell_reference(runtime_cell_id)

# 세션의 모든 셀 조회
cells = await reference_layer.get_session_cells(session_id)
```

---

## 🏭 **팩토리 API**

### **GameDataFactory**

#### **엔티티 생성**
```python
# 플레이어 엔티티 생성
player_entity = await game_data_factory.create_player_entity({
    "name": "TestPlayer",
    "class": "warrior",
    "level": 1,
    "stats": {"hp": 100, "mp": 50}
})

# NPC 엔티티 생성
npc_entity = await game_data_factory.create_npc_entity({
    "name": "상인 토마스",
    "type": "merchant",
    "dialogue_context": "MERCHANT_GREETING"
})
```

#### **월드 데이터 생성**
```python
# 지역 생성
region = await game_data_factory.create_region({
    "name": "북부 숲",
    "type": "forest",
    "properties": {"climate": "temperate"}
})

# 장소 생성
location = await game_data_factory.create_location({
    "name": "숲속 마을",
    "region_id": region["region_id"],
    "type": "village"
})

# 셀 생성
cell = await game_data_factory.create_cell({
    "name": "마을 광장",
    "location_id": location["location_id"],
    "size": {"width": 100, "height": 100}
})
```

### **InstanceFactory**

#### **런타임 인스턴스 생성**
```python
# 플레이어 인스턴스 생성
player_instance = await instance_factory.create_player_instance(
    game_entity_id="PLAYER_001",
    session_id=session_id,
    initial_cell_id="CELL_VILLAGE_CENTER_001"
)

# NPC 인스턴스 생성
npc_instance = await instance_factory.create_npc_instance(
    game_entity_id="NPC_001",
    session_id=session_id,
    cell_id="CELL_VILLAGE_CENTER_001"
)
```

---

## ⚡ **Effect Carrier API**

### **Effect Carrier 관리**
```python
from app.entity.effect_carrier import EffectCarrierManager

# Effect Carrier 생성
effect = await EffectCarrierManager.create_effect(
    name="Fireball",
    carrier_type="skill",
    effect_json={
        "damage": 50,
        "range": 3,
        "cooldown": 5
    },
    constraints_json={
        "mana_cost": 10,
        "level_required": 5
    }
)

# 엔티티에 Effect Carrier 부여
await EffectCarrierManager.grant_effect(
    session_id=session_id,
    entity_id=entity_id,
    effect_id=effect.effect_id,
    source="quest_reward"
)

# 엔티티의 Effect Carrier 조회
effects = await EffectCarrierManager.get_entity_effects(
    session_id=session_id,
    entity_id=entity_id
)

# Effect Carrier 적용
result = await EffectCarrierManager.apply_effect(
    session_id=session_id,
    entity_id=entity_id,
    effect_id=effect.effect_id,
    target_id=target_id
)
```

### **Effect Carrier 타입**
- **skill**: 스킬 (Fireball, Heal, etc.)
- **buff**: 버프 (Strength Boost, Speed, etc.)
- **item**: 아이템 (Sword, Potion, etc.)
- **blessing**: 축복 (Divine Protection, etc.)
- **curse**: 저주 (Weakness, etc.)
- **ritual**: 의식 (Summoning, etc.)

---

## 🛠️ **Dev Mode API**

### **개발자 모드 기능**
```python
from app.ui.dev_mode import DevModeManager

# Dev Mode 활성화
dev_mode = await DevModeManager.activate(session_id=session_id)

# Game Data 편집
region = await dev_mode.create_region(
    region_name="New Forest",
    region_type="forest",
    properties={"danger_level": 3}
)

# Runtime → Game Data Promote
promoted = await dev_mode.promote_to_game_data(
    runtime_id=runtime_id,
    target_table="entities",
    reason="Player created NPC"
)

# 미리보기 생성
preview = await dev_mode.generate_preview(
    content_type="dialogue",
    context={"npc_personality": "friendly"},
    constraints={"max_length": 200}
)

# 버전/감사 로그
audit_log = await dev_mode.get_audit_log(
    entity_id=entity_id,
    limit=10
)
```

### **권한 관리**
```python
# RBAC 권한 확인
can_edit = await dev_mode.check_permission(
    user_id=user_id,
    action="edit",
    resource="game_data"
)

# 승격 권한 확인
can_promote = await dev_mode.check_promote_permission(
    user_id=user_id,
    target_table="entities"
)
```

---

## 🌍 **World Tick API**

### **세계 틱 시스템**
```python
from app.world.world_tick import WorldTickManager

# World Tick 실행
tick_result = await WorldTickManager.execute_tick(
    session_id=session_id,
    tick_interval=3600  # 1시간
)

# 백그라운드 이벤트 스케줄링
await WorldTickManager.schedule_event(
    event_type="political_change",
    trigger_time=datetime.now() + timedelta(hours=2),
    parameters={"faction": "northern_kingdom"}
)

# 비가시 이벤트 로그 조회
invisible_events = await WorldTickManager.get_invisible_events(
    session_id=session_id,
    since=last_check_time
)

# 오프라인 진행 처리
catchup_result = await WorldTickManager.process_offline_progress(
    session_id=session_id,
    last_activity=last_activity_time
)
```

### **이벤트 타입**
- **political_change**: 정치적 변화
- **disaster**: 재난
- **relationship_change**: 관계 변화
- **economic_shift**: 경제 변화
- **seasonal_event**: 계절 이벤트

---

## 🚌 **EventBus API**

### **이벤트 발행/구독**
```python
from app.core.event_bus import EventBus

# 이벤트 발행
await EventBus.emit(
    event_type="cell_entered",
    data={
        "cell_id": cell_id,
        "entity_id": entity_id,
        "timestamp": datetime.now()
    }
)

# 이벤트 구독
@EventBus.subscribe("entity_spawned")
async def handle_entity_spawned(data):
    # 엔티티 생성 처리
    pass

# 예약 이벤트
await EventBus.schedule_event(
    event_type="world_tick",
    trigger_time=datetime.now() + timedelta(minutes=30),
    data={"tick_type": "economic"}
)
```

### **세션 락 API**
```python
from app.core.session_lock import SessionLockManager

# 세션 락 획득
async with SessionLockManager.acquire(session_id):
    # 락이 걸린 상태에서 작업
    await process_game_action(session_id, action)

# 낙관적 버전 확인
version_conflict = await SessionLockManager.check_version(
    session_id=session_id,
    entity_id=entity_id,
    expected_version=current_version
)
```

---

## 💾 **캐시 관리 API**

### **캐시 시스템**
```python
from app.core.cache import CacheManager

# 셀 컨텐츠 캐시
await CacheManager.set_cell_content(
    cell_id=cell_id,
    content=cell_data,
    ttl=3600
)

cached_content = await CacheManager.get_cell_content(cell_id)

# LLM 응답 캐시
cache_key = CacheManager.generate_cache_key(
    context_hash=context_hash,
    prompt_hash=prompt_hash
)

cached_response = await CacheManager.get_llm_response(cache_key)
if not cached_response:
    response = await llm.generate(prompt)
    await CacheManager.set_llm_response(cache_key, response)

# 이미지 캐시
image_path = await CacheManager.get_cached_image(
    seed=image_seed,
    style=image_style
)
```

---

## 🤖 **LLM/RAG API**

### **LLM 통합**
```python
from app.core.llm import LLMManager

# 컨텍스트 패키지 생성
context = await LLMManager.build_context_package(
    session_id=session_id,
    cell_id=cell_id,
    entities=entities,
    active_events=events
)

# LLM 호출 (비용 통제)
response = await LLMManager.generate_response(
    context=context,
    prompt_type="dialogue",
    constraints={
        "max_tokens": 200,
        "tone": "friendly"
    }
)

# 캐시 확인
cached_response = await LLMManager.get_cached_response(
    context_hash=context.hash()
)
```

### **RAG 시스템**
```python
# 관련 지식 검색
knowledge = await LLMManager.retrieve_knowledge(
    query=player_question,
    context=current_context,
    limit=5
)

# 응답 생성
response = await LLMManager.generate_rag_response(
    question=player_question,
    knowledge=knowledge,
    constraints=constraints
)
```

---

## 🎮 **게임 매니저 API**

### **GameManager**

#### **게임 세션 관리**
```python
# 게임 매니저 초기화
game_manager = GameManager()

# 새 게임 시작
session = await game_manager.start_new_game({
    "player_name": "TestPlayer",
    "difficulty": "normal",
    "starting_cell": "CELL_VILLAGE_CENTER_001"
})

# 게임 저장
await game_manager.save_game(session["session_id"])

# 게임 로드
session = await game_manager.load_game(session_id)

# 게임 종료
await game_manager.end_game(session_id)
```

#### **플레이어 액션 처리**
```python
# 플레이어 이동
await game_manager.move_player(session_id, {"x": 60, "y": 60})

# NPC와 상호작용
dialogue = await game_manager.interact_with_npc(session_id, npc_entity_id)

# 아이템 사용
result = await game_manager.use_item(session_id, item_id)

# 스킬 사용
effect = await game_manager.use_skill(session_id, skill_id, target_id)
```

---

## 🎭 **시나리오 API**

### **ScenarioLoader**

#### **시나리오 로드**
```python
# 시나리오 파일 로드
scenario = await scenario_loader.load_scenario("basic_interaction_scenario.json")

# 시나리오 검증
is_valid = await scenario_loader.validate_scenario(scenario)

# 시나리오 메타데이터 조회
metadata = await scenario_loader.get_scenario_metadata(scenario)
```

### **ScenarioExecutor**

#### **시나리오 실행**
```python
# 시나리오 실행
executor = ScenarioExecutor(session_id)
await executor.execute_scenario(scenario)

# 시나리오 단계 실행
await executor.execute_step(step_id)

# 시나리오 상태 조회
state = await executor.get_scenario_state()

# 시나리오 중단
await executor.stop_scenario()
```

---

## 🎨 **UI API**

### **MainWindow**

#### **화면 관리**
```python
# 메인 윈도우 생성
main_window = MainWindow()

# 화면 전환
await main_window.show_dialogue_screen(npc_entity_id)
await main_window.show_map_screen()
await main_window.show_inventory_screen()
await main_window.show_status_screen()
```

#### **이벤트 처리**
```python
# 이벤트 핸들러 등록
main_window.on_dialogue_choice.connect(handle_dialogue_choice)
main_window.on_item_use.connect(handle_item_use)
main_window.on_skill_use.connect(handle_skill_use)
```

---

## 🔧 **유틸리티 API**

### **Logger**

#### **로깅**
```python
from common.utils.logger import Logger

logger = Logger("game_module")

# 로그 레벨별 기록
logger.debug("디버그 정보")
logger.info("일반 정보")
logger.warning("경고 메시지")
logger.error("오류 메시지")
logger.critical("심각한 오류")
```

### **Validator**

#### **데이터 검증**
```python
from common.utils.validator import Validator

validator = Validator()

# 엔티티 데이터 검증
is_valid = validator.validate_entity_data(entity_data)

# 게임 상태 검증
is_valid = validator.validate_game_state(game_state)

# 사용자 입력 검증
is_valid = validator.validate_user_input(input_data)
```

---

## 📊 **쿼리 API**

### **복잡한 조회**

#### **게임 상태 조회**
```python
# 세션의 전체 상태 조회
game_state = await runtime_data.get_session_game_state(session_id)

# 셀의 모든 엔티티 조회
cell_entities = await runtime_data.get_cell_entities(cell_id)

# 플레이어 주변 엔티티 조회
nearby_entities = await runtime_data.get_nearby_entities(
    player_entity_id, 
    radius=5
)
```

#### **통계 조회**
```python
# 플레이어 통계
player_stats = await runtime_data.get_player_statistics(player_entity_id)

# 세션 통계
session_stats = await runtime_data.get_session_statistics(session_id)

# 게임 전체 통계
game_stats = await runtime_data.get_game_statistics()
```

---

## 🚨 **에러 처리**

### **예외 타입**

#### **데이터베이스 에러**
```python
from database.exceptions import DatabaseError, ConnectionError, QueryError

try:
    result = await database.query(sql)
except ConnectionError as e:
    logger.error(f"데이터베이스 연결 오류: {e}")
except QueryError as e:
    logger.error(f"쿼리 실행 오류: {e}")
except DatabaseError as e:
    logger.error(f"데이터베이스 오류: {e}")
```

#### **게임 로직 에러**
```python
from app.exceptions import GameLogicError, ValidationError, StateError

try:
    await game_manager.move_player(session_id, position)
except ValidationError as e:
    logger.error(f"입력 검증 오류: {e}")
except StateError as e:
    logger.error(f"게임 상태 오류: {e}")
except GameLogicError as e:
    logger.error(f"게임 로직 오류: {e}")
```

---

## 📈 **성능 모니터링**

### **성능 측정**
```python
import time
from functools import wraps

def measure_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        
        logger.info(f"{func.__name__} 실행 시간: {end_time - start_time:.3f}초")
        return result
    return wrapper

@measure_performance
async def expensive_operation():
    # 비용이 큰 작업
    pass
```

### **메모리 사용량 모니터링**
```python
import psutil
import os

def log_memory_usage():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    logger.info(f"메모리 사용량: {memory_info.rss / 1024 / 1024:.2f} MB")
    logger.info(f"가상 메모리: {memory_info.vms / 1024 / 1024:.2f} MB")
```

---

## 📚 **참고 자료**

### **Python 비동기 프로그래밍**
- **asyncio 문서**: https://docs.python.org/3/library/asyncio.html
- **asyncpg 문서**: https://magicstack.github.io/asyncpg/
- **PyQt5 문서**: https://doc.qt.io/qtforpython/

### **데이터베이스 설계**
- **PostgreSQL 문서**: https://www.postgresql.org/docs/
- **SQL 최적화**: https://use-the-index-luke.com/
- **데이터베이스 패턴**: https://martinfowler.com/

### **게임 개발**
- **게임 아키텍처**: https://www.gamasutra.com/
- **RPG 디자인**: https://www.rpgdesign.net/
- **사용자 경험**: https://uxdesign.cc/

---

**문서 작성자**: RPG Engine Development Team  
**최종 검토**: 2025-10-18  
**다음 검토 예정**: 2025-11-18
