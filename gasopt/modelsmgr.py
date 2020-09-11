import math

import numpy as np
import pandas as pd

import joblib

from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.neural_network import MLPRegressor


from gasopt.LinearNNRegression import LinearNNRegression
from gasopt.LinearSARIMAX import LinearSARIMAX
from gasopt.LinearARCH import LinearARCH
from gasopt.LinearRNN import LinearRNN

from gasopt.MeanRegularizedExtrapolation import MeanRegularizedExtrapolation


class ModelsMgr(object):
    ''' A class to manage predictive models '''


    def __init__(self, depth, offset, horizon):
        self.models = {}
        mlp = MLPRegressor(hidden_layer_sizes=(10,5), activation='relu', solver='lbfgs')
        mre = MeanRegularizedExtrapolation(lag=depth, offset=offset, savgol=False, filter_window=11, filter_polyorder=1)

        self.models['FFNN'] = LinearNNRegression(lin_regressor=mre, nn_regressor=mlp)
        self.models['RNN'] = LinearRNN(lin_regressor=mre, horizon=horizon)
        self.models['SARIMAX'] = LinearSARIMAX(lin_regressor=mre)
        self.models['ARCH'] = LinearARCH(lin_regressor=mre, horizon=horizon)

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

    def get_forecasts(self, H, depth, horizon):
        X, y = H.filter(regex='^f', axis=1).to_numpy(), H.filter(regex='^t', axis=1).to_numpy()

        trained_models = []
        for mname, model in self.models.items():
            try:
                model.fit(X,y)
            except:
                print('Error training model: '+mname)

            trained_models.append(mname)

        P = pd.DataFrame(columns=trained_models)

        scores = {}
        for mn in trained_models:
            forecast = self.models[mn].predict(H.iloc[-depth:,-1].to_numpy().reshape(1,-1))
            scores[mn] = self.models[mn].score(X[-depth:], y[-depth:])
            #print(forecast.shape)
            P[mn] = pd.Series(forecast.ravel())

        return P, scores


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






