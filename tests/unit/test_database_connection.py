"""
?°ì´?°ë² ?´ìŠ¤ ?°ê²° ?ŒìŠ¤??"""
import pytest
from database.connection import DatabaseConnection
from app.config.app_config import get_db_settings


class TestDatabaseConnection:
    """?°ì´?°ë² ?´ìŠ¤ ?°ê²° ?ŒìŠ¤???´ë˜??""
    
    @pytest.fixture
    def db_connection(self):
        """?°ì´?°ë² ?´ìŠ¤ ?°ê²° ?¸ìŠ¤?´ìŠ¤"""
        return DatabaseConnection()
    
    def test_connection_initialization(self, db_connection):
        """?°ê²° ì´ˆê¸°???ŒìŠ¤??""
        # Given & When
        # DatabaseConnection ?¸ìŠ¤?´ìŠ¤ ?ì„±
        db_settings = get_db_settings()
        
        # Then
        assert db_connection.host == db_settings.host
        assert db_connection.port == db_settings.port
        assert db_connection.user == db_settings.user
        assert db_connection.database == db_settings.database
        assert db_connection.password == db_settings.password
    
    def test_settings_integration(self):
        """?¤ì • ?µí•© ?ŒìŠ¤??""
        # Given & When
        db_connection = DatabaseConnection()
        db_settings = get_db_settings()
        
        # Then
        assert db_connection.host == db_settings.host
        assert db_connection.port == db_settings.port
        assert db_connection.user == db_settings.user
        assert db_connection.password == db_settings.password
        assert db_connection.database == db_settings.database
    
    def test_singleton_pattern(self):
        """?±ê????¨í„´ ?ŒìŠ¤??""
        # Given & When
        db1 = DatabaseConnection()
        db2 = DatabaseConnection()
        
        # Then
        assert db1 is db2
    
    def test_connection_parameters(self, db_connection):
        """?°ê²° ë§¤ê°œë³€???ŒìŠ¤??""
        # Given & When
        # DatabaseConnection ?¸ìŠ¤?´ìŠ¤ ?ì„±
        
        # Then
        assert isinstance(db_connection.host, str)
        assert isinstance(db_connection.port, int)
        assert isinstance(db_connection.user, str)
        assert isinstance(db_connection.password, str)
        assert isinstance(db_connection.database, str)
        
        # ê¸°ë³¸ê°?ê²€ì¦?        assert db_connection.host == "localhost"
        assert db_connection.port == 5432
        assert db_connection.user == "postgres"
        assert db_connection.database == "rpg_engine"
