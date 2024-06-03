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
from unidecode import unidecode
#import torch # pytorch and tensorflow are both very powerful deep learning libraries for more advanced machine learning models
#import tensorflow as tf # they currently do not work with the latest Python version however

#%% read in data and create a pandas dataframe
# don't forget escape character "\" in file paths

username = os.getlogin() # get your active username
share_path = fr"C:\Users\{username}\\" # insert your username in the file path

path = fr"C:\Users\{username}\PNNL\NEB Decarb - General\Datasets\ResStock\2024.1" #os.getcwd() # this will get your current active folder, or you can type it directly with r"C:\path\to\folder\etc\\"
file = r"baseline_metadata_and_annual_results.parquet" # if you set your current folder to the directory where the file is located (in the top right of Spyder) then all you need is the file name
filepath = os.path.join(path, file) # add the file to the folder path
df0 = pd.read_parquet(filepath) # read the file at the speicifed filepath into a pandas dataframe

file1 = r"upgrade2.01_metadata_and_annual_results.parquet" # if you set your current folder to the directory where the file is located (in the top right of Spyder) then all you need is the file name
filepath1 = os.path.join(path, file1) # add the file to the folder path
df1 = pd.read_parquet(filepath1) 

file2 = r"upgrade2.02_metadata_and_annual_results.parquet" # if you set your current folder to the directory where the file is located (in the top right of Spyder) then all you need is the file name
filepath2 = os.path.join(path, file2) # add the file to the folder path
df2 = pd.read_parquet(filepath2) 

file3 = r"upgrade2.03_metadata_and_annual_results.parquet" # if you set your current folder to the directory where the file is located (in the top right of Spyder) then all you need is the file name
filepath3 = os.path.join(path, file3) # add the file to the folder path
df3 = pd.read_parquet(filepath3) 

file4 = r"upgrade2.04_metadata_and_annual_results.parquet" # if you set your current folder to the directory where the file is located (in the top right of Spyder) then all you need is the file name
filepath4 = os.path.join(path, file4) # add the file to the folder path
df4 = pd.read_parquet(filepath4) 

file5 = r"upgrade2.05_metadata_and_annual_results.parquet" # if you set your current folder to the directory where the file is located (in the top right of Spyder) then all you need is the file name
filepath5 = os.path.join(path, file5) # add the file to the folder path
df5 = pd.read_parquet(filepath5) 

#Now get the info you need from each
for column in df0.columns:
    print(column)


# Creating a new DataFrame with the selected columns
#df0_new = pd.DataFrame(df0.loc[:, "bldg_id":"upgrade"].join(df0.loc[:, "out.emissions.all_fuels.lrmer_high_re_cost_2030_boxavg.co2e_kg":"out.emissions.all_fuels.lrmer_mid_case_2030_boxavg.co2e_kg"]))

df0 = df0[['upgrade', 'in.sqft', 'in.ashrae_iecc_climate_zone_2004', 'weight', 'in.duct_leakage_and_insulation', 'in.insulation_wall', 'in.windows', 'in.county']]
df1 = df1[['upgrade', 'in.sqft', 'in.ashrae_iecc_climate_zone_2004', 'weight', 'in.windows', 'in.county']]
df2 = df2[['upgrade', 'in.sqft', 'in.ashrae_iecc_climate_zone_2004', 'weight', 'in.windows', 'in.county']]
df3 = df3[['upgrade', 'in.sqft', 'in.ashrae_iecc_climate_zone_2004', 'weight', 'in.duct_leakage_and_insulation', 'in.insulation_wall', 'in.county']]
df4 = df4[['upgrade', 'in.sqft', 'in.ashrae_iecc_climate_zone_2004', 'weight', 'in.duct_leakage_and_insulation', 'in.insulation_wall', 'in.county']]
df5 = df5[['upgrade', 'in.sqft', 'in.ashrae_iecc_climate_zone_2004', 'weight', 'in.duct_leakage_and_insulation', 'in.insulation_wall', 'in.county']]

data_ins = {
    'in.insulation_wall_match': [
        'Brick, 12-in, 3-wythe, R-11', 'Brick, 12-in, 3-wythe, R-15', 'Brick, 12-in, 3-wythe, R-19', 
        'Brick, 12-in, 3-wythe, R-7', 'Brick, 12-in, 3-wythe, Uninsulated', 'CMU, 6-in Hollow, R-11', 
        'CMU, 6-in Hollow, R-15', 'CMU, 6-in Hollow, R-19', 'CMU, 6-in Hollow, R-7', 
        'CMU, 6-in Hollow, Uninsulated', 'Wood Stud, R-11', 'Wood Stud, R-15', 'Wood Stud, R-19', 
        'Wood Stud, R-7', 'Wood Stud, Uninsulated'
    ],
    'STC': [
        58, 60, 62, 56, 54, 49, 51, 53, 47, 45, 41, 43, 45, 39, 37
    ]
}

