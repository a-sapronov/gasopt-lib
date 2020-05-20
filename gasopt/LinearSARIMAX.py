"""
This is a module to be used as a reference for building other modules
"""
import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin, TransformerMixin
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted
from sklearn.utils.multiclass import unique_labels
from sklearn.metrics import euclidean_distances

import statsmodels.formula.api as smf
import statsmodels.tsa.api as smt
import statsmodels.api as sm
import scipy.stats as scs

class LinearSARIMAX(BaseEstimator):
    """ A template estimator to be used as a reference implementation.
    For more information regarding how to build your own estimator, read more
    in the :ref:`User Guide <user_guide>`.
    Parameters
    ----------
    ts_depth : int, default=2
        A parameter of time series depth for linear regression.
    """
    def __init__(self, lin_regressor):
        self.lin_regressor = lin_regressor
        self.sarimax = None

        self.pdq = (2, 1, 1)
        self.PDQs = (1, 1, 0, 24)

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

        self.lin_regressor.fit(X, y)
        y_linextr = self.lin_regressor.predict(X)

        y_resid = y - y_linextr

        self.fit_sarimax(y_resid)

        self.is_fitted_ = True
        # `fit` should always return `self`
        return self

    def fit_sarimax(self, y_resid):
        try:
            self.sarimax = sm.tsa.statespace.SARIMAX(y_resid[:,0], order=self.pdq,
                    seasonal_order=self.PDQs).fit(disp=-1)
        except RuntimeError:
            print('WARNING: ARIMA was unable to build model.')
        
        if self.sarimax is not None:
            print(self.sarimax.summary())

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
        check_is_fitted(self, 'is_fitted_')

        y_linextr = self.lin_regressor.predict(X)
        y_resid = self.sarimax.predict(start=0,end=len(y_linextr)-1)

        y = y_linextr + y_resid

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


