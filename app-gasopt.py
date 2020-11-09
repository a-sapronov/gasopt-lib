"""Filename: app-gasopt.py
"""

import os
import pandas as pd
import glob
import hashlib
import json
from datetime import date, datetime, timedelta

from urllib.request import urlretrieve
from flask import Flask, jsonify, request, abort

from gasopt.data_load import furn_forecast_data_process, furn_optimization_data_process
from gasopt.furnace_interface import furnace_forecast, furnace_optimization

from gasopt.data_load import tses_forecast_data_process
from gasopt.generator_interface import generator_forecast

app = Flask(__name__)

@app.route('/forecast', methods=['POST', 'GET'])
def api_forecast():
    """Forecast API call
    """

    HISTORY_PREPROCESSED_DATA_FNAME = 'history_data.pkl'

    if request.method == 'POST':
        if not check_forecast_post_arguments(request.args):
            responses = jsonify(status=-1, error='Invalid request aruments')
            responses.status_code = 200
            return(responses)

        history_data_xlsx, error_str = get_history_file(request.args)
        if not history_data_xlsx:
            responses = jsonify(status=-1, error=error_str)
            responses.status_code = 200
            return(responses)

        shop_code = request.args.get('shop_code')

        try:
            D = None
            if shop_code == 'lpc10':
                D = furn_forecast_data_process(history_data_xlsx)
            elif shop_code == 'ces':
                D = tses_forecast_data_process(history_data_xlsx)
        except Exception as e:
            print(repr(e))
            responses = jsonify(status=-1, error='Falied to preprocess historic data')
            responses.status_code = 200
            return(responses)
            
        D.to_pickle(f'{shop_code}_{HISTORY_PREPROCESSED_DATA_FNAME}')

        remove_files_by_patterns(f'{shop_code}_forecast_*.pkl', f'{shop_code}_scores_*.pkl')

        responses = jsonify(status=2, num_records=len(D))
        responses.status_code = 200

    if request.method == 'GET':

        date_str = request.args.get('date_st', default='history_last', type=str)
        #print(datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").date())
        date_start = request.args.get('date_st', default=None, type=toDate)
        #if not date_start:
        #    responses = jsonify(status=-1, error='Bad start date format')
        #    responses.status_code = 200
        #    return responses

        horizon_from_start = request.args.get('days_cnt', default=1, type=int)
        furnace_id = request.args.get('furn_id', default=0, type=int)
        shop_code = request.args.get('shop_code')

        if not check_forecast_get_arguments(horizon_from_start, furnace_id, shop_code):
            responses = jsonify(status=-1, error='Invalid request aruments')
            responses.status_code = 200
            return responses

        output_pkl = f'./{shop_code}_forecast_s_{date_str}_h_{horizon_from_start}_furn_{furnace_id}.pkl'
        scores_pkl = f'./{shop_code}_scores_s_{date_str}_h_{horizon_from_start}_furn_{furnace_id}.pkl'
        F, scores = None, None

        D = None
        try:
            D = pd.read_pickle(f'{shop_code}_{HISTORY_PREPROCESSED_DATA_FNAME}')
        except Exception as e:
            print(repr(e))
            responses = jsonify(status=-1, error='No history data found')
            responses.status_code = 200
            return(responses)

        last_history_date = D.dt_hour.iloc[-1].date()
        offset = (date_start - last_history_date).days if date_start is not None else 0

        if offset < 0:
            responses = jsonify(status=-1, error='Invalid forecast start date: must be later than the last historic data date')
            responses.status_code = 200
            return responses

        if os.path.isfile(output_pkl) and os.path.isfile(scores_pkl):
            F = pd.read_pickle(output_pkl)
            scores = pd.read_pickle(scores_pkl)
        else:
            try:
                if shop_code == 'lpc10':
                    F, scores = furnace_forecast(D,
                            horizon=horizon_from_start+offset, furn_id=furnace_id)
                elif shop_code == 'ces':
                    F, scores = generator_forecast(D,
                            horizon=horizon_from_start+offset)
            except Exception as e:
                print(repr(e))
                responses = jsonify(status=-1, error='Forecast failure')
                responses.status_code = 200
                return responses

            dates = pd.date_range(last_history_date+timedelta(days=1), periods=offset+horizon_from_start)
            F.set_index(dates, inplace=True, drop=True)

            F.to_pickle(output_pkl)
            pd.to_pickle(scores, scores_pkl)

        responses = jsonify(predictions=F.iloc[offset:].to_json(date_format='iso'), 
                scores=scores,
                history_timestamp=os.path.getmtime(f'{shop_code}_{HISTORY_PREPROCESSED_DATA_FNAME}'))
        responses.status_code = 200

    return (responses)

