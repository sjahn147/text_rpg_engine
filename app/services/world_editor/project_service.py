"""
프로젝트 관리 서비스
"""
from typing import Dict, Any, List
from database.connection import DatabaseConnection
from app.services.world_editor.region_service import RegionService
from app.services.world_editor.location_service import LocationService
from app.services.world_editor.cell_service import CellService
from app.services.world_editor.entity_service import EntityService
from app.services.world_editor.world_object_service import WorldObjectService
from app.services.world_editor.effect_carrier_service import EffectCarrierService
from app.services.world_editor.item_service import ItemService
from app.services.world_editor.pin_service import PinService
from app.services.world_editor.road_service import RoadService
from app.services.world_editor.map_service import MapService
from app.api.schemas import (
    RegionCreate, LocationCreate, CellCreate, EntityCreate,
    WorldObjectCreate, EffectCarrierCreate, ItemCreate,
    PinPositionCreate, RoadCreate
)
from common.utils.logger import logger


class ProjectService:
    """프로젝트 저장/로드 서비스"""
    
    def __init__(self, db_connection=None):
        self.db = db_connection or DatabaseConnection()
        self.region_service = RegionService(self.db)
        self.location_service = LocationService(self.db)
        self.cell_service = CellService(self.db)
        self.entity_service = EntityService(self.db)
        self.world_object_service = WorldObjectService(self.db)
        self.effect_carrier_service = EffectCarrierService(self.db)
        self.item_service = ItemService(self.db)
        self.pin_service = PinService(self.db)
        self.road_service = RoadService(self.db)
        self.map_service = MapService(self.db)
    
    async def export_project(self) -> Dict[str, Any]:
        """전체 프로젝트 데이터 내보내기"""
        try:
            # 모든 데이터 수집
            regions = await self.region_service.get_all_regions()
            locations = await self.location_service.get_all_locations()
            cells = await self.cell_service.get_all_cells()
            world_objects = await self.world_object_service.get_all_world_objects()
            effect_carriers = await self.effect_carrier_service.get_all_effect_carriers()
            items = await self.item_service.get_all_items()
            pins = await self.pin_service.get_all_pins()
            roads = await self.road_service.get_all_roads()
            map_metadata = await self.map_service.get_map('default_map')
            if not map_metadata:
                map_metadata = None
            
            # 엔티티는 셀별로 가져오기
            entities = []
            for cell in cells:
                try:
                    cell_id = cell.cell_id if hasattr(cell, 'cell_id') else cell['cell_id']
                    cell_entities = await self.entity_service.get_entities_by_cell(cell_id)
                    for e in cell_entities:
                        if hasattr(e, 'dict'):
                            entities.append(e.dict())
                        elif hasattr(e, 'model_dump'):
                            entities.append(e.model_dump())
                        else:
                            entities.append(e)
                except Exception as e:
                    logger.warning(f"셀 {cell_id if 'cell_id' in locals() else 'unknown'}의 엔티티 조회 실패: {e}")
            
            # Pydantic 모델을 dict로 변환하는 헬퍼 함수
            def to_dict(obj):
                if hasattr(obj, 'dict'):
                    return obj.dict()
                elif hasattr(obj, 'model_dump'):
                    return obj.model_dump()
                elif isinstance(obj, dict):
                    return obj
                else:
                    return obj
            
            return {
                'version': '1.0.0',
                'map_metadata': to_dict(map_metadata),
                'pins': [to_dict(p) for p in pins],
                'roads': [to_dict(r) for r in roads],
                'regions': [to_dict(r) for r in regions],
                'locations': [to_dict(l) for l in locations],
                'cells': [to_dict(c) for c in cells],
                'entities': entities,
                'world_objects': [to_dict(w) for w in world_objects],
                'effect_carriers': [to_dict(e) for e in effect_carriers],
                'items': [to_dict(i) for i in items],
            }
        except Exception as e:
            logger.error(f"프로젝트 내보내기 실패: {e}")
            raise
    
    async def import_project(self, project_data: Dict[str, Any]) -> Dict[str, int]:
        """프로젝트 데이터 가져오기"""
        try:
            stats = {
                'regions': 0,
                'locations': 0,
                'cells': 0,
                'entities': 0,
                'world_objects': 0,
                'effect_carriers': 0,
                'items': 0,
                'pins': 0,
                'roads': 0,
            }
            
            # Regions 가져오기
            if 'regions' in project_data:
                for region_dict in project_data['regions']:
                    try:
                        region_id = region_dict.get('region_id')
                        if not region_id:
                            continue
                        # 기존 데이터 확인 후 업데이트 또는 생성
                        existing = await self.region_service.get_region(region_id)
                        if existing:
                            await self.region_service.update_region(region_id, region_dict)
                        else:
                            region_create = RegionCreate(**region_dict)
                            await self.region_service.create_region(region_create)
                        stats['regions'] += 1
                    except Exception as e:
                        logger.warning(f"지역 가져오기 실패: {e}")
            
            # Locations 가져오기
            if 'locations' in project_data:
                for location_dict in project_data['locations']:
                    try:
                        location_id = location_dict.get('location_id')
                        if not location_id:
                            continue
                        existing = await self.location_service.get_location(location_id)
                        if existing:
                            await self.location_service.update_location(location_id, location_dict)
                        else:
                            location_create = LocationCreate(**location_dict)
                            await self.location_service.create_location(location_create)
                        stats['locations'] += 1
                    except Exception as e:
                        logger.warning(f"위치 가져오기 실패: {e}")
            
            # Cells 가져오기
            if 'cells' in project_data:
                for cell_dict in project_data['cells']:
                    try:
                        cell_id = cell_dict.get('cell_id')
                        if not cell_id:
                            continue
                        existing = await self.cell_service.get_cell(cell_id)
                        if existing:
                            await self.cell_service.update_cell(cell_id, cell_dict)
                        else:
                            cell_create = CellCreate(**cell_dict)
                            await self.cell_service.create_cell(cell_create)
                        stats['cells'] += 1
                    except Exception as e:
                        logger.warning(f"셀 가져오기 실패: {e}")
            
            # Entities 가져오기
            if 'entities' in project_data:
                for entity_dict in project_data['entities']:
                    try:
                        entity_id = entity_dict.get('entity_id')
                        if not entity_id:
                            continue
                        existing = await self.entity_service.get_entity(entity_id)
                        if existing:
                            await self.entity_service.update_entity(entity_id, entity_dict)
                        else:
                            entity_create = EntityCreate(**entity_dict)
                            await self.entity_service.create_entity(entity_create)
                        stats['entities'] += 1
                    except Exception as e:
                        logger.warning(f"엔티티 가져오기 실패: {e}")
            
            # World Objects 가져오기
            if 'world_objects' in project_data:
                for obj_dict in project_data['world_objects']:
                    try:
                        object_id = obj_dict.get('object_id')
                        if not object_id:
                            continue
                        existing = await self.world_object_service.get_world_object(object_id)
                        if existing:
                            await self.world_object_service.update_world_object(object_id, obj_dict)
                        else:
                            obj_create = WorldObjectCreate(**obj_dict)
                            await self.world_object_service.create_world_object(obj_create)
                        stats['world_objects'] += 1
                    except Exception as e:
                        logger.warning(f"월드 오브젝트 가져오기 실패: {e}")
            
            # Pins 가져오기
            if 'pins' in project_data:
                for pin_dict in project_data['pins']:
                    try:
                        pin_id = pin_dict.get('pin_id')
                        if not pin_id:
                            continue
                        existing = await self.pin_service.get_pin(pin_id)
                        if existing:
                            await self.pin_service.update_pin(pin_id, pin_dict)
                        else:
                            pin_create = PinPositionCreate(**pin_dict)
                            await self.pin_service.create_pin(pin_create)
                        stats['pins'] += 1
                    except Exception as e:
                        logger.warning(f"핀 가져오기 실패: {e}")
            
            # Roads 가져오기
            if 'roads' in project_data:
                for road_dict in project_data['roads']:
                    try:
                        road_id = road_dict.get('road_id')
                        if not road_id:
                            continue
                        existing = await self.road_service.get_road(road_id)
                        if existing:
                            await self.road_service.update_road(road_id, road_dict)
                        else:
                            road_create = RoadCreate(**road_dict)
                            await self.road_service.create_road(road_create)
                        stats['roads'] += 1
                    except Exception as e:
                        logger.warning(f"도로 가져오기 실패: {e}")
            
            # Map Metadata 업데이트
            if 'map_metadata' in project_data:
                try:
                    await self.map_service.update_map('default_map', project_data['map_metadata'])
                except Exception as e:
                    logger.warning(f"맵 메타데이터 업데이트 실패: {e}")
            
            return stats
        except Exception as e:
            logger.error(f"프로젝트 가져오기 실패: {e}")
            raise

