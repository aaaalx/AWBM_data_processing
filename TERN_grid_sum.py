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

