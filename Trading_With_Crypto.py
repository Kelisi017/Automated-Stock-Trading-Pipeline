from flask import Flask, request, jsonify
import robin_stocks.robinhood as r
import logging
import os

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Login to Robinhood
r.login('l1277435756@gmail.com', '1277435756', store_session=True)

# Define allowed tickers for trading
ALLOWED_TICKERS = ["NVDA", "TSLA", "TEM", "AMD", "ASTS","NFLX"]
ALLOWED_CRYPTOS = ["DOGEUSD", "BTC", "ETHUSD","DOGE","BCH",]

# Define dollar risk factors for each ticker
DOLLAR_RISK_FACTORS = {
    "NVDA": 107,
    "TSLA": 122,
    "TEM": 54,
    "AMD": 48.2,
    "ASTS": 35,
    "DOGEUSD": 111.63,
    "DOGE": 111.63,
    "BTC": 60.82,
    "ETHUSD": 18.21,
    "NFLX":135,
    "BCH":100,
}

@app.route('/')
def home():
    return "Welcome to the Flask Webhook Application with Position Sizing!"

@app.route('/webhook', methods=['POST'])
def webhook():
    if not request.is_json:
        logging.error("Error: Request is not in JSON format.")
        return jsonify({"status": "error", "message": "Invalid JSON data"}), 400

    data = request.json
    logging.info(f"Received data: {data}")

    # Extract 'signal' and 'ticker' from the received data
    signal = data.get('signal')
    ticker = data.get('ticker')
    
    # Check if 'signal' and 'ticker' are provided and ticker is allowed
    if signal and ticker:
        if ticker in ALLOWED_TICKERS:
            execute_trade(signal, ticker, is_crypto=False)
        elif ticker in ALLOWED_CRYPTOS:
            execute_trade(signal, ticker, is_crypto=True)
        else:
            return jsonify({"status": "error", "message": f"Ticker {ticker} is not allowed for trading"}), 400
    else:
        missing_keys = [k for k in ['signal', 'ticker'] if not data.get(k)]
        logging.error(f"Error: Missing key(s): {', '.join(missing_keys)}")
        return jsonify({"status": "error", "message": f"Missing key(s): {', '.join(missing_keys)}"}), 400

    return jsonify({"status": "success"})

def execute_trade(action, ticker, is_crypto):
    try:
        # Get current price
        if is_crypto:
            current_price = float(r.crypto.get_crypto_quote(ticker)['mark_price'])
        else:
            current_price = float(r.stocks.get_latest_price(ticker)[0])
        logging.info(f"Current price of {ticker} is {current_price}")
    except Exception as e:
        logging.error(f"Error fetching current price for {ticker}: {e}")
        return

    # Retrieve total account balance
    try:
        account_balance = float(r.account.build_user_profile()['cash'])
        logging.info(f"Account balance is {account_balance}")
    except Exception as e:
        logging.error(f"Error fetching account balance: {e}")
        return

    if action == "buy":
        # Position sizing formula for buying shares/crypto
        dollar_risk_factor = DOLLAR_RISK_FACTORS.get(ticker, 100)  # Default risk factor
        num_shares = (dollar_risk_factor * 0.083) / (current_price - (current_price * 0.97))
        num_shares = round(num_shares,4)
        if num_shares > 0:
            try:
                if is_crypto:
                    # Crypto trading: Fractional buy
                    buy_crypto  =r.orders.order_buy_crypto_by_quantity(ticker, num_shares)
                    print(buy_crypto)
                    logging.info(f"Buy order placed for {num_shares} units of {ticker} at price {current_price}")
                else:
                    # Stock trading: Fractional buy
                    r.orders.order_buy_fractional_by_quantity(ticker, num_shares)
                    logging.info(f"Buy order placed for {num_shares} shares of {ticker} at price {current_price}")
            except Exception as e:
                logging.error(f"Error executing buy order for {ticker}: {e}")
        else:
            logging.info(f"Position size for {ticker} is too small to execute a buy order.")

    elif action == "sell":
        try:
            if is_crypto:
                # Sell all crypto
                positions = r.crypto.get_crypto_positions()
                for position in positions:
                    if position['currency']['code'] == ticker:
                        current_holdings = float(position['quantity_available'])
                        if current_holdings > 0:
                            r.orders.order_sell_crypto_by_quantity(ticker, current_holdings)
                            logging.info(f"Sell order placed for all {current_holdings} units of {ticker}")
                        else:
                            logging.info(f"No crypto holdings to sell for {ticker}")
                        break
                else:
                    logging.info(f"No crypto holdings found for {ticker} to sell.")
            else:
                # Sell all stocks
                positions = r.account.build_holdings()
                if ticker in positions:
                    current_holdings = float(positions[ticker]['quantity'])
                    if current_holdings > 0:
                        r.orders.order_sell_fractional_by_quantity(ticker, current_holdings)
                        logging.info(f"Sell order placed for all {current_holdings} shares of {ticker}")
                    else:
                        logging.info(f"No shares to sell for {ticker}")
                else:
                    logging.info(f"No stock holdings found for {ticker} to sell.")
        except Exception as e:
            logging.error(f"Error executing sell order for {ticker}: {e}")
    else:
        logging.info(f"No trade executed for {ticker}. Invalid action.")

if __name__ == '__main__':
    app.run(port=5000)
