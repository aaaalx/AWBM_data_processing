# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 11:18:54 2021

@author: Alex
"""


# =============================================================================
# Setup and notes
# =============================================================================

import numpy as np
import pandas as pd
import time
import csv


# =============================================================================
# %% User input
# =============================================================================

dir_voronoi_gregors = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data_processing/Voronoi_SILO_gregors.csv'
dir_voronoi_full = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data_processing/Voronoi_SILO_fullcatchment.csv'
# dir_Data = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data/SILO_downloads/Compile/SILO-1985-2020.csv'
# dir_Data = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data/SILO_downloads/Compile/SILO-1985-1985.csv'
dir_Data = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data/SILO_downloads/Compile/SILO-1985-1989-09-18.csv'

dir_vor = dir_voronoi_gregors # choose which catchment to calculate proportions with
outfile_prefix = 'SILO_Gregors_1985-1989_' # [outfile_prefix][X_Y].csv
dir_Out = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data/SILO_downloads/Compile/grids_test_4/'

outfile_compile = 'SILO_Gregors_1985-1989_testcompile.csv' # filename to write end product to

# =============================================================================
#%% Loading data: v1
# =============================================================================

# tic = time.time()
# test_gregors = np.genfromtxt(dir_Data, delimiter=',',skip_header=0 )
# toc_genfromtxt = time.time() - tic

# =============================================================================
#%% Loading data: v2 
# =============================================================================
# init the list objects to store the data being read from csv
tic = time.time()
Date_in = []
P_in = [] # daily_rain
E_in = [] # et_morton_actual
# Lat_in = [] # [x]
# Lon_in = [] # [y]
LatLon_in = [] # String of "[x]_[y]"

print('Loading input data...')
with open(dir_Data) as csvDataFile:
    csvReader = csv.reader(csvDataFile)
    next(csvReader)         # This skips the 1st row (header information)
    for row in csvReader:
        Date_in.append(row[0])
        # Lat_in.append(row[1])
        # Lon_in.append(row[2])
        P_in.append(row[3])
        E_in.append(row[4])
        LatLon_in.append(row[2]+'_'+row[1])
        
toc_csv = round(time.time() - tic,5)
print(f'...Data loaded t={toc_csv}')  

print('Converting to floats...')
tic = time.time()
# Formatting or unit conversion
P = np.array(P_in)
P[P==''] = 0               
#P[P==''] = np.nan                   # Alternative scripting to convert to NaN
P=[float(x) for x in P]

E = np.array(E_in)
E[E==''] = 0               
#E[E==''] = np.nan                   # Alternative scripting to convert to NaN
E=[float(x) for x in E]
del E_in
del P_in
toc = round(time.time() - tic,5)
print(f'... Done t={toc}')

tic = time.time()
# Creating dataframe after variables have been loaded
print(f'Creating df_in, wait ~5min... {time.ctime()}')
data_in = [Date_in,LatLon_in,P,E,]
index = ['Date','X_Y','P', 'E']
df_in = pd.DataFrame(data_in,index=index).T
toc_df = round(time.time() - tic,5)           
print(f'...df_in ready t={toc_df}')

# =============================================================================
#%% Create filter arrays for each grid cell
# =============================================================================
XY_in = []
Prop_in = []

tic = time.time()
print('Reading grid data...')
with open(dir_vor) as csvDataFile: # opens the QGIS-calculated grid data
    csvReader = csv.reader(csvDataFile)
    next(csvReader)         # This skips the 1st row (header information)
    for row in csvReader:
        XY_in.append(row[5])
        Prop_in.append(row[4])
toc = round(time.time() - tic,5)   
print(f'...Grid data loaded t={toc}')

Prop=[float(x) for x in Prop_in] 
dict_prop = dict(zip(XY_in,Prop)) # creates the dictionary to assign each cell (X_Y) a "prop" factor
print('dict_prop ready...')

for g in range(0,len(XY_in)): # for each grid defined by 'dir_vor'...
# for g in range(0,3): # for each grid defined by 'dir_vor'...
    tic = time.time()

    print(f'Starting {g} of {len(XY_in)}...')
    filter_df = (df_in['X_Y'] == XY_in[g]) # filter array to only index grids "g" in quesiton
    df_crop_g = df_in[filter_df] # use filter array to crop df_in to only include rows relating to that grid
    
    # factor P and E by 'Prop' before export
    factor_g = dict_prop[XY_in[g]]
    df_crop_g['P']  = factor_g * df_crop_g['P'] #https://stackoverflow.com/questions/20625582/how-to-deal-with-settingwithcopywarning-in-pandas
    df_crop_g['E']  = factor_g * df_crop_g['E']
    toc = round(time.time() - tic,5)
    print(f'... df_crop_g updated t={toc}')
    

    try:
        test_g = df_crop_g['Date'].iloc[0] # tests if the first day has loaded
    except:
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        break # ends loop if not

    tic = time.time()
    outfile_path = (dir_Out + outfile_prefix + XY_in[g] + '.csv')
    print(f'Writing {outfile_prefix+XY_in[g]} to file...')
    df_crop_g.to_csv(outfile_path, index=False)
    toc = round(time.time() - tic,5)
    print(f'... {outfile_prefix+XY_in[g]} done t={toc}')
    
    
    
# =============================================================================
#%% Sum the exported csvs
# =============================================================================
# End goal: sum the factored (and exported) csvs into finished AWBM-calibration.py input file
import glob

# Generate list of input files
infile_form = (dir_Out + outfile_prefix + "*.csv") # form/pattern for the input csv file path
infile_list = glob.glob(infile_form) # generates the list of filepaths in dir_Data which match the infile_form criteria

# TODO: load first input file to df_export

df_cum_sum_P = []
df_cum_sum_E = []

for f in range(0,len(infile_list)):
    df_i_P = [] # reset the temp data and variables
    df_i_E = []

    print(f'===================================== {time.ctime()}')
    if f == 0:
        tic = time.time()
        print('Loading first grid and populating df_cum_sum lists')
        with open(infile_list[f]) as csvDataFile:
            csvReader = csv.reader(csvDataFile)
            next(csvReader)         # This skips the 1st row (header information)
            for row in csvReader:
                df_cum_sum_P.append(row[2])
                df_cum_sum_E.append(row[3])
        toc = round(time.time() - tic,5)
        print(f'... Done t ={toc}')

        print('############# df_cum_sums reset')
    else:
        tic = time.time()
        print(f'Loading {f} of {len(infile_list)-1} : {infile_list[f][(len(dir_Out + outfile_prefix)):]}')
        with open(infile_list[f]) as csvDataFile:
            csvReader = csv.reader(csvDataFile)
            next(csvReader)         # This skips the 1st row (header information)
            for row in csvReader:
                df_i_P.append(row[2])
                df_i_E.append(row[3])
        toc = round(time.time() - tic,5)
        print(f'... Done t ={toc}')
        
# TODO: loop through, df_export = df_i+df_export to calc a cumulative sum
    # seems to be an error in the grid csv creation leading to empty csvs for 
    # grids without decimal points (i.e. all cells with -27.0 and 152.0), 27 total grids with errors
        # this error didn't seem to be the case for the first test (prefix = SILO_Gregors_[X_Y])

        print('Converting dfs to float...')
        tic = time.time()

        if isinstance(df_cum_sum_E[0], str) == True: # if the first value in E is a string, convert all cum_sum to floats
            df_cum_sum_E = [eval(x) for x in df_i_E]
            df_cum_sum_P = [eval(x) for x in df_i_P]
        df_i_P = [eval(x) for x in df_i_P]
        df_i_E = [eval(x) for x in df_i_E]

        # map(float, df_i_P)
        # map(float, df_i_E)
        # map(float, df_cum_sum_E)
        # map(float, df_cum_sum_P)
        
        toc = round(time.time() - tic,5)
        
        print(f'... Done t ={toc}')
        
        tic = time.time()
        print('Adding df_i to df_cum_sum')
        zip_i_E = zip(df_cum_sum_E,df_i_E) # https://www.kite.com/python/answers/how-to-find-the-sum-of-two-lists-in-python
        zip_i_P = zip(df_cum_sum_P,df_i_P)
        
        df_cum_sum_E = [x + y for (x,y) in zip_i_E] # overwrite the df_cum_sum with the updated values
        df_cum_sum_P = [x + y for (x,y) in zip_i_P]        
        # df_cum_sum_P = df_cum_sum_P + df_i_P # add new data to cumulative sum
        # df_cum_sum_E = df_cum_sum_E + df_i_E
        
        toc = round(time.time() - tic,5)
        print(f'... Done t ={toc}')
        # print('=== Pausing script 10 seconds ===')
        # time.sleep(10) # pauses for x seconds before starting the loop again for debugging purposes
        # del zip_i_E # delete the temp zipped items to save memory
        # del zip_i_P
        
# TODO: clear other objects from memory (only need to keep Date_in, cumsum for P and E)
# del filter_df
# del df_in
# del df_crop_g
# del LatLon_in

    

#%% Export to file

# TODO: export df_export once all the grids have been added together

tic = time.time()
# Creating dataframe for export
print(f'Creating df_out, wait ~5min... {time.ctime()}')
data_in = [Date_in,df_cum_sum_P,df_cum_sum_E]
index = ['Date','P[mm]', 'E[mm?]',]
df_out = pd.DataFrame(data_in,index=index).T
toc_df_out = round(time.time() - tic,5)           
print(f'...df_out ready t={toc_df_out}')

outfile_compile_path = (dir_Out+outfile_compile)
print(f'...Exporting {outfile_compile}')     
df_out.to_csv(outfile_compile_path, index=False)
print(f'Export complete: {outfile_compile}')


print(f'fin ======= {time.ctime()}')


























