import pandas as pd

from gasopt.data_load import furn_forecast_data_process
from gasopt.furnance_interface import furnace_forecast

# Открыть dataframe с историческими данными
G = furn_forecast_data_process('./test_data/gas-expense-10.19.xlsx')

# Получить прогноз для печи 1 с горизонтом в 24 часа
F = furnace_forecast(G, horizon=24, furn_id=1)

print(F)
