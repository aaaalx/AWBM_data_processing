# -*- coding: utf-8 -*-
"""
Created on Fri May  6 15:03:51 2022

@author: Alex

Converts the output of TERN_csv_compile (gridded data) to a weighted (by proportion of grid area inside of the catchment) sum that the AWBM accepts.
    - e.g. a grid cell 1 has P=20, E=11, T=25 and the grid contributes to 25% of the catchment area (derived form QGIS)
        - another grid cell 2 is P=40, E=10, T=25.2 and is 75% of the catchment area  
        - If these are the only grids; P_avg = 20*0.25 + 40*0.75 = 35mm
                                        E_avg = 11*0.25 + 10*0.75 = 10.25mm
                                        T_avg = 25*0.25 + 25.2*0.75 = 25.15mm



"""
# =============================================================================
#%% Set up
# =============================================================================
import glob
import pandas as pd
import numpy as np
pd.set_option('display.max_columns', None)
import os
import time
tic_script = time.time()


# =============================================================================
#%% User input 
# =============================================================================

# dir_voronoi_somerset = r"\\fs07.watech.local\redirected folders$\alex.xynias\My Documents\GitHub\AWBM_data_processing\Voronoi_CCAM10_somerset.csv"
# dir_voronoi_wivenhoe = r"\\fs07.watech.local\redirected folders$\alex.xynias\My Documents\GitHub\AWBM_data_processing\Voronoi_CCAM10_wivenhoe.csv"

dir_voronoi_somerset = r"C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data_processing/Voronoi_CCAM10_somerset.csv"
dir_voronoi_wivenhoe = r"C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data_processing/Voronoi_CCAM10_wivenhoe.csv"
dir_vor = dir_voronoi_wivenhoe # [gridID][x][y][area_km2][proportion of total area]

# dir_data = r"C:\Users\alex.xynias\OneDrive - Water Technology Pty Ltd\UQ\Thesis\Data\TERN_downloads\CompileV2"
dir_data = r"C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data/TERN_downloads/CompileV2"


infile_form = "Compile-*.csv" # General form for the data files in the format: [time][latitude][longitude][data - see: dict_var_col]
infile_list = glob.glob(os.path.join(dir_data,infile_form)) 

# dir_out = r"C:\Users\alex.xynias\OneDrive - Water Technology Pty Ltd\UQ\Thesis\Data\TERN_downloads\CompileV2\grids_Full"
dir_out = r"C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data/TERN_downloads/CompileV2/grids_Full"

outfile_prefix = 'CCAM10_wivenhoe~' #for the output filename e.g. {outfile_prefix}{model_name}.csv
    # ~ at the end to help with splitting later on
convert_K_to_C = -273.15
UTC_hrs = +9


# =============================================================================
#%% Other Settings
# =============================================================================
dict_model = {
    # RCP4.5
    1: 'ACCESS1-0Q_rcp45', # Australian Community Climate and Earth-System Simulator, version 1.0
    2: 'ACCESS1-3Q_rcp45', # Australian Community Climate and Earth-System Simulator, version 1.3
    3: 'CCSM4Q_rcp45', # Community Climate System Model, version 4
    4: 'CNRM-CM5Q_rcp45', # Centre National de Recherches Météorologiques Coupled Global Climate Model, version 5
    5: 'CSIRO-Mk3-6-0Q_rcp45', # Commonwealth Scientific and Industrial Research Organisation Mark 3.6.0
    6: 'GFDL-CM3Q_rcp45', # Geophysical Fluid Dynamics Laboratory Climate Model, version 3
    7: 'GFDL-ESM2MQ_rcp45', # Geophysical Fluid Dynamics Laboratory Earth System Model with Modular Ocean Model, version 4 component
    8: 'HadGEM2Q_rcp45', # Hadley Centre Global Environment Model, version 2 
    9: 'MIROC5Q_rcp45', # Model for Interdisciplinary Research on Climate, version 5 
    10: 'MPI-ESM-LRQ_rcp45', # Max Planck Institute Earth System Model, low resolution 
    11: 'NorESM1-MQ_rcp45', # Norwegian Earth System Model, version 1 (intermediate resolution)
    
    # RCP8.5
    12: 'ACCESS1-0Q_rcp85', # Australian Community Climate and Earth-System Simulator, version 1.0
    13: 'ACCESS1-3Q_rcp85', # Australian Community Climate and Earth-System Simulator, version 1.3
    14: 'CCSM4Q_rcp85', # Community Climate System Model, version 4
    15: 'CNRM-CM5Q_rcp85', # Centre National de Recherches Météorologiques Coupled Global Climate Model, version 5
    16: 'CSIRO-Mk3-6-0Q_rcp85', # Commonwealth Scientific and Industrial Research Organisation Mark 3.6.0
    17: 'GFDL-CM3Q_rcp85', # Geophysical Fluid Dynamics Laboratory Climate Model, version 3
    18: 'GFDL-ESM2MQ_rcp85', # Geophysical Fluid Dynamics Laboratory Earth System Model with Modular Ocean Model, version 4 component
    19: 'HadGEM2Q_rcp85', # Hadley Centre Global Environment Model, version 2 
    20: 'MIROC5Q_rcp85', # Model for Interdisciplinary Research on Climate, version 5 
    21: 'MPI-ESM-LRQ_rcp85', # Max Planck Institute Earth System Model, low resolution 
    22: 'NorESM1-MQ_rcp85' # Norwegian Earth System Model, version 1 (intermediate resolution)
    }

dict_var_col = { # variable name headers as they appear in the infile csvs
    1: 'rnd24.daily'
    ,2: 'epan_ave'
    ,3: 'rnd24Adjust.daily'
    ,4: 'tscr_ave.daily' # needs to be converted to C from K
    }

