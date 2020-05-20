import datetime
import numpy as np
import pandas as pd

import traceback

def furn_forecast_data_process(input_data_str):
    '''Конвертирует данные из текстового формата в pandas-датафрейм
    для модулей прогнозирования потребления ПГ в ЛПЦ-10

    Args:
        input_data_str: данные для конвертации (CSV)

    Returns:
        D: (pd.DataFrame): таблица данных в формате pandas.DataFrame

    '''

    zones = ['Unnamed: 0_level_1', 'Unnamed: 1_level_1', 'на печь,м3/час']

    furnaces = [1,2,3,4]

    D = pd.DataFrame(columns=furnaces)

    for ifurn in furnaces:
        G = None
        try:
            G = read_gas(input_data_str, ifurn)
        except Exception as exc:
            traceback.print_exc()
            continue

        df = None
        try:
            df = G.loc[~G[('№ печи','Unnamed: 1_level_1')].isnull(),
                       (['Дата загрузки', '№ печи', 'Расход газа'], zones)]
        except Exception as exc:
            traceback.print_exc()
            continue
            
        df.columns = ['datetime', 'furn', 'gas']

        df['datetime'] = df['datetime'].apply(fix_minutes)
        df['dt_hour'] = df['datetime'].dt.floor('H')
        df_hour = df.groupby('dt_hour')['gas'].mean().to_frame()

        D[ifurn] = df_hour['gas']

    D.reset_index(inplace=True)

    D.fillna(0, inplace=True)

    return D

def read_gas(gas_excel, furn):
    G = pd.read_excel(gas_excel, sheet_name=furn-1, header=[2,3])
        
    return G

def furn_optimization_data_process(input_data_str):
    '''Конвертирует данные из текстового формата в pandas-датафрейм
    для модулей оптимизации потребления ПГ в ЛПЦ-10

    Args:
        input_data_str: данные для конвертации (CSV)

    Returns:
        D: (pd.DataFrame): таблица данных в формате pandas.DataFrame

    '''

    pass
    return D

def tses_forecast_data_process(input_data_str):
    '''Конвертирует данные из текстового формата в pandas-датафрейм
    для модулей прогнозирования потребления ПГ в ЦЭС

    Args:
        input_data_str: данные для конвертации (CSV)

    Returns:
        D: (pd.DataFrame): таблица данных в формате pandas.DataFrame

    '''
    zones = ['Unnamed: 0_level_0', 'Q ПГ ЦЭС', 'Температура окружающего воздуха']

    D = pd.DataFrame(columns=['gas'])
    G = None

    try:
        G = read_gas(input_data_str, 0)
    except Exception as exc:
        traceback.print_exc()

    df = None
    try:
        df = G.loc[:,(zones, ['Дата', 'тыс.м3/ч', 'град.С'])]
    except Exception as exc:
        traceback.print_exc()
        
    df.columns = ['datetime', 'gas', 'amb_t']

    df['datetime'] = df['datetime'].apply(fix_minutes)
    df.set_index('datetime', drop=True, inplace=True)

    D['gas'] = df['gas']
        
    D.fillna(0, inplace=True)
    return D

def read_tses_gas(gas_excel, sheet_name):
    G = pd.read_excel(gas_excel, sheet_name=sheet_name, header=[0,1])
    
    return G

def fix_minutes(gas_dt):
    
    round_minute = round(float(gas_dt.minute) / 10)
    dminute = datetime.timedelta(minutes=10*(round_minute %6))
    dhour = datetime.timedelta(hours=round_minute//6)
    #print(dminute, dhour)
    
    new_dt = datetime.datetime(gas_dt.year, gas_dt.month, gas_dt.day, gas_dt.hour) + dhour + dminute

    return new_dt

def build_furn_dataset(D, depth, horizon, furn_id):
    offset = 0

    D.reset_index(drop=True, inplace=True)

    features = ['f'+str(i) for i in range(-depth,0)]
    targets = ['t'+str(i) for i in range(horizon)]

    O = pd.DataFrame(columns=['datetime']+features+targets)

    for ix in range(depth, len(D)-horizon-offset):
        
        if not ix%100:
            print(ix)
        #print(ix-depth)
        DT = pd.Series(D.loc[ix-depth, 'dt_hour'], index=['datetime'])
        SF = pd.Series(D.loc[ix-depth:ix-1, furn_id].values, index=features)
        ST = pd.Series(D.loc[ix+offset:ix-1+offset+horizon, furn_id].values, index=targets)
        O.loc[ix-depth] = pd.concat([DT,SF,ST])

    return O

