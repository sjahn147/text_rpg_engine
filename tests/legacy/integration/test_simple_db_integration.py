"""
간단한 DB 통합 테스트
- 복잡한 픽스처 없이 직접 연결 관리
"""
import pytest
import asyncio
import uuid
from database.connection import DatabaseConnection
from app.entity.entity_manager import EntityManager, EntityType
from app.world.cell_manager import CellManager, CellType
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository


class TestSimpleDBIntegration:
    """간단한 DB 통합 테스트"""
    
    @pytest.mark.asyncio
    async def test_simple_entity_creation(self):
        """간단한 엔티티 생성 테스트"""
        # DB 연결 생성
        db_connection = DatabaseConnection()
        await db_connection.initialize()
        
        try:
            # 리포지토리 생성
            game_data_repo = GameDataRepository(db_connection)
            runtime_data_repo = RuntimeDataRepository(db_connection)
            reference_layer_repo = ReferenceLayerRepository(db_connection)
            
            # EntityManager 생성
            entity_manager = EntityManager(
                db_connection=db_connection,
                game_data_repo=game_data_repo,
                runtime_data_repo=runtime_data_repo,
                reference_layer_repo=reference_layer_repo,
                effect_carrier_manager=None  # 간단한 테스트를 위해 None
            )
            
            # 엔티티 생성
            result = await entity_manager.create_entity(
                name="Test Player",
                entity_type=EntityType.PLAYER,
                properties={"health": 100, "level": 1}
            )
            
            assert result.success
            assert result.entity is not None
            assert result.entity.name == "Test Player"
            assert result.entity.entity_type == EntityType.PLAYER
            
            print(f"✅ 엔티티 생성 성공: {result.entity.name}")
            
        finally:
            # 연결 정리
            await db_connection.close()
    
    @pytest.mark.asyncio
    async def test_simple_cell_creation(self):
        """간단한 셀 생성 테스트"""
        # DB 연결 생성
        db_connection = DatabaseConnection()
        await db_connection.initialize()
        
        try:
            # 리포지토리 생성
            game_data_repo = GameDataRepository(db_connection)
            runtime_data_repo = RuntimeDataRepository(db_connection)
            reference_layer_repo = ReferenceLayerRepository(db_connection)
            
            # CellManager 생성
            cell_manager = CellManager(
                db_connection=db_connection,
                game_data_repo=game_data_repo,
                runtime_data_repo=runtime_data_repo,
                reference_layer_repo=reference_layer_repo,
                entity_manager=None  # 간단한 테스트를 위해 None
            )
            
            # 셀 생성
            result = await cell_manager.create_cell(
                name="Test Room",
                cell_type=CellType.INDOOR,
                location_id="test-location-1",
                description="A test room"
            )
            
            assert result.success
            assert result.cell is not None
            assert result.cell.name == "Test Room"
            assert result.cell.cell_type == CellType.INDOOR
            
            print(f"✅ 셀 생성 성공: {result.cell.name}")
            
        finally:
            # 연결 정리
            await db_connection.close()
    
    @pytest.mark.asyncio
    async def test_multiple_operations(self):
        """여러 작업 연속 실행 테스트"""
        # DB 연결 생성
        db_connection = DatabaseConnection()
        await db_connection.initialize()
        
        try:
            # 리포지토리 생성
            game_data_repo = GameDataRepository(db_connection)
            runtime_data_repo = RuntimeDataRepository(db_connection)
            reference_layer_repo = ReferenceLayerRepository(db_connection)
            
            # EntityManager 생성
            entity_manager = EntityManager(
                db_connection=db_connection,
                game_data_repo=game_data_repo,
                runtime_data_repo=runtime_data_repo,
                reference_layer_repo=reference_layer_repo,
                effect_carrier_manager=None
            )
            
            # CellManager 생성
            cell_manager = CellManager(
                db_connection=db_connection,
                game_data_repo=game_data_repo,
                runtime_data_repo=runtime_data_repo,
                reference_layer_repo=reference_layer_repo,
                entity_manager=entity_manager
            )
            
            # 1. 엔티티 생성
            player_result = await entity_manager.create_entity(
                name="Adventurer",
                entity_type=EntityType.PLAYER,
                properties={"health": 100, "level": 1}
            )
            assert player_result.success
            print(f"✅ 플레이어 생성: {player_result.entity.name}")
            
            # 2. 셀 생성
            cell_result = await cell_manager.create_cell(
                name="Village Square",
                cell_type=CellType.OUTDOOR,
                location_id="village-1",
                description="A peaceful village square"
            )
            assert cell_result.success
            print(f"✅ 셀 생성: {cell_result.cell.name}")
            
            # 3. 플레이어를 셀에 배치
            enter_result = await cell_manager.enter_cell(
                cell_id=cell_result.cell.cell_id,
                player_id=player_result.entity.entity_id
            )
            assert enter_result.success
            print(f"✅ 셀 진입: {enter_result.message}")
            
            # 4. 엔티티 조회
            get_result = await entity_manager.get_entity(player_result.entity.entity_id)
            assert get_result.success
            assert get_result.entity.name == "Adventurer"
            print(f"✅ 엔티티 조회: {get_result.entity.name}")
            
            print("🎉 모든 작업이 성공적으로 완료되었습니다!")
            
        finally:
            # 연결 정리
            await db_connection.close()
    
    @pytest.mark.asyncio
    async def test_connection_stability(self):
        """연결 안정성 테스트"""
        # 여러 연결을 순차적으로 생성하고 정리
        for i in range(3):
            db_connection = DatabaseConnection()
            await db_connection.initialize()
            
            try:
                # 간단한 작업 수행
                pool = await db_connection.pool
                async with pool.acquire() as conn:
                    result = await conn.fetchval("SELECT 1")
                    assert result == 1
                
                print(f"✅ 연결 {i+1} 테스트 성공")
                
            finally:
                await db_connection.close()
        
        print("🎉 연결 안정성 테스트 완료!")
