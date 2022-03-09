import datetime
import pandas as pd
import math

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

dict_time = {text: num for num, text in enumerate(fig_columns)}
dict_OP = {i:19-i for i in range(1,20)}

#讀取TX資料
dataset = pd.read_csv("CDP_Cha.csv")
#製作TX取index的dict
match_date = {date: cdp for date, cdp in zip(dataset['date'], dataset['cdp_volta'])}
#計算Std(日)
positive_std = 0.007293226559444942
negative_std = 0.010214333531845005
Positive_volatile = [0,0+positive_std,0+2*positive_std]
Negative_volatile = [0,0-negative_std,0-2*negative_std]
#計算Std(1分鐘)
positive_std_m = 0.0003163450588580745
negative_std_m = 0.00032446880701456543
Positive_volatile_m = [0,0+positive_std_m,0+2*positive_std_m]
Negative_volatile_m = [0,0-negative_std_m,0-2*negative_std_m]


#計算該時間是第幾週 - 用於月選使用
def week_month(year, month, day):
    last = int(datetime.datetime(year, month, day).strftime("%W"))
    if datetime.datetime(year, month, 1).weekday()+1>=4:
        first = int(datetime.datetime(year, month, 1).strftime("%W"))+1
    else:
        first = int(datetime.datetime(year, month, 1).strftime("%W"))
    different_week = (last - first)+1
    return different_week

#用來計算最後一天（週三結算）
def count_last(long,price):
    init_last = datetime.datetime.strptime("1998-09-28", "%Y-%m-%d")
    for i in range(long):
        if i == 0 :
            init_last = datetime.datetime.strptime(price[i][-1][1], "%Y-%m-%d")
        temp_last = datetime.datetime.strptime(price[i][-1][1], "%Y-%m-%d")
        if temp_last>init_last:
            init_last = temp_last
    return(init_last)

#簡單計算Weight
def count_weight(w):
    if w <=1:
        return(5)
    elif(w<=4):
        return(4)
    elif(w<=12):
        return(3)
    elif(w<=24):
        return(2)
    elif(w<=48):
        return(1)
#計算前五分鐘的波動是否連續上升或下降趨勢
def sign_P(i,j):
    count_sign = 0
    # 避免前5筆資料變成與最後資料相比
    if j >=4:
        list_sign = []
        for temp in range(j-5,j):
            list_sign.append((price[i][temp][13]))
        if list_sign[0]>=0:
            count_sign = sum(i >= 0 for i in list_sign)
    return(count_sign)
def sign_N(i,j):
    count_sign = 0
    # 避免前5筆資料變成與最後資料相比
    if j >=4:
        list_sign = []
        for temp in range(j-5,j):
            list_sign.append((price[i][temp][13]))
        if list_sign[0]<=0:
            count_sign = sum(i >= 0 for i in list_sign)
    return(count_sign)

#順勢
#用於計算獲利與損失(Positive_volatile)
def distinguish_call_P(data_call_all,data_call_double,price,w,date,v,i,j,temp,odd):#分別傳入該筆之波動、位置[i,j]、temp為該次時間、odd為止損率
    if price[i][j][9]>=5:
        OP= dict_OP.get(math.floor(price[i][j][9]/5))
        time = dict_time.get(temp)
        weight = count_weight(w)
        if v == 2 : #第三區間
            if match_date.get(date) >= Positive_volatile[v]:
                data_call_all.iloc[OP,time] =data_call_all.iloc[OP,time] + weight
                if price[i][j][odd]==0 :
                    data_call_double.iloc[OP,time] = data_call_double.iloc[OP,time]+ ((price[i][-1][9]-price[i][j][9])/price[i][j][9]) * weight
        elif v == 1: #第二區間
            if Positive_volatile[v] <= match_date.get(date) < Positive_volatile[v+1]:
                data_call_all.iloc[OP,time] =data_call_all.iloc[OP,time] + weight
                if price[i][j][odd]==0:
                    data_call_double.iloc[OP,time] = data_call_double.iloc[OP,time]+((price[i][-1][9]-price[i][j][9])/price[i][j][9]) * weight
        else: #第一區間(因為0在中間，所以算在正方)
            if Positive_volatile[v] <= match_date.get(date) < Positive_volatile[v+1]:
                if sign_P(i,j)==5:
                    data_call_all.iloc[OP,time] =data_call_all.iloc[OP,time] + weight
                    if price[i][j][odd]==1:
                        data_call_double.iloc[OP,time] = data_call_double.iloc[OP,time]+ weight
                    elif(price[i][-1][9]>price[i][j][9]):
                        data_call_double.iloc[OP,time] = data_call_double.iloc[OP,time]+((price[i][-1][9]-price[i][j][9])/price[i][j][9]) * weight
    return data_call_double,data_call_all
