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
import random
#import torch # pytorch and tensorflow are both very powerful deep learning libraries for more advanced machine learning models
#import tensorflow as tf # they currently do not work with the latest Python version however

#%% read in data and create a pandas dataframe
# don't forget escape character "\" in file paths

username = os.getlogin() # get your active username
share_path = fr"C:\Users\{username}\\" # insert your username in the file path

path = fr"C:\Users\{username}\PNNL\NEB Decarb - General\Datasets\ResStock\2024.1" #os.getcwd() # this will get your current active folder, or you can type it directly with r"C:\path\to\folder\etc\\"
#path = "/Users/rose775/Library/CloudStorage/OneDrive-PNNL/General - NEB Decarb/Datasets/ResStock/2024.1/"


file = r"baseline_metadata_and_annual_results.parquet" # if you set your current folder to the directory where the file is located (in the top right of Spyder) then all you need is the file name
filepath = os.path.join(path, file) # add the file to the folder path
df0 = pd.read_parquet(filepath) # read the file at the specified filepath into a pandas dataframeb

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
#df_TL = pd.read_excel("/Users/rose775/Library/CloudStorage/OneDrive-PNNL/General - NEB Decarb/Conferences/Buildings XVI/Data and Analysis/TL_database.xlsx")
#df_traffic = pd.read_excel("/Users/rose775/Library/CloudStorage/OneDrive-PNNL/General - NEB Decarb/Conferences/Buildings XVI/Data and Analysis/traffic_spectrum.xlsx")
#df_oitc = pd.read_excel("/Users/rose775/Library/CloudStorage/OneDrive-PNNL/General - NEB Decarb/Conferences/Buildings XVI/Data and Analysis/Transmission Loss Coefficients.xlsx", sheet_name="OITC_plain")

#Kieren Filepath Below:
df_TL = pd.read_excel("C:/Users/mcco689/PNNL/NEB Decarb - General/Conferences/Buildings XVI/Data and Analysis/TL_database.xlsx")
df_traffic = pd.read_excel("C:/Users/mcco689/PNNL/NEB Decarb - General/Conferences/Buildings XVI/Data and Analysis/traffic_spectrum.xlsx")
df_oitc = pd.read_excel("C:/Users/mcco689/PNNL/NEB Decarb - General/Conferences/Buildings XVI/Data and Analysis/Transmission Loss Coefficients.xlsx", sheet_name="OITC_plain")



# NOT WORKING
# interpolating TL values
# define frequency values
freqs = {
    "f50": 50, "f63": 63, "f80": 80, "f100": 100, "f125": 125,
    "f160": 160, "f200": 200, "f250": 250, "f315": 315
}

# column groups
cols_interp = ["f50", "f63", "f80"]  # columns to interpolate
cols_known = ["f100", "f125", "f160", "f200", "f250", "f315"]  # reference columns

for idx, row in df_TL.iterrows():
    available_cols = [col for col in cols_known if not pd.isna(row[col])]

    if len(available_cols) < 2:  # Need at least two points for interpolation
        continue

    # corresponding frequencies and values
    known_freqs = np.array([freqs[col] for col in available_cols])  # maybe change to log scale
    known_values = row[available_cols].astype(float).values

    # Interpolate in linear space
    for col in cols_interp:
        if pd.isna(row[col]):  # Only fill missing values
            interp_value = np.interp(freqs[col], known_freqs, known_values)
            df_TL.at[idx, col] = interp_value


print("break")


##function for getting the TL rows that we will use for each entry in ResStock
def get_matching_TL(df, basic_category, secondary_category=None):
    """Fetch a random row based on the Basic_Category and optional Secondary_Category,
       returning the 'f' columns as a Series if a match is found, otherwise None."""
    
    if secondary_category:
        filtered_df = df[
            df["ResStock_match"].str.contains(basic_category, na=False) & 
            df["ResStock_match_out"].str.contains(secondary_category, na=False)
        ]
    else:
        filtered_df = df[df["ResStock_match"].str.contains(basic_category, na=False)]
    
    if not filtered_df.empty:
        random_row = filtered_df.sample(n=1)
        f_columns = [col for col in random_row.columns if col.startswith("f") and "80" <= col[1:] <= "4000"] #added indices for beginning and ending columns of interest
        return random_row[f_columns].squeeze()
    else:
        return None

# Method to calculate OITC
# for row, index in df0.iterrows():
#     A_win = df0.loc[row, 'A_win']
#     A_wal = df0.loc[row, 'A_wal']
#     A_tot = df0.loc[row, 'A_tot']
#     win = df0.loc[row, 'in.windows']
#     wall_in = df0.loc[row, 'in.insulation_wall']
#     wall_out = df0.loc[row, 'in.geometry_wall_exterior']

# match the value in wall_in, wall_out to a row in df_TL using df_TL["Basic_Category"] for wall_in and df_TL["Secondary_Category"] for wall_out, which gives us our  wall F values for
# that resstock row. return series of f values named TL_wall

