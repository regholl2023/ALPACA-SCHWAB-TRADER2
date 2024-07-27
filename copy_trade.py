from alpaca_api import check_for_change
from logger_config import setup_logger
from dotenv import load_dotenv
import time

logger = setup_logger('copy_trade', 'logs/copy_trade.log')

# Load environment variables from .env file
load_dotenv()

# Copy Trade Variables
PERIOD=1

# Execute the script
if __name__ == '__main__':
    while True:
        time.sleep(PERIOD)
        
        # We are just going to check for changes and then copy trade instead of
        if check_for_change():
            print("Change Occured!")
