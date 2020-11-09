import numpy as np

from sklearn.utils import check_array
from sklearn.metrics import mean_squared_error, mean_absolute_error

import numpy.ma as ma


def mean_absolute_scaled_error(y_train, y_test, y_pred):
    """
    Computes the MEAN-ABSOLUTE SCALED ERROR forcast error for univariate time series prediction.
    
    See "Another look at measures of forecast accuracy", Rob J Hyndman
    
    parameters:
        training_series: the series used to train the model, 1d numpy array
        testing_series: the test series to predict, 1d numpy array or float
        prediction_series: the prediction of testing_series, 1d numpy array (same size as testing_series) or float
        absolute: "squares" to use sum of squares and root the result, "absolute" to use absolute values.
    
    """
    #print "Needs to be tested."
    n = y_train.shape[0]
    d = np.abs(  np.diff( y_train[:,0]) ).sum()/(n-1)
    #rint(d)
    
    errors = np.abs(y_test - y_pred )
    return errors.mean()/d



def compute_metrics(y_train, y_test, y_pred):
    metrics = {}
    
    y_true = check_array(y_test)
    y_pred = check_array(y_pred)

    mask_y_test = ma.masked_values(y_test, 0.)
    
    metrics['mae'] = mean_absolute_error(y_test, y_pred)
    metrics['rmse'] = np.sqrt(mean_squared_error(y_test, y_pred))
    metrics['mape'] = np.mean(np.abs((y_test - y_pred) / mask_y_test)) * 100
    metrics['mase'] = mean_absolute_scaled_error(y_train, y_test, y_pred)
    
    return metrics
