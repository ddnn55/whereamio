from cluster import Cluster

class Tile:

  def __init__(self, ltte, roi):
    self.roi = roi
    self.ltte = ltte
  
  def clusters(self):
    bbox = self.roi
    clusters_cursor = self.ltte.clusters.find({'center': {'$within': {'$box': [[bbox.bottom, bbox.left], [bbox.top, bbox.right]]}}})
    for cluster_data in clusters_cursor:
      yield Cluster(self.ltte, cluster_data)
