# logger_config.py
import logging
from pathlib import Path

def setup_logger(logger_name, log_file, level=logging.INFO):
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    handler = logging.FileHandler(log_file)
    handler.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
