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
import configparser
import os

from geopy.geocoders import GoogleV3

from .providers.foursquare import FourSquare
from .providers.flickr import Flickr
from .providers.twitter import Twitter
from .utilities import Utilities


class GeOSINT(object):

	def __init__(self, address, city, state, radius):
		self.utils = Utilities()
		self.radius = radius
		self.coords = self.get_coords(address, city, state)

		self.mapbox_api = self.get_keys('Mapbox')
		self.foursquare_api = self.get_keys('FourSquare')
		self.flickr_api = self.get_keys('Flickr')
		self.twitter_api = self.get_keys('Twitter')

	def get_keys(self, service):
		"""
		Parse API keys from configuration file.
		"""
		api_keys = {}

		config = configparser.ConfigParser()
		if os.path.isfile(os.path.abspath('api_keys.ini')):
			config.read(os.path.abspath('api_keys.ini'))
			keys = config.options(service)
			for key in keys:
				try:
					key_value = config.get(service, key)
					if key_value == '':
						api_keys[key] = None
					else:
						api_keys[key] = key_value
				except Exception as error:
					raise error
		else:
			self.utils.print_error("API configuration file not found at {0}".format(os.path.abspath('api_keys.ini')))

		return api_keys

	def get_coords(self, address, city, state):
		"""
		Get latitude and longitude from supplied address.
		"""
		coords = {
			'address': "{0}, {1}, {2}".format(address, city, state),
			'lat': None,
			'lon': None
		}

		try:
			geolocator = GoogleV3(timeout=5)
			location = geolocator.geocode(coords['address'], exactly_one=True)
			coords['lat'] = location.latitude
			coords['lon'] = location.longitude
		except Exception as error:
			raise error

		return coords

	def find(self):
		"""
		Get photos for social media accounts with API keys.
		"""
		collected_photos = {
			'FourSquare': None,
			'Flickr': None,
			'Twitter': None
		}

		if None not in self.foursquare_api.values():
			collected_photos['FourSquare'] = FourSquare(self.coords, self.radius, self.foursquare_api).photos()

		if None not in self.flickr_api.values():
			collected_photos['Flickr'] = Flickr(self.coords, self.radius, self.flickr_api).photos()

		if None not in self.twitter_api.values():
			collected_photos['Twitter'] = Twitter(self.coords, self.radius, self.twitter_api).photos()

		return collected_photos
