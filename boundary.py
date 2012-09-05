#!/usr/bin/env python

import shapefile
import Image, ImageDraw

PLOT_WIDTH = 512

r = shapefile.Reader("data/USA_adm/USA_adm2")
#sr = r.shapeRecords()
#sr_test = sr[10]
#print sr_test.shape.points

left = None
right = None
top = None
bottom = None

# find nyc
nyc = None
for sr in r.shapeRecords():
  if sr.record[4] == "New York" and sr.record[6] == "New York":
    nyc = sr

# calculate bounding box
left = nyc.shape.points[0][0]
right = nyc.shape.points[0][0]
top = nyc.shape.points[0][1]
bottom = nyc.shape.points[0][1]
for point in nyc.shape.points:
  left = min(left, point[0])
  right = max(right, point[0])
  bottom = min(bottom, point[1])
  top = max(top, point[1])
print (left, right, bottom, top)

# plot shape
llwidth = right - left
llheight = top - bottom
aspect = llwidth / llheight
height = int(PLOT_WIDTH / aspect)
plot = Image.new("L", (PLOT_WIDTH, height))
# convert to plot coordinates
plot_points = map(lambda p: ( PLOT_WIDTH * (p[0] - left) / llwidth, height - height * (p[1] - bottom) / llheight), nyc.shape.points)

draw = ImageDraw.Draw(plot)
previous_point = nyc.shape.points[0]
draw.line(plot_points, fill = 128)

plot.save("data/debug/nyc.jpg")
