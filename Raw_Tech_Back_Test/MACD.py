import matplotlib.pyplot as plt
import warnings
from utility import *
import glob
warnings.filterwarnings('ignore')


# Simple moving average
def macd(signals,ma1,ma2):
    signals['ma1'] = signals['Close'].rolling(window=ma1, min_periods=1, center=False).mean()
    signals['ma2'] = signals['Close'].rolling(window=ma2, min_periods=1, center=False).mean()
    signals['DIF'] = signals['ma1'] - signals['ma2']
    signals['DEM'] = signals['DIF'].ewm(span=9).mean()
    signals['OSC'] = signals['DIF'] - signals['DEM']
    return signals


def signal_generation(df, method,ma1,ma2):
    signals = method(df,ma1,ma2)
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
def main(name):
    model = "Train" if "Train" in name else "Test"
    ticker = 'TXF'
    ma1 = 140  # W = 1 7天
    ma2 = 500  # W = 4 25天
    slicer = 501

    df = pd.read_csv(name)
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    new = signal_generation(df, macd,ma1,ma2)
    new = new[slicer:]

    plot(new, ticker)
    portfolio_ = portfolio_mine(new)
    performance_list = performance_mine(portfolio_)
    portfolio_.to_csv("./usstock_draw/MACD_" + model + ".csv")


if __name__ == '__main__':
    file_name = glob.glob("./Data/TXF_20*")
    for name in file_name:
        main(name)
    # if you wanna use the code to concat
    concat_dataframe("MACD")