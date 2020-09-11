"""Filename: app-gasopt.py
"""

import os
import pandas as pd
import glob
import hashlib
from datetime import timedelta

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
            abort(400, 'Invalid request aruments')

        history_data_xlsx = get_history_file(request.args)
        if not history_data_xlsx:
            responses = jsonify(status=-1, num_records=0)
            responses.status_code = 200
            return(responses)

        shop_code = request.args.get('shop_code')

        try:
            D = furn_forecast_data_process(history_data_xlsx)
        except Exception as e:
            raise e
            
        D.to_pickle(f'{shop_code}_{HISTORY_PREPROCESSED_DATA_FNAME}')

        remove_files_by_patterns(f'{shop_code}_forecast_*.pkl', f'{shop_code}_scores_*.pkl')

        responses = jsonify(status=2, num_records=len(D))
        responses.status_code = 200

    if request.method == 'GET':

        offset = request.args.get('days_offset', default=0, type=int)
        horizon_from_offset = request.args.get('days_cnt', default=1, type=int)
        furnace_id = request.args.get('furn_id', default=1, type=int)
        shop_code = request.args.get('shop_code')

        if not check_forecast_get_arguments(offset, horizon_from_offset, furnace_id, shop_code):
            abort(400, 'Invalid request aruments')

        output_pkl = f'./{shop_code}_forecast_o_{offset}_h_{horizon_from_offset}_furn_{furnace_id}.pkl'
        scores_pkl = f'./{shop_code}_scores_o_{offset}_h_{horizon_from_offset}_furn_{furnace_id}.pkl'
        F = None

        if os.path.isfile(output_pkl) and os.path.isfile(scores_pkl):
            F = pd.read_pickle(output_pkl)
            scores = pd.read_pickle(scores_pkl)
        else:
            D = pd.read_pickle(f'{shop_code}_{HISTORY_PREPROCESSED_DATA_FNAME}')
            start_date = D.dt_hour.iloc[-1].date() + timedelta(days=1)
            F, scores = furnace_forecast(D,
                    horizon=horizon_from_offset+offset, furn_id=furnace_id)

            dates = pd.date_range(start_date, periods=offset+horizon_from_offset)
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

    slabs_df = read_slabs_from_json(request.json['slabs'])
    # read fetched data into dataframe
    gas_df = furn_optimization_data_process(slabs_df=slabs_df)

    # calculate optimized gas values
    furn_opt_df = furnace_optimization(gas_df, furn_id=request.args.get('furn_id'))

    responses = jsonify(optimized_gas=furn_opt_df.to_json())
    responses.status_code = 200

    return (responses)

def get_history_file(reqargs):
    history_data_fname = None

    history_data_url = reqargs.get('file_url')
    history_data_fname = reqargs.get('shop_code')+'_history_data.xlsx'
    # check the file exists and get it
    try: 
        urlretrieve(history_data_url, history_data_fname)
    except:
        abort(400, 'Historic data not available')

    if hashlib.md5(open(history_data_fname, 'rb').read()).hexdigest() \
            != reqargs.get('file_md5'):
        abort(400, 'md5 check failed for history data file')

    return history_data_fname


def check_forecast_post_arguments(request_args):
    ret = False
    musthave_arguments = ['file_url', 'file_md5', 'shop_code']
    if all (a in request_args for a in musthave_arguments) and \
        request_args.get('shop_code') in ['lpc10', 'ces']:
        ret = True

    return ret

def check_forecast_get_arguments(offset, horizon, furnace_id, shop_code):
    ret = False
    if horizon > 0 and offset >= 0 \
        and horizon + offset <= 7  \
        and ((shop_code == 'lpc10' and furnace_id in [1, 2, 3, 4]) \
                or (shop_code == 'ces')):
        ret = True

    return ret

def read_slabs_from_json(slabs_json):
    slabs_df = None
    try:
        slabs_df = pd.DataFrame(slabs_json)
    except:
        raise ValueError("Bad json with slab data")

    slab_fields = ['length_s', 'width_s', 'weight_s', 'slab_temp', 'l_thick', 'dt_prev', 'row', 'mark']
    if not all (sf in slabs_df.columns for sf in slab_fields):
        abort(400, 'Bad slab data')

    return slabs_df
    
def remove_files_by_patterns(*args):

    for pattern in args:
        file_list = glob.glob(pattern)
        for f in file_list:
            try:
                os.remove(f)
            except OSError:
                print(f'Error deleting {f}')

