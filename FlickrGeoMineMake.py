#!/usr/bin/env python

import sys
import os
import time
import calendar
import json

#import dpy
import boundary
from dgeo import GeoGrid

if(len(sys.argv) < 3):
   print "Usage: " + sys.argv[0] + " state county"
   sys.exit(0)

state    = sys.argv[1]
county   = sys.argv[2]
#columns  = float(sys.argv[3])
#right   = float(sys.argv[4])
#name    = sys.argv[6]


def make_task(cell):
   task_filename = str(cell.row)+"_"+str(cell.column)+".json"
   task_file = open(task_queue_directory+"/"+task_filename, "w")
   task_file.write(json.dumps(cell.toDict()))

boundary = boundary.Boundary(state, county)

mine_directory = "data/flickr_mine/" + boundary.name
if not os.path.exists(mine_directory):
   os.makedirs(mine_directory)

metadata = dict()
metadata["bbox"] = boundary.bbox()
metadata_file = open(mine_directory+"/metadata.json", "w")
metadata_file.write(json.dumps(metadata))

print "Created mine " + mine_directory

#grid = GeoGrid(left, right, top, bottom, columns)
#grid.foreach_cell(make_task)
