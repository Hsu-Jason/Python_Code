import pandas as pd
import numpy as np

# 改版 邏輯
def computeRevenue(data):
    Revenue = data["total_asset"].iloc[-1] - data["total_asset"].iloc[0]
    return Revenue


def computeAnnualizedReturn(data):
    # Compute the cumulative return over the entire trading horizon
    Total_Return = data["total_asset"].iloc[-1] - data["total_asset"].iloc[0]
    # 獲利 / 本金(368_000)
    Ratio_Return = Total_Return / 368_000
    # Compute the time elapsed (in days)
    start = data.index[0].to_pydatetime()
    end = data.index[-1].to_pydatetime()
    timeElapsed = end - start
    timeElapsed = timeElapsed.days

    # Compute the Annualized Return
    if (Ratio_Return > -1):
        annualizedReturn = 100 * (((1 + Ratio_Return) ** (365 / timeElapsed)) - 1)
    else:
        annualizedReturn = -100
    return annualizedReturn


def computeShortLongProfit(data):
    short_p = 0
    long_p = 0
    for i in range(len(data)):
        if data['F_diff'][i] != 0:
            if data['positions'][i - 2] == 1:
                long_p += data['F_diff'][i] * 200
            if data['positions'][i - 2] == -1:
                short_p += data['F_diff'][i] * 200
    return long_p, short_p


def computeAnnualizedVolatility(data):
    annualizedVolatily = 100 * np.sqrt(252) * data['returns'].std()
    return annualizedVolatily


def computeSharpeRatio(data, riskFreeRate=0):
    # Compute the expected return
    expectedReturn = data['returns'].mean()

    # Compute the returns volatility
    volatility = data['returns'].std()

    # Compute the Sharpe Ratio (252 trading days in 1 year)
    if expectedReturn != 0 and volatility != 0:
        sharpeRatio = np.sqrt(252) * (expectedReturn - riskFreeRate) / volatility
    else:
        sharpeRatio = 0
    return sharpeRatio


def computeSortinoRatio(data, riskFreeRate=0):
    # Compute the expected return
    expectedReturn = np.mean(data['returns'])

    # Compute the negative returns volatility
    negativereturns = [returns for returns in data['returns'] if returns < 0]
    volatility = np.std(negativereturns)

    # Compute the Sortino Ratio (252 trading days in 1 year)
    if expectedReturn != 0 and volatility != 0:
        sortinoRatio = np.sqrt(252) * (expectedReturn - riskFreeRate) / volatility
    else:
        sortinoRatio = 0
    return sortinoRatio


def computeMaxDrawdown(data, plotting=False):
    # Compute both the Maximum Drawdown and Maximum Drawdown Duration
    capital = data['total_asset'].values
    through = np.argmax(np.maximum.accumulate(capital) - capital)
    if through != 0:
        peak = np.argmax(capital[:through])
        maxDD = 100 * (capital[peak] - capital[through]) / capital[peak]
        maxDDD = through - peak
    else:
        maxDD = 0
        maxDDD = 0
        return maxDD, maxDDD

    # Plotting of the Maximum Drawdown if required
    #     if plotting:
    #         plt.figure(figsize=(10, 4))
    #         plt.plot(data['total_asset'], lw=2, color='Blue')
    #         plt.plot([data.iloc[[peak]].index, data.iloc[[through]].index],
    #                  [capital[peak], capital[through]], 'o', color='Red', markersize=5)
    #         plt.xlabel('Time')
    #         plt.ylabel('Price')
    #         plt.savefig(''.join(['Figures/', 'MaximumDrawDown', '.png']))
    # plt.show()

    # Return of the results
    return maxDD, maxDDD


def computeProfitability(data):
    good = len(data[data['F_diff'] > 0]['F_diff'])
    bad = len(data[data['F_diff'] < 0]['F_diff'])
    if good != 0 and bad != 0:
        Win_Loss_Ration = good / (good + bad) * 100

        profit_point = sum(data[data['F_diff'] > 0]['F_diff']) / good
        loss_point = sum(data[data['F_diff'] < 0]['F_diff']) / bad
        ProfitLossRatio = (profit_point / -loss_point) * 200
        return Win_Loss_Ration, ProfitLossRatio
    else:
        return 0, 0


def computeSkewness(data):
    # Compute the Skewness of the returns
    skewness = data["returns"].skew()
    return skewness


