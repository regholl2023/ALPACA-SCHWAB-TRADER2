from schwab.auth import client_from_manual_flow
from logger_config import setup_logger
from dotenv import load_dotenv
from enum import Enum
import schwab.client as Client

# Load environment variables from .env file
load_dotenv()

logger = setup_logger('schwab_api', 'logs/schwab.log')


class Modes(Enum):
    # Run logic but only log orders
    DEBUG = 1,
    # Run logic and send orders to broker
    LIVE = 2,
    
# --------------------------------------
# Used to dictate if orders are real or not
MODE = Modes.DEBUG
# --------------------------------------

def is_token_valid() -> bool:
    """Used to check if token is valid

    Returns:
        bool: True/False on if token is still valid
    """
    pass

def get_quotes(symbols: list):
    """Used to collected

    Args:
        symbols (list): List of Symbols to get quotes for
    """
    Client.get_quotes()
    pass

def get_account_total_value(account_hash: str):
    """Used to collect the value of the 

    Args:
        account_hash (str): hash of account to interact with
    """
    Client.get_account()
    pass

def breakdown_account_by_quotes(account_hash: str, percentages: dict) -> dict:
    """Used to breakout an accounts value by the percentages from Alpaca

    Args:
        account_hash (str): hash of account to interact with
        percentages (dict): Percentage breakdown from Alpaca

    Returns:
        dict: Breakdown of the amount of each ticker to buy
    """
    pass

def check_orders(account_hash: str):
    """Used to check for orders

    Args:
        account_hash (str): hash of account to interact with
    """
    Client.get_orders_for_account()
    pass

def submit_orders(account_hash: str, orders: list):
    """Submit orders

    Args:
        account_hash (str): hash of account to interact with
        orders (list): List of orders to submit
    """
    
    if MODE is Modes.DEBUG:
        pass
    elif MODE is Modes.LIVE:
        Client.place_order()
    else:
        pass

