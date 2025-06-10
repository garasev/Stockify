from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt
import pandas as pd
import base64
import io

CLOSE_NAME = "_Close"
df = pd.read_csv("union.csv")
forecast_df = pd.read_csv("last_forecast.csv")

START_MSG = """
Командный проект по ML. Авторство: Гарасев Никита Алексеевич и Тишин Роман Вячеславович.

Бот создан для предсказания стоимостей акций JPM WFC C BAC

Доступные команды:

/JPM, /WFC, /Citi, /BAC - для установки банка, как таргет для команд.

/target -узнать текущий таргет.

/graph - строит STL разложение для таргета.

/forecast - выводит предсказания на месяц для таргета. 

/forecastGraph - строит график предсказаний на месяц для таргета.

/getCache - вывод кеш приложения. 

/clearCache - очищает кеш приложения.
"""

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

def picture_from_graph(target):
    target = target + CLOSE_NAME
    plt = decompose(target)
    plt.savefig("last_pic.jpg", format='jpg')
    return "last_pic.jpg"

def get_forecast(date):
    row = forecast_df.loc[forecast_df['date'] == date].iloc[0].to_dict()
    return row

def forecast_graph(target):
    plt = _forecast_graph(target)
    plt.savefig("last_pic2.jpg", format='jpg')
    return "last_pic2.jpg"

def _forecast_graph(target):
    plt.figure(figsize=(10, 5))
    plt.plot(forecast_df.index, forecast_df[target + CLOSE_NAME], marker='o')
    plt.title(f'График для {target}')
    plt.xlabel('Дата')
    plt.ylabel('Цена закрытия')
    plt.grid(True)
    return plt

def get_all_forecast(target):
    dates = forecast_df["date"].tolist()
    values = forecast_df[target + CLOSE_NAME].tolist()
    result_dict = dict(zip(dates, values))
    return result_dict

def get_new_forecast(path):
    global forecast_df 
    forecast_df = pd.read_csv(path)


def dict_to_str(d: dict):
    tmp = ""
    for k, v in d.items():
        tmp += k + ": " + str(v) + "\n"
    return tmp