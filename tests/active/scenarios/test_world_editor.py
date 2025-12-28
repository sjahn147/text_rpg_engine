"""
월드 에디터 통합 테스트
"""
import pytest
import pytest_asyncio
import uuid
from typing import Dict, Any

from database.connection import DatabaseConnection
from app.services.world_editor.region_service import RegionService
from app.services.world_editor.location_service import LocationService
from app.services.world_editor.cell_service import CellService
from app.services.world_editor.pin_service import PinService
from app.services.world_editor.road_service import RoadService
from app.services.world_editor.map_service import MapService
from app.api.schemas import (
    RegionCreate, LocationCreate, CellCreate,
    PinPositionCreate, RoadCreate, MapMetadataCreate
)
from common.utils.logger import logger


@pytest_asyncio.fixture(scope="function")
async def db_connection():
    """데이터베이스 연결 픽스처"""
    db = DatabaseConnection()
    await db.initialize()
    yield db
    await db.close()


@pytest_asyncio.fixture(scope="function")
async def test_services(db_connection):
    """서비스 픽스처"""
    return {
        'region': RegionService(db_connection),
        'location': LocationService(db_connection),
        'cell': CellService(db_connection),
        'pin': PinService(db_connection),
        'road': RoadService(db_connection),
        'map': MapService(db_connection),
    }


@pytest.mark.asyncio
async def test_map_metadata_operations(test_services):
    """지도 메타데이터 CRUD 테스트"""
    map_service = test_services['map']
    
    # 조회 (기본 지도)
    map_data = await map_service.get_map('default_map')
    assert map_data is not None
    assert map_data.map_id == 'default_map'
    assert map_data.background_image == 'assets/world_editor/worldmap.png'
    
    # 업데이트
    updated = await map_service.update_map('default_map', {
        'zoom_level': 1.5,
        'grid_enabled': True,
        'grid_size': 100,
    })
    assert updated.zoom_level == 1.5
    assert updated.grid_enabled is True
    assert updated.grid_size == 100
    
    logger.info("✓ 지도 메타데이터 테스트 통과")


@pytest.mark.asyncio
async def test_region_operations(test_services):
    """지역 CRUD 테스트"""
    region_service = test_services['region']
    region_id = f"REG_TEST_{uuid.uuid4().hex[:8].upper()}"
    
    # 생성
    region = await region_service.create_region(RegionCreate(
        region_id=region_id,
        region_name="테스트 지역",
        region_description="테스트용 지역입니다",
        region_type="forest",
        region_properties={
            "climate": "temperate",
            "danger_level": 3,
        }
    ))
    assert region.region_id == region_id
    assert region.region_name == "테스트 지역"
    assert region.region_properties["climate"] == "temperate"
    
    # 조회
    retrieved = await region_service.get_region(region_id)
    assert retrieved is not None
    assert retrieved.region_name == "테스트 지역"
    
    # 업데이트
    updated = await region_service.update_region(region_id, {
        "region_name": "업데이트된 지역",
        "region_properties": {
            "climate": "cold",
            "danger_level": 5,
        }
    })
    assert updated.region_name == "업데이트된 지역"
    assert updated.region_properties["climate"] == "cold"
    
    # 삭제
    deleted = await region_service.delete_region(region_id)
    assert deleted is True
    
    # 삭제 확인
    after_delete = await region_service.get_region(region_id)
    assert after_delete is None
    
    logger.info("✓ 지역 CRUD 테스트 통과")


@pytest.mark.asyncio
async def test_location_operations(test_services):
    """위치 CRUD 테스트"""
    region_service = test_services['region']
    location_service = test_services['location']
    
    # 지역 생성
    region_id = f"REG_TEST_{uuid.uuid4().hex[:8].upper()}"
    region = await region_service.create_region(RegionCreate(
        region_id=region_id,
        region_name="테스트 지역",
        region_type="forest"
    ))
    
    # 위치 생성
    location_id = f"LOC_TEST_{uuid.uuid4().hex[:8].upper()}"
    location = await location_service.create_location(LocationCreate(
        location_id=location_id,
        region_id=region_id,
        location_name="테스트 마을",
        location_description="테스트용 마을입니다",
        location_type="village",
        location_properties={
            "background_music": "peaceful_01",
            "ambient_effects": ["birds", "wind"],
        }
    ))
    assert location.location_id == location_id
    assert location.region_id == region_id
    assert location.location_name == "테스트 마을"
    
    # 지역별 위치 조회
    locations = await location_service.get_locations_by_region(region_id)
    assert len(locations) >= 1
    assert any(loc.location_id == location_id for loc in locations)
    
    # 업데이트
    updated = await location_service.update_location(location_id, {
        "location_name": "업데이트된 마을",
    })
    assert updated.location_name == "업데이트된 마을"
    
    # 정리
    await location_service.delete_location(location_id)
    await region_service.delete_region(region_id)
    
    logger.info("✓ 위치 CRUD 테스트 통과")


