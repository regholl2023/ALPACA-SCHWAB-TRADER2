from alpaca_api import check_for_change
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

# Copy Trade Variables
PERIOD=1

# Execute the script
if __name__ == '__main__':
    while True:
        time.sleep(PERIOD)
        if check_for_change():
            print("Change Occured!")
