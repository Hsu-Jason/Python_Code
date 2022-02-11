import matplotlib.pyplot as plt
import warnings
from utility import *
warnings.simplefilter('ignore')


# Simple moving average
def duel_trust(signals, ks, kx):
    signals['up_line'] = signals['Open'] + (signals['range'] * ks)
    signals['down_line'] = signals['Open'] - (signals['range'] * kx)

    return signals


def signal_generation(df, method, cycle, ks, kx, a_long, a_short):
    signals = method(df, ks, kx)
    signals['positions'] = 0

    # positions becomes and stays one once the short moving average is above long moving average
    signals['positions'] = np.select(
        [signals['up_line'] * a_long <= signals['Close'], signals['down_line'] * a_short >= signals['Close']]
        , [1, -1], default=0)
    # Row n's position should be n-1
    Positions_list = list(signals['positions'].values)
    Positions_list.pop(-1)
    Positions_list.insert(0, 0)
    signals['positions'] = Positions_list
    signals['signals'] = signals['positions'].diff()
    signals['oscillator'] = signals['up_line'] - signals['down_line']

    return signals


# plotting the backtesting result
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
    global stdate, eddate, ticker, slicer, new, performance_list, portfolio_

    # Adjust parameters
    cycle = 10
    ks = 1
    kx = 3
    a_long = 0.996
    a_short = 1.006
    slicer = 11
    ticker = 'TXF'
    # df = pd.read_csv('./Data/TXF_2012-01-01_2019-12-31_With_Night_15M.csv')
    df = pd.read_csv('./Data/TXF_2020-01-01_2021-07-31_With_Night_15M.csv')
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df['HH'] = df['High'].rolling(window=cycle, center=False, closed="left").max()
    df['LC'] = df['Close'].rolling(window=cycle, center=False, closed="left").min()
    df['HC'] = df['Close'].rolling(window=cycle, center=False, closed="left").max()
    df['LL'] = df['Low'].rolling(window=cycle, center=False, closed="left").min()
    df.fillna(0, inplace=True)
    df['range'] = np.where((df['HH'] - df['LC']) > (df['HC'] - df['LL']), df['HH'] - df['LC'], df['HC'] - df['LL'])

    new = signal_generation(df, duel_trust, cycle, ks, kx, a_long, a_short)
    new = new[slicer:]
    plot(new, ticker)
    portfolio_ = portfolio_mine(new)
    performance_list = performance_mine(portfolio_)

if __name__ == '__main__':
    main()