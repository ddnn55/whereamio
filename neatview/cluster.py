from db import ltte
from Flickr import MirroredPhoto

class Cluster:

  def __init__(self, ltte, data):
    self.ltte = ltte
    self.data = data
    self.db_id = data['_id']
  
  def center(self):
    return self.data['center']

  def first_image(self):
    result = ltte.photos.find_one({'cluster':self.db_id})
    if result != None:
      return MirroredPhoto(result)
    else:
      return None

  def display_data(self):
    #db_rep_images = []
    #if 'representative_images' in self.data:
    #  db_rep_images = self.data['representative_images']
    
    #images = {}
    #for rep_image in db_rep_images:
    #  (rep_image_type, image_id) = rep_image.items()[0]
    #  photo = ltte.photos.find_one({'_id':image_id})
    #  mi = MirroredPhoto(photo)
    #  images[rep_image_type] = mi.ui_metadata()
     
    display_data = {
      '_id'    : str(self.data['_id']),
      'center' : self.center(),
      'count'  : self.data['count']
    }
    image = self.first_image()
    if image != None:
      display_data['image'] = image.ui_metadata()

    return display_data
