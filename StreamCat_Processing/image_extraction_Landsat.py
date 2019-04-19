"""
Downloads a satellite images to Google Drive given a list of locations

 *must first have the Google Earth Engine Python API installed and
  authenticated*
====================================================================
**Author**: Laurel Hopkins
**Modified by**: Marc Weber
**Date**:   March 2018
**Modified Date**: February 2019

IMPORTANT:
If the list exceeds 1000 locations, manually split the list into smaller batches of 1000
 where the filename includes the offset (then run script in parallel for all batches)

 ex. 3000 locations (locations.csv)
       --> locations 0-999 (locations_0.csv)
           locations 1000 - 1999 (locations_1000.csv)
           locations 2000 - 2999 (locations_2000.csv)

run: image_extraction.py [locations.csv] [locations_offset]
 ex. image_extraction.py [oregon_0c.csv] [0]
"""


import ee
from ee import batch
import csv
import re
import sys

ee.Initialize()

fc = ee.FeatureCollection("users/mweber36/NN_Testing/PNW_Cat_Centroid_Sq_Bufs")

# function to get catchment centroids - doing this in GeoPandas but left in
#def getCentroid(feature):
#    keepProperties = ['AreaSqKM','FEATUREID','GRIDCODE','SOURCEFC']
#    centroid = feature.geometry().centroid()
#    return ee.Feature(centroid).copyProperties(feature, keepProperties)
#
#centroids = fc.map(getCentroid)

featlist = fc.getInfo()["features"]
#featlist = centroids.getInfo()["features"]
#def cloudMaskL457:
#  qa = image.select('pixel_qa')
#  // If the cloud bit (5) is set and the cloud confidence (7) is high
#  // or the cloud shadow bit is set (3), then it's a bad pixel.
#  cloud = qa.bitwiseAnd(1 << 5)
#                  .and(qa.bitwiseAnd(1 << 7))
#                  .or(qa.bitwiseAnd(1 << 3));
#  // Remove edge pixels that don't occur in all bands
#  mask2 = image.mask().reduce(ee.Reducer.min());
#  return image.updateMask(cloud.not()).updateMask(mask2)

# functions used from here: https://gis.stackexchange.com/questions/274048/apply-cloud-mask-to-landsat-imagery-in-google-earth-engine-python-api
def getQABits(image, start, end, mascara):
    # Compute the bits we need to extract.
    pattern = 0
    for i in range(start,end+1):
        pattern += 2**i
    # Return a single band image of the extracted QA bits, giving the     band a new name.
    return image.select([0], [mascara]).bitwiseAnd(pattern).rightShift(start)
#A function to mask out cloudy pixels.

def maskQuality(image):
    # Select the QA band.
    QA = image.select('pixel_qa')
    # Get the internal_cloud_algorithm_flag bit.
    sombra = getQABits(QA,3,3,'cloud_shadow')
    nubes = getQABits(QA,5,5,'cloud')
    #  var cloud_confidence = getQABits(QA,6,7,  'cloud_confidence')
    cirrus_detected = getQABits(QA,9,9,'cirrus_detected')
    #var cirrus_detected2 = getQABits(QA,8,8,  'cirrus_detected2')
    #Return an image masking out cloudy areas.
    return image.updateMask(sombra.eq(0)).updateMask(nubes.eq(0).updateMask(cirrus_detected.eq(0)))

LandSat = ee.ImageCollection('LANDSAT/LE07/C01/T1_SR')\
                  .filterDate('2011-01-01', '2011-12-31')\
                  .map(maskQuality)\
                  .reduce(ee.Reducer.median())
                  
# testing if works for sample area
geometry = ee.Geometry.Rectangle([116.2621, 39.8412, 116.4849, 40.01236]);
task = batch.Export.image.toDrive(
        image=LandSat,
        description='test',
        dimensions=[224,224],
        region=featlist[0]['geometry']['coordinates'][0],
        folder='GEE'
        )

task.start()            


def collect_images(_input_file, _imgsize, _export_outputs):
    LandSat = ee.ImageCollection('LANDSAT/LE07/C01/T1_SR')\
        .filterDate('2011-01-01', '2011-12-31')\
        .map(maskQuality)\
        .reduce(ee.Reducer.median())
    for feat in featlist:
        desc = 'LS7' +'_' + str(feat['properties']['FEATUREID'])
        try:
			#extract images
			# Landsat7
            task = ee.batch.Export.image.toDrive(
				image=LandSat,
				description= desc,
				dimensions=_imgsize,
#                scale = _scale,
				region=feat['geometry']['coordinates'],               
				folder='GEE'  # 'GEE/NAIP_image'
			)
            task.start()
            state = task.status()['state']
            while state in ['READY', 'RUNNING']:
                if export_outputs:
                    print(state + '...')
				# print task.status()
                state = task.status()['state']
            if task.status()['state'] == 'COMPLETED':
                print('Landsat image ' + desc + ' done')
            else:
                print('Landsat image ' + desc +' failed')
                print(task.status())
        except:
            print('Landsat image ' + desc)
    print('Finished exporting images!')


if __name__ == '__main__':
	# https://fusiontables.google.com/data?docid=1n-XWd5KgdVGGKRaw-XVkerYL3xM2BZwXY1bQEhqF#rows:id=1

#	'EXPORT IMAGES'
	_input_file = ee.FeatureCollection("users/mweber36/NN_Testing/PNW_Cat_Centroid_Sq_Bufs")

#	'IMAGE PARAMETERS'
	_imgsize = [224, 224]
#    _scale = 30


	# enable export outputs [READY/RUNNING]
	_export_outputs = True

#	collect_images(_input_file, _imgsize, _export_outputs)
    collect_images(_input_file, _scale, _export_outputs)
