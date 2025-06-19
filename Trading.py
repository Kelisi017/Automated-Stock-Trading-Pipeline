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
ALLOWED_TICKERS = ["NVDA", "TSLA","TEM","AMD","DJT","ASTS"]

# Define dollar risk factors for each ticker
DOLLAR_RISK_FACTORS = {
    "NVDA": 107,
    "TSLA": 122,
    "TEM" : 54,
    "AMD": 48.2,
    "DJT":35.63,
    "ASTS":35,
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
        if ticker not in ALLOWED_TICKERS:
            return jsonify({"status": "error", "message": f"Ticker {ticker} is not allowed for trading"}), 400
        
        if signal in ['buy', 'sell']:
            execute_trade(signal, ticker)
        else:
            return jsonify({"status": "error", "message": "Invalid signal"}), 400
    else:
        missing_keys = [k for k in ['signal', 'ticker'] if not data.get(k)]
        logging.error(f"Error: Missing key(s): {', '.join(missing_keys)}")
        return jsonify({"status": "error", "message": f"Missing key(s): {', '.join(missing_keys)}"}), 400

    return jsonify({"status": "success"})

def execute_trade(action, ticker):
    # Get the current price of the stock
    # try: 
    #     r.login('l1277435756@gmail.com',"1277435756", store_session = True)
    # except Exception as e:
    #     logging.error(f"Login failed:{e}")
    #     return

    try:
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
        # Position sizing formula for buying shares, with specific dollar risk factor for each ticker
        dollar_risk_factor = DOLLAR_RISK_FACTORS.get(ticker, 100)  # Default risk factor of 100 if not specified

        # Adjust position size based on dollar risk factor and risk percentage
        num_shares = (dollar_risk_factor * 0.083) / (current_price - (current_price * 0.97))
        num_shares = round(num_shares,4)  # Convert to integer shares for Robinhood

        if num_shares > 0:
            r.orders.order_buy_fractional_by_quantity(ticker, num_shares)
            logging.info(f"Buy order placed for {num_shares} shares of {ticker} at price {current_price}")

        else:
            logging.info(f"Position size for {ticker} is too small to execute a buy order.")

    elif action == "sell":
        # Sell all shares of the current stock
        try:
            # Get the current holdings for the ticker
            positions = r.account.build_holdings()
            if ticker in positions:
                current_holdings = float(positions[ticker]['quantity'])
                if current_holdings > 0:
                    response = r.orders.order_sell_fractional_by_quantity(ticker, current_holdings)
                    print("Sell order response:", response)
                    logging.info(f"Sell order placed for all {current_holdings} shares of {ticker}")
                    if response and "id" in response:
                        logging.info(f"Successfully placed sell order for {current_holdings} shares of {ticker}")
                    else:
                        logging.warning("Sell order may not have been successfully placed")
                else:
                    logging.info(f"No shares to sell for {ticker}")
            else:
                logging.info(f"No holdings found for {ticker} to sell.")
        except Exception as e:
            logging.error(f"Error executing sell order for {ticker}: {e}")
    else:
        logging.info(f"No trade executed for {ticker}. Invalid action.")

if __name__ == '__main__':
    app.run(port=5000)