def distinguish_put_P(data_put_all,data_put_double,price,w,date,v,i,j,temp,odd):
    if price[i][j][9]>=5:
        OP= dict_OP.get(math.floor(price[i][j][9]/5))
        time = dict_time.get(temp)
        weight = count_weight(w)
        if v == 2 :
            if match_date.get(date) > Positive_volatile[v]:
                data_put_all.iloc[OP,time] =data_put_all.iloc[OP,time] + weight
                if price[i][j][odd]==0 :
                    data_put_double.iloc[OP,time] = data_put_double.iloc[OP,time]+((price[i][-1][9]-price[i][j][9])/price[i][j][9]) * weight
        elif v ==1:
            if Positive_volatile[v] <= match_date.get(date) < Positive_volatile[v+1]:
                data_put_all.iloc[OP,time] =data_put_all.iloc[OP,time] + weight
                if price[i][j][odd]==0 :
                    data_put_double.iloc[OP,time] = data_put_double.iloc[OP,time]+((price[i][-1][9]-price[i][j][9])/price[i][j][9]) * weight
        else: # (因為0在中間，所以算在正方)
            if Positive_volatile[v] <= match_date.get(date) < Positive_volatile[v+1]:
                if sign_N(i,j)==5:
                    data_put_all.iloc[OP,time] =data_put_all.iloc[OP,time] + weight
                    if price[i][j][odd]==1:
                        data_put_double.iloc[OP,time] = data_put_double.iloc[OP,time] +  weight
                    elif(price[i][-1][9]>price[i][j][9]):
                        data_put_double.iloc[OP,time] = data_put_double.iloc[OP,time] + ((price[i][-1][9]-price[i][j][9])/price[i][j][9]) * weight
#用於計算獲利與損失(Negative_volatile)
def distinguish_call_N(data_call_all,data_call_double,price,w,date,v,i,j,temp,odd):#分別傳入該筆之波動、位置[i,j]、temp為該次時間、odd為止損率
    if price[i][j][9]>=5:
        OP= dict_OP.get(math.floor(price[i][j][9]/5))
        time = dict_time.get(temp)
        weight = count_weight(w)
        if v == 2 : #第三區間
            if match_date.get(date) < Negative_volatile[v]:
                data_call_all.iloc[OP,time] =data_call_all.iloc[OP,time] + weight
                if price[i][j][odd]==0:
                    data_call_double.iloc[OP,time] = data_call_double.iloc[OP,time]+ ((price[i][-1][9]-price[i][j][9])/price[i][j][9]) * weight
        elif v == 1: #第二區間
            if Negative_volatile[v] >= match_date.get(date) > Negative_volatile[v+1]:
                data_call_all.iloc[OP,time] =data_call_all.iloc[OP,time] + weight
                if price[i][j][odd]==0:
                    data_call_double.iloc[OP,time] = data_call_double.iloc[OP,time]+ ((price[i][-1][9]-price[i][j][9])/price[i][j][9]) * weight
        else: #第一區間
            if Negative_volatile[v] > match_date.get(date) > Negative_volatile[v+1]:
                if sign_P(i,j)==5:
                    data_call_all.iloc[OP,time] =data_call_all.iloc[OP,time] + weight
                    if price[i][j][odd]==1:
                        data_call_double.iloc[OP,time] = data_call_double.iloc[OP,time] + weight
                    elif(price[i][-1][9]>price[i][j][9]):
                        data_call_double.iloc[OP,time] = data_call_double.iloc[OP,time] + ((price[i][-1][9]-price[i][j][9])/price[i][j][9]) * weight

def distinguish_put_N(data_put_all,data_put_double,price,w,date,v,i,j,temp,odd):
    if price[i][j][9]>=5:
        OP= dict_OP.get(math.floor(price[i][j][9]/5))
        time = dict_time.get(temp)
        weight = count_weight(w)
        if v == 2 :
            if match_date.get(date) < Negative_volatile[v]:
                data_put_all.iloc[OP,time] =data_put_all.iloc[OP,time] + weight
                if price[i][j][odd]==0:
                    data_put_double.iloc[OP,time] = data_put_double.iloc[OP,time]+((price[i][-1][9]-price[i][j][9])/price[i][j][9]) * weight
        elif v ==1:
            if Negative_volatile[v] >= match_date.get(date) > Negative_volatile[v+1]:
                data_put_all.iloc[OP,time] =data_put_all.iloc[OP,time] + weight
                if price[i][j][odd]==0:
                    data_put_double.iloc[OP,time] = data_put_double.iloc[OP,time]+((price[i][-1][9]-price[i][j][9])/price[i][j][9]) * weight
        else:
            if Negative_volatile[v] > match_date.get(date) > Negative_volatile[v+1]:
                if sign_N(i,j)==5:
                    data_put_all.iloc[OP,time] =data_put_all.iloc[OP,time] + weight
                    if price[i][j][odd]==1:
                        data_put_double.iloc[OP,time] = data_put_double.iloc[OP,time] + weight
                    elif(price[i][-1][9]>price[i][j][9]):
                        data_put_double.iloc[OP,time] = data_put_double.iloc[OP,time] + ((price[i][-1][9]-price[i][j][9])/price[i][j][9]) * weight

