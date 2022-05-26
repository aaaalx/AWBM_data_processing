#%% Notes
#-----------------------------------------------------------------------------#
#         Downloading SILO gridded daily rainfall and evaporation data 
#-----------------------------------------------------------------------------#
#For example, the 2015 data for class A pan evaporation can be downloaded using curl as follows:
# curl "https://s3-ap-southeast-2.amazonaws.com/silo-open-data/annual/evap_pan/2015.evap_pan.nc" --remote-name

# https://s3-ap-southeast-2.amazonaws.com/silo-open-data/annual/index.html

# shape file to .nc mask 
# https://mygeoblog.com/2019/06/25/mask-netcdf-using-shp-file/


#https://s3-ap-southeast-2.amazonaws.com/silo-open-data/annual/index.html
#https://www.longpaddock.qld.gov.au/silo/gridded-data/
#https://s3-ap-southeast-2.amazonaws.com/silo-open-data/annual/<variable>/<year>.<variable>.nc



#%% Setup

# import numpy as np
# import netCDF4
import os
import time
import requests

# =============================================================================
# Define variables
# =============================================================================

dict_var = { # comment out the variables you don't want, add any others that are needed
    # 1: 'daily_rain'
    # ,2: 'et_morton_actual'
    # ,3: 'evap_morton_lake'
    # ,4: 'evap_pan'
    # ,5: 'monthly_rain'
    # ,6: 'radiation'
    1: 'et_morton_potential'
    }

number_of_var = len(dict_var) +1 # +1 for range()
# =============================================================================
# User inputs
# =============================================================================

time_start = 1900 # first year to download toa
time_end = 2021 # last year to download
url_start = 'https://s3-ap-southeast-2.amazonaws.com/silo-open-data/annual/'
save_directory = 'SILO_downloads/deltachange/' # the subdirectory for all files to write to
save_directory = r"C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data/SILO_downloads/deltachange//"


# =============================================================================
# %% Download loop
# =============================================================================
tic_script = time.time() # starts the timer
for var_number in range(1,number_of_var):
    # try: # Comment out "try" and "except" to bugfix
        for year in range(time_start,time_end+1):
            # try:                
# =============================================================================
#                 Generate filenames and URLS
# =============================================================================
                
                filename = (
                    str(year) 
                    +'.' 
                    + dict_var[var_number] 
                    + '.nc'
                    )
                    
                url = ( url_start 
                       + dict_var[var_number] + '/'
                       + filename
                       )
# =============================================================================
#                 Downloading
# =============================================================================

                
                print('... Trying download of ' + filename)
                if os.path.isfile(save_directory + filename) == False: #checks that the file doesn't exist already before starting to downloading
                    
                    tic_file = time.time()
                    print('... Download started')
                    r = requests.get(url, allow_redirects=True)   
                    print('Download complete for: ' + filename )
                    with open(save_directory + filename, 'xb') as save_nc: 
                        # 'xb' to only create (or continue download), 'wb' to ignore and overwrite existing files
                        save_nc.write(r.content)
                        
                    elapsed_file = time.time() - tic_file #calculates time to download file
                    elapsed_script_cum = time.time() - tic_script #calculates elapsed script time
                    
                   
                else:
                    raise # If the file exists, move to the "except:" code block, and skip to next file.
                    
                # print('Cumulative elapsed seconds: ' + str(round(elapsed_script_cum)))
                print('Cumulative elapsed minutes: ' + str(round(elapsed_script_cum)/60))
            
          
            
            # except:
                # print('Error, trying next year...')
    # except:
        # print('Error, trying next variable...')
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                