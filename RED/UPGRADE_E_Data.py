#%%
import os
from glob import glob
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import statistics as st
import ipywidgets as widgets
from ipywidgets import VBox
from functools import reduce

#%% set directory of datasets

def set_path():
    
    username = os.getlogin() # get your active username
    path = rf"C:\Users\{username}\PNNL\User-Centered Research - General\clean data\UPGRADE-E Dataset"
    current_location = path.split("\\")[-3:]
    assert current_location[-1] == "UPGRADE-E Dataset", "Set working directory to correct location."
    allfiles = os.listdir(path)

    return path, allfiles

#%% select data to visualize

def choose_data(path, files, file_format="csv"):
    
    datasets = [dataset for dataset in files if dataset.endswith(f".{file_format}")]
    
    checkboxes = [widgets.Checkbox(value=False, description=f"{dataset}") for dataset in datasets]
    checkboxes.append(widgets.Checkbox(value=False, description="Select All"))
    
    box = VBox(checkboxes)
    display(box)
    
    return checkboxes

def selected_datasets(checked_boxes):

    if checked_boxes[-1].value == True:
        selected_datasets = [checked_boxes[i].description for i in range(len(checked_boxes)-1)]
    else:
        selected_datasets = [checked_boxes[i].description for i in range(len(checked_boxes)) if checked_boxes[i].value == True]
    
    print("Selected datasets to merge: \n", selected_datasets, "\n")
    
    return selected_datasets

#%% merge datasets by particpant number

def merge_datasets(datasets, path):
    
    dfs = []
    for dataset in datasets:
        
        filepath = os.path.join(path, dataset)
        df = pd.read_csv(filepath, encoding = "cp1252")
        df.replace([999, "999", 777, "777", "Prefer not to say"], pd.NA, inplace = True)
        dfs.append(df)
    
    df_merged = reduce(lambda left, right: pd.merge(left, right, on = "PermNum", how = "inner"), dfs)

    return df_merged

#%% detect the type of data

def auto_data_typer(df, column):
    
    if not isinstance(df, (pd.DataFrame, dict)):
        raise TypeError("Data type not supported; function only works with DataFrame or dict")
    
    if isinstance(df, pd.DataFrame):
        
        column_cats = df[column].unique()[ ~pd.isnull(df[column].unique()) ]
        data_types = [type(cat) for cat in column_cats]
    
        if all([isinstance(cat, (int, np.integer)) for cat in column_cats]) and len(column_cats) <= 2:
            data_type = "Binary"
        elif all([isinstance(cat, (int, np.integer)) for cat in column_cats]) and len(column_cats) > 2:
            data_type = "Numeric"
        elif str in data_types and column in ordinal_data_order.keys():
            data_type = "Ordinal"
        elif str in data_types and column not in ordinal_data_order.keys():
            data_type = "Nominal"
        else:
            data_type = "Unknown"
    
    elif isinstance(df, dict):
        
        column_cats = df[column]
        data_types = [type(cat) for cat in column_cats]
        
        if all([isinstance(cat, (int, np.integer)) for cat in column_cats]) and len(column_cats) <= 2:
            data_type = "Binary"
        elif all([isinstance(cat, (int, np.integer)) for cat in column_cats]) and len(column_cats) > 2:
            data_type = "Numeric"
        elif str in data_types and column in ordinal_data_order.keys():
            data_type = "Ordinal"
        elif str in data_types and column not in ordinal_data_order.keys():
            data_type = "Nominal"
        else:
            data_type = "Unknown"
    
    return data_type

def assign_data_type(column_categories_dict):

    d_type_dict = {col: auto_data_typer(column_categories_dict, col) for col in column_categories_dict.keys()}
    
    binary_categories = [key for key, val in d_type_dict.items() if val == "Binary"]
    numeric_categories = [key for key, val in d_type_dict.items() if val == "Numeric"] 
    ordinal_categories = [key for key, val in d_type_dict.items() if val == "Ordinal"]
    nominal_categories = [key for key, val in d_type_dict.items() if val == "Nominal"]
    
    return binary_categories, numeric_categories, ordinal_categories, nominal_categories


ordinal_data_order = {
    # from home_demographics.csv
    "education": ["Some high school, no diploma", "High school diploma or GED", "Associates degree or trade school", "Bachelor's degree", "Graduate or professional degree"],
    "energyexpenses": ["Up to $25", "$26-$50", "$51-$100", "$101-$150", "$151-$200", "$201-$250", "$251-$300", "Greater than $300"],
    "hhincome": ["0", "1-15,000", "15,001-30,000", "30,001-45,000", "45,001-60,000", "60,001-75,000", "75,001-100,000", "100,001-125,000", "125,001-150,000", "150,001-175,000", "175,001 or more"],
    "homesqft": ["500 square feet or smaller", "501-1,000 square feet", "1,001-1,500 square feet", "1,501-2,000 square feet", "2,001-2,500 square feet", "2,501-3,000 square feet", "3,000 square feet or larger"],
    "homeyrs": ["Less than 1 year", "1-3 years", "3-5 years", "5-10 years", "10 years or longer"],
    "mortgagerentbins": ["$0-700", "$701-1,500", "$1,501-2,000", "$2,001-3,000", "$3,001-4,000", "$4,001-5,000", "$5,001-6,000", "$6,001-7,500", "$7,501-10,000", "Over $10,000"],
    "reported_age": ["18-25", "26-35", "36-45", "46-55", "56-65", "65-70", "over 70"],
    "yrbuilt": ["before 1900", "1901-1930", "1930-1959", "1960-1979", "1980-1990", "1991-2010", "after 2010"]
    }

#%% find the unique categories of each column, nans excluded

