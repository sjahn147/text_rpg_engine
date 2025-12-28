import logging
import logging.config
from pathlib import Path
from app.config.app_config import LOGGING_CONFIG

def setup_logging():
    """로깅 설정을 초기화합니다."""
    # 로그 디렉토리 생성
    log_file = Path(LOGGING_CONFIG["handlers"]["file"]["filename"])
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 로깅 설정 적용
    logging.config.dictConfig(LOGGING_CONFIG)

def get_logger(name: str) -> logging.Logger:
    """지정된 이름의 로거를 반환합니다."""
    return logging.getLogger(name)

# 기본 로거 설정
setup_logging()

# 전역 로거 인스턴스
logger = get_logger(__name__) 