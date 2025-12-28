"""
Entity Behavior Schedule Service 테스트
"""
import pytest
import pytest_asyncio
from database.connection import DatabaseConnection
from app.world_editor.services.behavior_schedule_service import BehaviorScheduleService
from app.world_editor.schemas import EntityBehaviorScheduleCreate, EntityBehaviorScheduleUpdate


@pytest_asyncio.fixture
async def db_connection():
    """데이터베이스 연결 픽스처"""
    db = DatabaseConnection()
    await db.initialize()
    yield db
    await db.close()


@pytest_asyncio.fixture
async def behavior_schedule_service(db_connection):
    """Behavior Schedule Service 픽스처"""
    return BehaviorScheduleService(db_connection)


@pytest_asyncio.fixture
async def test_entity(db_connection):
    """테스트용 Entity 생성"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        entity_id = "TEST_ENTITY_BEHAVIOR_001"
        await conn.execute("""
            INSERT INTO game_data.entities
            (entity_id, entity_type, entity_name, base_stats, default_equipment, 
             default_abilities, default_inventory, entity_properties)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (entity_id) DO NOTHING
        """, entity_id, "npc", "Test NPC", "{}", "{}", "{}", "{}", "{}")
        yield entity_id
        # 정리
        await conn.execute("""
            DELETE FROM game_data.entity_behavior_schedules WHERE entity_id = $1
        """, entity_id)
        await conn.execute("""
            DELETE FROM game_data.entities WHERE entity_id = $1
        """, entity_id)


@pytest.mark.asyncio
async def test_create_behavior_schedule(behavior_schedule_service, test_entity):
    """행동 스케줄 생성 테스트"""
    schedule_data = EntityBehaviorScheduleCreate(
        entity_id=test_entity,
        time_period="morning",
        action_type="work",
        action_priority=1,
        conditions={"min_energy": 20, "weather": "clear"},
        action_data={"duration": 2, "location": "shop"}
    )
    
    schedule = await behavior_schedule_service.create_schedule(schedule_data)
    
    assert schedule is not None
    assert schedule.entity_id == test_entity
    assert schedule.time_period == "morning"
    assert schedule.action_type == "work"
    assert schedule.action_priority == 1
    assert schedule.conditions["min_energy"] == 20
    assert schedule.action_data["duration"] == 2


@pytest.mark.asyncio
async def test_get_schedules_by_entity(behavior_schedule_service, test_entity):
    """엔티티별 행동 스케줄 조회 테스트"""
    # 여러 스케줄 생성
    schedule1 = EntityBehaviorScheduleCreate(
        entity_id=test_entity,
        time_period="morning",
        action_type="work",
        action_priority=1,
        conditions={},
        action_data={}
    )
    schedule2 = EntityBehaviorScheduleCreate(
        entity_id=test_entity,
        time_period="afternoon",
        action_type="rest",
        action_priority=2,
        conditions={},
        action_data={}
    )
    
    await behavior_schedule_service.create_schedule(schedule1)
    await behavior_schedule_service.create_schedule(schedule2)
    
    schedules = await behavior_schedule_service.get_schedules_by_entity(test_entity)
    
    assert len(schedules) >= 2
    assert all(s.entity_id == test_entity for s in schedules)


@pytest.mark.asyncio
async def test_update_behavior_schedule(behavior_schedule_service, test_entity):
    """행동 스케줄 업데이트 테스트"""
    # 스케줄 생성
    schedule_data = EntityBehaviorScheduleCreate(
        entity_id=test_entity,
        time_period="morning",
        action_type="work",
        action_priority=1,
        conditions={},
        action_data={}
    )
    created = await behavior_schedule_service.create_schedule(schedule_data)
    
    # 업데이트
    update_data = EntityBehaviorScheduleUpdate(
        time_period="afternoon",
        action_priority=5,
        conditions={"min_energy": 30}
    )
    updated = await behavior_schedule_service.update_schedule(created.schedule_id, update_data)
    
    assert updated is not None
    assert updated.time_period == "afternoon"
    assert updated.action_priority == 5
    assert updated.conditions["min_energy"] == 30
    # 변경되지 않은 필드는 유지
    assert updated.action_type == "work"


@pytest.mark.asyncio
async def test_delete_behavior_schedule(behavior_schedule_service, test_entity):
    """행동 스케줄 삭제 테스트"""
    # 스케줄 생성
    schedule_data = EntityBehaviorScheduleCreate(
        entity_id=test_entity,
        time_period="morning",
        action_type="work",
        action_priority=1,
        conditions={},
        action_data={}
    )
    created = await behavior_schedule_service.create_schedule(schedule_data)
    
    # 삭제
    success = await behavior_schedule_service.delete_schedule(created.schedule_id)
    assert success is True
    
    # 삭제 확인
    deleted = await behavior_schedule_service.get_schedule(created.schedule_id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_schedule_not_found(behavior_schedule_service):
    """존재하지 않는 스케줄 조회 테스트"""
    import uuid
    # UUID 형식의 존재하지 않는 ID 사용
    non_existent_id = str(uuid.uuid4())
    schedule = await behavior_schedule_service.get_schedule(non_existent_id)
    assert schedule is None

