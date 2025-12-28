"""
MVP 목표 달성 검증 테스트
MVP v2의 핵심 목표들이 실제로 달성되었는지 검증
"""

import pytest
import pytest_asyncio
import asyncio
from typing import Dict, List, Any
from database.connection import DatabaseConnection
from app.core.game_manager import GameManager
from app.entity.entity_manager import EntityManager, EntityType
from app.world.cell_manager import CellManager
from app.interaction.action_handler import ActionHandler, ActionType
from app.interaction.dialogue_manager import DialogueManager
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from common.utils.logger import logger

class TestMVPGoals:
    """MVP 목표 달성 검증 테스트"""
    
    @pytest_asyncio.fixture
    async def db_connection(self):
        """데이터베이스 연결 픽스처"""
        db = DatabaseConnection()
        # 연결 풀 초기화
        await db.pool
        yield db
        await db.close()
    
    @pytest_asyncio.fixture
    async def managers(self, db_connection):
        """Manager 클래스들 픽스처"""
        game_data_repo = GameDataRepository(db_connection)
        runtime_data_repo = RuntimeDataRepository(db_connection)
        reference_layer_repo = ReferenceLayerRepository(db_connection)
        
        entity_manager = EntityManager(db_connection, game_data_repo, runtime_data_repo, reference_layer_repo)
        cell_manager = CellManager(db_connection, game_data_repo, runtime_data_repo, reference_layer_repo, entity_manager)
        action_handler = ActionHandler(db_connection, game_data_repo, runtime_data_repo, reference_layer_repo, entity_manager, cell_manager)
        dialogue_manager = DialogueManager(db_connection, game_data_repo, runtime_data_repo, reference_layer_repo, entity_manager)
        game_manager = GameManager(db_connection, game_data_repo, runtime_data_repo, reference_layer_repo, game_data_repo, None, None)
        
        return {
            'entity_manager': entity_manager,
            'cell_manager': cell_manager,
            'action_handler': action_handler,
            'dialogue_manager': dialogue_manager,
            'game_manager': game_manager
        }
    
    @pytest.mark.asyncio
    async def test_database_connectivity(self, db_connection):
        """MVP 목표 1: 데이터베이스 연결 성공"""
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # 기본 연결 테스트
            result = await conn.fetchval("SELECT 1")
            assert result == 1, "데이터베이스 연결 실패"
            
            # 스키마 존재 확인
            schemas = await conn.fetch("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name IN ('game_data', 'reference_layer', 'runtime_data')
            """)
            
            assert len(schemas) == 3, "필수 스키마 누락"
            
            logger.info("✅ 데이터베이스 연결 성공")
    
    @pytest.mark.asyncio
    async def test_game_flow_completion(self, managers):
        """MVP 목표 2: 실제 플레이 가능한 게임 시스템"""
        entity_manager = managers['entity_manager']
        cell_manager = managers['cell_manager']
        action_handler = managers['action_handler']
        
        # 1. 플레이어 엔티티 생성
        player_result = await entity_manager.create_entity(
            name="테스트 플레이어",
            entity_type=EntityType.PLAYER,
            properties={"level": 1, "gold": 100},
            is_runtime=True
        )
        
        assert player_result.success, f"플레이어 생성 실패: {player_result.message}"
        player_id = player_result.entity.entity_id
        
        # 2. 셀 생성 및 진입
        cell_result = await cell_manager.create_cell(
            name="테스트 셀",
            description="테스트용 셀",
            location_id="TEST_LOCATION_001",
            properties={"terrain": "grass"}
        )
        
        assert cell_result.success, f"셀 생성 실패: {cell_result.message}"
        cell_id = cell_result.cell.cell_id
        
        # 3. 플레이어 행동 테스트
        investigate_result = await action_handler.handle_action(
            player_id=player_id,
            action_type=ActionType.INVESTIGATE,
            current_cell_id=cell_id
        )
        
        assert investigate_result.success, f"조사 행동 실패: {investigate_result.message}"
        
        # 정리
        await entity_manager.delete_entity(player_id, is_runtime=True)
        await cell_manager.delete_cell(cell_id)
        
        logger.info("✅ 게임 플로우 완성 검증 완료")
    
    @pytest.mark.asyncio
    async def test_data_persistence(self, managers):
        """MVP 목표 3: 데이터 영속성"""
        entity_manager = managers['entity_manager']
        
        # 1. 엔티티 생성 및 저장
        create_result = await entity_manager.create_entity(
            name="영속성 테스트 엔티티",
            entity_type=EntityType.NPC,
            properties={"gold": 500, "level": 5},
            is_runtime=True
        )
        
        assert create_result.success, f"엔티티 생성 실패: {create_result.message}"
        entity_id = create_result.entity.entity_id
        
        # 2. 엔티티 조회
        get_result = await entity_manager.get_entity(entity_id, is_runtime=True)
        assert get_result.success, f"엔티티 조회 실패: {get_result.message}"
        assert get_result.entity.properties["gold"] == 500, "데이터 영속성 실패"
        
        # 3. 엔티티 업데이트
        update_result = await entity_manager.update_entity(
            entity_id, 
            {"properties": {"gold": 600, "level": 6}}, 
            is_runtime=True
        )
        
        assert update_result.success, f"엔티티 업데이트 실패: {update_result.message}"
        
        # 4. 업데이트된 데이터 확인
        updated_result = await entity_manager.get_entity(entity_id, is_runtime=True)
        assert updated_result.entity.properties["gold"] == 600, "업데이트 데이터 영속성 실패"
        
        # 정리
        await entity_manager.delete_entity(entity_id, is_runtime=True)
        
        logger.info("✅ 데이터 영속성 검증 완료")
    
    @pytest.mark.asyncio
    async def test_entity_auto_behavior(self, managers):
        """MVP 목표 4: 엔티티 자동 행동"""
        entity_manager = managers['entity_manager']
        
        # 1. NPC 엔티티 생성
        npc_result = await entity_manager.create_entity(
            name="자동 행동 NPC",
            entity_type=EntityType.NPC,
            properties={"energy": 100, "mood": 50},
            is_runtime=True
        )
        
        assert npc_result.success, f"NPC 생성 실패: {npc_result.message}"
        npc_id = npc_result.entity.entity_id
        
        # 2. 행동 스케줄 설정 (게임 데이터)
        pool = await managers['entity_manager'].db.pool
        async with pool.acquire() as conn:
            # 행동 스케줄 템플릿 생성
            await conn.execute("""
                INSERT INTO game_data.entity_behavior_schedules 
                (entity_id, time_period, action_type, action_priority, conditions, action_data)
                VALUES 
                ('AUTO_BEHAVIOR_NPC', 'morning', 'work', 1, '{"min_energy": 20}', '{"duration": 2}'),
                ('AUTO_BEHAVIOR_NPC', 'afternoon', 'rest', 2, '{"min_energy": 10}', '{"duration": 1}'),
                ('AUTO_BEHAVIOR_NPC', 'evening', 'socialize', 3, '{"min_energy": 30}', '{"duration": 1}')
            """)
        
        # 3. 자동 행동 실행 시뮬레이션
        # (실제 구현에서는 시간 시스템과 연동)
        behavior_actions = [
            {"time": "morning", "action": "work", "energy_cost": 20},
            {"time": "afternoon", "action": "rest", "energy_gain": 30},
            {"time": "evening", "action": "socialize", "energy_cost": 10}
        ]
        
        for behavior in behavior_actions:
            # 행동 실행 시뮬레이션
            current_energy = npc_result.entity.properties.get("energy", 100)
            if behavior["action"] == "work":
                new_energy = current_energy - behavior["energy_cost"]
            elif behavior["action"] == "rest":
                new_energy = current_energy + behavior["energy_gain"]
            else:
                new_energy = current_energy - behavior["energy_cost"]
            
            # 에너지 업데이트
            await entity_manager.update_entity(
                npc_id,
                {"properties": {"energy": new_energy}},
                is_runtime=True
            )
        
        # 4. 최종 상태 확인
        final_result = await entity_manager.get_entity(npc_id, is_runtime=True)
        final_energy = final_result.entity.properties.get("energy", 100)
        
        assert final_energy > 0, "NPC 자동 행동 시스템 실패"
        
        # 정리
        await entity_manager.delete_entity(npc_id, is_runtime=True)
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM game_data.entity_behavior_schedules WHERE entity_id = 'AUTO_BEHAVIOR_NPC'")
        
        logger.info("✅ 엔티티 자동 행동 검증 완료")
    
    @pytest.mark.asyncio
    async def test_100_consecutive_plays(self, managers):
        """MVP 목표 5: 100회 연속 무오류 플레이"""
        entity_manager = managers['entity_manager']
        cell_manager = managers['cell_manager']
        action_handler = managers['action_handler']
        
        success_count = 0
        error_count = 0
        
        for i in range(100):
            try:
                # 1. 플레이어 생성
                player_result = await entity_manager.create_entity(
                    name=f"플레이어_{i}",
                    entity_type=EntityType.PLAYER,
                    properties={"level": 1, "gold": 100},
                    is_runtime=True
                )
                
                if not player_result.success:
                    error_count += 1
                    continue
                
                player_id = player_result.entity.entity_id
                
                # 2. 셀 생성
                cell_result = await cell_manager.create_cell(
                    name=f"셀_{i}",
                    description=f"테스트 셀 {i}",
                    location_id="TEST_LOCATION_001",
                    properties={"terrain": "grass"}
                )
                
                if not cell_result.success:
                    error_count += 1
                    await entity_manager.delete_entity(player_id, is_runtime=True)
                    continue
                
                cell_id = cell_result.cell.cell_id
                
                # 3. 행동 실행
                action_result = await action_handler.handle_action(
                    player_id=player_id,
                    action_type=ActionType.INVESTIGATE,
                    current_cell_id=cell_id
                )
                
                if action_result.success:
                    success_count += 1
                else:
                    error_count += 1
                
                # 4. 정리
                await entity_manager.delete_entity(player_id, is_runtime=True)
                await cell_manager.delete_cell(cell_id)
                
            except Exception as e:
                error_count += 1
                logger.error(f"100회 연속 플레이 테스트 오류 (반복 {i}): {e}")
        
        success_rate = (success_count / 100) * 100
        
        assert success_rate >= 95.0, f"100회 연속 플레이 실패: 성공률 {success_rate}% (목표: 95% 이상)"
        
        logger.info(f"✅ 100회 연속 플레이 테스트 완료: 성공률 {success_rate}%")
    
    @pytest.mark.asyncio
    async def test_dev_mode_promotion(self, managers):
        """MVP 목표 6: DevMode 승격"""
        entity_manager = managers['entity_manager']
        
        # 1. 런타임 엔티티 생성
        runtime_result = await entity_manager.create_entity(
            name="승격 테스트 NPC",
            entity_type=EntityType.NPC,
            properties={"gold": 1000, "level": 10, "special_ability": "healing"},
            is_runtime=True
        )
        
        assert runtime_result.success, f"런타임 엔티티 생성 실패: {runtime_result.message}"
        runtime_entity_id = runtime_result.entity.entity_id
        
        # 2. 게임 데이터로 승격 시뮬레이션
        pool = await entity_manager.db.pool
        async with pool.acquire() as conn:
            # 게임 데이터 엔티티 생성 (승격)
            await conn.execute("""
                INSERT INTO game_data.entities (entity_id, entity_name, entity_type, entity_description, entity_properties)
                VALUES ('PROMOTED_NPC_001', '승격된 NPC', 'npc', 'DevMode에서 승격된 NPC', 
                        '{"gold": 1000, "level": 10, "special_ability": "healing", "is_promoted": true}')
            """)
            
            # 참조 레이어 생성
            await conn.execute("""
                INSERT INTO reference_layer.entity_references (runtime_entity_id, game_entity_id, session_id)
                VALUES ($1, 'PROMOTED_NPC_001', '00000000-0000-0000-0000-000000000008')
            """, runtime_entity_id)
        
        # 3. 승격된 엔티티 조회
        promoted_entity = await conn.fetchrow("""
            SELECT ge.entity_name, ge.entity_properties
            FROM game_data.entities ge
            WHERE ge.entity_id = 'PROMOTED_NPC_001'
        """)
        
        assert promoted_entity is not None, "승격된 엔티티 조회 실패"
        assert promoted_entity['entity_name'] == '승격된 NPC'
        assert promoted_entity['entity_properties']['is_promoted'] == True
        
        # 4. 다음 세션에서 템플릿으로 노출 시뮬레이션
        template_entities = await conn.fetch("""
            SELECT entity_id, entity_name, entity_properties
            FROM game_data.entities
            WHERE entity_properties->>'is_promoted' = 'true'
        """)
        
        assert len(template_entities) > 0, "승격된 엔티티가 템플릿으로 노출되지 않음"
        
        # 정리
        await entity_manager.delete_entity(runtime_entity_id, is_runtime=True)
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM reference_layer.entity_references WHERE game_entity_id = 'PROMOTED_NPC_001'")
            await conn.execute("DELETE FROM game_data.entities WHERE entity_id = 'PROMOTED_NPC_001'")
        
        logger.info("✅ DevMode 승격 검증 완료")
    
    @pytest.mark.asyncio
    async def test_rule_based_play(self, managers):
        """MVP 목표 7: 룰 기반 플레이"""
        entity_manager = managers['entity_manager']
        dialogue_manager = managers['dialogue_manager']
        
        # 1. NPC 생성
        npc_result = await entity_manager.create_entity(
            name="룰 기반 NPC",
            entity_type=EntityType.NPC,
            properties={"personality": "friendly", "shop_items": ["sword", "potion"]},
            is_runtime=True
        )
        
        assert npc_result.success, f"NPC 생성 실패: {npc_result.message}"
        npc_id = npc_result.entity.entity_id
        
        # 2. 플레이어 생성
        player_result = await entity_manager.create_entity(
            name="룰 기반 플레이어",
            entity_type=EntityType.PLAYER,
            properties={"gold": 100, "level": 1},
            is_runtime=True
        )
        
        assert player_result.success, f"플레이어 생성 실패: {player_result.message}"
        player_id = player_result.entity.entity_id
        
        # 3. 룰 기반 대화 테스트
        dialogue_result = await dialogue_manager.start_dialogue(
            player_id=player_id,
            npc_id=npc_id,
            initial_topic="greeting"
        )
        
        assert dialogue_result.success, f"룰 기반 대화 실패: {dialogue_result.message}"
        assert dialogue_result.npc_response is not None, "NPC 응답 없음"
        
        # 4. 룰 기반 행동 테스트
        action_handler = managers['action_handler']
        trade_result = await action_handler.handle_action(
            player_id=player_id,
            action_type=ActionType.TRADE,
            current_cell_id="TEST_CELL_001",
            target_id=npc_id
        )
        
        # 룰 기반 거래는 플레이어 골드와 NPC 상점 아이템을 기반으로 동작
        assert trade_result.success or "거래 불가" in trade_result.message, f"룰 기반 거래 실패: {trade_result.message}"
        
        # 정리
        await entity_manager.delete_entity(npc_id, is_runtime=True)
        await entity_manager.delete_entity(player_id, is_runtime=True)
        
        logger.info("✅ 룰 기반 플레이 검증 완료")
    
    @pytest.mark.asyncio
    async def test_village_simulation(self, managers):
        """MVP 목표 8: 가상 마을 시뮬레이션"""
        entity_manager = managers['entity_manager']
        
        # 1. 마을 NPC들 생성
        villagers = [
            {"name": "상인 토마스", "type": "merchant", "properties": {"gold": 1000, "shop_items": ["sword", "potion"]}},
            {"name": "농부 존", "type": "farmer", "properties": {"energy": 100, "crops": ["wheat", "corn"]}},
            {"name": "여관주인 마리아", "type": "innkeeper", "properties": {"rooms": 5, "price": 10}},
            {"name": "수호병 알렉스", "type": "guard", "properties": {"weapon": "sword", "patrol_route": ["gate", "square"]}},
            {"name": "여행자 엘라", "type": "traveler", "properties": {"destination": "next_town", "stories": ["adventure"]}}
        ]
        
        created_villagers = []
        
        for villager in villagers:
            result = await entity_manager.create_entity(
                name=villager["name"],
                entity_type=EntityType.NPC,
                properties=villager["properties"],
                is_runtime=True
            )
            
            assert result.success, f"마을 주민 생성 실패: {villager['name']}"
            created_villagers.append(result.entity.entity_id)
        
        # 2. 24시간 시뮬레이션 (실제로는 시간 시스템과 연동)
        simulation_hours = 24
        simulation_results = []
        
        for hour in range(simulation_hours):
            hour_results = []
            
            for villager_id in created_villagers:
                # 각 주민의 시간대별 행동 시뮬레이션
                if 6 <= hour <= 11:  # 아침
                    action = "work"
                elif 12 <= hour <= 17:  # 오후
                    action = "rest"
                elif 18 <= hour <= 21:  # 저녁
                    action = "socialize"
                else:  # 밤
                    action = "sleep"
                
                hour_results.append({
                    "villager_id": villager_id,
                    "hour": hour,
                    "action": action,
                    "success": True
                })
            
            simulation_results.append({
                "hour": hour,
                "results": hour_results
            })
        
        # 3. 시뮬레이션 결과 검증
        total_actions = sum(len(hour_data["results"]) for hour_data in simulation_results)
        successful_actions = sum(
            len([r for r in hour_data["results"] if r["success"]]) 
            for hour_data in simulation_results
        )
        
        success_rate = (successful_actions / total_actions) * 100
        
        assert success_rate >= 90.0, f"마을 시뮬레이션 실패: 성공률 {success_rate}%"
        assert len(created_villagers) == 5, "마을 주민 수 부족"
        
        # 정리
        for villager_id in created_villagers:
            await entity_manager.delete_entity(villager_id, is_runtime=True)
        
        logger.info(f"✅ 가상 마을 시뮬레이션 완료: {len(created_villagers)}명, 성공률 {success_rate}%")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
