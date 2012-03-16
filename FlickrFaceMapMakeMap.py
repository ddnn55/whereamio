#!/usr/bin/env python

import sys
import os

import dpy

import flickrfacemap
import georacedata

if len(sys.argv) < 9:
   # TODO store lat lng bounds in session, yessir.
   print "\nUsage: " + sys.argv[0] + " name timestamp social_explorer_csv tile_border_fraction left right top bottom \n\nMaps:\n-----------"

   task_queues_directory = "data/tasks/flickr_geo_face/"
   for root, dirs, files in os.walk(task_queues_directory):
      for d in dirs:
         print d

   print " "
   sys.exit(0)

name      = sys.argv[1]
timestamp = sys.argv[2]
socialexplorer_csv = sys.argv[3]

border_fraction = 0.0
try:
   border_fraction = float(sys.argv[4])
except:
   pass

facemap = flickrfacemap.FlickrFaceMap(name, timestamp)
face_image = facemap.get_big_image(border_fraction)

left   = float(sys.argv[5])
right  = float(sys.argv[6])
top    = float(sys.argv[7])
bottom = float(sys.argv[8])

racemap = georacedata.GeoRaceData(socialexplorer_csv)
race_image = racemap.get_image(face_image.size[0], (left, right, top, bottom))

race_image.paste(face_image, (0, 0), face_image) # need to use the image as mask too if you want to use its alpha channel, cuz this API is retarded.

facerace_out_dir = "data/facerace"
dpy.ensure_dir(facerace_out_dir)
facerace_path = facerace_out_dir + "/facerace_" + name + "_" + timestamp + ".jpg"
race_image.save(facerace_path)
#face_image.save(facerace_path)
print "Saved face race map to " + facerace_path
