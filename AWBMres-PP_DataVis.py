"""
Created on Thu Jun  2 12:21:31 2022

@author: alex.xynias

DataVis component of the post processing

# https://towardsdatascience.com/plotting-time-series-boxplots-5a21f2b76cfe
# https://seaborn.pydata.org/tutorial/aesthetics.html


"""

# =============================================================================
# %% Setup and Inputs
# =============================================================================

import glob
import pandas as pd
import numpy as np
import os
# from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import seaborn

dict_model = {
    # RCP4.5
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
    11: 'NorESM1-MQ', # Norwegian Earth System Model, version 1 (intermediate resolution)
    }

dict_rcp = {
    1: 'rcp45'
    ,2: 'rcp85'    
    }

dict_bias = {
    1: 'BC'
    ,2: 'NBC'
    }


# Directories
# dir_results_in = r'C:\Users\Alex\OneDrive\Documents\Uni\Honours Thesis\output_AWBMres-Forecast'
dir_in = r"C:\Users\alex.xynias\OneDrive - Water Technology Pty Ltd\UQ\Thesis\Data\output_AWBMres-Forecast\PP\GB_annual"
dir_PlotsOut = dir_in + r'\Plots'


# =============================================================================
# %% Percentage from delta-change values
# =============================================================================

# Define colums we want to compare between files    
target_cols_PercentFromBase = ['P_%change','E_%change','resVol[m3]_%change','resVol%_%change','Qtotal_%change']

df_out = pd.DataFrame()
df_out_mean = pd.DataFrame()
for var_comp in target_cols_PercentFromBase:
    for i in dict_rcp:
        i_rcp = dict_rcp[i] # This line could have been avoided by using an inpuy list, but the dicts were copy/pasted from prev script; so this was faster
        print(f'Processing {i_rcp}...')
        for j in dict_bias:
            i_bias = dict_bias[j]
            print(f'   Processing {i_bias}...')
            for k in dict_model:
                i_model = dict_model[k]
                print(f'      Loading {i_model}...')
                i_dir_infile = os.path.join(dir_in,f'AnnualChange~{i_model}~{i_rcp}~{i_bias}.csv')
    
                print(f'         Compiling {var_comp} data')
                df_comp_in = pd.read_csv(i_dir_infile,usecols=['Date',var_comp],parse_dates=['Date'])
                df_comp_in.set_index('Date',inplace=True)
                df_comp_in.index = df_comp_in.index.year
                                                
                # Rename column to reflect data source (Just model, rcp and bias in the filename?)
                df_comp_in.rename(columns={var_comp : f'{i_model}'},inplace=True)           
                                
                # Append column to a df_out to save to file (re-read then plot so that the raw data can be viewed later)
                df_out = pd.concat([df_out,df_comp_in],axis=1)
                    
            # After each model has been added to df_out, calculate an average column
            df_out[f'Mean_{i_rcp}_{i_bias}'] = df_out.mean(axis=1)
            df_out_mean[f'{var_comp}_{i_rcp}_{i_bias}'] = df_out.mean(axis=1)
            
            # export to file with descriptive filename
            fn_out = f'Percent~AnnualChangeComp~{var_comp}~{i_rcp}~{i_bias}.csv'
            print(f'   Exporting {fn_out}')
            df_out.to_csv(os.path.join(dir_PlotsOut,fn_out))
            df_out = pd.DataFrame() 
            # Export df is being init here again so that it can be reset before moving to next category of results

# Export a csv of only the means to file for easy plotting later
fn_out = 'Mean~Percent~AnnualChangeComp.csv'
print(f'   Exporting {fn_out}')
df_out_mean.to_csv(os.path.join(dir_PlotsOut,fn_out))

