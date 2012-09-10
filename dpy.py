#!/usr/bin/env python

import os
import calendar
import time

def ensure_dir(dir_path):
   if not os.path.exists(dir_path):
      os.makedirs(dir_path)

def now():
   unix_time = calendar.timegm(time.gmtime())
   return unix_time
