#!/usr/bin/env python

import sys
import os
import math

def distance_on_spherical_earth(lat1, long1, lat2, long2):

    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
        
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
        
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
        
    # Compute spherical distance from spherical coordinates.
        
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
    
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )

    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc * 6378100

class GeoGridCell:

   def __init__(self, left, right, top, bottom):
      self.top    = top
      self.left   = left
      self.bottom = bottom
      self.right  = right

   def center(self):
      return ( (self.left + self.right) / 2.0, (self.top + self.bottom) / 2.0 )

class GeoGrid:

   def __init__(self, left, right, top, bottom, columns):
      self.top    = top
      self.left   = left
      self.bottom = bottom
      self.right  = right

      self.degree_width  = (self.right - self.left)
      self.degree_height = (self.top - self.bottom)

      self.center_x = self.left + (self.right - self.left) / 2.0
      self.center_y = self.bottom + (self.top - self.bottom) / 2.0

      self.meter_width  = distance_on_spherical_earth(self.center_y, self.left, self.center_y, self.right)
      self.meter_height = distance_on_spherical_earth(self.bottom, self.center_x, self.top, self.center_x)

      self.columns = columns
      self.rows = int(self.columns * self.meter_height / self.meter_width)

   def foreach_cell(self, cell_callback):
      for x in range(0, self.columns):
	 for y in range(0, self.rows):

            cell_degree_width  = self.degree_width  * 1.0 / self.columns
            cell_degree_height = self.degree_height * 1.0 / self.rows

	    cell_degree_left   = self.left + cell_degree_width  * x
	    cell_degree_right  = cell_degree_left + cell_degree_width
	    cell_degree_bottom = self.bottom + cell_degree_height * y
	    cell_degree_top    = cell_degree_bottom + cell_degree_height

            cell = GeoGridCell(cell_degree_left, cell_degree_right, cell_degree_top, cell_degree_bottom)
            cell_callback(cell)

if __name__ == "__main__":
   
   # do a test

   def print_center(cell):
      print cell.center()

   nyc = GeoGrid(-74.034805, -73.891296, 40.800296, 40.66866, 5)
   print "Rows: " + str(nyc.rows)
   print "Columns: " + str(nyc.columns)
   nyc.foreach_cell(print_center)
