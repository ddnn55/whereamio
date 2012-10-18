import numpy as np
from scipy.spatial import Delaunay

from ..db import ltte

def layout(clusters):
  cluster_centers = map(lambda cluster: cluster.center(), clusters)
  cluster_centers = np.array(cluster_centers)

  triangulation = Delaunay(cluster_centers)
  
  mesh = {
    'name'     : 'delaunay triangulation',
    'type'     : 'mesh',
    'vertices' : triangulation.points.tolist(),
    'faces'    : triangulation.vertices.tolist()
  }

  ltte.debug.update({'name':mesh['name']}, mesh, upsert=True)

  print "Triangulated centers of", len(clusters), "clusters"
