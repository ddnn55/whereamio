#!/usr/bin/env python

import sys
import os
import json

import geoflickrfacefinder

# list open tasks
if len(sys.argv) < 3:
   print "\nUsage: " + sys.argv[0] + " name timestamp\n\nOpen tasks:\n-----------"
   
   task_queues_directory = "data/tasks/flickr_geo_face/"
   for root, dirs, files in os.walk(task_queues_directory):
      for d in dirs:
         print d

   print " "
   sys.exit(0)

# run tasks
name = sys.argv[1]
timestamp = sys.argv[2]

task_queue_directory = "data/tasks/flickr_geo_face/"+name+"/"+timestamp

gfff = geoflickrfacefinder.GeoFlickrFaceFinder(name, timestamp)

for task_filename in os.listdir(task_queue_directory):
   task_filepath = task_queue_directory + "/" + task_filename

   print "starting task " + task_filepath

   cell_dict = json.load(file(task_filepath))
   #TODO maybe set a timeout for how long before we kill the task?
   gfff.cellTask(cell_dict)

   os.remove(task_filepath)
