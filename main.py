import pygame
from pygame.locals import *
import sys
from os import path
from multiline_text_pygame import *
import gradients

pygame.init()

windowSurface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
w, h = pygame.display.get_surface().get_size()
min_rect = min(w, h)

sign = pygame.image.load(path.join('astro_signs', 'Astrological_sign_Aries_at_the_Wisconsin_State_Capitol.jpeg'))
sign = pygame.transform.scale(sign, (min_rect / 2, min_rect / 2))

trait = pygame.image.load(path.join('traits', 'leadership', '1.png')).convert_alpha()
trait = pygame.transform.scale(trait, (min_rect / 2, min_rect / 2))

prompt_template = 'Press the GREEN button IF the screen shows BOTH a representation of the {}' \
                  ' symbol AND a representation of {}. \n\nOTHERWISE press the RED button.'

trait_name = 'leadership'
sign_name = 'Aries'

grad_color_start = (0xAB, 0xA6, 0xBF, 0xFF)
grad_color_end = (0x59, 0x57, 0x75, 0xFF)
text_color = (0x5E, 0x00, 0x1F)

prompt = prompt_template.format(sign_name.upper(), trait_name.upper())

font = pygame.font.Font('freesansbold.ttf', 32)

format_prompt = StringFormat(ALIGNMENT_CENTER, ALIGNMENT_CENTER)
rect_fps = Rect(0, 0, w - 4, h / 6)

running = True

while running:
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                running = False
            elif pygame.KEYDOWN == event.type:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_y:
                    print("Yes!")
                elif event.key == pygame.K_n:
                    print("No!")

        windowSurface.blit(gradients.vertical((w, h), grad_color_start, grad_color_end), (1, 1))
        draw_string(windowSurface, prompt,
                    rect_fps, font, format_prompt, text_color)

        windowSurface.blit(sign, (w / 4 - (min_rect / 4), h / 2 - (min_rect / 4)))
        windowSurface.blit(trait, (w / 4 - (min_rect / 4) + w / 2, h / 2 - (min_rect / 4)))
        pygame.display.flip()

pygame.quit()
sys.exit()
