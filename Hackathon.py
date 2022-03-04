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
#from matplotlib.finance import candlestick2_ohlc as ohlc
#import matplotlib.ticker as ticker
from datetime import datetime

lh.init("1c0c7bca-53b8-43d7-aa08-3fa488f20e91")

#%% get tickers and data
tickers = lh.getTickers()

data = pd.DataFrame (lh.getStockHistory('all',90))

#%% PIVOT DATA DVS MAKE NAN AND THINGS

stocks = data.pivot('time','symbol','bidClose')
print(stocks)


#%% plot things
'''plt.figure()

for i in range(0,len(tickers)):
    plt.plot(stocks[tickers])
'''
#%% Main code
def main():
    while True:
        for ticker in tickers:
            
            stock = lh.getStockHistory(ticker, 90)
            stock = getmidprices(stock)
            signal = strategy1(stock, ticker)
            execution(ticker,signal)


#%% Functions

def getmidprices(indata: pd.DataFrame):
    indata['Open'] = (indata.askOpen + indata.bidOpen)/2
    indata['Low'] = (indata.askLow + indata.bidLow)/2
    indata['Close'] = (indata.askClose + indata.bidClose)/2
    indata['Volume'] = (indata.askVolume + indata.bidVolume)/2
    return indata

def execution(ticker, signals):
    print("Checking signals for {ticker}: {datetime.now()}")

    # kolla om marknad öppen
    if lh.getStock(ticker)["askVolume"] > 0:
        portfolio = lh.getPortfolio()
        valport = lh.getSaldo()

        amount = [e["amount"] for e in portfolio
                  if e["symbol"] == ticker][0] if \
            len([e["amount"] for e in portfolio
                 if e["symbol"] == ticker]) > 0 else 0

        # sälj om du har
        if amount > 0:

            # Kolla säljsignal
            if signals < 0:
                lh.sellStock(ticker, amount)
                print("Sold {amount} of {ticker} for",
                      "{lh.getStock(ticker)['askClose']}")
                print("Time {lh.getStock(ticker)['time']}")

        # köpsignal
        
        elif signals > 0 and valport < 50000 :
            price = lh.getStock(ticker)["bidClose"]
            total_value = lh.getSaldo() +\
                (sum([e["totalValue"] for e in lh.getPortfolio()])
                 if len(lh.getPortfolio()) > 0 else 0)
            amount = int((total_value * 0.1) / price)
            lh.buyStock(ticker, amount)
            lh.placeStoploss(ticker,price*0.95,amount)
            
            print("Bought {amount} of {ticker} for {price}")
            print("Set stopploss {amount} of {ticker} for {price*0.95}")
    else:
        print("{ticker} is closed. {datetime.now()}")
        
def resample_ohlcv(indata: pd.DataFrame, resolution: str):
    return indata.resample(resolution).agg({"Open": "first",
                                            "High": "max",
                                            "Low": "min",
                                            "Close": "last",
                                            "Volume": "sum"}).dropna()

def strategy1(indata: pd.DataFrame, ticker):
    five = resample_ohlcv(getmidprices(indata), "5 min")
    if len(five) < 10:
        print("Not enough data")
        return None
    
    ema_short = five.Close.rolling(25).ewm(span=25, adjust=False).mean()
    ema_long = five.Close.rolling(100).ewm(span=100, adjust=False).mean()
    ma_volume_short = five.Close.rolling(25).mean()
    if ema_short[-1] < five.Close[-1] and ma_volume_short[-1] < five.Volume[-1]*2 and ema_long[-1] < five.Close[-1]:
        return 1
    elif ema_long[-1] > five.Close[-1]:
        return -1
    else:
        return 0
    
#%% Plot
'''
plt.figure1()

for i in range(0,len(tickers)):
    stockdata = data[data['symbol']==tickers[i]]
    stockdata.reset_index(drop=True, inplace=True)
    plt.plot(stockdata['bidClose'])
'''





#%%Functions