@pytest.mark.asyncio
async def test_cell_operations(test_services):
    """셀 CRUD 테스트"""
    region_service = test_services['region']
    location_service = test_services['location']
    cell_service = test_services['cell']
    
    # 지역 및 위치 생성
    region_id = f"REG_TEST_{uuid.uuid4().hex[:8].upper()}"
    location_id = f"LOC_TEST_{uuid.uuid4().hex[:8].upper()}"
    
    await region_service.create_region(RegionCreate(
        region_id=region_id,
        region_name="테스트 지역"
    ))
    await location_service.create_location(LocationCreate(
        location_id=location_id,
        region_id=region_id,
        location_name="테스트 위치"
    ))
    
    # 셀 생성
    cell_id = f"CELL_TEST_{uuid.uuid4().hex[:8].upper()}"
    cell = await cell_service.create_cell(CellCreate(
        cell_id=cell_id,
        location_id=location_id,
        cell_name="테스트 셀",
        matrix_width=20,
        matrix_height=20,
        cell_description="테스트용 셀입니다",
        cell_properties={
            "terrain": "grass",
            "walkable": True,
        }
    ))
    assert cell.cell_id == cell_id
    assert cell.matrix_width == 20
    assert cell.matrix_height == 20
    
    # 위치별 셀 조회
    cells = await cell_service.get_cells_by_location(location_id)
    assert len(cells) >= 1
    assert any(c.cell_id == cell_id for c in cells)
    
    # 정리
    await cell_service.delete_cell(cell_id)
    await location_service.delete_location(location_id)
    await region_service.delete_region(region_id)
    
    logger.info("✓ 셀 CRUD 테스트 통과")


@pytest.mark.asyncio
async def test_pin_operations(test_services):
    """핀 CRUD 테스트"""
    region_service = test_services['region']
    pin_service = test_services['pin']
    
    # 지역 생성
    region_id = f"REG_TEST_{uuid.uuid4().hex[:8].upper()}"
    await region_service.create_region(RegionCreate(
        region_id=region_id,
        region_name="테스트 지역"
    ))
    
    # 핀 생성
    pin = await pin_service.create_pin(PinPositionCreate(
        game_data_id=region_id,
        pin_type="region",
        x=500,
        y=300,
        icon_type="city",
        color="#FF6B9D",
        size=12
    ))
    assert pin.game_data_id == region_id
    assert pin.pin_type == "region"
    assert pin.x == 500
    assert pin.y == 300
    assert pin.icon_type == "city"
    
    # 게임 데이터 ID로 핀 조회
    retrieved = await pin_service.get_pin_by_game_data(region_id, "region")
    assert retrieved is not None
    assert retrieved.pin_id == pin.pin_id
    
    # 핀 이동
    updated = await pin_service.update_pin(pin.pin_id, {
        "x": 600,
        "y": 400,
    })
    assert updated.x == 600
    assert updated.y == 400
    
    # 정리
    await pin_service.delete_pin(pin.pin_id)
    await region_service.delete_region(region_id)
    
    logger.info("✓ 핀 CRUD 테스트 통과")


@pytest.mark.asyncio
async def test_road_operations(test_services):
    """도로 CRUD 테스트"""
    region_service = test_services['region']
    pin_service = test_services['pin']
    road_service = test_services['road']
    
    # 두 지역 생성
    region1_id = f"REG_TEST_{uuid.uuid4().hex[:8].upper()}"
    region2_id = f"REG_TEST_{uuid.uuid4().hex[:8].upper()}"
    
    await region_service.create_region(RegionCreate(
        region_id=region1_id,
        region_name="지역 1"
    ))
    await region_service.create_region(RegionCreate(
        region_id=region2_id,
        region_name="지역 2"
    ))
    
    # 두 핀 생성
    pin1 = await pin_service.create_pin(PinPositionCreate(
        game_data_id=region1_id,
        pin_type="region",
        x=100,
        y=100,
    ))
    pin2 = await pin_service.create_pin(PinPositionCreate(
        game_data_id=region2_id,
        pin_type="region",
        x=500,
        y=500,
    ))
    
    # 도로 생성 (핀 ID 기반)
    road = await road_service.create_road(RoadCreate(
        from_pin_id=pin1.pin_id,
        to_pin_id=pin2.pin_id,
        road_type="normal",
        distance=100.5,
        travel_time=120,
        danger_level=3,
        color="#8B4513",
        width=3,
        dashed=False,
        path_coordinates=[
            {"x": 100, "y": 100},
            {"x": 300, "y": 300},
            {"x": 500, "y": 500},
        ]
    ))
    assert road.from_pin_id == pin1.pin_id
    assert road.to_pin_id == pin2.pin_id
    assert road.road_type == "normal"
    assert road.distance == 100.5
    assert road.color == "#8B4513"
    assert road.width == 3
    assert road.dashed is False
    assert len(road.path_coordinates) == 3
    
    # 도로 업데이트
    updated = await road_service.update_road(road.road_id, {
        "danger_level": 5,
        "color": "#FF0000",
        "dashed": True,
    })
    assert updated.danger_level == 5
    assert updated.color == "#FF0000"
    assert updated.dashed is True
    
    # 정리
    await road_service.delete_road(road.road_id)
    await pin_service.delete_pin(pin1.pin_id)
    await pin_service.delete_pin(pin2.pin_id)
    await region_service.delete_region(region1_id)
    await region_service.delete_region(region2_id)
    
    logger.info("✓ 도로 CRUD 테스트 통과")


