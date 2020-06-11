import sys

from gasopt.modelsmgr import ModelsMgr
from gasopt.data_load import build_tses_dataset


def generator_forecast(H, horizon):
    '''Прогнозирует поребление природного газа в ЦЭС

    Args:
        H (pd.DataFrame): pandas-датафрейм с историческими данными по
        расходу газа с часовой детализацией
        horizon (int): горизонт прогнозирования в часах

    Returns:
        P: (pd.DataFrame): прогноз расхода природного газа на ЦЭС
        для следующих 'horizon' часов после последнего часа, приведенного
        в 'H'

    '''

    depth = 24
    training_depth = 720
    if len(H) < training_depth:
        print('Error: not enough data for forecast training. \n  \
            Need at least one month of hourly data of gas consumption')

        sys.exit(1)

    gas_dataset = build_tses_dataset(H[-training_depth:], depth, horizon)

    mm = ModelsMgr(depth=depth, offset=0)
    P = mm.get_forecasts(gas_dataset, depth, horizon)

    return P


    pass
    return P

