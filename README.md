# geOSINT
Search physical locations for geo tagged photos
# geOSINT
Search physical locations for geotagged photos

## Summary ##
geOSINT is a script that searches for geotagged photos on social media and plots them on a map. This can be used to perform OSINT on a physical location. If an image is found, a red marker is placed on the map. By clicking on this marker you can view the identified image.

![Demo 1](https://raw.githubusercontent.com/coldfusion39/geOSINT/screenshots/demo1.png)

![Demo 2](https://raw.githubusercontent.com/coldfusion39/geOSINT/screenshots/demo2.png)

## Quick Start ##
    $ git clone https://github.com/coldfusion39/geOSINT.git
    $ cd geOSINT/
    $ sudo pip install -r requirements.txt
    $ cp api_keys.ini.example api_keys.ini
    # add api keys
    $ ./geOSINT.py -a 9231 W 87th Pl -c Arvada -s CO -d 1000

## Requirements ##
Run `pip install -r requirements.txt` to install the required python modules.
 * [Folium](https://github.com/python-visualization/folium)
 * [geopy](https://github.com/geopy/geopy)
 * [Twython](https://github.com/ryanmcgrath/twython)

## API ##
geOSINT uses [FourSquare](https://developer.foursquare.com), [Flickr](https://developer.foursquare.com), and [Twitter](https://dev.twitter.com) APIs to search for photos posted within a certain distance of the supplied address. At least one API key is required required for geOSINT to return any results.

Optionally, if you want to use an aerial map, similar to Google Earth, a [Mapbox](https://www.mapbox.com/studio/signup/?plan=starter) API is required. 

After getting your API keys, copy the `api_keys.ini.example` file to `api_keys.ini` and add your keys as shown below.
```
[Mapbox]
access_token: xxxxx

[FourSquare]
client_id: xxxxx
client_secret: xxxxx

[Flickr]
api_key: xxxxx

[Twitter]
app_key: xxxxx
app_secret: xxxxx
oauth_token: xxxxx
oauth_token_secret: xxxxx
```

## Usage ##
After setting your API keys in the `api_keys.ini` file, supply geOSINT with a physical address. Optionally, you can specify the distance from the location you want to search, default is 500 meters.

Example:
    `./geOSINT.py -a 9231 W 87th Pl -c Arvada -s CO -d 1000`

Options:
```
  -h, --help            show this help message and exit
  -a ADDRESS            Address
  -c CITY               City
  -s STATE              State (ex. OH)
  -o OUTPUT             Name of output file, (default: geo_osint.html)
  -d DISTANCE           Distance, in meters, to search from address, (default: 500)
```
