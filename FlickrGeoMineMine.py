#!/usr/bin/env python

import sys
import os
import time
import calendar
import json
import random

import redis

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
min_upload_time = metadata['min_upload_time']
max_upload_time = metadata['max_upload_time']

r = redis.StrictRedis(host='localhost', port=6379, db=0)
# if mine list does not exist, create it (with single top level quad)
unfinished_mines_key = mine_path + '_unfinished_mines'
started_mining_key = mine_path + '_started_mining'
if r.get(started_mining_key) == None:
   print "Initializing " + mine_path + " in Redis ..."
   unfinished_mines_value = json.dumps(bbox)
   pipe = r.pipeline(transaction=True)
   pipe.rpush(unfinished_mines_key, unfinished_mines_value)
   pipe.set(started_mining_key, True)
   pipe.execute()

# for unfinished mines in mine list:
while r.llen(unfinished_mines_key) > 0:
   pipe = r.pipeline(transaction=True)
   unfinished_mine_bbox = json.loads(r.lindex(unfinished_mines_key, 0))
   mine = Flickr.GeoMine(unfinished_mine_bbox, min_upload_time, max_upload_time)
   if mine.might_be_truncated():
#     break mine into children
      for child in mine.children():
         pipe.rpush(unfinished_mines_key, json.dumps(child.bbox))
   else:
#     download photos (and their metadata) in mine, mark mine finished
      print "Reached quadtree leaf with " + str(len(mine.results)) + " photos"
      mine.store_photos_and_metadata()
   pipe.lpop(unfinished_mines_key)
   pipe.execute()
