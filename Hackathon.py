#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 17:47:23 2022

@author: noahakesson
"""

import linchackathon as lh
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.finance import candlestick2_ohlc as ohlc
import matplotlib.ticker as ticker
from datetime import datetime

lh.init("1c0c7bca-53b8-43d7-aa08-3fa488f20e91")
#%%

tickers = lh.getTickers()

#%% Main code to run everything

def main():
    while True:
        for ticker in tickers:
            stock = lh.getStockHistory(ticker, 90)
            stock = getmidprices(stock)
            signal = strategy(stock, ticker)
            execution(ticker,signal)

#%% Functions

def getmidprices(indata:pd.DataFrame):
    indata['Open'] = (indata.askOpen + indata.bidOpen)/2
    indata['Low'] = (indata.askLow + indata.bidLow)/2
    indata['Close'] = (indata.askClose + indata.bidClose)/2
    indata['Volume'] = (indata.askVolume + indata.bidVolume)/2
    return indata

def execution(ticker, signals, nbrshares):
    print(f"\t> Checking signals for {ticker}: {datetime.now()}")

    # kolla om marknad öppen
    if lh.getStock(ticker)["askVolume"] > 0:
        portfolio = lh.getPortfolio()

        amount = [e["amount"] for e in portfolio
                  if e["symbol"] == ticker][0] if \
            len([e["amount"] for e in portfolio
                 if e["symbol"] == ticker]) > 0 else 0

        # sälj om du har
        if amount > 0:

            # You own the stock
            # Check if you have a sell signal
            if signals < 0:
                lh.sellStock(ticker, nbrshares)
                print(f"\t> Sold {amount} of {ticker} for",
                      f"{lh.getStock(ticker)['askClose']}")
                print(f"\t> Time {lh.getStock(ticker)['time']}")

        # Buy if you have a buy signal
        elif signals > 0:
            price = lh.getStock(ticker)["bidClose"]
            total_value = lh.getSaldo() +\
                (sum([e["totalValue"] for e in lh.getPortfolio()])
                 if len(lh.getPortfolio()) > 0 else 0)
            amount = int((total_value * 0.1) / price)
            lh.buyStock(ticker, amount)
            print(f"\t> Bought {amount} of {ticker} for {price}")
    else:
        print(f"\t> {ticker} is closed. {datetime.now()}")


def strategy1 (indata:pd.DataFrame, ticker):
    five = resample_ohlcv(get_midprices(indata), "5 min")
    if len(quarterly) < 10:
        print("Not enough data.")
        return None
    
    ema_short = five.Close.rolling(25).ewm(span=25, adjust=False).mean()
    ma_volume_short = five.Close.rolling(25).mean()
    if ma_short.values[-1]/ma_long.values[-1] > 1.01 and ma_volume_short :
        return 1
    elif ma_short.values[-1]/ma_long.values[-1] < 0.99:
        return -1
    else:
        return 0
    
    
#%% Anlyize data

data = pd.DataFrame (lh.getStockHistory('all',90))

#%% Plot

plt.figure1()

for i in range(0,len(tickers)):
    stockdata = data[data['symbol']==tickers[i]]
    stockdata.reset_index(drop=True, inplace=True)
    plt.plot(stockdata['bidClose'])






#%%Functions

def downloadData(tickers, days):
    start = datetime.now()

    if isinstance(tickers, str):
        tickers = [tickers]

    stocks = {}
    for ticker in tickers:

        print(f"\t> Loading {ticker}")
        print(f"\t> Time {lh.getStock(ticker)['time']}")

        stock = pd.DataFrame(lh.getStockHistory(ticker, days))
        stock.time = pd.to_datetime(stock.time)
        stocks[ticker] = stock[stock.askVolume > 0].set_index("time")

        print(f"\t> Finished loading {ticker},",
              f"{days} days of data after {datetime.now()-start}.")

    return stocks

def resample_ohlcv(indata: pd.DataFrame, resolution: str):
    return indata.resample(resolution).agg({"Open": "first",
                                            "High": "max",
                                            "Low": "min",
                                            "Close": "last",
                                            "Volume": "sum"}).dropna()

def get_midprices(indata: pd.DataFrame):
    indata["Open"] = (indata.askOpen + indata.bidOpen) / 2
    indata["High"] = (indata.askHigh + indata.bidHigh) / 2
    indata["Low"] = (indata.askLow + indata.bidLow) / 2
    indata["Close"] = (indata.askClose + indata.bidClose) / 2
    indata["Volume"] = (indata.askVolume + indata.bidVolume) / 2
    return indata

