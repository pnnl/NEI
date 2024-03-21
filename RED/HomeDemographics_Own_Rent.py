#%%
import os
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import statistics as st

#%% open data csv into dataframe, change default encoding

# set check to make sure user directory is correct
path = os.getcwd() # \User-Centered Research - General\clean data\UPGRADE-E Dataset
file = r"home_demographics.csv"
filepath = os.path.join(path, file)
df = pd.read_csv(filepath, encoding = "cp1252") # change csv encoding type

# set save path for exports
save_dir = r"home_demographics_plots"

#%% split data into renter vs. owner

df_rent = df.loc[(df.loc[:, "own_rent"] == "Rent")]
df_own = df.loc[(df.loc[:, "own_rent"] == "Own")]                               

#%% open home_mods df and merge with home_demographics by PermNum

df_home_mods = pd.read_csv(os.path.join(path, "home_mods.csv"))
df_home_mods.replace(999, pd.NA, inplace = True) # replace 999 with nan for removal
df_home_mods = pd.merge(df[["PermNum", "own_rent"]], df_home_mods, on = "PermNum", how = "inner").dropna() # merge with own_rent column by PermNum

#%% combine variables of like types together

mods_list = [mod for mod in df_home_mods.columns if mod.split("_")[0] == "mod" and len(mod.split("_")) == 2] # get the main mod categories

mod_cats = {mod: [ sub_mod for sub_mod in df_home_mods.columns if sub_mod.split("_")[0:2] == mod.split("_")[0:2] 
                  and len(sub_mod.split("_")) > 2 ] for mod in mods_list} # group subcategories of each mod category

factors_list = [fac for fac in df_home_mods.columns if fac.split("_")[0] == "fac"] # get list of factor categories

#%% find the unique categories of each column, nans excluded

# renters
df_rent_columns = df_rent.drop(["PermNum", "own_rent", "race_prefernottosay", "mortgagerent"], axis = 1).columns # drop unneeded columns
rent_column_categories = {df_rent_columns[i]: 
                          sorted(df_rent[df_rent_columns[i]].unique()
                          [~pd.isnull(df_rent[df_rent_columns[i]].unique())])
                          for i in range(len(df_rent_columns))
                          }

# owners
df_own_columns = df_own.drop(["PermNum", "own_rent", "race_prefernottosay", "mortgagerent"], axis = 1).columns # drop unneeded columns
own_column_categories = {df_own_columns[i]: 
                         sorted(df_own[df_own_columns[i]].unique()
                         [~pd.isnull(df_own[df_own_columns[i]].unique())])
                         for i in range(len(df_own_columns))
                         }

all_columns = sorted(list(set(list(df_rent_columns) + list(df_own_columns)))) # create list of all columns together for later

#%% create dict for each column and categories in df and count occurences

# renters
rent_data_dict = {}
for column_name in df_rent_columns:
    categories = sorted(rent_column_categories.get(f"{column_name}"))
    category_counts = {str(category): len(df_rent.loc[(df_rent.loc[:, f"{column_name}"] == category)]) for category in categories}
    rent_data_dict[f"{column_name}"] = category_counts

# owners
own_data_dict = {}
for column_name in df_own_columns:
    
    categories = own_column_categories.get(f"{column_name}")
    category_counts = {str(category): len(df_own.loc[(df_own.loc[:, f"{column_name}"] == category)]) for category in categories}
    own_data_dict[f"{column_name}"] = category_counts

#%% combine race counts into dictionary and add to data_dicts

# rent
df_rent_races = df_rent.loc[:, "race_americanindianoralaskannati" : "race_white"].drop(["race_prefernottosay"], axis = 1)
df_rent_races.columns = [column.replace("race_", "") for column in df_rent_races.columns]
df_rent_races.rename( columns = {"otherpleasespecify": "other"}, inplace = True )

rent_races_all = {}
for column_name in df_rent_races.columns:
    column_counts = sum(df_rent_races[f"{column_name}"])
    rent_races_all[f"{column_name}"] = column_counts

rent_data_dict["races_all"] = rent_races_all

