import pygame
from pygame.locals import *
import sys
from os import path
from multiline_text_pygame import *
import gradients
from game import Game

pygame.init()

windowSurface = pygame.display.set_mode((1920, 1080), pygame.NOFRAME)
#pygame.display.toggle_fullscreen()
w, h = pygame.display.get_surface().get_size()
min_rect = min(w, h)

running = True
game = Game(windowSurface, num_questions=2)
pygame.joystick.init()
for i in range(pygame.joystick.get_count()):
    joystick = pygame.joystick.Joystick(i)
    joystick.init()

while running:

    if game.display_start():
        if game.run_game():
            pass
        else:
            game.display_timeout()
    else:
        running = False


pygame.quit()
sys.exit()
