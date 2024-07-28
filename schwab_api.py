from schwab.auth import client_from_manual_flow
from logger_config import setup_logger
from dotenv import load_dotenv
import schwab.client as Client
from enum import Enum

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
# Percentage of account equity to trade with (i.e. 1%-100%)
TRADE_WITH = 100
# In the above example, using 90% with a 500$ padding:
#  Account equity = $100,000 * .90 = $90,000 - $500 = $89,500.  
#  This is the amount that will be used as the starting point for all calculations when determining how many shares to purchase, etc.  
#  This allows for some slippage, etc.
# Minimum value for padding is $500
PADDING = 500
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
    # Client.get_quotes()
    pass

def get_account_total_value(account_hash: str):
    """Used to collect the value of the 

    Args:
        account_hash (str): hash of account to interact with
    """
    # Client.get_account()
    pass

def breakdown_account_by_quotes(account_hash: str, percentages: dict) -> dict:
    """Used to breakout an accounts value by the percentages from Alpaca, TRADE_WITH, and PADDING

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
    # Client.get_orders_for_account()
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
        # Client.place_order()
        # Log the orders submitted for sells
        # Execute sell orders
        # Log that we are checking for sell orders
        # Once we see all sell orders are executed we exit.
        # Check for open sell orders every 1 second until the API indicates that no outstanding sell orders exist.  
        # Abort this check after ~5 seconds (in the event that there is an issue with the response from Schwab).
        # Log the buy orders
        # Execute buy orders
        pass
    else:
        pass

