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
from pyarrow.parquet import ParquetFile 
import math
from sklearn import linear_model # scikit-learn is a very useful machine learning library with many models built in
from unidecode import unidecode
import random
from matplotlib.ticker import PercentFormatter
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
#df0 = pd.read_parquet(filepath) # read the file at the specified filepath into a pandas dataframeb

pf = ParquetFile(filepath) 
first_n_rows = next(pf.iter_batches(batch_size = 100000)) 
df0 = pa.Table.from_batches([first_n_rows]).to_pandas() 

#filter to only include buildings with 4 units or fewer
building_types_of_interest = ["2 Unit", "3 or 4 Unit", "Single-Family Attached", "Single-Family Detached"]

# Filter the DataFrame
df0 = df0[df0['in.geometry_building_type_acs'].isin(building_types_of_interest)]


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


# interpolating TL values
# define frequency values
freqs = {
    "f50": 50, "f63": 63, "f80": 80, "f100": 100, "f125": 125,
    "f160": 160, "f200": 200, "f250": 250, "f315": 315
}

# column groups
#cols_interp = ["f50", "f63", "f80"]  # columns to interpolate
#cols_known = ["f100", "f125", "f160", "f200", "f250", "f315"]  # reference columns
cols_interp = ["f50", "f63", "f80", "f100"]  # columns to interpolate
cols_known = ["f125", "f250"]  # reference columns

for idx, row in df_TL.iterrows():
    #available_cols = [col for col in cols_known if not pd.isna(row[col])]

    #if len(available_cols) < 2:  # Need at least two points for interpolation
    if pd.isna(row["f125"]) or pd.isna(row["f250"]):
        continue

    

    #redid to just use 125 and 250 center band frequencies for simplicity
    # Values at 125 and 250 Hz
    val_125 = row["f125"]
    val_250 = row["f250"]

    # Log frequencies
    log_freq_125 = np.log10(freqs["f125"])
    log_freq_250 = np.log10(freqs["f250"])

    # Calculate the slope in log space
    slope = (val_250 - val_125) / (log_freq_250 - log_freq_125)

    # Interpolate missing values using calculated slope
    for col in cols_interp:
        if pd.isna(row[col]):  # Only fill missing values
            log_freq = np.log10(freqs[col])
            interp_value = val_125 + slope * (log_freq - log_freq_125)
            df_TL.at[idx, col] = interp_value



print("break")

def match_in_list(column, value):
        return column.apply(lambda x: value in x.split(";") if isinstance(x,str) else False) #for each one, split on a delimiter
    
    
##function for getting the TL rows that we will use for each entry in ResStock
def get_matching_TL(df, basic_category, secondary_category=None):
    """Fetch a random row based on the Basic_Category and optional Secondary_Category,
        returning the 'f' columns as a Series if a match is found, otherwise None."""
    
    if secondary_category:
        filtered_df = df[
            df["ResStock_match"].str.contains(basic_category, na=False) &     #Temporarily removing second category match until I can make the dataset more robust
            df["ResStock_match_out"].str.contains(secondary_category, na=False)
        ]
    else:
        filtered_df = df[df["ResStock_match"].str.contains(basic_category, na=False)] ###PROBLEM - with and without storm window will match regardless since with storm windows is identical but with added text
    
    if not filtered_df.empty:
        random_row = filtered_df.sample(n=1) #potential to sample with weighting incorporated
        f_columns = [col for col in random_row.columns if col.startswith("f") and 80 <= int(col[1:]) <= 4000] #added indices for beginning and ending columns of interest
        return random_row[f_columns].squeeze()
    else:
        return None




# =============================================================================
# def get_matching_TL(df, basic_category, secondary_category=None):
#     """Fetch a random row based on the Basic_Category and optional Secondary_Category,
#         returning the 'f' columns as a Series if a match is found, otherwise None."""
#     
#     if secondary_category:
#         filtered_df = df[
#             match_in_list(df["ResStock_match"], basic_category) &
#             match_in_list(df["ResStock_match_out"], secondary_category)
#         ]
#     else:
#         filtered_df = df[match_in_list(df["ResStock_match"], basic_category)]
#     if not filtered_df.empty:
#         random_row = filtered_df.sample(n=1) #potential to sample with weighting incorporated
#         f_columns = [col for col in random_row.columns if col.startswith("f") and 80 <= int(col[1:]) <= 4000] #added indices for beginning and ending columns of interest
#         return random_row[f_columns].squeeze()
#     else:
#         return None
# =============================================================================


