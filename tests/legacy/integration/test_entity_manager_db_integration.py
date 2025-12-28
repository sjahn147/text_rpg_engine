"""
Entity Manager 실제 DB 통합 테스트
"""

import pytest
import pytest_asyncio
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from app.entity.entity_manager import EntityManager, EntityData, EntityType, EntityStatus, EntityResult
from app.effect_carrier.effect_carrier_manager import EffectCarrierManager, EffectCarrierData, EffectCarrierType, EffectCarrierResult
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from common.utils.logger import logger

class TestEntityManagerDBIntegration:
    """Entity Manager 실제 DB 통합 테스트"""
    
    @pytest_asyncio.fixture
    async def db_connection(self):
        """실제 DB 연결"""
        db = DatabaseConnection()
        try:
            await db.pool
            logger.info("실제 DB 연결 성공")
            return db
        except Exception as e:
            logger.error(f"실제 DB 연결 실패: {str(e)}")
            pytest.skip("DB 연결 실패")
    
    @pytest_asyncio.fixture
    async def repositories(self, db_connection):
        """리포지토리 인스턴스들"""
        return {
            'game_data_repo': GameDataRepository(db_connection),
            'runtime_data_repo': RuntimeDataRepository(db_connection),
            'reference_layer_repo': ReferenceLayerRepository(db_connection)
        }
    
    @pytest_asyncio.fixture
    async def effect_carrier_manager(self, db_connection, repositories):
        """Effect Carrier Manager 인스턴스"""
        return EffectCarrierManager(
            db_connection,
            repositories['game_data_repo'],
            repositories['runtime_data_repo'],
            repositories['reference_layer_repo']
        )
    
    @pytest_asyncio.fixture
    async def entity_manager(self, db_connection, repositories, effect_carrier_manager):
        """Entity Manager 인스턴스"""
        return EntityManager(
            db_connection,
            repositories['game_data_repo'],
            repositories['runtime_data_repo'],
            repositories['reference_layer_repo'],
            effect_carrier_manager
        )
    
    @pytest.mark.asyncio
    async def test_entity_creation_with_db(self, entity_manager):
        """실제 DB를 통한 엔티티 생성 테스트"""
        # Given
        name = "Test Entity DB"
        entity_type = EntityType.NPC
        properties = {"health": 100, "level": 5, "mana": 50}
        position = {"x": 10.0, "y": 20.0}
        
        # When
        result = await entity_manager.create_entity(
            name=name,
            entity_type=entity_type,
            properties=properties,
            position=position
        )
        
        # Then
        assert result.success, f"엔티티 생성 실패: {result.message}"
        assert result.entity is not None
        assert result.entity.name == name
        assert result.entity.entity_type == entity_type
        assert result.entity.properties == properties
        assert result.entity.position == position
        
        # 생성된 엔티티 ID 저장
        entity_id = result.entity.entity_id
        logger.info(f"엔티티 생성 성공: {entity_id}")
        
        return entity_id
    
    @pytest.mark.asyncio
    async def test_entity_retrieval_with_db(self, entity_manager):
        """실제 DB를 통한 엔티티 조회 테스트"""
        # Given - 엔티티 생성
        entity_id = await self.test_entity_creation_with_db(entity_manager)
        
        # When
        result = await entity_manager.get_entity(entity_id)
        
        # Then
        assert result.success, f"엔티티 조회 실패: {result.message}"
        assert result.entity is not None
        assert result.entity.entity_id == entity_id
        assert result.entity.name == "Test Entity DB"
        
        logger.info(f"엔티티 조회 성공: {entity_id}")
    
    @pytest.mark.asyncio
    async def test_entity_update_with_db(self, entity_manager):
        """실제 DB를 통한 엔티티 업데이트 테스트"""
        # Given - 엔티티 생성
        entity_id = await self.test_entity_creation_with_db(entity_manager)
        
        # When - 엔티티 업데이트
        updates = {
            "properties": {"health": 80, "level": 6, "mana": 60},
            "position": {"x": 15.0, "y": 25.0}
        }
        result = await entity_manager.update_entity(entity_id, updates)
        
        # Then
        assert result.success, f"엔티티 업데이트 실패: {result.message}"
        assert result.entity is not None
        assert result.entity.properties["health"] == 80
        assert result.entity.properties["level"] == 6
        assert result.entity.position["x"] == 15.0
        
        logger.info(f"엔티티 업데이트 성공: {entity_id}")
    
    @pytest.mark.asyncio
    async def test_entity_deletion_with_db(self, entity_manager):
        """실제 DB를 통한 엔티티 삭제 테스트"""
        # Given - 엔티티 생성
        entity_id = await self.test_entity_creation_with_db(entity_manager)
        
        # When
        result = await entity_manager.delete_entity(entity_id)
        
        # Then
        assert result.success, f"엔티티 삭제 실패: {result.message}"
        
        # 삭제된 엔티티 조회 시 실패해야 함
        get_result = await entity_manager.get_entity(entity_id)
        assert not get_result.success, "삭제된 엔티티가 여전히 존재함"
        
        logger.info(f"엔티티 삭제 성공: {entity_id}")
    
    @pytest.mark.asyncio
    async def test_effect_carrier_creation_with_db(self, effect_carrier_manager):
        """실제 DB를 통한 Effect Carrier 생성 테스트"""
        # Given
        name = "Fireball Spell"
        carrier_type = EffectCarrierType.SKILL
        effect_json = {
            "damage": 50,
            "range": 3,
            "cooldown": 5,
            "mana_cost": 20
        }
        constraints_json = {
            "min_level": 3,
            "required_class": "mage"
        }
        tags = ["fire", "damage", "ranged"]
        
        # When
        result = await effect_carrier_manager.create_effect_carrier(
            name=name,
            carrier_type=carrier_type,
            effect_json=effect_json,
            constraints_json=constraints_json,
            tags=tags
        )
        
        # Then
        assert result.success, f"Effect Carrier 생성 실패: {result.message}"
        assert result.data is not None
        assert result.data.name == name
        assert result.data.carrier_type == carrier_type
        assert result.data.effect_json == effect_json
        assert result.data.constraints_json == constraints_json
        assert result.data.tags == tags
        
        # 생성된 Effect Carrier ID 저장
        effect_id = result.data.effect_id
        logger.info(f"Effect Carrier 생성 성공: {effect_id}")
        
        return effect_id
    
    @pytest.mark.asyncio
    async def test_effect_carrier_retrieval_with_db(self, effect_carrier_manager):
        """실제 DB를 통한 Effect Carrier 조회 테스트"""
        # Given - Effect Carrier 생성
        effect_id = await self.test_effect_carrier_creation_with_db(effect_carrier_manager)
        
        # When
        result = await effect_carrier_manager.get_effect_carrier(effect_id)
        
        # Then
        assert result.success, f"Effect Carrier 조회 실패: {result.message}"
        assert result.data is not None
        assert result.data.effect_id == effect_id
        assert result.data.name == "Fireball Spell"
        
        logger.info(f"Effect Carrier 조회 성공: {effect_id}")
    
    @pytest.mark.asyncio
    async def test_entity_effect_carrier_integration(self, entity_manager, effect_carrier_manager):
        """엔티티와 Effect Carrier 통합 테스트"""
        # Given - 엔티티와 Effect Carrier 생성
        entity_id = await self.test_entity_creation_with_db(entity_manager)
        effect_id = await self.test_effect_carrier_creation_with_db(effect_carrier_manager)
        session_id = "test-session-001"
        
        # When - 엔티티에 Effect Carrier 적용
        apply_result = await entity_manager.apply_effect_carrier(entity_id, effect_id, session_id)
        
        # Then
        assert apply_result.success, f"Effect Carrier 적용 실패: {apply_result.message}"
        
        # 엔티티의 Effect Carrier 목록 조회
        effects_result = await entity_manager.get_entity_effects(entity_id, session_id)
        assert effects_result.success, f"엔티티 Effect Carrier 조회 실패: {effects_result.message}"
        assert effects_result.data is not None
        assert len(effects_result.data) == 1
        assert effects_result.data[0].effect_id == effect_id
        
        logger.info(f"엔티티 Effect Carrier 통합 성공: {entity_id} -> {effect_id}")
        
        # Effect Carrier 제거
        remove_result = await entity_manager.remove_effect_carrier(entity_id, effect_id, session_id)
        assert remove_result.success, f"Effect Carrier 제거 실패: {remove_result.message}"
        
        logger.info(f"Effect Carrier 제거 성공: {entity_id} -> {effect_id}")
    
    @pytest.mark.asyncio
    async def test_entity_stats_update_with_db(self, entity_manager):
        """실제 DB를 통한 엔티티 스탯 업데이트 테스트"""
        # Given - 엔티티 생성
        entity_id = await self.test_entity_creation_with_db(entity_manager)
        
        # When - 스탯 업데이트
        stats = {
            "health": 120,
            "level": 7,
            "mana": 80,
            "strength": 15,
            "intelligence": 12
        }
        result = await entity_manager.update_entity_stats(entity_id, stats)
        
        # Then
        assert result.success, f"엔티티 스탯 업데이트 실패: {result.message}"
        assert result.entity is not None
        assert result.entity.properties["health"] == 120
        assert result.entity.properties["level"] == 7
        assert result.entity.properties["strength"] == 15
        
        logger.info(f"엔티티 스탯 업데이트 성공: {entity_id}")
    
    @pytest.mark.asyncio
    async def test_entity_list_with_db(self, entity_manager):
        """실제 DB를 통한 엔티티 목록 조회 테스트"""
        # Given - 여러 엔티티 생성
        entity_ids = []
        for i in range(3):
            entity_id = await self.test_entity_creation_with_db(entity_manager)
            entity_ids.append(entity_id)
        
        # When
        result = await entity_manager.list_entities()
        
        # Then
        assert result.success, f"엔티티 목록 조회 실패: {result.message}"
        assert result.data is not None
        assert len(result.data) >= 3
        
        # 생성된 엔티티들이 목록에 있는지 확인
        entity_names = [entity.name for entity in result.data]
        assert "Test Entity DB" in entity_names
        
        logger.info(f"엔티티 목록 조회 성공: {len(result.data)}개 엔티티")
    
    @pytest.mark.asyncio
    async def test_entity_list_with_filters_with_db(self, entity_manager):
        """실제 DB를 통한 필터링된 엔티티 목록 조회 테스트"""
        # Given - 여러 엔티티 생성
        entity_ids = []
        for i in range(3):
            entity_id = await self.test_entity_creation_with_db(entity_manager)
            entity_ids.append(entity_id)
        
        # When - NPC 타입으로 필터링
        result = await entity_manager.list_entities(entity_type=EntityType.NPC)
        
        # Then
        assert result.success, f"필터링된 엔티티 목록 조회 실패: {result.message}"
        assert result.data is not None
        
        # 모든 엔티티가 NPC 타입인지 확인
        for entity in result.data:
            assert entity.entity_type == EntityType.NPC
        
        logger.info(f"필터링된 엔티티 목록 조회 성공: {len(result.data)}개 NPC")
    
    @pytest.mark.asyncio
    async def test_entity_cache_consistency_with_db(self, entity_manager):
        """실제 DB를 통한 엔티티 캐시 일관성 테스트"""
        # Given - 엔티티 생성
        entity_id = await self.test_entity_creation_with_db(entity_manager)
        
        # When - 캐시에서 조회
        result1 = await entity_manager.get_entity(entity_id)
        result2 = await entity_manager.get_entity(entity_id)
        
        # Then
        assert result1.success and result2.success
        assert result1.entity.entity_id == result2.entity.entity_id
        assert result1.entity.name == result2.entity.name
        
        # 캐시 초기화 후 다시 조회
        await entity_manager.clear_cache()
        result3 = await entity_manager.get_entity(entity_id)
        
        assert result3.success
        assert result3.entity.entity_id == entity_id
        
        logger.info(f"엔티티 캐시 일관성 테스트 성공: {entity_id}")
    
    @pytest.mark.asyncio
    async def test_entity_error_handling_with_db(self, entity_manager):
        """실제 DB를 통한 엔티티 에러 처리 테스트"""
        # Given - 존재하지 않는 엔티티 ID
        non_existent_id = "non-existent-entity-id"
        
        # When
        result = await entity_manager.get_entity(non_existent_id)
        
        # Then
        assert not result.success, "존재하지 않는 엔티티 조회가 성공함"
        assert "찾을 수 없습니다" in result.message
        
        logger.info(f"엔티티 에러 처리 테스트 성공: {non_existent_id}")
    
    @pytest.mark.asyncio
    async def test_effect_carrier_error_handling_with_db(self, effect_carrier_manager):
        """실제 DB를 통한 Effect Carrier 에러 처리 테스트"""
        # Given - 존재하지 않는 Effect Carrier ID
        non_existent_id = "non-existent-effect-id"
        
        # When
        result = await effect_carrier_manager.get_effect_carrier(non_existent_id)
        
        # Then
        assert not result.success, "존재하지 않는 Effect Carrier 조회가 성공함"
        assert "찾을 수 없습니다" in result.message
        
        logger.info(f"Effect Carrier 에러 처리 테스트 성공: {non_existent_id}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
