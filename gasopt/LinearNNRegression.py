"""
This is a module to be used as a reference for building other modules
"""
import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin, TransformerMixin
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted
from sklearn.utils.multiclass import unique_labels
from sklearn.metrics import euclidean_distances

from sklearn.preprocessing import MinMaxScaler

class LinearNNRegression(BaseEstimator):
    """ A template estimator to be used as a reference implementation.
    For more information regarding how to build your own estimator, read more
    in the :ref:`User Guide <user_guide>`.
    Parameters
    ----------
    ts_depth : int, default=2
        A parameter of time series depth for linear regression.
    """
    def __init__(self, lin_regressor, nn_regressor):
        self.lin_regressor = lin_regressor
        self.nn_regressor = nn_regressor

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

        X = self.Xscaler.fit_transform(X)
        y = self.yscaler.fit_transform(y)

        self.lin_regressor.fit(X, y)
        y_linextr = self.lin_regressor.predict(X)

        y_resid = y - y_linextr

        self.nn_regressor.fit(X, y_resid)

        self.is_fitted_ = True
        # `fit` should always return `self`
        return self

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
        y_resid = self.nn_regressor.predict(X)

        y = y_linextr + y_resid

        y = self.yscaler.inverse_transform(y)

        return y

    def set_params(self, **params):
        lin_params = {}
        nn_params = {}
        for pname in params:
            pn = pname.split('__')[1]
            if pname.startswith('lin_regressor'):
                lin_params[pn] = params[pname]
            elif pname.startswith('nn_regressor'):
                nn_params[pn] = params[pname]

        self.lin_regressor.set_params(**lin_params)
        self.nn_regressor.set_params(**nn_params)

        return self


