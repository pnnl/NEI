#%%
import os
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt

#%% open data csv into dataframe, change default encoding

path = os.getcwd()
file = r"home.demographics_30jan2024.csv"
filepath = os.path.join(path, file)
df = pd.read_csv(filepath, encoding = "cp1252")

#%% split data into renter vs. owner

df_rent = df.loc[(df.loc[:, "own_rent"] == "Rent")]
df_own = df.loc[(df.loc[:, "own_rent"] == "Own")]                               

df_rent_stats = df_rent.describe()
df_own_stats = df_own.describe()

df_rent_count = len(df_rent)
df_own_count = len(df_own)

#%% find the unique categories of each column, nans excluded

# renters
df_rent_columns = df_rent.drop(["PermNum", "own_rent","mortgagerent"], axis = 1).columns # drop unneeded columns
rent_column_categories = {df_rent_columns[i]: 
                          sorted(df_rent[df_rent_columns[i]].unique()
                          [~pd.isnull(df_rent[df_rent_columns[i]].unique())])
                          for i in range(len(df_rent_columns))
                          }

# owners
df_own_columns = df_own.drop(["PermNum", "own_rent", "mortgagerent"], axis = 1).columns # drop unneeded columns
own_column_categories = {df_own_columns[i]: 
                         sorted(df_own[df_own_columns[i]].unique()
                         [~pd.isnull(df_own[df_own_columns[i]].unique())])
                         for i in range(len(df_own_columns))
                         }

#%% create df for categories in df_rent and count occurences

hometype = sorted(rent_column_categories.get("hometype"))
hometype_df = df_rent.loc[(df_rent.loc[:, "hometype"] == "Single family detached home")]
hometype_counts = {type: len(df_rent.loc[(df_rent.loc[:, "hometype"] == type)]) for type in hometype}

age18_64 = sorted(rent_column_categories.get("age18_64"))
age18_64_df = df_rent.loc[(df_rent.loc[:, "age18_64"] == 2)]
age18_64_counts = {type: len(df_rent.loc[(df_rent.loc[:, "age18_64"] == type)]) for type in age18_64}

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
    
#%% function to plot renter vs. owner

# compare renter vs. buyer in same chart
def bar_plotter(column, path=None):
    
    rent_category = list(rent_data_dict[f"{column}"].keys())
    rent_values = list(rent_data_dict[f"{column}"].values())
    
    own_category = list(own_data_dict[f"{column}"].keys())
    own_values = list(own_data_dict[f"{column}"].values())
    
    # adjust values for uneven x-axis categories by adding zeroes
    def pad_array(vals, target_len):
        return np.pad(vals, (0, target_len - len(vals)), mode = "constant")
    
    max_len = max(len(rent_values), len(own_values))
    padded_rent_values = pad_array(rent_values, max_len)
    padded_own_values = pad_array(own_values, max_len)
    
    # concatenate categories
    categories = sorted(list(set( rent_category + own_category )))
    
    # set fig, ax parameters
    x_axis = np.arange(len(categories))
    width = 0.4
    fig, ax = plt.subplots()
    
    # plot owner and renter plots next to each other on same chart
    plt.bar(x_axis - width/2, padded_rent_values, width, color = "darkgreen", label = "Renter")
    plt.bar(x_axis + width/2, padded_own_values, width, color = "maroon", label = "Owner")
    
    for i, cat in enumerate(categories):
        text = ax.text(i, -200, cat, ha = "center", va = "top") # set alignment and position for x labels
        
        # rotate x label if length overlaps with other labels
        if len (cat) > 12: # if any over len
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
    
    if path:
        fig.tight_layout()
        plt.savefig(os.path.join(save_path, f"{column}_own_rent_plot.jpeg"))
    
    #plt.show() # uncomment to print plots to console
    #plt.clf()

#%% create plots for each column and export

all_columns = sorted(list(set(list(df_rent_columns) + list(df_own_columns))))

# save as image to folder in cwd
save_folder = r"home_demographics_30jan2024_plots\own_rent_counts"
save_path = os.path.join(path, save_folder)

for column in all_columns:
    
    bar_plotter(f"{column}", save_path) # call plotting function on each column

#%% plot normalized data



#%% stats

#df_rent.groupby(by = "hometype").mean()

