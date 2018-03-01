"""
Creates a link to a static satellite image centered at 'center' w/
 given zoom level and image size
====================================================================
**Author**: Laurel Hopkins
**Date**:   Sept 2017

Based on code from http://hci574.blogspot.com/2010/04/using-google-maps-static-images.html

run: get_static_google_map("google_map_example", center="44.57,-123.30", zoom=16,
                            imgsize=(224, 224), imgformat="png32", maptype="satellite")
"""


import urllib


def get_static_google_map(filename_wo_extension, center=None, zoom=16, imgsize="224x224", imgformat="png32",
						  maptype="satellite", markers=None):
	"""retrieve a map (image) from the static google maps server
	 See: http://code.google.com/apis/maps/documentation/staticmaps/

		Creates a request string with a URL like this:
		http://maps.google.com/maps/api/staticmap?center=Brooklyn+Bridge,New+York,NY&zoom=14&size=512x512&maptype=roadmap
		  &markers=color:blue|label:S|40.702147,-74.015794&sensor=false"""

	# assemble the URL
	request = "http://maps.google.com/maps/api/staticmap?"  # base URL, append query params, separated by &

	# if center and zoom  are not given, the map will show all marker locations
	if center != None:
		request += "center=%s&" % center
		# request += "center=%s&" % "40.714728, -73.998672"   # latitude and longitude (up to 6-digits)
		# request += "center=%s&" % "50011" # could also be a zipcode,
		# request += "center=%s&" % "Brooklyn+Bridge,New+York,NY"  # or a search term
	if center != None:
		request += "zoom=%i&" % zoom  # zoom 0 (all of the world scale ) to 22 (single buildings scale)

	request += "size=%ix%i&" % (imgsize)  # tuple of ints, up to 640 by 640
	request += "format=%s&" % imgformat
	request += "maptype=%s&" % maptype  # roadmap, satellite, hybrid, terrain

	# request += "mobile=false&"  # optional: mobile=true will assume the image is shown on a small screen (mobile device)
	# request += "sensor=false&"  # must be given, deals with getting location from mobile device
	print request

	urllib.urlretrieve(request, filename_wo_extension + "." + imgformat)  # Option 1: save image directly to disk


if __name__ == '__main__':
	get_static_google_map("google_map_example", center="44.57,-123.30", zoom=16, imgsize=(224, 224), imgformat="png32", maptype="satellite")
	#png32: 32-bit format, default is 8-bit