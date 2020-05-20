from unittest import TestCase

from gasopt import datamgr, modelsmgr

class TestDataManager(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestDataManager, self).__init__(*args, **kwargs)

    def test_load_models(self):
        print("Проверка загрузки моделей...")
        test_models = {}
        mm = modelsmgr.ModelsMgr()
        for model in mm.get_model_names():
            try:
                test_models[model] = mm.load(model)
            except ValueError:
                print("Не смогли загрузить модель: ", model)

        self.assertEqual(len(test_models), len(mm.get_model_names()), "Не все модели загружены")
        print("Все модели успешно загружены.")
        
    def test_load_testdata(self):
        print("Проверка загрузки данных...")
        dm = datamgr.DataMgr(furn=1)
        try:
            dm.load_prediction_data(slabs_csv='examples/test_data/slabs_test.csv', gas_csv='examples/test_data/gas_test.csv',\
                    ambient_csv='examples/test_data/ambient_test.csv')
        except ValueError:
            print("Не смогли загрузить данные")

        self.assertEqual(len(dm.S), 5866, "Не смогли загрузить данные по слябам")
        self.assertEqual(len(dm.G), 670, "Не смогли загрузить данные по расходу газа")
        self.assertEqual(len(dm.T), 669, "Не смогли загрузить данные по температуре окружающего воздуха")
        self.datamgr = dm
        print("--  Данные по слябам успешно загружены:")
        dm.S.info()
        print("-- Данные по расходу газа успешно загружены:")
        dm.G.info()
        print("-- Данные по температуре окружающего воздуха успешно загружены:")
        dm.T.info()
        
    def test_testdata_prep(self):
        dm = datamgr.DataMgr(furn=1)
        try:
            dm.load_prediction_data(slabs_csv='examples/test_data/slabs_test.csv', gas_csv='examples/test_data/gas_test.csv',\
                    ambient_csv='examples/test_data/ambient_test.csv')
        except ValueError:
            print("Не смогли загрузить данные")

        preprocess_report = dm.preprocess_prediction()
        print("Проверка очистки данных...")
        self.assertEqual(preprocess_report['invalid_entries'], 18)
        print("Очищено некорректных записей - ", preprocess_report['invalid_entries'])
        self.assertEqual(preprocess_report['valid_entries'], 5848)
        print("Осталось корректных записей - ", preprocess_report['valid_entries'])
        print("Проверка заполнения пропусков...")
        filler_report = dm.fill_missing()
        self.assertEqual(filler_report['filled_entries'], 579)
        print("Найдено и заполнено пропусков в данных - ", filler_report['filled_entries'])
        
    def test_load_traindata(self):
        print("Проверка загрузки данных...")
        dm = datamgr.DataMgr(furn=1)
        try:
            dm.load_prediction_data(slabs_csv='examples/test_data/slabs_test.csv', gas_csv='examples/test_data/gas_test.csv',\
                    ambient_csv='examples/test_data/ambient_test.csv')
            #dm.load_optimization_data(slabs_csv='examples/test_data/slabs_train.csv', gas_csv='examples/test_data/gas_train.csv',\
            #        ambient_csv='examples/test_data/ambient_train.csv')
        except ValueError:
            print("Не смогли загрузить данные")

        self.assertEqual(len(dm.S), 5866, "Не смогли загрузить данные по слябам")
        self.assertEqual(len(dm.G), 670, "Не смогли загрузить данные по расходу газа")
        self.assertEqual(len(dm.T), 669, "Не смогли загрузить данные по температуре окружающего воздуха")
        self.datamgr = dm
        print("--  Данные по слябам успешно загружены:")
        dm.S.info()
        print("-- Данные по расходу газа успешно загружены:")
        dm.G.info()
        print("-- Данные по температуре окружающего воздуха успешно загружены:")
        dm.T.info()
        
    def test_traindata_prep(self):
        dm = datamgr.DataMgr(furn=1)
        try:
            dm.load_prediction_data(slabs_csv='examples/test_data/slabs_test.csv', gas_csv='examples/test_data/gas_test.csv',\
                    ambient_csv='examples/test_data/ambient_test.csv')
        except ValueError:
            print("Не смогли загрузить данные")

        preprocess_report = dm.preprocess_prediction()
        print("Проверка очистки данных...")
        self.assertEqual(preprocess_report['invalid_entries'], 18)
        print("Очищено некорректных записей - ", preprocess_report['invalid_entries'])
        self.assertEqual(preprocess_report['valid_entries'], 5848)
        print("Осталось корректных записей - ", preprocess_report['valid_entries'])
        print("Проверка заполнения пропусков...")
        filler_report = dm.fill_missing()
        self.assertEqual(filler_report['filled_entries'], 579)
        print("Найдено и заполнено пропусков в данных - ", filler_report['filled_entries'])


