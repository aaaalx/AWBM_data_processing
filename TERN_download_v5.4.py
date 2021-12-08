# =============================================================================
# Notes 
# =============================================================================
# #   Downloads all daily CMIP5 data from TERN for defined:
  #      Geographic extent, 
  #      Start year,
  #      RCPs,
  #      & Variables
  
# https://www.tutorialspoint.com/downloading-files-from-web-using-python
# https://stackoverflow.com/questions/19602931/basic-http-file-downloading-and-saving-to-disk-in-python


# Info on the models & data : 
        # https://www.longpaddock.qld.gov.au/qld-future-climate/understand-data/
        # https://dap.tern.org.au/thredds/fileServer/CMIP5QLD/Queensland_FutureClimate_Data_Availability.pdf
# example url = 
    # https://dap.tern.org.au/thredds/ncss/CMIP5QLD/CMIP5_Downscaled_CCAM_QLD10/RCP45/daily/Precipitation/rnd24.daily.ccam10_CSIRO-Mk3-6-0Q_rcp45.nc?var=rnd24&north=-26&west=152&east=153&south=-27&disableProjSubset=on&horizStride=1&time_start=1990-01-01T15%3A00%3A00Z&time_end=2099-12-31T15%3A00%3A00Z&timeStride=1

# TODO: Downloading the files at once rather than sequenced?
    # exporting all url strings to file is good enough to use in another d/l mgmt program if needed.

# =============================================================================
#%%                                  Setup 
# =============================================================================
import requests
import time
import os.path

tic_script = time.time() # starts the timer

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

dict_var_name = {
    1: 'Precipitation'
    ,2: 'PanEvaporation'
    ,3: 'Precipitation'
    # ,4: 'MeanTemperature'
    }

dict_timestep = { # defines the string TERN uses to organise results by timestep
    1: 'daily'
    ,2: 'daily'
    ,3: 'daily_adjusted'
    # ,4: 'daily'    
    }

dict_filenamefiller = { # defines another part [grid type?] of the filename and url that changes with variable
    1: '.daily.ccam10_'
    ,2: '.daily.ccam10_'
    ,3: '.daily.ccam10-awap_' #for the bias corrected data,  "-awap" is added for "Australian Water Availability Project"
    # ,4: '.daily.ccam10_'
    }

dict_rcp = {
    1: 'rcp45',
    2: 'rcp85'    
    }

dict_RCP = {
    1: 'RCP45',
    2: 'RCP85'    
    }

number_of_models = len(dict_model) + 1 # +1 because of how range() works
number_of_var = len(dict_var) + 1
number_of_rcp = len(dict_rcp) + 1

# =============================================================================
#%% User Input Parameters                 
# =============================================================================
url_north='-26' # lat/long model extents, use $x and $y in QGIS field calculator to find
url_west='151'
url_east='153'
url_south='-28' 
url_year ='1985' # first year to download data from, >1980

save_directory = 'TERN_downloads/' # the subdirectory for all files to write to

# =============================================================================
#%%                  Create url string from parameters
# =============================================================================
with open(save_directory + 'url_log.txt', 'a') as log:
    log.write('Coords (N,S,E,W): ' + url_north + ',' + url_south + ',' + url_east + ',' + url_west +',-----------,' + time.ctime() + '\n')

for var_number in range(1,number_of_var): # loops through all defined variables
    try:
        for rcp_number in range(1,number_of_rcp): # loops through the  RCPs
            try:
                for model_number in range(1, number_of_models): # loops through all models
                    try:
       
                        print('\n'+'... Creating url for ' + dict_var[var_number] + ' from: ' + dict_model[model_number])
                        print('......Var   : ' + str(var_number) + ' of ' + str(number_of_var-1))
                        print('......RCP   : ' + str(rcp_number) + ' of ' + str(number_of_rcp-1))   
                        print('......Model : ' + str(model_number) + ' of ' + str(number_of_models-1)+ '\n')     
                        # Input constants:        
                        url_RCP = dict_RCP[rcp_number] # RCP45 or RCP85
                        url_rcp = dict_rcp[rcp_number] # rcp45 or rcp85
                        url_model = dict_model[model_number]  
                        url_var = dict_var[var_number]    
                        url_time_start = url_year + '-01-01T15%3A00%3A00Z&'
                        url_time_end = '2099-12-31T15%3A00%3A00Z&'
                        filename = url_var + dict_filenamefiller[var_number] + url_model +'_' + url_rcp + '.nc'
                        url_timestep = dict_timestep[var_number]
                        
                        url = (
                               'https://dap.tern.org.au/thredds/ncss/CMIP5QLD/CMIP5_Downscaled_CCAM_QLD10/' 
                               + url_RCP
                               + '/' + url_timestep + '/' 
                               + dict_var_name[var_number] + '/'
                               + filename       
                               + '?var=' + url_var + '&'
                               + 'north=' + url_north + '&'
                               + 'west=' + url_west + '&'
                               + 'east=' + url_east + '&'
                               + 'south=' + url_south + '&'
                               + 'disableProjSubset=on&horizStride=1&' # not sure what this part does
                               + 'time_start=' + url_time_start 
                               + 'time_end=' + url_time_end
                               + 'timeStride=1' # or this part
                               )
                
                        
# =============================================================================
# %%               Download & Save files (request version)
# =============================================================================
                        print('... Attempting download:  ' + filename +' from url: ' + url + '\n')
                       
                        
                    
                        if os.path.isfile(save_directory + filename) == False: #checks that the file doesn't exist already before starting to downloading
                            print('... Download started')
                            tic_file = time.time()
                            r = requests.get(url, allow_redirects=True)   
                            
                            with open(save_directory + filename, 'xb') as save_nc: 
                                # 'xb' to only create (or continue download), 'wb' to ignore and overwrite existing files
                                save_nc.write(r.content)
                                
                            elapsed_file = time.time() - tic_file #calculates time to download file
                            elapsed_script_cum = time.time() - tic_script #calculates elapsed script time
                            
                            print('Download complete for: ' + filename + '\n' + 'time: ' + str(elapsed_file))
                        else:
                            print('Matching file exists...')
                            raise # If the file exists, move to the "except:" code block, and skip to next file.
                            
                        # print('Cumulative elapsed seconds: ' + str(round(elapsed_script_cum)))
                        print('Cumulative elapsed minutes: ' + str(round(elapsed_script_cum)/60))
                        
# =============================================================================
# %% Export .nc url list to log file
# =============================================================================
                
                        with open(save_directory + 'url_log.txt', 'a') as log: #appends the url generated to file
                            log.write(url)
                            log.write('\n')
                                                       
                            
                    except:
                        print('Error; Download skipped, attempting next model...')
                        continue
                        
            except:
                print('Error; Download skipped, attempting next RCP...')
                continue                 
    except:
        print('Error; Download skipped, attempting next var...')
        continue

elapsed_script = round((time.time() - tic_script),5)
print('....Script ended; total time: ' + str(elapsed_script) + ' [s]' )