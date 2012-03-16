#!/usr/bin/env python

import sys
import os

import flickrfacemap

if len(sys.argv) < 3:
   print "\nUsage: " + sys.argv[0] + " name timestamp [tile_border_fraction]\n\nMaps:\n-----------"
   
   task_queues_directory = "data/tasks/flickr_geo_face/"
   for root, dirs, files in os.walk(task_queues_directory):
      for d in dirs:
         print d

   print " "
   sys.exit(0)

name      = sys.argv[1]
timestamp = sys.argv[2]

border_fraction = 0.0
try:
   border_fraction = float(sys.argv[3])
except:
   pass

facemap = flickrfacemap.FlickrFaceMap(name, timestamp)
facemap.saveBigImage(border_fraction)
