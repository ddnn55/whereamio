#!/usr/bin/env python

import sys
import os

import urllib2
import flickrapi

import json

import pprint

import time, calendar
from datetime import timedelta

import math

def distance_on_spherical_earth(lat1, long1, lat2, long2):

    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
        
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
        
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
        
    # Compute spherical distance from spherical coordinates.
        
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
    
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )

    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc * 6378100

def now():
   unix_time = calendar.timegm(time.gmtime())
   return unix_time

top    = float(sys.argv[1])
left   = float(sys.argv[2])
bottom = float(sys.argv[3])
right  = float(sys.argv[4])

degree_width  = (right - left)
degree_height = (top - bottom)

center_x = left + (right - left) / 2.0
center_y = bottom + (top - bottom) / 2.0

meter_width  = distance_on_spherical_earth(center_y, left, center_y, right)
meter_height = distance_on_spherical_earth(bottom, center_x, top, center_x)

print (meter_width, meter_height)

columns = int(sys.argv[5])
rows = int(columns * meter_height / meter_width)

name = sys.argv[6]

timestamp_id = 0
if len(sys.argv) > 7:
   timestamp_id = sys.argv[7]
else:
   timestamp_id = now()



zoom = 2

print 'Session is: ' + name + ' ' + str(timestamp_id)

#print rows
#exit()

print str(columns) + ' x ' + str(rows)
print str(degree_width) + " x " + str(degree_height)




class FlickrPhotos:

   api_key    = '9db4bbb1d275baedb6e77c2aa7538c90'
   api_secret = '09be4700c52c3996'

   def __init__(self):
      self.flickr = flickrapi.FlickrAPI(self.api_key, self.api_secret)
      # authenticate
      (token, frob) = self.flickr.get_token_part_one(perms='read')
      if not token: raw_input("Press ENTER after you authorized this program")
      self.flickr.get_token_part_two((token, frob))
      print "Authed to Flickr"

   def getPhotosAtLatLng(self, latitude, longitude):

      print "start getPhotosAtLatLng"

      #photos = flickr.photos_geo_photosForLocation(lon='41.882692', lat='-87.623316', per_page='500')
      #photos = flickr.photos_search(lon='41.882692', lat='-87.623316', per_page='500')
      #for current_page in range(1, pages+1):
         #photos = flickr.photos_search(place_id=2379574, text="the bean", per_page='500', page=str(current_page))
      photos_response = self.flickr.photos_search(lat=latitude, lon=longitude, min_upload_date='1238433133', max_upload_date='1298433133', accuracy='16', per_page='500', page=0)
      #photos_response = self.flickr.photos_search(lat=40.830891, lon=-73.865304, min_upload_date='1238433133', max_upload_date='1298433133', accuracy='16', per_page='500', page=0)
      return photos_response[0]

      for photoss in photos_response:
      #   print photo
         for photo in photoss:
            # <photo farm="8" id="6630559531" isfamily="0" isfriend="0" ispublic="1" owner="74669477@N00" secret="e56a7ce7ba" server="7020" title="love and the bean 3" />
            url = "http://farm%s.staticflickr.com/%s/%s_%s_b.jpg" % ( photo.attrib['farm'], photo.attrib['server'], photo.attrib['id'], photo.attrib['secret'] )
            #print photo.attrib['id']
            #image_response = urllib2.urlopen(url)
            #image_file = open("data/flickr_image/%s_%s_%s_%s_b.jpg" % ( photo.attrib['farm'], photo.attrib['server'], photo.attrib['id'], photo.attrib['secret'] ), 'w')
            #image_file.write(image_response.read())
            #image_file.close()
            print "Found " + url
      print str(latitude) + ', ' + str(longitude)
      sys.exit(0)




class FaceDetector:

   api_key = '256d354cd4cd3e51ab8ce004b1f6aad2'
   api_secret = '9d629a8692f4c407e092f59ffec2f384'

   def getFaces(self, url):
      faces_url = 'http://api.face.com/faces/detect.json?api_key='+self.api_key+'&api_secret='+self.api_secret+'&format=json&attributes=all&urls='+url
      face_response = urllib2.urlopen(faces_url)
      face_str = face_response.read()
      #face_str = file('face_sample.json').read()
      #print "============"
      #print face_str
      #print "============"
      faces = json.loads(face_str)
      return faces


