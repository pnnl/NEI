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

path = r"C:\Users\mcco689\PNNL\NEB Decarb - General\Datasets\ResStock" #os.getcwd() # this will get your current active folder, or you can type it directly with r"C:\path\to\folder\etc\\"
file = r"baseline_metadata_and_annual_results.csv" # if you set your current folder to the directory where the file is located (in the top right of Spyder) then all you need is the file name
filepath = os.path.join(path, file) # add the file to the folder path
df = pd.read_csv(filepath) # read the file at the speicifed filepath into a pandas dataframe

#%% open, examine, and select data

df_stats = df.describe() # descriptive statistics on each column

# find and remove NaNs
nans = df.isnull().sum() # check how many nans are in each column
df_no_nans = df.dropna() # removes all nans, or can set thresh to limit how many nans are needed to drop that row or column
df_nans_filled = df.fillna(0).astype("int") # replace all nans with a value (useful for plotting, sometimes nans break matplotlib)

df_sel_col_name = df[["homesize", "yearsinhome", "heatpumpHVAC"]] # select columns by name
df_sliced_name = df.loc[:, "yearbuilt" : "yearsinhome"] # slice by the name of the columns, ":" by itself means "all" rows or columns
df_sliced_idx = df.iloc[0:100, 2:5] # slice the dataframe by index [rows, columns]
df_sliced_conditional = df.loc[(df.loc[:, "heatpumpwh"] == 1)] # select rows if a column is equal to a certain value

df_heatpumpwh_transposed = df_sliced_conditional.T # transpose a dataframe so rows are now columns

#%% basic Pythonic operations

# define a simple function
def age_count_for_loop(df, threshold):
    """
    Count all participants over the threshold age.
    """
    
    i = 0
    for age in df["age"]:
        if age > threshold:
            i += 1
            
    return i

# list comprehension is a Python technique that can replace a for loop while making a list
list_comp = [i for i in df.columns]

# e.g., the list comprehension below does the same thing as the for loop in the previous function
def age_count_list_comp(df, threshold):
    
    i = 0
    [i := i + 1 for age in df["age"] if age > threshold]
    
    return i

age_with_loop = age_count_for_loop(df, 65)
age_with_listcomp = age_count_list_comp(df, 65)
print(age_with_loop == age_with_listcomp) # both functions should return the same value

# you can use a switch-case statement instead of an if-else iteration (only for Python versions 3.10+)
def has_heatpump(df):
    """
    Check what type of heat pump a participant has.
    """
    
    match (df["heatpumpwh"], df["heatpumpHVAC"]):
        case (0, 0):
            return "None"
        case (1, 0):
            return "Water Heater"
        case (0, 1):
            return "HVAC"
        case (1, 1):
            return "Both"
        case _:
            return "Unknown"

# lambda creates a local function that can be applied in one line. axis = 1 applies function to columns, and 0 to rows
df["heatpump"] = df.apply(lambda df: has_heatpump(df), axis = 1) # create a new column in the dataframe called "heatpump"

# dictionaries are a Python data structure similar to JSON, they can store any type of data in key-value pairs
number_heatpumps_dict = {
                        "Both": sum(df["heatpump"] == "Both"),
                        "HVAC": sum(df["heatpump"] == "HVAC"),
                        "Water Heater": sum(df["heatpump"] == "Water Heater"),
                        "None": sum(df["heatpump"] == "None"),
                        "Unknown": sum(df["heatpump"] == "Unknown")
                        }

# dictionary comprehension can create a dictionary similar to how list comprehension works, the code below does the same thing as the previous dict
number_heatpumps_dict_comp = {df["heatpump"].value_counts().index[i]: df["heatpump"].value_counts().iloc[i] for i in range(len(df["heatpump"].value_counts()))}

#%% plot the data with seaborn and matplotlib

# create a plot of education vs. income
sns.lineplot(data = df, x = df["education"], y = df["income"])
plt.show() # display the plot in the IDE
plt.clf() # clear the plot from active memory to show the next one

# create a boxplot of income and customize the visual properties and labels
sns.boxplot(data = df["income"], width = 0.25,
            boxprops = {"facecolor": "lightsteelblue", "edgecolor": "black"},
            medianprops = {"color": "r","linewidth": 2},
            whiskerprops = {"color": "black"},
            flierprops = {"marker": "x"}
            )
plt.title("Income")
plt.xlabel("All")
plt.xticks([])
plt.ylabel("$")
plt.show()
plt.clf()

# create a pivot table and plot a heat map
category_order = ["Both", "HVAC", "Water Heater", "None"] # set order for labels, otherwise default is alphabetical/ascending
df_pivot = pd.pivot_table(data = df, index = "heatpump", columns = "education", values = "income").reindex(category_order)
sns.heatmap(data = df_pivot, cmap = "Spectral_r") # set the color palette with cmap, there are many built-in color options
plt.title("Income")
plt.show()
plt.savefig("income_heatmap.jpeg") # save the plot as an image in your current folder
plt.clf()

#%% save output as a csv file

df_to_save = df_heatpumpwh_transposed

current_date = dt.today().strftime("%m-%d-%y")
save_file_name = f"Results_{current_date}.csv"
save_path = os.path.join(path, save_file_name)

df_to_save.to_csv(save_path)