from alpaca.trading.client import TradingClient
from logger_config import setup_logger
from dotenv import load_dotenv
from pprint import pp, pformat
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
        rounded_qty = round(float(asset.qty), 2)
        total_per += rounded_qty
        assets.update({asset.symbol: {"rounded_qty": rounded_qty,
                                      "qty": float(asset.qty)}})
    
    # Convert to percentages
    percentages = {}
    per_checksum = 0
    for asset, qty in assets.items():
        amount = round((qty["rounded_qty"]/total_per)*100, 2)
        per_checksum += amount
        percentages.update({asset: amount})

    # Lets validate that we have the correct percentage
    if per_checksum < 99:
        raise Exception("Invalid Checksum")
    
    percentages.update({"checksum": per_checksum})

    return {"percentages": percentages,
            "assets": assets}

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
            logger.info(f"\n===\n!!! Changes Detected !!!\nOld Holdings: \n{pformat(saved_pos)}\nNew Holdings: \n{pformat(cur_positions)}\n===")
            return True
        
    return False
    
if __name__ == '__main__':
    pp(get_alpaca_percentages())