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
import subprocess
import pymongo

import dpy

pp = pprint.PrettyPrinter(indent=3)

flickr = None

def flickrJSON2MongoGeoJSON(flickrJSON):
   mongoGeoJSON = dict()
   mongoGeoJSON['flickr'] = flickrJSON
   mongoGeoJSON['location'] = [ float(flickrJSON['latitude']), float(flickrJSON['longitude']) ] # mongo recommended format for geo queries
   return mongoGeoJSON

class GeoMine: # TODO separate top level mine and this (sub mine)

   def __init__(self, params):
      self.bbox = params['bbox']
      #self.year = year # TODO make low/high constructor instead
      self.min_upload_time = params['min_upload_time']
      self.max_upload_time = params['max_upload_time']
      
      self.limit = 250
      self.results = None

   def toJSON(self):
      params = dict()
      params['bbox'] = self.bbox
      params['min_upload_time'] = self.min_upload_time
      params['max_upload_time'] = self.max_upload_time
      return json.dumps(params);

   def llwidth(self):
      return self.bbox['right'] - self.bbox['left']

   def llheight(self):
      return self.bbox['top'] - self.bbox['bottom']

   def might_be_truncated(self):
      self.assure_query_ran()
      print str(self.bbox) + ": " + str(len(self.results))
      return len(self.results) >= int(0.9 * self.limit)
   
   def assure_query_ran(self):
      if self.results == None:
         self.results = flickr.query_bbox_and_upload_time_segment(self.bbox, self.min_upload_time, self.max_upload_time, self.limit)

   def children(self):
      MINIMUM_QUAD_SIZE = 0.0001
      children = list()
      if self.llwidth() > MINIMUM_QUAD_SIZE and self.llheight() > MINIMUM_QUAD_SIZE:
         for r in range(0, 2):
            for c in range(0, 2):
               child_bbox = dict()
               child_bbox['left']  = self.bbox['left'] + c * (self.llwidth() / 2)
               child_bbox['right'] = child_bbox['left'] + (self.llwidth() / 2)
               child_bbox['bottom'] = self.bbox['bottom'] + r * (self.llheight() / 2)
               child_bbox['top'] = child_bbox['bottom'] + (self.llheight() / 2)
	       params = dict();
	       params['bbox'] = child_bbox
	       params['min_upload_time'] = self.min_upload_time
	       params['max_upload_time'] = self.max_upload_time
               yield GeoMine(params)
      else:
         print "Subdivided time"
         middle_upload_time = self.min_upload_time / 2 + self.max_upload_time / 2
	 params = dict();
	 params['bbox'] = self.bbox
	 params['min_upload_time'] = self.min_upload_time
	 params['max_upload_time'] = middle_upload_time
         yield GeoMine(params)
	 params = dict();
	 params['bbox'] = self.bbox
	 params['min_upload_time'] = middle_upload_time
	 params['max_upload_time'] = self.max_upload_time
         yield GeoMine(params)
	    
   
   def store_photos_and_metadata(self):
      self.assure_query_ran()
      for photo in self.results:
         try:
            photo.store_medium_and_metadata()
	 except:
	    # wait a bit (maybe Flickr is rate limiting us), and skip this photo (maybe problem with this photo)
            with open("data/flickr_mine/error.log", "a") as logfile:
               logfile.write(photo.flickr_locator_string() + "\n")
	    time.sleep(4)