# =============================================================================
# %% Abolsute Values
# =============================================================================
target_cols_Absolute = ['P','E','resVolume[m3]','resVol_beforespill[%]','Qtotal']
df_out = pd.DataFrame()
df_out_mean = pd.DataFrame()
for var_comp in target_cols_Absolute:
    for i in dict_rcp:
        i_rcp = dict_rcp[i] # This line could have been avoided by using an inpuy list, but the dicts were copy/pasted from prev script; so this was faster
        print(f'Processing {i_rcp}...')
        for j in dict_bias:
            i_bias = dict_bias[j]
            print(f'   Processing {i_bias}...')
            for k in dict_model:
                i_model = dict_model[k]
                print(f'      Loading {i_model}...')
                i_dir_infile = os.path.join(dir_in,f'AnnualChange~{i_model}~{i_rcp}~{i_bias}.csv')
    
                print(f'         Compiling {var_comp} data')
                df_comp_in = pd.read_csv(i_dir_infile,usecols=['Date',var_comp],parse_dates=['Date'])
                df_comp_in.set_index('Date',inplace=True)
                df_comp_in.index = df_comp_in.index.year
                                                
                # Rename column to reflect data source (Just model, rcp and bias in the filename?)
                df_comp_in.rename(columns={var_comp : f'{i_model}'},inplace=True)           
                                
                # Append column to a df_out to save to file (re-read then plot so that the raw data can be viewed later)
                df_out = pd.concat([df_out,df_comp_in],axis=1)
                    
            # After each model has been added to df_out, calculate an average column
            df_out[f'Mean_{i_rcp}_{i_bias}'] = df_out.mean(axis=1)
            df_out_mean[f'{var_comp}_{i_rcp}_{i_bias}'] = df_out.mean(axis=1)
            
            # export to file with descriptive filename
            fn_out = f'Absolute~AnnualChangeComp~{var_comp}~{i_rcp}~{i_bias}.csv'
            print(f'   Exporting {fn_out}')
            df_out.to_csv(os.path.join(dir_PlotsOut,fn_out))
            df_out = pd.DataFrame() 
            # Export df is being init here again so that it can be reset before moving to next category of results

# Export a csv of only the means to file for easy plotting later
fn_out = 'Mean~Absolute~AnnualChangeComp.csv'
print(f'   Exporting {fn_out}')
df_out_mean.to_csv(os.path.join(dir_PlotsOut,fn_out))

    

# =============================================================================
#%% Timeseries box plots 
# =============================================================================
# Create a Timeseries Box/Whisper plot for each of the files generated above
    # For each, every 'Date' will always be the x-axis - every other column will be y-data
    # Output filename can be the same as the input csv
    
# TODO: Groupby Decade for this one?
def plotBoxWhisp_Percent(dir_parent,fn_in,cond_filter,format_ColName,showfliers,title):
    # https://towardsdatascience.com/plotting-time-series-boxplots-5a21f2b76cfe
    # https://stackoverflow.com/questions/43434020/black-and-white-boxplots-in-seaborn
    global df_in_plot, df_plot
        # Helps to debug in variable explorer
    
    # Load data from directory
    df_in_plot = pd.read_csv(os.path.join(dir_parent,fn_in)
                             # ,parse_dates=['Date']
                             )
    df_in_plot.set_index(['Date'],inplace=True)
    
    # Filter for column name condition
    if cond_filter == True:
        df_plot = df_in_plot.filter(like=format_ColName)
    else:
        df_plot = df_in_plot

    fig, ax = plt.subplots(figsize=(20,10))

    seaborn.set_context("talk")
    seaborn.boxplot(data = df_plot.T #df_plot.iloc[1:].T  #df_plot.iloc[:-1].T
                    ,ax=ax 
                    ,color='white'
                    ,width=.5
                    ,fliersize=4
                    ,showfliers = showfliers
                    )
    # Vertical year labels
    ax.set_xticklabels(ax.get_xticklabels(), rotation = 90)
    
    # axis labels
    ax.set_ylabel("% Change From Delta-Change")
    ax.set_xlabel("Simulation Year")

    # Fix box plot colours
    plt.setp(ax.artists, edgecolor = 'k', facecolor='w')
    plt.setp(ax.lines, color='k')

    # Plot red horizontal line at 0%
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.axhline.html
    ax.axhline(0,color='r')

    # Year label ticks
    ax.xaxis.set_major_locator(ticker.MultipleLocator(5))

    # Set Plot title
    ax.set(title=title)
    
    # Save plot to file    
    plt.savefig(os.path.join(dir_parent,f'plotBoxWhisp_Percent~{title}.png'))
    

#%%.   Rainfall
dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~P_%change~rcp85~BC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~P_%change~rcp85~BC"
showfliers = True
plotBoxWhisp_Percent(dir_parent,fn_in,cond_filter,format_ColName,showfliers,title)

dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~P_%change~rcp85~NBC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~P_%change~rcp85~NBC"
showfliers = True
plotBoxWhisp_Percent(dir_parent,fn_in,cond_filter,format_ColName,showfliers,title)

dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~P_%change~rcp45~BC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~P_%change~rcp45~BC"
showfliers = True
plotBoxWhisp_Percent(dir_parent,fn_in,cond_filter,format_ColName,showfliers,title)

dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~P_%change~rcp45~NBC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~P_%change~rcp45~NBC"
showfliers = True
plotBoxWhisp_Percent(dir_parent,fn_in,cond_filter,format_ColName,showfliers,title)

#%%.   Evap
dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~E_%change~rcp85~BC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~E_%change~rcp85~BC"
showfliers = True
plotBoxWhisp_Percent(dir_parent,fn_in,cond_filter,format_ColName,showfliers,title)

dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~E_%change~rcp85~NBC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~E_%change~rcp85~NBC"
showfliers = True
plotBoxWhisp_Percent(dir_parent,fn_in,cond_filter,format_ColName,showfliers,title)

dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~E_%change~rcp45~BC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~E_%change~rcp45~BC"
showfliers = True
plotBoxWhisp_Percent(dir_parent,fn_in,cond_filter,format_ColName,showfliers,title)

dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~E_%change~rcp45~NBC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~E_%change~rcp45~NBC"
showfliers = True
plotBoxWhisp_Percent(dir_parent,fn_in,cond_filter,format_ColName,showfliers,title)

#%%.   Q_total
dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~Qtotal_%change~rcp45~BC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~Qtotal_%change~rcp45~BC"
showfliers = True
plotBoxWhisp_Percent(dir_parent,fn_in,cond_filter,format_ColName,showfliers,title)

dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~Qtotal_%change~rcp45~NBC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~Qtotal_%change~rcp45~NBC"
showfliers = True
plotBoxWhisp_Percent(dir_parent,fn_in,cond_filter,format_ColName,showfliers,title)

dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~Qtotal_%change~rcp85~BC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~Qtotal_%change~rcp85~BC"
showfliers = True
plotBoxWhisp_Percent(dir_parent,fn_in,cond_filter,format_ColName,showfliers,title)

dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~Qtotal_%change~rcp85~NBC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~Qtotal_%change~rcp85~NBC"
showfliers = True
plotBoxWhisp_Percent(dir_parent,fn_in,cond_filter,format_ColName,showfliers,title)


#%%.   resVol[m3]
dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~resVol[m3]_%change~rcp45~BC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~resVol[m3]_%change~rcp45~BC"
showfliers = True
plotBoxWhisp_Percent(dir_parent,fn_in,cond_filter,format_ColName,showfliers,title)

dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~resVol[m3]_%change~rcp45~NBC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~resVol[m3]_%change~rcp45~NBC"
showfliers = True
plotBoxWhisp_Percent(dir_parent,fn_in,cond_filter,format_ColName,showfliers,title)

dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~resVol[m3]_%change~rcp85~BC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~resVol[m3]_%change~rcp85~BC"
showfliers = True
plotBoxWhisp_Percent(dir_parent,fn_in,cond_filter,format_ColName,showfliers,title)

dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~resVol[m3]_%change~rcp85~NBC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~resVol[m3]_%change~rcp85~NBC"
showfliers = True
plotBoxWhisp_Percent(dir_parent,fn_in,cond_filter,format_ColName,showfliers,title)


# =============================================================================
# %% Timeseries plot with error bands
# =============================================================================
# https://seaborn.pydata.org/examples/errorband_lineplots.html
# Potentially clearer than the timeseries box plot for showing the range of variation in the TERN ensemble
# plotBoxWhisp_Percent(dir_parent,fn_in,cond_filter,format_ColName,showfliers,title)

