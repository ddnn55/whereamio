#!/usr/bin/env python

import sys
import os
import time
import calendar
import json

from geogrid import GeoGrid

if(len(sys.argv) < 7):
   print "Usage: " + sys.argv[0] + " left right top bottom columns name"
   sys.exit(0)

top     = float(sys.argv[1])
left    = float(sys.argv[2])
bottom  = float(sys.argv[3])
right   = float(sys.argv[4])
columns = int(sys.argv[5])
name    = sys.argv[6]

def now():
   unix_time = calendar.timegm(time.gmtime())
   return unix_time

task_queue_directory = "data/tasks/flickr_geo_face/"+name+"/"+str(now())
if not os.path.exists(task_queue_directory):
   os.makedirs(task_queue_directory)

def make_task(cell):
   task_filename = str(cell.row)+"_"+str(cell.column)+".json"
   task_file = open(task_queue_directory+"/"+task_filename, "w")
   task_file.write(json.dumps(cell.toDict()))

grid = GeoGrid(left, right, top, bottom, columns)
grid.foreach_cell(make_task)
