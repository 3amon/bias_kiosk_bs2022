from datetime import datetime, timedelta
from pygame.locals import *
import sys
from os import path
from multiline_text_pygame import *
import gradients
from random import choice, shuffle
from enum import Enum
from trait_map import TraitMap
from pymongo import MongoClient
from uuid import uuid4
import pygame

GAME_TIMEOUT = 60000
GAME_TIMEOUT_SHORT = 10000
PROMPT_TEMPLATE_1 = '[>]Section 1 of 4\n\n' \
                    '[>]You will be shown a sequence of {0} images.\n' \
                    '[>]Each will consist of a representation of the sign {1}\n' \
                    '   or the sign {2}.\n' \
                    '[>]Put your left hand on the green button.\n' \
                    '   You will press the green button when the sign {1} is shown.\n' \
                    '[>]Put your right hand on the red button.\n' \
                    '   You will press the red button when the sign {2} is shown.\n' \
                    '[>]Your goal is to press the correct button as quickly\n' \
                    '   as possible without mistakes!\n'

PROMPT_TEMPLATE_2 = '[>]Section 2 of 4\n\n' \
                    '[>]You will be shown a sequence of {0} words.\n' \
                    '[>]Each prompt will consist of either a good word\n' \
                    '   or a bad word.\n' \
                    '[>]Put your left hand on the green button.\n' \
                    '   You will press the green button when a good word is shown.\n' \
                    '[>]Put your right hand on the red button.\n' \
                    '   You will press the red button when a bad word is shown.\n' \
                    '[>]Your goal is to press the correct button as quickly\n' \
                    '   and accurately as possible!\n'

PROMPT_TEMPLATE_3 = '[>]Section 3 of 4\n\n' \
                    '[>]Now we will do another {0} that can be either words or signs.\n' \
                    '[>]Each prompt can be a good word, a bad word,\n' \
                    '   sign {1}, or {2}.\n' \
                    '[>]You will press the green button when a good word\n' \
                    '   or the sign {1} is shown.\n' \
                    '[>]You will press the red button when a bad word or \n' \
                    '   the sign {2} is shown.\n' \
                    '[>]Do the best you can!\n'

PROMPT_TEMPLATE_4 = '[>]Section 4 of 4\n\n' \
                    '[>]Another {0} of words and images.\n' \
                    '[>]We are switching the association!\n' \
                    '[>]Green will be {2} and Good.\n' \
                    '[>]And you guessed it, press red when shown \n' \
                    '{1} or bad this time.\n' \
                    '[>]Go fast but no mistakes!\n'

PRESS_START = "[>]Press the START button to continue..."

PROMPT_TEMPLATES = [PROMPT_TEMPLATE_1, PROMPT_TEMPLATE_2, PROMPT_TEMPLATE_3, PROMPT_TEMPLATE_4]

TEXT_COLOR = (0x5E, 0x00, 0x1F)
GRAD_COLOR_START = (0xAB, 0xA6, 0xBF, 0xFF)
GRAD_COLOR_END = (0x59, 0x57, 0x75, 0xFF)
FONT_SIZE = 48

TIMEOUT_EVENT = pygame.USEREVENT + 1

ALLOW_START_SKIP = True

clock = pygame.time.Clock()

class Cursor(pygame.sprite.Sprite):

    def __init__(self, board, pos, size=FONT_SIZE):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.image = pygame.Surface(pos, pygame.SRCALPHA)
        self.text_height = 17 / 18.0 * size
        self.text_width = 10 / 18.0 * size
        self.rect = self.image.get_rect(topleft=(self.pos[0] + self.text_width, self.pos[1] + self.text_height))
        self.board = board
        self.font = pygame.font.SysFont("monospace", size)
        self.text = ''
        self.cooldown = 0
        self.cooldowns = {'.': 12,
                        '[': 18,
                        ']': 18,
                        ' ': 5,
                        '\n': 5}

    @property
    def done(self):
        return not self.text or ALLOW_START_SKIP

    def write(self, text):
        self.text = list(text)

    def update(self):
        if not self.cooldown and self.text:
            letter = self.text.pop(0)
            if letter == '\n':
                self.rect.move_ip((0, self.text_height))
                self.rect.x = self.text_width + self.pos[0]
            else:
                s = self.font.render(letter, True, TEXT_COLOR)
                self.board.add_letter(s, self.rect.topleft)
                self.rect.move_ip((self.text_width, 0))
            self.cooldown = self.cooldowns.get(letter, 3)

        if self.cooldown:
            self.cooldown -= 1

