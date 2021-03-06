"""
This is a module to be used as a reference for building other modules
"""
import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin, TransformerMixin
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted
from sklearn.utils.multiclass import unique_labels
from sklearn.metrics import euclidean_distances

from sklearn.preprocessing import MinMaxScaler

import torch
import torch.nn as nn
import torch.utils.data

from gasopt.VanillaRNN import VanillaRNN
from gasopt.utils import compute_metrics

class LinearRNN(BaseEstimator):
    """ A template estimator to be used as a reference implementation.
    For more information regarding how to build your own estimator, read more
    in the :ref:`User Guide <user_guide>`.
    Parameters
    ----------
    ts_depth : int, default=2
        A parameter of time series depth for linear regression.
    """
    def __init__(self, lin_regressor, depth=24, horizon=24, n_epochs=10, learning_rate=0.00001):
        self.lin_regressor = lin_regressor

        self.device = torch.device("cpu")
        self.input_size, self.output_size, self.hidden_size = depth, horizon, 10
        self.rnn = VanillaRNN(input_size=self.input_size, output_size=self.output_size, hidden_dim=self.hidden_size,  \
                 device=self.device, n_layers=1)
        self.rnn.to(self.device)
        # Define hyperparameters
        self.n_epochs = n_epochs
        self.lr = learning_rate

        # Define Loss, Optimizer
        self.criterion = nn.MSELoss()
        self.optimizer = torch.optim.Adam(self.rnn.parameters(), lr=self.lr)
        print(self.rnn)

        self.Xscaler = MinMaxScaler(feature_range=(0.2, 0.8))
        self.yscaler = MinMaxScaler(feature_range=(0.2, 0.8))


    def fit(self, X, y):
        """A reference implementation of a fitting function.
        Parameters
        ----------
        X : {array-like, sparse matrix}, shape (n_samples, n_features)
            The training input samples.
        y : array-like, shape (n_samples,) or (n_samples, n_outputs)
            The target values (class labels in classification, real numbers in
            regression).
        Returns
        -------
        self : object
            Returns self.
        """
        X, y = check_X_y(X, y, accept_sparse=True, multi_output=True, y_numeric=True)

        # first self.ts_depth features are the average gas consumption for 
        # previous self.ts_depth days. They are used for extrapolation

        X = self.Xscaler.fit_transform(X)
        y = self.yscaler.fit_transform(y)

        self.lin_regressor.fit(X, y)
        y_linextr = self.lin_regressor.predict(X)

        y_resid = y - y_linextr

        self.fit_rnn(X, y_resid)

        self.is_fitted_ = True
        # `fit` should always return `self`
        return self

    def fit_rnn(self, X, y_resid):
        X_hour = torch.Tensor([x.reshape(-1,self.input_size) for x in X]).float().to(self.device)
        y_hour = torch.Tensor(y_resid.reshape(-1,self.output_size)).float().to(self.device)
        #print(X_hour.shape, y_hour.shape)

        train_hour_data = torch.utils.data.TensorDataset(X_hour, y_hour)
        train_hour_loader = torch.utils.data.DataLoader(train_hour_data, batch_size=1, shuffle=False)

        for epoch in range(1, self.n_epochs + 1):
            self.optimizer.zero_grad()
            for i, _data in enumerate(train_hour_loader, 0):
                input_data_seq, pred_value = _data
                input_data_seq, pred_value = input_data_seq.to(self.device), pred_value.to(self.device)
                output, hidden = self.rnn(input_data_seq)

                loss = self.criterion(output, pred_value)
                loss.backward() # Does backpropagation and calculates gradients
                self.optimizer.step() # Updates the weights accordingly  

    def predict(self, X):
        """ A reference implementation of a predicting function.
        Parameters
        ----------
        X : {array-like, sparse matrix}, shape (n_samples, n_features)
            The training input samples.
        Returns
        -------
        y : ndarray, shape (n_samples,)
            Returns an array of ones.
        """

        X = check_array(X, accept_sparse=True)
        X = self.Xscaler.transform(X)
        check_is_fitted(self, 'is_fitted_')

        y_linextr = self.lin_regressor.predict(X)

        pred_input = torch.Tensor([x.reshape(-1,self.input_size) for x in X]).float().to(self.device)

        out, _ = self.rnn(pred_input)
        y_resid = out.detach().numpy()
        #print(y_resid)

        y = y_linextr + y_resid
        y = self.yscaler.inverse_transform(y)

        return y

    def score(self, X, y):
        """An implementation of a scoring function.
        Parameters
        ----------
        X : {array-like, sparse matrix}, shape (n_samples, n_features)
            The training input samples.
        y : array-like, shape (n_samples,) or (n_samples, n_outputs)
            The target values (class labels in classification, real numbers in
            regression).
        Returns
        -------
        self : object
            Returns self.
        """
        X, y = check_X_y(X, y, accept_sparse=True, multi_output=True, y_numeric=True)

        y_pred = self.predict(X)
        metrics = compute_metrics(y, y, y_pred)

        return metrics['mape']

#    def set_params(self, **params):
#        lin_params = {}
#        nn_params = {}
#        for pname in params:
#            pn = pname.split('__')[1]
#            if pname.startswith('lin_regressor'):
#                lin_params[pn] = params[pname]
#            elif pname.startswith('nn_regressor'):
#                nn_params[pn] = params[pname]
#
#        self.lin_regressor.set_params(**lin_params)
#        self.nn_regressor.set_params(**nn_params)
#
#        return self


