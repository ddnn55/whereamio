#!/usr/bin/env python

import sys
import os
import time
import calendar
import json
import random
import web


import redis

#import dpy
import boundary
from dgeo import GeoGrid
import Flickr

#if(len(sys.argv) < 2):
#   print "Usage: " + sys.argv[0] + " mine_path"
#   sys.exit(0)

mine_path = "data/flickr_mine/New York-New York"

metadata = json.load(file(mine_path + "/metadata.json"))
bbox = metadata['bbox']
min_upload_time = metadata['min_upload_time']
max_upload_time = metadata['max_upload_time']

r = redis.StrictRedis(host='localhost', port=6379, db=0)
# if mine list does not exist, create it (with single top level quad)
unfinished_mines_key = mine_path + '_unfinished_mines'


#for mine in unfinished_mines:
   #print mine
#print str(len(unfinished_mines)) + " unfinished mines"


        
urls = (
    '/mines.json', 'mines',
    '/(.*)', 'status'
)
app = web.application(urls, globals())

class status:        
    def GET(self, name):
        if not name: 
            name = 'World'
        return file("MineStatus.html")

class mines:
    def GET(self):
        unfinished_mines = r.lrange(unfinished_mines_key, 0, -1)
        unfinished_mines = [ json.loads(mine_string) for mine_string in unfinished_mines ]
        return json.dumps(unfinished_mines)

if __name__ == "__main__":
    app.run()


"""
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
   pipe.lpop(unfinished_mines_key)
   pipe.execute()
"""
