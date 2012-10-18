from db import ltte
from tile import Tile

class Neatview:

  def __init__(self):
    pass
  
  def tile(self, bbox):
    return Tile(ltte, bbox)
