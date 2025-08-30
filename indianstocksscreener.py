import pandas as pd
import numpy as np
import yfinance as yf
import talib as ta
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt
from datetime import date
today=date.today()

indian_stocks = pd.read_csv("C:/Users/mansh/EQUITY_L.csv")

tickers = indian_stocks['SYMBOL'].tolist()

yf_tickers = [f"{ticker}.NS" for ticker in tickers]

data = yf.download(yf_tickers[:10], start="2024-01-01", end=today, group_by='ticker' ,auto_adjust=True,
    threads=True)
print(data)
df=pd.DataFrame(data)
print(df)

data_close = data.loc[:, (slice(None), 'Close')]

print(data_close)

data_open=data.loc[:,(slice(None),'Open')]
print(data_open)

data_high=data.loc[:,(slice(None),'High')]
print(data_high)

data_low=data.loc[:,(slice(None),'Low')]
print(data_low)



data_volume=data.loc[:,(slice(None),'Volume')]
print(data_volume)

rsi_df = pd.DataFrame(index=data.index)


for ticker in yf_tickers[:10]:
    
    close_prices = data.loc[:, (ticker, 'Close')]
  
    rsi_df[ticker] = ta.RSI(close_prices.values, timeperiod=14)


for ticker in yf_tickers[:10]:
    data[(ticker, 'RSI')] = rsi_df[ticker]

print(data)

data_rsi=data.loc[:,(slice(None),'RSI')]
print(data_rsi)

plt.plot(data_rsi)
plt.show()

sma_50_df = pd.DataFrame(index=data.index)

# Fix 2: Initialize sma_50 dictionary
sma_50 = {}

for ticker in yf_tickers[:10]:
    close_prices = data.loc[:, (ticker, 'Close')]
    # Fix 3: Use close_prices.values directly instead of trying to access it as a column
    sma_50[ticker] = pd.Series(close_prices.values).rolling(window=50).mean().values

for ticker in yf_tickers[:10]:
    data[(ticker, 'SMA_50')] = sma_50[ticker]
    
print(data)

sma_50_prices=data.loc[:,(slice(None),'SMA_50')]
print(sma_50_prices)

sma_150_df=pd.DataFrame(index=data.index)
sma_150={}
for ticker in yf_tickers[:10]:
    close_prices = data.loc[:, (ticker, 'Close')]
    sma_150[ticker]=pd.Series(close_prices.values).rolling(window=150).mean().values
    
for ticker in yf_tickers[:10]:  # Fixed indentation - this was inside the previous loop
    data[(ticker,'SMA_150')]=sma_150[ticker]
    
print(data)  # Fixed indentation - this was inside the loop

sma_150_prices=data.loc[:,(slice(None),'SMA_150')]
print(sma_150_prices)



latest_rsi=data_rsi.iloc[-1]
print(latest_rsi)

latest_sma_50=sma_50_prices.iloc[-1]
print(latest_sma_50)

latest_sma_150=sma_150_prices.iloc[-1]
print(latest_sma_150)

latest_close_1=data_close.iloc[-1]
print(latest_close_1)

def find_signals(yf_tickers):
    signals = []
    
    for ticker in yf_tickers[:10]:  # Iterate through tickers
        try:
            # Get the latest values for this ticker
            ticker_rsi = latest_rsi[ticker] if ticker in latest_rsi else None
            ticker_sma_50 = latest_sma_50[ticker]['SMA_50'] if ticker in latest_sma_50 else None
            ticker_sma_150 = latest_sma_150[ticker]['SMA_150'] if ticker in latest_sma_150 else None
            
            # Skip this ticker if any required data is missing
            if ticker_rsi is None or ticker_sma_50 is None or ticker_sma_150 is None:
                continue
            
            # Convert Series to scalar values if needed
            if hasattr(ticker_rsi, 'item'):
                ticker_rsi = ticker_rsi.item()
            if hasattr(ticker_sma_50, 'item'):
                ticker_sma_50 = ticker_sma_50.item()
            if hasattr(ticker_sma_150, 'item'):
                ticker_sma_150 = ticker_sma_150.item()
                
            bullish_signal = False
            # Now comparing scalar values, not Series
            if ticker_sma_50 > ticker_sma_150:
                bullish_signal = True
            if ticker_rsi < 30 and ticker_sma_50 > ticker_sma_150:
                bullish_signal = True
         
            bearish_signal = False
            if ticker_sma_50 < ticker_sma_150:
                bearish_signal = True                      
            if ticker_rsi > 70 and ticker_sma_50 < ticker_sma_150:
                bearish_signal = True
                
            if bullish_signal and not bearish_signal:
                signals.append({'ticker': ticker, 'signal': 'Bullish', 'RSI': ticker_rsi, 'MA50': ticker_sma_50, 'MA150': ticker_sma_150})
            elif bearish_signal and not bullish_signal:
                signals.append({'ticker': ticker, 'signal': 'Bearish', 'RSI': ticker_rsi, 'MA50': ticker_sma_50, 'MA150': ticker_sma_150})
            else:
                signals.append({'ticker': ticker, 'signal': 'Neutral', 'RSI': ticker_rsi, 'MA50': ticker_sma_50, 'MA150': ticker_sma_150})
        except Exception as e:
            # Skip this ticker if there's any error
            print(f"Error processing ticker {ticker}: {e}")
            continue

    return pd.DataFrame(signals) 

results = find_signals(yf_tickers)

print(results)