# match the value in win to a row in df_TL["Basic_Category"] , which gives us our  window F values for that resstock row. return series of f values named TL_win

# TL_ass = 10 * np.log10((A_win * 10 ** (-TL_win / 10) + A_wal * 10**(-TL_wal / 10)) / A_tot) # this is a series, equation computed for each value in TL_win/TL_wall series, inxed position across two series is the same
# if possible, replace rss with NTNM data by county match with spectral curve from traffic_spectrum.xlsx
# indoor_noise_curve = df_oitc["sum_bcf_rss"] - TL_ass

# indoor_level = 10 * np.log10(sum(10**((indoor_noise_curve))))
# outdoor_level = 10 * np.log10(sum(10**((df_oitc["sum_bcf_rss"]))))

# df0["oitc"] = outdoor_level - indoor level

# calculate OITC attempt 1
def calculate_oitc(df0, df_TL, df_oitc):
    # OITC results list
    oitc_list = []

    # constant for now, change with county later
    # @ Kieren: this series should be an expected shape, dependent on the final decision for which of the frequency bands/cols we want to use 
    #note from Kieren: use all between 80 and 4000, so the object should be 18 values (numerical)
    sum_bcf_rss = df_oitc["sum_bcf_rss"]

    # list TL columns in df_TL to be used later (do we still need this step or is it redundant now based on line 114?) commenting out for now
    #f_columns = [col for col in df_TL.columns if col.startswith("f") and "80" <= col[1:] <= "4000"] #added indices for beginning and ending columns 

    for _, row in df0.iterrows():
        A_win = row['A_win']
        A_wal = row['A_wal']
        A_tot = row['A_tot']
        win = row['in.windows']
        wall_in = row['in.insulation_wall']
        wall_out = row['in.geometry_wall_exterior_finish']

        # change the matching. should look at ResStock_match in TL_database for wall_in and window.
        # ResStock_match_out for exterior wall finish. match using %isin% to see if item is in those cols,
        # will return 0-lots of rows. if 0 drop row. randomly select one of the matching rows considering
        # values for each row in weight column.

        # Match wall TL
        TL_wall = get_matching_TL(df_TL, wall_in, wall_out)

        # Match window TL
        TL_win = get_matching_TL(df_TL, win)

        # @ Kieren: here is the point where we want to check to make sure that TL_wall and TL_win are the same shape
        # as sum_bcf_rss.

        # area-weighted TL across all frequency bands
        TL_ass = 10 * np.log10((A_win * 10 ** (-TL_win / 10) + A_wal * 10 ** (-TL_wall / 10)) / A_tot)

        # @ Kieren: here we should check to ensure that TL_ass and sum_bcf_rss are the same shape
        # indoor noise at each frequency band
        indoor_noise_curve = sum_bcf_rss - TL_ass

        # convert to linear scale, sum, then back to dB
        indoor_level = 10 * np.log10(np.sum(10 ** (indoor_noise_curve / 10)))
        outdoor_level = 10 * np.log10(np.sum(10 ** (sum_bcf_rss / 10)))

        oitc = outdoor_level - indoor_level
        oitc_list.append(oitc)

    # Add OITC column to the input df0
    df0["oitc"] = oitc_list
    return df0

df_out = calculate_oitc(df0=df0,df_TL=df_TL, df_oitc=df_oitc)

print("done")












######################################


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


# # Assign TL values based on spreadsheet, using placeholders for now
# tl_frequencies = [
#     50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800,
#     1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000
# ]

# # Set TL values for windows and walls
# for freq in tl_frequencies:
#     df0[f'TL_win_{freq}'] = 30
#     df0[f'TL_wal_{freq}'] = 30

# # Calculate TL of the whole assembly using weighted average
# for freq in tl_frequencies:
#     df0[f'TL_tot_{freq}'] = 10 * np.log10(
#         (df0['A_win'] * 10**(-df0[f'TL_win_{freq}'] / 10) +
#          df0['A_wal'] * 10**(-df0[f'TL_wal_{freq}'] / 10)) / df0['A_tot']
#     )



# #in.geometry_wall_exterior_finish
# #in.geometry_wall_type
# #in.insulation_wall







# # interpolate values in TL_database
# # only look at f100 to f315 to make the line, interpolate f50-f80
# cols_to_interpolate = ["f50", "f63", "f80", "f100", "f125", "f160", "f200","f250", "f315"]
# df_subset = df_TL[cols_to_interpolate].T  # Transpose for row-wise interpolation

# # Perform linear interpolation
# df_interpolated = df_subset.interpolate(method='linear', axis=0, limit_direction='both')

# # Keep existing values from original DataFrame
# df_TL[cols_to_interpolate] = df_interpolated.T.where(df_TL[cols_to_interpolate].isna(), df_TL[cols_to_interpolate])