def nine_grids(df_new,df,x, y):
    # 處理左上
    if (x == 0 and y == 0) or (x == 0 and y == 301) or (x == 0 and y == 1142) or (x == 0 and y == 1443) or (
            x == 0 and y == 2284) or (x == 0 and y == 2585) or (x == 0 and y == 3426) or (x == 0 and y == 3727) or (
            x == 0 and y == 4568) or (x == 0 and y == 4869) or (x == 0 and y == 5710):
        df_new.iloc[x, y] = (df.iloc[x, y] + df.iloc[x, y + 1] + df.iloc[x + 1, y + 1] + df.iloc[x + 1, y]) / 4
    # 處理左下
    elif (x == 11 and y == 0) or (x == 11 and y == 301) or (x == 11 and y == 1142) or (x == 11 and y == 1443) or (
            x == 11 and y == 2284) or (x == 11 and y == 2585) or (x == 11 and y == 3426) or (x == 11 and y == 3727) or (
            x == 11 and y == 4568) or (x == 11 and y == 4869) or (x == 11 and y == 5710):
        df_new.iloc[x, y] = (df.iloc[x, y] + df.iloc[x - 1, y] + df.iloc[x - 1, y + 1] + df.iloc[x, y + 1]) / 4
    # 處理右上
    elif (x == 0 and y == 0) or (x == 0 and y == 300) or (x == 0 and y == 1141) or (x == 0 and y == 1442) or (
            x == 0 and y == 2283) or (x == 0 and y == 2584) or (x == 0 and y == 3425) or (x == 0 and y == 3726) or (
            x == 0 and y == 4567) or (x == 0 and y == 4868) or (x == 0 and y == 5709) or (x == 0 and y == 5995):
        df_new.iloc[x, y] = (df.iloc[x, y] + df.iloc[x + 1, y] + df.iloc[x + 1, y - 1] + df.iloc[x, y - 1]) / 4
    # 處理右下
    elif (x == 11 and y == 0) or (x == 11 and y == 300) or (x == 11 and y == 1141) or (x == 11 and y == 1442) or (
            x == 11 and y == 2283) or (x == 11 and y == 2584) or (x == 11 and y == 3425) or (x == 11 and y == 3726) or (
            x == 11 and y == 4567) or (x == 11 and y == 4868) or (x == 11 and y == 5709) or (x == 11 and y == 5995):
        df_new.iloc[x, y] = (df.iloc[x, y] + df.iloc[x - 1, y] + df.iloc[x, y - 1] + df.iloc[x - 1, y - 1]) / 4
    # 處理正上方
    elif (x == 0):
        df_new.iloc[x, y] = (df.iloc[x, y] + df.iloc[x, y + 1] + df.iloc[x + 1, y + 1] + df.iloc[x + 1, y] + df.iloc[
            x + 1, y - 1]
                             + df.iloc[x, y - 1]) / 6
    # 處理正下方
    elif (x == 11):
        df_new.iloc[x, y] = (df.iloc[x, y] + df.iloc[x - 1, y] + df.iloc[x - 1, y + 1] + df.iloc[x, y + 1] + df.iloc[
            x, y - 1]
                             + df.iloc[x - 1, y - 1]) / 6
        # 處理左排
    elif y == 0 or y == 301 or y == 1142 or y == 1443 or y == 2284 or y == 2585 or y == 3426 or y == 3727 or y == 4568 or y == 4869 or y == 5710:
        df_new.iloc[x, y] = (df.iloc[x, y] + df.iloc[x - 1, y] + df.iloc[x - 1, y + 1] + df.iloc[x, y + 1] + df.iloc[
            x + 1, y + 1] + df.iloc[x + 1, y]) / 6
    # 處理右排
    elif y == 300 or y == 1141 or y == 1442 or y == 2283 or y == 2584 or y == 3425 or y == 3726 or y == 4567 or y == 4868 or y == 5709 or y == 5995:
        df_new.iloc[x, y] = (df.iloc[x, y] + df.iloc[x - 1, y] + df.iloc[x + 1, y] + df.iloc[x + 1, y - 1] + df.iloc[
            x, y - 1] + df.iloc[x - 1, y - 1]) / 6
    else:
        df_new.iloc[x, y] = (df.iloc[x, y] + df.iloc[x - 1, y] + df.iloc[x + 1, y - 1] + df.iloc[x, y + 1] + df.iloc[
            x + 1, y + 1] + df.iloc[x + 1, y] + df.iloc[x + 1, y - 1] + df.iloc[x - 1, y] + df.iloc[x - 1, y - 1]) / 9