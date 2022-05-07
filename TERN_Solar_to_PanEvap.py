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