# =============================================================================
# %% Loading full climate data
# =============================================================================

# First load spatial data for the grids
df_vor = pd.read_csv(dir_vor)
df_vor['X_Y'] = df_vor['x'].astype(str) + df_vor['y'].astype(str) # creates the grid ID column
df_vor.drop(columns=['x','y'],inplace=True)

dict_prop = dict(zip(df_vor['X_Y'],df_vor['proportion'])) # creates the dictionary to assign each cell (X_Y) a "prop" factor
  


for f in infile_list: # for each model's data file (f)...
    tic_f = time.time()
    fn_in = f.split("\\")[-1]
    model_name = fn_in[len(infile_form.split("*")[0]):-len(infile_form.split("*")[1])]
        # Grabs model name from filename: fn_in[number of characters before the *:-number of characters after the *]
    print(f'Loading climate data for {model_name}...')
    df_in = pd.read_csv(f,parse_dates=['time'])
    print(f'   {len(df_in)} lines loaded...')
    print('   Applying formatting fixes...')
    df_in['time'] = df_in['time'] + pd.Timedelta(hours=UTC_hrs)
    date_start = df_in['time'].min()
    date_end = df_in['time'].max()
    
    df_in['X_Y'] = df_in['longitude'].astype(str) + df_in['latitude'].astype(str) # creates the grid ID column
    df_in.drop(columns=['latitude','longitude'],inplace=True)
    
    df_in['tscr_ave.daily'] = df_in['tscr_ave.daily'] + convert_K_to_C
    
    toc_f = time.time() - tic_f
    print(f'   ...Completed in {round(toc_f,5)} ')
    
    # remove data for grids outside of the catchment https://stackoverflow.com/questions/44803007/pandas-dataframe-use-np-where-and-drop-together
        # Data in the CompileV2 has data for grids outside of the catchment, 
        # these needs to be filtered about before the next step otherwise it runs into a key error   
    df_catchment = df_in.drop(np.where(~df_in['X_Y'].isin(df_vor['X_Y']))[0])
        # the ~ here reverses the "isin" condition to work as "is not in x list"
        # np.where returns an array, the [0] selects just the bool part so that .drop can use it
    del df_in # to save memory
# =============================================================================
#%% Apply df_vor factors to input data
# =============================================================================
# https://realpython.com/pandas-groupby/#pandas-groupby-vs-sql

    def ApplyProp(X_Y,Value):
        # Given a grid code (X_Y) and a variable value(Value); return the correct factored value for that grid
        factored_value = Value * dict_prop[X_Y]
        return factored_value
    
    df_Prop = df_catchment
    
    for i in dict_var_col:
        tic_factor = time.time()
        v = dict_var_col[i]
        print(f'Factoring {v}...')
        df_Prop[v] = df_catchment.apply(
            lambda row: ApplyProp(row['X_Y'],row[v]),axis=1
            )
        toc_factor = time.time() - tic_factor
        print(f'   done in {toc_factor}')
# =============================================================================
#%% Groupby time & sum for final export 
# =============================================================================
    print(f'Groupby time & sum for {model_name}...')
        # for each timestep, sum each variable to calculate the catchment weighted average
    tic_gbtime = time.time()
    df_out = df_Prop.groupby('time').sum()
    toc_gbtime = time.time() - tic_gbtime
    print(f'   ...finished in {toc_gbtime} ')


# =============================================================================
#%% Export processed model results
# =============================================================================
    print(f'Starting export for {model_name}...')
    
    fn_out = f'{outfile_prefix}{model_name}.csv'

    dir_out_full = os.path.join(dir_out,fn_out)
    df_out.to_csv(dir_out_full)
    


# =============================================================================
#%% SS code
# =============================================================================

     # df_prop['rnd24.daily'] = np.where(df_in['X_Y'] == g, #https://numpy.org/doc/stable/reference/generated/numpy.where.html
     #                                   df_in['rnd24.daily'] * dict_prop[g],
     #                                   df_prop['rnd24.daily']
     #                                   )



# by_grid = df_in.groupby('X_Y')

# by_grid.groups['152.1-27.4'] # index of rows which are in the group
# by_grid.get_group("152.1-27.4") # returns the rows in that group

# =============================================================================
# Export factored grid time series to files
# =============================================================================

    # df_vor = pd.read_csv(dir_vor)
    # df_vor['X_Y'] = df_vor['x'].astype(str) + df_vor['y'].astype(str) # creates the grid ID column
    # df_vor.drop(columns=['x','y'],inplace=True)

    # dict_prop = dict(zip(df_vor['X_Y'],df_vor['proportion'])) # creates the dictionary to assign each cell (X_Y) a "prop" factor
  
   





    # for g in dict_prop: # for each grid ID (g)...
    #     df_grid = df_in.loc[df_in['X_Y'] == str(g)] # this df is a timeseries for one grid cell
        
    #     print(f'Factoring variables for {g}...')
    #     for i in dict_var_col: # for each variable name (v)...
    #         v = dict_var_col[i]
    #         df_grid[v] = df_grid[v] * dict_prop[g]

    #         print(f'   Factored {v} by {dict_prop[g]} ')
        
    #     print(f'Exporting {g} to file...')
        
    #     fn_gridprop = f'{outfile_gridprop}~{model_name}~{g}.csv'
    #     outfile_grid = os.path.join(dir_out,fn_gridprop)
    #     df_grid.to_csv(outfile_grid,index=False)
    #     print(f'   {outfile_grid}')
    
    # gridprop_form = f'{outfile_gridprop}*.csv'
    # gridprop_list =  glob.glob(os.path.join(dir_out,gridprop_form)) 