# -*- coding: utf-8 -*-
"""
Created on Tue May 24 17:35:05 2022

@author: alex.xynias

After the gridded SILO data has been downloaded (SILO_download.py), converted to csv (nc_data_cleaning_v4.5.py),
and run through the SILO_grid_sum_v3 script to compile a single timeseries for the catchment; it will be put through this script
to apply delta change to SILO data according to the methodologies outlined by:
        https://link.springer.com/content/pdf/10.1007/s00382-014-2130-8.pdf



SILO data is available from 1900-2021 (121 yrs)
CMIP5 data is available from 1985-2100 (115 yrs)

P_o is the observed timeseries data
    Daily SILO data starting from 1900
    
P_c_monthly is the control period timeseries
    Monthly averages derived from SILO observations between 1986 and 2005
        This range of data spans an appropriate range of SOI values & is broadly "before" recent climate shifts
        Longpaddock uses 1986-2005 (19 yrs), so I'll use this same range
        
        
P_s_monthly is the simulated monthly mean timeseries
    This is from the CMIP5 data for a particular YYYY-MM
    
P_p is the resulting delta-change projected timeseries data
    This is what will be used in the AWBM model
    P_p = (P_s_monthly/P_c_monthly) * P_o
        This is the "traditional delta change method" from (Ra¨ty et al, 2014) - linked above


"""

# =============================================================================
# %% Inputs & Setup
# =============================================================================

import glob
import os
import pandas as pd
 
dir_out = r"C:\Users\alex.xynias\OneDrive - Water Technology Pty Ltd\UQ\Thesis\Data\processed_ForModel\\"
# dir_out_CMIP5_Monthly = r"C:\Users\alex.xynias\OneDrive - Water Technology Pty Ltd\UQ\Thesis\Data\TERN_WithEvap\P_s_monthly\\"
dir_out_CMIP5_Monthly = r"C:\Users\alex.xynias\OneDrive - Water Technology Pty Ltd\UQ\Thesis\Data\DeltaChange\P_s_monthly\\"
    # the output folder for all P_s data
    
dir_out_Pc = r"C:\Users\alex.xynias\OneDrive - Water Technology Pty Ltd\UQ\Thesis\Data\DeltaChange\P_c_monthly.csv"


dir_in_CMIP5 = r"C:\Users\alex.xynias\OneDrive - Water Technology Pty Ltd\UQ\Thesis\Data\TERN_WithEvap\\" # folder containing pro

dir_in_SILO = r"C:\Users\alex.xynias\OneDrive - Water Technology Pty Ltd\UQ\Thesis\Data\SILO_downloads\deltachange\Compile\SILO_full~-1900-2021.csv"


dir_in_Ps_rcp45 = r"C:\Users\alex.xynias\OneDrive - Water Technology Pty Ltd\UQ\Thesis\Data\DeltaChange\P_s_monthly\P_s_monthly~rcp45.csv"
dir_in_Ps_rcp85 = r"C:\Users\alex.xynias\OneDrive - Water Technology Pty Ltd\UQ\Thesis\Data\DeltaChange\P_s_monthly\P_s_monthly~rcp85.csv"

# P_c period start and end (inclusive)
date_start_Pc = '1986-01-01' 
date_end_Pc = '2005-12-31'



# Col names (CN) in input CMIP5 data 
cn_P = 'rnd24.daily' # For rain [mm]
cn_Padj = 'rnd24Adjust.daily' # For bias adjusted rain [mm]
cn_T = 'tscr_ave.daily' # For temp [c]
cn_E = 'EvapPot[mm]' # For potential evap [mm]

# CN for SILO data
cn_s_P = 'daily_rain' # Rainfall [mm]
cn_s_E = 'et_morton_potential' # Potential evap [mm]


dict_rcp = {
    1: 'rcp45',
    2: 'rcp85'    
    }

