import math

import numpy as np
import pandas as pd

from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

from copy import deepcopy

class DataMgr(object):
    ''' A class to manage MMK slabs and gas data '''
    def __init__(self, furn=5):
        self.furn = furn

    def load_prediction_data(self, slabs_csv, gas_csv, ambient_csv):
        S = pd.read_csv(slabs_csv, ';', encoding='cp1251')
        S['unload_t'] = pd.to_datetime(S['unload_t'], errors='coerce')

        G = self.read_gas_expense(gas_csv, self.furn)
        G = G.dropna().reset_index(drop=True)

        T = pd.read_csv(ambient_csv, '\s+')
        T['dt_day'] = pd.to_datetime(T['date'])
        T.drop('date', axis=1, inplace=True)
        
        self.S = S[S.furn == self.furn]
        self.G = G
        self.T = T

        self.PS = None
        self.PG = None
        self.P = None
        self.P_filled = None

        #self.t_unl_mean = S.t_unl.mean()

        self.preprocess_report = {}

    def read_gas_expense(self, gas_csv, furn):
        use_columns = [0]

        use_columns.extend([ic+3*(furn-1) for ic in [1, 2, 3]])

        use_columns.extend([16,17])
        #print(use_columns)
        
        gas_columns = ['dt', 'gas_m3', 'tons', 'm3_per_ton',
                  'gasT', 'gasP']
        D = pd.read_csv(gas_csv, sep=';', 
                        names=gas_columns, usecols=use_columns,
                        skiprows=2, decimal=',')[:-5]
        
        D['furn'] = furn
        D['gas_m3'] = D.gas_m3.astype(float)
        D['tons'] = D.tons.astype(float)
        D['m3_per_ton'] = D.m3_per_ton.astype(float)
        
        D['dt'] = pd.to_datetime(D['dt'].apply(lambda x: x.split('-')[0]), \
                                    format="%d.%m.%Y %H")
        
        return D

    def preprocess_prediction(self):
        preprocess_report = {}
        slabs_columns = ['thick_s', 'width_s', 'length_s', 'weight_s', 'furn',
                'row', 'slab_temp', 'unload_t', 'l_thick', 'l_width']

        gas_columns = ['dt', 'gas_m3', 'tons', 'm3_per_ton', 'furn']
        preprocess_report['invalid_entries'] = len(self.S[self.S.unload_t.isna()])
        preprocess_report['valid_entries'] = len(self.S) - len(self.S[self.S.unload_t.isna()])

        PS = self.S[slabs_columns].dropna(axis=0, subset=['unload_t'])
        # aggregate by hours
        PS['dt_hour'] = PS['unload_t'].dt.floor('H')
        PS['dt_day'] = PS['unload_t'].dt.floor('D')
        PS_by_hour = PS.groupby('dt_hour')['length_s', 'weight_s'].sum()
        PS_by_hour[['thick_s', 'width_s', 'slab_temp', 'l_thick', 'l_width']] \
            = PS.groupby('dt_hour')['thick_s', 'width_s', 'slab_temp', 'l_thick', 'l_width'].mean()

        PS_by_hour.reset_index(inplace=True)
        PS_by_hour = PS_by_hour.merge(PS[['dt_hour', 'dt_day']].drop_duplicates(), how='left', on='dt_hour')
        PS_by_hour = PS_by_hour.merge(self.T, how='left', on='dt_day')

        PS_by_hour['furn'] = PS.furn.values[0]

        PG = deepcopy(self.G[gas_columns])
        PG.loc[:,'dt_hour'] = PG.loc[:,'dt'].dt.floor('H')
        self.PG = PG

        self.P = PS_by_hour.merge(PG, how='right', on=['dt_hour', 'furn'])

        return preprocess_report

    def fill_missing(self):
        filler_report = {}
        imp = IterativeImputer(max_iter=10, random_state=0, tol=0.1)
        nodate_df = self.P.drop(['dt_hour', 'dt_day', 'dt'], axis=1)
        imp.fit(nodate_df.values)
        df_filled = pd.DataFrame(imp.transform(nodate_df.values), columns = nodate_df.columns)

        filler_report['filled_entries'] = len(df_filled)-len(nodate_df[nodate_df.thick_s.isna()])
        return filler_report

    def filter(self):
        pass

    def scale(self):
        pass

    def data_for_prediction(self):
        return deepcopy(self.P)

    def data_for_optimization(self):
        pass