def plotTSError_Percent(dir_parent,fn_in,cond_filter,format_ColName,title):
    global df_in_plot, df_plot, df_plot_stack,test,test2
    
    # Load data from directory
    df_in_plot = pd.read_csv(os.path.join(dir_parent,fn_in)
                              # ,parse_dates=['Date']
                             )
    df_in_plot.set_index(['Date'],inplace=True)


    # Filter for column name condition
    if cond_filter == True:
        df_plot = df_in_plot.filter(like=format_ColName)
    else:
        df_plot = df_in_plot


    # Prepare data structure
    df_plot_stack = df_plot.stack().reset_index(level=1).rename(columns={"level_1":"Model"})
    
    
    
    # Plot data
    seaborn.set_context("talk")

    fig, ax = plt.subplots(figsize=(20,10))

    seaborn.lineplot(data=df_plot_stack
                     
                     )
    
    
    
    # Extra plot formatting
        # axis labels
    ax.set_ylabel("% Change From Delta-Change")
    ax.set_xlabel("Simulation Year")
        # Horizontal 0% line
    ax.axhline(0,color='r')
        # Set Plot title
    ax.set(title=title)
    
    # Save plot to file    
    plt.savefig(os.path.join(dir_parent,f'plotTSError_Percent~{title}.png'))




#%%.   Rainfall
dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~P_%change~rcp85~BC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~P_%change~rcp85~BC"
plotTSError_Percent(dir_parent,fn_in,cond_filter,format_ColName,title)

dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~P_%change~rcp85~NBC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~P_%change~rcp85~NBC"
plotTSError_Percent(dir_parent,fn_in,cond_filter,format_ColName,title)

dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~P_%change~rcp45~BC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~P_%change~rcp45~BC"
plotTSError_Percent(dir_parent,fn_in,cond_filter,format_ColName,title)

dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~P_%change~rcp45~BC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~P_%change~rcp45~BC"
plotTSError_Percent(dir_parent,fn_in,cond_filter,format_ColName,title)

#%%.   Evap
dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~E_%change~rcp85~BC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~E_%change~rcp85~BC"
plotTSError_Percent(dir_parent,fn_in,cond_filter,format_ColName,title)

dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~E_%change~rcp85~NBC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~E_%change~rcp85~NBC"
plotTSError_Percent(dir_parent,fn_in,cond_filter,format_ColName,title)

dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~E_%change~rcp45~BC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~E_%change~rcp45~BC"
plotTSError_Percent(dir_parent,fn_in,cond_filter,format_ColName,title)

dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~E_%change~rcp45~BC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~E_%change~rcp45~BC"
plotTSError_Percent(dir_parent,fn_in,cond_filter,format_ColName,title)

#%%.   Q_total
dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~Qtotal_%change~rcp85~BC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~Qtotal_%change~rcp85~BC"
plotTSError_Percent(dir_parent,fn_in,cond_filter,format_ColName,title)

dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~Qtotal_%change~rcp85~NBC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~Qtotal_%change~rcp85~NBC"
plotTSError_Percent(dir_parent,fn_in,cond_filter,format_ColName,title)

dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~Qtotal_%change~rcp45~BC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~Qtotal_%change~rcp45~BC"
plotTSError_Percent(dir_parent,fn_in,cond_filter,format_ColName,title)

dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~Qtotal_%change~rcp45~BC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~Qtotal_%change~rcp45~BC"
plotTSError_Percent(dir_parent,fn_in,cond_filter,format_ColName,title)

#%%.   resVol[m3]
dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~resVol[m3]_%change~rcp85~BC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~resVol[m3]_%change~rcp85~BC"
plotTSError_Percent(dir_parent,fn_in,cond_filter,format_ColName,title)

dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~resVol[m3]_%change~rcp85~NBC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~resVol[m3]_%change~rcp85~NBC"
plotTSError_Percent(dir_parent,fn_in,cond_filter,format_ColName,title)

dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~resVol[m3]_%change~rcp45~BC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~resVol[m3]_%change~rcp45~BC"
plotTSError_Percent(dir_parent,fn_in,cond_filter,format_ColName,title)

dir_parent = dir_PlotsOut
fn_in = "Percent~AnnualChangeComp~resVol[m3]_%change~rcp45~BC.csv"
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~resVol[m3]_%change~rcp45~BC"
plotTSError_Percent(dir_parent,fn_in,cond_filter,format_ColName,title)

 



# =============================================================================
#%% Multi-Input Timeseries plot with error bands
# ============================================================================