dict_Ps_dirs = {
    1: dir_in_Ps_rcp45
    ,2: dir_in_Ps_rcp85    
    }


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
# =============================================================================
#%% P_s_monthly: Load TERN data & analyse in ensemble (for each RCP)
# =============================================================================

for i in dict_rcp: # for each RCP...
    i_rcp = dict_rcp[i] # turn the index "i" into an rcp string
    print(f'Processing {i_rcp}...')

    for j in dict_model: # for each model...
        i_model = dict_model[j]
        print(f'   Loading {i_model}...')
        
        infile_form = os.path.join(dir_in_CMIP5,f"*{i_model}_{i_rcp}.csv")
        infile = glob.glob(infile_form)         
        if len(infile) != 1: # Generates a list, but should only have one file per loop.
            input(f'ERROR: Check input directory: {infile}')
        
        
        # Load the data for the target i_rcp and i_model
        df_in = pd.read_csv(infile[0],parse_dates=['time'])
        
        # Calculate total statistics (mean, std) for Precipitation, Evap, Temp
        ss_P = df_in[cn_P].agg(["min","max","mean","skew","std"]) # .describe() could also be used here
        ss_Padj = df_in[cn_Padj].agg(["min","max","mean","skew","std"])
        ss_T = df_in[cn_T].agg(["min","max","mean","skew","std"])
        ss_E = df_in[cn_E].agg(["min","max","mean","skew","std"])
        
        # TODO: export sum stats for each model?
        
        print('   Monthly resample...')
        # Calculate P_s_monthly for i_model                
        df_in.set_index('time',inplace=True)
        # df_GB_yyyymm = df_in.groupby(pd.Grouper(freq='M')).mean() 
        df_GB_yyyymm = df_in.resample("M").mean()
        
        # Save P_s_monthly to file        
        print(f'   Exporting {i_model} {i_rcp} to file...')
        dir_out_CMIP5_Monthly_i_model = os.path.join(dir_out_CMIP5_Monthly,f'P_s_monthly~{i_model}_{i_rcp}.csv')
        df_GB_yyyymm.to_csv(dir_out_CMIP5_Monthly_i_model)
        print(f'      Saved to: {dir_out_CMIP5_Monthly_i_model}')
        
        
        
del df_GB_yyyymm # to save RAM

# =============================================================================
# %% .   Calculate mean P_s_monthly for each RCP
# =============================================================================
# input('pause')
for i in dict_rcp: # for each RCP...
    i_rcp = dict_rcp[i] # turn the index "i" into an rcp string
    print(f'Processing P_s_monthly for {i_rcp}...')



    for j in dict_model: # for each model...
        i_model = dict_model[j]
        print(f'   Locating {i_model} {i_rcp}...')
        infile_form_P_s_monthly = os.path.join(dir_out_CMIP5_Monthly,f'*{i_model}_{i_rcp}.csv')
        infile_P_s_monthly = glob.glob(infile_form_P_s_monthly) 
        
        if len(infile_P_s_monthly) != 1: # Generates a list, but should only have one file per loop.
            input(f'ERROR: Check input directory: {infile_P_s_monthly}')

        # Load the monthly mean data for the target i_rcp and i_model

        if j == 1: # for the first model, set up the dataframe
            print(f'   First model; performing init setup for {i_model}...')
            df_Ps_Rain = pd.DataFrame() # set up empty dfs
            df_Ps_Evap = pd.DataFrame()
            df_Ps_Temp = pd.DataFrame()
            df_Ps_RainAdj = pd.DataFrame()
            
            print(f'   Reading df_Ps_in for {i_model}...')
            # load i_model's data
            df_Ps_in = pd.read_csv(infile_P_s_monthly[0],parse_dates=['time']) 
            df_Ps_in.set_index(['time'],inplace=True) # set the datetime index first so that values line up when concat'ing
            
            
            # Extract columns 
            print('      Extracting Rain...')
            df_Ps_Rain[f'{i_model}'] = df_Ps_in[cn_P]
            print('      Extracting Evap...')
            df_Ps_Evap[f'{i_model}'] = df_Ps_in[cn_E]
            print('      Extracting Temp...')
            df_Ps_Temp[f'{i_model}'] = df_Ps_in[cn_T]
            print('      Extracting RainAdj...')
            df_Ps_RainAdj[f'{i_model}'] = df_Ps_in[cn_Padj]
            
            # input('check df_Ps after init')
        else: # For all subsequent models, just concat to previous set up    
        # Concat data to average with other models
            print(f'   Reading df_Ps_in for {i_model}...')
            df_Ps_in = pd.read_csv(infile_P_s_monthly[0],parse_dates=['time'])
            df_Ps_in.set_index(['time'],inplace=True)

            # Extract columns 
            print('      Extracting Rain...')
            df_Ps_Rain[f'{i_model}'] = df_Ps_in[cn_P]
            print('      Extracting Evap...')
            df_Ps_Evap[f'{i_model}'] = df_Ps_in[cn_E]
            print('      Extracting Temp...')
            df_Ps_Temp[f'{i_model}'] = df_Ps_in[cn_T]
            print('      Extracting RainAdj...')
            df_Ps_RainAdj[f'{i_model}'] = df_Ps_in[cn_Padj]

            
            
            
            # input('check df_Ps after first concat')
    
    # Once all models have been joined to their respective df_Ps; the loop ends.
    
