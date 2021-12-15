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
# dir_Data = 'C:/Users/alex.xynias/OneDrive - Water Technology Pty Ltd/UQ/Thesis/Data/SILO_downloads/' # (must end in /)

dir_Data = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data/SILO_downloads/'

dict_var = { # comment out the variables you don't want, add any others that are needed
    1: 'daily_rain'
    ,2: 'et_morton_actual'
    # ,3: 'evap_morton_lake'
    # ,4: 'evap_pan'
    # ,5: 'monthly_rain'
    # ,6: 'radiation'
    }


# Outfile information (for naming)
dir_Out = (dir_Data + 'Compile/' )  # Specify folder to write compiled csvs to. (must end in /)
outfile_prefix = 'SILO-1985-2020' # string to be placed at the start of the export filename as [string].csv

# =============================================================================
#%% Compile SILO data into single DF & export
# =============================================================================

    
for i_var in dict_var: # Loops through each variable in use inputs
    infile_var = dict_var[i_var]    
    infile_form = (dir_Data + '*.' +  infile_var + ".csv") # form/pattern for the input csv file path
    infile_list = glob.glob(infile_form) # generates the list of filepaths in dir_Data which match the infile_form criteria
    
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
        
        df_export = pd.concat([df_export,df_i],axis = 1)
        print(f'Finished concat for {infile_var}...')
    
    
  
    
# Loop is exited once all variables have been joined to df_1
# df_export is saved to file as [time],[lat],[long],[var1],[var2], etc...   

print(f'...Exporting {outfile_prefix}')     
df_export.to_csv(outfile_name, index=False)
print(f'Export complete: {outfile_name}')
    
del df_i



