# own
df_own_races = df_own.loc[:, "race_americanindianoralaskannati" : "race_white"].drop(["race_prefernottosay"], axis = 1)
df_own_races.columns = [column.replace("race_", "") for column in df_own_races.columns]
df_own_races.rename( columns = {"otherpleasespecify": "other"}, inplace = True )

own_races_all = {}
for column_name in df_own_races.columns:
    column_counts = sum(df_own_races[f"{column_name}"])
    own_races_all[f"{column_name}"] = column_counts

own_data_dict["races_all"] = own_races_all

# add races_all to all_columns list
all_columns.insert(22, "races_all")

#%% manually reorder ordinal categories that were sorted by string
# treating "prefer not to say" as a NaN and removing

# rent

rent_data_dict["education"] = {
    "Some high school, no diploma": 147,
    "High school diploma or GED": 1392,
    "Associates degree or trade school": 645,
    "Bachelor's degree": 399,
    "Graduate or professional degree": 147
    }

rent_data_dict["energyexpenses"] = {
    "Up to $25": 57,
    "$26-$50": 143,
    "$51-$100": 422,
    "$101-$150": 600,
    "$151-$200": 550,
    "$201-$250": 379,
    "$251-$300": 290,
    "Greater than $300": 315    
    }

rent_data_dict["hhincome"] = {
    "0": 54,
    "1-15,000": 456,
    "15,001-30,000": 762,
    "30,001-45,000": 534,
    "45,001-60,000": 405,
    "60,001-75,000": 203,
    "75,001-100,000": 190,
    "100,001-125,000": 76,
    "125,001-150,000": 55,
    "150,001-175,000": 65,
    "175,001 or more": 40
    }

rent_data_dict["homesqft"] = {
    "500 square feet or smaller": 110,
    "501-1,000 square feet": 542,
    "1,001-1,500 square feet": 688,
    "1,501-2,000 square feet": 567,
    "2,001-2,500 square feet": 346,
    "2,501-3,000 square feet": 163,
    "3,000 square feet or larger": 64
    }

rent_data_dict["homeyrs"] = {
    "Less than 1 year": 402,
    "1-3 years": 1000,
    "3-5 years": 666,
    "5-10 years": 520,
    "10 years or longer": 306
    }

rent_data_dict["mortgagerentbins"] = {
    "$0-700": 1069,
    "$701-1,500": 1285,
    "$1,501-2,000": 238,
    "$2,001-3,000": 156,
    "$3,001-4,000": 36,
    "$4,001-5,000": 26,
    "$5,001-6,000": 22,
    "$6,001-7,500": 17,
    "$7,501-10,000": 7,
    "Over $10,000": 5
    }

rent_data_dict["yrbuilt"] = {
    "before 1900": 49,
    "1901-1930": 148,
    "1930-1959": 357,
    "1960-1979": 598,
    "1980-1990": 475,
    "1991-2010": 447,
    "after 2010": 221    
    }

# own

own_data_dict["education"] = {
    "Some high school, no diploma": 113,
    "High school diploma or GED": 1790,
    "Associates degree or trade school": 1542,
    "Bachelor's degree": 1828,
    "Graduate or professional degree": 1296
    }

own_data_dict["energyexpenses"] = {
    "Up to $25": 41,
    "$26-$50": 138,
    "$51-$100": 740,
    "$101-$150": 1352,
    "$151-$200": 1545,
    "$201-$250": 1184,
    "$251-$300": 903,
    "Greater than $300": 743
    }

own_data_dict["hhincome"] = {
    "0": 39,
    "1-15,000": 300,
    "15,001-30,000": 740,
    "30,001-45,000": 862,
    "45,001-60,000": 961,
    "60,001-75,000": 738,
    "75,001-100,000": 1034,
    "100,001-125,000": 637,
    "125,001-150,000": 569,
    "150,001-175,000": 404,
    "175,001 or more": 510
    }

own_data_dict["homesqft"] = {
    "500 square feet or smaller": 73,
    "501-1,000 square feet": 441,
    "1,001-1,500 square feet": 1389,
    "1,501-2,000 square feet": 1889,
    "2,001-2,500 square feet": 1523,
    "2,501-3,000 square feet": 830,
    "3,000 square feet or larger": 531
    }

own_data_dict["homeyrs"] = {
    "Less than 1 year": 236,
    "1-3 years": 873,
    "3-5 years": 1144,
    "5-10 years": 1394,
    "10 years or longer": 3346
    }

