#!/usr/bin/env python

import sys
import os

import dpy

import flickrfacemap
import georacedata

if len(sys.argv) < 4:
   print "\nUsage: " + sys.argv[0] + " name timestamp social_explorer_csv [tile_border_fraction]\n\nMaps:\n-----------"
   
   task_queues_directory = "data/tasks/flickr_geo_face/"
   for root, dirs, files in os.walk(task_queues_directory):
      for d in dirs:
         print d

   print " "
   sys.exit(0)

name      = sys.argv[1]
timestamp = sys.argv[2]
socialexplorer_csv = sys.argv[3]

border_fraction = 0.0
try:
   border_fraction = float(sys.argv[4])
except:
   pass

census_data = True

facemap = flickrfacemap.FlickrFaceMap(name, timestamp)
facemap.save_big_image(border_fraction)

race_out_dir = "data/facerace"
race_plot_path = race_out_dir + "/race_" + name + "_" + timestamp + ".jpg"
dpy.ensure_dir(race_out_dir)
racemap = georacedata.GeoRaceData(socialexplorer_csv)
race_image = racemap.get_image()
race_image.save(race_plot_path)
print "Saved race plot to " + race_plot_path
