#!/usr/bin/env python

import os
import calendar
import time
import random

def ensure_dir(dir_path):
   if not os.path.exists(dir_path):
      os.makedirs(dir_path)

def now():
   unix_time = calendar.timegm(time.gmtime())
   return unix_time

def random_item(items):
   return items[random.randint(0, len(items)-1)]

def random_color3f():
   return (random.random(), random.random(), random.random())
