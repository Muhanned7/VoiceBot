import sys
from loguru import logger

def setup_logger(log_level: str = "INFO") -> None:
    logger.remove()
    
    logger.add(
        sys.stdout,
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{line} | {message}"
    )

def get_logger(name:str):
    return logger.bind(name=name)