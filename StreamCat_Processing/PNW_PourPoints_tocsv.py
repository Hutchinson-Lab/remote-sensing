# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 16:34:35 2018

@author: mweber

Purpose: Generate a .csv of randomly sampled NHDPlus catchment pour points for the PNW HydroRegion

    1) Generate a table of x,y coordinates for endpoints of NHDPlus flowlines
    2) Add the coordinates for these downstream nodes to table of NHDPlus catchments for PNW
    3) Subset table of catchments to just those with matching flowline endpoints (drops 'sink' catchments)
    4) This will yield a table of NHDPlus catchment pour points
"""
import pandas as pd
import geopandas as gpd
from geopandas.geoseries import Point

flowlines = gpd.GeoDataFrame.from_file("H:/NHDPlusV21/NHDPlusPN/NHDPlus17/NHDSnapshot/Hydrography/NHDFlowline.shp")
catchments = gpd.GeoDataFrame.from_file("H:/NHDPlusV21/NHDPlusPN/NHDPlus17/NHDPlusCatchment/Catchment.shp")


for index,row in flowlines.iterrows(): 
    if row[flowlines._geometry_column_name].geom_type != 'LineString': 
        print(row['COMID'])
        
flowlines.loc[flowlines['COMID'] == 947050377, 'geometry']
flowlines = flowlines[flowlines.COMID != 947050377].copy(deep = True)
COMs = flowlines['COMID']
endpts = gpd.GeoSeries([Point(list(pt['geometry'].coords)[-1]) for i,pt in flowlines.iterrows()])
endpts = gpd.GeoDataFrame(endpts)
endpts = endpts.rename(columns={0:'geometry'}).set_geometry('geometry')
# Bring in the COMIDs from original flowlines
result = pd.concat([endpts, COMs], axis=1, ignore_index=True) 
result = result[[1,0]]
result = gpd.GeoDataFrame(result)
result = result.rename(columns={1: 'COMID', 0: 'geometry'}).set_geometry('geometry')
result.to_file("H:/WorkingData/Junk/result_test.shp") # just to check results

# restrict to catchment endpoints
result = result[result['COMID'].isin(catchments['FEATUREID'])].dropna()
result["Lon"] = result.centroid.map(lambda p: p.x)
result["Lat"] = result.centroid.map(lambda p: p.y)
result = result[['COMID','Lat','Lon']]
# Random sample
result = result.sample(2000)

result_coms = catchments[catchments['FEATUREID'].isin(result['COMID'])]
result.to_csv('H:/WorkingData/PNW_PourPoints.csv', index=False)
result_coms.to_file('H:/WorkingData/PNW_PourPoints_Cats.shp')

# generate centroids and then boxes around centroids, then export and use this for extracting GEE Landsat
pnw_cats = gpd.GeoDataFrame.from_file('C:/Users/mweber/GitProjects/remote-sensing/PNW_PourPoints_Cats.shp')
pnw_centroids = pnw_cats.copy()
def getXY(pt):
    return (pt.x, pt.y)
pnw_centroids['geometry'] = pnw_centroids['geometry'].centroid
x,y = [list(t) for t in zip(*map(getXY,pnw_centroids['geometry']))]
pnw_centroids['Lat'] = x
pnw_centroids['Lon'] = y
pnw_centroids['ID']= 'LS7_' + pnw_centroids['FEATUREID'].astype(str)
pnw_centroids = pnw_centroids[['ID','Lat','Lon','geometry']]
pnw_centroids.to_file("C:/Users/mweber/GitProjects/remote-sensing/PNW_Centroids.shp")
pnw_centroids = pd.DataFrame(pnw_centroids.drop(columns='geometry'))
pnw_centroids.to_csv("C:/Users/mweber/GitProjects/remote-sensing/PNW_Centroids.csv", index=False)

# apply planar CRS
pnw_centroids.crs
pnw_centroids = pnw_centroids.to_crs(epsg=5070)

# create 'box' buffer
pnw_buffer = pnw_centroids.copy()
help(gpd.GeoSeries.buffer) # GeoPandas doesn't fully parameterize shapely options
import shapely
pnw_buffer['geometry'] = pnw_buffer['geometry'].buffer(1400, cap_style=3)
pnw_buffer = pnw_buffer.to_crs(epsg=4326)
pnw_buffer.to_file("C:/Users/mweber/GitProjects/remote-sensing/PNW_Cat_Centroid_Sq_Bufs.shp")
