# -*- coding: utf-8 -*-
"""
Created on Wed Dec 15 13:53:11 2021

@author: Alex

Code still very messy, but working a lot better now
probably won't update it beyond this point untill I need to use the 
script again for the TERN data


"""


# =============================================================================
# Setup and notes
# =============================================================================

import glob
import numpy as np
import pandas as pd
import time
import csv
from datetime import date, timedelta

# =============================================================================
# %% User input
# =============================================================================

dir_voronoi_gregors = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data_processing/Voronoi_SILO_gregors.csv'
dir_voronoi_full = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data_processing/Voronoi_SILO_fullcatchment.csv'
# full data from "SILO_csv_compile.py"
dir_Data = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data/SILO_downloads/Compile/SILO-1985-2020.csv'
# dir_Data = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data/SILO_downloads/Compile/SILO-1985-1985.csv' # excel cropped, first few days of 1985
# dir_Data = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data/SILO_downloads/Compile/SILO-1985-1989-09-18.csv' # excel crop all rows supported in excel
# dir_Data = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data/SILO_downloads/Compile/SILO-1985-1985-V2.csv' # "SILO_csv_compile.py" cropped one year
# dir_Data = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data/SILO_downloads/Compile/SILO-1985-1985-V1.csv' # Excel cropped one year

dir_vor = dir_voronoi_full  # choose which catchment to calculate proportions with
dir_Out = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data/SILO_downloads/Compile/grids_Full/'
dir_Log = (dir_Out + 'log.txt')  # where to write the log file for grid errors

outfile_prefix = 'SILO_Full_1985-2020_'  # [outfile_prefix][X_Y].csv
outfile_compile = 'SILO_Full_1985-2020-pd.csv'  # filename to write end product to

start_date = date(1985,1,1) # TODO: I could make it read this from the dir_Data auto 
end_date = date(2020,12,31)


# =============================================================================
#%% loading data: v3 (way better)
# =============================================================================
# https://www.kite.com/python/answers/how-to-sum-two-columns-in-a-pandas-dataframe-in-python#:~:text=Select%20each%20column%20of%20DataFrame,add%20it%20to%20the%20DataFrame.

# not going to both updating the whole script to pandas atm, 
# just going to use the same date conversion below to fix the data as it comes into the AWBM-calibration script as a quick fix

print('Reading grid data...')
tic = time.time()
df_in = pd.read_csv(dir_Data)
df_in['X_Y'] = df_in['longitude'].astype(str) + df_in['latitude'].astype(str)
# df_in['X_Y'] = X_Y_pd
df_in = df_in.drop(columns=['latitude','longitude'])
df_in['time'] = df_in['time'].astype('datetime64[ns]')
    # https://stackoverflow.com/questions/13703720/converting-between-datetime-timestamp-and-datetime64
toc_df_pd = round(time.time() - tic, 5)
print(f'...Grid data loaded t={toc_df_pd}')

# =============================================================================
#%% Create filter arrays for each grid cell
# =============================================================================


tic = time.time()
print('Reading voronoi data...')

df_vor = pd.read_csv(dir_vor) # load csv into dataframe
df_vor['X_Y'] = df_vor['x'].astype(str) + df_vor['y'].astype(str) # create "X_Y"
df_vor = df_vor.drop(columns=['ID','area_km2','x','y']) # remove cols not needed
df_vor = df_vor.rename(columns={"proportion":"Prop"}) # rename to match previous naming

toc = round(time.time() - tic, 5)
print(f'... data loaded t={toc}')

# creates the dictionary to assign each cell (X_Y) a "prop" factor
# dict_prop = dict(zip(XY_in, Prop)) # v2 verison
dict_prop = dict(zip(df_vor['X_Y'],df_vor['Prop'])) 
print('dict_prop ready...')


# input("Press Enter to continue with script...")

#%%
for g in range(0, len(dict_prop)):  # for each grid defined by 'dir_vor'...
    # for g in range(0,3): # for each grid defined by 'dir_vor'...
    tic = time.time()

    print(f'Starting {g} of {len(dict_prop)+1}...')
    # filter array to only index grids "g" in quesiton
    filter_df = (df_in['X_Y'] == df_vor['X_Y'][g])
    # use filter array to crop df_in to only include rows relating to that grid
    df_crop_g = df_in[filter_df]

    # factor P and E by 'Prop' before export
    factor_g = dict_prop[df_vor['X_Y'][g]]
    # https://stackoverflow.com/questions/20625582/how-to-deal-with-settingwithcopywarning-in-pandas
    df_crop_g['daily_rain'] = factor_g * df_crop_g['daily_rain']
    df_crop_g['et_morton_actual'] = factor_g * df_crop_g['et_morton_actual']
    toc = round(time.time() - tic, 5)
    print(f'... df_crop_g updated t={toc}')

    try:
        test_g = df_crop_g['time'].iloc[0]  # tests if the first day has loaded
    except:
        print(f'@@@@@@@@@@ Error for: {df_vor["X_Y"][g]}')
        with open(dir_Log, 'a') as log:
            log.write(f'{df_vor["X_Y"][g]}')
            log.write('\n')
        # input("Press Enter to continue with script...")
        # break # ends loop if not

    tic = time.time()
    outfile_path = (dir_Out + outfile_prefix + df_vor['X_Y'][g] + '.csv')
    print(f'Writing {outfile_prefix+df_vor["X_Y"][g]} to file...')
    df_crop_g.to_csv(outfile_path, index=False)
    toc = round(time.time() - tic, 5)
    print(f'... {outfile_prefix+df_vor["X_Y"][g]} done t={toc}')


# =============================================================================
#%% Sum the exported csvs
# =============================================================================
# End goal: sum the factored (and exported) csvs into finished AWBM-calibration.py input file