# =============================================================================
#%% .   Export P_s_monthly
# =============================================================================
    
    df_Ps_export = pd.DataFrame()
    df_Ps_export.index = df_Ps_in.index
    df_Ps_export[cn_P] = df_Ps_Rain.mean(axis=1)
    df_Ps_export[cn_E] = df_Ps_Evap.mean(axis=1)
    df_Ps_export[cn_T] = df_Ps_Temp.mean(axis=1)
    df_Ps_export[cn_Padj] = df_Ps_RainAdj.mean(axis=1)
    
    # input('check df_Ps before export')
    
    # drop first row (1984-12) because the EvapPot[mm] will always be nan (no 7-day moving avg temp)
    df_Ps_export.drop(index=df_Ps_export.index[0], axis=0,inplace=True)
    
    # Add a YYYY and MM col
    df_Ps_export['YYYY-MM'] = df_Ps_export.index.year.astype(str) + "-" + (df_Ps_export.index.month).astype(str)
    df_Ps_export['MM'] = df_Ps_export.index.month
    
    
    
    print('Exporting df_Ps to file...')
    dir_out_CMIP5_Ps = os.path.join(dir_out_CMIP5_Monthly,f"P_s_monthly~{i_rcp}.csv")
    df_Ps_export.to_csv(dir_out_CMIP5_Ps,index=True)
   
    
# =============================================================================
# %% P_c_monthly: Load SILO observations for defined control period
# =============================================================================
# Repeat the above code, but we'll need to also create month-averages... with groupby?

#
print(f'Loading input SILO data for P_c_monthly..')
df_Pc_in = pd.read_csv(dir_in_SILO,parse_dates=['time'])
df_Pc_in.set_index(['time'],inplace=True)

# selecting rows between our start and end dates
mask_Pc = (df_Pc_in.index >= date_start_Pc) & (df_Pc_in.index <= date_end_Pc)
df_Pc_trim = df_Pc_in.loc[mask_Pc]
print(f'   Reference period set between {date_start_Pc} & {date_end_Pc}')



# Calc some summary statistics of the whole dataset
ss_P_silo = df_Pc_trim[cn_s_P].agg(["min","max","mean","skew","std"])
ss_E_silo = df_Pc_trim[cn_s_E].agg(["min","max","mean","skew","std"])

# Create month column
df_Pc_trim['Month'] = df_Pc_trim.index.month

# Groupby month column
df_Pc_monthly = df_Pc_trim.groupby('Month').mean()

