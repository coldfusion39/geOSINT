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
from geopy.distance import vincenty
from twython import Twython


class Twitter(object):
	"""
	Get photos from Twitter
	"""
	def __init__(self, coords, radius, api):
		self.lat = coords['lat']
		self.lon = coords['lon']
		self.radius = radius
		self.twitter = Twython(
			api['app_key'],
			api['app_secret'],
			api['oauth_token'],
			api['oauth_token_secret']
		)

		self.twitter.verify_credentials()

		self.found_photos = []

	def photos(self):
		response = self.twitter.search(q="geocode:{0},{1},{2}km".format(self.lat, self.lon, float(self.radius) / 1000.0), count=100)
		for tweet in response['statuses']:
			if tweet.get('geo') is None:
				continue

			photo_lat, photo_lon = tweet['geo']['coordinates']
			photo = next((e[0]['media_url'] for e in tweet['entities'] if 'media' in e), None)
			if photo is None:
				continue

			distance = int(vincenty((self.lat, self.lon), (photo_lat, photo_lon)).meters)
			if distance <= self.radius:
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
