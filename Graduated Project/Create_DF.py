import pandas as pd
import re

def create_df(dfb):
    dfb[['PSH', 'PSD', 'PSA']] = 1 / dfb[['PSH', 'PSD', 'PSA']]
    total_prob = dfb.PSH + dfb.PSD + dfb.PSA
    dfb.PSH = dfb.PSH / total_prob
    dfb.PSD = dfb.PSD / total_prob
    dfb.PSA = dfb.PSA / total_prob
    dfb["Date"] = pd.to_datetime(dfb["Date"], dayfirst=True)
    dfb.sort_values(by=["Date"], inplace=True, ascending=False)
    dfb = dfb.reset_index(drop=True)

    # Win = 3 scores ; Draw = 1 scores ; Loss = 0 scores
    cal_w, cal_d, cal_l = 3, 1, 0
    # Win 15 scores ; Draw 5 scores ; Loss 0 scores
    five_w, five_d, five_l = 15, 5, 0
    # Win 20 scores ; Draw 10 scores ; Loss 5 scores
    three_w, three_d, three_l = 20, 10, 5

    # Consider the team's close five games, more closer more realated, will have more multiplier
    cross_five = {0: 1, 1: 0.8, 2: 0.6, 3: 0.4, 4: 0.2}
    # Consider the team's close three games with specific team, more closer more realated, will have more multiplier
    cross_three = {0: 3, 1: 2.5, 2: 2}

    # Store Close five Games
    five_h = pd.DataFrame()
    five_a = pd.DataFrame()

    # Store Past Games
    past_h = pd.DataFrame()
    past_a = pd.DataFrame()

    # Store Home Team / Away Team
    games_h = pd.DataFrame()
    games_a = pd.DataFrame()
    dfb["Mem_plus_H"] = 0
    dfb["Mem_plus_A"] = 0

    # Preprocessinhg Player Columns
    # exist_player_number = len(dfb.dropna())
    # for idx in range(exist_player_number):
    #     dfb["homenamesmapped"][idx] = re.sub(r'[[]]', "", dfb["homenamesmapped"][idx]).split(',')
    #     dfb["awaynamesmapped"][idx] = re.sub(r'[[]]', "", dfb["awaynamesmapped"][idx]).split(',')

    for idx2 in range(1307):
        dfb["homenamesmapped"][idx2] = re.sub('[[]', "", dfb["homenamesmapped"][idx2])
        dfb["homenamesmapped"][idx2] = re.sub('[]]', "", dfb["homenamesmapped"][idx2])
        dfb["awaynamesmapped"][idx2] = re.sub('[[]', "", dfb["awaynamesmapped"][idx2])
        dfb["awaynamesmapped"][idx2] = re.sub('[]]', "", dfb["awaynamesmapped"][idx2])
        dfb['homenamesmapped'][idx2] = str(dfb['homenamesmapped'][idx2]).split(',')
        dfb['awaynamesmapped'][idx2] = str(dfb['awaynamesmapped'][idx2]).split(',')

    # Calculate Teams' scores
    for idx2 in range(1687):

        # Process HomeTeam
        h3 = dfb.iloc[idx2 + 1:]
        h = h3[(h3["HomeTeam"] == dfb.HomeTeam[idx2]) | (h3["AwayTeam"] == dfb.HomeTeam[idx2])].head(38)
        h.reset_index(inplace=True)
        gs, w, d, l, sc, scl, psc, ac = 0, 0, 0, 0, 0, 0, 0, 0
        for idx in range(38):
            try:
                if h.HomeTeam[idx] == dfb.HomeTeam[idx2]:
                    if h.FTR[idx] == "H":
                        w += 1
                        sc += h.FTHG[idx]
                        scl += h.FTAG[idx]
                        psc = sc - scl
                        gs += 1

                    elif h.FTR[idx] == "A":
                        l += 1
                        sc += h.FTHG[idx]
                        scl += h.FTAG[idx]
                        psc = sc - scl
                        gs += 1
                    else:
                        d += 1
                        sc = sc + h.FTHG[idx]
                        scl = scl + h.FTAG[idx]
                        psc = sc - scl
                        gs += 1
                else:
                    if h.FTR[idx] == "A":
                        w += 1
                        sc += h.FTAG[idx]
                        scl += h.FTHG[idx]
                        psc = sc - scl
                        gs += 1
                    elif h.FTR[idx] == "H":
                        l += 1
                        sc += h.FTAG[idx]
                        scl += h.FTHG[idx]
                        psc = sc - scl
                        gs += 1
                    else:
                        d += 1
                        sc += h.FTAG[idx]
                        scl += h.FTHG[idx]
                        psc = sc - scl
                        gs += 1

                pass
            except:
                break
        ac = w * cal_w + d * cal_d + l * cal_l
        if gs == 38: games_h = games_h.append(
            pd.Series([dfb.Date[idx2], dfb.HomeTeam[idx2], gs, w, d, l, sc, scl, psc, ac]), ignore_index=True)

        # Process AwayTeam
        h = h3[(h3["HomeTeam"] == dfb.AwayTeam[idx2]) | (h3["AwayTeam"] == dfb.AwayTeam[idx2])].head(38)
        h.reset_index(inplace=True)
        gs, w, d, l, sc, scl, psc, ac = 0, 0, 0, 0, 0, 0, 0, 0

        for idx in range(38):
            try:
                if h.HomeTeam[idx] == dfb.AwayTeam[idx2]:
                    if h.FTHG[idx] > h.FTAG[idx]:
                        w += 1
                        sc += h.FTHG[idx]
                        scl += h.FTAG[idx]
                        psc = sc - scl
                        gs += 1

                    elif h.FTHG[idx] < h.FTAG[idx]:
                        l += 1
                        sc += h.FTHG[idx]
                        scl += h.FTAG[idx]
                        psc = sc - scl
                        gs += 1
                    else:
                        d += 1
                        sc += h.FTHG[idx]
                        scl += h.FTAG[idx]
                        psc = sc - scl
                        gs += 1
                else:
                    if h.FTHG[idx] < h.FTAG[idx]:
                        w += 1
                        sc += h.FTAG[idx]
                        scl += h.FTHG[idx]
                        psc = sc - scl
                        gs += 1
                    elif h.FTHG[idx] > h.FTAG[idx]:
                        l += 1
                        sc += h.FTAG[idx]
                        scl += h.FTHG[idx]
                        psc = sc - scl
                        gs += 1
                    else:
                        d += 1
                        sc += h.FTAG[idx]
                        scl += h.FTHG[idx]
                        psc = sc - scl
                        gs += 1
                    pass
            except:
                break
        ac = w * cal_w + d * cal_d + l * cal_l
        if gs == 38: games_a = games_a.append(
            pd.Series([dfb.Date[idx2], dfb.AwayTeam[idx2], gs, w, d, l, sc, scl, psc, ac]), ignore_index=True)

    games_h.columns = ["Date", "HomeTeam", "場次", "勝", "平", "敗", "進球", "失球", "淨勝", "主隊積分"]
    games_a.columns = ["Date", "AwayTeam", "場次", "勝", "平", "敗", "進球", "失球", "淨勝", "客隊積分"]
    dfb = dfb.merge(games_h[["Date", "HomeTeam", "主隊積分"]], on=["Date", "HomeTeam"], how="left")
    dfb = dfb.merge(games_a[["Date", "AwayTeam", "客隊積分"]], on=["Date", "AwayTeam"], how="left")

    for idx2 in range(len(dfb)):

        h3 = dfb.iloc[idx2 + 1:]
        h = h3[(h3["HomeTeam"] == dfb.HomeTeam[idx2]) | (h3["AwayTeam"] == dfb.HomeTeam[idx2])].head(10)
        h.reset_index(inplace=True)
        a = [dfb.Date[idx2], dfb.HomeTeam[idx2], "", "", "", "", "", "", ""]
        count, point = 0, 0

        for idx in range(5):
            p = cross_five.get(idx)
            try:
                if h.HomeTeam[idx] == dfb.HomeTeam[idx2]:
                    count = count + 1
                    if h.FTHG[idx] > h.FTAG[idx]:
                        a[idx + 2] = "w"
                        point += five_w * p
                    elif h.FTHG[idx] < h.FTAG[idx]:
                        a[idx + 2] = "l"
                        point += five_l * p
                    else:
                        a[idx + 2] = "e"
                        point += five_d * p
                else:
                    count = count + 1
                    if h.FTHG[idx] < h.FTAG[idx]:
                        a[idx + 2] = "w"
                        point += five_w * p
                    elif h.FTHG[idx] > h.FTAG[idx]:
                        a[idx + 2] = "l"
                        point += five_l * p
                    else:
                        a[idx + 2] = "e"
                        point += five_d * p
            except:
                break

        a[7] = point
        a[8] = count
        if count == 5:
            five_h = five_h.append(pd.Series(a), ignore_index=True)

        # Store team's all members in five games( will repeat)
        temp_list = []

        for i in range(len(h)):
            # Some Members will face the problem of missing
            try:
                for j in range(len(h['homenamesmapped'][i])):
                    temp_list.append(h['homenamesmapped'][i][j]) if h.HomeTeam[i] == dfb.HomeTeam[
                        idx2] else temp_list.append(h['awaynamesmapped'][i][j])
            except:
                pass

        mem_plus = 0
        # Some Members will face the problem of missing
        try:
            for j in range(len(dfb['homenamesmapped'][idx2])):
                temp_mem_plus = temp_list.count(dfb['homenamesmapped'][idx2][j])
                if temp_mem_plus >= 5: mem_plus += 1
            dfb["Mem_plus_H"][idx2] = mem_plus
        except:
            pass

        h = h3[(h3["HomeTeam"] == dfb.AwayTeam[idx2]) | (h3["AwayTeam"] == dfb.AwayTeam[idx2])].head(10)
        h.reset_index(inplace=True)

        a = [dfb.Date[idx2], dfb.AwayTeam[idx2], 2, 3, 4, 5, 6, 7, 8]
        point, count = 0, 0
        for idx in range(5):
            p = cross_five.get(idx)
            # Try Except to avoid some teams haven't played more than 5 games
            try:
                if h.HomeTeam[idx] == dfb.AwayTeam[idx2]:
                    count = count + 1
                    if h.FTHG[idx] > h.FTAG[idx]:
                        a[idx + 2] = "w"
                        point += five_w * p
                    elif h.FTHG[idx] < h.FTAG[idx]:
                        a[idx + 2] = "l"
                        point += five_l * p
                    else:
                        a[idx + 2] = "e"
                        point += five_d * p
                else:
                    count = count + 1
                    if h.FTHG[idx] < h.FTAG[idx]:
                        a[idx + 2] = "w"
                        point += five_w * p
                    elif h.FTHG[idx] > h.FTAG[idx]:
                        a[idx + 2] = "l"
                        point += five_l * p
                    else:
                        a[idx + 2] = "e"
                        point += five_d * p
            except:
                break
        a[7] = point
        a[8] = count
        if count == 5:
            five_a = five_a.append(pd.Series(a), ignore_index=True)

        temp_list = []  # 該隊伍5場內所有球員（會重複）

        for i in range(len(h)):
            try:
                for j in range(len(h['awaynamesmapped'][i])):
                    temp_list.append(h['homenamesmapped'][i][j]) if h.HomeTeam[i] == dfb.AwayTeam[
                        idx2] else temp_list.append(h['awaynamesmapped'][i][j])
            except:
                pass

        mem_plus = 0
        try:
            for j in range(len(dfb['awaynamesmapped'][idx2])):
                temp_mem_plus = temp_list.count(dfb['awaynamesmapped'][idx2][j])
                if temp_mem_plus >= 5:
                    mem_plus += 1
            dfb["Mem_plus_A"][idx2] = mem_plus
        except:
            pass

        # Close Three Games, Calculate the Same Teams to Fight
        h1 = h3["HomeTeam"] == dfb.HomeTeam[idx2]
        h2 = h3["AwayTeam"] == dfb.AwayTeam[idx2]
        h5 = h3["HomeTeam"] == dfb.AwayTeam[idx2]
        h6 = h3["AwayTeam"] == dfb.HomeTeam[idx2]
        h = h3[(h1 & h2) | (h5 & h6)]
        h.reset_index(inplace=True)

        a = [dfb.Date[idx2], dfb.HomeTeam[idx2], 2, 3, 4, 5, 6, 7, 8]
        point, count = 0, 0
        for idx in range(3):
            P_P = cross_three.get(idx)
            try:
                if h.HomeTeam[idx] == dfb.HomeTeam[idx2]:
                    count += 1
                    if h.FTHG[idx] > h.FTAG[idx]:
                        a[idx + 2] = "w"
                        point += three_w * P_P
                    elif h.FTHG[idx] < h.FTAG[idx]:
                        a[idx + 2] = "l"
                        point -= three_l * P_P
                    else:
                        a[idx + 2] = "e"
                        point += three_d * P_P
                else:
                    count += 1
                    if h.FTHG[idx] < h.FTAG[idx]:
                        a[idx + 2] = "w"
                        point += three_w * P_P
                    elif h.FTHG[idx] > h.FTAG[idx]:
                        a[idx + 2] = "l"
                        point -= three_l * P_P
                    else:
                        a[idx + 2] = "e"
                        point += three_d * P_P
            except:
                break
        a[7] = point
        a[8] = count
        if count == 3:
            past_h = past_h.append(pd.Series(a), ignore_index=True)

        a = [dfb.Date[idx2], dfb.AwayTeam[idx2], 2, 3, 4, 5, 6, 7, 8]
        point, count = 0, 0
        for idx in range(3):
            P_P = cross_three.get(idx)
            try:
                if h.HomeTeam[idx] == dfb.AwayTeam[idx2]:
                    count += 1
                    if h.FTHG[idx] > h.FTAG[idx]:
                        a[idx + 2] = "w"
                        point += three_w * P_P
                    elif h.FTHG[idx] < h.FTAG[idx]:
                        a[idx + 2] = "l"
                        point -= three_l * P_P
                    else:
                        a[idx + 2] = "e"
                        point += three_d * P_P
                else:
                    count += 1
                    if h.FTHG[idx] < h.FTAG[idx]:
                        a[idx + 2] = "w"
                        point += three_w * P_P
                    elif h.FTHG[idx] > h.FTAG[idx]:
                        a[idx + 2] = "l"
                        point -= three_l * P_P
                    else:
                        a[idx + 2] = "e"
                        point += three_d * P_P
            except:
                break
        a[7] = point
        a[8] = count
        if count == 3:
            past_a = past_a.append(pd.Series(a), ignore_index=True)

    five_h.columns = ["Date", "HomeTeam", "1", "2", "3", "4", "5", "five_h", "play"]
    five_a.columns = ["Date", "AwayTeam", "1", "2", "3", "4", "5", "five_a", "play"]
    past_h.columns = ["Date", "HomeTeam", "1", "2", "3", "4", "5", "past_h", "play"]
    past_a.columns = ["Date", "AwayTeam", "1", "2", "3", "4", "5", "past_a", "play"]
    dfb = dfb.merge(five_h[["Date", "HomeTeam", "five_h"]], on=["Date", "HomeTeam"], how="left")
    dfb = dfb.merge(five_a[["Date", "AwayTeam", "five_a"]], on=["Date", "AwayTeam"], how="left")
    dfb = dfb.merge(past_h[["Date", "HomeTeam", "past_h"]], on=["Date", "HomeTeam"], how="left")
    dfb = dfb.merge(past_a[["Date", "AwayTeam", "past_a"]], on=["Date", "AwayTeam"], how="left")
    dfb['AveH'] += dfb['Mem_plus_H']
    dfb['AveA'] += dfb['Mem_plus_A']
    return dfb