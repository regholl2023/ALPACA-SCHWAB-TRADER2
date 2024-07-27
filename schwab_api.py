from logger_config import setup_logger
from enum import Enum

logger = setup_logger('schwab_api', 'logs/schwab.log')

class Modes(Enum):
    # Run logic but only log orders
    DEBUG = 1,
    # Run logic and send orders to broker
    LIVE = 2,
    # Clear out everything
    LIQUIDATE = 3,
