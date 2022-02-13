import matplotlib.pyplot as plt
import warnings
from utility import *
import glob
warnings.filterwarnings('ignore')

def smma(series, n):
    output = [series[0]]

    for i in range(1, len(series)):
        temp = output[-1] * (n - 1) + series[i]
        output.append(temp / n)

    return output


def rsi(data, n=10):
    delta = data.diff().dropna()

    up = np.where(delta > 0, delta, 0)
    down = np.where(delta < 0, -delta, 0)

    rs = np.divide(smma(up, n), smma(down, n))

    # Similar RSI calculation way, Original one is (up / (up+down) * 100)
    output = 100 - 100 / (1 + rs)
    return output[n - 1:]


def signal_generation(df, method, n, rsi_down=30, rsi_up=70):
    df['rsi'] = 0.0
    df['rsi'][n:] = method(df['Close'], n)
    condition_long = np.logical_and(df['rsi'] <= rsi_down, df['rsi'].shift() > rsi_down)  # rsi < 45, Long Way
    condition_sellshort = np.logical_and(df['rsi'] >= rsi_up, df['rsi'].shift() < rsi_up)  # rsi > 60, Short Way
    df['ma'] = df['Close'].rolling(window=n, min_periods=n).mean()

    df['positions'] = np.select([condition_long, condition_sellshort], [1, -1], np.nan)
    df['positions'].fillna(method="ffill", inplace=True)

    # Down to Average, Stop Long
    condition_sell = np.logical_and(df['positions'] == 1,
                                    np.logical_and(df['Close'] <= df['ma'], df['Close'].shift() > df['ma'].shift()))
    # Up to Average, Stop Short
    condition_buytocover = np.logical_and(df['positions'] == -1, np.logical_and(df['Close'] >= df['ma'],
                                                                                df['Close'].shift() < df['ma'].shift()))

    df['positions'] = np.select([condition_sell, condition_buytocover], [0, 0], df['positions'])
    df['signals'] = df['positions'].diff()

    return df[n:]

def plot(new, ticker):
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111)

    ax.plot(new['Close'], label=ticker)
    ax.plot(new.loc[new['positions'] == 1].index, new['Close'][new['positions'] == 1], label='LONG', lw=0, marker='v',
            c='r')
    ax.plot(new.loc[new['positions'] == -1].index, new['Close'][new['positions'] == -1], label='SHORT', lw=0,
            marker='^', c='g')

    plt.legend(loc='best')
    plt.grid(True)
    plt.title('Positions')
    plt.xlabel('Date')
    plt.ylabel('price')

    plt.show()

    # the second plot is rsi with overbought/oversold interval capped at 45/60
    bx = plt.figure(figsize=(10, 10)).add_subplot(111, sharex=ax)
    bx.plot(new['rsi'], label='relative strength index', color='b')
    bx.fill_between(new.index,  60, 45, alpha=0.5, color='r')

    # TODO -30 is not the correct place to overbought / oversold
    bx.text(new.index[-20], 60, 'overbought', color='black', size=12.5)
    bx.text(new.index[-20], 45, 'oversold', color='black', size=12.5)

    plt.xlabel('Date',  fontsize = 10)
    plt.ylabel('value', fontsize = 10)
    plt.title('RSI', fontsize = 10)
    plt.legend(loc='best')
    plt.grid(True)
    plt.show()

def main(name):
    model = "Train" if "Train" in name else "Test"
    ticker = "TXF"
    rsi_up = 60
    rsi_down = 45
    slicer = 141
    df = pd.read_csv(name)
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)

    new = signal_generation(df, rsi, n=140, rsi_down=rsi_down, rsi_up=rsi_up)
    new = new[slicer:]
    plot(new, ticker)

    portfolio_ = portfolio_mine(new)
    performance_list = performance_mine(portfolio_)
    portfolio_.to_csv("./usstock_draw/RSI_" + model + ".csv")

if __name__ == '__main__':
    file_name = glob.glob("./Data/TXF_20*")
    for name in file_name:
        main(name)
    # if you wanna use the code to concat
    concat_dataframe("RSI")

