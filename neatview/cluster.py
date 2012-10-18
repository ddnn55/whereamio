class Cluster:

  def __init__(self, ltte, data):
    self.ltte = ltte
    self.data = data
  
  def center(self):
    return self.data['center']
