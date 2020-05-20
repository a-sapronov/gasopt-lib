import sys

from modlesmgr import ModelsMgr
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

    mm = ModelsMgr()
    for model in mm.models():


    pass
    return P

def furnace_optimization(S, duration, furn_id):
    '''Вычисляет оптимальный расход газа по зонам исходя из требуемого
    набора слябов.

    Args:
        S (pd.DataFrame): список слябов для нагрева с их параметрами (размеры, тип посада)
        duration (float): время в минутах, за которое необходимо нагреть слябы
        furn_id (int): номер печи (1,2,3 or 4)

    Returns:
        G: (pd.DataFrame): рекомендуемые значения подачи газа в зонах печи 'furn_id'
        для оптимального нагрева слябов из 'S'

    '''


    pass
    return G

