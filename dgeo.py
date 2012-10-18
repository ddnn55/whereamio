#!/usr/bin/env python

import sys
import os
import math
import geopy
import json

def aspect_of_bbox(bbox):
   left   = bbox['left']
   right  = bbox['right']
   top    = bbox['top']
   bottom = bbox['bottom']
   
   middle_top    = geopy.point.Point(top, (left + right) / 2.0)
   middle_bottom = geopy.point.Point(bottom, (left + right) / 2.0)
   middle_right  = geopy.point.Point((top + bottom) / 2.0, right)
   middle_left   = geopy.point.Point((top + bottom) / 2.0, left)
   
   width  = geopy.distance.distance(middle_left, middle_right)
   height = geopy.distance.distance(middle_top, middle_bottom)

   return width.m / height.m

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

def ok_projection_aspect(left, right, top, bottom):
   degree_width  = (right - left)
   degree_height = (top - bottom)

   center_x = left + (right - left) / 2.0
   center_y = bottom + (top - bottom) / 2.0

   meter_width  = distance_on_spherical_earth(center_y, left, center_y, right)
   meter_height = distance_on_spherical_earth(bottom, center_x, top, center_x)

   return meter_width / meter_height
  
class LatLngBoundingBox:

   def __init__(self, bbox_dict):
      self.left = bbox_dict['left']
      self.right = bbox_dict['right']
      self.top = bbox_dict['top']
      self.bottom = bbox_dict['bottom']
      self.bbox_dict = bbox_dict

   def __str__(self):
      return json.dumps(self.bbox_dict)

   def aspect(self):
      middle_top    = geopy.point.Point(self.top, (self.left + self.right) / 2.0)
      middle_bottom = geopy.point.Point(self.bottom, (self.left + self.right) / 2.0)
      middle_right  = geopy.point.Point((self.top + self.bottom) / 2.0, self.right)
      middle_left   = geopy.point.Point((self.top + self.bottom) / 2.0, self.left)
   
      width  = geopy.distance.distance(middle_left, middle_right)
      height = geopy.distance.distance(middle_top, middle_bottom)

      return width.m / height.m

   def width(self):
      return self.right - self.left
   
   def height(self):
      return self.top - self.bottom

   def normalize(self, point):
      normal = point
      normal[0] = (point[0] - self.bottom) / self.height()
      normal[1] = (point[1] - self.left) / self.width()
      return normal

   def contains(self, point):
      return self.left <= point[1] and self.right >= point[1] and self.top >= point[0] and self.bottom <= point[0]

class GeoGridCell:

   def __init__(self, left, right, top, bottom, row, column):
      self.top    = top
      self.left   = left
      self.bottom = bottom
      self.right  = right

      self.row = row
      self.column = column

   def center(self):
      return ( (self.left + self.right) / 2.0, (self.top + self.bottom) / 2.0 )

   def toDict(self):
      data = { "bounds": {}, "location": {} }
      data['bounds']['left'] = self.left
      data['bounds']['right'] = self.right
      data['bounds']['top'] = self.top
      data['bounds']['bottom'] = self.bottom
      data['location']['row'] = self.row
      data['location']['column'] = self.column
      return data

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

            cell = GeoGridCell(cell_degree_left, cell_degree_right, cell_degree_top, cell_degree_bottom, y, x)
            cell_callback(cell)

if __name__ == "__main__":
   
   # do a test

   def print_center(cell):
      print cell.center()

   nyc = GeoGrid(-74.034805, -73.891296, 40.800296, 40.66866, 5)
   print "Rows: " + str(nyc.rows)
   print "Columns: " + str(nyc.columns)
   nyc.foreach_cell(print_center)
