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


pp = pprint.PrettyPrinter(indent=3)

class FlickrPhoto:

   def __init__(self, flickrapi_photo_xml):
      self.xml = flickrapi_photo_xml

   def big_url(self):
      url = "http://farm%s.staticflickr.com/%s/%s_%s_b.jpg" % ( self.xml.attrib['farm'], self.xml.attrib['server'], self.xml.attrib['id'], self.xml.attrib['secret'] )
      return url

   def flickr_locator_string(self):
      return "%s_%s_%s_%s" % ( self.xml.attrib['farm'], self.xml.attrib['server'], self.xml.attrib['id'], self.xml.attrib['secret'] )
      
   def saveToDirectory(self, path):
      image_response = urllib2.urlopen(self.big_url())
      image_file = open(path + "/" + self.flickr_locator_string() + ".jpg", "w")
      image_file.write(image_response.read())
      image_file.close()
      

class Flickr:

   api_key    = '9db4bbb1d275baedb6e77c2aa7538c90'
   api_secret = '09be4700c52c3996'

   def __init__(self):
      self.flickr = flickrapi.FlickrAPI(self.api_key, self.api_secret)
      # authenticate
      (token, frob) = self.flickr.get_token_part_one(perms='read')
      if not token: raw_input("Press ENTER after you authorized this program")
      self.flickr.get_token_part_two((token, frob))
      print "Authed to Flickr"

   def getPhotos(self, bounds, limit):

      print "start getPhotosAtLatLng"

      bbox_string = "%s,%s,%s,%s" % (bounds['left'], bounds['bottom'], bounds['right'], bounds['top'])

      # TODO search smartly through time limits
      photos_response = self.flickr.photos_search(bbox=bbox_string, min_upload_date='1238433133', max_upload_date='1298433133', per_page=limit, page=0)

      photos = []
      for photoxml in photos_response[0]:
         photos.append(FlickrPhoto(photoxml))
      return photos


class FaceDetector:

   api_key = '256d354cd4cd3e51ab8ce004b1f6aad2'
   api_secret = '9d629a8692f4c407e092f59ffec2f384'

   def getFaces(self, url):
      faces_url = 'http://api.face.com/faces/detect.json?api_key='+self.api_key+'&api_secret='+self.api_secret+'&format=json&attributes=all&urls='+url
      face_response = urllib2.urlopen(faces_url)
      face_str = face_response.read()
      response = json.loads(face_str)

      # API limit reminder...
      sys.stderr.write(str(response['usage']['remaining']) + ' calls remaining. resets at ' + response['usage']['reset_time_text'] + "\n")

      if response['status'] == 'success':
	 tags = response['photos'][0]['tags']

         confident_tags = []

	 for tag in tags:
	    if int(tag['attributes']['face']['confidence']) > 50:
	       confident_tags.append({'center': tag['center'], 'width': tag['width'], 'height': tag['height']})
         if len(confident_tags) > 0:
            return confident_tags

      return None




class FlickrFaceMap:

   def __init__(self, name, timestamp):
      self.session = {}
      self.session_name = name
      self.session_timestamp = timestamp

      self.flickrPhotos = Flickr()
      self.faceDetector = FaceDetector()

      self.root_face_image_dir = 'data/facemap/'+self.session_name+'/'+self.session_timestamp
      if not os.path.exists(self.root_face_image_dir):
	 os.makedirs(self.root_face_image_dir)

   def saveFace(self, face, photo, cell):

      face_image_dir = self.root_face_image_dir + "/" + str(cell['location']['row']) + "/" + str(cell['location']['column'])
      if not os.path.exists(face_image_dir):
	 os.makedirs(face_image_dir)

      photo.saveToDirectory(face_image_dir)

      face_file = open(face_image_dir + '/'+photo.flickr_locator_string()+'.json', 'w')
      face_file.write(json.dumps(face))
      face_file.close()


   def cellTask(self, cell):
      photos = self.flickrPhotos.getPhotos(bounds=cell['bounds'], limit=100)

      face = None

      while face == None and len(photos) > 0:
         photo = photos.pop()

         print "finding faces in " + str(cell['location']['row']) + ", " + str(cell['location']['column']) + ": " + photo.big_url() + " ..."
         faces = self.faceDetector.getFaces(photo.big_url())

         if faces != None:
            face = faces[0]
            self.saveFace(face, photo, cell)
