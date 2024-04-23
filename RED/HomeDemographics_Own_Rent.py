#%%
import os
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import statistics as st

#%% open data csv into dataframe, change default encoding

# check to make sure user working directory is correct
path = os.getcwd() # \User-Centered Research - General\clean data\UPGRADE-E Dataset\
current_location = path.split("\\")[-3:]
assert current_location[-1] == "UPGRADE-E Dataset", "Set working directory to correct location."

# set file path for dataset
file = r"home_demographics.csv"
filepath = os.path.join(path, file)
df = pd.read_csv(filepath, encoding = "cp1252") # change csv encoding type

# set save path for exports
parent_dir = os.path.dirname(path)
save_dir = r"home_demographics_plots"
save_filepath = os.path.join(parent_dir, save_dir)

#%% open home_mods df and merge with home_demographics by PermNum and own_rent columns

df_home_mods = pd.read_csv(os.path.join(path, "home_mods.csv"))
df_home_mods.replace(999, pd.NA, inplace = True) # replace 999 with nan for removal
#df_home_mods = pd.merge(df[["PermNum", "own_rent"]], df_home_mods, on = "PermNum", how = "inner").dropna() # merge with own_rent column by PermNum
df = pd.merge(df, df_home_mods, on = "PermNum", how = "inner").dropna() # merge with demographics df by PermNum

#%% split data into renter vs. owner

df_rent = df.loc[ (df.loc[:, "own_rent"] == "Rent") ]
df_own = df.loc[ (df.loc[:, "own_rent"] == "Own") ]                               

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

# create list of all columns together for later
all_columns = list(df_rent_columns)
all_columns.extend([col for col in df_own_columns if col not in all_columns])

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
all_columns.insert(15, "races_all")

#%% manually reorder ordinal categories that were sorted by string and update data dicts
# treating "prefer not to say" as a NaN and removing

ordinal_data_order = {
    "education": ["Some high school, no diploma", "High school diploma or GED", "Associates degree or trade school", "Bachelor's degree", "Graduate or professional degree"],
    "energyexpenses": ["Up to $25", "$26-$50", "$51-$100", "$101-$150", "$151-$200", "$201-$250", "$251-$300", "Greater than $300"],
    "hhincome": ["0", "1-15,000", "15,001-30,000", "30,001-45,000", "45,001-60,000", "60,001-75,000", "75,001-100,000", "100,001-125,000", "125,001-150,000", "150,001-175,000", "175,001 or more"],
    "homesqft": ["500 square feet or smaller", "501-1,000 square feet", "1,001-1,500 square feet", "1,501-2,000 square feet", "2,001-2,500 square feet", "2,501-3,000 square feet", "3,000 square feet or larger"],
    "homeyrs": ["Less than 1 year", "1-3 years", "3-5 years", "5-10 years", "10 years or longer"],
    "mortgagerentbins": ["$0-700", "$701-1,500", "$1,501-2,000", "$2,001-3,000", "$3,001-4,000", "$4,001-5,000", "$5,001-6,000", "$6,001-7,500", "$7,501-10,000", "Over $10,000"],
    "reported_age": ["18-25", "26-35", "36-45", "46-55", "56-65", "65-70", "over 70"],
    "yrbuilt": ["before 1900", "1901-1930", "1930-1959", "1960-1979", "1980-1990", "1991-2010", "after 2010"]
    }

def manually_reorder(dict, column, data_order=ordinal_data_order):
    
    order = data_order[column]
    reordered_dict = {key: dict[column][key] for key in order}
    
    dict[column] = reordered_dict
    
    return reordered_dict

for col in ordinal_data_order.keys():
    manually_reorder(rent_data_dict, col)
    manually_reorder(own_data_dict, col)

#%% combine variables of like types together

# TODO
# remove blocks for just mods

mods_list = [mod for mod in df_home_mods.columns if mod.split("_")[0] == "mod" and len(mod.split("_")) == 2] # get the main mod categories

# group subcategories of each mod category
mod_cats = {mod: { sub_mod for sub_mod in df_home_mods.columns if sub_mod.split("_")[0:2] == mod.split("_")[0:2] } for mod in mods_list}

factors_list = [fac for fac in df_home_mods.columns if fac.split("_")[0] == "fac"] # get list of factor categories

mods_list.extend(["factors"])
all_columns.extend(mods_list)

#%% create dict for each mod category and sum totals

# renters
rent_mod_cats_dict = {}
for mod in mod_cats.keys():
    
    sub_mods = mod_cats.get(f"{mod}")
    sub_mods_totals = {sub_mod: sum(df_home_mods_rent[f"{sub_mod}"]) for sub_mod in sub_mods}
    rent_mod_cats_dict[f"{mod}"] = sub_mods_totals

# owners
own_mod_cats_dict = {}
for mod in mod_cats.keys():
    sub_mods = mod_cats.get(f"{mod}")
    sub_mods_totals = {sub_mod: sum(df_home_mods_own[f"{sub_mod}"]) for sub_mod in sub_mods}
    own_mod_cats_dict[f"{mod}"] = sub_mods_totals

