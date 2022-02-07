import pandas as pd
import requests
import time
import io
import glob
import datetime
import sqlite3
import os
import matplotlib.pyplot as plt
# 抓取資料並進行前處理
def crawler(date_time):
    page_url = 'http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + \
        date_time + '&type=ALLBUT0999'
    use_text = requests.get(page_url).text.splitlines()
    for i, text in enumerate(use_text):
        if text == '"證券代號","證券名稱","成交股數","成交筆數","成交金額","開盤價","最高價","最低價","收盤價","漲跌(+/-)","漲跌價差","最後揭示買價","最後揭示買量","最後揭示賣價","最後揭示賣量","本益比",':
            initial_point = i
            break
    test_df = pd.read_csv(io.StringIO(
        ''.join([text[:-1] + '\n' for text in use_text[initial_point:]])))
    test_df['證券代號'] = test_df['證券代號'].apply(lambda x: x.replace('"', ''))
    test_df['證券代號'] = test_df['證券代號'].apply(lambda x: x.replace('=', ''))
    return test_df

# 轉換日期使用
def trans_date(date_time):
    return ''.join(str(date_time).split(' ')[0].split('-'))

# 確認抓取日期
def processing_n_days(start_date, n):
    df_dict = {}
    now_date = start_date
    times, plus = 0, 0
    while (times < n):
        time.sleep(5)
        now_date = now_date - datetime.timedelta(days=1)
        try:
            if os.path.exists("./Data/Trading_Data/" + str(trans_date(now_date)) + '.csv'):
                print("Current data " + trans_date(now_date) + " Installed Already")
            else:
                df = crawler(trans_date(now_date))
                df_dict.update({trans_date(now_date): df})
                print("Current date " + trans_date(now_date) + "Successful")
            plus+=1
            times+=1
        except:
            print('Fails at ' + str(now_date))
            plus += 1
    return df_dict

days = 5
result_dict = processing_n_days(datetime.datetime.now(), days)

# 存成csv作為Raw Data
for key in result_dict.keys():
    result_dict[key].to_csv("./Data/Trading_Data/" + str(key) + '.csv')

# 抓取csv的檔案存成資料庫，後續使用方便
All_csv_file = glob.glob('./Data/Trading_Data/2022*.csv')  # glob可以抓取相似的文件
db = sqlite3.connect('TWStock.db')
for file_name in All_csv_file:
    pd.read_csv(file_name).iloc[:, 1:].to_sql(
        file_name.replace('.csv', '').replace('./Data/Trading_Data/',''), db, if_exists='replace')

# 查詢語法
# print(pd.read_sql(con=db, sql = 'SELECT * FROM  "20220124"'))

# 建立一個大表，將五天資料都讀入total_df的DataFrame
dates_list = [file_name.replace('.csv', '').replace('./Data/Trading_Data/','') for file_name in All_csv_file]
total_df = pd.DataFrame()
for date in dates_list:
    df = pd.read_sql(con=db, sql='SELECT * FROM' + '"' + date + '"')
    df['Date'] = date
    total_df = total_df.append(df)
total_df = total_df.reindex(columns=['index', '證券代號', 'Date', '證券名稱', '成交股數', '成交筆數', '成交金額', '開盤價', '最高價', '最低價',
                                     '收盤價', '漲跌(+/-)', '漲跌價差', '最後揭示買價', '最後揭示買量', '最後揭示賣價', '最後揭示賣量', '本益比', ])
# 存取各檔股票
db2 = sqlite3.connect('TWStock_idv.db')

total_dict = dict(tuple(total_df.groupby('證券代號')))
for key in total_dict.keys():
    df = total_dict[key].iloc[:, 2:]
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by=['Date'])
    df.to_sql(key, db2, if_exists='replace')

# 搜尋方式
# print(pd.read_sql(con=db2,sql='SELECT * FROM "2330"'))

# 將資料存成類似字典
db2 = sqlite3.connect("TWStock_idv.db")
stocks_dict = {}
stocks_dict.update({'test_data': pd.read_sql(con=db2, sql='SELECT * FROM "2330"')})
stocks_dict.update({'UMC': pd.read_sql(con=db2, sql='SELECT * FROM "2303"')})

for key in stocks_dict.keys():
    df = stocks_dict[key]
    df.index = pd.to_datetime(df['Date'])
    df = df[['證券名稱', '收盤價']]
    df['收盤價'] = pd.to_numeric(df['收盤價'].apply(lambda x: x.replace(',', '')))
    df.columns = ['Stock_code', 'Close']
    stocks_dict[key] = df

# 簡易繪製收盤趨勢
fig, ax = plt.subplots(2, 1, figsize=(5, 5))
plt.subplots_adjust(hspace=1)
stocks_dict['test_data'][:].plot(ax=ax[0])
ax[0].set_title('test_data')
stocks_dict['UMC'][:].plot(ax=ax[1])
ax[1].set_title('UMC')
ax[1].set_ylim([50,70])
fig.suptitle('Stock Price Through Time')
plt.show()