own_data_dict["mortgagerentbins"] = {
    "$0-700": 2433,
    "$701-1,500": 2077,
    "$1,501-2,000": 800,
    "$2,001-3,000": 642,
    "$3,001-4,000": 180,
    "$4,001-5,000": 113,
    "$5,001-6,000": 114,
    "$6,001-7,500": 77,
    "$7,501-10,000": 56,
    "Over $10,000": 71
    }

own_data_dict["yrbuilt"] = {
    "before 1900": 169 ,
    "1901-1930": 316,
    "1930-1959": 901,
    "1960-1979": 1337,
    "1980-1990": 1113,
    "1991-2010": 1825,
    "after 2010": 1061
    }

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

#%% function to plot pie graphs comparing owner vs. renter

# compare own vs. rent side by side
def pie_plotter(column, save_path=None):
    
    rent_categories = rent_data_dict[f"{column}"].keys()
    rent_values = rent_data_dict[f"{column}"].values()
    
    own_categories = own_data_dict[f"{column}"].keys()
    own_values = own_data_dict[f"{column}"].values()
    
    plt.rc("font", size = 7)
    plt.rc("axes", titlesize = 9)
    
    fig, ax = plt.subplots(1, 2
                           #constrained_layout=True
                           )
    
    ax[0].pie(rent_values, labels = rent_categories, autopct = "%1.0f%%", labeldistance = None, 
              colors = plt.colormaps["viridis"].resampled(len(rent_categories)).colors, # resample colormap to length of categories for column
              pctdistance = 1.15 
              )
    ax[0].set_title("Rent")
    
    ax[1].pie(own_values, labels = own_categories, autopct = "%1.0f%%", labeldistance = None, 
              colors = plt.colormaps["viridis"].resampled(len(own_categories)).colors, # resample colormap to length of categories for column
              pctdistance = 1.15
              )
    ax[1].set_title("Own")
    
    handles, labels = ax[0].get_legend_handles_labels()
    handles += ax[1].get_legend_handles_labels()[0]
    labels_1 = ax[1].get_legend_handles_labels()[1]
    for label in labels_1:
        if label not in labels:
            labels += label

    fig.suptitle(f"Column: {column}", fontsize = 10)
    fig.legend(loc = "lower center", labels = labels)
    
    if save_path != None:
        #fig.tight_layout()
        plt.savefig(os.path.join(save_path, f"{column}_own_rent_pie.png"),
                    dpi = 300
                    )
    
    return None

#%% create plots for each column and export

# save as image to folder in cwd
save_folder_counts = r"\own_rent_counts"
save_folder_pie = r"\own_rent_pie"
save_path_counts = os.path.join(path, save_dir + save_folder_counts)
save_path_pie = os.path.join(path, save_dir + save_folder_pie)

# call plotting functions on each column
for column in all_columns:
    
    bar_plotter(f"{column}", save_path_counts) 
    pie_plotter(f"{column}", save_path_pie)

#%% stats

# split data into discrete, ordinal, and nominal groups
idx_dis = [0,1,2,9]
idx_ord = [3,5,10,11,13,14,23,26]
idx_nom = [i for i in range(len(all_columns)) if i not in idx_ord and i not in idx_dis]

discrete_categories = [all_columns[idx] for idx in idx_dis]
ordinal_categories = [all_columns[idx] for idx in idx_ord]
nominal_categories = [all_columns[idx] for idx in idx_nom]

#%% run descriptive statistics on discrete numerical data

def discrete_descriptive_stats(df, column): # add skew kertosis
    
    mode = st.mode(df[f"{column}"])
    average = round(np.mean(df[f"{column}"]), 2)
    stdev = round(np.std(df[f"{column}"]), 2)
    median = np.median(df[f"{column}"])
    quartile_25 = np.quantile(df[f"{column}"], 0.25)
    quartile_75 = np.quantile(df[f"{column}"], 0.75)
    max = np.max(df[f"{column}"])
    min = np.min(df[f"{column}"])
    
    return mode, max, quartile_75, median, quartile_25, min, average, stdev

