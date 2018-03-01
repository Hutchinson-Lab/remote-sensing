/**
 *  Displays NLCD 2011 and NAIP 2011
 *  ================================================
 * **Author**: Laurel Hopkins
 * **Date**:   Oct 2017
 */

//NLCD - 2011
var landCover = ee.Image('USGS/NLCD/NLCD2011')
  .select('landcover');
print("nlcd: ", landCover);

//NAIP - 2011
var naip = ee.ImageCollection('USDA/NAIP/DOQQ')
  .filterDate('2011-01-01', '2011-12-01')
  .reduce(ee.Reducer.median())
  .visualize();
print ("naip: ", naip);

Map.setCenter(-123.28, 44.56, 14);
Map.addLayer(landCover, {}, 'NLCD');
Map.addLayer(naip, {}, 'NAIP');


