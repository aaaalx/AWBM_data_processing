# -*- coding: utf-8 -*-
"""
Post processing of the AWBMres-Forecast script

    - "Catchment" elasticity
    - Mean of each RCP from CMIP5
    - Summary statistics from each simulation
    - Timeseries and other plots
    - Misc statistics
        - % wet days
        - % days below x% of res volume
        - Groupby season ?
        - flow/duration plot of Qtotal for each model / group of models?


"""

# =============================================================================
# %% Setup and Inputs
# =============================================================================

import glob
import pandas as pd
import os

# Directories
dir_results_in = r'C:\Users\Alex\OneDrive\Documents\Uni\Honours Thesis\output_AWBMres-Forecast'
dir_output = dir_results_in + r'\PP'

# Input filename pattern {i_run}_{i_model}~{i_rcp}~{i_bias}.csv
    # Where {i_run} = RAWresultsAWBM
    
# Define dir list of the Delta-change / base cases
form_basecase = 'RAWresultsAWBM_DT_M1*.csv'
i_run = 'RAWresultsAWBM_'
fn_list_basecase = glob.glob(os.path.join(dir_results_in,form_basecase)) 

# =============================================================================
# %% "Catchment" Elasticity
# =============================================================================
# For each x% change in [climate forcing variable], calculates the y% change in either streamflow, res volume,

for f_basecase in fn_list_basecase:
    # Grab the other variables from the f_basecase
    fn_basecase = f_basecase.split("\\")[-1]
    i_c_model = fn_basecase[len(i_run):].split("~")[0]
    i_c_rcp = fn_basecase[len(i_run):].split("~")[1]
    i_c_bias = fn_basecase[len(i_run):].split("~")[2][:-4] # because '.csv' is 4 char
    print(f'Basecase set: {i_c_model} {i_c_rcp} {i_c_bias}')
    
    # Load basecase comparison data
    df_basecase_in = pd.read_csv(f_basecase,parse_dates=['Date'])
    
    # Glob list of relevant comparison results (same i_rcp and i_bias)
    form_compare = f'{i_run}*~{i_c_rcp}~{i_c_bias}.csv'
    fn_list_compare = glob.glob(os.path.join(dir_results_in,form_compare)) 

    for f_compare in fn_list_compare:
        print(f_compare)
    
    
    
    
    
