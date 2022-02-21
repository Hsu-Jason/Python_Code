import numpy as np
import pandas as pd

def generate_table(tem_df,HT_h):

    # To set the upper bound
    tem_df.loc[tem_df["past_h"] >= 135, "past_h"] = 135
    tem_df.loc[tem_df["past_a"] >= 135, "past_a"] = 135


    # Parameter
    tem_df.insert(4, "主隊分數", np.array((((tem_df["主隊積分"] - tem_df['主隊積分'].min()) / (tem_df['主隊積分'].max() - tem_df['主隊積分'].min()) * 100 * 0.7) +
                                ((tem_df["five_h"] - tem_df['five_h'].min()) / (tem_df['five_h'].max() - tem_df['five_h'].min()) * 100 * 0.1) +
                                ((tem_df["AveH"] - tem_df['AveH'].min()) / (tem_df['AveH'].max() - tem_df['AveH'].min()) * 100 * 0.1) +
                                ((tem_df['past_h'] - tem_df['past_h'].min()) / (tem_df['past_h'].max() - tem_df['past_h'].min()) * 100 * 0.1)) * HT_h))

    tem_df.insert(8, "客隊分數", np.array(((tem_df["客隊積分"] - tem_df['客隊積分'].min()) / (tem_df['客隊積分'].max() - tem_df['客隊積分'].min()) * 100 * 0.7) +
                                  ((tem_df["five_a"] - tem_df['five_a'].min()) / (tem_df['five_a'].max() - tem_df['five_a'].min()) * 100 * 0.1) +
                                  ((tem_df["AveA"] - tem_df['AveA'].min()) / (tem_df['AveA'].max() - tem_df['AveA'].min()) * 100 * 0.1) +
                                  ((tem_df['past_a'] - tem_df['past_a'].min()) / (tem_df['past_a'].max() - tem_df['past_a'].min()) * 100 * 0.1)))
    tem_df.insert(4, "分數差", (tem_df["主隊分數"]) - np.array(tem_df["客隊分數"]))

    # Split Train & Test
    train = tem_df[(tem_df["Date"] < "2018-12-27")]
    test = tem_df[(tem_df["Date"] > "2018-12-27")]

    # Create Comparable Table
    rows, num_gap = -1, 20
    up = max(tem_df["分數差"])
    down = min(tem_df["分數差"])
    table = pd.DataFrame()

    mid = up
    while mid > down:
        mid = up - num_gap
        train_tmp = train[(train["分數差"] > mid) & (train["分數差"] <= up)]
        try:
            ser1 = train_tmp.groupby("Div").FTR.value_counts()
            ser2 = ser1.unstack()
            h ,d ,a = 0 ,0 ,0
            if "H" in ser2.columns:
                h += ser2.H[0]
            if "D" in ser2.columns:
                d += ser2.D[0]
            if "A" in ser2.columns:
                a += ser2.A[0]
            total = h + d + a
            table = table.append(pd.Series([mid, up ,h, d, a, total, h / total, d / total, a / total]), ignore_index=True)
            up -= num_gap
            rows += 1
        except:
            up = up - num_gap
            table = table.append(pd.Series([mid, up, 0, 0, 0, 0, 0, 0, 0]), ignore_index=True)
            rows += 1
    table.columns = ["above", "bellow", "H", "A", "D", "Sum", "OH", "OD", "OA"]
    return train,test,table