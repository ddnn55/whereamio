#!/usr/bin/env python

import shapefile
import Image, ImageDraw

PLOT_WIDTH = 1024

#sr = r.shapeRecords()
#sr_test = sr[10]
#print sr_test.shape.points

r = shapefile.Reader("data/USA_adm/USA_adm2")

class Boundary:
  def __init__(self, state, keys):
    self.name = state + "-" + str(keys)

    self.left = None
    self.right = None
    self.top = None
    self.bottom = None

    self.records = []
    for sr in r.shapeRecords():
      if sr.record[4] == state and sr.record[6] in keys:
        self.records.append(sr)
        print sr.record

    # calculate bounding box
    self.left = self.records[0].shape.points[0][0]
    self.right = self.records[0].shape.points[0][0]
    self.top = self.records[0].shape.points[0][1]
    self.bottom = self.records[0].shape.points[0][1]
    for record in self.records:
      for point in record.shape.points:
        self.left = min(self.left, point[0])
        self.right = max(self.right, point[0])
        self.bottom = min(self.bottom, point[1])
        self.top = max(self.top, point[1])
    print (self.left, self.right, self.bottom, self.top)

  def bbox(self):
    bbox = dict()
    bbox['left']   = self.left
    bbox['right']  = self.right
    bbox['top']    = self.top
    bbox['bottom'] = self.bottom
    return bbox

  def llwidth(self):
    return self.right - self.left

  def llheight(self):
    return self.top - self.bottom

  def plot(self):
    aspect = self.llwidth() / self.llheight()
    height = int(1.4 * PLOT_WIDTH / aspect) # TODO 1.4 is complete hack, do a semi decent projection.
    plot = Image.new("L", (PLOT_WIDTH, height))
    # convert to plot coordinates
    plot_shapes = []
    for record in self.records:
      plot_shapes.append(map(lambda p: ( PLOT_WIDTH * (p[0] - self.left) / self.llwidth(), height - height * (p[1] - self.bottom) / self.llheight()), record.shape.points))

    draw = ImageDraw.Draw(plot)
    for plot_points in plot_shapes:
      draw.line(plot_points, fill = 255)

    plot.save("data/debug/" + self.name + ".jpg")

if __name__ == "__main__":
  nyc = Boundary("New York", ["New York", "Queens", "Bronx", "Kings", "Richmond"], r)
  nyc.plot()
  la = Boundary("California", ["Los Angeles"], r)
  la.plot()
  atl = Boundary("Georgia", ["Fulton"], r)
  atl.plot()
  chi = Boundary("Illinois", ["Cook", "DuPage"], r)
  chi.plot()
