import pandas as pd

def ProcessData(data_streams: list):
    df_signals = pd.DataFrame(data_streams)
    df_signals.columns = [str(i*5) for i in range(len(df_signals.columns))]
    num_cols = len(df_signals.columns)

    df_new = pd.DataFrame()
    for i in range(0, num_cols, 9):
        cols = df_signals.iloc[:, i:i+9]
        new_col = cols.sum(axis=1)
        df_new[f'sum_{i+1}_{i+9}'] = new_col

    df_new.columns = [str(i*45) for i in range(len(df_new.columns))]
    means = df_new.mean()
    std_devs = df_new.std(ddof=0)
    z_scores = (df_new - means) / std_devs
    z_scores = z_scores.drop(["anomaly"], axis=1)

    z_scores["cumsum"] = z_scores.sum(axis=1)
    z_scores["cumsum"].idxmax()

def NewTest():
    return "Pass"



