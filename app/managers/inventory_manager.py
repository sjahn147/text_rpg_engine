"""
인벤토리 관리 매니저
아이템/장비를 엔티티 인벤토리에 추가/제거하는 로직
"""
from typing import Dict, Any, List, Optional
import json
from database.connection import DatabaseConnection
from common.utils.logger import logger


class InventoryManager:
    """인벤토리 관리 클래스"""
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        self.db = db_connection or DatabaseConnection()
    
    async def add_item_to_inventory(
        self,
        runtime_entity_id: str,
        item_id: str,
        quantity: int = 1
    ) -> bool:
        """
        엔티티 인벤토리에 아이템 추가
        
        Args:
            runtime_entity_id: 엔티티 런타임 ID
            item_id: 아이템 템플릿 ID (예: "ITEM_POTION_001")
            quantity: 추가할 수량 (기본값: 1)
        
        Returns:
            성공 여부
        """
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                async with conn.transaction():
                    # 현재 인벤토리 조회
                    entity_state = await conn.fetchrow(
                        """
                        SELECT inventory
                        FROM runtime_data.entity_states
                        WHERE runtime_entity_id = $1
                        """,
                        runtime_entity_id
                    )
                    
                    if not entity_state:
                        raise ValueError(f"Entity state not found: {runtime_entity_id}")
                    
                    # 인벤토리 파싱
                    inventory = json.loads(entity_state['inventory']) if isinstance(entity_state['inventory'], str) else entity_state['inventory']
                    if not inventory:
                        inventory = {"items": [], "quantities": {}}
                    
                    # 아이템 목록에 추가 (없으면)
                    if item_id not in inventory.get("items", []):
                        inventory.setdefault("items", []).append(item_id)
                    
                    # 수량 업데이트
                    quantities = inventory.setdefault("quantities", {})
                    current_quantity = quantities.get(item_id, 0)
                    quantities[item_id] = current_quantity + quantity
                    
                    # 인벤토리 업데이트
                    await conn.execute(
                        """
                        UPDATE runtime_data.entity_states
                        SET inventory = $1::jsonb,
                            updated_at = NOW()
                        WHERE runtime_entity_id = $2
                        """,
                        json.dumps(inventory),
                        runtime_entity_id
                    )
                    
                    logger.info(f"Added {quantity}x {item_id} to inventory of {runtime_entity_id}")
                    return True
                    
        except Exception as e:
            logger.error(f"Failed to add item to inventory: {str(e)}")
            raise
    
    async def remove_item_from_inventory(
        self,
        runtime_entity_id: str,
        item_id: str,
        quantity: int = 1
    ) -> bool:
        """
        엔티티 인벤토리에서 아이템 제거
        
        Args:
            runtime_entity_id: 엔티티 런타임 ID
            item_id: 아이템 템플릿 ID
            quantity: 제거할 수량
        
        Returns:
            성공 여부
        """
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                async with conn.transaction():
                    # 현재 인벤토리 조회
                    entity_state = await conn.fetchrow(
                        """
                        SELECT inventory
                        FROM runtime_data.entity_states
                        WHERE runtime_entity_id = $1
                        """,
                        runtime_entity_id
                    )
                    
                    if not entity_state:
                        raise ValueError(f"Entity state not found: {runtime_entity_id}")
                    
                    # 인벤토리 파싱
                    inventory = json.loads(entity_state['inventory']) if isinstance(entity_state['inventory'], str) else entity_state['inventory']
                    if not inventory:
                        raise ValueError("Inventory is empty")
                    
                    quantities = inventory.get("quantities", {})
                    current_quantity = quantities.get(item_id, 0)
                    
                    if current_quantity < quantity:
                        raise ValueError(f"Insufficient quantity: {item_id} (have {current_quantity}, need {quantity})")
                    
                    # 수량 업데이트
                    new_quantity = current_quantity - quantity
                    if new_quantity <= 0:
                        # 수량이 0 이하면 아이템 제거
                        quantities.pop(item_id, None)
                        items = inventory.get("items", [])
                        if item_id in items:
                            items.remove(item_id)
                    else:
                        quantities[item_id] = new_quantity
                    
                    # 인벤토리 업데이트
                    await conn.execute(
                        """
                        UPDATE runtime_data.entity_states
                        SET inventory = $1::jsonb,
                            updated_at = NOW()
                        WHERE runtime_entity_id = $2
                        """,
                        json.dumps(inventory),
                        runtime_entity_id
                    )
                    
                    logger.info(f"Removed {quantity}x {item_id} from inventory of {runtime_entity_id}")
                    return True
                    
        except Exception as e:
            logger.error(f"Failed to remove item from inventory: {str(e)}")
            raise
    
    async def get_inventory(self, runtime_entity_id: str) -> Dict[str, Any]:
        """
        엔티티 인벤토리 조회
        
        Args:
            runtime_entity_id: 엔티티 런타임 ID
        
        Returns:
            인벤토리 정보 {"items": [...], "quantities": {...}}
        """
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                entity_state = await conn.fetchrow(
                    """
                    SELECT inventory
                    FROM runtime_data.entity_states
                    WHERE runtime_entity_id = $1
                    """,
                    runtime_entity_id
                )
                
                if not entity_state:
                    raise ValueError(f"Entity state not found: {runtime_entity_id}")
                
                inventory = entity_state['inventory']
                if isinstance(inventory, str):
                    inventory = json.loads(inventory)
                
                return inventory if inventory else {"items": [], "quantities": {}}
                
        except Exception as e:
            logger.error(f"Failed to get inventory: {str(e)}")
            raise

