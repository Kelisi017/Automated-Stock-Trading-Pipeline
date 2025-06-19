# Automated-Stock-Trading-Pipeline
Automated trading pipeline integrating TradingView alerts and Robinhood API, with position sizing based on the Kelly Criterion. 

## How It Works: 
EMA_TRIX.txt is a version 5 pinescript code that executes trading strategies based on two EMA lines and TRIX indicator. 
TradingView sends webhook alerts triggered by EMA_TRIX pine script strategies. 
A Flask server receives those alerts at a specified /webhook endpoint. 
The bot extracts signal type (either buy or sell), ticker, and timestamp. 
The bot calculates position size based on Kelly Criterion and executes trades on Robinhood. 
