import yfinance as yf
import pandas as pd
tickets = ["BAC", "C", "JPM", "WFC"]






def load(date):
    df = pd.read_csv("union.csv")
    #df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d 00:00:00')
    df.index = pd.to_datetime(df['date'])
    df = df.iloc[::-1]
    new_df = pd.DataFrame()
    for t in tickets:
        data = yf.download(t, start=date)
        if t == "C":
            new_df["Citi_Close"] = data["Close"]
        else:
            new_df[t + "_Close"] = data["Close"]

    print(new_df.index)
    print(df.index)
    new_df.index.rename('date', inplace=True)
    df = pd.concat([df, new_df])
    # df = pd.merge(new_df, df,  left_index=True, right_index=True, how='outer')
    df.fillna(method='ffill', inplace=True)
    df = df.drop("date", axis=1)
    print(df.columns)
    df.to_csv('combined_dataset.csv')
    




load("2023-11-01")