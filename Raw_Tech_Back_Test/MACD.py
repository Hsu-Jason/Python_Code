import matplotlib.pyplot as plt
import warnings
from utility import *
warnings.filterwarnings('ignore')


# Simple moving average
def macd(signals):
    signals['ma1'] = signals['Close'].rolling(window=ma1, min_periods=1, center=False).mean()
    signals['ma2'] = signals['Close'].rolling(window=ma2, min_periods=1, center=False).mean()
    signals['DIF'] = signals['ma1'] - signals['ma2']
    signals['DEM'] = signals['DIF'].ewm(span=9).mean()
    signals['OSC'] = signals['DIF'] - signals['DEM']
    return signals


def signal_generation(df, method):
    signals = method(df)
    signals['positions'] = 0

    condition_long = np.logical_and(signals['OSC'] >= 0, signals['OSC'].shift() < 0)  # OSC Up to 0, Long Way
    condition_sellshort = np.logical_and(signals['OSC'] <= 0, signals['OSC'].shift() > 0)  # OSC Down to 0, Short Way

    signals['positions'] = np.select([condition_long, condition_sellshort], [1, -1], np.nan)
    signals['positions'].fillna(method="ffill", inplace=True)

    # Down to Average, Stop Long
    condition_sell = np.logical_and(signals['positions'] == 1,
                                    np.logical_and(signals['Close'] <= signals['ma2'],
                                    signals['Close'].shift() > signals['ma2'].shift()))
    # Up to Average, Stop Short
    condition_buytocover = np.logical_and(signals['positions'] == -1,
                                          np.logical_and(signals['Close'] >= signals['ma2'],
                                          signals['Close'].shift() < signals['ma2'].shift()))

    signals['positions'] = np.select([condition_sell, condition_buytocover], [0, 0], signals['positions'])
    signals['signals'] = signals['positions'].diff()
    signals['oscillator'] = signals['ma1'] - signals['ma2']

    return signals

def plot(new, ticker):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.plot(new['Close'], label=ticker)
    ax.plot(new.loc[new['positions'] == 1].index, new['Close'][new['positions'] == 1], label='LONG', lw=0, marker='v',
            c='r')
    ax.plot(new.loc[new['positions'] == -1].index, new['Close'][new['positions'] == -1], label='SHORT', lw=0,
            marker='^', c='g')

    plt.legend(loc='best')
    plt.grid(True)
    plt.title('Positions')

    plt.show()
def main():
    global ma1, ma2, stdate, eddate, ticker, slicer, new, performance_list, portfolio_

    ticker = 'TXF'
    ma1 = 140  # W = 1 7天
    ma2 = 500  # W = 4 25天
    slicer = 501

    df = pd.read_csv("./Data/TXF_2012-01-01_2019-12-31_With_Night_15M.csv")  # 30分資料
    #     df = pd.read_csv("./Data/TXF_2020-01-01_2021-07-31_With_Night_15M.csv")  # 30分資料
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    new = signal_generation(df, macd)
    new = new[slicer:]

    plot(new, ticker)
    portfolio_ = portfolio_mine(new)
    performance_list = performance_mine(portfolio_)


if __name__ == '__main__':
    main()