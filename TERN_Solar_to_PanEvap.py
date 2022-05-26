# -*- coding: utf-8 -*-
"""
Created on Fri May  6 14:21:04 2022

@author: Alex


Script which adds a mm of evap column to the output of TERN_grid_sum (converting from W/m^2 to mm/m^2)
    


    1. Calculate the 7-day moving average of "tscr_ave" (T_7dayAvg) to aproximate the avg water temperature
        - Since the data will have already been passed through the grid sum script, it'll already be spatially averaged.
        - 
    
    2. λ = 2.50025 - 0.002365 * T_7dayAvg
    3. function to convert T_7dayAvg to water density
    4. Total water mass lost from catchment [kg/m^2] = "epan_ave" (which is actually the daily solar radiation [W/m^2]) * λ [MJ/kg] 
        - unit conversions todo : W/day to MJ & final conversion to kg/m^2
    5. Use water density to calc volume of water evap'd
    
"""

# =============================================================================
#%% Inputs & Setup 
# =============================================================================

import os
import pandas as pd
import glob

dir_in = r"C:\Users\alex.xynias\OneDrive - Water Technology Pty Ltd\UQ\Thesis\Data\TERN_downloads\CompileV2\grids_Full"
dir_out = r"C:\Users\alex.xynias\OneDrive - Water Technology Pty Ltd\UQ\Thesis\Data\TERN_WithEvap"

# Input data column names (CN)
CN_temp = 'tscr_ave.daily'    # Air temp
CN_solar = 'epan_ave' # Evaporation data in W/m^2

# Output new column names (NCN)
NCN_7DayTemp = 'twater_ave.daily' # 7 Day rolling average temperature (to aproximate water temperature)
NCN_lhv = 'LatentHeat[MJ/Kg]' # latent heat of vaporisation
NCN_potevapM = 'EvapPot[Kg]' # potential mass of water evap'd [kg]
NCN_potevap = 'EvapPot[mm]' # calculated potential evap [mm]

# Water property constants for calculations
     # TODO: interpolate rho from the aprox water temp in the data?
rho_water = 998.2 # Density of water at 20c in [kg/m^3] (Streeter and Wylie 1981)
s_per_day = 86400



# =============================================================================
# %% Process input data
# =============================================================================

# generate list of input files
infile_form = "CCAM10_wivenhoe~*.csv" # General form for the data files in the format: [time][latitude][longitude][data - see: dict_var_col]
infile_list = glob.glob(os.path.join(dir_in,infile_form)) 


for f in infile_list: # for each file in the list...
    label_data = f[len(dir_in)+17:-4] # "CCAM10_wivenhoe~" is another 17 chars, ".csv" is 4
    print(f'Loading data from {label_data}')    
    # load data into a df
    df_in = pd.read_csv(f,parse_dates=['time'])
    
    print('   loaded...')
    # Create column with the 7 day moving air temp average
        # TODO: Download and append bias adjusted temp data to the TERN compiled csvs
        # For now I'll do a test set up using the un-adjusted air temp data.
    df_in[NCN_7DayTemp] = df_in[CN_temp].rolling(window=7).mean()
    print('   7 Day moving average calculated...')
    
    # Use water temp to calc latent heat of vaporisation [MJ/kg]
    df_in[NCN_lhv] = 2.50025 - (0.002365 * df_in[NCN_7DayTemp])
    print('   latent heat of vaporisation calculated...')
    
    # Calculate potential evaporation [mm]
    df_in[NCN_potevapM] = (df_in[CN_solar] * s_per_day * (10**-6))/df_in[NCN_lhv]
        # 10^-6 to convert J to MJ
    df_in[NCN_potevap] = (df_in[NCN_potevapM] / rho_water) *1000
    print(f'   mean pot evap: {df_in[NCN_potevap].mean()}')
    print(f'   mean temp: {df_in[NCN_7DayTemp].mean()}')
    
    # Export calculations to file
    fn_out = f[len(dir_in)+2:] # same file names, but being saved to a different folder
    dir_out_full = os.path.join(dir_out,fn_out)
    
    df_in.to_csv(dir_out_full, index=False)
    
    #