def performance_mine(data):
    Revenue = computeRevenue(data)
    AnnualizedVolatility = computeAnnualizedVolatility(data)
    SharpeRatio = computeSharpeRatio(data, riskFreeRate=0)
    SortinoRatio = computeSortinoRatio(data, riskFreeRate=0)
    AnnualizedReturn = computeAnnualizedReturn(data)
    MaxDrawdown = computeMaxDrawdown(data, plotting=False)
    Profitability = computeProfitability(data)
    Skewness = computeSkewness(data)
    ShortLongProfit = computeShortLongProfit(data)
    positions_1 = len(data[data['positions'] == 1])
    positions_2 = len(data[data['positions'] == -1])
    positions_3 = len(data[data['positions'] == 0])
    list_performance = [Revenue, AnnualizedReturn, AnnualizedVolatility, ShortLongProfit, SharpeRatio, SortinoRatio,
                        MaxDrawdown, Profitability, Skewness, positions_1, positions_2, positions_3]
    performance_ = pd.DataFrame(list_performance,
                                index=["Revenue", "AnnualizedReturn", "AnnualizedVolatility", "ShortLongProfit", \
                                       "SharpeRatio", "SortinoRatio", "MaxDrawdown",
                                       "Win_Loss_Ratio / averageProfitLossRatio", "Skewness", "Positive", "Negative",
                                       "Neural"], columns=['Performance'])
    print(performance_)
    return performance_