# Save to file
df_Pc_monthly.to_csv(dir_out_Pc)


# =============================================================================
# %% P_o to P_p set up
# =============================================================================
# P_p = (P_s_monthly/P_c_monthly) * P_o

# Loading P_o data 
# df_Po_in = pd.read_csv(dir_in_SILO,parse_dates=['time'])
    # already loaded in from last, cell as df_Pc_in

# Give input SILO data (P_o) the same time index as P_p
    # i.e. Give the SILO data the date index of the CMIP5 models such that
    # 1-1-1900 becomes 1-1-1985
from datetime import date
df_Pp = df_Pc_in
df_Pp.index = df_Pc_in.index + pd.Timedelta(days=(date(1985,1,1)-date(1900,1,1)).days)

df_Pp['YYYY-MM'] = df_Pp.index.year.astype(str) + "-" + (df_Pp.index.month).astype(str)
df_Pp['MM'] = df_Pp.index.month

# Dirs to load later
# dir_in_Ps_rcp45
# dir_in_Ps_rcp85
# dir_out_Pc # Already loaded as df_Pc_monthly

# Append P_c_monthly to the months using a Join
# df_Pp_join = df_Pp.join(df_Pc_monthly, on='MM')



# Repeat for each RCP...

for i in dict_rcp:
    i_rcp = dict_rcp[i]
    i_Ps_dir = dict_Ps_dirs[i]
    print(f'Performing Delta-Change M1 with {i_rcp}...')
    
    # Load in relevant Ps data
    df_Ps_in = pd.read_csv(i_Ps_dir,parse_dates=['time']) 
    
    # Merge Ps data to Po data
    df_Pp_merge = pd.merge(df_Pp,df_Pc_monthly, left_on="MM", right_index=True, how="left")

    # Merge P_s_monthly to the corresponding YYYY-MM in the Po data
    df_Pp_merge = pd.merge(df_Pp_merge, df_Ps_in, left_on='YYYY-MM', right_on='YYYY-MM',how="left")

    df_Pp_merge.index = df_Pp.index # bc merge deletes the original timeseries index

    print('   Merge complete')
    


#  Calc alpha (P_s_monthly/P_c_monthly) to calculate Pp and Ep
        # Po data has been marked with _x
        # Pc data has been marked with _y
        # Ps data had different col name ["EvapPot[mm]"] a
    df_Pp_merge[f'Ep_{i_rcp}'] = (df_Pp_merge["EvapPot[mm]"]/df_Pp_merge['et_morton_potential_y'])*df_Pp_merge['et_morton_potential_x']
    df_Pp_merge[f'Pp_{i_rcp}'] = (df_Pp_merge["rnd24.daily"]/df_Pp_merge['daily_rain_y'])*df_Pp_merge['daily_rain_x']
    df_Pp_merge[f'Pp_adj_{i_rcp}'] = (df_Pp_merge["rnd24Adjust.daily"]/df_Pp_merge['daily_rain_y'])*df_Pp_merge['daily_rain_x']
    print('Pp and Ep calculations complete')

    input('check df_Pp_merge before col drops')
# Clean up columns names, and drop unneeded rows (past 2099-12-31)
    Pp_export_cols = [f'Ep_{i_rcp}',f'Pp_{i_rcp}',f'Pp_adj_{i_rcp}']
    df_Pp_export = df_Pp_merge.loc[:,df_Pp_merge.columns.intersection(Pp_export_cols)]
    input('check df_Pp_merge after col drops')

# Export the Pp,Pp_adj, and Ep timeseries to file
    fn_M1 = f"DeltaChangeM1-{i_rcp}.csv"
    print(f'Saving {fn_M1}...')
    dir_out_M1 = os.path.join(dir_out,fn_M1)
    df_Pp_export.to_csv(dir_out_M1)
    print('   Done!')




# TODO: Delta Change calculation based on M2, or others from the paper?
























