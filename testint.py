import constants
import pygame

pygame.init
screen = pygame.display.set_mode(constants.Graphics.SIZE)
pygame.display.set_caption("Mazda Miata The Game")

finish = False
while not finish:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finish = True
              

pygame.quit