def portfolio_mine(data, initially=368_000, positions=1):
    # 一口保證金 $84,000；每點價 $200；交易稅 萬分之2；手續費 50 / 口
    temp_return, goods_price, buy_tax, sell_tax, tax, fee = 0, 0, 0, 0, 0.00001, 50
    data['F_diff'] = 0.0
    data['goods_price'] = 0
    # 特殊處理第一筆資料
    if data['positions'][0] != 0:
        goods_price = data['Close'][1]
        buy_tax = data['Close'][1] * tax * 200
        data['goods_price'][1] = data['Close'][1]
    for i in range(1, len(data)):
        try:
            # 新多單進場
            if data['positions'][i] == 1 and data['positions'][i - 1] == 0:
                goods_price = data['Close'][i + 1]
                buy_tax = data['Close'][i + 1] * tax * 200
                data['goods_price'][i + 1] = data['Close'][i + 1]
            # 多單平倉
            elif data['positions'][i] == 0 and data['positions'][i - 1] == 1:
                sell_tax = data['Close'][i + 1] * tax * 200
                data['F_diff'][i + 1] = data['Close'][i + 1] - goods_price - (buy_tax + sell_tax + (2 * 50)) / 200
            # 多單轉空單
            elif data['positions'][i] == -1 and data['positions'][i - 1] == 1:
                sell_tax = data['Close'][i + 1] * tax * 200
                data['F_diff'][i + 1] = data['Close'][i + 1] - goods_price - (buy_tax + sell_tax + (2 * 50)) / 200
                goods_price = data['Close'][i + 1]
                buy_tax = data['Close'][i + 1] * tax * 200
                data['goods_price'][i + 1] = data['Close'][i + 1]
            # 新空單進場
            elif data['positions'][i] == -1 and data['positions'][i - 1] == 0:
                goods_price = data['Close'][i + 1]
                buy_tax = data['Close'][i + 1] * tax * 200
                data['goods_price'][i + 1] = data['Close'][i + 1]
            # 空單平倉
            elif data['positions'][i] == 0 and data['positions'][i - 1] == -1:
                sell_tax = data['Close'][i + 1] * tax * 200
                data['F_diff'][i + 1] = -1 * (data['Close'][i + 1] - goods_price) - (
                            buy_tax + sell_tax + (2 * 50)) / 200
            # 空單轉多單
            elif data['positions'][i] == 1 and data['positions'][i - 1] == -1:
                sell_tax = data['Close'][i + 1] * tax * 200
                data['F_diff'][i + 1] = -1 * (data['Close'][i + 1] - goods_price) - (
                            buy_tax + sell_tax + (2 * 50)) / 200
                goods_price = data['Close'][i + 1]
                buy_tax = data['Close'][i + 1] * tax * 200
                data['goods_price'][i + 1] = data['Close'][i + 1]
                # 多/空/平 單維持
            else:
                pass
        # 最後為 1 / -1 -> 0 此時會超出範圍，不做特殊處理
        except:
            pass

    # 如趨勢連續，則須保留商品購買價讓Holding可以計算
    data['goods_price'][data['goods_price'] == 0] = np.nan
    data.fillna(method='ffill', inplace=True)
    data.fillna(0, inplace=True)
    data['holdings'] = 0
    for i in range(1, len(data)):
        data['holdings'][i] = (data['positions'][i - 1] * (
                    data['Close'][i] - data['goods_price'][i]) * positions * 200) + (
                                          184_000 * abs(data['positions'][i - 1]))

    data['cash'] = 0
    data['cash'][0] = initially
    # 特殊處理第一筆
    if data['positions'][0] != 0:
        data['holdings'][1] = 184_000
        data['cash'][1] = initially - 184_000
    else:
        data['cash'][1] = initially
    for i in range(2, len(data)):
        try:  # 少4種組合
            # 新倉 0 -> 1 -> 0 ; 0 -> -1 -> 0
            if data['positions'][i] == 0 and data['positions'][i - 1] != 0 and data['positions'][i - 2] == 0:
                data['cash'][i] = data['cash'][i - 1] - 184_000
            # 新倉 0 -> 1 -> 1 ; 0 -> 1 -> -1 ; 0 -> -1 -> 1 ; 0 -> -1 -> -1
            elif data['positions'][i] != 0 and data['positions'][i - 1] != 0 and data['positions'][i - 2] == 0:
                data['cash'][i] = data['cash'][i - 1] - 184_000
            #             ## 新倉 -1 -> -1(已經進場) -> 0 ; 1 -> 1(已經進場) -> 0
            #             elif data['positions'][i] == 0 and data['positions'][i-1] != 0 and data['positions'][i-2] != 0 and data['positions'][i-1] == data['positions'][i-2]:
            #                 data['cash'][i] = data['cash'][i-1] - 184_000
            ## 轉倉 -1 -> -1 > 1 ; 1 -> 1 -> -1
            elif data['positions'][i] != 0 and data['positions'][i - 1] == data['positions'][i - 2] and \
                    data['positions'][i - 1] != 0 and data['positions'][i - 2] != 0:
                data['cash'][i] = data['cash'][i - 1] + data['F_diff'][i] * 1 * 200
            # 轉倉 -1 -> 1 -> 1 ; 1 -> -1 -> -1
            elif (data['positions'][i] == data['positions'][i - 1] != 0) and (
                    data['positions'][i - 1] != data['positions'][i - 2] != 0):
                data['cash'][i] = data['cash'][i - 1] + data['F_diff'][i] * 1 * 200
            ## 轉倉 1 -> -1 -> 1 ; -1 -> 1 -> -1
            elif (data['positions'][i] == data['positions'][i - 2]) and data['positions'][i] != 0 and data['positions'][
                i - 2] != 0 and (data['positions'][i - 1] != 0):
                data['cash'][i] = data['cash'][i - 1] + data['F_diff'][i] * 1 * 200
                ## 轉倉 -1 -> 1 -> 0 ; 1 -> -1 -> 0
            elif data['positions'][i] == 0 and data['positions'][i - 1] != 0 and data['positions'][i - 2] != 0 and \
                    data['positions'][i - 1] != data['positions'][i - 2]:
                data['cash'][i] = data['cash'][i - 1] + data['F_diff'][i] * 1 * 200
            # 清倉 1 -> 0 -> 0 ; -1 -> 0 -> 0
            elif data['positions'][i] == 0 and data['positions'][i - 1] == 0 and data['positions'][i - 2] != 0:
                data['cash'][i] = data['cash'][i - 1] + data['F_diff'][i] * 1 * 200 + 184_000
            # 清倉 1 -> 0 -> 1 ; 1 -> 0 -> -1 ; -1 -> 0 -> 1 ; -1 -> 0 -> -1
            elif data['positions'][i] != 0 and data['positions'][i - 1] == 0 and data['positions'][i - 2] != 0:
                data['cash'][i] = data['cash'][i - 1] + data['F_diff'][i] * 1 * 200 + 184_000

            # 空倉 0 -> 0 -> 0 ; 1 -> 1 -> 1 ; -1 -> -1 -> -1; 0 -> 0 -> 1 ; 0 -> 0 -> -1
            else:
                data['cash'][i] = data['cash'][i - 1]
        # 最後為 1 / -1 -> 0 此時會超出範圍，cash = cash[t-1]
        except:
            data['cash'][i] = data['cash'][i - 1]
    data['total_asset'] = data['holdings'] + data['cash']
    data['asset_diff'] = data['total_asset'].diff()
    data['returns'] = data['total_asset'].pct_change()
    return data