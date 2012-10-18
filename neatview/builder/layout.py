import numpy as np
from scipy.spatial import Delaunay

from ..db import ltte

def layout(clusters):
  cluster_centers = map(lambda cluster: cluster.center(), clusters)
  cluster_centers = np.array(cluster_centers)

  triangulation = Delaunay(cluster_centers)
  delaunay_vertices = triangulation.points.tolist()
  delaunay_triangles = triangulation.vertices.tolist()

  delaunay_triangulation = {
    'name'      : 'delaunay triangulation',
    'type'      : 'mesh',
    'vertices'  : triangulation.points.tolist(),
    'triangles' : delaunay_triangles
  }

  voronoi_vertices = map(lambda triangle: circumcenter(triangle, delaunay_vertices), delaunay_triangles)
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

  print "\n\n", delaunay_triangulation
  print "\n\n", voronoi_tesselation, "\n\n"

  ltte.debug.update({'name':delaunay_triangulation['name']}, delaunay_triangulation, upsert=True)
  ltte.debug.update({'name':voronoi_tesselation['name']},    voronoi_tesselation,    upsert=True)
  

  print "Triangulated centers of", len(clusters), "clusters"


def circumcenter(vertex_indices, vertices):
  (A, B, C) = map(lambda index: vertices[index], vertex_indices)
  D = 2*(A[0]*(B[1]-C[1]) + B[0]*(C[1]-A[1]) + C[0]*(A[1]-B[1]))

  def sq(x):
    return x*x
  
  x = ((sq(A[0])+sq(A[1]))*(B[1]-C[1]) + (sq(B[0])+sq(B[1]))*(C[1]-A[1]) + (sq(C[0])+sq(C[1]))*(A[1]-B[1])) / D
  y = ((sq(A[0])+sq(A[1]))*(C[0]-B[0]) + (sq(B[0])+sq(B[1]))*(A[0]-C[0]) + (sq(C[0])+sq(C[1]))*(B[0]-A[0])) / D

  return [x, y]

