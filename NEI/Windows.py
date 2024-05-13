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
file = r"baseline_metadata_and_annual_results.csv" # if you set your current folder to the directory where the file is located (in the top right of Spyder) then all you need is the file name
filepath = os.path.join(path, file) # add the file to the folder path
df0 = pd.read_csv(filepath) # read the file at the speicifed filepath into a pandas dataframe

file1 = r"upgrade2.01_metadata_and_annual_results.csv" # if you set your current folder to the directory where the file is located (in the top right of Spyder) then all you need is the file name
filepath1 = os.path.join(path, file1) # add the file to the folder path
df1 = pd.read_csv(filepath1) 

file2 = r"upgrade2.02_metadata_and_annual_results.csv" # if you set your current folder to the directory where the file is located (in the top right of Spyder) then all you need is the file name
filepath2 = os.path.join(path, file2) # add the file to the folder path
df2 = pd.read_csv(filepath2) 


#Now get the info you need from each
for column in df0.columns:
    print(column)


# Creating a new DataFrame with the selected columns
df0_new = pd.DataFrame(df0.loc[:, "bldg_id":"upgrade"].join(df0.loc[:, "out.site_energy.net.energy_consumption.kwh":"out.emissions.all_fuels.lrmer_mid_case_15_2025_start.co2e_kg"]))
df1_new = pd.DataFrame(df1.loc[:, "bldg_id":"upgrade"].join(df1.loc[:, "out.site_energy.net.energy_consumption.kwh":"out.emissions.all_fuels.lrmer_mid_case_15_2025_start.co2e_kg"]))


df_diff = df1_new - df0_new
df_metadata = df0[['bldg_id', 'in.sqft', 'weight', 'in.ashrae_iecc_climate_zone_2004', 'in.census_division', 'in.census_region', 'in.county']]

df_full = pd.concat([df_metadata,df_diff], axis=1)



# Select numerical columns excluding the specific non-numerical or grouping column
numerical_cols = df_full.select_dtypes(include=[np.number]).columns.drop('in.ashrae_iecc_climate_zone_2004', errors='ignore')

df_averaged_cz = df_full.groupby('in.ashrae_iecc_climate_zone_2004')[numerical_cols].mean().reset_index()

#copy to clipboard:
df_averaged_cz.to_clipboard(index=False, header=True)



##Do the same comparison now with Envelope Upgrade option 2
# Creating a new DataFrame with the selected columns
df2_new = pd.DataFrame(df2.loc[:, "bldg_id":"upgrade"].join(df2.loc[:, "out.site_energy.net.energy_consumption.kwh":"out.emissions.all_fuels.lrmer_mid_case_15_2025_start.co2e_kg"]))


df_diff2 = df2_new - df0_new

df_full2 = pd.concat([df_metadata,df_diff2], axis=1)


# Select numerical columns excluding the specific non-numerical or grouping column
numerical_cols2 = df_full2.select_dtypes(include=[np.number]).columns.drop('in.ashrae_iecc_climate_zone_2004', errors='ignore')

df_averaged_cz2 = df_full2.groupby('in.ashrae_iecc_climate_zone_2004')[numerical_cols].mean().reset_index()

#copy to clipboard:
df_averaged_cz2.to_clipboard(index=False, header=True)




#import census data and PNNL datato find number of households per climate zone
path_hh = fr"C:\Users\{username}\PNNL\NEB Decarb - General\Datasets\CensusDemographicsAndHousing" 
file_hh = r"households.counties.csv" 
filepath_hh = os.path.join(path_hh, file_hh) 
df_hh = pd.read_csv(filepath_hh) 


df_hh = df_hh[df_hh["Unnamed: 2"] != "Percent"]
df_hh.columns = ['county', 'state', 'unit', 'households']
df_hh['state'] = df_hh['state'].str.strip()
# Remove accents from strings in the 'county' column
df_hh['county'] = df_hh['county'].apply(lambda x: unidecode(x))


#counties and climate zones
path_czc = fr"C:\Users\{username}\PNNL\NEB Decarb - General\Datasets" 
file_czc = r"County Climate Regions BA and IECC DOE PNNL MC 2-18-2022_km_data_processing.csv" 
filepath_czc = os.path.join(path_czc, file_czc) 
df_czc = pd.read_csv(filepath_czc) 


pattern = r'(.+?)\s*(County|Borough|Municipio|Municipality|Parish|Census Area|city|City and Borough)$'
df_hh[['county1', 'countydes']] = df_hh['county'].str.extract(pattern, expand=True)


# Adjust county1 and countydes based on the condition
df_hh.loc[df_hh['countydes'] == 'city', 'county1'] = df_hh['county1'] + ' (city)'
df_hh.loc[df_hh['countydes'] == 'city', 'countydes'] = 'city'

df_hh.loc[df_hh['countydes'] == 'Census Area', 'county1'] = df_hh['county1'] + ' (CA)'
df_hh.loc[df_hh['countydes'] == 'Census Area', 'countydes'] = 'Census Area'

#manually fix carson city, NV and DC
df_hh.loc[(df_hh['county'] == 'Carson City') & (df_hh['state'] == 'Nevada'), 'county1'] = 'Carson City (city)'
df_hh.loc[(df_hh['county'] == 'Carson City') & (df_hh['state'] == 'Nevada'), 'countydes'] = 'city'

