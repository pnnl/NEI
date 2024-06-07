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

datsets_path = os.getcwd()

#%% set gpd map projection to USA

world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres")) # get world map
USA = world[(world["name"] == "United States of America")] # set to just the US
USA = USA.to_crs("ESRI:102039") # reproject the coordinates to match the noise data

#%% open census county shape file data into df
# https://www.census.gov/cgi-bin/geo/shapefiles/index.php

shp_path = r"CensusPopulationEstimates\Census_2023_US_County\tl_2023_us_county.shp"
shp_filepath = os.path.join(datsets_path, shp_path)
shp_df = gpd.read_file(shp_filepath)
shp_df = shp_df.to_crs("ESRI:102039")

#%% clean data and combine county geometry with noise data
# USA county GEO ID's range from 0500000US01001 to 0500000US56045, excludes other US-owned territories

# take the GEO_ID's and geometry from the shapefile data
gdf1 = shp_df[["GEOIDFQ", "geometry"]].sort_values("GEOIDFQ").reset_index(drop=True)
gdf1.rename(columns = {"GEOIDFQ": "GEO_ID"}, inplace = True)
USA_slice = gdf1["GEO_ID"].ge("0500000US01001") & gdf1["GEO_ID"].le("0500000US56045")
gdf1_USA = gdf1[USA_slice]

#%% open one National Transportation Noise Map Excel file for New England

NE_noise_path = r"National Transportation Noise Map\ArcGIS\Final Excel Spreadsheets (All Stats)\RRA_New_England_CB_STAT.xls" 
NE_noise_filepath = os.path.join(datsets_path, NE_noise_path)
NE_noise_df = pd.read_excel(NE_noise_filepath)

#NE_noise_df = NE_noise_df[["AFFGEOID", "Average dBA"]] # take geoID and noise thresholds
NE_noise_df = NE_noise_df[["Count", "AFFGEOID", "Average dBA", 
                           "45 dBA count", "46-50 dBA count", "51-55 dBA count", "56-60 dBA count", "61-65 dBA count", 
                           "66-70 dBA count", "71-75 dBA count", "76-80 dBA count", "81-85 dBA count", "86-90 dBA count", 
                           "91-95 dBA count", "95-100 dBA count", "101+ dBA count"]]

NE_noise_df.rename(columns = {"AFFGEOID": "GEO_ID"}, inplace = True)


#%% create threshold columns manually
# county counts do not align with dBA counts totals

thresh_85 = ["86-90 dBA count", "91-95 dBA count", "95-100 dBA count", "101+ dBA count"]
NE_noise_df["85+ Threshold"] = NE_noise_df[thresh_85].sum(axis = 1) / (NE_noise_df["Count"] * 0.01)

thresh_75 = ["76-80 dBA count", "81-85 dBA count", "86-90 dBA count", "91-95 dBA count", "95-100 dBA count", "101+ dBA count"]
NE_noise_df["75+ Threshold"] = NE_noise_df[thresh_75].sum(axis = 1) / (NE_noise_df["Count"] * 0.01)

thresh_65 = ["66-70 dBA count", "71-75 dBA count", "76-80 dBA count", "81-85 dBA count", "86-90 dBA count", "91-95 dBA count", 
             "95-100 dBA count", "101+ dBA count"]
NE_noise_df["65+ Threshold"] = NE_noise_df[thresh_65].sum(axis = 1) / (NE_noise_df["Count"] * 0.01)

thresh_55 = ["56-60 dBA count", "61-65 dBA count","66-70 dBA count", "71-75 dBA count", "76-80 dBA count", "81-85 dBA count", 
             "86-90 dBA count", "91-95 dBA count", "95-100 dBA count", "101+ dBA count"]
NE_noise_df["55+ Threshold"] = NE_noise_df[thresh_55].sum(axis = 1) / (NE_noise_df["Count"] * 0.01)

thresh_45 = ["45 dBA count", "46-50 dBA count", "51-55 dBA count", "56-60 dBA count", "61-65 dBA count", "66-70 dBA count", 
             "71-75 dBA count", "76-80 dBA count", "81-85 dBA count", "86-90 dBA count", "91-95 dBA count", "95-100 dBA count", "101+ dBA count"]
NE_noise_df["45+ Threshold"] = NE_noise_df[thresh_45].sum(axis = 1) / (NE_noise_df["Count"] * 0.01)


#%% create threshold columns from percent columns




#%% open all BTS data from ArcGIS National Transportation Noise Map Excel files

noise_path = r"National Transportation Noise Map\ArcGIS\Final Excel Spreadsheets (All Stats)"
all_noise_files = os.listdir(noise_path)
CONUS_noise_files = [file for file in all_noise_files if file not in ["RRA_AK_CB_Stat.xls", "RRA_HI_Stat.xls"]]

#%% combine all noise data into one df

noise_dfs = []
for file in all_noise_files:
    filepath = os.path.join(noise_path, file)
    df = pd.read_excel(filepath)
    df = df[["AFFGEOID", "Average dBA"]]
    df.rename(columns = {"AFFGEOID": "GEO_ID"}, inplace = True)
    noise_dfs.append(df)

noise_combined_df = pd.concat(noise_dfs).sort_values("GEO_ID").reset_index(drop=True)

noise_no_0_df = noise_combined_df.replace(0, pd.NA, inplace = True)
noise_combined_df.dropna()


#%% combine cleaned county geometry with noise data

noise_gdf = gpd.GeoDataFrame( pd.merge(noise_combined_df, gdf1_USA, on = "GEO_ID", how = "inner") ) # all counties

