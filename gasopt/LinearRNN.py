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

from VanillaRNN import VanillaRNN

class LinearRNN(BaseEstimator):
    """ A template estimator to be used as a reference implementation.
    For more information regarding how to build your own estimator, read more
    in the :ref:`User Guide <user_guide>`.
    Parameters
    ----------
    ts_depth : int, default=2
        A parameter of time series depth for linear regression.
    """
    def __init__(self, lin_regressor, depth=24, horizon=24, n_epochs=10, learning_rate=0.001):
        self.lin_regressor = lin_regressor

        self.device = torch.device("cpu")
        self.input_size, self.output_size, self.hidden_size = depth, horizon, 10
        self.rnn = VanillaRNN(input_size=self.input_size, output_size=self.output_size, hidden_dim=self.hidden_size, 
                n_layers=1, device=self.device)
        self.rnn.to(self.device)
        # Define hyperparameters
        self.n_epochs = n_epochs
        self.lr = learning_rate

        # Define Loss, Optimizer
        self.criterion = nn.MSELoss()
        self.optimizer = torch.optim.Adam(self.rnn.parameters(), lr=self.lr)
        print(self.rnn)

        self.minmaxscaler = MinMaxScaler(feature_range=(0.2, 0.8))


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

        X = self.minmaxscaler.fit_transform(X)
        y = self.minmaxscaler.transform(y)

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

        train_hour_data = torch.utils.data.TensorDataset(X_hour, y_hour)
        train_hour_loader = torch.utils.data.DataLoader(train_hour_data, batch_size=1, shuffle=False)

        for epoch in range(1, self.n_epochs + 1):
            self.optimizer.zero_grad()
            for i, _data in enumerate(train_hour_loader, 0):
                input_data_seq, pred_value = _data
                input_data_seq, pred_value = input_data_seq.to(self.device), pred_value.to(self.device)
                output, hidden = self.rnn(input_data_seq)

                loss = criterion(output, pred_value.view(-1))
                loss.backward() # Does backpropagation and calculates gradients
                optimizer.step() # Updates the weights accordingly  

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
        X = self.minmaxscaler.transform(X)
        check_is_fitted(self, 'is_fitted_')

        y_linextr = self.lin_regressor.predict(X)

        pred_input = torch.Tensor([x.reshape(-1,self.input_size) for x in X_test]).float().to(self.device)

        out, _ = self.rnn(pred_input)
        y_resid = out.detach().numpy()

        y = y_linextr + y_resid
        y = self.minmaxscaler.inverse_transform(y)

        return y

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


