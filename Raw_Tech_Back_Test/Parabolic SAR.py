import matplotlib.pyplot as plt
import warnings
from utility import *
import glob
warnings.filterwarnings('ignore')

def parabolic_sar(new):
    initial_af = 0.02
    step_af = 0.02
    end_af = 0.2

    new['trend'] = 0
    new['sar'] = 0.0
    new['real sar'] = 0.0
    new['ep'] = 0.0
    new['af'] = 0.0

    # initial values for recursive calculation
    new['trend'][1] = 1 if new['Close'][1] > new['Close'][0] else -1
    new['sar'][1] = new['High'][0] if new['trend'][1] > 0 else new['Low'][0]
    new.at[1, 'real sar'] = new['sar'][1]
    new['ep'][1] = new['High'][1] if new['trend'][1] > 0 else new['Low'][1]
    new['af'][1] = initial_af

    # calculation
    for i in range(2, len(new)):

        temp = new['sar'][i - 1] + new['af'][i - 1] * (new['ep'][i - 1] - new['sar'][i - 1])
        if new['trend'][i - 1] < 0:
            new.at[i, 'sar'] = max(temp, new['High'][i - 1], new['High'][i - 2])
            temp = 1 if new['sar'][i] < new['High'][i] else new['trend'][i - 1] - 1
        else:
            new.at[i, 'sar'] = min(temp, new['Low'][i - 1], new['Low'][i - 2])
            temp = -1 if new['sar'][i] > new['Low'][i] else new['trend'][i - 1] + 1
        new.at[i, 'trend'] = temp

        if new['trend'][i] < 0:
            temp = min(new['Low'][i], new['ep'][i - 1]) if new['trend'][i] != -1 else new['Low'][i]
        else:
            temp = max(new['High'][i], new['ep'][i - 1]) if new['trend'][i] != 1 else new['High'][i]
        new.at[i, 'ep'] = temp

        if np.abs(new['trend'][i]) == 1:
            temp = new['ep'][i - 1]
            new.at[i, 'af'] = initial_af
        else:
            temp = new['sar'][i]
            if new['ep'][i] == new['ep'][i - 1]:
                new.at[i, 'af'] = new['af'][i - 1]
            else:
                new.at[i, 'af'] = min(end_af, new['af'][i - 1] + step_af)
        new.at[i, 'real sar'] = temp

    return new


def signal_generation(df, method):
    new = method(df)

    new['positions'], new['signals'] = 0, 0
    new['ma'] = new['Close'].rolling(window=60, min_periods=60).mean()

    # Start
    # Peak Stock Price Up to SAR, Long Way
    condition_long = np.logical_and(
        np.logical_and(new['sar'] >= new['real sar'], new['sar'].shift() < new['real sar'].shift()), new['trend'] > 0)
    # Bottom Stock Price Down to SAR, Short Way
    condition_sellshort = np.logical_and(
        np.logical_and(new['sar'] * 1.003 <= new['real sar'], new['sar'].shift() > new['real sar'].shift()),
        new['trend'] < 0)

    new['positions'] = np.select([condition_long, condition_sellshort], [1, -1], np.nan)
    new['positions'].fillna(method="ffill", inplace=True)

    # Down to Average, Stop Long
    condition_sell = np.logical_and(new['positions'] == 1,
                                    np.logical_and(new['Close'] <= new['ma'],
                                                   new['Close'].shift() > new['ma'].shift()))
    # Up to Average, Stop Short
    condition_buytocover = np.logical_and(new['positions'] == -1,
                                          np.logical_and(new['Close'] >= new['ma'],
                                                         new['Close'].shift() < new['ma'].shift()))

    new['positions'] = np.select([condition_sell, condition_buytocover], [0, 0],new['positions'])
    new['signals'] = new['positions'].diff()

    return new

def plot(new, ticker):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    plt.plot(new['Close'], lw=2, label='%s' % ticker)
    plt.plot(new['real sar'], linestyle=':', label='Parabolic SAR', color='k')
    ax.plot(new.loc[new['positions'] == 1].index, new['Close'][new['positions'] == 1], marker='^', color='r',
            label='LONG', lw=0, markersize=5)
    ax.plot(new.loc[new['positions'] == -1].index, new['Close'][new['positions'] == -1], marker='v', color='g',
            label='SHORT', lw=0, markersize=5)

    plt.legend()
    plt.grid(True)
    plt.title('Parabolic SAR')
    plt.ylabel('price')
    plt.show()


def main(name):
    model = "Train" if "Train" in name else "Test"
    slicer = 61
    ticker = 'TXF'
    df = pd.read_csv(name)
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index("Date", inplace=True)
    df.reset_index(inplace=True)

    new = signal_generation(df, parabolic_sar)
    new.set_index(new['Date'], inplace=True)
    new = new[slicer:]
    plot(new, ticker)

    portfolio_ = portfolio_mine(new)
    performance_list = performance_mine(portfolio_)
    portfolio_.to_csv("./usstock_draw/SAR_" + model + ".csv")

if __name__ == '__main__':
    file_name = glob.glob("./Data/TXF_20*")
    for name in file_name:
        main(name)
    # if you wanna use the code to concat
    concat_dataframe("SAR")
