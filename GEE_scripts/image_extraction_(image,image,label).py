"""
Downloads a triple (satellite image, labeled image, majority label) in the
 form of (image, image, scalar) to Google Drive given a list of locations

 *must first have the Google Earth Engine Python API installed and
  authenticated*
====================================================================
**Author**: Laurel Hopkins
**Date**:   Oct 2017

IMPORTANT:
If the list exceeds 1000 locations, manually split the list into smaller batches of 1000
 where the filename includes the offset (the run script in parallel for all batches)

 ex. 3000 locations (locations.csv)
       --> locations 0-999 (locations_0.csv)
           locations 1000 - 1999 (locations_1000.csv)
           locations 2000 - 2999 (locations_2000.csv)

run: image_extraction.py [locations.csv] [locations_offset]
 ex. image_extraction.py [oregon_0c.csv] [0]

"""


import ee
import csv
import re
import sys

ee.Initialize()


def collect_images(filename, width, scale, offset, imgsize, nlcd_filename, naip_filename, nlcd_folder, naip_folder, export_outputs):

	# NLCD image
	landCover = ee.Image('USGS/NLCD/NLCD2011') \
		.select('landcover')

	# NAIP image
	NAIP = ee.ImageCollection('USDA/NAIP/DOQQ')\
		.filterDate('2011-01-01', '2011-12-01')\
		.reduce(ee.Reducer.median())

	NAIP_vis = NAIP.visualize()  # takes first three bands (R,G,B)

	ft_points = []
	letter = filename[-5]
	with open('oregon_points/' + filename, 'rb') as csvfile:
		record = csv.reader(csvfile)
		for row in record:
			point_index = row[0]
			feature = row[1]
			coords = re.search('"coordinates":(.+?)}', feature)
			if coords:
				found = coords.group(1)
				found = found[1:-1].split(',')
				ft_points += [[point_index, (round(float(found[0]), 6), round(float(found[1]), 6))]]

	# calculate labels and export images
	count, exported_images = 0, 0
	num_points = len(ft_points)

	# save nlcd_labels for classification
	with open('NLCD_labels_' + str(offset) + letter + '.csv', 'ab') as nlcd_csv, open('delete_coordinates_' + str(offset) + letter + '.csv', 'ab') as delete_csv:
		nlcd_writer = csv.writer(nlcd_csv)
		delete_writer = csv.writer(delete_csv)

		total_points = num_points + offset - 1

		for set in ft_points:
			index, point = set[0], set[1]
			_long, _lat = point[0], point[1]
			image_index = count + offset

			try:
				point = ee.Geometry.Point(_long, _lat)
				buffered_point = point.buffer(width / 2).bounds()
				print 'Creating buffered feature ' + str(image_index) + ' of ' + str(total_points)

				# Collect NLCD landcover classifications from most recent year (2011)
				# Create polygon for selected region
				f1 = buffered_point.getInfo()
				f1 = f1['coordinates'][0]
				_poly = ee.Geometry.Polygon([f1])
				landCover_mode = landCover.reduceRegion(ee.Reducer.mode(), _poly, scale)
				mode_dict = landCover_mode.getInfo()

				landcover_class = round(float(mode_dict['landcover']))

				#extract images
				# NAIP
				task = ee.batch.Export.image.toDrive(
					image=NAIP_vis,
					description=naip_filename + str(image_index),
					dimensions=imgsize,
					region=f1,
					folder=naip_folder + letter  # 'GEE/NAIP_image'
				)

				task.start()
				state = task.status()['state']
				while state in ['READY', 'RUNNING']:
					if export_outputs:
						print state + '...'
					# print task.status()
					state = task.status()['state']

				if task.status()['state'] == 'COMPLETED':
					print 'NAIP image ', str(image_index), ' of', str(total_points), ' done'
				else:
					print 'NAIP image ', str(image_index), ' of', str(total_points), ' failed:'
					print task.status()
					delete_writer.writerow([index, point])
					count += 1
					continue

				# NLCD
				task = ee.batch.Export.image.toDrive(
					image=landCover,
					description=nlcd_filename + str(image_index),
					dimensions=imgsize,
					region=f1,
					folder=nlcd_folder + letter  # 'GEE/NLCD_image'
				)

				task.start()
				state = task.status()['state']
				while state in ['READY', 'RUNNING']:
					if export_outputs:
						print state + '...'
					# print task.status()
					state = task.status()['state']

				if task.status()['state'] == 'COMPLETED':
					print 'NLCD image ', str(image_index), ' of', str(total_points), ' done'
				else:
					print 'NLCD image ', str(image_index), ' of', str(total_points), ' failed:'
					print task.status()
					delete_writer.writerow([index, point])
					count += 1
					continue

				nlcd_writer.writerow([index, landcover_class, _long, _lat])
				exported_images += 1
				count += 1

			except:
				print 'Error in export. Skipping ' + str(image_index) + ' of ' + str(total_points)
				delete_writer.writerow([index, point])
				count += 1

	print 'Finished exporting ' + str(exported_images) + ' labels and images!'


if __name__ == '__main__':
	# https://fusiontables.google.com/data?docid=1n-XWd5KgdVGGKRaw-XVkerYL3xM2BZwXY1bQEhqF#rows:id=1

	'EXPORT IMAGES'
	input_file = sys.argv[1]
	offset = int(sys.argv[2])

	'MAP PARAMETERS'
	zoom = 16  # range 0 - 20 (whole world - building)
	scale = 30  # 30 meters/pixel - native NLCD resolution

	'IMAGE PARAMETERS'
	imgsize = [224, 224]
	width = 400  # width (and height) of output image in meters
	imgformat = "png32"  # doesn't matter for Export.toDrive - saved as .tiff

	'EXPORT PARAMETERS'
	nlcd_filename = "oregon_nlcd_"
	naip_filename = "oregon_naip_"
	nlcd_folder = 'GEE/NLCD_'
	naip_folder = 'GEE/NAIP_'

	# enable export outputs [READY/RUNNING]
	export_outputs = False

	collect_images(input_file, width, scale, offset, imgsize, nlcd_filename, naip_filename, nlcd_folder, naip_folder, export_outputs)