# calculate OITC 
def calculate_oitc(df0, df_TL, df_oitc):
    # OITC results list
    oitc_list = []

    # constant for now, change with county later
    # @ Kieren: this series should be an expected shape, dependent on the final decision for which of the frequency bands/cols we want to use 
    #note from Kieren: use all between 80 and 4000, so the object should be 18 values (numerical)
    sum_bcf_rss = df_oitc["sum_bcf_rss"] # we need this to have named indices f80 thorugh f4000
    
    f_columns = ['f80', 'f100', 'f125', 'f160', 'f200', 'f250', 'f315', 'f400', 'f500', 'f630', 'f800', 'f1000', 'f1250', 'f1600', 'f2000', 'f2500', 'f3150', 'f4000'] #theres a better way to do this I'm sure
    sum_bcf_rss.index = f_columns


    #for _, row in df0.iterrows():

    # list TL columns in df_TL to be used later (do we still need this step or is it redundant now based on line 114?) commenting out for now
    #f_columns = [col for col in df_TL.columns if col.startswith("f") and "80" <= col[1:] <= "4000"] #added indices for beginning and ending columns 

    for idx, (_,row) in enumerate(df0.iterrows()):
        print(f"Iteration {idx + 1}")
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


        #if None in [A_win, TL_win, A_wal, TL_wall, A_tot]:
        #    oitc_list.append(np.nan)
        #    continue
        
        # area-weighted TL across all frequency bands
        try:
            TL_ass = 10 * np.log10((A_win * 10 ** (TL_win / 10) + A_wal * 10 ** (TL_wall / 10)) / A_tot)
    
            # @ Kieren: here we should check to ensure that TL_ass and sum_bcf_rss are the same shape
            # indoor noise at each frequency band
            indoor_noise_curve = sum_bcf_rss - TL_ass
    
            # convert to linear scale, sum, then back to dB
            indoor_level = 10 * np.log10(np.sum(10 ** (indoor_noise_curve / 10)))
            outdoor_level = 10 * np.log10(np.sum(10 ** (sum_bcf_rss / 10)))
    
            oitc = outdoor_level - indoor_level
        except Exception as e:
            oitc = np.nan  # Ensure any calculation errors append NaN
            print(f"Exception on iteration {idx + 1}: {e}") #print errors for debugging
            
            
        oitc_list.append(oitc)

    # Add OITC column to the input df0
    df0["oitc"] = oitc_list
    return df0

df_out = calculate_oitc(df0=df0,df_TL=df_TL, df_oitc=df_oitc)

print("done")


#use this to troubleshoot TL database to try to get more matches
unique_pairs = df0[['in.insulation_wall', 'in.geometry_wall_exterior_finish']].drop_duplicates()
print(unique_pairs)





# Create the histogram of oitc
df0['oitc'].dropna().plot(kind='hist', bins=30, edgecolor='black', figsize=(10, 6))

# Adding titles and labels
plt.title('Histogram of OITC')
plt.xlabel('OITC')
plt.ylabel('Frequency')

# Show the plot
plt.show()


# Plot the building vintage
# Create a table of the counts of each value in 'in.vintage'
vintage_counts = df0['in.vintage'].value_counts()

# Convert the counts to a dataframe
vintage_counts_df = vintage_counts.reset_index()
vintage_counts_df.columns = ['in.vintage', 'count']

# Calculate the total counts for percentage calculation
total_counts = vintage_counts_df['count'].sum()

# Calculate the percentage for each value
vintage_counts_df['percentage'] = (vintage_counts_df['count'] / total_counts) * 100

# Define the correct chronological order 
chronological_order = ['<1940', '1940s', '1950s', '1960s', '1970s', '1980s', '1990s', '2000s', '2010s']

