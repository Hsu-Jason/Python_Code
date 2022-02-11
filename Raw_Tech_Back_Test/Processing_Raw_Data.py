import pandas as pd

df = pd.read_csv('./Data/TXF_1mins.txt', sep=",")
df.Date = pd.to_datetime(df.Date)
df.Time = pd.to_datetime(df.Time)
df.Time = df.Time.apply(lambda x: str(x.time()))
df = df.set_index(df.Date+df.Time).drop(columns=['Date','Time'])
for col in ['Open', 'High', 'Low', 'Close', 'TotalVolume']:
    df[col] = df[col].astype(float)
# Split Data to 30Mins
data2 = df.resample('30T').agg(dict(zip(df.columns,['first','max','min','last','sum'])))
data2 = data2.dropna()

# Create Training Data
data_train = data2.iloc[31934:72240]
data_train.to_csv('./Data/TXF_2012-01-01_2019-12-31_With_Night_30M.csv')

# Create Test Data
data_test = data2.iloc[72240:]
data_test.to_csv('./Data/TXF_2020-01-01_2021-07-31_With_Night_30M.csv')