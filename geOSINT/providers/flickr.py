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
import requests
import json

from geopy.distance import vincenty

try:
	requests.packages.urllib3.disable_warnings()
except:
	pass


class Flickr(object):
	"""
	Get photos from Flickr.
	"""
	def __init__(self, coords, radius, api):
		self.lat = coords['lat']
		self.lon = coords['lon']
		self.radius = radius
		self.key = api['api_key']

		self.found_photos = []

	def photos(self):
		response = requests.get(
			"https://api.flickr.com/services/rest/?method=flickr.photos.search&format=json&accuracy=16&content_type=4&lat={0}&lon={1}&radius={2}&per_page=500&page=1&api_key={3}".format(self.lat, self.lon, float(self.radius) / 1000.0, self.key),
			verify=False
		)
		if response.status_code == 200:
			search_results = json.loads((response.content).replace('jsonFlickrApi(', '').replace(')', ''))
			for result in search_results['photos']['photo']:
				response = requests.get(
					"https://api.flickr.com/services/rest/?method=flickr.photos.geo.getLocation&photo_id={0}&format=json&api_key={1}".format(result['id'], self.key),
					verify=False
				)
				search_results = json.loads((response.content).replace('jsonFlickrApi(', '').replace(')', ''))
				photo_lat = search_results['photo']['location']['latitude']
				photo_lon = search_results['photo']['location']['longitude']
				if photo_lat and photo_lon:
					distance = int(vincenty((self.lat, self.lon), (photo_lat, photo_lon)).meters)
					if distance <= self.radius:
						photo = "https://c2.staticflickr.com/{0}/{1}/{2}_{3}_b.jpg".format(result['farm'], result['server'], result['id'], result['secret'])
						found_photo = {
							'photo': [photo],
							'lat': float(photo_lat),
							'lon': float(photo_lon)
						}

						if self.found_photos:
							self._sort(found_photo)
						else:
							self.found_photos.append(found_photo)

		return self.found_photos

	def _sort(self, found):
		for photo in self.found_photos:
			if photo['lat'] == found['lat'] and photo['lon'] == found['lon']:
				photo['photo'].append(found['photo'][0])
				return

		self.found_photos.append(found)
