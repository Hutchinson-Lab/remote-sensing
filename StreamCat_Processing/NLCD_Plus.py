# -*- coding: utf-8 -*-
"""
Created on Thu Dec  6 12:04:20 2018

Recode NLCD 2011 raster to incorporate mines, dams and create an NLCD_Plus raster

@author: mweber
"""


import geopandas as gpd
from subprocess import call
import rasterio
from datetime import datetime as dt

nlcd = "H:/WorkingData/nlcd2011.tif"
coalmines = "L:/Priv/CORFiles/Geospatial_Library/Data/Project/StreamCat/LandscapeRasters/QAComplete/USTRAT.shp"
mines = "L:/Priv/CORFiles/Geospatial_Library/Data/Project/StreamCat/LandscapeRasters/QAComplete/mines.shp"
dams = "L:/Priv/CORFiles/Geospatial_Library/Data/Project/StreamCat/LandscapeRasters/QAComplete/NABD.shp"

# open point shapefiles 
coalmines = gpd.read_file(coalmines)
mines = gpd.read_file(mines)
dams = gpd.read_file(dams)

list(mines)
mines.state_loca.unique()

# restrict mines and dams to CONUS (coalmines already is)
excluded = ['Alaska','Hawaii']
mines = mines[~mines['state_loca'].isin(excluded)]
mines.plot()

list(dams)
dams.State.unique()
dams = dams[dams.State.notnull()]
dams = dams[dams.State != 'HI']
dams.plot()

# Add dummy field with value of 1 for each shapefile
coalmines['junk'] = 4
mines['junk'] = 5
dams['junk'] = 6

rast = rasterio.open(nlcd)
if not coalmines.crs == rast.crs:    
    coalmines = coalmines.to_crs(rast.crs)
if not mines.crs == rast.crs:    
    mines = mines.to_crs(rast.crs)
if not dams.crs == rast.crs:    
    dams = dams.to_crs(rast.crs)    

rast.close()

# Write out modified point shapefiles in correct projection with dummy attribute fields to burn into nlcd raster
coalmines.to_file('H:/WorkingData/coalmines.shp')
mines.to_file('H:/WorkingData/mines.shp')
dams.to_file('H:/WorkingData/dams.shp')
    
# burn each shapefile into nlcd
resamp_string = 'gdal_rasterize -a junk -l dams H:/WorkingData/dams.shp H:/WorkingData/nlcd2011.tif'
startTime = dt.now()
call(resamp_string)
print "elapsed time " + str(dt.now()-startTime)

resamp_string = 'gdal_rasterize -a junk -l mines H:/WorkingData/mines.shp H:/WorkingData/nlcd2011.tif'
startTime = dt.now()
call(resamp_string)
print "elapsed time " + str(dt.now()-startTime)

resamp_string = 'gdal_rasterize -a junk -l coalmines H:/WorkingData/coalmines.shp H:/WorkingData/nlcd2011.tif'
startTime = dt.now()
call(resamp_string)
print "elapsed time " + str(dt.now()-startTime)

 
                        