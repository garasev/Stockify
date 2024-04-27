from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt
import pandas as pd
import base64
import io

df = pd.read_csv("union.csv")
forecast_df = pd.read_csv("last_forecast.csv")

def decompose(target):

    wfc_close_series = df[target]
    decomposition = seasonal_decompose(wfc_close_series, model='additive', period=60)

    plt.figure(figsize=(14, 10))
    plt.subplot(411)
    plt.plot(wfc_close_series, label='Original')
    plt.legend(loc='upper left')
    plt.subplot(412)
    plt.plot(decomposition.trend, label='Trend')
    plt.legend(loc='upper left')
    plt.subplot(413)
    plt.plot(decomposition.seasonal, label='Seasonality')
    plt.legend(loc='upper left')
    plt.subplot(414)
    plt.plot(decomposition.resid, label='Residuals')
    plt.legend(loc='upper left')
    plt.tight_layout()

    return plt

def convert(plt):
    my_stringIObytes = io.BytesIO()
    plt.savefig(my_stringIObytes, format='jpg')
    my_stringIObytes.seek(0)
    return base64.b64encode(my_stringIObytes.read()).decode()

def get_graph_plt(target):
    return convert(decompose(target))


def get_forecast(date):
    row = forecast_df.loc[forecast_df['date'] == date].iloc[0].to_dict()
    return row


def get_new_forecast(path):
    global forecast_df 
    forecast_df = pd.read_csv(path)

