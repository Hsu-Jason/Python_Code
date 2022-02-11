import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import datetime
import os

# 爬每日收盤行情（主要可以看股票的交易量、金額）
def closing_quotation(date_time):
    if os.path.exists("./Data/" + date_time + "_Closing_Quotation"):
        pass
    else:
        url = "https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=" + \
            date_time + "&type=MS"
        text = requests.get(url).text
        use_text = text.splitlines()
        for i, text in enumerate(use_text):
            if text == '"成交統計","成交金額(元)","成交股數(股)","成交筆數",':
                initial_point = i
                break
        tem_df = pd.read_csv(io.StringIO(
            ''.join([text[:-1] + '\n' for text in use_text[initial_point:]])))
        tem_df = tem_df.drop(index=[21, 22, 23])
        for i in range(len(tem_df['成交統計'])):
            try:
                tem_df['成交統計'][i] = tem_df['成交統計'][i].split('.')[1]
            except:
                pass
        tem_df['成交統計'][15] = ''.join(tem_df['成交統計'][15].split('\n'))
        tem_df.to_csv("./Data/" + date_time + "_Closing_Quotation", index=False)


# 每次皆取5日資訊
times, plus = 0, 0
while(times < 5):
    date_time = datetime.datetime.now() - datetime.timedelta(days=plus)
    date_time = ''.join(str(date_time).split(' ')[0].split('-'))
    try:
        closing_quotation(date_time)
        print(date_time + "Finished Download")
        plus += 1
        times += 1
    except:
        plus += 1


# 繪製圖形曲線
def draw(date_time):
    tem = pd.read_csv("./Data/" + date_time + "_Closing_Quotation", index_col=0)
    close_list.append(
        int(int(''.join(tem["成交金額(元)"][0].split(',')))/1_000_000_000))


times, plus = 0, 0
close_list = []
while(times < 5):
    date_time = datetime.datetime.now() - datetime.timedelta(days=plus)
    date_time = ''.join(str(date_time).split(' ')[0].split('-'))
    try:
        draw(date_time)
        plus += 1
        times += 1
    except:
        plus += 1
plt.figure(figsize=(5, 7.5))
plt.plot(close_list, marker='o', c='r')
plt.bar(np.arange(5),close_list)
plt.title("Closing Quotation in 5 Days  (Unit: Billion)")
plt.xticks(np.arange(5))
plt.xlabel("Days")
plt.ylabel("Volume")
for x, y in zip(np.arange(5), close_list):
    plt.annotate(y, (x, y), xytext=(0, 10),
                 textcoords='offset points', ha='center')
plt.show()