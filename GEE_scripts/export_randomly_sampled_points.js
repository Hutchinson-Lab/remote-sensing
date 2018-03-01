/**
 *  Creates a random sample of points given a region
 *  ================================================
 * **Author**: Laurel Hopkins
 * **Date**:   Oct 2017
 */


//Fusion table with all US states
// https://fusiontables.google.com/data?docid=1fRY18cjsHzDgGiJiS2nnpUU3v9JPDc2HNaR7Xk8#rows:id=1

var states = ee.FeatureCollection('ft:1fRY18cjsHzDgGiJiS2nnpUU3v9JPDc2HNaR7Xk8');
var oregon = states.filter(ee.Filter.eq('Name', 'Oregon'));
Map.setCenter(-120.47, 44.09, 6);
Map.addLayer(oregon, {'color' : 'FF0000'});

//uniformly create random points within region
var num_points = 5000;
var seed = Math.floor(Math.random()*1000000);
print('seed: ' + seed);
var points = ee.FeatureCollection.randomPoints(oregon, num_points, seed);
print('Points', points);
Map.addLayer(points);

Export.table.toDrive ({
    collection : points,
    folder : 'GEE/csv',
    fileNamePrefix : 'oregon_' + num_points.toString(),
    fileFormat : 'CSV'
  });