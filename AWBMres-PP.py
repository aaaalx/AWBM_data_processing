# -*- coding: utf-8 -*-
"""
Post processing of the AWBMres-Forecast script

    - "Catchment" elasticity
        - just expanding on https://www.tandfonline.com/doi/pdf/10.1623/hysj.51.4.613?needAccess=true
            Estimation of rainfall elasticity of streamflow in Australia
        - and https://agupubs.onlinelibrary.wiley.com/doi/epdf/10.1029/2007WR005890
            A two‐parameter climate elasticity of streamflow index to assess climate change effects on annual streamflow
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
import numpy as np
import os
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt

# Directories
# dir_results_in = r'C:\Users\Alex\OneDrive\Documents\Uni\Honours Thesis\output_AWBMres-Forecast'
dir_results_in = r"C:\Users\alex.xynias\OneDrive - Water Technology Pty Ltd\UQ\Thesis\Data\output_AWBMres-Forecast"
dir_output = dir_results_in + r'\PP'

# Input filename pattern {i_run}_{i_model}~{i_rcp}~{i_bias}.csv
    # Where {i_run} = RAWresultsAWBM
    
# Define dir list of the Delta-change / base cases
form_basecase = 'RAWresultsAWBM_DT_M1*.csv'
i_run = 'RAWresultsAWBM_'
fn_list_basecase = glob.glob(os.path.join(dir_results_in,form_basecase)) 


# Result headers not used in PP
headers_drop = ["S1","S2","S3","S1_E","S2_E","S3_E","Total_Excess","BFR","SFR","BS","SS","Qbase","Qsurf" ,"resSpill[m3]", "outflow_demand[m3]"]

# =============================================================================
# %% Climate Elasticity
# =============================================================================
# For each x% change in [climate forcing variable], calculates the y% change in either streamflow, res volume,

for f_basecase in fn_list_basecase: # for each basecase...
    # Grab the other variables from the f_basecase
    fn_basecase = f_basecase.split("\\")[-1]
    i_c_model = fn_basecase[len(i_run):].split("~")[0]
    i_c_rcp = fn_basecase[len(i_run):].split("~")[1]
    i_c_bias = fn_basecase[len(i_run):].split("~")[2][:-4] # because '.csv' is 4 char
    print(f'Basecase set: {i_c_model} {i_c_rcp} {i_c_bias}')
    
    # Load basecase comparison data
    print('   Loading data...')
    df_basecase_in = pd.read_csv(f_basecase,parse_dates=['Date'])
    df_basecase = df_basecase_in.set_index(['Date'])
    
    # TODO: Calculate the net wet days bool column, then: https://stackoverflow.com/questions/30311211/pandas-groupby-to-find-percent-true-and-false
        # also do days below x% of res volume? -> it seems like it's regularly 90% in these sims anyway ?
    
    
    # Calculate annual averages for the basecase
    print('   Annual means...')
    GB_year_mean_basecase = df_basecase.groupby([df_basecase.index.map(lambda x: x.year)]).mean()
    GB_year_mean_basecase['YYYY'] = GB_year_mean_basecase.index
    GB_year_mean_basecase.drop(headers_drop,axis=1,inplace=True)
    
    print('   Preparing for e_p calculation...')
    df_ep_basecase = pd.DataFrame()
    df_ep_basecase.index = df_basecase.index
    
    # Transfer the daily data
    df_ep_basecase['Q_t'] = df_basecase['Q']
    df_ep_basecase['P_t'] = df_basecase['P']
    df_ep_basecase['E_t'] = df_basecase['E']
    df_ep_basecase['dS_t'] = df_basecase['dS']
    df_ep_basecase['YYYY'] = df_basecase.index.year

    # Merge the mean annual data to daily 
    df_ep_basecase_merge = pd.merge(df_ep_basecase, GB_year_mean_basecase, left_on='YYYY', right_on='YYYY',how="left")
    df_ep_basecase_merge.index = df_basecase.index
    
    
    # Part 1. Calculating the "x" in ε_p = median("x") as a timeseries
    """ a robust estimator of the precipitation elasticity ofstreamflow for a 
        wide class of hydrological models thatdoes not depend on 
        the form of the hydrological model"""
        
    def calc_ep_P(x):
        ep = (x['Q_t']-x['Q'])/(x['P_t']-x['P']) * (x['P']/x['Q'])
        return ep
    df_ep_basecase_merge['X_P'] = df_ep_basecase_merge.apply(lambda x: calc_ep_P(x),axis=1)

    def calc_ep_E(x):
        ep = (x['Q_t']-x['Q'])/(x['E_t']-x['E']) * (x['E']/x['Q'])
        return ep
    df_ep_basecase_merge['X_E'] = df_ep_basecase_merge.apply(lambda x: calc_ep_E(x),axis=1)
       
    def calc_ep_dS(x):
        ep = (x['Q_t']-x['Q'])/(x['dS_t']-x['dS']) * (x['dS']/x['Q'])
        return ep
    df_ep_basecase_merge['X_dS'] = df_ep_basecase_merge.apply(lambda x: calc_ep_dS(x),axis=1)

    # Part 2. median of the whole timeseries
    results_BC_Ep_Q = { # Results of the basecase's streamflow elasticity
        'P':df_ep_basecase_merge['X_P'].median()
        ,'E':df_ep_basecase_merge['X_E'].median()
        ,'dS':df_ep_basecase_merge['X_dS'].median()}
    
    
    print(results_BC_Ep_Q)
    # Glob list of relevant comparison results (same i_rcp and i_bias)
    form_RCM = f'{i_run}*~{i_c_rcp}~{i_c_bias}.csv'
    fn_list_RCM = glob.glob(os.path.join(dir_results_in,form_RCM)) 

    for f_RCM in fn_list_RCM: # for each RCM sim relevant to the basecase...
        fn_RCM = f_RCM.split("\\")[-1]
        i_R_model = fn_RCM[len(i_run):].split("~")[0]
        i_R_rcp = fn_RCM[len(i_run):].split("~")[1]
        i_R_bias = fn_RCM[len(i_run):].split("~")[2][:-4] # because '.csv' is 4 char

        
        # load comparison data
        df_RCM_in = pd.read_csv(f_RCM,parse_dates=['Date'])
        df_RCM = df_RCM_in.set_index(['Date']) 
        
        # TODO: Calculate the net wet bool column for the RCM
        
    
        # Same process to get a GB_year_mean_comparison
        GB_year_mean_RCM = df_RCM.groupby([df_RCM.index.map(lambda x: x.year)]).mean()
        GB_year_mean_RCM['YYYY'] = GB_year_mean_RCM.index
        GB_year_mean_RCM.drop(headers_drop,axis=1,inplace=True)
        
        # Convert the annual mean df into % change (from basecase)
            # All the dimensions will be the same (row index and column headers)
            
        # def ArrayDiff(x): # where x is the row in the comparison df
        #     x['P'] = (x['P']-GB_year_mean_basecase['P'])/GB_year_mean_basecase['P']
        #     x['E'] = (x['E']-GB_year_mean_basecase['E'])/GB_year_mean_basecase['E']
        #     x['dS'] = (x['dS']-GB_year_mean_basecase['dS'])/GB_year_mean_basecase['dS']
        #     x['Qtotal'] = (x['Qtotal']-GB_year_mean_basecase['Qtotal'])/GB_year_mean_basecase['Qtotal']
        #     x['Q'] = (x['Q']-GB_year_mean_basecase['Q'])/GB_year_mean_basecase['Q']
        #     x['resVolume[m3]'] = (x['resVolume[m3]']-GB_year_mean_basecase['resVolume[m3]'])/GB_year_mean_basecase['resVolume[m3]']
        #     x['resEvapLoss[m3]'] = (x['resEvapLoss[m3]']-GB_year_mean_basecase['resEvapLoss[m3]'])/GB_year_mean_basecase['resEvapLoss[m3]']
        #     x['A_res[m2]'] = (x['A_res[m2]']-GB_year_mean_basecase['A_res[m2]'])/GB_year_mean_basecase['A_res[m2]']
        #     x['resVol_beforespill[%]'] = (x['resVol_beforespill[%]']-GB_year_mean_basecase['resVol_beforespill[%]'])/GB_year_mean_basecase['resVol_beforespill[%]']
        
        # def ArrayDiff_V2(x): # where x is the row in the comparison df
        #     # x[colname] = (x[colname]-GB_year_mean_basecase[colname])/GB_year_mean_basecase[colname]
        #     x['P'] = (x['P']-GB_year_mean_basecase['P'])/GB_year_mean_basecase['P']
        
        # GB_year_mean_RCM['P_%change'] = GB_year_mean_RCM.apply(lambda x: ArrayDiff_V2(x),axis=1)
        
        GB_year_mean_RCM['P_%change'] = 100*(GB_year_mean_RCM['P']-GB_year_mean_basecase['P'])/GB_year_mean_basecase['P']
        GB_year_mean_RCM['E_%change'] = 100*(GB_year_mean_RCM['E']-GB_year_mean_basecase['E'])/GB_year_mean_basecase['E']
        GB_year_mean_RCM['resVol[m3]_%change'] = 100*(GB_year_mean_RCM['resVolume[m3]']-GB_year_mean_basecase['resVolume[m3]'])/GB_year_mean_basecase['resVolume[m3]']
        GB_year_mean_RCM['resVol%_%change'] = 100*(GB_year_mean_RCM['resVol_beforespill[%]']-GB_year_mean_basecase['resVol_beforespill[%]'])/GB_year_mean_basecase['resVol_beforespill[%]']
        GB_year_mean_RCM['Qtotal_%change'] = 100*(GB_year_mean_RCM['Qtotal']-GB_year_mean_basecase['Qtotal'])/GB_year_mean_basecase['Qtotal']




        # Either add a fn_RCM column and groupby later to separate, or save individual results to file as quick fix?
        print(f'Saving annual stats from {fn_RCM} to file...')
        
        dir_out_change = dir_output +  r'\GB_annual'
        fn_out_change = f'AnnualChange~{i_R_model}~{i_R_rcp}~{i_R_bias}.csv'
    
        GB_year_mean_RCM.to_csv(os.path.join(dir_out_change,fn_out_change),index=True)
        
    
# =============================================================================
# %% TODO: Exceedance/Freq analysis of the climate data?
# =============================================================================




# =============================================================================
# %% Data vis
# =============================================================================
    





# =============================================================================
# %% Scrap code & notes
# =============================================================================
# # Other attempt: fit a trend to annual P vs Q    https://stackoverflow.com/a/59120799
# x_data = df_ep_basecase_merge['P'].values#.reshape(-1,1)
# y_data = df_ep_basecase_merge['Q'].values#.reshape(-1,1)
# plt.plot(x_data,y_data,".",ms=2,mec="k")
# z = np.polyfit(x_data,y_data,1)
# y_hat = np.poly1d(z)(x_data)
# plt.plot(x_data,y_hat,"r--", lw=1)
# text_trendline = f" y = {z[0]}x + {z[1]}"
# text_r2 = f" R^2 = {r2_score(y_data,y_hat)}"
    
    
    
    
    
    
    
    
    