# Generate list of input files
# form/pattern for the input csv file path
infile_form = (dir_Out + outfile_prefix + "*.csv")
# generates the list of filepaths in dir_Data which match the infile_form criteria
infile_list = glob.glob(infile_form)

# TODO: load first input file to df_export

df_cum_sum_P = []
df_cum_sum_E = []

# day1check_P = []
# day1check_E = []

# day2check_P = []
# day2check_E = []

# day1check_sum_P = []
# day2check_sum_P = []

# day1check_sum_E = []
# day2check_sum_E = []

for f in range(0, len(infile_list)):
    df_i_P = []  # reset the temp data and variables
    df_i_E = []

    print(f'===================================== {time.ctime()}')
    if f == 0:
        tic = time.time()
        print('Loading first grid and populating df_cum_sum lists')
        with open(infile_list[f]) as csvDataFile:
            csvReader = csv.reader(csvDataFile)
            next(csvReader)         # This skips the 1st row (header information)
            for row in csvReader:
                df_cum_sum_P.append(row[1])
                df_cum_sum_E.append(row[2])
        toc = round(time.time() - tic, 5)
        print(f'... Done t ={toc}')

    else:
        tic = time.time()
        print(
            f'Loading {f} of {len(infile_list)-1} : {infile_list[f][(len(dir_Out + outfile_prefix)):]}')
        with open(infile_list[f]) as csvDataFile:
            csvReader = csv.reader(csvDataFile)
            next(csvReader)         # This skips the 1st row (header information)
            for row in csvReader:
                df_i_P.append(row[1])
                df_i_E.append(row[2])
        toc = round(time.time() - tic, 5)
        print(f'... Done t ={toc}')

# TODO: loop through, df_export = df_i+df_export to calc a cumulative sum
    # seems to be an error in the grid csv creation leading to empty csvs for
    # grids without decimal points (i.e. all cells with -27.0 and 152.0), 27 total grids with errors
        # this error didn't seem to be the case for the first test (prefix = SILO_Gregors_[X_Y])

        print('Converting dfs to float...')
        tic = time.time()

        # if the first value in E is a string, convert all cum_sum to floats
        if isinstance(df_cum_sum_E[0], str) == True:
            df_cum_sum_E = [eval(x) for x in df_i_E]
            df_cum_sum_P = [eval(x) for x in df_i_P]
        df_i_P = [eval(x) for x in df_i_P]
        df_i_E = [eval(x) for x in df_i_E]

        # input("Press Enter to continue with script...")

        # day1check_P.append(df_i_P[0])
        # day1check_E.append(df_i_E[0])

        # day2check_P.append(df_i_P[1])
        # day2check_E.append(df_i_E[1])

        # day1check_sum_E.append(df_cum_sum_E[0])
        # day2check_sum_E.append(df_cum_sum_E[1])

        # day1check_sum_P.append(df_cum_sum_P[0])
        # day2check_sum_P.append(df_cum_sum_P[1])

        toc = round(time.time() - tic, 5)

        print(f'... Done t ={toc}')

        tic = time.time()
        print('Adding df_i to df_cum_sum')
        # https://www.kite.com/python/answers/how-to-find-the-sum-of-two-lists-in-python
        zip_i_E = zip(df_cum_sum_E, df_i_E)
        zip_i_P = zip(df_cum_sum_P, df_i_P)

        # overwrite the df_cum_sum with the updated values
        df_cum_sum_E = [x + y for (x, y) in zip_i_E]
        df_cum_sum_P = [x + y for (x, y) in zip_i_P]
        # df_cum_sum_P = df_cum_sum_P + df_i_P # add new data to cumulative sum
        # df_cum_sum_E = df_cum_sum_E + df_i_E

        toc = round(time.time() - tic, 5)
        print(f'... Done t ={toc}')
        # print('=== Pausing script 10 seconds ===')
        # time.sleep(10) # pauses for x seconds before starting the loop again for debugging purposes
        # del zip_i_E # delete the temp zipped items to save memory
        # del zip_i_P

# del filter_df
# del df_in
# del df_crop_g
# del LatLon_in

#%% export check data
# check_data_in = [day1check_E, day1check_sum_E, day1check_P, day1check_sum_P,
#                  day2check_E, day2check_sum_E, day2check_P, day2check_sum_P]
# index = ['day1check_E', 'day1check_sum_E', 'day1check_P', 'day1check_sum_P',
#          'day2check_E', 'day2check_sum_E', 'day2check_P', 'day2check_sum_P']
# df_check_out = pd.DataFrame(check_data_in, index=index).T
# df_check_out.to_csv('datacheck_gregors.csv', index=False)

#%% Fix dates & Export to file


#%% Creating new date list 
# (https://stackoverflow.com/questions/59882714/python-generating-a-list-of-dates-between-two-dates)

new_dates = pd.date_range(start_date,end_date,freq='D')

Date_out = new_dates.tolist()

#%%

tic = time.time()
# Creating dataframe for export
print(f'Creating df_out, wait ~5min... {time.ctime()}')
data_in = [Date_out, df_cum_sum_P, df_cum_sum_E]

index = ['Date', 'P[mm]', 'E[mm?]', ]
df_out = pd.DataFrame(data_in, index=index).T
toc_df_out = round(time.time() - tic, 5)
print(f'...df_out ready t={toc_df_out}')

# -6 to cut "grids/" from the dir_Out and save to main folder
outfile_compile_path = (dir_Out[:-14]+outfile_compile)
print(f'...Exporting {outfile_compile}')
df_out.to_csv(outfile_compile_path, index=False)
print(f'Export complete: {outfile_compile}')


print(f'fin ======= {time.ctime()}')