df_hh.loc[(df_hh['county'] == 'District of Columbia') & (df_hh['state'] == 'District of Columbia'), 'county1'] = 'District of Columbia'
df_hh.loc[(df_hh['county'] == 'District of Columbia') & (df_hh['state'] == 'District of Columbia'), 'countydes'] = 'District'

#Fix Misc differences
df_hh.loc[(df_hh['county'] == 'De Baca County') & (df_hh['state'] == 'New Mexico'), 'county1'] = 'DeBaca'
df_hh.loc[(df_hh['county'] == 'De Baca County') & (df_hh['state'] == 'New Mexico'), 'countydes'] = 'County'

df_hh.loc[(df_hh['county'] == 'LaSalle Parish') & (df_hh['state'] == 'Louisiana'), 'county1'] = 'La Salle'
df_hh.loc[(df_hh['county'] == 'LaSalle Parish') & (df_hh['state'] == 'Louisiana'), 'countydes'] = 'Parish'

df_hh.loc[(df_hh['county'] == 'LaPorte County') & (df_hh['state'] == 'Indiana'), 'county1'] = 'La Porte'
df_hh.loc[(df_hh['county'] == 'LaPorte County') & (df_hh['state'] == 'Indiana'), 'countydes'] = 'County'

df_hh.loc[(df_hh['county'] == 'LaGrange County') & (df_hh['state'] == 'Indiana'), 'county1'] = 'Lagrange'
df_hh.loc[(df_hh['county'] == 'LaGrange County') & (df_hh['state'] == 'Indiana'), 'countydes'] = 'County'

df_hh.loc[(df_hh['county'] == 'DeKalb County') & (df_hh['state'] == 'Indiana'), 'county1'] = 'De Kalb'
df_hh.loc[(df_hh['county'] == 'DeKalb County') & (df_hh['state'] == 'Indiana'), 'countydes'] = 'County'

df_hh.loc[(df_hh['county'] == 'LaSalle County') & (df_hh['state'] == 'Illinois'), 'county1'] = 'La Salle'
df_hh.loc[(df_hh['county'] == 'LaSalle County') & (df_hh['state'] == 'Illinois'), 'countydes'] = 'County'

#Alaska modifications (need someone to double check assumptions here)
df_hh.loc[(df_hh['county'] == 'Prince of Wales-Hyder Census Area') & (df_hh['state'] == 'Alaska'), 'county1'] = 'Prince of Wales-Outer Ketchikan (CA)'
df_hh.loc[(df_hh['county'] == 'Prince of Wales-Hyder Census Area') & (df_hh['state'] == 'Alaska'), 'countydes'] = 'Census Area'

df_hh.loc[(df_hh['county'] == 'Wrangell City and Borough') & (df_hh['state'] == 'Alaska'), 'county1'] = 'Wrangell-Petersburg (CA)'
df_hh.loc[(df_hh['county'] == 'Wrangell City and Borough') & (df_hh['state'] == 'Alaska'), 'countydes'] = 'Census Area fm. City and Borough'

df_hh.loc[(df_hh['county'] == 'Petersburg Borough') & (df_hh['state'] == 'Alaska'), 'county1'] = 'Wrangell-Petersburg (CA)'
df_hh.loc[(df_hh['county'] == 'Petersburg Borough') & (df_hh['state'] == 'Alaska'), 'countydes'] = 'Census Area fm. Borough'

df_hh.loc[(df_hh['county'] == 'Skagway Municipality') & (df_hh['state'] == 'Alaska'), 'county1'] = 'Skagway-Hoonah-Angoon (CA)'
df_hh.loc[(df_hh['county'] == 'Skagway Municipality') & (df_hh['state'] == 'Alaska'), 'countydes'] = 'Census Area fm. Municipality'

df_hh.loc[(df_hh['county'] == 'Hoonah-Angoon Census Area') & (df_hh['state'] == 'Alaska'), 'county1'] = 'Skagway-Hoonah-Angoon (CA)'
df_hh.loc[(df_hh['county'] == 'Hoonah-Angoon Census Area') & (df_hh['state'] == 'Alaska'), 'countydes'] = 'Census Area'



# Create a dictionary mapping (county, state) to 'cz'
cz_mapping = {(county, state): cz for county, state, cz in zip(df_czc['County'], df_czc['State'], df_czc['cz'])}

# Use map to apply the mapping to create a new 'cz' column in df_hh
df_hh['cz'] = df_hh.apply(lambda row: cz_mapping.get((row['county'], row['state']), 'None'), axis=1)



cz_mapping = {(county, state): cz for county, state, cz in zip(df_czc['County'], df_czc['State'], df_czc['cz'])}

# Use map to apply the mapping to create a new 'cz' column in df_hh
df_hh['cz'] = df_hh.apply(lambda row: cz_mapping.get((row['county1'], row['state']), None), axis=1)



# Group by 'cz' and calculate sum and count
hh_per_cz = df_hh.groupby('cz').agg({'households': ['sum', 'count']}).reset_index()

# Flatten the multi-index columns
hh_per_cz.columns = ['cz', 'total_households', 'n_counties']


hh_per_cz.to_clipboard(index=False, excel=True)