discrete_rent_descriptive_stats_df = pd.DataFrame(index = ["mode", "max", "quartile_75", "median", "quartile_25", "min", "average", "stdev"])
discrete_own_descriptive_stats_df = pd.DataFrame(index = ["mode", "max", "quartile_75", "median", "quartile_25", "min", "average", "stdev",])
for column in discrete_categories:
    
    mode, max, quartile_75, median, quartile_25, min, average, stdev = discrete_descriptive_stats(df_rent, column)
    discrete_rent_descriptive_stats_df[f"{column}"] = [mode, max, quartile_75, median, quartile_25, min, average, stdev]
    
    mode, max, quartile_75, median, quartile_25, min, average, stdev = discrete_descriptive_stats(df_own, column)
    discrete_own_descriptive_stats_df[f"{column}"] = [mode, max, quartile_75, median, quartile_25, min, average, stdev]

#%% run descriptive statistics on ordinal categorical and binned data

def ordinal_descriptive_stats(df, column):
        
    ordinal_list = []
    total = 0
    for i, j in df[f"{column}"].items():
        total += j
        for n in range(j):
            ordinal_list.append(i)
    
    mode = st.mode(ordinal_list)
    median = ordinal_list[int(len(ordinal_list)/2)]
    quartile_25 = ordinal_list[int(len(ordinal_list)*0.25)]
    quartile_75 = ordinal_list[int(len(ordinal_list)*0.75)]
    max = ordinal_list[-1]
    min = ordinal_list[0]
    
    return mode, max, quartile_75, median, quartile_25, min


ordinal_rent_descriptive_stats_df = pd.DataFrame(index = ["mode", "max", "quartile_75", "median", "quartile_25", "min"])
ordinal_own_descriptive_stats_df = pd.DataFrame(index = ["mode", "max", "quartile_75", "median", "quartile_25", "min"])
for column in ordinal_categories:
    
    mode, max, quartile_75, median, quartile_25, min = ordinal_descriptive_stats(rent_data_dict, column)
    ordinal_rent_descriptive_stats_df[f"{column}"] = [mode, max, quartile_75, median, quartile_25, min]
    
    mode, max, quartile_75, median, quartile_25, min = ordinal_descriptive_stats(own_data_dict, column)
    ordinal_own_descriptive_stats_df[f"{column}"] = [mode, max, quartile_75, median, quartile_25, min]

#%% run descriptive statistics on nominal categorical data

def nominal_descriptive_stats(df, column):
        
    nominal_list = []
    total = 0
    for i, j in df[f"{column}"].items():
        total += j
        for n in range(j):
            nominal_list.append(i)
    
    mode = st.mode(nominal_list)
    
    return mode

nominal_rent_descriptive_stats_df = pd.DataFrame(index = ["mode"])
nominal_own_descriptive_stats_df = pd.DataFrame(index = ["mode"])
for column in nominal_categories:
    
    mode = nominal_descriptive_stats(rent_data_dict, column)
    nominal_rent_descriptive_stats_df[f"{column}"] = [mode]
    
    mode = nominal_descriptive_stats(own_data_dict, column)
    nominal_own_descriptive_stats_df[f"{column}"] = [mode]

#%% combine stats dfs into one df and export

# add column for rent or own
descriptive_stats_rent_combined_df = pd.concat([discrete_rent_descriptive_stats_df, ordinal_rent_descriptive_stats_df, nominal_rent_descriptive_stats_df], axis = 1).T
descriptive_stats_rent_combined_df.insert(0, column = "Rent/Own", value = "Rent")

descriptive_stats_own_combined_df = pd.concat([discrete_own_descriptive_stats_df, ordinal_own_descriptive_stats_df, nominal_own_descriptive_stats_df], axis = 1).T
descriptive_stats_own_combined_df.insert(0, column = "Rent/Own", value = "Own")

# combine rent and own into same df
descriptive_stats_all_combined_df = pd.concat([descriptive_stats_rent_combined_df, descriptive_stats_own_combined_df], axis = 0).fillna("")

# export combined df to csv
save_path_stats = os.path.join(path, save_dir)
descriptive_stats_all_combined_df.to_csv(os.path.join(save_path_stats, "own_rent_descriptive_stats.csv"))

#%% chi** statistcal comparison of own vs. rent data


