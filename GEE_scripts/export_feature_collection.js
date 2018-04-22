/**
 *  Export a list of locations as a list of feature collections 
 *  ================================================
 * **Author**: Laurel Hopkins
 * **Date**:   March 2018
 */

//Example fusion table with test locations
// https://fusiontables.google.com/DataSource?docid=1fExKVvpaWAeoZmVbi9mR3uq1gm7ztQ6_KWjJPj7U#map:id=3

var locations = ee.FeatureCollection('ft:1fExKVvpaWAeoZmVbi9mR3uq1gm7ztQ6_KWjJPj7U');
print(locations);
Map.addLayer(locations, {color: 'FF0000'}, 'points');

Export.table.toDrive ({  
    collection : locations,
    folder : 'GEE/csv',
    fileNamePrefix : 'test points',
    fileFormat : 'CSV'
  });
