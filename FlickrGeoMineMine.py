#!/usr/bin/env python

import sys
import os
import time
import calendar
import json
import random

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
   mine = children[random.randint(0, len(children)-1)]


