#%%
import os
import pandas as pd
import numpy as np
import geopandas as gpd
import fiona as fi
import cartopy
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

#%% set Spyder working folder to file location: \NEB Decarb - General\Datasets\

datasets_path = os.getcwd()

#%% open census county shape file data into df (2020)
# https://www.census.gov/cgi-bin/geo/shapefiles/index.php

shp_path = r"CensusGeographyData\Census_2020_US_County\tl_2020_us_county.shp"
shp_filepath = os.path.join(datasets_path, shp_path)
shp_df = gpd.read_file(shp_filepath)
shp_df = shp_df.to_crs("ESRI:102039")

#%% clean data and slice county geometry by CONUS, AK, and HI
# USA county GEO ID's range from 0500000US01001 to 0500000US56045, excludes other US-owned territories

# take the GEOID's and geometry from the shapefile data
gdf1 = shp_df[["GEOID", "geometry"]].sort_values("GEOID").reset_index(drop=True)
USA_slice = gdf1["GEOID"].ge("01001") & gdf1["GEOID"].le("56045") # take just the USA slice
gdf1_USA = gdf1[USA_slice]

#%% open all BTS data from ArcGIS National Transportation Noise Map Excel files

noise_path = r"National Transportation Noise Map\QGIS\Final Output 2020"

def combine_noise(noise_path, CONUS=False):
    
    all_noise_files = os.listdir(noise_path)
    
    if CONUS == True:
        US_noise_files = [file for file in all_noise_files if file.endswith(".csv") and file not in ["df.alaska2020.csv", "df.hawaii.csv"]]
    else: 
        US_noise_files = [file for file in all_noise_files if file.endswith(".csv")]
    
    # combine all noise data into one df
    noise_dfs = []
    for file in US_noise_files:
        filepath = os.path.join(noise_path, file)
        df = pd.read_csv(filepath)
        df = df.fillna(0) # fill in blanks or nans with 0
        df["GEOID"] = df["GEOID"].astype(int).astype(str) # convert to string to avoid leading 0 loss
        df["GEOID"] = df["GEOID"].str.pad(5, "left", "0") # add leading 0 back
        noise_dfs.append(df)
    
    noise_combined_df = pd.concat(noise_dfs).sort_values("GEOID").reset_index(drop=True)
    
    return noise_combined_df

US_noise_combined_df = combine_noise(noise_path)
CONUS_noise_combined_df = combine_noise(noise_path, CONUS=True)


#%% create threshold columns from percent columns

def add_thresh(noise_combined_df):

    noise_combined_df["85+ Threshold"] = noise_combined_df.loc[:, "per85-90":"per>100"].sum(axis = 1)
    noise_combined_df["75+ Threshold"] = noise_combined_df.loc[:, "per75-80":"per>100"].sum(axis = 1)
    noise_combined_df["65+ Threshold"] = noise_combined_df.loc[:, "per65-70":"per>100"].sum(axis = 1)
    noise_combined_df["55+ Threshold"] = noise_combined_df.loc[:, "per55-60":"per>100"].sum(axis = 1)
    noise_combined_df["45+ Threshold"] = noise_combined_df.loc[:, "per46-50":"per>100"].sum(axis = 1)
    
    return noise_combined_df

US_noise_combined_df = add_thresh(US_noise_combined_df)
CONUS_noise_combined_df = add_thresh(CONUS_noise_combined_df)


#%% combine cleaned county geometry with noise data

US_noise_gdf = gpd.GeoDataFrame( pd.merge(US_noise_combined_df, gdf1_USA, on = "GEOID", how = "inner") ) # all US counties
CONUS_noise_gdf = gpd.GeoDataFrame( pd.merge(CONUS_noise_combined_df, gdf1_USA, on = "GEOID", how = "inner") ) # exclude AK and HI


#%% plot noise data on county geomtry map by selected column

def noise_mapper(gdf, column="mean.db"):
    
    fig, ax = plt.subplots(1, figsize = (10, 6))
    
    gdf.plot(column = column, cmap = "viridis", ax = ax, cax = ax)
    
    # add annotations to map plot
    ax.axis("off")
    ax.set_title("Average Noise by County (dBA), 2020")
    ax.annotate("Source: BTS National Transportation Noise Map, 2020", xy = (0.1, 0.08), xycoords = "figure fraction", 
                horizontalalignment = "left", verticalalignment = "top", fontsize = 12, color = "grey"
                )
    
    # create colorbar as a legend
    sm = plt.cm.ScalarMappable(cmap = "viridis",
                               norm = plt.Normalize(vmin = np.min(gdf[column]), vmax = np.max(gdf[column]))
                               )
    sm._A = [] # empty array for the data range
    cbar = fig.colorbar(sm, ax = ax) # add the colorbar to the figure
    
    return None

