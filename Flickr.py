#!/usr/bin/env python



import sys
import os
import urllib2
import flickrapi
import json
import pprint
import time, calendar
from datetime import timedelta
import datetime
import math
from PIL import Image
import glob

pp = pprint.PrettyPrinter(indent=3)

flickr = None

class GeoMine:

   def __init__(self, bbox, year):
      self.bbox = bbox
      self.year = year # TODO make low/high constructor instead
      self.min_upload_time = time.mktime(datetime.datetime(year, 1,   1,  0,  0,  0).timetuple())
      self.max_upload_time = time.mktime(datetime.datetime(year, 12, 30, 23, 59, 59).timetuple())


   def llwidth(self):
      return self.bbox['right'] - self.bbox['left']

   def llheight(self):
      return self.bbox['top'] - self.bbox['bottom']

   def might_be_truncated(self):
      limit = 200
      self.results = flickr.query_bbox_and_upload_time_segment(self.bbox, self.min_upload_time, self.max_upload_time, limit)
      print str(self.bbox) + ": " + str(len(self.results))
      return len(self.results) >= limit/2

   def children(self):
      children = list()
      for r in range(0, 2):
         for c in range(0, 2):
            child_bbox = dict()
            child_bbox['left']  = self.bbox['left'] + c * (self.llwidth() / 2)
            child_bbox['right'] = child_bbox['left'] + (self.llwidth() / 2)
            child_bbox['bottom'] = self.bbox['bottom'] + r * (self.llheight() / 2)
            child_bbox['top'] = child_bbox['bottom'] + (self.llheight() / 2)
            yield GeoMine(child_bbox, self.year)



class FlickrPhoto:

   def __init__(self, xml=None, locator_string=None, flickr=None):
      self.xml = xml
      self.locator_string = locator_string
      self.flickr = flickr

   def big_url(self):
      url = "http://farm%s.staticflickr.com/%s/%s_%s_b.jpg" % ( self.xml.attrib['farm'], self.xml.attrib['server'], self.xml.attrib['id'], self.xml.attrib['secret'] )
      return url

   def page_url(self):
      (farm, server, photo_id, secret) = self.locator_string.split('_')
      user_id = self.flickr.get_photo_user_id(photo_id, secret)
      return "http://www.flickr.com/photos/"+user_id+"/"+photo_id

   def lat_lng(self):
      return (float(self.xml.attrib['latitude']), float(self.xml.attrib['longitude']))

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

   def query_bbox_and_upload_time_segment(self, bbox, min_upload_time, max_upload_time, limit):
      bbox_string = "%s,%s,%s,%s" % (bbox['left'], bbox['bottom'], bbox['right'], bbox['top'])
      photos_response = self.flickr.photos_search(bbox=bbox_string, min_upload_date=min_upload_time, max_upload_date=max_upload_time, per_page=limit, extras="geo", page=0)
      photos = []
      for photoxml in photos_response[0]:
         photo = FlickrPhoto(xml=photoxml)
         photos.append(photo)
         (lat, lng) = photo.lat_lng()
         if lat < bbox['bottom'] or lat > bbox['top'] or lng < bbox['left'] or lng > bbox['right']:
            print "WTSSSSSSSSSSSSSSSSSSSSSSSSSS " + str(photo.lat_lng()) + " not in " + str(bbox)
      return photos



   def getPhotos(self, bounds, limit):

      bbox_string = "%s,%s,%s,%s" % (bounds['left'], bounds['bottom'], bounds['right'], bounds['top'])

      # TODO search smartly through time limits (Flickr requires limiter for geo queries, like time limits...)
      photos_response = self.flickr.photos_search(bbox=bbox_string, min_upload_date='1238433133', max_upload_date='1298433133', per_page=limit, extras="geo", page=0)

      photos = []
      for photoxml in photos_response[0]:
         photo = FlickrPhoto(xml=photoxml)
         photos.append(photo)
         (lat, lng) = photo.lat_lng()
         if lat < bounds['bottom'] or lat > bounds['top'] or lng < bounds['left'] or lng > bounds['right']:
            print "WTSSSSSSSSSSSSSSSSSSSSSSSSSS " + str(photo.lat_lng()) + " not in " + str(bounds)
      return photos

   def get_photo_user_id(self, photo_id, secret):
      info_response = self.flickr.photos_getInfo(photo_id=photo_id, secret=secret) #omg will this work
      return info_response.find('photo').find('owner').attrib['nsid']

flickr = Flickr()
