import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
import math

# 將資料存成類似字典
db = sqlite3.connect("TWStock_idv.db")
stocks_dict = {}
stocks_dict.update({'test_data': pd.read_sql(con=db, sql='SELECT * FROM "2330"')})
stocks_dict.update({'UMC': pd.read_sql(con=db, sql='SELECT * FROM "2303"')})

for key in stocks_dict.keys():
    df = stocks_dict[key]
    df.index = pd.to_datetime(df['Date'])
    df = df[['證券名稱', '收盤價']]
    df['收盤價'] = pd.to_numeric(df['收盤價'].apply(lambda x: x.replace(',', '')))
    df.columns = ['Stock_code', 'Close']
    stocks_dict[key] = df

# 根據變動百分比進行風險評估，進行現行報酬 Formular = (P1 / P0) -1 & 連續報酬 Formular = ln(P1 / P0)
df['linear return rate'] = df['Close'].pct_change()
df_lrp = df.iloc[:-1, :]
df_lra = df.iloc[1:, :]
plt.scatter(np.array(df_lrp['linear return rate']),
            np.array(df_lra['linear return rate']))
plt.show()
# 最大近似值MLE(https://zh.wikipedia.org/wiki/最大似然估计)
def MLE_mu_normal(X):
    n = len(X)
    return sum(X)/n

def MLE_sigma_normal(X):
    n = len(X)
    mu_hat = MLE_mu_normal(X)
    s = sum([(x-mu_hat)**2 for x in X])
    return s/n

test_data = stocks_dict["test_data"]
# resample可根據區段做群組並做相關計算 -> Mean()；有部分資料為空直故須用dropna()
test_data = test_data[['Close']].resample('W').mean().dropna()

# 計算連續報酬率
price_list = list(test_data['Close'])
ratio_list = [p_1/p_2 for p_1, p_2 in zip(price_list[1:], price_list[:-1])]
c_return_list = [math.log(x) for x in ratio_list]
mu = MLE_mu_normal(c_return_list)
sigma_2 = MLE_sigma_normal(c_return_list)
print(mu)
print(sigma_2)

# 產圖
h = sorted(c_return_list)
x_axis = np.arange(h[0], h[-1], 0.0001)
plt.plot(x_axis, stats.norm.pdf(x_axis, mu, math.sqrt(sigma_2)))
plt.hist(h)
plt.show()

# 估計週報酬小於-0.05 Pro
print(stats.norm(mu, math.sqrt(sigma_2)).cdf(-0.05))
# 大於0.5的機率 1 - Pro
print(1 - stats.norm(mu, math.sqrt(sigma_2)).cdf(0.5))
