#!/usr/bin/env python

import sys
import os
import time
import calendar
import json

#import dpy
import boundary
from dgeo import GeoGrid
import Flickr

if(len(sys.argv) < 2):
   print "Usage: " + sys.argv[0] + " mine_path"
   sys.exit(0)

mine_path = sys.argv[1]

metadata = json.load(file(mine_path + "/metadata.json"))
bbox = metadata['bbox']

mine = Flickr.GeoMine(bbox, 2011)
while mine.might_be_truncated():
   children = list(mine.children())
   mine = children[2]


exit()



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