@pytest.mark.asyncio
async def test_dnd_info_storage(test_services):
    """D&D 스타일 정보 저장 테스트"""
    region_service = test_services['region']
    region_id = f"REG_TEST_{uuid.uuid4().hex[:8].upper()}"
    
    # D&D 정보가 포함된 지역 생성
    dnd_info = {
        "dnd_info": {
            "name": "엘더우드 마을",
            "description": "고대 숲 속에 위치한 평화로운 마을",
            "type": "village",
            "demographics": {
                "population": 5000,
                "races": {
                    "human": 3000,
                    "elf": 1500,
                    "dwarf": 500
                },
                "classes": {
                    "warrior": 1000,
                    "mage": 500,
                    "rogue": 300
                }
            },
            "economy": {
                "primary_industry": "trade",
                "trade_goods": ["spices", "textiles", "metals"],
                "gold_value": 10000
            },
            "government": {
                "type": "monarchy",
                "leader": "King Aldric",
                "laws": ["No theft", "Respect the forest"]
            },
            "culture": {
                "religion": ["Nature worship", "Ancestor veneration"],
                "customs": ["Harvest festival", "Tree planting ceremony"],
                "festivals": ["Spring Equinox", "Autumn Harvest"]
            },
            "lore": {
                "history": "200년 전 설립된 마을로, 고대 숲의 수호자들이 세웠습니다.",
                "legends": ["The Legend of the First King", "The Guardian Tree"],
                "secrets": ["Hidden treasure in the castle", "Secret passage to the forest"]
            }
        }
    }
    
    region = await region_service.create_region(RegionCreate(
        region_id=region_id,
        region_name="엘더우드 마을",
        region_description="고대 숲 속 마을",
        region_properties=dnd_info
    ))
    
    # D&D 정보 검증
    assert region.region_properties is not None
    assert "dnd_info" in region.region_properties
    dnd_data = region.region_properties["dnd_info"]
    assert dnd_data["demographics"]["population"] == 5000
    assert dnd_data["demographics"]["races"]["elf"] == 1500
    assert dnd_data["economy"]["primary_industry"] == "trade"
    assert dnd_data["government"]["type"] == "monarchy"
    assert len(dnd_data["lore"]["legends"]) == 2
    
    # 정리
    await region_service.delete_region(region_id)
    
    logger.info("✓ D&D 정보 저장 테스트 통과")


@pytest.mark.asyncio
async def test_integration_scenario(test_services):
    """통합 시나리오 테스트: 전체 워크플로우"""
    region_service = test_services['region']
    location_service = test_services['location']
    pin_service = test_services['pin']
    road_service = test_services['road']
    
    # 1. 지역 생성
    region1_id = f"REG_SCENARIO_{uuid.uuid4().hex[:8].upper()}"
    region2_id = f"REG_SCENARIO_{uuid.uuid4().hex[:8].upper()}"
    
    region1 = await region_service.create_region(RegionCreate(
        region_id=region1_id,
        region_name="북부 숲",
        region_type="forest"
    ))
    region2 = await region_service.create_region(RegionCreate(
        region_id=region2_id,
        region_name="남부 평원",
        region_type="plains"
    ))
    
    # 2. 핀 생성
    pin1 = await pin_service.create_pin(PinPositionCreate(
        game_data_id=region1_id,
        pin_type="region",
        x=200,
        y=200,
        icon_type="forest",
        color="#FF6B9D"
    ))
    pin2 = await pin_service.create_pin(PinPositionCreate(
        game_data_id=region2_id,
        pin_type="region",
        x=800,
        y=600,
        icon_type="plains",
        color="#FF6B9D"
    ))
    
    # 3. 도로 생성
    road = await road_service.create_road(RoadCreate(
        from_pin_id=pin1.pin_id,
        to_pin_id=pin2.pin_id,
        road_type="normal",
        distance=150.0,
        travel_time=180,
        danger_level=2,
        path_coordinates=[
            {"x": 200, "y": 200},
            {"x": 500, "y": 400},
            {"x": 800, "y": 600},
        ]
    ))
    
    # 4. 검증
    assert road.from_pin_id == pin1.pin_id
    assert road.to_pin_id == pin2.pin_id
    assert road.distance == 150.0
    
    # 5. 모든 도로 조회
    all_roads = await road_service.get_all_roads()
    assert len(all_roads) >= 1
    assert any(r.road_id == road.road_id for r in all_roads)
    
    # 6. 정리
    await road_service.delete_road(road.road_id)
    await pin_service.delete_pin(pin1.pin_id)
    await pin_service.delete_pin(pin2.pin_id)
    await region_service.delete_region(region1_id)
    await region_service.delete_region(region2_id)
    
    logger.info("✓ 통합 시나리오 테스트 통과")