class FlickrPhoto:

   def __init__(self, xml=None, locator_string=None, flickr=None, locator_path=None):
      self.xml = xml
      self.locator_string = locator_string
      self.locator_path = locator_path
      self.flickr = flickr

   def image_base_url(self):
      base_url = "http://farm%s.staticflickr.com/%s/%s_%s_" % ( self.xml.attrib['farm'], self.xml.attrib['server'], self.xml.attrib['id'], self.xml.attrib['secret'] )
      return base_url

   def big_url(self):
      return self.image_base_url() + "b.jpg"

   def medium_url(self):
      return self.image_base_url() + "m.jpg"

   def page_url(self):
      (farm, server, photo_id, secret) = self.locator_string.split('_')
      user_id = self.flickr.get_photo_user_id(photo_id, secret)
      return "http://www.flickr.com/photos/"+user_id+"/"+photo_id

   def lat_lng(self):
      return (float(self.xml.attrib['latitude']), float(self.xml.attrib['longitude']))

   def flickr_locator_string(self):
      return "%s_%s_%s_%s" % ( self.xml.attrib['farm'], self.xml.attrib['server'], self.xml.attrib['id'], self.xml.attrib['secret'] )
   
   def flickr_locator_path(self):
      if self.locator_path != None:
         return self.locator_path
      else:
         return "%s/%s/%s_%s" % ( self.xml.attrib['farm'], self.xml.attrib['server'], self.xml.attrib['id'], self.xml.attrib['secret'] )
      
   def image_path(self):
      return "data/flickr_mirror/" + self.flickr_locator_path()
   
   def saveToDirectory(self, path):
      image_response = urllib2.urlopen(self.big_url())
      image_file = open(path + "/" + self.flickr_locator_string() + ".jpg", "w")
      image_file.write(image_response.read())
      image_file.close()

   def save_image_to_path(self, path):
      image_response = urllib2.urlopen(self.big_url())
      image_file = open(path, "w")
      image_file.write(image_response.read())
      image_file.close()

   def save_metadata_to_path(self, path):
      metadata_file = open(path, "w")
      metadata_file.write(json.dumps(self.xml.attrib))
      metadata_file.close()

   def store_medium_and_metadata(self):
      image_dir_path = "data/flickr_mirror/" + self.flickr_locator_path()
      dpy.ensure_dir(image_dir_path)
      image_path = image_dir_path + "/b.jpg"
      metadata_path = image_dir_path + "/metadata.json"

      if not os.path.exists(image_path) and not os.path.exists(metadata_path):
         self.save_image_to_path(image_path)
         self.save_metadata_to_path(metadata_path)
         print "Stored image/metadata " + image_dir_path
      else:
         print "Already stored " + image_dir_path
     
   def store_in_geodb(self):
      if self.xml == None:
         metadata = json.load(open(self.image_path() + "/metadata.json"))
	 geo_mongo_metadata = dict()
	 geo_mongo_metadata['flickr'] = metadata
	 geo_mongo_metadata['location'] = [ float(metadata['latitude']), float(metadata['longitude']) ]
	 flickr.geodb_photos.insert(geo_mongo_metadata)


#class MirrorImage:
#
#   def __init__(self, image_path):
#      self.path = image_path
#
#   def store_in_geo_db():
      

class Flickr:

   api_key    = '9db4bbb1d275baedb6e77c2aa7538c90'
   api_secret = '09be4700c52c3996'

   def __init__(self):
      self.flickr = flickrapi.FlickrAPI(self.api_key, self.api_secret)
      # authenticate
      (token, frob) = self.flickr.get_token_part_one(perms='read')
      if not token: raw_input("Press ENTER after you authorized this program")
      self.flickr.get_token_part_two((token, frob))
      sys.stderr.write("Authed to Flickr\n")

   def connect_geodb(self):
      self.geodb_connection = pymongo.Connection('localhost', 27017)
      self.geodb_photos = self.geodb_connection.ltte.photos

   def query_bbox_and_upload_time_segment(self, bbox, min_upload_time, max_upload_time, limit):
      all_extras = "description,license,date_upload,date_taken,owner_name,icon_server,original_format,last_update,geo,tags,machine_tags,o_dims,views,media,path_alias"
      bbox_string = "%s,%s,%s,%s" % (bbox['left'], bbox['bottom'], bbox['right'], bbox['top'])
      photos_response = self.flickr.photos_search(bbox=bbox_string, min_upload_date=min_upload_time, max_upload_date=max_upload_time, per_page=limit, extras=all_extras, page=0)
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

   def mirror_image_count(self):
      self._mirror_image_count = 0
      def visit(self, dirname, names):
         #print dirname
	 for name in names:
	    if name[-4:] == "json":
	       self._mirror_image_count = self._mirror_image_count + 1
      os.path.walk("data/flickr_mirror", visit, self)
      return self._mirror_image_count

   def mirrored_images(self):
      farms = os.listdir("data/flickr_mirror/")
      for farm in farms:
         servers = os.listdir("data/flickr_mirror/" + farm)
	 for server in servers:
            photos = os.listdir("data/flickr_mirror/" + farm + "/" + server)
	    for photo in photos:
	       locator = farm + "/" + server + "/" + photo
               yield(FlickrPhoto(locator_path=locator))

   def foreach_local_photo(self, function):
      for photo in self.mirrored_images():
         function(photo)

flickr = Flickr()

def geo_store_all(args):
   flickr.connect_geodb()
   success = 0
   fail = 0
   for photo in flickr.mirrored_images():
      try:
         photo.store_in_geodb()
         success = success + 1
      except KeyboardInterrupt:
         print "User exited"
         exit()
      except:
         fail = fail + 1
      print "geodb insertion: " + str(success) + " succeeded, " + str(fail) + " failed"

if __name__ == "__main__":
   import argparse
   import sys
   
   parser = argparse.ArgumentParser()
   subparsers = parser.add_subparsers(dest='command')
   
   geo_store_all_parser = subparsers.add_parser('geo_store_all')
   geo_store_all_parser.set_defaults(func=geo_store_all)
   
   args = parser.parse_args()
   args.func(args)
