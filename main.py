import pygame
from pygame.locals import *
import sys
from os import path
from multiline_text_pygame import *
import gradients
from game import Game

pygame.init()

windowSurface = pygame.display.set_mode((0, 0), pygame.NOFRAME)
pygame.display.toggle_fullscreen()
w, h = pygame.display.get_surface().get_size()
min_rect = min(w, h)

running = True
game = Game(windowSurface, num_questions=4)
pygame.joystick.init()
for i in range(pygame.joystick.get_count()):
    joystick = pygame.joystick.Joystick(i)
    joystick.init()

game.display_start()

while running:
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            running = False
        elif Game.get_start_event(event):
            if game.run_game():
                pass
            else:
                game.display_timeout()
            game.display_start()
        elif Game.get_esc_event(event):
            running = False


pygame.quit()
sys.exit()
