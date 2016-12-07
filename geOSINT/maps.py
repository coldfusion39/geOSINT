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
import folium


class Mapbox(object):

	def __init__(self, coords, radius, api):
		if api['access_token']:
			tiles = "https://api.mapbox.com/v4/mapbox.streets-satellite/{{z}}/{{x}}/{{y}}.png32?access_token={0}".format(api['access_token'])
			attr = 'Mapbox attribution'
		else:
			tiles = 'Stamen Toner'
			attr = None

		self.maps = folium.Map(
			location=[coords['lat'], coords['lon']],
			tiles=tiles,
			attr=attr,
			zoom_start=16
		)

		distance_marker = folium.CircleMarker(
			location=[coords['lat'], coords['lon']],
			radius=radius,
			color='#3186cc',
			fill_color='#3186cc',
			fill_opacity=0.2
		)

		distance_marker.add_to(self.maps)

	def add_point(self, photo):
		"""
		Plot point on the map based on photo's latitude and longitude coordinates.
		"""
		iframe = self._get_frame(photo)

		marker = folium.CircleMarker(
			location=[photo['lat'], photo['lon']],
			radius=3,
			popup=folium.Popup(iframe, max_width=2650),
			color='Red',
			fill_opacity=1.0,
			fill_color='Red'
		)

		marker.add_to(self.maps)

	def _get_frame(self, photo):
		"""
		Create an iframe for viewing photos on the generated map.
		"""
		html = []

		for photo in photo['photo']:
			html.append("<a href='{0}' target='_blank'><img src='{0}' width='200' height='auto'></a><div><br>".format(photo))

		return folium.element.IFrame(html=''.join(html), width=250, height=300)

	def save(self, output):
		"""
		Save generated map.
		"""
		self.maps.save(output)
		return True
