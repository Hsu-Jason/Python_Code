import numpy as np
import pandas as pd
from sklearn import linear_model
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

def linear_tranfer(tem_df,table,test, HT_h):
    # Linear Model
    X = np.array((table['above'] + table['bellow']) / 2).reshape((-1, 1))
    y_OH = np.array(table["OH"]).reshape((-1,1))
    y_OD = np.array(table["OD"]).reshape((-1,1))

    scores = test.分數差.values
    value_bellow = table.bellow.values
    value_above = table.above.values
    i, j = np.where((scores[:, None] >= value_above) & (scores[:, None] < value_bellow))
    res = pd.DataFrame(np.column_stack([test.values[i], table.values[j]]), columns=test.columns.append(table.columns))

    # Ternary Linear Regression -> OH
    model = make_pipeline(PolynomialFeatures(3), linear_model.LinearRegression())
    model.fit(X, y_OH)

    res_score = np.array(res.分數差.values).reshape(-1, 1)
    res["OH"] = model.predict(res_score)

    # Bivariate Linear Regression -> OD
    model = make_pipeline(PolynomialFeatures(2), linear_model.LinearRegression())
    model.fit(X,y_OD)

    res_score = np.array(res.分數差.values).reshape(-1, 1)
    res["OD"] = model.predict(res_score)
    res["OA"] = 1 - res["OH"] - res["OD"]

    # Infinite Upper & Lower Bounder
    table["bellow"][0] = table["bellow"][0] + 1000
    table.iloc[-1, 1] = table.iloc[-1, 1] - 1000

    res["ph"] = ((HT_h - 1) * (((tem_df["主隊積分"] - tem_df['主隊積分'].min()) / (tem_df['主隊積分'].max() - tem_df['主隊積分'].min()) * 100 * 0.6) +
                ((tem_df["five_h"] - tem_df['five_h'].min()) / (tem_df['five_h'].max() - tem_df['five_h'].min()) * 100 * 0.2) +
                ((tem_df["AveH"] - tem_df['AveH'].min()) / (tem_df['AveH'].max() - tem_df['AveH'].min()) * 100 * 0.1) +
                ((tem_df['past_h'] - tem_df['past_h'].min()) / (tem_df['past_h'].max() - tem_df['past_h'].min()) * 100 * 0.1))) / res.主隊分數
    res["phs"] = ((tem_df["主隊積分"] - tem_df['主隊積分'].min()) / (tem_df['主隊積分'].max() - tem_df['主隊積分'].min()) * 100 * 0.6) / res.主隊分數
    res["pas"] = ((tem_df["客隊積分"] - tem_df['客隊積分'].min()) / (tem_df['客隊積分'].max() - tem_df['客隊積分'].min()) * 100 * 0.6) / res.客隊分數
    res["phf"] = abs(((tem_df["five_h"] - tem_df['five_h'].min()) / (tem_df['five_h'].max() - tem_df['five_h'].min()) * 100 * 0.2) / res.主隊分數)
    res["paf"] = abs(((tem_df["five_a"] - tem_df['five_a'].min()) / (tem_df['five_a'].max() - tem_df['five_a'].min()) * 100 * 0.2) / res.客隊分數)
    res["phm"] = ((tem_df["AveH"] - tem_df['AveH'].min()) / (tem_df['AveH'].max() - tem_df['AveH'].min()) * 100 * 0.1) / res.主隊分數
    res["pam"] = ((tem_df["AveA"] - tem_df['AveA'].min()) / (tem_df['AveA'].max() - tem_df['AveA'].min()) * 100 * 0.1) / res.客隊分數
    res["phta"] = ((tem_df['past_h'] - tem_df['past_h'].min()) / (tem_df['past_h'].max() - tem_df['past_h'].min()) * 100 * 0.1) / res.主隊分數
    res["pata"] = ((tem_df['past_a'] - tem_df['past_a'].min()) / (tem_df['past_a'].max() - tem_df['past_a'].min()) * 100 * 0.1) / res.客隊分數
    res["Hdiff"] = abs(res.PSH - res.OH)
    res["Adiff"] = abs(res.PSA - res.OA)
    res["Ddiff"] = abs(res.PSD - res.OD)
    res["Sdiff"] = abs(res.Hdiff + res.Ddiff + res.Adiff)

    result = 1000
    if np.mean(res["Sdiff"]) < result:
        result = np.mean(res["Sdiff"])
        best = {}
        best['主隊優勢乘數'] = HT_h
        best['積分占比'] = 0.7
        best['近五場占比'] = 0.1
        best['球員占比'] = 0.1
        best['隊伍占比'] = 0.1
        best['每場殘差'] = result
        best['主隊積分'] = round(np.mean(res["phs"]), 4)
        best['主隊優勢'] = round(np.mean(res["ph"]), 4)
        best['主隊近五場'] = round(np.mean(res["phf"]), 4)
        best['主隊球員'] = round(np.mean(res["phm"]), 4)
        best['主隊隊伍'] = round(np.mean(res["phta"]), 4)
        best['客隊積分'] = round(np.mean(res["pas"]), 4)
        best['客隊近五場'] = round(np.mean(res["paf"]), 4)
        best['客隊球員'] = round(np.mean(res["pam"]), 4)
        best['客隊隊伍'] = round(np.mean(res["pata"]), 4)
    return pd.DataFrame(best, index=[0])