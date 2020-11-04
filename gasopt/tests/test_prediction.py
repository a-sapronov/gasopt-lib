from unittest import TestCase

from gasopt import datamgr, modelsmgr
from gasopt.data_load import furn_forecast_data_process
from gasopt.furnace_interface import furnace_forecast


class TestPrediction(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestPrediction, self).__init__(*args, **kwargs)

    def test_prediction(self):
        # Открыть dataframe с историческими данными
        G = furn_forecast_data_process('../../examples/test_data/gas-expense-10.19.xlsx')

        # Получить прогноз для печи 1 с горизонтом в 2 суток и сохранить в CSV-файл "furn_forecast.csv"
        F, scores = furnace_forecast(G, horizon=2, furn_id=1)
        print(F.info())

        self.assertEqual(len(F), 2, "Предсказание не сработало")

        models_count=1
        F.to_csv('../../examples/REPORTS/prediction_report_model0'+str(models_count)+'.csv', ';')
        print("Составление отчета прогнозирования для модели "+str(models_count))

