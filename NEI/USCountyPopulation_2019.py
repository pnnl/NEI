#%%
import os
import pandas as pd
import numpy as np
import geopandas as gpd
import geodatasets
import matplotlib.pyplot as plt

#%% set Spyder working folder to file location: \NEB Decarb - General\Datasets\
datsets_path = os.getcwd() 

#%% open census county shape file data into df
# https://www.census.gov/cgi-bin/geo/shapefiles/index.php

shp_path = r"CensusPopulationEstimates\Census_2023_US_County\tl_2023_us_county.shp"
shp_filepath = os.path.join(datsets_path, shp_path)
shp_df = gpd.read_file(shp_filepath)
shp_df = shp_df.to_crs("ESRI:102039")

#%% open census county population data into df
# data.census.gov population estimates annual for 2019

pop_path = r"CensusPopulationEstimates\PopulationEstimatesByCounty\PopulationEstimatesByCounty_Table.csv"
pop_filepath = os.path.join(datsets_path, pop_path)
pop_df = gpd.read_file(pop_filepath)

#%% clean data and combine county geometry with population data
# USA county GEO ID's range from 0500000US01001 to 0500000US56045, excludes other US-owned territories

# take the GEO_ID's and geometry from the shapefile data
gdf1 = shp_df[["GEOIDFQ", "geometry"]].sort_values("GEOIDFQ").reset_index(drop=True)
gdf1.rename(columns = {"GEOIDFQ": "GEO_ID"}, inplace = True)
USA_slice = gdf1["GEO_ID"].ge("0500000US01001") & gdf1["GEO_ID"].le("0500000US56045")
gdf1_USA = gdf1[USA_slice]

# take the GEO info and the population data from the population estimates dataset
gdf2 = pop_df[["GEO_ID", "NAME", "DATE_CODE", "DATE_DESC", "POP"]].sort_values("GEO_ID").reset_index(drop=True)
gdf2_2019 = gdf2.loc[( gdf2.loc[:, "DATE_CODE"] == "12" )].reset_index(drop=True)
USA_slice = gdf2_2019["GEO_ID"].ge("0500000US01001") & gdf2_2019["GEO_ID"].le("0500000US56045")
gdf2_2019_USA = gdf2_2019[USA_slice]
gdf2_2019_USA["POP"] = pd.to_numeric(gdf2_2019_USA["POP"])

# combine cleaned dataframes into one geodataframe
county_population_gdf = gpd.GeoDataFrame( pd.merge(gdf2_2019_USA, gdf1_USA, on = "GEO_ID", how = "inner") )

# create list of counties with missing info
missing_geometry = county_population_gdf[county_population_gdf["geometry"].isna()]

#%% plot population estimates data on county geomtry map

fig, ax = plt.subplots(1, figsize = (10, 6))
vmax = 1000000 # set the max population per county to plot
county_population_gdf.plot(column = "POP", cmap = "viridis", vmax = vmax, ax = ax, cax = ax)

# add annotations to map plot
ax.axis("off")
ax.set_title("Population (in millions) by County, 2019")
ax.annotate("Source: U.S. Census, 2019", xy = (0.1, 0.08), xycoords = "figure fraction", 
            horizontalalignment = "left", verticalalignment = "top", fontsize = 12, color = "grey"
            )

# Create colorbar as a legend
sm = plt.cm.ScalarMappable(cmap = "viridis",
                           norm = plt.Normalize(vmin = np.min(gdf2_2019_USA["POP"]), vmax = vmax)
                           )
sm._A = [] # empty array for the data range
cbar = fig.colorbar(sm, ax = ax) # add the colorbar to the figure

# save plot and export
save_path = r"CensusPopulationEstimates"
save_filepath = os.path.join(datsets_path, save_path)
fig.savefig(os.path.join(save_filepath, "US_Population_County_2019.png"), dpi = 300)

#%% 