def find_unique_categories(df):

    if "PermNum" in df.columns:
        df_columns = df.drop(["PermNum"], axis = 1).columns
    
    column_categories = {df_columns[i]: 
                         sorted( df[df_columns[i]].unique()[ ~pd.isnull(df[df_columns[i]].unique()) ] )
                         for i in range(len(df_columns))
                         }

    return column_categories

def manually_reorder(dict, data_order=ordinal_data_order):

    for column in data_order.keys():
        if column in dict.keys():
            dict[column] = data_order[column]
    
    return dict

#%% select how to compare data, e.g. by column category, region, or as a whole

def split_data(df, group_by_column):
    
    df_groups = df.groupby(group_by_column)
    
    groups = {}
    for group_name, group_df in df_groups:
        group = df_groups.get_group(f"{group_name}")
        groups[group_name] = group

    reordered_groups = {}
    if group_by_column in ordinal_data_order.keys():
        for key in ordinal_data_order[group_by_column]:
            reordered_groups[key] = groups[key]
        
        return reordered_groups
        
    else:
        return groups

#%% create dict for each column and categories in df and count occurences

def data_counts(df, column_categories_dict):
    
    data_dict = {}
    for column_name in column_categories_dict.keys():
        categories = column_categories_dict.get(column_name)
        category_counts = {str(category): len(df.loc[(df.loc[:, column_name] == category)]) for category in categories}
        data_dict[column_name] = category_counts

    return data_dict

def data_grouper(groups, column_categories_dict):
    
    data_groups_dicts = {}
    for group in groups.keys():
        data_dict = data_counts(groups[group], column_categories_dict)
        data_groups_dicts[group] = data_dict

    return data_groups_dicts

#%% plot and analyze data

#%% function to plot renter vs. owner

# compare renter vs. buyer in same chart
def bar_plotter(column, save_path=None):
    
    rent_category = list(rent_data_dict[f"{column}"].keys())
    rent_values = list(rent_data_dict[f"{column}"].values())

    own_category = list(own_data_dict[f"{column}"].keys())
    own_values = list(own_data_dict[f"{column}"].values())

    # adjust values for uneven x-axis categories by adding zeroes
    def pad_array(vals, target_len):
        return np.pad(vals, (0, target_len - len(vals)), mode = "constant")
    

    max_len = np.maximum(len(rent_values), len(own_values))
    padded_rent_values = pad_array(rent_values, max_len)
    padded_own_values = pad_array(own_values, max_len)
    
    # concatenate categories
    categories = rent_category
    for cat in own_category:
        if cat not in rent_category:
            categories.append(cat)
    
    # set fig, ax parameters
    x_axis = np.arange(len(categories))
    width = 0.4
    fig, ax = plt.subplots()
    
    # plot owner and renter plots next to each other on same chart
    plt.bar(x_axis - width/2, padded_rent_values, width, color = plt.colormaps["viridis"].colors[0], label = "Renter")
    plt.bar(x_axis + width/2, padded_own_values, width, color = plt.colormaps["viridis"].colors[195], label = "Owner")
    
    for i, cat in enumerate(categories):
        text = ax.text(i, -200, cat, ha = "center", va = "top") # set alignment and position for x labels
        
        # rotate x label if length overlaps with other labels
        if len(cat) > 12: # if any over len
            angle = 90
        elif len(cat) > 6:
            angle = 45
        else:
            angle = 0
        
        text.set_rotation(angle)
    
    plt.gca().xaxis.set_major_formatter(plt.NullFormatter()) # remove original x labels
    plt.ylabel("Occurences")
    
    plt.title(f"Column: {column}")
    plt.legend()
    
    if save_path != None:
        fig.tight_layout()
        plt.savefig(os.path.join(save_path, f"{column}_own_rent_plot.png"),
                    dpi = 300
                    )
    
    return None

#%% function to plot pie graphs comparing groups of data

# compare data groups side by side
import math
from collections import OrderedDict

def pie_plotter(data_groups_dicts, column, group_by_column, save_path=None):
    
    data_groups = list(data_groups_dicts.keys())
    num_groups = len(data_groups)

    # calculate the number of rows and columns for subplots
    num_rows = math.ceil(num_groups / 3)
    num_cols = min(num_groups, 3)

    # create a figure and axis objects for subplots
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(num_cols * 5, num_rows * 4))
    if num_groups == 1:
        axes = [axes]  # ensure axes is a list for the single subplot case
    else:
        axes = axes.ravel()  # flatten the axes array

    plt.rc("font", size=7)
    plt.rc("axes", titlesize=9)

    unique_labels = OrderedDict()
    handles = []

    for i, group in enumerate(data_groups):
        categories = data_groups_dicts[group][column].keys()
        values = data_groups_dicts[group][column].values()

        ax = axes[i]
        wedges, texts, autotexts = ax.pie(
            values,
            labels=categories,
            autopct="%1.0f%%",
            labeldistance=None,
            colors=plt.colormaps["viridis"].resampled(len(categories)).colors,  # resample colormap to length of categories for column
            pctdistance=1.15,
        )
        ax.set_title(group)

        # get legend handles and labels for the current subplot
        subplot_handles, subplot_labels = ax.get_legend_handles_labels()
        handles.extend([h for h, l in zip(subplot_handles, subplot_labels) if l not in unique_labels])
        unique_labels.update((l, None) for l in subplot_labels if l not in unique_labels)

    # remove any unused axes
    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    fig.suptitle(f"Group: {group_by_column} \n Column: {column}", fontsize=10)
    fig.legend(handles, list(unique_labels.keys()), loc="center left", bbox_to_anchor=(1, 0.5), ncol=1)

    if save_path is not None:
        plt.savefig(os.path.join(save_path, f"{column}_pie.png"), dpi=300, bbox_inches="tight")

    return None

#%%


