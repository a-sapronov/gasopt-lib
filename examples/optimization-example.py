import pandas as pd

from gasopt.data_load import furn_optimization_data_process
from gasopt.furnace_interface import furnace_optimization

# Открыть dataframe с данными о слябах
G = furn_optimization_data_process('./test-slab-input-furn1.csv')

# Получить рекомендованные настройки газа для зон печи 1 для каждого сляба
F = furnace_optimization(G, furn_id=1, output_csv='optimization_test.csv')

print(F)
