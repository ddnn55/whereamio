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

import dpy
import boundary
from dgeo import GeoGrid
#import Flickr


r = redis.StrictRedis(host='localhost', port=6379, db=0)
unfinished_mines_key = 'unfinished_mines'


#app = web.application(urls, globals())
app = Flask(__name__)

@app.route('/')
def console():
    print "this function------------------------------------"
    return file("static/Console.html").read()

@app.route('/mean_shift')
def mean_shift():
    lat = float(request.args['lat'])
    lat = float(request.args['lng'])
    print str(request.args) + "--------"
    return "yo"

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
    return file(image_path)
    return photo
    server = dpy.random_item(os.path.listdir("data/flickr_mirror"))

@app.route('/delete_all_mines')
def delete_all():
    r.delete(unfinished_mines_key)

@app.route('/mines.json')
def mines():
    unfinished_mines = r.lrange(unfinished_mines_key, 0, -1)
    unfinished_mines = [ json.loads(mine_string) for mine_string in unfinished_mines ]
    return json.dumps(unfinished_mines)





if __name__ == "__main__":
  #  app.run()
  # Bind to PORT if defined, otherwise default to 5000.
  #port = int(os.environ.get('PORT', 5001))
  #app.run(host='0.0.0.0', port=port, debug=True)
  app.run(debug=True)
