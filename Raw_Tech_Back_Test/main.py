import matplotlib.pyplot as plt
import warnings
from utility import *

warnings.filterwarnings("ignore")
def main():
    # Read Data
    Bolling = pd.read_csv('./usstock_draw/Bolling.csv')
    SAR = pd.read_csv('./usstock_draw/SAR.csv')
    RSI = pd.read_csv('./usstock_draw/RSI.csv')
    Dual_Trust = pd.read_csv('./usstock_draw/Dual_Trust.csv')
    MACD = pd.read_csv('./usstock_draw/MACD.csv')
    FinRL_A2C = pd.read_csv('./usstock_draw/FinRL_A2C.csv')
    MSHRL = pd.read_csv('./usstock_draw/MSHRL.csv')

    # Change Date to Datetime type
    Bolling['date'] = pd.to_datetime(Bolling['date'])
    SAR['date'] = pd.to_datetime(SAR['date'])
    RSI['date'] = pd.to_datetime(RSI['date'])
    Dual_Trust['date'] = pd.to_datetime(Dual_Trust['date'])
    MACD['date'] = pd.to_datetime(MACD['date'])
    FinRL_A2C['date'] = pd.to_datetime(FinRL_A2C['date'])
    MSHRL['date'] = pd.to_datetime(MSHRL['date'])

    # Reset index
    Bolling_data = Bolling[77872:106001].reset_index(drop=True)
    SAR_data = SAR[77872:106001].reset_index(drop=True)
    RSI_data = RSI[77872:106001].reset_index(drop=True)
    Dual_Trust_data = Dual_Trust[77872:106001].reset_index(drop=True)
    MACD_data = MACD[77872:106001].reset_index(drop=True)
    FinRL_A2C_data = FinRL_A2C[77872:106001].reset_index(drop=True)

    # Create diagram
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(Bolling_data['date'], Bolling_data['asset'].values, c='blue', label='SAR')
    ax.plot(SAR_data['date'], SAR_data['asset'].values, c='green', label='Bolling')
    ax.plot(RSI_data['date'], RSI_data['asset'].values, c='black', label='RSI')
    ax.plot(Dual_Trust_data['date'], Dual_Trust_data['asset'].values, c='orange', label='Dual_Thrust')
    ax.plot(MACD_data['date'], MACD_data['asset'].values, c='purple', label='MACD')
    ax.plot(FinRL_A2C_data['date'], FinRL_A2C_data['asset'].values, c='magenta', label='A2C')
    ax.plot(MSHRL['date'], MSHRL['asset'].values, c='sienna', label='MSHRL')
    ax.set_title('Portfolio Value Change')
    ax.set_xlabel("Datetime")
    ax.set_ylabel("Profit", rotation=0)
    ax.legend()
    fig.savefig('Total_Performance.png')
    plt.show()

    # Bolling
    Bolling_data.drop(columns=['total_asset'], inplace=True) # use aseet to replace total_asset
    Bolling_data.columns = ['date', 'positions', 'change', 'total_asset']
    Bolling_data.set_index("date", inplace=True)
    Bolling_data['returns'] = Bolling_data['total_asset'].diff()
    Bolling_LIST = [computeRevenue(Bolling_data), computeAnnualizedReturn(Bolling_data), "-", "-",
                    computeSharpeRatio(Bolling_data), \
                    computeSortinoRatio(Bolling_data), computeMaxDrawdown(Bolling_data), "-", "-", "-", "-", "-"]

    # SAR
    SAR_data.drop(columns=['total_asset'], inplace=True)
    SAR_data.columns = ['date', 'positions', 'change', 'total_asset']
    SAR_data.set_index("date", inplace=True)
    SAR_data['returns'] = SAR_data['total_asset'].diff()
    SAR_LIST = [computeRevenue(SAR_data), computeAnnualizedReturn(SAR_data), "-", "-", computeSharpeRatio(SAR_data), \
                computeSortinoRatio(SAR_data), computeMaxDrawdown(SAR_data), "-", "-", "-", "-", "-"]

    # RSI
    RSI_data.drop(columns=['total_asset'], inplace=True)
    RSI_data.columns = ['date', 'positions', 'change', 'total_asset']
    RSI_data.set_index("date", inplace=True)
    RSI_data['returns'] = RSI_data['total_asset'].pct_change()
    RSI_LIST = [computeRevenue(RSI_data), computeAnnualizedReturn(RSI_data), "-", "-", computeSharpeRatio(RSI_data), \
                computeSortinoRatio(RSI_data), computeMaxDrawdown(RSI_data), "-", "-", "-", "-", "-"]

    # Dual_Trust
    Dual_Trust_data.drop(columns=['total_asset'], inplace=True)
    Dual_Trust_data.columns = ['date', 'positions', 'change', 'total_asset']
    Dual_Trust_data.set_index("date", inplace=True)
    Dual_Trust_data['returns'] = Dual_Trust_data['total_asset'].pct_change()
    Dual_Trust_LIST = [computeRevenue(Dual_Trust_data), computeAnnualizedReturn(Dual_Trust_data), "-", "-",
                       computeSharpeRatio(Dual_Trust_data), \
                       computeSortinoRatio(Dual_Trust_data), computeMaxDrawdown(Dual_Trust_data), "-", "-", "-", "-", "-"]

    # MACD
    MACD_data.drop(columns=['total_asset'], inplace=True)
    MACD_data.columns = ['date', 'positions', 'change', 'total_asset']
    MACD_data.set_index("date", inplace=True)
    MACD_data['returns'] = MACD_data['total_asset'].pct_change()
    MACD_LIST = [computeRevenue(MACD_data), computeAnnualizedReturn(MACD_data), "-", "-", computeSharpeRatio(MACD_data), \
                 computeSortinoRatio(MACD_data), computeMaxDrawdown(MACD_data), "-", "-", "-", "-", "-"]

    # FinRL_A2C
    FinRL_A2C_data.drop(columns=['total_asset'], inplace=True)
    FinRL_A2C_data.columns = ['date', 'positions', 'change', 'total_asset']
    FinRL_A2C_data.set_index("date", inplace=True)
    FinRL_A2C_data['returns'] = FinRL_A2C_data['total_asset'].pct_change()
    FinRL_A2C_LIST = [computeRevenue(FinRL_A2C_data), computeAnnualizedReturn(FinRL_A2C_data), "-", "-",
                      computeSharpeRatio(FinRL_A2C_data), \
                      computeSortinoRatio(FinRL_A2C_data), computeMaxDrawdown(FinRL_A2C_data), "-", "-", "-", "-", "-"]

    #MSHRL
    MSHRL.columns = ['date', 'total_asset']
    MSHRL.set_index("date", inplace=True)
    MSHRL['returns'] = MSHRL['total_asset'].pct_change()
    MSHRL_LIST = [computeRevenue(MSHRL), computeAnnualizedReturn(MSHRL), "-", "-", computeSharpeRatio(MSHRL), \
                  computeSortinoRatio(MSHRL), computeMaxDrawdown(MSHRL), "-", "-", "-", "-", "-"]

    # Create DataFrame
    data = [np.array(Bolling_LIST).reshape(12),
            np.array(SAR_LIST).reshape(12),
            np.array(RSI_LIST).reshape(12),
            np.array(Dual_Trust_LIST).reshape(12),
            np.array(MACD_LIST).reshape(12),
            np.array(FinRL_A2C_LIST).reshape(12),
            np.array(MSHRL_LIST).reshape(12)]

    Performace = pd.DataFrame(data, index=['Bolling', 'SAR', 'RSI', 'Dual_Trust', 'MACD', 'A2C', "MSHRL"],
                              columns=["Revenue", "AnnualizedReturn", "AnnualizedVolatility", "ShortLongProfit", \
                                       "SharpeRatio", "SortinoRatio", "MaxDrawdown",
                                       "Win_Loss_Ratio / averageProfitLossRatio", "Skewness", "Positive", "Negative",
                                       "Neural"]).T
    print(Performace)

if __name__ == '__main__':
    main()
