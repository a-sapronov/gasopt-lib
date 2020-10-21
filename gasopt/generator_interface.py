import sys

from gasopt.modelsmgr import ModelsMgr
from gasopt.data_load import build_tses_dataset


def generator_forecast(H, horizon, output_csv=None):
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
        raise ValueError('Not enough data for forecast training. \n  \
            Need at least one month of hourly data of gas consumption')

    if horizon > 7:
        raise ValueError('The requested forecasting horizon is too long.')

    horizon_hours = horizon*24
    gas_dataset = build_tses_dataset(H[-training_depth:], depth, horizon_hours)

    mm = ModelsMgr(depth=depth, offset=0, horizon=horizon_hours)
    P, scores = None, None
    try:
        P, scores = mm.get_forecasts(gas_dataset, depth, horizon_hours)
    except:
        raise RuntimeError('Forecast failure')

    if not len(P):
        raise ValueError('Forecast result is empty, cannot agregate to hours')

    P_hour = P.rolling(window=24,center=True).sum().iloc[12::24,:]

    if output_csv:
        P_hour.to_csv(output_csv, ';', index=False)

    return P_hour, scores


