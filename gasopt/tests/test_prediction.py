from unittest import TestCase

from gasopt import datamgr, modelsmgr

class TestPrediction(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestPrediction, self).__init__(*args, **kwargs)

    def test_prediction(self):
        print("Проверка загрузки моделей...")
        test_models = {}
        mm = modelsmgr.ModelsMgr()
        for model in mm.get_model_names():
            try:
                test_models[model] = mm.load(model)
            except ValueError:
                print("Не смогли загрузить модель: ", model)

        dm = datamgr.DataMgr(furn=1)
        try:
            dm.load_prediction_data(slabs_csv='examples/test_data/slabs_test.csv', gas_csv='examples/test_data/gas_test.csv',\
                    ambient_csv='examples/test_data/ambient_test.csv')
        except ValueError:
            print("Не смогли загрузить данные")

        preprocess_report = dm.preprocess_prediction()

        D = dm.data_for_prediction()
        D.dropna(inplace=True)
        models_count = 0

        for model_name, model in test_models.items():
            models_count = models_count + 1
            
            print("Проверка модели "+str(models_count))
            mm.load(model_name)
            R = mm.predict(model_name, D)
            self.assertEqual(len(R), 406, "Предсказание не сработало")

            R.to_csv('examples/REPORTS/prediction_report_model0'+str(models_count)+'.csv', ';')
            print("Составление отчета прогнозирования для модели "+str(models_count))

