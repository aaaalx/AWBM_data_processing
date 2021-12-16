# -*- coding: utf-8 -*-
"""
Created on Thu Dec 16 15:42:06 2021

@author: https://medium.com/casual-inference/the-most-time-efficient-ways-to-import-csv-data-in-python-cc159b44063d
"""

import pandas as pd
import time
import csv
# import paratext
import dask.dataframe

input_file = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data/SILO_downloads/Compile/SILO-1985-2020.csv'
 
# start_time = time.time()
# data = csv.DictReader(open(input_file))
# print("csv.DictReader took %s seconds" % (time.time() - start_time))
# input("Press Enter to continue with script...")
start_time = time.time()
data = pd.read_csv(input_file)
print("pd.read_csv took %s seconds" % (time.time() - start_time))
# input("Press Enter to continue with script...")

# start_time = time.time()
# data = pd.read_csv(input_file, chunksize=100000)
# print("pd.read_csv with chunksize took %s seconds" % (time.time() - start_time))
# # input("Press Enter to continue with script...")
# start_time = time.time()
# data = dask.dataframe.read_csv(input_file)
# print("dask.dataframe took %s seconds" % (time.time() - start_time))