class Game(pygame.sprite.Sprite):

    def __init__(self, windowSurface, num_questions=10):
        pygame.sprite.Sprite.__init__(self)
        self.num_questions = num_questions
        self.base_num_questions = num_questions
        self.windowSurface = windowSurface
        self.w, self.h = pygame.display.get_surface().get_size()
        self.min_rect = min(self.w, self.h)
        self.client = MongoClient(uuidRepresentation='standard')
        self.db = self.client.kiosk_database
        self.runs = self.db.runs
        self.avg_target = 0.0
        self.avg_miss = 0.0

    def add_letter(self, s, pos):
        self.windowSurface.blit(s, pos)

    @staticmethod
    def get_start_event(event):
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_s) or \
           (event.type == pygame.JOYBUTTONDOWN and event.button == pygame.CONTROLLER_BUTTON_B):
            pygame.time.set_timer(TIMEOUT_EVENT, GAME_TIMEOUT, loops=1)
            return True
        return False

    @staticmethod
    def get_y_event(event):
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_y) or \
           (event.type == pygame.JOYBUTTONDOWN and event.button == pygame.CONTROLLER_BUTTON_Y):
            pygame.time.set_timer(TIMEOUT_EVENT, GAME_TIMEOUT, loops=1)
            return True
        return False

    @staticmethod
    def get_n_event(event):
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_n) or \
           (event.type == pygame.JOYBUTTONDOWN and event.button == pygame.CONTROLLER_BUTTON_A):
            pygame.time.set_timer(TIMEOUT_EVENT, GAME_TIMEOUT, loops=1)
            return True
        return False

    @staticmethod
    def get_esc_event(event, watch_timeout=True):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE or event.type == TIMEOUT_EVENT and watch_timeout:
            if event.type == TIMEOUT_EVENT:
                pygame.time.set_timer(TIMEOUT_EVENT, GAME_TIMEOUT_SHORT, loops=1)
            else:
                pygame.time.set_timer(TIMEOUT_EVENT, GAME_TIMEOUT, loops=1)
            return True
        return False

    @staticmethod
    def get_run_template():
        return {
            'sign1': '',
            'sign2': '',
            'timestamp': '',
            'guid': '',
            'phase': 0,
            'button_error_count': 0,
            'green_times': [],
            'red_times': []
        }


    def run_game(self):

        guid = uuid4()
        phase_2_sum = 0
        phase_3_sum = 0

        sign1, sign2 = TraitMap.get_random_two_signs()
        for i in range(4):

            if i == 2 or i == 3:
                self.num_questions = self.base_num_questions * 2
            else:
                self.num_questions = self.base_num_questions

            keep_going, run_sum = self.do_run(guid, sign1, sign2, i)
            if not keep_going:
                return False
            if i == 2:
                phase_2_sum = run_sum
            if i == 3:
                phase_3_sum = run_sum

        if not self.display_score(phase_2_sum, phase_3_sum, sign1, sign2):
            return False
        return True

    def do_run(self, guid, sign1, sign2, phase: int):
        run_record = self.get_run_template()
        run_record['sign1'] = sign1.name
        run_record['sign2'] = sign2.name
        run_record['timestamp'] = datetime.now()
        run_record['guid'] = guid
        run_record['phase'] = phase

        if not self.display_prompt(sign1, sign2, phase):
            return False, 0

        run_hits = ([False] * int(self.num_questions / 2))
        run_hits = run_hits + ([True] * int((self.num_questions + 1) / 2))
        shuffle(run_hits)

        choose_signs = ([False] * int(self.num_questions / 2))
        choose_signs = choose_signs + ([True] * int((self.num_questions + 1) / 2))
        shuffle(choose_signs)

        for press_green, choose_sign in zip(choose_signs, run_hits):
            if not self.run_game_instance(sign1, sign2, phase, run_record, press_green, choose_sign):
                return False, 0

        self.runs.insert_one(run_record)
        return True, sum(run_record['green_times']) + sum(run_record['red_times'])

    def run_game_instance(self, sign1, sign2, phase, run_record, press_green, choose_sign):

        sign1_name = sign1.name
        sign2_name = sign2.name

        if phase == 0:
            left_text = 'Green\nif\n{}'.format(sign1_name)
            right_text = 'Red\nif\n{}'.format(sign2_name)
        elif phase == 1:
            left_text = 'Green\nif\nGood'
            right_text = 'Red\nif\nBad'
        elif phase == 2:
            left_text = '{}\nor\nGood'.format(sign1_name)
            right_text = '{}\nor\nBad'.format(sign2_name)
        elif phase == 3:
            left_text = '{}\nor\nGood'.format(sign2.name)
            right_text = '{}\nor\nBad'.format(sign1.name)

        first_miss = True
        start_time = datetime.now()

        if press_green:
            sign_img = pygame.image.load(TraitMap.get_sign_img(sign1)) if not phase == 3 else pygame.image.load(TraitMap.get_sign_img(sign2))
            word = TraitMap.get_random_good_word()

        else:
            sign_img = pygame.image.load(TraitMap.get_sign_img(sign2)) if not phase == 3 else pygame.image.load(TraitMap.get_sign_img(sign1))
            word = TraitMap.get_random_bad_word()

        first_run = True

        while True:
            font = pygame.font.SysFont("monospace", FONT_SIZE)
            self.windowSurface.blit(gradients.vertical((self.w, self.h), GRAD_COLOR_START, GRAD_COLOR_END), (1, 1))

            rect_fps = Rect(0, 0, 400, self.h / 6)

            format_prompt = StringFormat(ALIGNMENT_CENTER, ALIGNMENT_CENTER)

            draw_string(self.windowSurface, left_text,
                        rect_fps, font, format_prompt, (0x00, 0xFF, 0x00))

            rect_fps = Rect(self.w - self.w/6, self.h/100, 500, self.h / 6)

            draw_string(self.windowSurface, right_text,
                        rect_fps, font, format_prompt, (0xFF, 0x00, 0x00))

            sign_img = pygame.transform.scale(sign_img, (self.min_rect / 2, self.min_rect / 2))

            x_img = pygame.image.load('x_bad_button.png').convert_alpha()
            check_img = pygame.image.load('check_good_button.png').convert_alpha()

            if first_run:
                pygame.display.flip()
                pygame.time.delay(500)
                first_run = False

            if phase == 0:
                self.windowSurface.blit(sign_img, (self.w / 2 - (self.min_rect / 4), self.h / 2 - (self.min_rect / 4)))
            elif phase == 1:
                rect_fps = Rect(0, 0, self.w, self.h)
                font = pygame.font.SysFont("monospace", FONT_SIZE * 2)
                draw_string(self.windowSurface, word,
                            rect_fps, font, format_prompt, (0x00, 0x00, 0xFF))
            elif phase == 2 or phase == 3:
                if choose_sign:
                    self.windowSurface.blit(sign_img,
                                            (self.w / 2 - (self.min_rect / 4), self.h / 2 - (self.min_rect / 4)))
                else:
                    rect_fps = Rect(0, 0, self.w, self.h)
                    font = pygame.font.SysFont("monospace", FONT_SIZE * 2)
                    draw_string(self.windowSurface, word,
                                rect_fps, font, format_prompt, (0x00, 0x00, 0xFF))

            pygame.display.flip()

            event = pygame.event.wait(timeout=GAME_TIMEOUT)
            if Game.get_esc_event(event):
                return False
            elif Game.get_y_event(event):
                if press_green:
                    hit_time_taken = datetime.now() - start_time
                    run_record['green_times'].append(hit_time_taken / timedelta(milliseconds=1))
                    self.windowSurface.blit(check_img,
                                            (self.w / 2 - (self.min_rect / 4), self.h / 2 - (self.min_rect / 4)))

                    pygame.display.flip()
                    pygame.time.delay(500)
                    return True
                else:
                    run_record['button_error_count'] += 1
                    self.windowSurface.blit(x_img,
                                            (self.w / 2 - (self.min_rect / 4), self.h / 2 - (self.min_rect / 4)))

                    pygame.display.flip()
                    if first_miss:
                        pygame.time.delay(1000)
                        first_miss = False

            elif Game.get_n_event(event):
                if not press_green:
                    hit_time_taken = datetime.now() - start_time
                    run_record['red_times'].append(hit_time_taken / timedelta(milliseconds=1))
                    self.windowSurface.blit(check_img,
                                            (self.w / 2 - (self.min_rect / 4), self.h / 2 - (self.min_rect / 4)))

                    pygame.display.flip()
                    pygame.time.delay(500)
                    return True
                else:
                    run_record['button_error_count'] += 1
                    self.windowSurface.blit(x_img,
                                            (self.w / 2 - (self.min_rect / 4), self.h / 2 - (self.min_rect / 4)))

                    pygame.display.flip()
                    if first_miss:
                        #pygame.time.delay(1000)
                        pass
                        first_miss = False

    def display_start(self):

        self.windowSurface.blit(gradients.vertical((self.w, self.h), GRAD_COLOR_START, GRAD_COLOR_END), (1, 1))

        all_sprites = pygame.sprite.Group()
        cursor = Cursor(self, (self.w/10, self.h / 6), FONT_SIZE)
        all_sprites.add(cursor)

        cursor.write("[>]Welcome to the astrological implicit bias test kiosk!\n\n[>]Press the START button to begin...")

        running = True
        while running:

            events = pygame.event.get()
            for event in events:
                if Game.get_esc_event(event, False):
                    return False
                if Game.get_start_event(event) and cursor.done:
                    return True

            all_sprites.update()
            all_sprites.draw(self.windowSurface)
            pygame.display.flip()
            clock.tick(60)

    def display_prompt(self, sign1, sign2, phase: int):
        sign1 = sign1.name
        sign2 = sign2.name

        prompt_template = PROMPT_TEMPLATES[phase]

        prompt = prompt_template.format(self.num_questions, sign1.upper(), sign2.upper())

        self.windowSurface.blit(gradients.vertical((self.w, self.h), GRAD_COLOR_START, GRAD_COLOR_END), (1, 1))

        prompt += '\n\n' + PRESS_START

        all_sprites = pygame.sprite.Group()
        cursor = Cursor(self, (self.w / 10, self.h / 6), FONT_SIZE)
        all_sprites.add(cursor)

        cursor.write(prompt)

        while True:
            events = pygame.event.get()
            for event in events:
                if Game.get_esc_event(event):
                    return False
                elif Game.get_start_event(event) and cursor.done:
                    return True

            all_sprites.update()
            all_sprites.draw(self.windowSurface)
            pygame.display.flip()
            clock.tick(60)


    def display_timeout(self):

        self.windowSurface.blit(gradients.vertical((self.w, self.h), GRAD_COLOR_START, GRAD_COLOR_END), (1, 1))

        all_sprites = pygame.sprite.Group()
        cursor = Cursor(self, (self.w/10, self.h / 6), FONT_SIZE)
        all_sprites.add(cursor)

        cursor.write("[>]Student was too slow!\n[>]Womp womp...")

        while True:
            events = pygame.event.get()
            for event in events:
                if Game.get_esc_event(event):
                    return False
                elif Game.get_start_event(event):
                    return True

            all_sprites.update()
            all_sprites.draw(self.windowSurface)
            pygame.display.flip()
            clock.tick(60)

    def display_score(self, trait1_good_sum, trait2_good_sum, sign1, sign2):

        self.windowSurface.blit(gradients.vertical((self.w, self.h), GRAD_COLOR_START, GRAD_COLOR_END), (1, 1))

        score_string = "[>]We compared the times it took you to\n" \
                       "   associate {0} with good and {1} with bad\n" \
                       "   and vice versa.\n" \
                       "[>]Hmmm....\n" \
                       "[>]You seem to be about {2:0.3f} seconds faster when\n" \
                       "  {0} was associated with good.\n" \
                       "[>]This indicates that you see {0} in a more favorable light.\n" \
                       "[>]You are biased!\n" \
                       "[>]Have a nice day!"

        delta = (trait1_good_sum - trait2_good_sum) / 1000.0
        if delta > 0:
            score_string = score_string.format(sign1.name, sign2.name, abs(delta))
        else:
            score_string = score_string.format(sign2.name, sign1.name, abs(delta))

        all_sprites = pygame.sprite.Group()
        cursor = Cursor(self, (self.w / 10, self.h / 6), FONT_SIZE)
        all_sprites.add(cursor)

        cursor.write(score_string)

        while True:
            events = pygame.event.get()
            for event in events:
                if Game.get_esc_event(event):
                    return False
                elif Game.get_start_event(event):
                    return True

            all_sprites.update()
            all_sprites.draw(self.windowSurface)
            pygame.display.flip()
            clock.tick(60)




