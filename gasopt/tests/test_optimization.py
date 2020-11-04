from unittest import TestCase

from gasopt import datamgr, modelsmgr
from gasopt.data_load import furn_optimization_data_process
from gasopt.furnace_interface import furnace_optimization


class TestOptimization(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestOptimization, self).__init__(*args, **kwargs)

    def test_prediction(self):
        # Открыть dataframe с историческими данными
        G = furn_optimization_data_process('../../examples/test-slab-input-furn1.csv')

        # Получить рекомендованные настройки газа для зон печи 1 для каждого сляба
        F = furnace_optimization(G, furn_id=1)

        print(F)
        print(F.info())

        self.assertEqual(len(F), 10, "Оптимизация не сработала")

        F.to_csv('../../examples/REPORTS/optimization_report.csv', ';')
        print("Составление отчета оптимизации")

