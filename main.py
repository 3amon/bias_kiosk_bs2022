import pygame
from pygame.locals import *
import sys
from os import path
from multiline_text_pygame import *
import gradients
from game import Game

pygame.init()

windowSurface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
w, h = pygame.display.get_surface().get_size()
min_rect = min(w, h)

running = True
game = Game(windowSurface, num_questions=4)
game.display_start()

while running:
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            running = False
        elif pygame.KEYDOWN == event.type:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_s:
                if game.run_game():
                    game.display_score()
                else:
                    game.display_timeout()
                game.display_start()

pygame.quit()
sys.exit()
