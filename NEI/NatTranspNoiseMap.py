#%%
import os
import geopandas as gpd
import fiona as fi
import matplotlib.pyplot as plt

#%% open gdb into a geodataframe

gdb_path = os.getcwd() # set Spyder working folder to file location
gdf = gpd.read_file(gdb_path, driver="FileGDB")

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

plt.show()
plt.clf()

#%% plot an individual layer from the gdb

def plot_layer(layer=0):
    fig, ax = plt.subplots()
    USA.plot(ax = ax, color = "white", edgecolor = "black", zorder = 0)
    layerx = gpd.read_file(gdb_path, driver = "FileGDB", layer = layer)
    layerx.plot(ax = ax, cmap = "Reds", alpha = 0.1)
    plt.show()
    plt.clf()

plot_layer(6)

#%%


