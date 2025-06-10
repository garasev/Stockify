import pandas as pd
from etna.models import NaiveModel, AutoARIMAModel, CatBoostMultiSegmentModel
from etna.datasets import TSDataset
from etna.pipeline import Pipeline
from etna.metrics import SMAPE, MAE, MAPE
from etna.analysis import stl_plot
from etna.transforms import (STLTransform, LagTransform, SegmentEncoderTransform,
                             DateFlagsTransform, MeanTransform)
from copy import deepcopy
from etna.transforms import (TimeSeriesImputerTransform,
                             DensityOutliersTransform,
                             MedianOutliersTransform)
from etna.analysis import (plot_anomalies, plot_anomalies_interactive,
                           plot_backtest, plot_forecast)
from etna.datasets import TSDataset

HORIZON = 30

def _read_csv(file_name):
    df = pd.read_csv(file_name)
    return df

def _set_index(df):
    df['date'] = pd.to_datetime(df['date'])
    df.rename(columns={'date': 'timestamp'}, inplace=True)
    df.set_index('timestamp', inplace=True)
    return df

def _drops(df):
    df = df.drop("RD", axis=1)
    return df

def _reindex(df):
    full_index = pd.date_range(start=df.index.min(), end=df.index.max(), freq='B')
    df_filled = df.reindex(full_index).fillna(method='ffill')
    return df_filled

def _reset_index(df):
    df = df.reset_index().rename(columns={'index': 'timestamp'})
    return df

def _correct_df(df):
    feature_columns = df.columns.difference(['timestamp', 
                                             'WFC_Close', 
                                             'JPM_Close', 
                                             'Citi_Close', 
                                             'BAC_Close']).tolist()
    target_columns = ['WFC_Close', 'JPM_Close', 'Citi_Close', 'BAC_Close']

    df_corrected = pd.melt(df, id_vars=['timestamp'] + feature_columns, 
                           value_vars=target_columns, var_name='segment', 
                           value_name='target')
    return df_corrected

def _create_ts(df):
    ts_dataset = TSDataset.to_dataset(df)
    ts = TSDataset(ts_dataset, freq='B')

    return ts

def _get_corrected_ts(data, target, dropped):
    feature_columns = data.columns.difference(dropped).tolist()
    target_columns = target
    
    df_corrected = pd.melt(data, id_vars=['timestamp'] + feature_columns,
                               value_vars=target_columns,
                               var_name='segment', value_name='target')

    return _create_ts(df_corrected)

def _to_pandas(ts):
    return ts.to_pandas(flatten=True)


def _extract_features(df):
    return extract_features(
        df,
        column_id='segment',
        column_sort='timestamp',
        default_fc_parameters=EXTRACTION_SETTINGS
    )

def _get_new_features_ts(df, target, dropped):
    ts = _get_corrected_ts(df, target, dropped)
    df = _to_pandas(ts)
    features = _extract_features(df)

    for feature_name in features.columns:
        df[feature_name] = features[feature_name].values[0]

    return _create_ts(df)

# =========================================================================================
def create_featured_ts(name):
    df = _read_csv(name)
    df = _set_index(df)
    df = _drops(df)
    df = _reindex(df)
    df = _reset_index(df)
    df = _correct_df(df)
    features = _extract_features(df)
    for feature_name in features.columns:
        df[feature_name] = features[feature_name].values[0]
    ts = _create_ts(df)
    return ts

def create_ts(name):
    df = _read_csv(name)
    df = _set_index(df)
    df = _drops(df)
    df = _reindex(df)
    df = _reset_index(df)
    df = _correct_df(df)
    ts = _create_ts(df)
    return ts

def save_to_csv(forecast_ts):
    forecast_ts[:, :, "target"].round(3).to_csv("last_forecast.csv")
    res_df = pd.read_csv("last_forecast.csv")
    res_df.rename(columns={'segment': 'date'}, inplace=True)
    res_df.set_index('date', inplace=True)
    res_df = res_df.iloc[2:]
    res_df.to_csv("last_forecast.csv")

    return res_df

# =========================================================================================