NE_noise_gdf = gpd.GeoDataFrame( pd.merge(NE_noise_df, gdf1_USA, on = "GEO_ID", how = "inner") ) # New England

# create list of counties with missing info
missing_geometry = noise_gdf[noise_gdf["geometry"].isna()]


#%% plot average noise data on county geomtry map

def noise_mapper(gdf):
    
    fig, ax = plt.subplots(1, figsize = (10, 6))
    
    gdf.plot(column = "Average dBA", cmap = "viridis", ax = ax, cax = ax)
    
    # add annotations to map plot
    ax.axis("off")
    ax.set_title("Average Noise by County (dBA), 2020")
    ax.annotate("Source: BTS National Transportation Noise Map, 2020", xy = (0.1, 0.08), xycoords = "figure fraction", 
                horizontalalignment = "left", verticalalignment = "top", fontsize = 12, color = "grey"
                )
    
    # create colorbar as a legend
    sm = plt.cm.ScalarMappable(cmap = "viridis",
                               norm = plt.Normalize(vmin = np.min(gdf["Average dBA"]), vmax = np.max(gdf["Average dBA"]))
                               )
    sm._A = [] # empty array for the data range
    cbar = fig.colorbar(sm, ax = ax) # add the colorbar to the figure
    
    return None

noise_mapper(NE_noise_gdf)


#%% plot noise thresholds on counties map

fig, axs = plt.subplots(2, 3, figsize = (15, 10))
axs = axs.flatten()

NE_noise_gdf.plot(column = "85+ Threshold", cmap = "viridis", ax = axs[0], cax = axs[0])
axs[0].axis("off")
axs[0].set_title("85+ Threshold (dBA)")

NE_noise_gdf.plot(column = "75+ Threshold", cmap = "viridis", ax = axs[1], cax = axs[1])
axs[1].axis("off")
axs[1].set_title("75+ Threshold (dBA)")

NE_noise_gdf.plot(column = "65+ Threshold", cmap = "viridis", ax = axs[2], cax = axs[2])
axs[2].axis("off")
axs[2].set_title("65+ Threshold (dBA)")

NE_noise_gdf.plot(column = "55+ Threshold", cmap = "viridis", ax = axs[3], cax = axs[3])
axs[3].axis("off")
axs[3].set_title("55+ Threshold (dBA)")

NE_noise_gdf.plot(column = "45+ Threshold", cmap = "viridis", ax = axs[4], cax = axs[4])
axs[4].axis("off")
axs[4].set_title("45+ Threshold (dBA)")

NE_noise_gdf.plot(column = "Average dBA", cmap = "viridis", ax = axs[5], cax = axs[5])
axs[5].axis("off")
axs[5].set_title("Average Noise (dBA)")

# annotate plot
fig.subplots_adjust(bottom = 0.12)
fig.suptitle("Percent (%) Exceeding Noise Thresholds by County, 2020")
fig.text(0.5, 0.05, "Source: BTS National Transportation Noise Map, 2020", ha = "center", va = "bottom", fontsize = 12, color = "grey")

# create colorbar as a legend
sm = plt.cm.ScalarMappable(cmap = "viridis",
                           norm = plt.Normalize(vmin = np.min(NE_noise_gdf.loc[:, "85+ Threshold":"45+ Threshold"]), 
                                                vmax = np.max(NE_noise_gdf.loc[:, "85+ Threshold":"45+ Threshold"]) 
                                                )
                           )
sm._A = [] # empty array for the data range
cbar = fig.colorbar(sm, ax = axs) # add the colorbar to the figure



#%% plot layers from gdb on top of CONUS projection

# layers = fi.listlayers(gdb_path) # get a list of layers in the .gdb file

# fig, ax = plt.subplots()
# USA.plot(ax = ax, color = "white", edgecolor = "black", zorder = 0) # plot map projection

# i = 1
# for layer in layers:
#     noise = gpd.read_file(gdb_path, driver = "FileGDB", layer = layer) # read each layer in the gdb
#     noise.plot(ax = ax, color = "green", alpha = 0.05, zorder = i) # plot layer ontop of map
#     i += 1

#plt.show()
#plt.clf()

#%% plot an individual layer from the gdb

# def plot_layer(layer=0):
#     fig, ax = plt.subplots()
#     USA.plot(ax = ax, color = "white", edgecolor = "black", zorder = 0)
#     layerx = gpd.read_file(gdb_path, driver = "FileGDB", layer = layer)
#     layerx.plot(ax = ax, cmap = "Reds", alpha = 0.1)
#     #plt.show()
#     #plt.clf()

# plot_layer(6)


#%% try opening geodatabase with fiona

# with fi.open(gbd_filepath) as src:
#     crs = src.meta['crs'] # Get the coordinate reference system (CRS)
#     schema = src.schema # Get the metadata about the features
#     feature_list = [] # Create an empty list to store features
    
#     for feat in src:
#         feature_list.append(feat) # Append each feature to the list
        
# gdf = gpd.GeoDataFrame.from_features(feature_list) # Convert the list to a GeoDataFrame

#%% create cartopy natural earth map projection of US

projection = ccrs.AlbersEqualArea(central_longitude=-96, central_latitude=23)
extent = [-125, -66.5, 20, 50]

fig = plt.figure(figsize=[10, 6])
ax = plt.axes([0, 0, 1, 1], projection=projection)
ax.coastlines()
ax.add_feature(cartopy.feature.LAND, facecolor='lightgray')
ax.set_extent(extent)

#%%


