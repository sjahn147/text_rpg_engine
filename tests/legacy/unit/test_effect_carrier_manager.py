"""
Effect Carrier Manager 단위 테스트
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
import json

from app.effect_carrier.effect_carrier_manager import (
    EffectCarrierManager,
    EffectCarrierData,
    EffectCarrierType,
    EffectOwnershipData,
    EffectCarrierResult
)
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository

class TestEffectCarrierManager:
    """Effect Carrier Manager 테스트"""
    
    @pytest_asyncio.fixture
    async def mock_db_connection(self):
        """Mock 데이터베이스 연결"""
        mock_db = AsyncMock(spec=DatabaseConnection)
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()
        mock_conn.fetchrow = AsyncMock()
        mock_conn.fetch = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_pool.acquire.return_value.__aexit__.return_value = None
        mock_db.pool = mock_pool
        return mock_db
    
    @pytest_asyncio.fixture
    async def mock_repositories(self):
        """Mock 리포지토리들"""
        return {
            'game_data_repo': AsyncMock(spec=GameDataRepository),
            'runtime_data_repo': AsyncMock(spec=RuntimeDataRepository),
            'reference_layer_repo': AsyncMock(spec=ReferenceLayerRepository)
        }
    
    @pytest_asyncio.fixture
    async def effect_carrier_manager(self, mock_db_connection, mock_repositories):
        """Effect Carrier Manager 인스턴스"""
        return EffectCarrierManager(
            mock_db_connection,
            mock_repositories['game_data_repo'],
            mock_repositories['runtime_data_repo'],
            mock_repositories['reference_layer_repo']
        )
    
    @pytest.fixture
    def sample_effect_data(self):
        """샘플 Effect Carrier 데이터"""
        return {
            'name': 'Fireball',
            'carrier_type': EffectCarrierType.SKILL,
            'effect_json': {
                'damage': 50,
                'range': 3,
                'cooldown': 5,
                'mana_cost': 20
            },
            'constraints_json': {
                'min_level': 3,
                'required_class': 'mage'
            },
            'tags': ['fire', 'damage', 'ranged']
        }
    
    @pytest.mark.asyncio
    async def test_create_effect_carrier_success(self, effect_carrier_manager, sample_effect_data):
        """Effect Carrier 생성 성공 테스트"""
        # Given
        effect_carrier_manager._save_effect_carrier_to_db = AsyncMock()
        
        # When
        result = await effect_carrier_manager.create_effect_carrier(**sample_effect_data)
        
        # Then
        assert result.success
        assert "생성 완료" in result.message
        assert isinstance(result.data, EffectCarrierData)
        assert result.data.name == sample_effect_data['name']
        assert result.data.carrier_type == sample_effect_data['carrier_type']
        assert result.data.effect_json == sample_effect_data['effect_json']
        assert result.data.constraints_json == sample_effect_data['constraints_json']
        assert result.data.tags == sample_effect_data['tags']
    
    @pytest.mark.asyncio
    async def test_create_effect_carrier_validation_error(self, effect_carrier_manager):
        """Effect Carrier 생성 검증 오류 테스트"""
        # Given
        invalid_data = {
            'name': '',  # 빈 이름
            'carrier_type': EffectCarrierType.SKILL,
            'effect_json': {}
        }
        
        # When
        result = await effect_carrier_manager.create_effect_carrier(**invalid_data)
        
        # Then
        assert not result.success
        assert "이름은 필수입니다" in result.message
    
    @pytest.mark.asyncio
    async def test_get_effect_carrier_success(self, effect_carrier_manager):
        """Effect Carrier 조회 성공 테스트"""
        # Given
        effect_id = "test-effect-id"
        sample_effect = EffectCarrierData(
            effect_id=effect_id,
            name="Test Effect",
            carrier_type=EffectCarrierType.SKILL,
            effect_json={"damage": 10}
        )
        
        effect_carrier_manager._load_effect_carrier_from_db = AsyncMock(return_value=sample_effect)
        
        # When
        result = await effect_carrier_manager.get_effect_carrier(effect_id)
        
        # Then
        assert result.success
        assert "조회 완료" in result.message
        assert isinstance(result.data, EffectCarrierData)
        assert result.data.effect_id == effect_id
    
    @pytest.mark.asyncio
    async def test_get_effect_carrier_not_found(self, effect_carrier_manager):
        """Effect Carrier 조회 실패 테스트"""
        # Given
        effect_id = "non-existent-id"
        effect_carrier_manager._load_effect_carrier_from_db = AsyncMock(return_value=None)
        
        # When
        result = await effect_carrier_manager.get_effect_carrier(effect_id)
        
        # Then
        assert not result.success
        assert "찾을 수 없습니다" in result.message
    
    @pytest.mark.asyncio
    async def test_update_effect_carrier_success(self, effect_carrier_manager):
        """Effect Carrier 수정 성공 테스트"""
        # Given
        effect_id = "test-effect-id"
        original_effect = EffectCarrierData(
            effect_id=effect_id,
            name="Original Name",
            carrier_type=EffectCarrierType.SKILL,
            effect_json={"damage": 10}
        )
        
        effect_carrier_manager.get_effect_carrier = AsyncMock(return_value=EffectCarrierResult.success_result("", original_effect))
        effect_carrier_manager._save_effect_carrier_to_db = AsyncMock()
        
        # When
        result = await effect_carrier_manager.update_effect_carrier(
            effect_id, 
            name="Updated Name",
            effect_json={"damage": 20}
        )
        
        # Then
        assert result.success
        assert "수정 완료" in result.message
        assert isinstance(result.data, EffectCarrierData)
        assert result.data.name == "Updated Name"
        assert result.data.effect_json == {"damage": 20}
    
    @pytest.mark.asyncio
    async def test_delete_effect_carrier_success(self, effect_carrier_manager):
        """Effect Carrier 삭제 성공 테스트"""
        # Given
        effect_id = "test-effect-id"
        sample_effect = EffectCarrierData(
            effect_id=effect_id,
            name="Test Effect",
            carrier_type=EffectCarrierType.SKILL,
            effect_json={"damage": 10}
        )
        
        effect_carrier_manager.get_effect_carrier = AsyncMock(return_value=EffectCarrierResult.success_result("", sample_effect))
        effect_carrier_manager._delete_effect_carrier_from_db = AsyncMock()
        
        # When
        result = await effect_carrier_manager.delete_effect_carrier(effect_id)
        
        # Then
        assert result.success
        assert "삭제 완료" in result.message
    
    @pytest.mark.asyncio
    async def test_grant_effect_to_entity_success(self, effect_carrier_manager):
        """엔티티에 Effect Carrier 부여 성공 테스트"""
        # Given
        session_id = "test-session"
        entity_id = "test-entity"
        effect_id = "test-effect"
        
        sample_effect = EffectCarrierData(
            effect_id=effect_id,
            name="Test Effect",
            carrier_type=EffectCarrierType.SKILL,
            effect_json={"damage": 10}
        )
        
        effect_carrier_manager.get_effect_carrier = AsyncMock(return_value=EffectCarrierResult.success_result("", sample_effect))
        effect_carrier_manager._save_effect_ownership_to_db = AsyncMock()
        
        # When
        result = await effect_carrier_manager.grant_effect_to_entity(session_id, entity_id, effect_id)
        
        # Then
        assert result.success
        assert "부여 완료" in result.message
    
    @pytest.mark.asyncio
    async def test_revoke_effect_from_entity_success(self, effect_carrier_manager):
        """엔티티에서 Effect Carrier 제거 성공 테스트"""
        # Given
        session_id = "test-session"
        entity_id = "test-entity"
        effect_id = "test-effect"
        
        effect_carrier_manager._delete_effect_ownership_from_db = AsyncMock()
        
        # When
        result = await effect_carrier_manager.revoke_effect_from_entity(session_id, entity_id, effect_id)
        
        # Then
        assert result.success
        assert "제거 완료" in result.message
    
    @pytest.mark.asyncio
    async def test_get_entity_effects_success(self, effect_carrier_manager):
        """엔티티의 Effect Carrier 목록 조회 성공 테스트"""
        # Given
        session_id = "test-session"
        entity_id = "test-entity"
        
        sample_ownerships = [
            EffectOwnershipData(
                session_id=session_id,
                runtime_entity_id=entity_id,
                effect_id="effect-1",
                source="quest"
            ),
            EffectOwnershipData(
                session_id=session_id,
                runtime_entity_id=entity_id,
                effect_id="effect-2",
                source="item"
            )
        ]
        
        sample_effects = [
            EffectCarrierData(
                effect_id="effect-1",
                name="Effect 1",
                carrier_type=EffectCarrierType.SKILL,
                effect_json={"damage": 10}
            ),
            EffectCarrierData(
                effect_id="effect-2",
                name="Effect 2",
                carrier_type=EffectCarrierType.BUFF,
                effect_json={"strength": 5}
            )
        ]
        
        effect_carrier_manager._load_entity_effect_ownerships = AsyncMock(return_value=sample_ownerships)
        effect_carrier_manager.get_effect_carrier = AsyncMock(side_effect=[
            EffectCarrierResult.success_result("", sample_effects[0]),
            EffectCarrierResult.success_result("", sample_effects[1])
        ])
        
        # When
        result = await effect_carrier_manager.get_entity_effects(session_id, entity_id)
        
        # Then
        assert result.success
        assert "목록 조회 완료" in result.message
        assert isinstance(result.data, list)
        assert len(result.data) == 2
    
    @pytest.mark.asyncio
    async def test_effect_carrier_data_validation(self):
        """Effect Carrier 데이터 검증 테스트"""
        # Given
        valid_data = {
            'effect_id': 'test-id',
            'name': 'Test Effect',
            'carrier_type': EffectCarrierType.SKILL,
            'effect_json': {'damage': 10},
            'constraints_json': {'min_level': 1},
            'tags': ['test']
        }
        
        # When
        effect_carrier = EffectCarrierData(**valid_data)
        
        # Then
        assert effect_carrier.effect_id == 'test-id'
        assert effect_carrier.name == 'Test Effect'
        assert effect_carrier.carrier_type == EffectCarrierType.SKILL
        assert effect_carrier.effect_json == {'damage': 10}
        assert effect_carrier.constraints_json == {'min_level': 1}
        assert effect_carrier.tags == ['test']
    
    @pytest.mark.asyncio
    async def test_effect_carrier_data_validation_error(self):
        """Effect Carrier 데이터 검증 오류 테스트"""
        # Given
        invalid_data = {
            'effect_id': 'test-id',
            'name': '',  # 빈 이름
            'carrier_type': EffectCarrierType.SKILL,
            'effect_json': 'invalid',  # 잘못된 타입
            'constraints_json': 'invalid'  # 잘못된 타입
        }
        
        # When & Then
        with pytest.raises(ValueError):
            EffectCarrierData(**invalid_data)
    
    @pytest.mark.asyncio
    async def test_effect_ownership_data_creation(self):
        """Effect Carrier 소유 관계 데이터 생성 테스트"""
        # Given
        ownership_data = {
            'session_id': 'test-session',
            'runtime_entity_id': 'test-entity',
            'effect_id': 'test-effect',
            'source': 'quest'
        }
        
        # When
        ownership = EffectOwnershipData(**ownership_data)
        
        # Then
        assert ownership.session_id == 'test-session'
        assert ownership.runtime_entity_id == 'test-entity'
        assert ownership.effect_id == 'test-effect'
        assert ownership.source == 'quest'
        assert isinstance(ownership.acquired_at, datetime)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
