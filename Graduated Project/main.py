import pandas as pd
from Create_DF import create_df
from Generate_Table import generate_table
from Linear_Model import linear_tranfer
import warnings
warnings.filterwarnings("ignore")

def main():
    # Load Data
    dfb = pd.read_csv("PL_games.csv")  # 球員1307,其他1687
    dfb = dfb[dfb["Date"] > "2015-08-01"]
    data = create_df(dfb)
    data = data.dropna()
    data = data.reset_index(drop=True)

    # Home Advantage
    HT_h = 1.1

    # Split the Train & Test
    # We use Train to Create Class interval
    train,test, class_interval = generate_table(data,HT_h)

    # Throungh Linear Model
    result = linear_tranfer(data, class_interval, test, HT_h)

    # We got best residual is 0.144639
    print("Best Residual is = " + str(result["每場殘差"].values))

if __name__ == '__main__':
    main()