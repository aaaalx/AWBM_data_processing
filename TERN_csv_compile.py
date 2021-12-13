# -*- coding: utf-8 -*-
"""
Created on Mon Dec 13 13:24:10 2021

@author: Alex.Xynias

Compiles the processed SILO data into a single time-series file.

"""
# =============================================================================
# Setup and notes
# =============================================================================

# import numpy as np
import pandas as pd
import glob
import time

# https://penandpants.com/2014/09/05/performance-of-pandas-series-vs-numpy-arrays/
    # np faster than pd for indexing, for large loops it can add up
    # Seems like generally, pd has some more features but is a bit slower than using np

# https://stackoverflow.com/questions/27731458/fastest-way-to-write-large-csv-with-python
    # Seems implied that it's going to be faster to do one big write or append
    # going to try loading everything into memory and doing a single output csv write at the end.

# Example scripts:
    # https://stackoverflow.com/questions/2512386/how-to-merge-200-csv-files-in-python
    # 
# Input csv data in the form:
    # TIME,Lat,Long,[variable]

# =============================================================================
#%% User inputs
# =============================================================================

# Input data information 
# (must end in /)
dir_Data = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data/TERN_downloads/'

dict_model = {
    1: 'ACCESS1-0Q', # Australian Community Climate and Earth-System Simulator, version 1.0
    2: 'ACCESS1-3Q', # Australian Community Climate and Earth-System Simulator, version 1.3
    3: 'CCSM4Q', # Community Climate System Model, version 4
    4: 'CNRM-CM5Q', # Centre National de Recherches Météorologiques Coupled Global Climate Model, version 5
    5: 'CSIRO-Mk3-6-0Q', # Commonwealth Scientific and Industrial Research Organisation Mark 3.6.0
    6: 'GFDL-CM3Q', # Geophysical Fluid Dynamics Laboratory Climate Model, version 3
    7: 'GFDL-ESM2MQ', # Geophysical Fluid Dynamics Laboratory Earth System Model with Modular Ocean Model, version 4 component
    8: 'HadGEM2Q', # Hadley Centre Global Environment Model, version 2 
    9: 'MIROC5Q', # Model for Interdisciplinary Research on Climate, version 5 
    10: 'MPI-ESM-LRQ', # Max Planck Institute Earth System Model, low resolution 
    11: 'NorESM1-MQ' # Norwegian Earth System Model, version 1 (intermediate resolution)
    }

dict_var = {
    1: 'rnd24' # rnd24 is 24hr rain (?)
    ,2: 'epan_ave'  # epan_ave for pan evap avg
    ,3: 'rnd24Adjust' # bias corrected 24 hr rain (?)
    # ,4: 'tscr_ave' # daily mean temp
    }



# Outfile information (for naming)
dir_Out = (dir_Data + 'Compile/' )  # Specify folder to write compiled csvs to. (must end in /)


# =============================================================================
#%% Script
# =============================================================================

    
for i_model in dict_model:
    infile_model = dict_model[i_model]
    print(f' model = {infile_model}')
    
    infile_form = (dir_Data + '*.' +  infile_var + ".csv") # form/pattern for the input csv file path
    infile_list = glob.glob(infile_form) # generates the list of filepaths in dir_Data which match the infile_form criteria
    
    
    for i_var in dict_var: # Loops through each variable in use inputs
        infile_var = dict_var[i_var]    
        
        
        # outfile_name = (dir_Out + outfile_prefix + '.' + infile_var + '.csv')    
        if i_var == 1: # define the case for the first df 
            outfile_name = (dir_Out + outfile_prefix + '.csv')    
            print(f'i_var = {i_var}')
            print(f'Setting up dataframe for first var: {infile_var}')
            print(f'Reading data for {infile_var}...')
            df_export = pd.concat([pd.read_csv(f) for f in infile_list]) # https://stackoverflow.com/a/40665364
             
            print(f'Finished concat for {infile_var}...')
        else: # for all subsequent variables, append the variable as a new column to df_export
            print(f'i_var = {i_var}')
            print(f'Reading data for next var: {infile_var}...')
            df_i = pd.concat([pd.read_csv(f) for f in infile_list])
            print('Joining new data in df_i to df_export')
            df_i = df_i[infile_var] # crop the repeated columns (time,lat,long) from the df
            
            df_export = pd.concat([df_export,df_i],axis = 1) # axis = 1 for col
            print(f'Finished concat for {infile_var}...')
    
    
  
    
    # Loop is exited once all variables have been joined to df_1
    # df_export is saved to file as [time],[lat],[long],[var1],[var2], etc...   
    print(f'...Exporting {outfile_prefix}')     
    df_export.to_csv(outfile_name, index=False)
    print(f'Export complete: {outfile_name}')
    

























