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


class FourSquare(object):
	"""
	Get photos from FourSquare
	"""
	def __init__(self, coords, radius, api):
		self.lat = coords['lat']
		self.lon = coords['lon']
		self.radius = radius
		self.key = api['client_id']
		self.secret = api['client_secret']

		self.found_photos = []

	def photos(self):
		response = requests.get(
			"https://api.foursquare.com/v2/venues/search?ll={0},{1}&limit=50&radius={2}&client_id={3}&client_secret={4}&v=20130815".format(self.lat, self.lon, self.radius, self.key, self.secret),
			verify=False
		)
		if response.status_code == 200:
			search_results = json.loads(response.text)
			for result in search_results['response']['venues']:
				try:
					photo_lat = result['location']['labeledLatLngs'][0]['lat']
					photo_lon = result['location']['labeledLatLngs'][0]['lng']
				except KeyError:
					photo_lat = result['location']['lat']
					photo_lon = result['location']['lng']

				distance = int(vincenty((self.lat, self.lon), (photo_lat, photo_lon)).meters)
				if distance <= self.radius:
					response = requests.get(
						"https://api.foursquare.com/v2/venues/{0}/photos?limit=200&offset=1&client_id={1}&client_secret={2}&v=20130815".format(result['id'], self.key, self.secret),
						verify=False
					)
					response = json.loads(response.text)
					if response['response']['photos']['count'] > 0:
						for item in response['response']['photos']['items']:
							photo = "{0}original{1}".format(item['prefix'], item['suffix'])
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