# Create the dataframe
df_ins = pd.DataFrame(data_ins)


data_leakage = {
    'in.duct_leakage_and_insulation_match': [
        '0% Leakage, Uninsulated', '10% Leakage, R-4', '10% Leakage, R-6', 
        '10% Leakage, R-8', '10% Leakage, Uninsulated', '20% Leakage, R-4', 
        '20% Leakage, R-6', '20% Leakage, R-8', '20% Leakage, Uninsulated', 
        '30% Leakage, R-4', '30% Leakage, R-6', '30% Leakage, R-8', '30% Leakage, Uninsulated'
    ],
    'STC Delta': [
        0, -1, -1, -1, -1, -2, -2, -2, -2, -3, -3, -3, -3
    ]
}

# Create the dataframe
df_leakage = pd.DataFrame(data_leakage)



data_ach = {
    'in.infiltration_match': [
        '1 ACH50', '2 ACH50','3 ACH50','4 ACH50','5 ACH50','6 ACH50','7 ACH50',
        '8 ACH50','10 ACH50','15 ACH50','20 ACH50','25 ACH50','30 ACH50','40 ACH50','50 ACH50'
    ],
    'STC Delta': [
        1, 0.5, 0.5, 0.5, 0.5, 0, 0, 0, -0.5, -1, -2, -2.5, -3.5, -4.5, -6
    ]
}

# Create the dataframe
df_ach = pd.DataFrame(data_ach)




data_windows = {
    'in.windows_match': [
        'Double, Clear, Metal, Air', 'Double, Clear, Metal, Air, Exterior Clear Storm', 
        'Double, Clear, Non-metal, Air', 'Double, Clear, Non-metal, Air, Exterior Clear Storm', 
        'Double, Low-E, Non-metal, Air, M-Gain', 'Single, Clear, Metal', 
        'Single, Clear, Metal, Exterior Clear Storm', 'Single, Clear, Non-metal', 
        'Single, Clear, Non-metal, Exterior Clear Storm', 'Triple, Low-E, Non-metal, Air, L-Gain'
    ],
    'STC': [
        33, 36, 33, 36, 33, 27, 29, 27, 29, 37
    ]
}

# Create the dataframe
df_windows = pd.DataFrame(data_windows)


###########Window Upgrade Calcs - 2.01 (thin triple) ###
df1['in.windows_upgrade'] = 'Triple, Low-E, Non-metal, Air, L-Gain'
# Add the STC column to df0
df0 = df0.merge(df_windows[['in.windows_match', 'STC']], how='left', left_on='in.windows', right_on='in.windows_match').drop(columns='in.windows_match')
# Add the STC column to df1
df1 = df1.merge(df_windows[['in.windows_match', 'STC']], how='left', left_on='in.windows_upgrade', right_on='in.windows_match').drop(columns='in.windows_match')

df1['STC_diff'] = df1['STC'] - df0['STC']
df1['STC_diff'].mean()
df1['STC_new'] = df1['STC']+df1['STC_diff']
#avg_stc_by_cz = df1.groupby('in.ashrae_iecc_climate_zone_2004')['STC_new'].mean().reset_index()
avg_stc_by_cz = df1.groupby('in.ashrae_iecc_climate_zone_2004').agg({'STC': 'mean', 'STC_diff': 'mean', 'STC_new': 'mean'}).reset_index()

# Rename the columns for clarity
avg_stc_by_cz.columns = ['Climate Zone', 'Average STC', 'Average STC_diff', 'Average STC_new']
print(avg_stc_by_cz)




###no new STC column because it's based on the infiltration percentage differences 
# Function to determine the value of STC_new
def calculate_stc_new(row):
    if 'single' in row['in.windows']:
        return row['STC'] + 4
    elif 'double' in row['in.windows']:
        return row['STC'] + 2
    else:
        return row['STC']


df2['STC_new'] = df0.apply(calculate_stc_new, axis=1)

df2['STC_diff'] = df2['STC_new'] - df0['STC']
df2['STC_diff'].mean()



#Meausre package 2.03 light touch- no STC delta based on assumptions/definition
#Measure package 2.04 
# Duct sealing
#o 10% Leakage, R-8
# Applies to all dwelling units with leakier and/or less-insulated ducts located in
#unconditioned space
#• Drill-and-fill wall insulation
#o R-13 insulation with wood stud walls
# Applies to dwelling units with uninsulated wood stud walls



