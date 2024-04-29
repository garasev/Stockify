import pandas as pd
import numpy as np

def load_gdp(filename):
    gdp = pd.read_excel(filename)
    gdp['date'] = pd.to_datetime(gdp['date'], format='%d-%m-%Y')
    return gdp[['date', 'Nominal GDP Index', 'Real GDP Index']]

def load_cpi(filename):
    cpi = pd.read_csv(filename, sep='"', decimal=',')
    cpi = cpi['date, "value"'].str.split(',', expand=True)
    cpi['date'] = pd.to_datetime(cpi[0], format='%m.%Y')
    cpi[1] = cpi[1].str.replace('"', '').astype('float')
    cpi[2] = cpi[2].str.replace('"', '').str.rstrip('%').astype('float')
    cpi['value'] = cpi[1] + cpi[2] / 10
    return cpi[['date', 'value']]

def load_financial_data(filename, date_format):
    data = pd.read_csv(filename, sep='"', decimal=',')
    data = data['date, "value"'].str.split(',', expand=True)
    data['date'] = pd.to_datetime(data[0], format=date_format)
    data[1] = data[1].str.replace('"', '').astype('float')
    data[2] = data[2].str.replace('"', '').str.rstrip('%').astype('float')
    data['value'] = data[1] + data[2] / 100
    return data[['date', 'value']]

def load_market_data(filename, date_col, value_col, date_format='%d.%m.%Y'):
    data = pd.read_csv(filename, sep='"', decimal=',')
    data['date'] = data[date_col].str.replace(',', '').str.strip()
    data['date'] = pd.to_datetime(data['date'], format=date_format)
    data['value'] = data[value_col].str.replace('.', '').str.replace(',', '.').astype(float)
    return data[['date', 'value']]

def process_stock_data(filename, date_format='%d.%m.%Y'):
    df = pd.read_csv(filename, sep='"', decimal=',')
    df['date'] = df.iloc[:, 0].str.replace(',', '').str.strip()
    df['date'] = pd.to_datetime(df['date'], format=date_format)
    df = df.drop(columns=df.columns[::2], axis=1)
    df.columns = ['date', 'Close', 'Open', 'Max', 'Min', 'Volume', 'Changes(%)']
    df['Volume'] = df['Volume'].str.replace(',', '').str.replace('M', '').astype(float)
    df['Changes(%)'] = df['Changes(%)'].str.replace(',', '').str.replace('%', '').astype(float) / 100
    return df

def merge_dataframes(dfs, on='date', how='left'):
    from functools import reduce
    merged_df = reduce(lambda left, right: pd.merge(left, right, on=on, how=how), dfs)
    return merged_df

def main():
    gdp = load_gdp('GDP.xlsx')
    cpi = load_cpi('cpi.csv')
    rd = load_financial_data('rate_desicion.csv', '%m.%Y')
    unemployment = load_financial_data('unemployment.csv', '%m.%Y')
    sp500 = load_market_data('SP500.csv', 'Дата,', 'Цена')
    industry_pmi = pd.read_excel('Industry PMI.xlsx')
    service_pmi = pd.read_excel('Service PMI.xlsx')
    trade_balance = load_financial_data('trade-balance.csv', '%m.%Y')
    index_usd = load_market_data('IndexUSD.csv', 'Дата,', 'Цена')

    bac = process_stock_data('BAC.csv')
    citi = process_stock_data('C.csv')
    jpm = process_stock_data('JPM.csv')
    wfc = process_stock_data('WFC.csv')

    dfs = [gdp, cpi, rd, unemployment, sp500, industry_pmi, service_pmi, trade_balance, index_usd, bac, citi, jpm, wfc]
    final_df = merge_dataframes(dfs)

    final_df.to_csv('union.csv', index=False)

if __name__ == '__main__':
    main()