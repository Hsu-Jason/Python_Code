import sqlite3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

db = sqlite3.connect("TWStock_idv.db")
stocks_dict = {}
test_data = pd.read_sql(con=db, sql = 'SELECT * FROM "2330"')
test_data.index = pd.to_datetime(test_data['Date'])
test_data = test_data[['證券名稱', '收盤價']]
test_data.columns = ['Stock_code', 'Close']
test_data['Close'] = pd.to_numeric(test_data['Close'].apply(lambda x: x.replace(',', '')))

# 移動平均線 rolling
test_data['MA_7'] = test_data['Close'].rolling(6).mean()
test_data['MA_15'] = test_data['Close'].rolling(14).mean()
test_data['MA_30'] = test_data['Close'].rolling(29).mean()
# 指數移動平均線 ewm
test_data['EMA_12'] = test_data['Close'].ewm(span=12).mean()
test_data['EMA_26'] = test_data['Close'].ewm(span=26).mean()
# MACD線 ewm
test_data['DIF'] = test_data['EMA_12'] - test_data['EMA_26']
test_data['DEM'] = test_data['DIF'].ewm(span=9).mean()
test_data['OSC'] = test_data['DIF'] - test_data['DEM']
# 製圖
fig, ax = plt.subplots(3, 1, figsize=(10, 10))
plt.subplots_adjust(hspace=0.8)
test_data['MA_7'].plot(ax=ax[0])
test_data['MA_15'].plot(ax=ax[0])
test_data['MA_30'].plot(ax=ax[0])
test_data['Close'].plot(ax=ax[0])
ax[0].legend()
test_data['EMA_12'].plot(ax=ax[1])
test_data['EMA_26'].plot(ax=ax[1])
test_data['Close'].plot(ax=ax[1])
ax[1].legend()
test_data['DIF'].plot(ax=ax[2])
test_data['DEM'].plot(ax=ax[2])
ax[2].fill_between(test_data.index, 0, test_data['OSC'])
ax[2].legend()
plt.show()

# RSI
test_data['Dif'] = test_data['Close'].diff()
def cal_U(num):
    if num >= 0:
        return num
    else:
        return 0
def cal_D(num):
    num = -num
    return cal_U(num)
test_data['U'] = test_data['Dif'].apply(cal_U)
test_data['D'] = test_data['Dif'].apply(cal_D)
test_data['ema_U'] = test_data['U'].ewm(span=14).mean()
test_data['ema_D'] = test_data['D'].ewm(span=14).mean()
test_data['RS'] = test_data['ema_U'].div(test_data['ema_D'])
test_data['RSI'] = test_data['RS'].apply(lambda rs: rs/(rs+1) * 100)
plt.figure(figsize=(10, 10))
test_data['RSI'].plot()
plt.plot(test_data.index, [70]*len(test_data.index))
plt.plot(test_data.index, [30]*len(test_data.index))
plt.title("RSI Curve")
plt.legend()
plt.show()