# Set the categorical type with the correct order
vintage_counts_df['in.vintage'] = pd.Categorical(vintage_counts_df['in.vintage'], categories=chronological_order, ordered=True)

# Sort the dataframe by 'in.vintage'
vintage_counts_df = vintage_counts_df.sort_values('in.vintage')

# Print the sorted dataframe
print(vintage_counts_df)

# Plot the percentages as a bar graph
plt.figure(figsize=(10, 6))
plt.bar(vintage_counts_df['in.vintage'], vintage_counts_df['percentage'], color='#56B4E9')
plt.title('Building Vintage Distribution in ResStock')
plt.xlabel('in.vintage')
plt.ylabel('Percentage of ResStock Entries')
plt.gca().yaxis.set_major_formatter(PercentFormatter(decimals = 0))
plt.xticks(rotation=45)
plt.show()





#side by side histograms for pre and post 2000
# Define the chronological order
chronological_order = ['<1940', '1940s', '1950s', '1960s', '1970s', '1980s', '1990s', '2000s', '2010s']

# Filter the DataFrames
pre_2000 = df0[df0['in.vintage'].isin(['<1940', '1940s', '1950s', '1960s', '1970s', '1980s', '1990s'])]
post_2000 = df0[df0['in.vintage'].isin(['2000s', '2010s'])]

# Create subplots
fig, axs = plt.subplots(1, 2, figsize=(15, 6), sharey=True)

# Pre 2000 histogram
axs[0].hist(pre_2000['oitc'].dropna(), bins=30, edgecolor='black', density=True)
axs[0].set_title('Histogram of OITC for Buildings Built Pre 2000')
axs[0].set_xlabel('OITC')
axs[0].set_ylabel('Percentage')
axs[0].yaxis.set_major_formatter(PercentFormatter(xmax=1))

# Post 2000 histogram
axs[1].hist(post_2000['oitc'].dropna(), bins=30, edgecolor='black', density=True)
axs[1].set_title('Histogram of OITC for Buildings Built Post 2000')
axs[1].set_xlabel('OITC')
axs[1].yaxis.set_major_formatter(PercentFormatter(xmax=1))

# Show the plot
plt.show()



## make tables of the wall type by vintage
# Group by insulation_wall for both pre 2000 and post 2000 and count
pre_2000_table = pre_2000.groupby('in.insulation_wall').size().reset_index(name='count_pre_2000')
post_2000_table = post_2000.groupby('in.insulation_wall').size().reset_index(name='count_post_2000')

# Calculate the total counts in each group
total_pre_2000 = pre_2000_table['count_pre_2000'].sum()
total_post_2000 = post_2000_table['count_post_2000'].sum()

# Calculate the percentages
pre_2000_table['percent_pre_2000'] = (pre_2000_table['count_pre_2000'] / total_pre_2000) * 100
post_2000_table['percent_post_2000'] = (post_2000_table['count_post_2000'] / total_post_2000) * 100

# Merge the tables on in.insulation_wall to have them side by side
merged_table = pd.merge(pre_2000_table[['in.insulation_wall', 'percent_pre_2000']], 
                        post_2000_table[['in.insulation_wall', 'percent_post_2000']], 
                        on='in.insulation_wall', 
                        how='outer').fillna(0)

# Display the resulting table
print(merged_table)



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


# corresponding frequencies and values
#known_freqs = np.array([freqs[col] for col in available_cols])  # maybe change to log scale
#known_values = row[available_cols].astype(float).values

#new method just based on 125 and 250:
#known_freqs = [np.log10(freqs["f125"]), np.log10(freqs["f250"])]
#known_values = [row["f125"], row["f250"]]

# Interpolate in linear space
#for col in cols_interp:
#    if pd.isna(row[col]):  # Only fill missing values
#        interp_freq = np.log10(freqs[col]) #added to convert interpolation to log
#        interp_value = np.interp(interp_freq, known_freqs, known_values) #interp_freq used to be freqs[col]
#        df_TL.at[idx, col] = interp_value
