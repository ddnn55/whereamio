#!/usr/bin/env python

import Flickr
import dgeo
import geopy
from geopy import distance, point
import math

class GeoMeanShift:

   def __init__(self, initial_point, radius):
      self.mean = list()
      self.mean.append(point.Point(initial_point[0], initial_point[1]))
      self.radius = radius

   def weight_kernel(self, d):
      return math.exp( - d * d )

   def step(self):
      current_total_weight = 0.0
      current_mean = self.mean[-1]
      running_average = [0.0, 0.0]
      for photo in Flickr.flickr.points_in_circle(self.mean[-1], self.radius):
         #current_mean = self.mean[-1]
	 pt = point.Point(photo['location'][0], photo['location'][1])
	 d = distance.distance(pt, current_mean).km
	 weight = self.weight_kernel(d)

         weighted_pt = [weight * pt[0], weight * pt[1]]
	 weighted_running_average = [current_total_weight * running_average[0], current_total_weight * running_average[1]]

	 new_x = (weighted_pt[0] + weighted_running_average[0]) / (weight + current_total_weight)
	 new_y = (weighted_pt[1] + weighted_running_average[1]) / (weight + current_total_weight)
	 running_average = point.Point(new_x, new_y)
	 current_total_weight = current_total_weight + weight

         #print running_average
      print "new_mean: " + str(running_average[0]) + ", " + str(running_average[1])
      self.mean.append(running_average)
         
if __name__ == "__main__":
   initial = [40.777194,-73.958545]
   target = [40.779388,-73.963437]
   delta = [abs(initial[0] - target[0]), abs(initial[1] - target[1])]
   dist = 1.0 * math.sqrt( delta[0] * delta[0] + delta[1] * delta[1] )
   print dist
   #radius = dgeo.approx_meters_to_degrees_at_location(500, center)
   ms = GeoMeanShift([40.777194,-73.958545], dist) # near metropolitan museum of art
   ms = GeoMeanShift([40.777194,-73.958545], dist)
   while True:
      ms.step()