# create dict for each factor category totals and append to mod dicts
factors_rent = {fac: sum(df_home_mods_rent[f"{fac}"]) for fac in factors_list}
rent_mod_cats_dict["factors"] = factors_rent

factors_own = {fac: sum(df_home_mods_own[f"{fac}"]) for fac in factors_list}
own_mod_cats_dict["factors"] = factors_own

# append mod category dicts to data dicts
rent_data_dict.update(rent_mod_cats_dict)
own_data_dict.update(own_mod_cats_dict)

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
save_path_counts = os.path.join(path, save_filepath + save_folder_counts)
save_path_pie = os.path.join(path, save_filepath + save_folder_pie)

# call plotting functions on each column
for column in all_columns:
    
    bar_plotter(f"{column}", save_path_counts) 
    pie_plotter(f"{column}", save_path_pie)

#%% stats

#%% auto detect data type of each column

def auto_data_type(df, column):
    
    column_cats = df[column].unique()
    data_types = [type(cat) for cat in column_cats]
    
    if np.issubdtype(column_cats.dtype, np.number) and len(column_cats) <= 2:
        data_type = "Binary"
    elif np.issubdtype(column_cats.dtype, np.number) and len(column_cats) > 2:
        data_type = "Numeric"
    elif str in data_types and column in ordinal_data_order.keys():
        data_type = "Ordinal"
    else:
        data_type = "Nominal"
    
    return data_type
    
d_type = auto_data_type(df, "education")
print(d_type)

# assign each column to a data type list

#%% run descriptive statistics on discrete numerical data

def discrete_descriptive_stats(df, column): 
    
    mode = st.mode(df[f"{column}"])
    average = round(np.mean(df[f"{column}"]), 2)
    stdev = round(np.std(df[f"{column}"]), 2)
    median = np.median(df[f"{column}"])
    quartile_25 = np.quantile(df[f"{column}"], 0.25)
    quartile_75 = np.quantile(df[f"{column}"], 0.75)
    max = np.max(df[f"{column}"])
    min = np.min(df[f"{column}"])
    count = sum(df[f"{column}"])
    
    return mode, max, quartile_75, median, quartile_25, min, average, stdev, count

discrete_rent_descriptive_stats_df = pd.DataFrame(index = ["mode", "max", "quartile_75", "median", "quartile_25", "min", "average", "stdev", "count"])
discrete_own_descriptive_stats_df = pd.DataFrame(index = ["mode", "max", "quartile_75", "median", "quartile_25", "min", "average", "stdev", "count"])
for column in discrete_categories:
    
    mode, max, quartile_75, median, quartile_25, min, average, stdev, count = discrete_descriptive_stats(df_rent, column)
    discrete_rent_descriptive_stats_df[f"{column}"] = [mode, max, quartile_75, median, quartile_25, min, average, stdev, count]
    
    mode, max, quartile_75, median, quartile_25, min, average, stdev, count = discrete_descriptive_stats(df_own, column)
    discrete_own_descriptive_stats_df[f"{column}"] = [mode, max, quartile_75, median, quartile_25, min, average, stdev, count]

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

#%% run descriptive statistics on binary data

def binary_descriptive_stats(df, column):
    
    mode = st.mode(df[f"{column}"])
    average = round(np.mean(df[f"{column}"]), 2)
    stdev = round(np.std(df[f"{column}"]), 2)
    count = sum(df[f"{column}"])
    
    return mode, average, stdev, count

binary_rent_descriptive_stats_df = pd.DataFrame(index = ["mode", "average", "stdev", "count"])
binary_own_descriptive_stats_df = pd.DataFrame(index = ["mode", "average", "stdev", "count"])
for column in binary_categories:
    
    mode, average, stdev, count = binary_descriptive_stats(df_rent, column)
    binary_rent_descriptive_stats_df[f"{column}"] = [mode, average, stdev, count]
    
    mode, average, stdev, count = binary_descriptive_stats(df_own, column)
    binary_own_descriptive_stats_df[f"{column}"] = [mode, average, stdev, count]

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
descriptive_stats_rent_combined_df = pd.concat([discrete_rent_descriptive_stats_df, ordinal_rent_descriptive_stats_df, 
                                                binary_rent_descriptive_stats_df, nominal_rent_descriptive_stats_df], axis = 1).T
descriptive_stats_rent_combined_df.insert(0, column = "Rent/Own", value = "Rent")

descriptive_stats_own_combined_df = pd.concat([discrete_own_descriptive_stats_df, ordinal_own_descriptive_stats_df, 
                                               binary_own_descriptive_stats_df, nominal_own_descriptive_stats_df], axis = 1).T
descriptive_stats_own_combined_df.insert(0, column = "Rent/Own", value = "Own")

# combine rent and own into same df
descriptive_stats_all_combined_df = pd.concat([descriptive_stats_rent_combined_df, descriptive_stats_own_combined_df], axis = 0).fillna("")

# export combined df to csv
save_path_stats = os.path.join(path, save_dir)
descriptive_stats_all_combined_df.to_csv(os.path.join(save_path_stats, "own_rent_descriptive_stats.csv"))

#%% chi** statistcal comparison of own vs. rent data