@app.route('/optimize', methods=['POST'])
def api_optimize():
    """Optimization API call
    """

    try:
        json.loads(request.data)
    except Exception as e:
        responses = jsonify(status=-1, error=repr(e))
        responses.status_code = 200
        return responses

    slabs_df, error_str = read_slabs_from_json(request.json.get('slabs'))
    if slabs_df is None:
        responses = jsonify(status=-1, error=error_str)
        responses.status_code = 200
        return responses

    # read fetched data into dataframe
    gas_df = None
    try:
        gas_df = furn_optimization_data_process(slabs_df=slabs_df)
    except Exception as e:
        print(repr(e))

    if gas_df is None:
        responses = jsonify(status=-1, error='Failed to preprocess gasa data')
        responses.status_code = 200
        return responses

    # calculate optimized gas values
    try:
        furn_opt_df = furnace_optimization(gas_df, furn_id=request.args.get('furn_id'))
    except Exception as e:
        print(repr(e))

    if gas_df is None:
        responses = jsonify(status=-1, error='Optimization failure')
        responses.status_code = 200
        return responses

    responses = jsonify(optimized_gas=furn_opt_df.to_json())
    responses.status_code = 200

    return (responses)

def get_history_file(reqargs):
    history_data_fname = None
    error_str = None

    history_data_url = reqargs.get('file_url')
    history_data_fname = reqargs.get('shop_code')+'_history_data.xlsx'
    # check the file exists and get it
    try: 
        urlretrieve(history_data_url, history_data_fname)
    except:
        history_data_fname = None
        error_str = 'Bad historic data URL'
        return history_data_fname, error_str

    if hashlib.md5(open(history_data_fname, 'rb').read()).hexdigest() \
            != reqargs.get('file_md5'):
        history_data_fname = None
        error_str = 'md5 check failed for history data file'

    return history_data_fname, error_str


def check_forecast_post_arguments(request_args):
    ret = False
    musthave_arguments = ['file_url', 'file_md5', 'shop_code']
    if all (a in request_args for a in musthave_arguments) and \
        request_args.get('shop_code') in ['lpc10', 'ces']:
        ret = True

    return ret

def check_forecast_get_arguments(horizon, furnace_id, shop_code):
    ret = False
    if horizon > 0   \
        and ((shop_code == 'lpc10' and furnace_id in [1, 2, 3, 4]) \
                or (shop_code == 'ces')):
        ret = True

    return ret

def read_slabs_from_json(slabs_json):
    slabs_df = None
    error_str = None
    try:
        slabs_df = pd.DataFrame(slabs_json)
    except Exception as e:
        return slabs_df, repr(e)
        
    slab_fields = ['length_s', 'width_s', 'weight_s', 'slab_temp', 'l_thick', 'dt_prev', 'row', 'mark']
    if not all (sf in slabs_df.columns for sf in slab_fields):
        slabs_df = None
        error_str = 'Bad slab data'

    return slabs_df, error_str
    
def remove_files_by_patterns(*args):

    for pattern in args:
        file_list = glob.glob(pattern)
        for f in file_list:
            try:
                os.remove(f)
            except OSError:
                print(f'Error deleting {f}')

def toDate(dateString): 
    date_from_string = None
    try:
        date_from_string = datetime.strptime(dateString, "%Y-%m-%d").date()
    except:
        raise ValueError('Bad date format')

    return date_from_string
