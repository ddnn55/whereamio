#!/usr/bin/env python

FACE_TILE_SIZE = 256

import sys
import os
import urllib2
import flickrapi
import json
import pprint
import time, calendar
from datetime import timedelta
import math
from PIL import Image
import glob


pp = pprint.PrettyPrinter(indent=3)

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

   def getPhotos(self, bounds, limit):

      print "start getPhotosAtLatLng"

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


class FaceCell:

   def __init__(self, cell_dir, row, column, facemap):
      self.cell_dir = cell_dir
      self.row = row
      self.column = column
      self.facemap = facemap

   def flickr_photo(self):
      jpg_files  = glob.glob(self.cell_dir + "/*.jpg")
      flickr_locator_string = jpg_files[0].split('.')[0]
      photo = FlickrPhoto(locator_string=flickr_locator_string, flickr=self.facemap.flickrPhotos)
      return photo
      

   def get_cropped_image(self):
      json_files = glob.glob(self.cell_dir + "/*.json")
      jpg_files  = glob.glob(self.cell_dir + "/*.jpg")

      tag = json.load(file(json_files[0]))
      face_image = Image.open(jpg_files[0])

      image_width  = face_image.size[0]
      image_height = face_image.size[1]

      face_pixel_center_x = (tag['center']['x'] / 100.0) * image_width
      face_pixel_center_y = (tag['center']['y'] / 100.0) * image_height

      face_pixel_width  = (tag['width'] / 100.0)  * image_width
      face_pixel_height = (tag['height'] / 100.0) * image_height
      face_pixel_size = max(face_pixel_width, face_pixel_height)

      face_pixel_left   = face_pixel_center_x - face_pixel_size / 2.0
      face_pixel_right  = face_pixel_center_x + face_pixel_size / 2.0
      face_pixel_bottom = face_pixel_center_y - face_pixel_size / 2.0
      face_pixel_top    = face_pixel_center_y + face_pixel_size / 2.0

      face_image = face_image.crop((int(face_pixel_left), int(face_pixel_bottom), int(face_pixel_right), int(face_pixel_top)))
      face_image = face_image.resize((FACE_TILE_SIZE, FACE_TILE_SIZE), Image.ANTIALIAS)

      return face_image
      


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

   def interactive_dir(self):
      return "data/faceit_interactive/" + self.session_name + "_" + self.session_timestamp

   def saveInteractiveMap(self):
      bounds = self.get_grid_bounds()
      pixel_width  = bounds['columns'] * FACE_TILE_SIZE
      pixel_height = bounds['rows']    * FACE_TILE_SIZE

      out_dir = self.interactive_dir()
      if not os.path.exists(out_dir):
	 os.makedirs(out_dir)

      self.html_file = open(out_dir + "/index.html", "w")
      self.foreach_face_cell(self.place_in_html_file)
      self.html_file.close()
      
      print "Saved " + out_dir + "/index.html"

   def place_in_html_file(self, cell):
      x = cell.column * FACE_TILE_SIZE
      y = cell.row    * FACE_TILE_SIZE

      image_relative_url_dir = "images/" + str(x) + "/" + str(y)
      image_dir = self.interactive_dir() + "/" + image_relative_url_dir
      if not os.path.exists(image_dir):
	 os.makedirs(image_dir)

      cell.get_cropped_image().save(image_dir + "/face.jpg")

      self.html_file.write('<a href="'+cell.flickr_photo().page_url()+'">')
      self.html_file.write('<img style="position:absolute;left:'+str(x)+';top:'+str(y)+';" src="'+image_relative_url_dir+'/face.jpg"></a>')
      
      

   def saveBigImage(self):
      bounds = self.get_grid_bounds()
      pixel_width  = bounds['columns'] * FACE_TILE_SIZE
      pixel_height = bounds['rows']    * FACE_TILE_SIZE

      self.big_image = Image.new('RGBA', (pixel_width, pixel_height))
      self.foreach_face_cell(self.place_in_big_image)

      out_dir = "data/faceit"
      if not os.path.exists(out_dir):
	 os.makedirs(out_dir)
      out_path = out_dir + "/face_" + self.session_name + "_" + self.session_timestamp + ".jpg"
      self.big_image.save(out_path)
      
      print "Saved " + out_path

   def place_in_big_image(self, cell):
      x = cell.column * FACE_TILE_SIZE
      y = cell.row    * FACE_TILE_SIZE

      self.big_image.paste(cell.get_cropped_image(), (x, y))

      print "Pasted at " + str(x) + " " + str(y)


   def get_grid_bounds(self):
      min_row = None
      max_row = None
      min_column = None
      max_column = None

      row_dirs = os.listdir(self.root_face_image_dir)

      for row_name in row_dirs:
         column_dirs = os.listdir(self.root_face_image_dir + "/" + row_name)
         for column_name in column_dirs:
            if min_row == None:
               min_row    = int(row_name)
               max_row    = int(row_name)
               min_column = int(column_name)
               max_column = int(column_name)
            else:
               if int(row_name) < min_row:
		  min_row    = int(row_name)
               if int(row_name) > max_row:
		  max_row    = int(row_name)
               if int(column_name) < min_column:
		  min_column = int(column_name)
               if int(column_name) > max_column:
		  max_column = int(column_name)

      columns = (max_column - min_column + 1)
      rows    = (max_row    - min_row    + 1)

      return {'min_column': min_column, 'max_column': max_column, 'max_row': max_row, 'min_row': min_row, 'columns': columns, 'rows': rows}


   def foreach_face_cell(self, callback):
      row_dirs = os.listdir(self.root_face_image_dir)
      r = 0
      for row_name in row_dirs:
         r = r + 1
         print str(r) + " / " + str(len(row_dirs)) + " rows"

         column_dirs = os.listdir(self.root_face_image_dir + "/" + row_name)
         for column_name in column_dirs:
            cell_dir = self.root_face_image_dir + "/" + row_name + "/" + column_name

            column = int(column_name)
            row    = int(row_name)

            cell = FaceCell(cell_dir, row, column, self)
            callback(cell)

