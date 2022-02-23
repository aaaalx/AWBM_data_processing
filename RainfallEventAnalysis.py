# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 14:43:52 2021

@author: Alex.Xynias
"""
import pandas as pd
import numpy as np
import time

# =============================================================================
#%% User inputs
# =============================================================================
# Location of Rainfall data .csv
    # Script is expecting precip data under the header "P[mm]" and evap under "E[mm]"

# dir_Data = 'D:/OneDrive/Documents/Uni/Honours Thesis/Data/SILO_downloads/Compile/SILO_Gregors_1985-2020-pd.csv'
dir_Data = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data/SILO_downloads/Compile/SILO_Gregors_1985-2020-pd.csv' 
data_name = 'SILO_Gregors_' # Data source / location for outpile file naming

# dir_Data = 'D:/OneDrive/Documents/Uni/Honours Thesis/Data/SILO_downloads/Compile/SILO_Full_1985-2020-pd.csv'
# dir_Data = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data/SILO_downloads/Compile/SILO_Full_1985-2020-pd.csv'
# data_name = 'SILO_Full_' # for outpile file naming


# dir_Export = 'D:/OneDrive/Documents/Uni/Honours Thesis/Data_processing/EventAnalysis/'
dir_Export = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data_processing/EventAnalysis/'

Thresh = float(0) # Rainfall threshold, minimum amount of rain which defines a "wet" day [mm]
n_events = 50 # longest n events to export 
    # TODO: Maybe have this input be a minimum duration of the event in interest.


# Optional trimming of input data to range of dates
ApplyTrim = False # Use True/False or bool(1)/bool(0)
date_start = pd.to_datetime('2000-1-1', format='%Y-%m-%d')
date_end = pd.to_datetime('2020-12-31', format='%Y-%m-%d')

SkipPlots = True # optional skip of plotting section

print('User inputs set...')
# =============================================================================
#%% Other Setup 
# =============================================================================

if ApplyTrim == True: # set the prefix for output files
    project_name = (data_name + str(date_start.year) + '-' + str(date_end.year) + '_') # prefix for output files
else:
    project_name = (data_name + '1985-2020_') 

input(f'Enter to continue for {project_name} with trim = {ApplyTrim}...')
# =============================================================================
#%% Setting up dataframes 
# =============================================================================
tic_script = time.time()
# Loading input data & df
df_in = pd.read_csv(dir_Data)
df_in['Date'] = pd.to_datetime(df_in['Date'], dayfirst=True) # fix input date formatting
df_in = df_in.set_index('Date') # sets the date column as the dataframe index 

if ApplyTrim == True:
    print(f'Trimming input data between {str(date_start)[:-9]} : {str(date_end)[:-9]}') #-9 to remove time of day info
    df_in = df_in[date_start:date_end]
 
df_in['dS'] = df_in['P[mm]'] - df_in['E[mm]'] # Adds new column calculating P_i-E_i

# Create day column for indexing
df_day_test = df_in.insert(loc=0, column='Day', value=np.arange(len(df_in)))


print('...df_in set up')
# =============================================================================
#%% Event Analysis
# =============================================================================
# Basic stats
Days = len(df_in) # Number of days in the input data

RainDays = np.sum(df_in['P[mm]'] > 0) # Get total number of days with rain
DryDays = np.sum(df_in['P[mm]'] == 0)  # Get total number of days without rain

DryDays_thresh = np.sum(df_in['P[mm]'] <= Thresh)  # Get total number of days below threshold 
RainDays_thresh = np.sum(df_in['P[mm]'] >= Thresh) # Get total days of rain above threshold

WetDays_net = np.sum(df_in['dS'] > 0) # Total number of days where P>E
DryDays_net = np.sum(df_in['dS'] < 0) # Total number of days where P<E


   
#%% WIP Categorise Events V2: without iter using apply/lambda to make the analysis faster (?)
print('Categorising events...')

df_cat_headers = ['Day','P[mm]','E[mm]','dS'
                  ,'CurrentlyWet_net'
                  ,'CurrentlyDry_net'
                  ,'CurrentlyWet'
                  ,'CurrentlyDry'
                  ,'Wet_net_streak'
                  ,'Dry_net_streak'
                  ,'Dry_streak'
                  ,'Wet_streak'
                  # ,'CummRain' # don't need this stat at the moment, removing for now
                 ]


df_cat = pd.DataFrame(df_in, columns = df_cat_headers) # set up the working df for categorising
del df_in # remove the raw input from memory


# https://datatofish.com/if-condition-in-pandas-dataframe/
# df['new column name'] = df['column name'].apply(lambda x: 'value if condition is met' if x condition else 'value if condition is not met')

df_cat['CurrentlyDry_net'] = df_cat['dS'].apply(lambda x: int(1) if x < 0 else int(0))
df_cat['CurrentlyWet_net'] = df_cat['dS'].apply(lambda x: int(1) if x>0 else int(0))
                        # if today is net wet (dS>0): True, else False
                        
df_cat['CurrentlyDry'] = df_cat['P[mm]'].apply(lambda x: int(1) if x <= Thresh else int(0))                       
df_cat['CurrentlyWet'] = df_cat['P[mm]'].apply(lambda x: int(1) if x > Thresh else int(0))
                        # if today is  wet (P>Threshold): True, else False      

# Group the events and count duration: https://stackoverflow.com/questions/27626542/counting-consecutive-positive-values-in-python-pandas-array
df_cat['Dry_net_streak'] = df_cat['CurrentlyDry_net'] * (df_cat['CurrentlyDry_net'].groupby((df_cat['CurrentlyDry_net'] != df_cat['CurrentlyDry_net'].shift()).cumsum()).cumcount() + 0)
df_cat['Wet_net_streak'] = df_cat['CurrentlyWet_net'] * (df_cat['CurrentlyWet_net'].groupby((df_cat['CurrentlyWet_net'] != df_cat['CurrentlyWet_net'].shift()).cumsum()).cumcount() + 0)
df_cat['Wet_streak'] = df_cat['CurrentlyWet'] * (df_cat['CurrentlyWet'].groupby((df_cat['CurrentlyWet'] != df_cat['CurrentlyWet'].shift()).cumsum()).cumcount() + 0)
df_cat['Dry_streak'] = df_cat['CurrentlyDry'] * (df_cat['CurrentlyDry'].groupby((df_cat['CurrentlyDry'] != df_cat['CurrentlyDry'].shift()).cumsum()).cumcount() + 0)
    # the +1 is really just for when you want to do a human style count vs a 0th start count for the event durations

toc_script = time.time() - tic_script 
print(f'... Categorisation complete : {toc_script}')

# =============================================================================
#%% Export suitable simulation start dates
# =============================================================================    
# Export df_cat to file 
fn_df_cat = (dir_Export + project_name[:-1] + '.csv') # sets the export filename 
df_cat.to_csv(fn_df_cat)


# find end date of longest streaks: https://stackoverflow.com/questions/6910641/how-do-i-get-indices-of-n-maximum-values-in-a-numpy-array


index_max_streak_dry = np.argpartition(df_cat['Dry_streak'], -n_events)[-n_events:] # indexes the maximum n values
export_dry = df_cat.iloc[index_max_streak_dry].sort_values(by=['Dry_streak'], ascending=False) # crops dataframe to those indexes and sort high to low
export_dry = export_dry.loc[:, ['Dry_streak']] # drop other columns


index_max_streak_dry_net = np.argpartition(df_cat['Dry_net_streak'], -n_events)[-n_events:]
export_dry_net = df_cat.iloc[index_max_streak_dry_net].sort_values(by=['Dry_net_streak'], ascending=False)
export_dry_net = export_dry_net.loc[:, ['Dry_net_streak']] 

index_max_streak_wet = np.argpartition(df_cat['Wet_streak'], -n_events)[-n_events:]
export_wet = df_cat.iloc[index_max_streak_wet].sort_values(by=['Wet_streak'], ascending=False)
export_wet = export_wet.loc[:, ['Wet_streak']]

index_max_streak_wet_net = np.argpartition(df_cat['Wet_net_streak'], -n_events)[-n_events:]
export_wet_net = df_cat.iloc[index_max_streak_wet_net].sort_values(by=['Wet_net_streak'], ascending=False)
export_wet_net = export_wet_net.loc[:, ['Wet_net_streak']]


df_export = pd.concat([export_dry,export_dry_net,export_wet,export_wet_net], axis = 1) # concat into single df

fn_df_export = (dir_Export + project_name + 'top' + str(n_events) + '.csv') # generate filename
df_export.to_csv(fn_df_export) # save to file

toc_script = time.time() - tic_script 

# =============================================================================
#%% Plotting
# =============================================================================


if SkipPlots == False:
    print('Plotting...')
    
    import calplot # https://github.com/tomkwok/calplot
    import seaborn as sns
    import matplotlib.pyplot as plt
    
    # Calendar plots
    
    def calenderplot(df,col,title="",cmap=""):
        # https://calplot.readthedocs.io/en/latest/
            # https://medium.com/pandex-journal/create-time-series-heat-maps-using-a-pandas-extension-dff41df1d393
        # https://thiago-bernardes-carvalho.medium.com/calendar-heatmaps-with-pythons-calplot-b4dec29ee805
        
        # plot = calplot.yearplot(df[col]
        #                         ,year=2000    
        plot = calplot.calplot(df[col]
                                # ,how = 'sum'
                                ,cmap = cmap # https://matplotlib.org/stable/tutorials/colors/colormaps.html
                                ,suptitle  = title
                                )[0] 
    
        plot.savefig(fname = (dir_Export + project_name + 'Calplot_' + title + '.png')
                     ,format = 'png'
                     ,bbox_inches="tight"
                     )
    
    calenderplot(df_cat,'Dry_net_streak',title='Dry net streak', cmap = 'YlOrRd')
    calenderplot(df_cat,'Wet_net_streak',title='Wet net streak',cmap = 'Blues')

    calenderplot(df_cat,'Dry_streak',title='Dry streak', cmap = 'YlOrRd')
    calenderplot(df_cat,'Wet_streak',title='Wet streak',cmap = 'Blues')
    
    # Timeseries Plots
    # https://www.kdnuggets.com/2018/07/5-quick-easy-data-visualizations-python-code.html
    # https://www.dataquest.io/blog/tutorial-time-series-analysis-with-pandas/
    # https://seaborn.pydata.org/generated/seaborn.lineplot.html
    # https://matplotlib.org/stable/tutorials/colors/colors.html
    
    def ts_plot(y_data, y_label="", title="",color=""):

        # Use seaborn style defaults and set the default figure size
        sns.set(rc={'figure.figsize':(100, 4)})
        
        # Create the plot object
        _, ax = plt.subplots()
        ax.set_title(title)
        ax.set_xlabel("Date")
        ax.set_ylabel(y_label)
        
        plt.plot(y_data, lw = 2, color=color) 
        
        plt.savefig(fname = (dir_Export + project_name + 'TS_' + title + '.png')
                     ,format = 'png'
                     ,bbox_inches="tight"
                     )
        
    ts_plot(df_cat['Wet_streak'], y_label="Wet Streak [days]",title="Wet Periods",color="xkcd:azure")
    ts_plot(df_cat['Wet_net_streak'], y_label="Net Wet Streak [days]",title="Net Wet Periods",color="xkcd:azure")
    
    ts_plot(df_cat['Dry_streak'], y_label="Dry Streak [days]",title="Dry Periods",color="xkcd:crimson")
    ts_plot(df_cat['Dry_net_streak'],y_label="Net Dry Streak [days]",title="Net Dry Periods",color="xkcd:crimson")
    
    # def heatmapplot(df,col,title_in,cmap_in):
        # https://datavizpyr.com/heatmaps-with-seaborn-in-python/
else:
    print('Plotting Skipped')


print(f'== Script Complete == t = {toc_script}')

