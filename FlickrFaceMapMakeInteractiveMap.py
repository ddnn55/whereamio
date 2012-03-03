#!/usr/bin/env python

import sys
import os

import flickrfacemap

if len(sys.argv) < 3:
   print "\nUsage: " + sys.argv[0] + " name timestamp\n\nMaps:\n-----------"
   
   task_queues_directory = "data/tasks/flickr_geo_face/"
   for root, dirs, files in os.walk(task_queues_directory):
      for d in dirs:
         print d

   print " "
   sys.exit(0)

name      = sys.argv[1]
timestamp = sys.argv[2]

facemap = flickrfacemap.FlickrFaceMap(name, timestamp)
facemap.saveInteractiveMap()
