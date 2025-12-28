from typing import Dict, Any, Optional
from pathlib import Path
import os
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class DatabaseSettings(BaseSettings):
    """데이터베이스 설정"""
    host: str = Field(default="localhost", alias="DB_HOST")
    port: int = Field(default=5432, alias="DB_PORT")
    user: str = Field(default="postgres", alias="DB_USER")
    password: str = Field(default="", alias="DB_PASSWORD")
    database: str = Field(default="rpg_engine", alias="DB_NAME")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "populate_by_name": True
    }

# 전역 설정 인스턴스 (지연 초기화)
db_settings = None

def get_db_settings():
    """데이터베이스 설정을 반환합니다 (지연 초기화)"""
    global db_settings
    if db_settings is None:
        db_settings = DatabaseSettings()
    return db_settings

# 기존 호환성을 위한 설정
def get_database_config():
    """데이터베이스 설정을 딕셔너리로 반환합니다"""
    settings = get_db_settings()
    return {
        "host": settings.host,
        "port": settings.port,
        "user": settings.user,
        "password": settings.password,
        "database": settings.database
    }

# 게임 기본 설정
GAME_CONFIG = {
    "max_players_per_session": 1,
    "save_interval_seconds": 300,  # 5분
    "session_timeout_minutes": 60,  # 1시간
    "default_inventory_size": 20
}

# 로그 디렉토리 설정
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# 로깅 설정
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s"
        },
        "scenario": {
            "format": "%(asctime)s [SCENARIO] %(message)s"
        },
        "gui": {
            "format": "%(asctime)s [GUI] %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "level": "INFO",
            "formatter": "detailed",
            "class": "logging.FileHandler",
            "filename": str(LOG_DIR / "game.log"),
            "mode": "a",
        },
        "scenario_file": {
            "level": "INFO",
            "formatter": "scenario",
            "class": "logging.FileHandler",
            "filename": str(LOG_DIR / "scenario.log"),
            "mode": "a",
        },
        "gui_file": {
            "level": "INFO",
            "formatter": "gui",
            "class": "logging.FileHandler",
            "filename": str(LOG_DIR / "gui.log"),
            "mode": "a",
        },
        "error_file": {
            "level": "ERROR",
            "formatter": "detailed",
            "class": "logging.FileHandler",
            "filename": str(LOG_DIR / "error.log"),
            "mode": "a",
        }
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["console", "file", "error_file"],
            "level": "INFO",
            "propagate": True
        },
        "app.core.scenario_executor": {
            "handlers": ["console", "scenario_file", "error_file"],
            "level": "INFO",
            "propagate": False
        },
        "app.core.scenario_loader": {
            "handlers": ["console", "scenario_file", "error_file"],
            "level": "INFO",
            "propagate": False
        },
        "app.ui": {
            "handlers": ["console", "gui_file", "error_file"],
            "level": "INFO",
            "propagate": False
        },
        "app.core.game_manager": {
            "handlers": ["console", "file", "error_file"],
            "level": "INFO",
            "propagate": False
        },
        "app.game_session": {
            "handlers": ["console", "file", "error_file"],
            "level": "INFO",
            "propagate": False
        },
        "database": {
            "handlers": ["console", "file", "error_file"],
            "level": "INFO",
            "propagate": False
        }
    }
} 