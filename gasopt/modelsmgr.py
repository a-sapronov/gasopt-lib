import math

import numpy as np
import pandas as pd

import joblib

from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline


class ModelsMgr(object):
    ''' A class to manage predictive models '''


    def __init__(self):
        self.models = {}
        self.models['ridge'] = None

        self.path_to_models = './examples/'

    def get_model_names(self):
        return self.models.keys()

    def load(self, model_name):
        self.models[model_name] = joblib.load(self.path_to_models+model_name+'.pkl')

    def dump_model(self, model_name):
        if model_name in self.models:
            joblib.dump(self.models[model_name], model_name+'.pkl')
        else:
            raise ValueError('Unknown model name selected to dump')

    def dump_all_models(self):
        for model_name, model in self.models:
            joblib.dump(model, model_name+'.pkl')

    def build_prediction_model(self, model_name, data_df):
        factors = ['thick_s', 'width_s', 'weight_s', 'slab_temp', 'l_thick', 'amb_t']
        targets = ['gas_m3', 'tons']

        X = D[factors].values
        y = D[targets].values

        X_train, X_test, y_train, y_test = \
                    train_test_split(X, y, test_size=0.7, random_state=42)

        self.models[model_name] = Pipeline([('scaler', StandardScaler()), ('regr', Ridge())])
        self.models[model_name].fit(X_train,y_train)

    def predict(self, model_name, data_df):
        data_df.set_index('dt_hour', inplace=True)
        factors = ['thick_s', 'width_s', 'weight_s', 'slab_temp', 'l_thick', 'amb_t']
        targets = ['gas_m3', 'tons']

        X = data_df[factors]
        y = data_df[targets]

        X_train, X_test, y_train, y_test = \
                    train_test_split(X, y, test_size=0.7, random_state=42)

        y_pred = self.models[model_name].predict(X_test)

        pred_df = pd.DataFrame(y_pred, columns=targets)
        pred_df.index = y_test.index

        return pred_df






