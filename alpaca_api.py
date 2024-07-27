from alpaca.trading.client import TradingClient
from logger_config import setup_logger
from dotenv import load_dotenv
from pprint import pformat
import yaml
import os

# Load environment variables from .env file
load_dotenv()

PAPER = False

logger = setup_logger('alpaca_api', 'logs/alpaca.log')

def get_alpaca_percentages():
    """Used to collect the position percentages

    Args:
        paper (bool, optional): Dictate if paper account or not. Defaults to False.

    Returns:
        dict: Dict of assets and their percent of the portfolio
    """
    trading_client = TradingClient(os.getenv('ALPACA_API_KEY'), os.getenv('ALPACA_SECRET_KEY'), paper=PAPER)
    holdings = trading_client.get_all_positions()
    # Collect the Assets
    assets = {}
    total_per = 0
    for asset in holdings:
        rounded_qty = round(float(asset.qty))
        total_per += rounded_qty
        assets.update({asset.symbol: rounded_qty})
    # Convert to percentages
    percentages = {}
    for asset, qty in assets.items():
        percentages.update({asset: round((qty/total_per)*100)})

    return percentages

def check_for_change():
    """Handles checking if a change has occured compared

    Returns:
        bool: If Changes occured True, else False
    """
    cur_positions = get_alpaca_percentages()
    
    saved_pos_file = "./saved_pos.yaml"
    
    if not os.path.exists(saved_pos_file):
        with open(saved_pos_file, 'w') as file:
            yaml.dump(cur_positions, file, default_flow_style=False)
    else:
        with open(saved_pos_file, 'r') as file:
            saved_pos = yaml.safe_load(file)
        
        if cur_positions != saved_pos:
            logger.info(f"===\nOld: \n{pformat(saved_pos)}\nNew: \n{pformat(cur_positions)}\n===")
            return True
        
    return False
    
