#!/usr/bin/env python

import sys
import os
import json

import flickrfacemap

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

gfff = flickrfacemap.FlickrFaceMap(name, timestamp)

tasks_succeeded = 0
tasks_failed = 0
tasks_remaining = len(os.listdir(task_queue_directory))
for task_filename in os.listdir(task_queue_directory):
   task_filepath = task_queue_directory + "/" + task_filename

   print "tasks: " + str(tasks_succeeded) + " succeeded. " + str(tasks_failed) + " failed. " + str(tasks_remaining) + " remaining."
   print "face api: " + gfff.face_api_pretty_status()

   tasks_remaining = tasks_remaining - 1

   try:
      cell_dict = json.load(file(task_filepath))
      #TODO maybe set a timeout for how long before we kill the task?
      gfff.cellTask(cell_dict)

      os.remove(task_filepath)
      tasks_succeeded = tasks_succeeded + 1
   except KeyboardInterrupt:
      print "User cancelled tasks."
      sys.exit(0)
   except:
      print "Task " + task_filepath + " failed, so did not delete task file. Moving on."
      tasks_failed = tasks_failed + 1
      pass
