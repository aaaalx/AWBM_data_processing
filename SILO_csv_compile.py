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
dir_Data = 'C:/Users/alex.xynias/OneDrive - Water Technology Pty Ltd/UQ/Thesis/Data/SILO_downloads/' # (must end in /)


dict_var = { # comment out the variables you don't want, add any others that are needed
    1: 'daily_rain'
    # ,2: 'et_morton_actual'
    # ,3: 'evap_morton_lake'
    # ,4: 'evap_pan'
    # ,5: 'monthly_rain'
    # ,6: 'radiation'
    }


# Outfile information (for naming)
dir_Out = (dir_Data + '/Compile/' )  # Specify folder to write compiled csvs to. (must end in /)
outfile_prefix = '1985-2020' # string to be placed at the start of the export filename [string].[infile_var].csv

# =============================================================================
#%% The Script: Compile each variable into its own csv
# =============================================================================

    
for i_var in dict_var: # Loops through each variable in use inputs
    infile_var = dict_var[i_var]    
    infile_form = (dir_Data + '*.' +  infile_var + ".csv") # form/pattern for the input csv file path
    infile_list = glob.glob(infile_form) # generates the list of filepaths in dir_Data which match the infile_form criteria
    
    outfile_name = (dir_Out + outfile_prefix + '.' + infile_var + '.csv')    
    
    print(f'Starting concat for {infile_var}...')
    outfile_csv = pd.concat([pd.read_csv(f) for f in infile_list]) # https://stackoverflow.com/a/40665364
    
    
    
    
    
    
# outfile_csv.to_csv(outfile_name, index=False)
# print(f'Export complete for {outfile_name}')
    


