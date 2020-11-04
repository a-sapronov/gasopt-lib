import pandas as pd

from gasopt.data_load import tses_forecast_data_process
from gasopt.generator_interface import generator_forecast

# Открыть dataframe с историческими данными
G = tses_forecast_data_process('./test_data/tses-data.xlsx')

# Получить прогноз для ЦЭС с горизонтом в 2 суток и сохранить в CSV-файл "tses_forecast.csv"
F = generator_forecast(G, horizon=2,  output_csv='tses_forecast.csv')

print(F)
