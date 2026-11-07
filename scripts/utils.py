import os
import sys
import pygame
from scripts import pixel_assets

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

BASE_IMG_PATH = resource_path('data/images/') 

def load_image(path):
  if path in pixel_assets.IMAGES:
    img = pixel_assets.IMAGES[path]().convert()
  else:
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
  img.set_colorkey((0,0,0))
  return img 
  

def load_images(path):
  names = pixel_assets.listdir(path)
  if names:
    return [load_image(path + '/' + n) for n in names]
  images = []
  for img_name in sorted(os.listdir(BASE_IMG_PATH + path)): 
    images.append(load_image(path + '/' + img_name)) 
  
  return images
  

def load_sound(name):
  return pixel_assets.make_sound(name)


class Animation:
  def __init__(self, images, img_dur=5, loop=True):
    self.images = images
    self.loop = loop
    self.img_duration = img_dur
    self.done = False 
    self.frame = 0 
    
  def copy(self):
    return Animation(self.images, self.img_duration, self.loop)
  
  def update(self):
    if self.loop:
      self.frame = (self.frame + 1) % (self.img_duration * len(self.images)) 
    else:
      self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1) 
      if self.frame >= self.img_duration * len(self.images) - 1:
        self.done = True 
      
  
  def img(self):
    return self.images[int(self.frame / self.img_duration)] 
  
  





