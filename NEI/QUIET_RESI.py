# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 16:19:23 2025

@author: mcco689
"""

#QUIET_RESI Quantitative Investigation and Evaluation Tool for Residential Envelope Sound Isolation

import os # built-in functions for working with the Windows system
from datetime import datetime as dt # library for getting and working with dates and time
from glob import glob # useful module for pattern matching and batch operations
import pandas as pd # most popular data science library for working with panel/tabular data
import numpy as np # most popular computational library, used in the backend of pandas
import scipy as sp # for more complex computational operations
import statsmodels.api as sm # for more advanced statistical testing
import matplotlib.pyplot as plt # popular plotting library
import seaborn as sns # wrapper for matplotlib to make plotting much easier
import pyarrow as pa #use if needed: pip install pyarrow
import fastparquet as fp 
import math
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
df0.all = pd.read_parquet(filepath) # read the file at the specified filepath into a pandas dataframe
df0 = df0.all

#assign window to wall ratio numerically, extracting from parameter in ResStock
df0['A_win.pre'] = df0['in.window_areas']
df0['A_win'] = df0['A_win.pre'].str.extract(r'F(\d+)')[0].astype(float) / 100
df0['A_wal'] = 1-df0['A_win']
df0['A_tot'] = 1


#check on which scenarios are most likely
df0['in.window_areas'].value_counts()
df0['in.windows'].value_counts()
df0['in.geometry_wall_exterior_finish'].value_counts()
df0['in.geometry_wall_type'].value_counts()
df0['in.insulation_wall'].value_counts()

#import TL values from spreadsheet TL_database from NEB Decarb - Conferences - Buildings XVI - Data and Analysis #NEED

#extrapolate down to get 100 and 80 Hz (linear)



# #assign TL values based on spreadsheet, use placeholders for now to set up calcs
# df0['TL_win_125']  = 30  #to be dynamically assigned within the master dataframe based on the decided methodology 
# df0['TL_win_160']  = 30   
# df0['TL_win_200']  = 30   
# df0['TL_win_250']  = 30   
# df0['TL_win_315']  = 30   
# df0['TL_win_100']  = 30   
# df0['TL_win_400']  = 30   
# df0['TL_win_500']  = 30   
# df0['TL_win_630']  = 30   
# df0['TL_win_800']  = 30   
# df0['TL_win_1000'] = 30       
# df0['TL_win_1250'] = 30      
# df0['TL_win_1600'] = 30       
# df0['TL_win_2000'] = 30       
# df0['TL_win_2500'] = 30       
# df0['TL_win_3150'] = 30      
# df0['TL_win_4000'] = 30       
# df0['TL_win_5000'] = 30  


# df0['TL_wal_125']  = 30   
# df0['TL_wal_160']  = 30   
# df0['TL_wal_200']  = 30   
# df0['TL_wal_250']  = 30   
# df0['TL_wal_315']  = 30   
# df0['TL_wal_100']  = 30   
# df0['TL_wal_400']  = 30   
# df0['TL_wal_500']  = 30   
# df0['TL_wal_630']  = 30   
# df0['TL_wal_800']  = 30   
# df0['TL_wal_1000'] = 30       
# df0['TL_wal_1250'] = 30      
# df0['TL_wal_1600'] = 30       
# df0['TL_wal_2000'] = 30       
# df0['TL_wal_2500'] = 30       
# df0['TL_wal_3150'] = 30      
# df0['TL_wal_4000'] = 30       
# df0['TL_wal_5000'] = 30   

# #calculate TL of whole assembly based on weighted average based on wwr
# #TL_tot = 10*log((A_win*10^(-TL_win/10)+A_wal*10^(-TL_wal/10))/A_tot)

# df0['TL_tot_100'] = 10*math.log10((df0['A_win']*10**(-df0['TL_win_100']/10)+df0['A_wal']*10**(-df0['TL_wal_100']/10))/df0['A_tot'])
# df0['TL_tot_125'] = 10*math.log10((df0['A_win']*10**(-df0['TL_win_125']/10)+df0['A_wal']*10**(-df0['TL_wal_125']/10))/df0['A_tot'])
# df0['TL_tot_160'] = 10*math.log10((df0['A_win']*10**(-df0['TL_win_160']/10)+df0['A_wal']*10**(-df0['TL_wal_160']/10))/df0['A_tot'])
# df0['TL_tot_200'] = 10*math.log10((df0['A_win']*10**(-df0['TL_win_200']/10)+df0['A_wal']*10**(-df0['TL_wal_200']/10))/df0['A_tot'])
# df0['TL_tot_250'] = 10*math.log10((df0['A_win']*10**(-df0['TL_win_250']/10)+df0['A_wal']*10**(-df0['TL_wal_250']/10))/df0['A_tot'])
# df0['TL_tot_315'] = 10*math.log10((df0['A_win']*10**(-df0['TL_win_315']/10)+df0['A_wal']*10**(-df0['TL_wal_315']/10))/df0['A_tot'])
# df0['TL_tot_400'] = 10*math.log10((df0['A_win']*10**(-df0['TL_win_400']/10)+df0['A_wal']*10**(-df0['TL_wal_400']/10))/df0['A_tot'])
# df0['TL_tot_500'] = 10*math.log10((df0['A_win']*10**(-df0['TL_win_500']/10)+df0['A_wal']*10**(-df0['TL_wal_500']/10))/df0['A_tot'])
# df0['TL_tot_630'] = 10*math.log10((df0['A_win']*10**(-df0['TL_win_630']/10)+df0['A_wal']*10**(-df0['TL_wal_630']/10))/df0['A_tot'])
# df0['TL_tot_800'] = 10*math.log10((df0['A_win']*10**(-df0['TL_win_800']/10)+df0['A_wal']*10**(-df0['TL_wal_800']/10))/df0['A_tot'])
# df0['TL_tot_1000']  = 10*math.log10((df0['A_win']*10**(-df0['TL_win_1000']/10)+df0['A_wal']*10**(-df0['TL_wal_1000']/10))/df0['A_tot'])
# df0['TL_tot_1250']  = 10*math.log10((df0['A_win']*10**(-df0['TL_win_1250']/10)+df0['A_wal']*10**(-df0['TL_wal_1250']/10))/df0['A_tot'])
# df0['TL_tot_1600']  = 10*math.log10((df0['A_win']*10**(-df0['TL_win_1600']/10)+df0['A_wal']*10**(-df0['TL_wal_1600']/10))/df0['A_tot'])
# df0['TL_tot_2000']  = 10*math.log10((df0['A_win']*10**(-df0['TL_win_2000']/10)+df0['A_wal']*10**(-df0['TL_wal_2000']/10))/df0['A_tot'])
# df0['TL_tot_2500']  = 10*math.log10((df0['A_win']*10**(-df0['TL_win_2500']/10)+df0['A_wal']*10**(-df0['TL_wal_2500']/10))/df0['A_tot'])
# df0['TL_tot_3150']  = 10*math.log10((df0['A_win']*10**(-df0['TL_win_3150']/10)+df0['A_wal']*10**(-df0['TL_wal_3150']/10))/df0['A_tot'])
# df0['TL_tot_4000']  = 10*math.log10((df0['A_win']*10**(-df0['TL_win_4000']/10)+df0['A_wal']*10**(-df0['TL_wal_4000']/10))/df0['A_tot'])
# df0['TL_tot_5000']  = 10*math.log10((df0['A_win']*10**(-df0['TL_win_5000']/10)+df0['A_wal']*10**(-df0['TL_wal_5000']/10))/df0['A_tot'])

# replacement for above
# Assign TL values based on spreadsheet, using placeholders for now
tl_frequencies = [
    100, 125, 160, 200, 250, 315, 400, 500, 630, 800,
    1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000
]

# Set TL values for windows and walls
for freq in tl_frequencies:
    df0[f'TL_win_{freq}'] = 30
    df0[f'TL_wal_{freq}'] = 30

# Calculate TL of the whole assembly using weighted average
for freq in tl_frequencies:
    df0[f'TL_tot_{freq}'] = 10 * math.log10(
        (df0['A_win'] * 10**(-df0[f'TL_win_{freq}'] / 10) +
         df0['A_wal'] * 10**(-df0[f'TL_wal_{freq}'] / 10)) / df0['A_tot']
    )

# interpolate values in TL_database
# Select only the relevant columns for interpolation
cols_to_interpolate = [50, 63, 80, 100, 125, 250]
df_subset = df_TL[cols_to_interpolate].T  # Transpose for row-wise interpolation

# Perform linear interpolation
df_interpolated = df_subset.interpolate(method='linear', axis=0, limit_direction='both')

# Keep existing values from original DataFrame
df_TL[cols_to_interpolate] = df_interpolated.T.where(df_TL[cols_to_interpolate].isna(), df_TL[cols_to_interpolate])

#in.geometry_wall_exterior_finish
#in.geometry_wall_type
#in.insulation_wall



