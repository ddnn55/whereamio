#!/usr/bin/env python

import sys
import os
import time
import calendar

import redis


if(len(sys.argv) < 2):
   print "Usage: " + sys.argv[0] + " mine_path"
   sys.exit(0)

mine_path = sys.argv[1]

r = redis.StrictRedis(host='localhost', port=6379, db=0)
unfinished_mines_key = mine_path + '_unfinished_mines'
started_mining_key = mine_path + '_started_mining'
r.delete(unfinished_mines_key)
r.delete(started_mining_key)
