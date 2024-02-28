# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 20:45:14 2024

@author: mcco689
"""

#%% import useful libraries into a Python scrypt with import. You can use an alias with "as" so you don't have to
# keep writing the full name of the library. Use "from" to import just the specific functions or methods you want
# from a library, this can save on run time.

import os # built-in functions for working with the Windows system
from datetime import datetime as dt # library for getting and working with dates and time
from glob import glob # useful module for pattern matching and batch operations
import pandas as pd # most popular data science library for working with panel/tabular data
import numpy as np # most popular computational library, used in the backend of pandas
import scipy as sp # for more complex computational operations
import statsmodels.api as sm # for more advanced statistical testing
import matplotlib.pyplot as plt # popular plotting library
import seaborn as sns # wrapper for matplotlib to make plotting much easier
from sklearn import linear_model # scikit-learn is a very useful machine learning library with many models built in
#import torch # pytorch and tensorflow are both very powerful deep learning libraries for more advanced machine learning models
#import tensorflow as tf # they currently do not work with the latest Python version however

#%% read in data and create a pandas dataframe
# don't forget escape character "\" in file paths

username = os.getlogin() # get your active username
share_path = fr"C:\Users\{username}\\" # insert your username in the file path

path = fr"C:\Users\{username}\PNNL\NEB Decarb - General\Datasets\ResStock" #os.getcwd() # this will get your current active folder, or you can type it directly with r"C:\path\to\folder\etc\\"
file = r"baseline_metadata_and_annual_results.csv" # if you set your current folder to the directory where the file is located (in the top right of Spyder) then all you need is the file name
filepath = os.path.join(path, file) # add the file to the folder path
df0 = pd.read_csv(filepath) # read the file at the speicifed filepath into a pandas dataframe

file1 = r"upgrade01_metadata_and_annual_results.csv" # if you set your current folder to the directory where the file is located (in the top right of Spyder) then all you need is the file name
filepath1 = os.path.join(path, file1) # add the file to the folder path
df1 = pd.read_csv(filepath1) 

file2 = r"upgrade02_metadata_and_annual_results.csv" # if you set your current folder to the directory where the file is located (in the top right of Spyder) then all you need is the file name
filepath2 = os.path.join(path, file2) # add the file to the folder path
df2 = pd.read_csv(filepath2) 

file3 = r"upgrade03_metadata_and_annual_results.csv" # if you set your current folder to the directory where the file is located (in the top right of Spyder) then all you need is the file name
filepath3 = os.path.join(path, file3) # add the file to the folder path
df3 = pd.read_csv(filepath3) 

file4 = r"upgrade04_metadata_and_annual_results.csv" # if you set your current folder to the directory where the file is located (in the top right of Spyder) then all you need is the file name
filepath4 = os.path.join(path, file4) # add the file to the folder path
df4 = pd.read_csv(filepath4) 

file5 = r"upgrade05_metadata_and_annual_results.csv" # if you set your current folder to the directory where the file is located (in the top right of Spyder) then all you need is the file name
filepath5 = os.path.join(path, file5) # add the file to the folder path
df5 = pd.read_csv(filepath5) 

file6 = r"upgrade06_metadata_and_annual_results.csv" # if you set your current folder to the directory where the file is located (in the top right of Spyder) then all you need is the file name
filepath6 = os.path.join(path, file6) # add the file to the folder path
df6 = pd.read_csv(filepath6) 

file7 = r"upgrade07_metadata_and_annual_results.csv" # if you set your current folder to the directory where the file is located (in the top right of Spyder) then all you need is the file name
filepath7 = os.path.join(path, file7) # add the file to the folder path
df7 = pd.read_csv(filepath7) 

file8 = r"upgrade08_metadata_and_annual_results.csv" # if you set your current folder to the directory where the file is located (in the top right of Spyder) then all you need is the file name
filepath8 = os.path.join(path, file8) # add the file to the folder path
df8 = pd.read_csv(filepath8) 

file9 = r"upgrade09_metadata_and_annual_results.csv" # if you set your current folder to the directory where the file is located (in the top right of Spyder) then all you need is the file name
filepath9 = os.path.join(path, file9) # add the file to the folder path
df9 = pd.read_csv(filepath9) 

file10 = r"upgrade10_metadata_and_annual_results.csv" # if you set your current folder to the directory where the file is located (in the top right of Spyder) then all you need is the file name
filepath10 = os.path.join(path, file10) # add the file to the folder path
df10 = pd.read_csv(filepath10) 


#Now get the info you need from each
for column in df0.columns:
    print(column)


# Creating a new DataFrame with the selected columns
df0_new = pd.DataFrame(df0.loc[:, "bldg_id":"upgrade"].join(df0.loc[:, "out.site_energy.net.energy_consumption.kwh":"out.emissions.all_fuels.lrmer_mid_case_15_2025_start.co2e_kg"]))
df1_new = pd.DataFrame(df1.loc[:, "bldg_id":"upgrade"].join(df1.loc[:, "out.site_energy.net.energy_consumption.kwh":"out.emissions.all_fuels.lrmer_mid_case_15_2025_start.co2e_kg"]))


df_diff = df1_new - df0_new
df_metadata = df0[['bldg_id', 'in.sqft', 'weight', 'in.ashrae_iecc_climate_zone_2004', 'in.census_division', 'in.census_region', 'in.county']]

df_full = pd.concat([df_metadata,df_diff], axis=1)