def plotTSErrorMULTI_Percent(form_infile,dir_parent,title,cond_filter,format_ColName):
    global df_in_plot,df_plot_stack,df_comp,i_junk,list_infiles
    
    # Filename structure to group together:
    list_infiles = glob.glob(os.path.join(dir_parent,form_infile))
    
    df_comp = pd.DataFrame() # Init and refresh the compilation dataframe
    i_junk = 0 # For a duct-tape way of dealing with duplicate column names
    for f in list_infiles:
        # print('hello')
        i_group = '~'.join(f.split("~")[3:])[:-4]
        i_junk += 1 # adds one to the counter
        # Load data from file
        # Load data from directory
        df_in_plot = pd.read_csv(f
                                  # ,parse_dates=['Date']
                                 )
        df_in_plot.set_index(['Date'],inplace=True)
    
        # Filter for column name condition
        if cond_filter == True:
            df_plot = df_in_plot.filter(like=format_ColName)
        else:
            df_plot = df_in_plot
    
        # Prepare data structure
        df_plot_stack = df_plot.stack().reset_index(level=1)
        
        # Rename Column to group label
        if i_junk == 1: # for the first stack...
            df_plot_stack = df_plot_stack.rename(columns={"level_1":"Model",0: i_group})
        else:
            df_plot_stack = df_plot_stack.rename(columns={"level_1":"Junk",0: i_group})
    
        # Add file to master df for plotting
        df_comp = pd.concat([df_comp,df_plot_stack],axis=1)
       
        
    
    # After all the input data is compiled, drop the Junk model labels
    df_comp.drop('Junk',axis=1,inplace=True)
    # df_comp.reset_index(inplace=True)
    
    # Misc formatting and axis setup
    fig, ax = plt.subplots(figsize=(20,10))
    seaborn.set_context("talk")
    seaborn.set_style("whitegrid")
    seaborn.set_palette("Paired")
    
    seaborn.lineplot(data=df_comp.loc[1990:] # df_comp.loc[2000:]
                     ,dashes=[(5, 1),(5, 1),(5, 1),(5, 1)]
                     ,
                     )
    
    # Extra plot formatting
    ax.set_ylim([-100,300])
    
        # Assign a qualitative colormap ("Paired") 
    
        # axis labels
    ax.set_ylabel("% Change From Delta-Change")
    ax.set_xlabel("Simulation Year")
        # Horizontal 0% line
    ax.axhline(0,color='red')
        # Set Plot title
    ax.set(title=title)

    # save to file
    plt.savefig(os.path.join(dir_parent,f'plotTSErrorMULTI_Percent~{title}.png'))



#%%.   Rainfall
dir_parent = dir_PlotsOut
form_infile = 'Percent~AnnualChangeComp~P_%change~*.csv'
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~P_%change"
plotTSErrorMULTI_Percent(form_infile,dir_parent,title,cond_filter,format_ColName)

#%%.   Evap
dir_parent = dir_PlotsOut
form_infile = 'Percent~AnnualChangeComp~E_%change~*.csv'
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~E_%change"
plotTSErrorMULTI_Percent(form_infile,dir_parent,title,cond_filter,format_ColName)

#%%.   Qtotal
dir_parent = dir_PlotsOut
form_infile = 'Percent~AnnualChangeComp~Qtotal_%change~*.csv'
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~Qtotal_%change"
plotTSErrorMULTI_Percent(form_infile,dir_parent,title,cond_filter,format_ColName)

dir_parent = dir_PlotsOut
form_infile = 'Percent~AnnualChangeComp~Qtotal_%change~*.csv'
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~Qtotal_%change - ylim100-300%"
plotTSErrorMULTI_Percent(form_infile,dir_parent,title,cond_filter,format_ColName)



#%%.   resVol[m3]
dir_parent = dir_PlotsOut
form_infile = 'Percent~AnnualChangeComp~resVol[m*.csv' # very strange glitch here when adding the 3 to the cond?
cond_filter = False
format_ColName = ''
title = "Percent~AnnualChangeComp~resVolume[m3]_%change"
plotTSErrorMULTI_Percent(form_infile,dir_parent,title,cond_filter,format_ColName)

# dir_parent = dir_PlotsOut
# form_infile = 'Percent~AnnualChangeComp~resVol[m*.csv' # very strange glitch here when adding the 3 to the cond?
# cond_filter = False
# format_ColName = ''
# title = "Percent~AnnualChangeComp~resVolume[m3]_%change - From 1990"
# plotTSErrorMULTI_Percent(form_infile,dir_parent,title,cond_filter,format_ColName)



# TODO: Some kind of exceedance/freqency plots on the over/under of the red 0% line?



# =============================================================================
# %% SS Code
# =============================================================================