def saveMetadataAndDownloadTiles(panoJSON, column, row):
   pano = json.loads(panoJSON)
   if len(pano) > 0:
      #pp = pprint.PrettyPrinter(indent=4)
      #pp.pprint(pano)

      longitude = pano[u'Location'][u'lng']
      latitude  = pano[u'Location'][u'lat']
      localFile = open('data/panojson/'+name+'_'+str(timestamp_id)+'_'+str(latitude)+'_'+str(longitude)+'_'+str(row)+'_'+str(column)+'.json', 'w')
      localFile.write(panoJSON)
      localFile.close()

      panoid = pano[u'Location'][u'panoId']
      for pano_x in range(0, 4): # this range depends on zoom level TODO
         tile_url = "http://cbk0.google.com/cbk?output=tile&panoid="+panoid+"&zoom="+str(zoom)+"&x="+str(pano_x)+"&y=0"
         #print "Borrowing image at " + tile_url
         tile_response = urllib2.urlopen(tile_url)
         #tile_file = open('data/panotile/'+panoid+'_z'+str(zoom)+'_'+str(pano_x)+'_0.jpeg', 'w')
         #tile_file.write(tile_response.read())
         #tile_file.close()

panojson_filenames = os.listdir('data/panojson')
max_row = 0
max_col = 0
for filename in panojson_filenames:
   components = filename[0:-5].split('_')
   if len(components) == 6:
      (json_name, json_timestamp_id, json_latitude, json_longitude, json_row, json_col) = filename[0:-5].split('_')
      if json_name == name:
         if json_timestamp_id == timestamp_id:
            max_row = max(int(max_row), int(json_row))
            max_col = max(int(max_col), int(json_col))

resuming = True # FIXME resume is broken!

flickrPhotos = FlickrPhotos()
faceDetector = FaceDetector()

pp = pprint.PrettyPrinter(indent=4)

for x in range(max_col, columns):
   for y in range(0, rows):

      longitude  = left   + degree_width  * x / columns
      latitude = bottom + degree_height * y / rows



      

      photos = flickrPhotos.getPhotosAtLatLng(latitude, longitude)
      pp.pprint(photos)

      # look for faces

      for photo in photos:
         pp.pprint(photo)
         # <photo farm="8" id="6630559531" isfamily="0" isfriend="0" ispublic="1" owner="74669477@N00" secret="e56a7ce7ba" server="7020" title="love and the bean 3" />
         url = "http://farm%s.staticflickr.com/%s/%s_%s_b.jpg" % ( photo.attrib['farm'], photo.attrib['server'], photo.attrib['id'], photo.attrib['secret'] )
         #print photo.attrib['id']
         #image_response = urllib2.urlopen(url)
         #image_file = open("data/flickr_image/%s_%s_%s_%s_b.jpg" % ( photo.attrib['farm'], photo.attrib['server'], photo.attrib['id'], photo.attrib['secret'] ), 'w')
         #image_file.write(image_response.read())
         #image_file.close()
         #url = 'http://farm2.staticflickr.com/1081/4605302764_cd76e6c5fa_b.jpg'
         print "Finding faces in " + url + " ..."
         faces = faceDetector.getFaces(url)
         if faces['status'] == 'success':
            if len(faces['photos'][0]['tags']) > 0:
               
         pp.pprint(faces)

         sys.exit(0)
         
         saveMetadataAndDownloadImage(panoJSON, x, y)
      


      elapsed = now() - actual_start_timestamp
      time_progress = (float(x * rows + y) / float(rows * columns) - start_progress) / (1.0 - start_progress)
      task_progress = float(x * rows + y) / float(rows * columns)
      if time_progress > 0:
         remaining = elapsed * (1 - time_progress) / time_progress
      else:
         remaining = 0
      hours, remainder = divmod(remaining, 3600)
      minutes, seconds = divmod(remainder, 60)

      sys.stdout.write('|')
      for p in range(0, int(task_progress * 50)):
         sys.stdout.write('=')
      for p in range(int(task_progress * 50), 50):
         sys.stdout.write(' ')
      sys.stdout.write('| ' + str(int(task_progress*100)) + ' % Remaining: ' + str(int(hours)) + 'h ' + str(int(minutes)) + 'm ' + str(int(seconds)) + 's               \r')
      sys.stdout.flush()

sys.stdout.write('\n')
sys.stdout.flush()
      
