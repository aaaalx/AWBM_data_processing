#%% Notes
#https://www.longpaddock.qld.gov.au/silo/gridded-data/python/

# netCDF4 documentation
##http://unidata.github.io/netcdf4-python/
# Adapted from example:
## https://confluence.ecmwf.int/display/CKB/How+to+convert+NetCDF+to+CSV

#%% Adapting the test version to loop through all SILO (and TERN?) nc files

# =============================================================================
# Setup and user inputs
# =============================================================================
import cdsapi
    # in anaconda prompt:
        #  conda config --append channels conda-forge
        #  conda install cdsapi
import netCDF4
from netCDF4 import num2date
import numpy as np
import os
import pandas as pd
import time
import glob
tic = time.time() # starts the run time timer 

# dir_Data = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data/SILO_downloads/'
# dir_Data = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data/TERN_downloads/'
# dir_Data = 'C:/Users/alex.xynias/OneDrive - Water Technology Pty Ltd/UQ/Thesis/Data/SILO_downloads'
# dir_Data = 'C:/Users/alex.xynias/OneDrive - Water Technology Pty Ltd/UQ/Thesis/nc_clean/netCDF4_input/'
dir_Data = r"C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data/TERN_downloads//"
    # the location of the .nc data (also where output is written to)

# infile = '2000.in_var.nc'

infile_var = "tscr_ave" 
        #TERN
            #epan_ave
            #rnd24Adjust
            #rnd24AdjustAdjust
            # tscr_ave
        #SILO
            #daily_rain
            #et_morton_actual
    # this part isn't automated; rerun script N times and update this each time with ctrl-R and replace all
# infile_form = (dir_Data + "*"+ infile_var + ".nc") # for SILO data
infile_form = (dir_Data + infile_var + "*.nc") # for TERN data
infile_list = glob.glob(infile_form) # generates the list of files in dir_Data which match the infile_form criteria


# outfile = 'test_compile.csv' # name of compiled csv file to be written

extent_east = 151.6 # east most longitude value (decimal degrees)
extent_west = 153.0 # west most longitude value (decimal degrees)
extent_north = -26.4 # north most latitude value (decimal degrees)
extent_south = -27.4 # south most latitude value (decimal degrees)


for file_location in infile_list:
# =============================================================================
# # Locating and opening netCDF4 files
# =============================================================================
   

    f = netCDF4.Dataset(file_location)
    
    # =============================================================================
    # # Extract variable(s) and get dimensions
    # =============================================================================
    
    in_var = f.variables[infile_var]
        # array  (sheet,row,col) as (day,lat,long) 
        
    # Get dimensions assuming 3D: time, latitude, longitude
    time_dim, lat_dim, lon_dim = in_var.get_dims()
    time_var = f.variables[time_dim.name]
    times = num2date(time_var[:], time_var.units)       
    latitudes = f.variables[lat_dim.name][:]
    longitudes = f.variables[lon_dim.name][:]
    
    # trim down the lat and long area of interest:
        # 151.6 to 153 (left to right)
        # -26.4 to -27.4 (top to bottom)
        
    # Index the points in the lat/long arrays where the defined extents are
    index_east = np.where(longitudes == extent_east)[0][0] # [0][0] discards other info about the data structure and type
        # 792
    index_west = np.where(longitudes == extent_west)[0][0]+1 # +1 for each "maximum" index, similar rules to range() function perhaps?
        # 820
    index_north = np.where(latitudes == extent_north)[0][0]+1
        # 352
    index_south = np.where(latitudes == extent_south)[0][0]
        # 332
        
    # https://realpython.com/lessons/indexing-and-slicing/
    latitudes_trim = f.variables[lat_dim.name][index_south:index_north]
    longitudes_trim = f.variables[lon_dim.name][index_east:index_west]
    
    #https://www.pythonlikeyoumeanit.com/Module3_IntroducingNumpy/AccessingDataAlongMultipleDimensions.html
    in_var_trim = in_var[:,index_south:index_north,index_east:index_west]
        # goal: all sheets, lat:332 to 352, long:792 to 820
    
    # =============================================================================
    # Write data as a table with 4 columns: time, latitude, longitude, value
    # =============================================================================
    outfile_location =  (file_location[:-3]+ ".csv") # -3 because ".nc" is 3 characters
        
    times_grid, latitudes_grid, longitudes_grid = [x.flatten() for x in np.meshgrid(times, latitudes_trim, longitudes_trim, indexing='ij')]
    
    print(f'... building dataframe for {outfile_location}') 
    print(f'... between lon:{extent_east},{extent_west} and lat:{extent_north},{extent_south}')
    print(f'... saving to {dir_Data}')
    # input("Press Enter to continue...")
    
    # len(longitudes_grid)
    # len(latitudes_grid)
    # len(times_grid)
    
    
    print('Compiling dataframe ...')
      
    df = pd.DataFrame({
        'time': [t.isoformat() for t in times_grid],
        'latitude': latitudes_grid,
        'longitude': longitudes_grid,
        
        # 'in_var': in_var[:].flatten()}) # original line
        'tscr_ave.daily': in_var_trim[:].flatten()})
    df.to_csv(outfile_location, index=False)
        # TODO: fix that strange rounding error in the lat/long variables that I've seen when saving to csv before
    elapsed_time = time.time() - tic
    
    print(f'Completed! Elapsed seconds: {round(elapsed_time,3)}')
    
    
# =============================================================================
# TODO: Process the above 4 column table into separate csv per grid point?
# =============================================================================

    # Compile each year's csv into one dataframe (or file if too large, seems like 700mb)
    
    
    # rearrange the compiled csv into separate files (time,rain,evap) at each grid location 
















