import sys

import pandas as pd
import numpy as np

import joblib

from modelsmgr import ModelsMgr
from data_load import build_furn_dataset


def furnace_forecast(H, horizon, furn_id):
    '''Прогнозирует поребление газа в печи ЛПЦ-10

    Args:
        H (pd.DataFrame): pandas-датафрейм с историческими данными по
        расходу газа с часовой детализацией
        horizon (int): горизонт прогнозирования в часах
        furn_id (int): номер печи (1,2,3 or 4)

    Returns:
        P: (pd.DataFrame): прогноз расхода газа для печи 'furn_id' 
        для следующих 'horizon' часов после последнего часа, приведенного
        в 'H'

    '''

    depth = 24
    training_depth = 720
    if len(H) < training_depth:
        print('Error: not enough data for forecast training. \n  \
            Need at least one month of hourly data of gas consumption')

        sys.exit(1)

    gas_dataset = build_furn_dataset(H[-training_depth:], depth, horizon, furn_id)

    mm = ModelsMgr(depth=depth, offset=0)
    P = mm.get_forecasts(gas_dataset, depth, horizon)

    return P

def furnace_optimization(S, furn_id):
    '''Вычисляет оптимальный расход газа по зонам исходя из требуемого
    набора слябов.

    Args:
        S (pd.DataFrame): список слябов для нагрева с их параметрами (размеры, тип посада)
        furn_id (int): номер печи (1,2,3 или 4)

    Returns:
        G: (pd.DataFrame): рекомендуемые значения подачи газа в зонах печи 'furn_id'
        для оптимального нагрева слябов из 'S'. Рекомендуемые значения газа приводятся
        для каждого сляба по зонам. Приводятся значения усредненного расхода газа (agas_N)
        и интегрированного (igas_N) для периода, пока сляб находится в соответствующей зоне.

    '''

    zones = ['agas_1', 'agas_2', 'agas_3', 'agas_4', 'agas_5', 'agas_6', 'agas_7l', 'agas_7r', 'agas_8l', 'agas_8r', \
            'igas_1', 'igas_2', 'igas_3', 'igas_4', 'igas_5', 'igas_6', 'igas_7l', 'igas_7r', 'igas_8l', 'igas_8r']

    factors = ['length_s', 'width_s', 'weight_s', 'slab_temp', 'area_s', 'vacant_area', 't_unl', 'l_thick', 'dt_prev', \
            'row', 'mark_0', 'mark_1', 'mark_2', 'mark_3', 'mark_4', 'mark_5', 'mark_6', 'mark_7', 'mark_8', 'mark_9', \
            'mark_10', 'mark_11', 'mark_12', 'mark_13', 'mark_14', 'mark_15', 'mark_16', 'mark_17', 'mark_18', 'mark_19',\
            'mark_20', 'temp_gain', 'heat_gain']

    X = S[factors].to_numpy()

    G = pd.DataFrame(columns=zones, index=S.index)

    for z in zones:
        try:
            model = joblib.load('./models/'+str(furn_id)+'/LGBMRegressor_'+z+'.joblib')
        except RuntimeError:
            print('Error: couldn\'t load model for zone {}'.format(z))

        y = model.predict(X)

        G[z] = y

    return G

