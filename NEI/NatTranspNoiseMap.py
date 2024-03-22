#%%
import os
import geopandas as gpd
import fiona as fi
import cartopy
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

#%% open noise geodatabase into a geodataframe

datsets_path = os.getcwd() # set Spyder working folder to file location: \NEB Decarb - General\Datasets\
gdb_path = r"National Transportation Noise Map\CONUS_rail_road_and_aviation_noise_2020\CONUS_rail_road_and_aviation_noise_2020\CONUS_rail_road_and_aviation_noise_2020.gdb"
gbd_filepath = os.path.join(datsets_path, gdb_path)
gdf = gpd.read_file(gbd_filepath, driver="FileGDB")

#%% set map projection to USA

world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres")) # get world map
USA = world[(world["name"] == "United States of America")] # set to just the US
USA = USA.to_crs("ESRI:102039") # reproject the coordinates to match the noise data
    
#%% plot layers from gdb on top of CONUS projection

layers = fi.listlayers(gdb_path) # get a list of layers in the .gdb file

fig, ax = plt.subplots()
USA.plot(ax = ax, color = "white", edgecolor = "black", zorder = 0) # plot map projection

i = 1
for layer in layers:
    noise = gpd.read_file(gdb_path, driver = "FileGDB", layer = layer) # read each layer in the gdb
    noise.plot(ax = ax, color = "green", alpha = 0.05, zorder = i) # plot layer ontop of map
    i += 1

#plt.show()
#plt.clf()

#%% plot an individual layer from the gdb

def plot_layer(layer=0):
    fig, ax = plt.subplots()
    USA.plot(ax = ax, color = "white", edgecolor = "black", zorder = 0)
    layerx = gpd.read_file(gdb_path, driver = "FileGDB", layer = layer)
    layerx.plot(ax = ax, cmap = "Reds", alpha = 0.1)
    #plt.show()
    #plt.clf()

plot_layer(6)


#%% try opening geodatabase with fiona

with fi.open(gbd_filepath) as src:
    crs = src.meta['crs'] # Get the coordinate reference system (CRS)
    schema = src.schema # Get the metadata about the features
    feature_list = [] # Create an empty list to store features
    
    for feat in src:
        feature_list.append(feat) # Append each feature to the list
        
gdf = gpd.GeoDataFrame.from_features(feature_list) # Convert the list to a GeoDataFrame

#%% create cartopy natural earth map projection of US

projection = ccrs.AlbersEqualArea(central_longitude=-96, central_latitude=23)
extent = [-125, -66.5, 20, 50]

fig = plt.figure(figsize=[10, 6])
ax = plt.axes([0, 0, 1, 1], projection=projection)
ax.coastlines()
ax.add_feature(cartopy.feature.LAND, facecolor='lightgray')
ax.set_extent(extent)

#%%

gdf.geometry.boundary.plot(ax=ax, edgecolor='black', alpha=0.5)
gdf[0]