noise_mapper(US_noise_gdf)


#%% plot noise thresholds on counties map

def noise_threshold_map(gdf):
    
    #fig, axs = plt.subplots(2, 3, figsize = (15, 10))
    fig, axs = plt.subplots(3, 2, figsize = (9, 9))
    axs = axs.flatten()
    
    columns = ["85+ Threshold", "75+ Threshold", "65+ Threshold", "55+ Threshold", "45+ Threshold"] # changing lower threshold because 100% is in per45
    
    for i, column in enumerate(columns):

        gdf.plot(column = column, cmap = "viridis", ax = axs[i], 
                 #cax = axs[i],
                 vmin = gdf[column].min(), vmax = gdf[column].max(), legend = True)
        axs[i].axis("off")
        axs[i].set_title(f"{column} (dBA)", fontsize = 10)
    
    i = len(columns)
    gdf.plot(column = "mean.db", cmap = "viridis", ax = axs[i], 
             #cax = axs[i],
             vmin = gdf["mean.db"].min(), vmax = gdf["mean.db"].max(), legend = True)
    axs[i].axis("off")
    axs[i].set_title("Average Noise (dBA)", fontsize = 10)
    
    plt.subplots_adjust(wspace=0.1, hspace=0.3)
    
    # annotate plot
    fig.subplots_adjust(bottom = 0.12)
    fig.suptitle("Percent (%) Exceeding Noise Thresholds by County, 2020", fontsize = 12, fontweight = "bold", y = 0.95)
    fig.text(0.95, 0.02, "Source: BTS National Transportation Noise Map, 2020", ha = "right", va = "bottom", fontsize = 9, color = "grey")
    
    # create colorbar as a legend
    sm = plt.cm.ScalarMappable(cmap = "viridis"
                               # norm = plt.Normalize(vmin = np.min(gdf.loc[:, "85+ Threshold":"45+ Threshold"]), 
                               #                      vmax = np.max(gdf.loc[:, "85+ Threshold":"45+ Threshold"]) 
                               #                      )
                               )
    # sm._A = [] # empty array for the data range
    # cbar = fig.colorbar(sm, ax = axs) # add the colorbar to the figure
    
    fig.tight_layout(rect=[0, 0.04, 1, 0.93])
    
    return None


noise_threshold_map(CONUS_noise_gdf)


#%% plot noise quartiles on counties map

def noise_quartiles_map(gdf):
    
    fig, axs = plt.subplots(2, 3, figsize = (15, 10))
    axs = axs.flatten()
    
    columns = ["100%", "75%", "50%", "25%", "0%"]
    
    for i, column in enumerate(columns):

        gdf.plot(column = column, cmap = "viridis", ax = axs[i], cax = axs[i])
        axs[i].axis("off")
        axs[i].set_title(f"{column}")
    
    i = len(columns)
    gdf.plot(column = "mean.db", cmap = "viridis", ax = axs[i], cax = axs[i])
    axs[i].axis("off")
    axs[i].set_title("Average (dBA)")
    
    # annotate plo
    fig.subplots_adjust(bottom = 0.12)
    fig.suptitle("Noise Quantiles by County (in dBA), 2020")
    fig.text(0.5, 0.05, "Source: BTS National Transportation Noise Map, 2020", ha = "center", va = "bottom", fontsize = 12, color = "grey")
    
    # create colorbar as a legend
    sm = plt.cm.ScalarMappable(cmap = "viridis",
                               norm = plt.Normalize(vmin = np.min(gdf.loc[:, columns]), 
                                                    vmax = np.max(gdf.loc[:, columns]) 
                                                    )
                               )
    
    sm._A = [] # empty array for the data range
    cbar = fig.colorbar(sm, ax = axs) # add the colorbar to the figure
    
    return None


noise_quartiles_map(US_noise_gdf)


#%% TODO 
# add region column to gdf
# pull out high risk counties (>85) and match with potential STC deltas from upgrades at county level
# compare with population or households per county
# export hi-res plots function




