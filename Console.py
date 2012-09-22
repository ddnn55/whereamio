#!/usr/bin/env python

import sys
import os
import time
import calendar
import json
import random
#import web
from flask import Flask
from flask import request

import redis
import pymongo
from bson import objectid

import dpy
import boundary
from dgeo import GeoGrid

#import Flickr
import GeoMeanShift


r = redis.StrictRedis(host='localhost', port=6379, db=0)
unfinished_mines_key = 'unfinished_mines'

m = pymongo.Connection()
mean_shifts = m.ltte.mean_shifts
clusters = m.ltte.clusters
photos = m.ltte.photos

#app = web.application(urls, globals())
app = Flask(__name__)

@app.route('/')
def console():
    print "this function------------------------------------"
    return file("static/Console.html").read()

@app.route('/mean_shift')
def mean_shift():
    lat = float(request.args['lat'])
    lng = float(request.args['lng'])
    print str(lat) + ", " + str(lng)
    ms = GeoMeanShift.GeoMeanShift([lat, lng], 0.005)
    start_id = mean_shifts.insert( { 'index': 0,  'first': True, 'location': [lat, lng] } )
    print start_id
    i = 1
    while not ms.done():
       ms.step()
       lat = ms.current_mean()[0]
       lng = ms.current_mean()[1]
       mean_shifts.insert( { 'start': start_id, 'index': i,  'location': [lat, lng] } )
       print ms.current_mean()
       i = i + 1
    return "yo"

@app.route('/clusters', methods=['GET'])
def sklearn_mean_shifts_json():
   left   = float(request.args['left'])
   right  = float(request.args['right'])
   top    = float(request.args['top'])
   bottom = float(request.args['bottom'])
   _clusters = []
   #for cluster in skmeanshifts.find({'location': {'$within': {'$box': [[bottom, left], [top, right]]}}}):
   for cluster in clusters.find():
      point = {'center': cluster['center'], '_id': str(cluster['_id'])}
      _clusters.append(point)
   return json.dumps(_clusters)

@app.route('/cluster/<cluster_id>')
def cluster(cluster_id):
   import Flickr
   html = ""
   count = 0
   oid = objectid.ObjectId(cluster_id)
   print oid
   for photo in photos.find({'cluster':oid}):
      mi = Flickr.MirroredPhoto(photo)
      html = html + '<img src="/static/flickr/' + mi.flickr_locator_path() + '/b.jpg">'
      html = html + photo['flickr']['title']
      html = html + photo['flickr']['tags']
      html = html + "<br>"
      count = count + 1
   html = str(count) + "<br>" + html
   return html

@app.route('/mean_shifts.json', methods=['GET'])
def mean_shifts_json():
   print "starting meanshifts getter"
   left   = float(request.args['left'])
   right  = float(request.args['right'])
   top    = float(request.args['top'])
   bottom = float(request.args['bottom'])
   paths = []
   for first in mean_shifts.find({'first': True, 'location': {'$within': {'$box': [[bottom, left], [top, right]]}}}):
      points = [first['location']]
      for point in mean_shifts.find({'start':first['_id']}).sort('index', 1):
         points.append(point['location'])
      paths.append(points)
   return json.dumps(paths)

@app.route('/create_mine', methods=['POST'])
def create_mine():
    data = request.form.items()[0][0]
    #return
    r.rpush(unfinished_mines_key, data)
    #print data
    return "cool"

@app.route('/image_count')
def image_count():
    return Flickr.flickr.mirror_image_count()

@app.route('/random')
def random():
    farm = dpy.random_item(os.listdir("data/flickr_mirror/"))
    server = dpy.random_item(os.listdir("data/flickr_mirror/" + farm))
    photo = dpy.random_item(os.listdir("data/flickr_mirror/" + farm + "/" + server))
    image_path = "data/flickr_mirror/" + farm + "/" + server + "/" + photo + "/b.jpg"
    return file(image_path).read()
    return photo
    server = dpy.random_item(os.path.listdir("data/flickr_mirror"))

@app.route('/delete_all_mines')
def delete_all():
    r.delete(unfinished_mines_key)
    return "cool"

@app.route('/mines.json')
def mines():
    unfinished_mines = r.lrange(unfinished_mines_key, 0, -1)
    unfinished_mines = [ json.loads(mine_string) for mine_string in unfinished_mines ]
    return json.dumps(unfinished_mines)





if __name__ == "__main__":
  #  app.run()
  # Bind to PORT if defined, otherwise default to 5000.
  #port = int(os.environ.get('PORT', 5001))
  app.run(host='0.0.0.0', port=5000, debug=True)
  #app.run(debug=True)

