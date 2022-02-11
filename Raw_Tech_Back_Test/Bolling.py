import matplotlib.pyplot as plt
import copy
from utility import *
import warnings
warnings.filterwarnings("ignore")


# first step is to calculate moving average and moving standard deviation
# we plus/minus three/two standard deviations on moving average
# we get our upper, mid, lower bands
def bollinger_bands(df):
    num = 280
    data = copy.deepcopy(df)
    data['std'] = data['Close'].rolling(window=num, min_periods=num).std()
    data['mid band'] = data['Close'].rolling(window=num, min_periods=num).mean()
    data['upper band'] = data['mid band'] + 3 * data['std']
    data['lower band'] = data['mid band'] - 2 * data['std']
    return data


def signal_generation_mine(data, method):
    df = method(data)
    condition_long = np.logical_and(df['Close'] >= df['lower band'],
                                 df['Close'].shift() < df['lower band'].shift())  # Up to Down, Long Way
    condition_short = np.logical_and(df['Close'] <= df['upper band'],
                                 df['Close'].shift() > df['upper band'].shift())  # Down to Up, Short Way

    df['signal_position'] = np.select([condition_long, condition_short], [1, -1], np.nan)
    df['signal_position'].fillna(method="ffill", inplace=True)

    # Down to Mid, Stop Long
    condition1 = np.logical_and(df['signal_position'] == 1, np.logical_and(df['Close'] <= df['mid band'],
                                                                      df['Close'].shift() > df['mid band'].shift()))
    # Up to Mid, Stop Short
    condition2 = np.logical_and(df['signal_position'] == -1, np.logical_and(df['Close'] >= df['mid band'],
                                                                       df['Close'].shift() < df['mid band'].shift()))

    df['positions'] = np.select([condition1, condition2], [0, 0], df['signal_position'])
    df['signals'] = df['positions'].diff()

    return df


def plot_mine(new, ticker):
    # the first plot is the actual close price with long/short signal_position
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

    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.plot(new['Close'], label=ticker)
    ax.plot(new['lower band'])
    ax.plot(new['upper band'])

    plt.legend(loc='best')
    plt.title('Bollinger bands')

    plt.show()


def main():
    global new, portfolio_, performance_list, df
    slicer = 281
    ticker = 'TXF'
    #     df = pd.read_csv('TXF_2012-01-01_2019-12-31_With_Night_15M.csv')
    df = pd.read_csv('./Data/TXF_2020-01-01_2021-07-31_With_Night_15M.csv')
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    df.reset_index(inplace=True)
    new = signal_generation_mine(df, bollinger_bands)
    new = new[slicer:]
    plot_mine(new, ticker)
    new['Date'] = pd.to_datetime(new['Date'])
    new.set_index('Date', inplace=True)
    portfolio_ = portfolio_mine(new)
    performance_list = performance_mine(portfolio_)

if __name__ == '__main__':
    main()