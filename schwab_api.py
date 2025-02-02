from schwab.auth import client_from_login_flow, easy_client
from logger_config import setup_logger
from dotenv import load_dotenv
from alpaca_api import get_alpaca_percentages
from enum import Enum
from pprint import pp, pformat
import httpx
import math
import os

# Load environment variables from .env file
load_dotenv()

logger = setup_logger('schwab_api', 'logs/schwab.log')

class Modes(Enum):
    # Run logic but only log orders
    DEBUG = 1,
    # Run logic and send orders to broker
    LIVE = 2,
    
class ShareRounding(Enum):
    # Your typical roudning .5+ goes to 1 .5- goes to 0
    NEAREST = 1,
    # Rounds down .99 goes to 0
    DOWN = 2,

class QuoteMode(Enum):
    # Last updated price
    LASTPRICE = "lastPrice",
    # Current ask price
    ASKPRICE = "askPrice",
    # Market 
    MARKET = "mark",

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
PADDING = 500.0
# Which way to round shares
SHARE_ROUND = ShareRounding.NEAREST
# When buying which mode to use
BUY_MODE = QuoteMode.MARKET
# --------------------------------------

def create_client():
    """Simple function to create a client to use

    Returns:
        Schwab Client
    """
    return easy_client(token_path=os.getenv("TMP_TOKEN_PATH"), 
                       api_key=os.getenv("SCWAHB_API_KEY"),
                       app_secret=os.getenv("SCWAHB_SECRET_KEY"),
                       callback_url=os.getenv("CALLBACK_URL"))
    
def read_in_accounts() -> set:
        """Grabs the accounts from the env

        Returns:
            set: of Accounts
        """
        # Lets grab the accounts
        accounts = os.getenv("SCHWAB_ACCOUNT_NUMS").strip()
        # Trim accidental end commans
        if accounts[-1] == ",":
            accounts = accounts [:-1]
        # Split out into a set
        if "," in accounts:
            accounts = set(accounts.split(","))
        else:
            accounts = set(accounts)
            
        return accounts

