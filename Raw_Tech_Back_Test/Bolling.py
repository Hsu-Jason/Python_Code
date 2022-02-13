import matplotlib.pyplot as plt
import copy
import pandas as pd
from utility import *
import warnings
import glob
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


def plot_mine(new, ticker, model):
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
    plt.title('Positions ' + model)

    plt.show()

    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.plot(new['Close'], label=ticker)
    ax.plot(new['lower band'], label = 'lower band')
    ax.plot(new['upper band'], label = 'upper band')

    plt.legend(loc='best')
    plt.title('Bollinger bands')

    plt.show()


def main(name):
    model = "Train" if "Train" in name else "Test"
    slicer = 281
    ticker = 'TXF'
    df = pd.read_csv(name)
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    df.reset_index(inplace=True)
    new = signal_generation_mine(df, bollinger_bands)
    new = new[slicer:]
    plot_mine(new, ticker, model)
    new['Date'] = pd.to_datetime(new['Date'])
    new.set_index('Date', inplace=True)
    portfolio_ = portfolio_mine(new)
    performance_list = performance_mine(portfolio_)
    portfolio_.to_csv("./usstock_draw/Bolling_" + model + ".csv")
    return portfolio_
if __name__ == '__main__':
    file_name = glob.glob("./Data/TXF_20*")
    for name in file_name:
        main(name)
    # if you wanna use the code to concat
    concat_dataframe("Bolling")