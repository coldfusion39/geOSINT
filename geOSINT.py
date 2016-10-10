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
import configparser
import folium
import json
import os
import requests
from geopy.geocoders import GoogleV3
from geopy.distance import vincenty
from twython import Twython


class GenericError(Exception):
	def __init__(self, *args, **kwargs):
		Exception.__init__(self, *args, **kwargs)


def main():
	parser = argparse.ArgumentParser(description='Search physical locations for geotagged photos')
	parser.add_argument('-a', dest='address', help='Address', nargs='+', required=True)
	parser.add_argument('-c', dest='city', help='City', nargs='+', required=True)
	parser.add_argument('-s', dest='state', help='State (ex. OH)', required=True)
	parser.add_argument('-o', dest='output', help='Name of output file', default='geo_osint.html')
	parser.add_argument('-d', dest='distance', help='Distance, in meters, to search from address (default: 500)', type=int, default=500)
	args = parser.parse_args()

	# Parse config
	config = configparser.ConfigParser()
	config.read(os.path.abspath('api_keys.ini'))

	# Get coordinates
	lat, lon, address = get_coords(' '.join(args.address), ' '.join(args.city), args.state)

	print_good("Looking for images within {0} meters of {1}".format(args.distance, address))

	if config.get('Mapbox', 'access_token'):
		tiles = "https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/256/{{z}}/{{x}}/{{y}}?access_token={0}".format(config.get('Mapbox', 'access_token'))
		attr = 'Mapbox attribution'
	else:
		tiles = 'Stamen Toner'
		attr = ''

	# Setup map
	maps = folium.Map(
		location=[lat, lon],
		tiles=tiles,
		attr=attr,
		zoom_start=16
	)

	folium.CircleMarker(
		location=[lat, lon],
		radius=args.distance,
		color='#3186cc',
		fill_color='#3186cc',
		fill_opacity=0.2
	).add_to(maps)

	# Get FourSquare photos
	if config.get('FourSquare', 'client_id') and config.get('FourSquare', 'client_secret'):
		print_status('Getting images from FourSquare...')
		maps = get_foursquare_venues(config.get('FourSquare', 'client_id'), config.get('FourSquare', 'client_secret'), lat, lon, args.distance, maps)
	else:
		print_warn('No Foursquare API keys in config')

	# Get Flickr photos
	if config.get('Flickr', 'api_key'):
		print_status('Getting images from Flickr...')
		maps = get_flickr_photos(config.get('Flickr', 'api_key'), lat, lon, args.distance, maps)
	else:
		print_warn('No Flickr API keys in config')

	# Get Twitter photos
	if config.get('Twitter', 'app_key') and config.get('Twitter', 'app_secret') and config.get('Twitter', 'oauth_token') and config.get('Twitter', 'oauth_token_secret'):
		print_status('Getting images from Twitter...')
		maps = get_twitter_photos(config.get('Twitter', 'app_key'), config.get('Twitter', 'app_secret'), config.get('Twitter', 'oauth_token'), config.get('Twitter', 'oauth_token_secret'), lat, lon, args.distance, maps)
	else:
		print_warn('No Twitter API keys in config')

	maps.save(args.output)
	print_good("Outfile written to {0}".format(os.path.abspath(args.output)))


# Get Geo-location coordinates
def get_coords(address, city, state):
	try:
		geolocator = GoogleV3(timeout=5)
		address = "{0}, {1}, {2}".format(address, city, state)
		location = geolocator.geocode(address, exactly_one=True)
		lat = location.latitude
		lon = location.longitude
	except Exception as error:
		raise GenericError(error)

	return lat, lon, address


# Get venue IDs
def get_foursquare_venues(key, secret, lat, lon, radius, maps):
	venue_url = "https://api.foursquare.com/v2/venues/search?ll={0},{1}&limit=50&radius={2}&client_id={3}&client_secret={4}&v=20130815".format(lat, lon, radius, key, secret)
	response = requests.get(venue_url)
	if response.status_code == 200:
		search_results = json.loads(response.text)
		for result in search_results['response']['venues']:
			venue_id = result['id']
			venue_name = result['name']
			try:
				photo_lat = result['location']['labeledLatLngs'][0]['lat']
				photo_lon = result['location']['labeledLatLngs'][0]['lng']
			except KeyError:
				photo_lat = result['location']['lat']
				photo_lon = result['location']['lng']

			distance = vincenty((lat, lon), (photo_lat, photo_lon)).meters
			if int(distance) <= radius:
				maps = get_foursquare_photos(venue_name, venue_id, key, secret, photo_lat, photo_lon, maps)
	else:
		raise GenericError('Could not connect to FourSquare')

	return maps


