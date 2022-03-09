import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime as dt
import seaborn as sns
from utility import *

def main():
    #圖形的index --權利金
    fig_index = ['(OP'+str(i)+'-'+'OP'+str(i+5)+']' for i in range(95,0,-5)]

    #一整週;製作成dict
    temp_h, temp_m =8, 45
    fig_columns = []
    time_list = ["3","4","5","1","2","N3"]
    for i in time_list:
        n=1142
        if i=="N3":n=286
        for d in range(n):
            temp = ('%s %d:%d' %(i,temp_h,temp_m))
            fig_columns.append(temp)
            temp_m+=1
            if temp_m ==60:
                temp_m = 0
                if temp_h==23 and temp_m==0:
                    temp_h = 0
                else:
                    temp_h+=1
            if temp_h==13 and temp_m==46:
                temp_h = 15
                temp_m = 0
            if temp_h ==5 and temp_m==1:
                temp_h=8
                temp_m=45
    #時間對照表
    dict_time = {text: num for num, text in enumerate(fig_columns)}
    #OP的縱軸
    dict_OP = {i:19-i for i in range(1,20)}
    #讀取TX資料
    dataset = pd.read_csv("CDP_Cha.csv")
    #製作TX取index的dict
    match_date = {date: cdp for date, cdp in zip(dataset['date'], dataset['cdp_volta'])}

    # 只跑202001-202008 想與原始的賣方策略看差異
    odd,v,w = 20,0,48
    # 以下為DataFrame製作放置表格
    data_call_all = pd.DataFrame(0, columns=fig_columns, index=fig_index)
    data_call_double = pd.DataFrame(0, columns=fig_columns, index=fig_index)
    data_put_all = pd.DataFrame(0, columns=fig_columns, index=fig_index)
    data_put_double = pd.DataFrame(0, columns=fig_columns, index=fig_index)
    for year in range(2020, 2021):
        for mon in range(1, 9):
            for week in range(1, 6):
                print(year, mon, week)
                # Excluding the weeks that don't have 5 trading days
                if (year == 2017 and mon == 10 and week == 1) or (year == 2018 and mon == 2 and week == 4) or \
                        (year == 2018 and mon == 4 and week == 1) or (year == 2018 and mon == 10 and week == 2) or \
                        (year == 2019 and mon == 2 and week == 1) or (year == 2019 and mon == 5 and week == 1) or \
                        (year == 2020 and mon == 1 and week == 1) or (year == 2020 and mon == 1 and week == 4):
                    pass
                else:
                    if week == 3:
                        ##月選的Ｃall
                        path_price = '/Users/jason/Downloads/TXO_data/%d%02d_C.npy' % (year, mon)
                        try:
                            price = np.load(path_price, allow_pickle=True)
                            for i in range(len(price)):  # 先計算有幾個履約價值 i = 履約價的個數
                                for j in range(len(price[i])):  # 再從該履約價值中filter特定值 j = 該履約價中有幾筆資料
                                    d = datetime.datetime.strptime(price[i][j][1], "%Y-%m-%d").weekday() + 1
                                    # 只做週二及三！
                                    if d == 2 or d == 3:
                                        h = datetime.datetime.strptime(price[i][j][2], "%H:%M:%S").hour
                                        m = datetime.datetime.strptime(price[i][j][2], "%H:%M:%S").minute
                                        temp_day = price[i][j][1].split('-')
                                        temp_week = week_month(int(temp_day[0]), int(temp_day[1]), int(temp_day[2]))
                                        if year == int(temp_day[0]) and mon == int(temp_day[1]):  # 篩選年份
                                            if (temp_week == 2 and d == 3 and h >= 8) or \
                                                    (temp_week == 2 and d > 3 and d <= 5) or \
                                                    (temp_week == 3 and d < 3) or \
                                                    (temp_week == 3 and d == 3 and h <= 14) or \
                                                    (temp_week == 2 and d == 6 and h <= 5):  # 1.處理第二週三星期三；2.處理第二週星期四五；3.處理第三週星期一二；4.處理第三週星期三
                                                if temp_week == 3 and datetime.datetime.strptime(price[i][j][1],"%Y-%m-%d").weekday() + 1 == 3:  # 處理Week3的禮拜三
                                                    if h <= 5:
                                                        d -= 1
                                                        temp = ('%d %d:%d' % (d, h, m))
                                                    else:
                                                        temp = ('N%d %d:%d' % (d, h, m))
                                                    try:
                                                        if (h <= 5):
                                                            date = datetime.datetime.strptime(price[i][j][1],"%Y-%m-%d") + datetime.timedelta(days=-1)
                                                            date = dt.strftime(date, '%Y-%m-%d')
                                                        else:
                                                            date = datetime.datetime.strptime(price[i][j][1], "%Y-%m-%d")
                                                            date = dt.strftime(date, '%Y-%m-%d')
                                                        if v == 0:
                                                            distinguish_call_P(data_call_all,data_call_double,price,w, date, v, i, j, temp, odd)
                                                            distinguish_call_N(data_call_all,data_call_double,price,w, date, v, i, j, temp, odd)
                                                        else:
                                                            distinguish_call_P(data_call_all,data_call_double,price,w, date, v, i, j, temp, odd)
                                                    except Exception as e:
                                                        pass
                                                # 處理其他資料
                                                else:
                                                    if h <= 5:
                                                        d -= 1
                                                        temp = ('%d %d:%d' % (d, h, m))
                                                    else:
                                                        temp = ('%d %d:%d' % (d, h, m))
                                                    try:
                                                        if (h <= 5):
                                                            date = datetime.datetime.strptime(price[i][j][1],
                                                                                              "%Y-%m-%d") + datetime.timedelta(
                                                                days=-1)
                                                            date = dt.strftime(date, '%Y-%m-%d')
                                                        else:
                                                            date = datetime.datetime.strptime(price[i][j][1], "%Y-%m-%d")
                                                            date = dt.strftime(date, '%Y-%m-%d')
                                                        if v == 0:
                                                            distinguish_call_P(data_call_all,data_call_double,price,w, date, v, i, j, temp, odd)
                                                            distinguish_call_N(data_call_all,data_call_double,price,w, date, v, i, j, temp, odd)
                                                        else:
                                                            distinguish_call_P(data_call_all,data_call_double,price,w, date, v, i, j, temp, odd)
                                                    except Exception as e:
                                                        pass
                        except Exception as e:
                            pass
                        ##月選的Put
                        path_price = '/Users/jason/Downloads/TXO_data/%d%02d_P.npy' % (year, mon)
                        try:
                            price = np.load(path_price, allow_pickle=True)
                            for i in range(len(price)):  # 先計算有幾個履約價值 i = 履約價的個數
                                for j in range(len(price[i])):  # 再從該履約價值中filter特定值 j = 該履約價中有幾筆資料
                                    d = datetime.datetime.strptime(price[i][j][1], "%Y-%m-%d").weekday() + 1
                                    # 只做週二！
                                    if d == 2 or d == 3:
                                        h = datetime.datetime.strptime(price[i][j][2], "%H:%M:%S").hour
                                        m = datetime.datetime.strptime(price[i][j][2], "%H:%M:%S").minute
                                        temp_day = price[i][j][1].split('-')
                                        temp_week = week_month(int(temp_day[0]), int(temp_day[1]), int(temp_day[2]))
                                        if year == int(temp_day[0]) and mon == int(temp_day[1]):
                                            if (temp_week == 2 and d == 3 and h >= 8) or (
                                                    temp_week == 2 and d > 3 and d <= 5) or (temp_week == 3 and d < 3) or (
                                                    temp_week == 3 and d == 3 and h <= 14) or (
                                                    temp_week == 2 and d == 6 and h <= 5):  # 1.處理第二週三星期三；2.處理第二週星期四五；3.處理第三週星期一二；4.處理第三週星期三
                                                if temp_week == 3 and datetime.datetime.strptime(price[i][j][1],
                                                                                                 "%Y-%m-%d").weekday() + 1 == 3:  # 處理Week3的禮拜三
                                                    if h <= 5:
                                                        d -= 1
                                                        temp = ('%d %d:%d' % (d, h, m))
                                                    else:
                                                        temp = ('N%d %d:%d' % (d, h, m))
                                                    try:
                                                        if (h <= 5):
                                                            date = datetime.datetime.strptime(price[i][j][1],
                                                                                              "%Y-%m-%d") + datetime.timedelta(
                                                                days=-1)
                                                            date = dt.strftime(date, '%Y-%m-%d')
                                                        else:
                                                            date = datetime.datetime.strptime(price[i][j][1], "%Y-%m-%d")
                                                            date = dt.strftime(date, '%Y-%m-%d')
                                                        if v == 0:
                                                            distinguish_put_P(data_put_all,data_put_double,price,w, date, v, i, j, temp, odd)
                                                            distinguish_put_N(data_put_all,data_put_double,price,w, date, v, i, j, temp, odd)
                                                        else:
                                                            distinguish_put_P(data_put_all,data_put_double,price,w, date, v, i, j, temp, odd)
                                                    except Exception as e:
                                                        pass
                                                # 處理其他資料
                                                else:
                                                    if h <= 5:
                                                        d -= 1
                                                        temp = ('%d %d:%d' % (d, h, m))
                                                    else:
                                                        temp = ('%d %d:%d' % (d, h, m))
                                                    try:
                                                        if (h <= 5):
                                                            date = datetime.datetime.strptime(price[i][j][1],
                                                                                              "%Y-%m-%d") + datetime.timedelta(
                                                                days=-1)
                                                            date = dt.strftime(date, '%Y-%m-%d')
                                                        else:
                                                            date = datetime.datetime.strptime(price[i][j][1], "%Y-%m-%d")
                                                            date = dt.strftime(date, '%Y-%m-%d')
                                                        if v == 0:
                                                            distinguish_put_P(data_put_all,data_put_double,price,w, date, v, i, j, temp, odd)
                                                            distinguish_put_N(data_put_all,data_put_double,price,w, date, v, i, j, temp, odd)
                                                        else:
                                                            distinguish_put_P(data_put_all,data_put_double,price,w, date, v, i, j, temp, odd)
                                                    except Exception as e:
                                                        pass
                        except Exception as e:
                            pass
                    else:
                        ##周選的Ｃall
                        path_price = '/Users/jason/Downloads/TXO_data/%d%02dW%d_C.npy' % (year, mon, week)
                        try:
                            price = np.load(path_price, allow_pickle=True)
                            init_last = count_last(len(price))
                            for i in range(len(price)):  # 先計算有幾個履約價值 i = 履約價的個數
                                arr = [[] for i in range(8)]
                                for j in range(len(price[i])):  # 再從該履約價值中filter特定值 j = 該履約價中有幾筆資料
                                    d = datetime.datetime.strptime(price[i][j][1], "%Y-%m-%d").weekday() + 1
                                    # 只做週二！
                                    if d == 2 or d == 3:
                                        h = datetime.datetime.strptime(price[i][j][2], "%H:%M:%S").hour
                                        m = datetime.datetime.strptime(price[i][j][2], "%H:%M:%S").minute
                                        arr[d] = 1
                                        if (arr.count(1) >= 2 and d == 3) or (
                                                datetime.datetime.strptime(price[i][j][1], "%Y-%m-%d") == init_last):
                                            if h <= 5:
                                                d -= 1
                                                temp = ('%d %d:%d' % (d, h, m))
                                            else:
                                                temp = ('N%d %d:%d' % (d, h, m))
                                            try:
                                                if (h <= 5):
                                                    date = datetime.datetime.strptime(price[i][j][1],
                                                                                      "%Y-%m-%d") + datetime.timedelta(
                                                        days=-1)
                                                    date = dt.strftime(date, '%Y-%m-%d')
                                                else:
                                                    date = datetime.datetime.strptime(price[i][j][1], "%Y-%m-%d")
                                                    date = dt.strftime(date, '%Y-%m-%d')
                                                if v == 0:
                                                    distinguish_call_P(data_call_all,data_call_double,price,w, date, v, i, j, temp, odd)
                                                    distinguish_call_N(data_call_all,data_call_double,price,w, date, v, i, j, temp, odd)
                                                else:
                                                    distinguish_call_P(data_call_all,data_call_double,price,w, date, v, i, j, temp, odd)
                                            except Exception as e:
                                                pass
                                        elif (d <= 5) or (d == 6 and h <= 5):
                                            if d == 3 and arr.count(1) <= 1:
                                                temp = ('%d %d:%d' % (d, h, m))
                                            else:
                                                if h <= 5:
                                                    d -= 1
                                                    temp = ('%d %d:%d' % (d, h, m))
                                                else:
                                                    temp = ('%d %d:%d' % (d, h, m))
                                            try:
                                                if (h <= 5):
                                                    date = datetime.datetime.strptime(price[i][j][1],
                                                                                      "%Y-%m-%d") + datetime.timedelta(
                                                        days=-1)
                                                    date = dt.strftime(date, '%Y-%m-%d')
                                                else:
                                                    date = datetime.datetime.strptime(price[i][j][1], "%Y-%m-%d")
                                                    date = dt.strftime(date, '%Y-%m-%d')
                                                if v == 0:
                                                    distinguish_call_P(data_call_all,data_call_double,price,w, date, v, i, j, temp, odd)
                                                    distinguish_call_N(data_call_all,data_call_double,price,w, date, v, i, j, temp, odd)
                                                else:
                                                    distinguish_call_P(data_call_all,data_call_double,price,w, date, v, i, j, temp, odd)
                                            except Exception as e:
                                                pass
                        except Exception as e:
                            pass

                        ##周選的Put
                        path_price = '/Users/jason/Downloads/TXO_data/%d%02dW%d_P.npy' % (year, mon, week)
                        try:
                            price = np.load(path_price, allow_pickle=True)
                            init_last = count_last(len(price))
                            for i in range(len(price)):  # 先計算有幾個履約價值 i = 履約價的個數
                                arr = [[] for i in range(8)]
                                for j in range(len(price[i])):  # 再從該履約價值中filter特定值 j = 該履約價中有幾筆資料
                                    d = datetime.datetime.strptime(price[i][j][1], "%Y-%m-%d").weekday() + 1
                                    # 只做週二！
                                    if d == 2 or d == 3:
                                        h = datetime.datetime.strptime(price[i][j][2], "%H:%M:%S").hour
                                        m = datetime.datetime.strptime(price[i][j][2], "%H:%M:%S").minute
                                        arr[d] = 1
                                        if (arr.count(1) >= 2 and d == 3) or (
                                                datetime.datetime.strptime(price[i][j][1], "%Y-%m-%d") == init_last):
                                            if h <= 5:
                                                d -= 1
                                                temp = ('%d %d:%d' % (d, h, m))
                                            else:
                                                temp = ('N%d %d:%d' % (d, h, m))
                                            try:
                                                if (h <= 5):
                                                    date = datetime.datetime.strptime(price[i][j][1],
                                                                                      "%Y-%m-%d") + datetime.timedelta(
                                                        days=-1)
                                                    date = dt.strftime(date, '%Y-%m-%d')
                                                else:
                                                    date = datetime.datetime.strptime(price[i][j][1], "%Y-%m-%d")
                                                    date = dt.strftime(date, '%Y-%m-%d')
                                                if v == 0:
                                                    distinguish_put_P(data_put_all,data_put_double,price,w, date, v, i, j, temp, odd)
                                                    distinguish_put_N(data_put_all,data_put_double,price,w, date, v, i, j, temp, odd)
                                                else:
                                                    distinguish_put_P(data_put_all,data_put_double,price,w, date, v, i, j, temp, odd)
                                            except Exception as e:
                                                pass
                                        elif (d <= 5) or (d == 6 and h <= 5):
                                            if d == 3 and arr.count(1) <= 1:
                                                temp = ('%d %d:%d' % (d, h, m))
                                            else:
                                                if h <= 5:
                                                    d -= 1
                                                    temp = ('%d %d:%d' % (d, h, m))
                                                else:
                                                    temp = ('%d %d:%d' % (d, h, m))
                                            try:
                                                if (h <= 5):
                                                    date = datetime.datetime.strptime(price[i][j][1],
                                                                                      "%Y-%m-%d") + datetime.timedelta(
                                                        days=-1)
                                                    date = dt.strftime(date, '%Y-%m-%d')
                                                else:
                                                    date = datetime.datetime.strptime(price[i][j][1], "%Y-%m-%d")
                                                    date = dt.strftime(date, '%Y-%m-%d')
                                                if v == 0:
                                                    distinguish_put_P(data_put_all,data_put_double,price,w, date, v, i, j, temp, odd)
                                                    distinguish_put_N(data_put_all,data_put_double,price,w, date, v, i, j, temp, odd)
                                                else:
                                                    distinguish_put_P(data_put_all,data_put_double,price,w, date, v, i, j, temp, odd)
                                            except Exception as e:
                                                pass
                        except Exception as e:
                            pass

    #存檔做後續操作
    data_call_double.to_csv(('Test_Long_5M(Trend)_Following_P%d_data_call_double.csv') % (v))
    data_put_double.to_csv(('Test_Long_5M(Trend)_Following_P%d_data_put_double.csv') % (v))
    data_call_all.to_csv(('Test_Long_5M(Trend)_Following_P%d_data_call_all.csv') % (v))
    data_put_all.to_csv(('Test_Long_5M(Trend)_Following_P%d_data_put_all.csv') % (v))
    data_call_final = round(data_call_double / data_call_all, 2)
    data_call_final.to_csv(('Test_Long_5M(Trend)_Following_P%d_data_Call_final.csv') % (v))
    data_put_final = round(data_put_double / data_put_all, 2)
    data_put_final.to_csv(('Test_Long_5M(Trend)_Following_P%d_data_Put_final.csv') % (v))

    # 分割確認統計資料
    data_call_SumNum = pd.DataFrame(0, columns=fig_columns, index=fig_index)
    for i in range(len(fig_index)):
        for j in range(len(fig_columns)):
            data_call_SumNum.iloc[i, j] = (str(data_call_double.iloc[i, j]) + '/' + str(data_call_all.iloc[i, j]))
    data_call_SumNum.to_csv(('Test_Long_5M(Trend)_Following_P%d_data_call_SumNum.csv') % (v))

    data_put_SumNum = pd.DataFrame(0, columns=fig_columns, index=fig_index)
    for i in range(len(fig_index)):
        for j in range(len(fig_columns)):
            data_put_SumNum.iloc[i, j] = (str(data_put_double.iloc[i, j]) + '/' + str(data_put_all.iloc[i, j]))
    data_put_SumNum.to_csv(('Test_Long_5M(Trend)_Following_P%d_data_put_SumNum.csv') % (v))

    # 建立圖檔
    fig, ax = plt.subplots(figsize=(400, 80))
    sns.heatmap(data_call_final, cmap='OrRd', vmin=0.5, mask=(data_call_final < 0.5), annot=True, fmt=".1f", ax=ax)
    ax.set_title('Call OP Life Cycle', fontsize=400)
    ax.set_xlabel('Time Value', fontsize=300)
    ax.set_ylabel('Option Premium', fontsize=300)
    plt.xticks(fontsize=50)
    plt.yticks(fontsize=100, rotation=0)
    plt.axvline(x=300, linestyle='-', color='blue')
    fig.savefig(('Test_Long_5M(Trend)_Following_P%d_Call_OPlifecycle.png') % (v))

    fig, ax = plt.subplots(figsize=(400, 80))
    sns.heatmap(data_put_final, cmap='OrRd', vmin=0.5, mask=(data_put_final < 0.5), annot=True, fmt=".1f", ax=ax)
    ax.set_title('Put OP Life Cycle', fontsize=400)
    ax.set_xlabel('Time Value', fontsize=300)
    ax.set_ylabel('Option Premium', fontsize=300)
    plt.xticks(fontsize=50)
    plt.yticks(fontsize=100, rotation=0)
    plt.axvline(x=300, linestyle='-', color='blue')
    fig.savefig(('Test_Long_5M(Trend)_Following_P%d_Put_OPlifecycle.png') % (v))

    # Col 一週版本版本
    beta = 0
    df = data_put_final
    df_new = pd.DataFrame(0, columns=fig_columns, index=fig_index)
    for x in range(0, 12):
        for y in range(0, 1142):
            df_new = nine_grids(df_new,df, x, y)
    df_new.to_csv('Test_Long_5M(Trend)_Following_P%d_data_Put_final_Con.csv' % (beta))

    fig, ax = plt.subplots(figsize=(400, 80))
    sns.heatmap(df_new, cmap='OrRd', vmin=0.5, mask=(df_new < 0.5), annot=True, fmt=".1f", ax=ax)
    ax.set_title('Put Life Cycle Con', fontsize=400)
    ax.set_xlabel('Time Value', fontsize=300)
    ax.set_ylabel('Option Premium', fontsize=300)
    plt.xticks(fontsize=50)
    plt.yticks(fontsize=100, rotation=0)
    plt.axvline(x=300, linestyle='-', color='blue')
    fig.savefig('Test_Long_5M(Trend)_Following_P%d_Put_OPlifecycle.png' % (beta))

    df = data_call_final
    df_new = pd.DataFrame(0, columns=fig_columns, index=fig_index)
    for x in range(0, 12):
        for y in range(0, 1142):
            nine_grids(x, y)
    df_new.to_csv('Test_Long_5M(Trend)_Following_P%d_data_Call_final_Con.csv' % (beta))

    fig, ax = plt.subplots(figsize=(400, 80))
    sns.heatmap(df_new, cmap='OrRd', vmin=0.5, mask=(df_new < 0.5), annot=True, fmt=".1f", ax=ax)
    ax.set_title('Call Life Cycle', fontsize=400)
    ax.set_xlabel('Time Value', fontsize=300)
    ax.set_ylabel('Option Premium', fontsize=300)
    plt.xticks(fontsize=50)
    plt.yticks(fontsize=100, rotation=0)
    plt.axvline(x=300, linestyle='-', color='blue')
    fig.savefig('Test_Long_5M(Trend)_Following_P%d_Call_OPlifecycle.pngg' % (beta))

if __name__ == '__main__':
    main()