class schwab_client:
    def __init__(self) -> None:
        self.c = create_client()

    def is_token_valid(self) -> bool:
        """Used to check if token is valid

        Returns:
            bool: True/False on if token is still valid
        """
        resp = self.c.get_account_numbers()
        
        if resp.status_code == httpx.codes.OK:
            logger.error("!!! Token was found to be active !!!")
            return True
        
        logger.info("--- Token was found to be not active ---")
        return False

    def access_to_expected_accounts(self) -> bool:
        """Used to check if expected accounts are returned

        Returns:
            bool: True/False on if expected accounts were found
        """
        
        resp = self.c.get_account_numbers()
        
        if resp.status_code != httpx.codes.OK:
            logger.error("!!! Failed to grab accounts !!!")
            return False

        # Lets grab the accounts we are expecting
        expected_accounts = read_in_accounts()
        
        ret_accounts = set()
        for account in resp.json():
            ret_accounts.add(account["accountNumber"])

        return ret_accounts == expected_accounts
            
    def get_quotes(self, symbols: set):
        """Used to collected

        Args:
            symbols (set): Set of Symbols to get quotes for
        """
        resp = self.c.get_quotes(symbols=symbols)
        
        if resp.status_code != httpx.codes.OK:
            logger.error("!!! Failed to grab Quote information !!!")
            return False
        
        return resp.json()

    def get_account_hash(self, account_num: int):
        """Used to get an accounts hash data

        Args:
            account_num (int): account num to get hash for

        Returns:
            str/None: str when found and None when not 
        """
        resp = self.c.get_account_numbers()
        
        if resp.status_code != httpx.codes.OK:
            logger.error("!!! Failed to get accounts !!!")
            return None
        
        account_hashes = resp.json()
        # Convert the List of dictionaries into a dict
        account_hashes = {account.get("accountNumber"): account.get("hashValue") for account in account_hashes}
        return account_hashes.get(account_num, None)
    
    def get_accout_details(self, account_num: int):
        """Used to get account details

        Args:
            account_num (int): account number

        Returns:
            dict/None: dictionary of account details or None
        """
        account_hash = self.get_account_hash(account_num)

        if account_hash is None:
            logger.error("!!! Failed to get account hash !!!")
            return None
        
        resp = self.c.get_account(account_hash, fields=[self.c.Account.Fields.POSITIONS])

        if resp.status_code != httpx.codes.OK:
            logger.error("!!! Failed to get account !!!")
            return None

        account_details = resp.json()
        
        return account_details
    
    def get_account_holdings(self, account_num: int):
        """Used to get the holdings of an account

        Args:
            account_num (int): account number

        Returns:
            dict/None: dictionary of holdings or None
        """
        details = self.get_accout_details(account_num)
        
        if details is None:
            return None
        pp(details)
        return details["securitiesAccount"]["positions"]
    
    def get_account_holding_value(self, account_num: int):
        """Used to collect the value of the 

        Args:
            account_num (str): hash of account to interact with
        """
        details = self.get_accout_details(account_num)
        
        if details is None:
            return None
        
        pp(details)
        
        return details["securitiesAccount"]["currentBalances"]["liquidationValue"]
    
    def get_account_trade_value(self, account_num: int):
        """Used to find how much of the account to trade with

        Args:
            account_num (int): account number

        Returns:
            int/None: int value or None if not found
        """
        account_total = self.get_account_holding_value(account_num)

        if account_total is None:
            logger.error("!!! Failed to get account hash !!!")
            return None
        
        if account_total < 1.0:
            logger.error("!!! Account has to low of a balance !!!")
            return None
        
        logger.info(f"\nAccount Total: {account_total} Trading with: {TRADE_WITH}% Padding: {PADDING}\nCalculated Trade Value: {round(account_total * (TRADE_WITH/100) - PADDING, 2)}\nCalculation: (Account Total * (Trading With/100) - Padding) Rounded to two decimals")
        return round(account_total * (TRADE_WITH/100) - PADDING, 2)

    def breakdown_account_by_quotes(self, account_num: int, percentages: dict) -> dict:
        """Used to breakout an accounts value by the percentages from Alpaca, TRADE_WITH, and PADDING

        Args:
            account_num (str): num of account to interact with
            percentages (dict): Percentage breakdown from Alpaca

        Returns:
            dict: Breakdown of the amount of each ticker to buy
        """
        logger.info(f"\n=== \nPercentages being used for breakdown \n{pformat(percentages)}\n===")
        
        total = self.get_account_trade_value(account_num)

        check_sum = 0
        for stock in percentages:
            percentages[stock] = round(total * percentages[stock]/100, 2)
            if stock != "checksum":
                check_sum += percentages[stock]
        
        logger.info(f"\n=== \n(What will be applied to Schwab account)\nBreaking down account {account_num} using account value of ${total}\nChecksum: {round(check_sum, 2)}\nBreakdown:\n{pformat(percentages)}\n===")
        
        ticker_quotes = {key for key in percentages.keys()}
        ticker_quotes.remove("checksum")
        ticker_data = self.get_quotes(ticker_quotes)
        
        buy_amounts = {}
        quotes = {}
        for stock in percentages:
            # We want to ignore the checksum
            if stock == "checksum":
                continue
            # Compile the quotes into a single dictionary for logging
            quotes[stock] = ticker_data[stock]["quote"][BUY_MODE.value[0]]
            # Based on setting we may want to round differently
            if SHARE_ROUND is ShareRounding.NEAREST:
                buy_amounts[stock] = round(percentages[stock]/quotes[stock] )
            elif SHARE_ROUND is ShareRounding.DOWN:
                buy_amounts[stock] = math.floor(percentages[stock]/quotes[stock] )
        
        rounding = "Nearest" if SHARE_ROUND is ShareRounding.NEAREST else "Down"
        
        logger.info(f"\n=== Quotes used: \n{pformat(quotes)} \n===")
        logger.info(f"\n=== Ticker buy amounts based on above Totals/Quotes w/ {rounding} Rounding \n{pformat(buy_amounts)}\n===")
        
        return buy_amounts

    def liquidate_holdings(self, account_num: int):
        """Used to liquidate the account holdings

        Args:
            account_num (int): account number

        Returns:
            list/None: list of orders created to sell/None if in debug mode
        """
        holdings = self.get_account_holdings(account_num)
        
        if holdings is None:
            return False
        
        sell = {}
        for holding in holdings:
            sell[holding["instrument"]["symbol"]] = holding["instrument"]["longQuantity"]
            
        logger.info(f"\n===\n Holdings being liquidated: {pformat(sell)}\n===")
        
        if MODE is Modes.LIVE:
            orders = []
            for ticker, quantity in sell.items():
                orders.append(self.c.place_order(self.c.orders.equities.equity_sell_market(symbol=ticker, quantity=quantity)))
            
            logger.info(f"\n===\n Orders: \n{pformat(orders)}\n===")
        
            return orders
        else:
            return None

    def check_orders_for_completion(self, account_num: str, orders: list):
        """Used to check for orders

        Args:
            account_hash (str): hash of account to interact with
        """
        account_hash = self.get_account_hash(account_num)
        
        if account_hash is None:
            return False
        
        order_details = []
        for order in orders:
            order_details.append(self.c.get_order(order, account_hash))
        
        for order in order_details:
            if order["status"] != "FILLED":
                return False
            
        return True

    def submit_orders(self, account_num: int, orders: list):
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

if __name__ == '__main__':
    # Used for Testing
    schwab_conn = schwab_client()
    # TODO: Remove
    # print(schwab_conn.get_account_trade_value("65992549"))
    print(schwab_conn.get_account_holdings("65992549"))
    # schwab_conn.breakdown_account_by_quotes("65992549", get_alpaca_percentages()["percentages"])
    # Used to fetch a token
    # client_from_login_flow(api_key=os.getenv("SCWAHB_API_KEY"), app_secret=os.getenv("SCWAHB_SECRET_KEY"),callback_url=os.getenv("CALLBACK_URL"), token_path=os.getenv("TMP_TOKEN_PATH"))