"""
This is a module to be used as a reference for building other modules
"""
import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin, TransformerMixin
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted
from sklearn.utils.multiclass import unique_labels
from sklearn.metrics import mean_squared_error

from scipy.optimize import minimize
from scipy.signal import savgol_filter
from scipy import interpolate


class MeanRegularizedExtrapolation(BaseEstimator):
    """ A template estimator to be used as a reference implementation.
    For more information regarding how to build your own estimator, read more
    in the :ref:`User Guide <user_guide>`.
    Parameters
    ----------
        A parameter of time series depth for linear regression.
    """
    def __init__(self, lag=10, offset=0, extrapolation='linear', savgol=False, filter_window=10, filter_polyorder=2):
        self.lag = lag
        self.extrapolation = extrapolation
        self.alpha = 0.
        self.offset = offset
        self.y_shape = 1
        self.savgol = savgol
        self.filter_window = filter_window
        self.filter_polyorder = filter_polyorder

#    def _more_tags(self):
#        return {'multioutput_only': True, 'multioutput': True}

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

        if X.shape[1] < self.lag:
            raise ValueError("Lag must be less than number of features")

        X, y = check_X_y(X, y, accept_sparse=True, multi_output=True, y_numeric=True)

        min_result = minimize(self.mse_alpha, 0.9, args=(X, y, self.lag), method='L-BFGS-B', 
                bounds=[(1e-10,1.-1.e-10)])

        self.y_shape = y.shape[1]

        self.alpha = min_result.x 

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
        check_is_fitted(self, 'is_fitted_')

        y = np.ndarray(shape=(X.shape[0], self.y_shape))

        for iX in np.arange(X.shape[0]):
            sX = X[iX]
            #print(iX, X[iX])
            if self.extrapolation == 'linear':
                y[iX,:] = self.mean_reg_extrapolate(np.arange(sX.size), sX, 
                        np.arange(self.y_shape)+self.offset+sX.size, 
                        lag=self.lag, alpha=self.alpha)

        return y 

    def mean_reg_extrapolate(self, x, y, x_pred, lag=10, alpha=0):
    
        #print(x,y)
        # filter y values to get smoother extrapolation
        if self.savgol:
            y_interp = savgol_filter(y[-lag:], self.filter_window, self.filter_polyorder)
        else:
            y_interp = y[-lag:]

        f = interpolate.interp1d(x[-lag:], y_interp, kind='linear', fill_value='extrapolate')
        my = np.mean(y)
        
        if alpha < 0 or alpha > 1:
            return np.zeros(x_pred.shape)
        
        y_pred = f(x_pred) - alpha*(f(x_pred)-my)
        
        return y_pred


    def mse_alpha(self, alpha, X, y, lag):
        mse = 0.

        for sX, sy in zip(X,y):
            if self.extrapolation == 'linear':
                xpred_offset = sX.size+self.offset
                #print(np.arange(sy.size)+xpred_offset)

                sy_extr = self.mean_reg_extrapolate(np.arange(sX.size), sX, 
                        np.arange(sy.size)+xpred_offset, lag=lag, alpha=alpha)
                #print(sy, sy_extr)
                mse = mse+mean_squared_error(sy, sy_extr)**2

        mse = np.sqrt(mse)

        return mse
