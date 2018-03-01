/**
 *  Displays and exports NLCD 2011 and NAIP 2011
 *  ================================================
 * **Author**: Laurel Hopkins
 * **Date**:   Oct 2017
 */

// Natoinal Agriculture Imagery Program
var naip = ee.ImageCollection('USDA/NAIP/DOQQ')
  .filterDate('2011-01-01', '2011-12-01')
  .reduce(ee.Reducer.median())
  .visualize();
print ("naip: ", naip);

// USGS Land Cover
var landCover = ee.Image('USGS/NLCD/NLCD2011')
  .select('landcover');
print("nlcd: ", landCover);

var scale = 30;

Map.setCenter(-123.28, 44.56, 14);
Map.addLayer(naip, {}, 'NAIP');
Map.addLayer(landCover, {}, 'NLCD');


var _point = ee.Geometry.Point(-118.55, 36.46);
print('point: ', _point);
var region = _point.buffer(200).bounds();
print('region: ', region);

var landCover_class = landCover.reduceRegion(ee.Reducer.mode(), ee.Geometry(region), scale);
print('NLCD class: ', landCover_class);


// Export NAIP image
Export.image.toDrive({
  image: naip,
  description: 'test_naip',
  dimensions: "224x224",
  region: region
});


// Export NLCD image
Export.image.toDrive({
  image: landCover,
  description: 'test_nlcd',
  dimensions: "224x224",
  region: region
});
