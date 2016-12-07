#!/usr/bin/env python
# Copyright (c) 2016, Brandan Geise [coldfusion]
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import argparse
import os

from geOSINT.main import GeOSINT
from geOSINT.maps import Mapbox
from geOSINT.utilities import Utilities


def main():
	parser = argparse.ArgumentParser(description='Search social media for geotagged photos near a physical location', usage='geOSINT.py -a ADDRESS -c CITY -s STATE [--distance DISTANCE] [--output OUTPUT] [-h]')
	parser.add_argument('-a', dest='address', help='Address', nargs='+', required=True)
	parser.add_argument('-c', dest='city', help='City', nargs='+', required=True)
	parser.add_argument('-s', dest='state', help='State (two letter abbreviation)', required=True)
	parser.add_argument('--distance', dest='distance', help='Distance, in meters, to search from address (default: 500)', type=int, default=500)
	parser.add_argument('--output', dest='output', help='Name of output file (default: geo_osint.html)', default='geo_osint.html')
	args = parser.parse_args()

	utils = Utilities()

	geosint = GeOSINT(' '.join(args.address), ' '.join(args.city), args.state, args.distance)

	# Setup map
	osint_map = Mapbox(geosint.coords, args.distance, geosint.mapbox_api)

	# Grab images
	utils.print_status("Looking for images within {0} meters of {1}".format(args.distance, geosint.coords['address']))
	found_photos = geosint.find()

	for provider in found_photos:
		if found_photos[provider]:
			utils.print_good("Found photos on {0}".format(provider))
			for photo in found_photos[provider]:
				osint_map.add_point(photo)
		elif found_photos[provider] is None:
			utils.print_warn("No API key found for {0}".format(provider))
		else:
			utils.print_warn("No photos found on {0}".format(provider))

	# Write output
	if any(found_photos.values()):
		osint_map.save(os.path.abspath(args.output))
		utils.print_good("Out file written to {0}".format(os.path.abspath(args.output)))

if __name__ == '__main__':
	main()
