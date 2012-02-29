#!/usr/bin/env python

import xml
import pprint
import flickrapi
import urllib2
import sys

pp = pprint.PrettyPrinter(indent=4)

api_key    = '9db4bbb1d275baedb6e77c2aa7538c90'
api_secret = '09be4700c52c3996'

flickr = flickrapi.FlickrAPI(api_key, api_secret)

# authenticate
(token, frob) = flickr.get_token_part_one(perms='read')
if not token: raw_input("Press ENTER after you authorized this program")
flickr.get_token_part_two((token, frob))

pages = int(sys.argv[1])

#photos = flickr.photos_geo_photosForLocation(lon='41.882692', lat='-87.623316', per_page='500')
#photos = flickr.photos_search(lon='41.882692', lat='-87.623316', per_page='500')

for current_page in range(1, pages+1):
   #photos = flickr.photos_search(place_id=2379574, text="the bean", per_page='500', page=str(current_page))
   photos = flickr.photos_search(lat=40.830891, lon=-73.865304, min_upload_date='1238433133', max_upload_date='1298433133', accuracy='16', per_page='500', page=str(current_page))
   for photoss in photos:
   #   print photo
      for photo in photoss:
         # <photo farm="8" id="6630559531" isfamily="0" isfriend="0" ispublic="1" owner="74669477@N00" secret="e56a7ce7ba" server="7020" title="love and the bean 3" />
         url = "http://farm%s.staticflickr.com/%s/%s_%s_b.jpg" % ( photo.attrib['farm'], photo.attrib['server'], photo.attrib['id'], photo.attrib['secret'] )
         #print photo.attrib['id']
         image_response = urllib2.urlopen(url)
         image_file = open("data/flickr_image/%s_%s_%s_%s_b.jpg" % ( photo.attrib['farm'], photo.attrib['server'], photo.attrib['id'], photo.attrib['secret'] ), 'w')
         image_file.write(image_response.read())
         image_file.close()
         print "Downloaded " + url

#for photo in photos:
#   pp.pprint(photo)
