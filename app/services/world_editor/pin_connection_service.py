"""
핀 연결 서비스 - 핀과 게임 데이터 연결 비즈니스 로직
"""
from typing import Optional
from database.connection import DatabaseConnection
from app.services.world_editor.region_service import RegionService
from app.services.world_editor.location_service import LocationService
from app.services.world_editor.cell_service import CellService
from app.services.world_editor.pin_service import PinService
from app.api.schemas import (
    RegionCreate, LocationCreate, CellCreate, PinPositionCreate
)
from common.utils.logger import get_logger

logger = get_logger(__name__)


class PinConnectionService:
    """핀 연결 서비스 - 핀과 게임 데이터를 연결하는 비즈니스 로직"""
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        self.db = db_connection or DatabaseConnection()
        self.region_service = RegionService(self.db)
        self.location_service = LocationService(self.db)
        self.cell_service = CellService(self.db)
        self.pin_service = PinService(self.db)
    
    async def connect_pin_to_region(
        self,
        pin_id: str,
        region_id: str,
        create_if_not_exists: bool = False,
        region_name: Optional[str] = None
    ) -> dict:
        """
        핀을 Region에 연결
        
        Args:
            pin_id: 핀 ID
            region_id: 연결할 Region ID
            create_if_not_exists: Region이 없으면 생성할지 여부
            region_name: Region 생성 시 이름 (create_if_not_exists=True일 때)
        
        Returns:
            연결 결과 정보
        """
        try:
            # 핀 조회
            pin = await self.pin_service.get_pin(pin_id)
            if not pin:
                raise ValueError(f"핀을 찾을 수 없습니다: {pin_id}")
            
            # Region 조회
            region = await self.region_service.get_region(region_id)
            
            # Region이 없고 생성 옵션이 활성화된 경우
            if not region and create_if_not_exists:
                if not region_name:
                    raise ValueError("Region 이름이 필요합니다.")
                
                region = await self.region_service.create_region(RegionCreate(
                    region_id=region_id,
                    region_name=region_name,
                    region_description="",
                    region_type="",
                    region_properties={}
                ))
                logger.info(f"Region 생성됨: {region_id}")
            
            if not region:
                raise ValueError(f"Region을 찾을 수 없습니다: {region_id}")
            
            # 핀의 game_data_id가 region_id와 다른 경우, 새 핀 생성
            if pin.game_data_id != region_id:
                # 기존 핀 정보로 새 핀 생성
                new_pin = await self.pin_service.create_pin(PinPositionCreate(
                    game_data_id=region_id,
                    pin_type='region',
                    x=pin.x,
                    y=pin.y,
                    icon_type=pin.icon_type,
                    color=pin.color,
                    size=pin.size
                ))
                
                # 기존 핀 삭제
                await self.pin_service.delete_pin(pin_id)
                
                return {
                    "success": True,
                    "message": "핀이 Region에 연결되었습니다.",
                    "new_pin_id": new_pin.pin_id,
                    "old_pin_id": pin_id
                }
            else:
                return {
                    "success": True,
                    "message": "핀이 이미 Region에 연결되어 있습니다.",
                    "pin_id": pin_id
                }
                
        except Exception as e:
            logger.error(f"핀-Region 연결 실패: {e}")
            raise
    
    async def connect_pin_to_location(
        self,
        pin_id: str,
        location_id: str,
        create_if_not_exists: bool = False,
        location_name: Optional[str] = None,
        region_id: Optional[str] = None
    ) -> dict:
        """
        핀을 Location에 연결
        
        Args:
            pin_id: 핀 ID
            location_id: 연결할 Location ID
            create_if_not_exists: Location이 없으면 생성할지 여부
            location_name: Location 생성 시 이름
            region_id: Location 생성 시 상위 Region ID (필수)
        
        Returns:
            연결 결과 정보
        """
        try:
            # 핀 조회
            pin = await self.pin_service.get_pin(pin_id)
            if not pin:
                raise ValueError(f"핀을 찾을 수 없습니다: {pin_id}")
            
            # Location 조회
            location = await self.location_service.get_location(location_id)
            
            # Location이 없고 생성 옵션이 활성화된 경우
            if not location and create_if_not_exists:
                if not location_name:
                    raise ValueError("Location 이름이 필요합니다.")
                if not region_id:
                    raise ValueError("상위 Region ID가 필요합니다.")
                
                location = await self.location_service.create_location(LocationCreate(
                    location_id=location_id,
                    region_id=region_id,
                    location_name=location_name,
                    location_description="",
                    location_type="",
                    location_properties={}
                ))
                logger.info(f"Location 생성됨: {location_id}")
            
            if not location:
                raise ValueError(f"Location을 찾을 수 없습니다: {location_id}")
            
            # 핀의 game_data_id가 location_id와 다른 경우, 새 핀 생성
            if pin.game_data_id != location_id:
                new_pin = await self.pin_service.create_pin(PinPositionCreate(
                    game_data_id=location_id,
                    pin_type='location',
                    x=pin.x,
                    y=pin.y,
                    icon_type=pin.icon_type,
                    color=pin.color,
                    size=pin.size
                ))
                
                await self.pin_service.delete_pin(pin_id)
                
                return {
                    "success": True,
                    "message": "핀이 Location에 연결되었습니다.",
                    "new_pin_id": new_pin.pin_id,
                    "old_pin_id": pin_id
                }
            else:
                return {
                    "success": True,
                    "message": "핀이 이미 Location에 연결되어 있습니다.",
                    "pin_id": pin_id
                }
                
        except Exception as e:
            logger.error(f"핀-Location 연결 실패: {e}")
            raise
    
    async def connect_pin_to_cell(
        self,
        pin_id: str,
        cell_id: str,
        create_if_not_exists: bool = False,
        cell_name: Optional[str] = None,
        location_id: Optional[str] = None
    ) -> dict:
        """
        핀을 Cell에 연결
        
        Args:
            pin_id: 핀 ID
            cell_id: 연결할 Cell ID
            create_if_not_exists: Cell이 없으면 생성할지 여부
            cell_name: Cell 생성 시 이름
            location_id: Cell 생성 시 상위 Location ID (필수)
        
        Returns:
            연결 결과 정보
        """
        try:
            # 핀 조회
            pin = await self.pin_service.get_pin(pin_id)
            if not pin:
                raise ValueError(f"핀을 찾을 수 없습니다: {pin_id}")
            
            # Cell 조회
            cell = await self.cell_service.get_cell(cell_id)
            
            # Cell이 없고 생성 옵션이 활성화된 경우
            if not cell and create_if_not_exists:
                if not cell_name:
                    raise ValueError("Cell 이름이 필요합니다.")
                if not location_id:
                    raise ValueError("상위 Location ID가 필요합니다.")
                
                cell = await self.cell_service.create_cell(CellCreate(
                    cell_id=cell_id,
                    location_id=location_id,
                    cell_name=cell_name,
                    matrix_width=10,
                    matrix_height=10,
                    cell_description="",
                    cell_properties={}
                ))
                logger.info(f"Cell 생성됨: {cell_id}")
            
            if not cell:
                raise ValueError(f"Cell을 찾을 수 없습니다: {cell_id}")
            
            # 핀의 game_data_id가 cell_id와 다른 경우, 새 핀 생성
            if pin.game_data_id != cell_id:
                new_pin = await self.pin_service.create_pin(PinPositionCreate(
                    game_data_id=cell_id,
                    pin_type='cell',
                    x=pin.x,
                    y=pin.y,
                    icon_type=pin.icon_type,
                    color=pin.color,
                    size=pin.size
                ))
                
                await self.pin_service.delete_pin(pin_id)
                
                return {
                    "success": True,
                    "message": "핀이 Cell에 연결되었습니다.",
                    "new_pin_id": new_pin.pin_id,
                    "old_pin_id": pin_id
                }
            else:
                return {
                    "success": True,
                    "message": "핀이 이미 Cell에 연결되어 있습니다.",
                    "pin_id": pin_id
                }
                
        except Exception as e:
            logger.error(f"핀-Cell 연결 실패: {e}")
            raise

