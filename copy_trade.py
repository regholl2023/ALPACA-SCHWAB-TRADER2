from schwab_api import breakdown_account_by_quotes, submit_orders, is_token_valid
from alpaca_api import check_for_change, get_alpaca_percentages
from logger_config import setup_logger
from dotenv import load_dotenv
import time
import os

logger = setup_logger('copy_trade', 'logs/copy_trade.log')

# Load environment variables from .env file
load_dotenv()

# --------------------------------------
# How often we want to check for changes
PERIOD = 1
# --------------------------------------

def execute_trades_across_accounts(percentages: dict) -> bool:
    """Will execute trades across all selected accounts

    Args:
        percentages (dict): Alpaca percentages

    Returns:
        bool: True if Executed successfully, False if not
    """
    
    accounts = os.getenv('SCHWAB_ACCOUNT_NUMS')
    
    # Let split out the accounts or put a single one into a list
    if "," in accounts:
        accounts = accounts.split(",")
    else:
        accounts = [accounts]
        
    # Iterate over all the accounts we selected and execute trades
    for account in accounts:
        pass
    
    return False

# How we run the copy trade method
if __name__ == '__main__':
    while True:
        time.sleep(PERIOD)
        
        if is_token_valid is False:
            # If the token is invalid lets get into an infinite loop of notifications
            while True:
                logger.error("\n!!! Invalid Token !!!\n")
                # Lets send an Email/SMS that the token is Invalid 
                pass
            
        # We are just going to check for changes and then copy trade instead of
        if check_for_change():
            logger.info("\n=== Change Detected ===\n")
            # Either sleep for a period or we check that all orders on Alpaca are done
            output = execute_trades_across_accounts(get_alpaca_percentages())
            
            if output is True:
                logger.info("\n=== Trading Completed Successfully ===\n")
                # Nothing else to do lets go back to checking for changes
                continue
            else:
                # Lets get into a lock so we dont trade anyfurther
                while True:
                    logger.error("\n!!! Trading FAILED !!!\n")
                    # Lets send an Email/SMS that a trade failure occured 
                    pass
            