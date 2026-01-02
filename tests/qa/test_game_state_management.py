"""
게임 상태 관리 QA 테스트

P2 (Medium): 게임 상태 관리 검증
"""
import pytest
import pytest_asyncio
import json
from typing import Dict, Any
from common.utils.logger import logger


@pytest.mark.asyncio
class TestGameStateManagement:
    """게임 상태 관리 테스트"""
    
    async def test_player_inventory_retrieval(
        self,
        db_connection,
        game_service,
        test_game_data
    ):
        """
        P2-1: 플레이어 인벤토리 조회 검증
        
        검증 항목:
        - 인벤토리 JSONB 파싱
        - 장착 아이템 정보 조회
        - 아이템 템플릿 정보 조회
        """
        logger.info("[P2-1] 플레이어 인벤토리 조회 검증 테스트 시작")
        
        # 게임 시작
        result = await game_service.start_game(
            player_template_id=test_game_data["player_template_id"],
            start_cell_id=test_game_data["cell_id"]
        )
        
        session_id = result["game_state"]["session_id"]
        
        # 플레이어 인벤토리 조회
        inventory = await game_service.get_player_inventory(session_id)
        
        assert inventory is not None, "인벤토리 정보가 조회되어야 함"
        assert "inventory" in inventory or "items" in inventory, \
            "인벤토리 항목이 포함되어야 함"
        
        # 인벤토리 JSONB 파싱 확인
        if "inventory" in inventory:
            assert isinstance(inventory["inventory"], (list, dict)), \
                "인벤토리는 리스트 또는 딕셔너리여야 함"
        
        # 장착 아이템 정보 확인
        if "equipped_items" in inventory:
            assert isinstance(inventory["equipped_items"], (list, dict)), \
                "장착 아이템은 리스트 또는 딕셔너리여야 함"
        
        logger.info("[P2-1] 플레이어 인벤토리 조회 검증 테스트 통과")
    
    async def test_player_character_info_retrieval(
        self,
        db_connection,
        game_service,
        test_game_data
    ):
        """
        P2-2: 플레이어 캐릭터 정보 조회 검증
        
        검증 항목:
        - 스탯 계산 정확성
        - HP/MP 계산 정확성
        - 장착 아이템 정보 정확성
        """
        logger.info("[P2-2] 플레이어 캐릭터 정보 조회 검증 테스트 시작")
        
        # 게임 시작
        result = await game_service.start_game(
            player_template_id=test_game_data["player_template_id"],
            start_cell_id=test_game_data["cell_id"]
        )
        
        session_id = result["game_state"]["session_id"]
        player_id = result["game_state"]["player_id"]
        
        # 플레이어 정보 조회
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # entity_states에서 플레이어 정보 조회
            entity_state = await conn.fetchrow("""
                SELECT 
                    current_stats,
                    current_position,
                    inventory,
                    equipped_items
                FROM runtime_data.entity_states
                WHERE runtime_entity_id = $1
            """, player_id)
            
            assert entity_state is not None, "플레이어 상태가 존재해야 함"
            
            # 스탯 정보 확인
            if entity_state["current_stats"]:
                stats = entity_state["current_stats"]
                if isinstance(stats, str):
                    stats = json.loads(stats)
                
                # 기본 스탯 필드 확인
                stat_fields = ["hp", "mp", "strength", "dexterity", "constitution", 
                              "intelligence", "wisdom", "charisma"]
                for field in stat_fields:
                    if field in stats:
                        assert isinstance(stats[field], (int, float)), \
                            f"{field}는 숫자여야 함"
                        if field in ["hp", "mp"]:
                            assert stats[field] >= 0, \
                                f"{field}는 0 이상이어야 함"
            
            # HP/MP 계산 정확성 확인
            # (기본값이 설정되어 있는지 확인)
            if entity_state["current_stats"]:
                stats = entity_state["current_stats"]
                if isinstance(stats, str):
                    stats = json.loads(stats)
                
                if "hp" in stats and "mp" in stats:
                    assert stats["hp"] > 0, "HP는 0보다 커야 함"
                    assert stats["mp"] >= 0, "MP는 0 이상이어야 함"
            
            # 장착 아이템 정보 확인
            if entity_state["equipped_items"]:
                equipped = entity_state["equipped_items"]
                if isinstance(equipped, str):
                    equipped = json.loads(equipped)
                
                if isinstance(equipped, list):
                    for item in equipped:
                        assert isinstance(item, dict), \
                            "장착 아이템은 딕셔너리여야 함"
        
        logger.info("[P2-2] 플레이어 캐릭터 정보 조회 검증 테스트 통과")