def catboost(ts):
    train_ts, test_ts = ts.train_test_split(test_size=HORIZON)
    
    catboost_model = CatBoostMultiSegmentModel(iterations = 750, depth = 5, learning_rate = 0.001)
    
    stl = STLTransform(in_column="target", period=30, model="arima")
    anomaly = DensityOutliersTransform(in_column="target", window_size=5, distance_coef=2.5)
    seg = SegmentEncoderTransform()
    lags = LagTransform(in_column="target", lags=list(range(HORIZON, 365)), out_column="lag")

    transforms = [stl, seg, lags, anomaly]  
    pipeline = Pipeline(model=catboost_model, transforms=transforms, horizon=HORIZON)

    metrics_df, forecast_df, fold_info_df = pipeline.backtest(
        ts=ts, metrics=[SMAPE(), MAE(), MAPE()], n_jobs=10
    )
    print(metrics_df.groupby(['segment']).mean())
    
    pipeline.fit(train_ts)
    forecast_ts = pipeline.forecast()
    plot_forecast(forecast_ts=forecast_ts, test_ts=test_ts, train_ts=train_ts, n_train_samples=100)
    pipeline.save("last_pipeline")
    return forecast_ts

def catboost_train(ts):
    train_ts, test_ts = ts.train_test_split(test_size=HORIZON)
    catboost_model = CatBoostMultiSegmentModel(iterations = 750, depth = 5, learning_rate = 0.001)
    
    stl = STLTransform(in_column="target", period=30, model="arima")
    anomaly = DensityOutliersTransform(in_column="target", window_size=5, distance_coef=2.5)
    seg = SegmentEncoderTransform()
    lags = LagTransform(in_column="target", lags=list(range(HORIZON, 365)), out_column="lag")

    transforms = [stl, seg, lags, anomaly]  
    pipeline = Pipeline(model=catboost_model, transforms=transforms, horizon=HORIZON)

    metrics_df, forecast_df, fold_info_df = pipeline.backtest(
        ts=ts, metrics=[SMAPE(), MAE(), MAPE()], n_jobs=10
    )
    print(metrics_df.groupby(['segment']).mean())
    
    pipeline.fit(ts)
    forecast_ts = pipeline.forecast()
    save_to_csv(forecast_ts)
    return forecast_ts

# =========================================================================================

def naive(ts):
    train_ts, test_ts = ts.train_test_split(test_size=HORIZON)
    
    model = NaiveModel(lag=30)

    # Define a pipeline
    pipeline = Pipeline(model=model, horizon=HORIZON)

    metrics_df, forecast_df, fold_info_df = pipeline.backtest(
        ts=ts, metrics=[SMAPE(), MAE(), MAPE()], n_jobs=10
    )
    print(metrics_df.groupby(['segment']).mean())
    
    pipeline.fit(train_ts)
    forecast_ts = pipeline.forecast()
    plot_forecast(forecast_ts=forecast_ts, test_ts=test_ts, train_ts=train_ts, n_train_samples=60)

# =========================================================================================

def arima(ts):
    train_ts, test_ts = ts.train_test_split(test_size=HORIZON)
    
    autoarima_model = AutoARIMAModel(lag=30)
    print(autoarima_model)
    pipeline = Pipeline(model=autoarima_model, horizon=HORIZON)

    metrics_df, forecast_df, fold_info_df = pipeline.backtest(
        ts=ts, metrics=[SMAPE(), MAE(), MAPE()], n_jobs=10
    )
    print(metrics_df.groupby(['segment']).mean())
    
    pipeline.fit(train_ts)
    forecast_ts = pipeline.forecast()
    plot_forecast(forecast_ts=forecast_ts, test_ts=test_ts, train_ts=train_ts, n_train_samples=30)

# =========================================================================================

def prophet(ts):
    train_ts, test_ts = ts.train_test_split(test_size=HORIZON)
    
    prophet_model = ProphetModel()
    pipeline = Pipeline(model=prophet_model, horizon=HORIZON)

    metrics_df, forecast_df, fold_info_df = pipeline.backtest(
        ts=ts, metrics=[SMAPE(), MAE(), MAPE()], n_jobs=10
    )
    print(metrics_df.groupby(['segment']).mean())
    
    pipeline.fit(train_ts)
    forecast_ts = pipeline.forecast()
    plot_forecast(forecast_ts=forecast_ts, test_ts=test_ts, train_ts=train_ts, n_train_samples=30)




if __name__ == "__main__":
    ts = create_ts('combined_dataset.csv')
    forecast = catboost_train(ts)