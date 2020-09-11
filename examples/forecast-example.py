import pandas as pd

from gasopt.data_load import furn_forecast_data_process
from gasopt.furnace_interface import furnace_forecast

# Открыть dataframe с историческими данными
G = furn_forecast_data_process('./test_data/gas-expense-10.19.xlsx')

# Получить прогноз для печи 1 с горизонтом в 2 суток и сохранить в CSV-файл "furn_forecast.csv"
F = furnace_forecast(G, horizon=2, furn_id=1, output_csv='furn_forecast.csv')

print(F)
