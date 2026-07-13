import pygame 
import sys

pygame.init()


WIDTH, HEIGHT = 640, 480
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ninja Game") 

clock = pygame.time.Clock() 

class Game():
  def __init__(self):
    pass
  
  
  def run(self):
    while True:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          pygame.quit()
          sys.exit
      
      
    pygame.display.update()
    clock.tick(FPS)
      
game = Game()

if __name__ == "__game__":
  game.run()
