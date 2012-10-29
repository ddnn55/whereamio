from math import atan2
import json

import numpy as np
from scipy.spatial import Delaunay

from ..db import ltte

def layout(tile):
  clusters = list(tile.clusters())
  cluster_centers = map(lambda cluster: cluster.center(), clusters)
  cluster_centers_np = np.array(cluster_centers)

  triangulation = Delaunay(cluster_centers_np)
  delaunay_vertices = triangulation.points.tolist()
  delaunay_triangles = triangulation.vertices.tolist()

  delaunay_triangulation = {
    'name'      : 'delaunay triangulation',
    'type'      : 'mesh',
    'vertices'  : triangulation.points.tolist(),
    'triangles' : delaunay_triangles
  }

  voronoi_vertices = map(lambda triangle: circumcenter(triangle, delaunay_vertices), delaunay_triangles)
  layout_data = {}
  layout_data['voronoi_vertices'] = voronoi_vertices
  layout_data['clusters'] = map(lambda cluster: cluster.display_data(), clusters)
  for cluster in layout_data['clusters']:
    cluster['voronoi_vertices'] = []
  for voronoi_vertex_index in range(0, len(voronoi_vertices)):
    delaunay_triangle = triangulation.vertices[voronoi_vertex_index]
    for cluster_index in delaunay_triangle:
      layout_data['clusters'][cluster_index]['voronoi_vertices'].append(voronoi_vertex_index)
  for cluster in layout_data['clusters']:
    cluster['voronoi_vertices'] = sorted(
      cluster['voronoi_vertices'],
      key = lambda voronoi_vertex_index: angle(cluster['center'], voronoi_vertices[voronoi_vertex_index])
    )

  voronoi_segments = []
  frontier = [ triangulation.vertex_to_simplex[0] ]
  visited = set()
  while len(frontier) > 0:
    t = frontier.pop(0)
    neighbors = triangulation.neighbors[t]
    for neighbor in neighbors.tolist():
      if neighbor not in visited:
        voronoi_segments.append([int(t), int(neighbor)])
	frontier.append(neighbor)
    visited.add(t)

  voronoi_tesselation = {
    'name'     : 'voronoi tesselation',
    'type'     : 'voronoi',
    'vertices' : voronoi_vertices,
    'segments' : voronoi_segments
  }

  ltte.debug.update({'name':delaunay_triangulation['name']}, delaunay_triangulation, upsert=True)
  ltte.debug.update({'name':voronoi_tesselation['name']},    voronoi_tesselation,    upsert=True)

  print "Triangulated centers of", len(clusters), "clusters"

  tile_filename = 'static/tile/all'
  tile_file = file(tile_filename, 'w')
  json.dump(layout_data, tile_file)
  print "Saved layout to " + tile_filename

def angle(lat_lng_a, lat_lng_b):
  return atan2(lat_lng_a[0] - lat_lng_b[0], lat_lng_a[1] - lat_lng_b[1])

def circumcenter(vertex_indices, vertices):
  (A, B, C) = map(lambda index: vertices[index], vertex_indices)
  D = 2*(A[0]*(B[1]-C[1]) + B[0]*(C[1]-A[1]) + C[0]*(A[1]-B[1]))

  def sq(x):
    return x*x
  
  x = ((sq(A[0])+sq(A[1]))*(B[1]-C[1]) + (sq(B[0])+sq(B[1]))*(C[1]-A[1]) + (sq(C[0])+sq(C[1]))*(A[1]-B[1])) / D
  y = ((sq(A[0])+sq(A[1]))*(C[0]-B[0]) + (sq(B[0])+sq(B[1]))*(A[0]-C[0]) + (sq(C[0])+sq(C[1]))*(B[0]-A[0])) / D

  return [x, y]

