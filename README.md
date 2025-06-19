# Automated-Stock-Trading-Pipeline

An automated trading pipeline that integrates TradingView alerts with Robinhood, with position sizing determined by the Kelly Criterion. Designed for automated stock and crypto trading.

---

## How It Works

1. `EMA_TRIX.txt` contains a Pine Script v5 strategy based on two EMA lines and the TRIX indicator.
2. TradingView sends alerts via webhook to a local Flask server.
3. The Flask app listens on the `/webhook` endpoint.
4. The bot extracts signal type (buy or sell), ticker symbol, and timestamp.
5. The position size is calculated using the Kelly Criterion.
6. The bot places fractional buy/sell orders using the Robinhood API via the `robin_stocks` library.

---

## Features

- Receives webhook alerts from TradingView
- Supports both stock and crypto trading
- Implements fixed-risk position sizing with the Kelly Criterion
- Places fractional orders automatically on Robinhood
- Logs all actions and errors for debugging and auditing

---

## Requirements

- Python 3.7+
- A valid Robinhood account
- `robin_stocks` Python library
- Flask
- Ngrok (for exposing local server to webhook)

---

## Installation

1. Clone this repository:

    ```bash
    git clone https://github.com/yourusername/Automated-Stock-Trading-Pipeline.git
    cd Automated-Stock-Trading-Pipeline
    ```

2. Create the conda environment:

    ```bash
    conda env create -f environment.yml
    conda activate trading
    ```

3. (Optional) Run the provided `Start_bot.bat` script to launch the webhook server:

    ```bat
    rem Launch Flask server and webhook tunnel
    call C:\Users\YourName\anaconda3\Scripts\activate.bat trading
    cd /d "F:\Coding"
    start cmd /k python Trading_With_Crypto.py
    start cmd /k ngrok http --url=mighty-cobra-rationally.ngrok-free.app 5000
    ```

---

## Alert Format from TradingView

Use this JSON format in TradingView alerts
Example:

```json
{
  "ticker": "AAPL",
  "signal": "buy",
}
```
---

## Project Structure

| File               | Description                                 |
|--------------------|---------------------------------------------|
| Trading_With_Crypto.py | Main trading bot and Flask server         |
| Trading.py         | Auxiliary trading logic                     |
| EMA_TRIX.txt       | Pinescript code used in TradingView for trading strategies|
| environment.yml    | Environment dependencies for Conda          |
| Start_bot.bat      | Script to start Flask and webhook tunnel    |

---

## Disclaimer

This project is intended for educational purposes only, and it is not financial advice.
Trading financial instruments involves risk. Use at your own discretion. 