# Get photo URLs
def get_foursquare_photos(name, venue, key, secret, lat, lon, maps):
	photos = []
	photo_url = "https://api.foursquare.com/v2/venues/{0}/photos?limit=200&offset=1&client_id={1}&client_secret={2}&v=20130815".format(venue, key, secret)
	response = requests.get(photo_url)
	if response.status_code == 200:
		search_results = json.loads(response.text)
		if search_results['response']['photos']['count'] > 0:
			for result in search_results['response']['photos']['items']:
				photo = "{0}original{1}".format(result['prefix'], result['suffix'])
				photos.append(photo)
				iframe = get_frame(photos)

				folium.CircleMarker(
					location=[lat, lon],
					radius=3,
					popup=folium.Popup(iframe, max_width=2650),
					color='Red',
					fill_opacity=1.0,
					fill_color='Red'
				).add_to(maps)
	else:
		raise GenericError('Could not connect to FourSquare')

	return maps


# Get photos from Flickr
def get_flickr_photos(key, lat, lon, radius, maps):
	photos = []
	api_url = "https://api.flickr.com/services/rest/?method=flickr.photos.search&format=json&accuracy=16&content_type=4&lat={0}&lon={1}&radius={2}&per_page=500&page=1&api_key={3}".format(lat, lon, (float(radius) / 1000.0), key)
	response = requests.get(api_url)
	if response.status_code == 200:
		search_results = json.loads((response.content).replace('jsonFlickrApi(', '').replace(')', ''))
		for result in search_results['photos']['photo']:
			photo_id = result['id']
			photo_farm = result['farm']
			photo_server = result['server']
			photo_secret = result['secret']

			photo_lat, photo_lon = flickr_photo_coords(key, photo_id)

			distance = vincenty((lat, lon), (photo_lat, photo_lon)).meters
			if int(distance) <= radius:
				photo = ["https://c2.staticflickr.com/{0}/{1}/{2}_{3}_b.jpg".format(photo_farm, photo_server, photo_id, photo_secret)]
				iframe = get_frame(photo)

				folium.CircleMarker(
					location=[photo_lat, photo_lon],
					radius=3,
					popup=folium.Popup(iframe, max_width=2650),
					color='Red',
					fill_opacity=1.0,
					fill_color='Red'
				).add_to(maps)
	else:
		raise GenericError('Could not connect to Flickr')

	return maps


# Get Flickr photo coordinates
def flickr_photo_coords(key, photo):
	exif_url = "https://api.flickr.com/services/rest/?method=flickr.photos.geo.getLocation&photo_id={0}&format=json&api_key={1}".format(photo, key)
	response = requests.get(exif_url)
	if response.status_code == 200:
		search_results = json.loads((response.content).replace('jsonFlickrApi(', '').replace(')', ''))
		lat = search_results['photo']['location']['latitude']
		lon = search_results['photo']['location']['longitude']
	else:
		raise GenericError('Could not get Flickr photo')

	return lat, lon


# Get photos from Twitter
def get_twitter_photos(app_key, app_secret, oauth_token, oauth_token_secret, lat, lon, radius, maps):
	twitter = Twython(app_key, app_secret, oauth_token, oauth_token_secret)
	twitter.verify_credentials()

	query = "geocode:{0},{1},{2}km -RT".format(lat, lon, float(radius) / 1000.0)
	results = twitter.search(q=query, count=100)
	for tweet in results['statuses']:
		try:
			photo_lat = tweet['geo']['coordinates'][0]
			photo_lon = tweet['geo']['coordinates'][1]
			photo = [tweet['entities']['media'][0]['media_url']]

			distance = vincenty((lat, lon), (photo_lat, photo_lon)).meters
			if int(distance) <= radius:
				iframe = get_frame(photo)

				folium.CircleMarker(
					location=[photo_lat, photo_lon],
					radius=3,
					popup=folium.Popup(iframe, max_width=2650),
					color='Red',
					fill_opacity=1.0,
					fill_color='Red'
				).add_to(maps)
		except KeyError:
			continue

	return maps


# Create iFrame
def get_frame(urls):
	html = ''
	for url in urls:
		html += "<a href='{0}' target='_blank'><img src='{0}' width='200' height='auto'></a><div>".format(url)

	iframe = folium.element.IFrame(html=html, width=250, height=300)

	return iframe


def print_error(msg):
	print "\033[1m\033[31m[-]\033[0m {0}".format(msg)


def print_status(msg):
	print "\033[1m\033[34m[*]\033[0m {0}".format(msg)


def print_good(msg):
	print "\033[1m\033[32m[+]\033[0m {0}".format(msg)


def print_warn(msg):
	print "\033[1m\033[33m[!]\033[0m {0}".format(msg)


if __name__ == '__main__':
	main()
