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
PROMPT_TEMPLATE = '[>]Section {} of {}\n\n' \
                  '[>]You will be shown a sequence of {} prompts.\n' \
                  '[>]Each prompt will consist of an astrological sign\n' \
                  '   and a personality trait.\n' \
                  '[>]When each prompt is shown, press the green\n' \
                  '   button if the screen shows both a representation\n' \
                  '   of the {} symbol and the word {}. \n' \
                  '[>]Otherwise press the red button.'

PRESS_START = "[>]Press the START button to continue..."

TEXT_COLOR = (0x5E, 0x00, 0x1F)
GRAD_COLOR_START = (0xAB, 0xA6, 0xBF, 0xFF)
GRAD_COLOR_END = (0x59, 0x57, 0x75, 0xFF)
FONT_SIZE = 48

TIMEOUT_EVENT = pygame.USEREVENT + 1

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
        return not self.text

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
            'trait': '',
            'sign': '',
            'timestamp': '',
            'guid': '',
            'button_error_count': 0,
            'hit_times': [],
            'miss_times': []
        }

    def run_game(self):

        guid = uuid4()

        if choice([True, False]):
            completed, target_run_record = self.run_hit(guid, 1)
            if not completed:
                return False
            completed, miss_run_record = self.run_miss(guid, 2)
            if not completed:
                return False
        else:
            completed, miss_run_record = self.run_miss(guid, 1)
            if not completed:
                return False
            completed, target_run_record = self.run_hit(guid, 2)
            if not completed:
                return False

        run_avg_target = sum(target_run_record['hit_times']) / len(target_run_record['hit_times'])
        run_avg_miss = sum(miss_run_record['hit_times']) / len(miss_run_record['hit_times'])

        self.display_score(run_avg_target, run_avg_miss, target_run_record['trait'], target_run_record['sign'])

        return True

    def run_hit(self, guid, section_num: int):
        trait, sign = TraitMap.get_random_target_trait_sign_pair()
        run_record = self.get_run_template()
        run_record['trait'] = trait.name
        run_record['sign'] = sign.name
        run_record['timestamp'] = datetime.now()
        run_record['guid'] = guid
        return self.do_run(trait, sign, run_record, section_num), run_record

    def run_miss(self, guid, section_num: int):
        trait, sign = TraitMap.get_random_nontarget_trait_sign_pair()
        run_record = self.get_run_template()
        run_record['trait'] = trait.name
        run_record['sign'] = sign.name
        run_record['timestamp'] = datetime.now()
        run_record['guid'] = guid
        return self.do_run(trait, sign, run_record, section_num), run_record

    def do_run(self, trait, sign, run_record, section_num: int):

        run_hits = ([False] * int(self.num_questions / 2))
        run_hits = run_hits + ([True] * int((self.num_questions + 1) / 2))
        shuffle(run_hits)
        if not self.display_prompt(trait, sign, section_num):
            return False
        for on_target in run_hits:
            if not self.run_instance_with_target(trait, sign, run_record, on_target):
                return False

        self.runs.insert_one(run_record)
        return True

    def run_instance_with_target(self, target_trait, target_sign, run_record, on_target: bool):
        if on_target:
            instance = self.both_hit
        else:
            instance = choice([self.both_miss, self.one_miss])

        trait, sign, press_y = instance(target_trait, target_sign)
        return self.run_game_instance(target_trait, target_sign, trait, sign, press_y, run_record)

    def both_hit(self, trait, sign):
        return trait, sign, True

    def both_miss(self, trait, sign):
        return TraitMap.get_not_trait(trait), TraitMap.get_not_sign(sign), False

    def one_miss(self, trait, sign):
        if choice([True, False]):
            return TraitMap.get_not_trait(trait), sign, False
        else:
            return trait, TraitMap.get_not_sign(sign), False

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

    def display_prompt(self, target_trait, target_sign, section_num: int, num_sections=2):
        trait_name = target_trait.name
        sign_name = target_sign.name

        prompt = PROMPT_TEMPLATE.format(section_num, num_sections, self.num_questions, sign_name.upper(), trait_name.upper())

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

    def display_score(self, run_avg_target, run_avg_miss, trait, sign):

        self.windowSurface.blit(gradients.vertical((self.w, self.h), GRAD_COLOR_START, GRAD_COLOR_END), (1, 1))

        score_string = "[>]We had you match the trait {} which\n   is commonly associated with the\n   astrological sign {}.\n" \
                       "[>]You matched that trait on average {:0.3f}\n   seconds faster than our control question.\n" \
                       "[>]This {} that this association is\n   present on a subconscious level.\n" \
                       "{}[>]Have a nice day!"

        delta = (run_avg_miss - run_avg_target) / 1000.0
        bias = 'does not indicate' if delta <= 0.0 else 'indicates'
        bias2 = '' if delta <= 0.0 else "[>]You are biased!\n"

        score_string = score_string.format(trait, sign, delta, bias, bias2)

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


    def run_game_instance(self, target_trait, target_sign, trait: Enum, sign: Enum, press_y: bool, run_record):
        start_time = datetime.now()
        trait_name = target_trait.name
        sign_name = target_sign.name
        font = pygame.font.SysFont("monospace", FONT_SIZE)
        format_prompt = StringFormat(ALIGNMENT_CENTER, ALIGNMENT_CENTER)
        prompt_template = 'Press green if both {} and {} are displayed.\nOtherwise press red.'

        prompt = prompt_template.format(sign_name.upper(), trait_name.upper())

        first_run = True
        first_miss = True

        while True:

            self.windowSurface.blit(gradients.vertical((self.w, self.h), GRAD_COLOR_START, GRAD_COLOR_END), (1, 1))

            rect_fps = Rect(0, 0, self.w - 4, self.h / 6)

            draw_string(self.windowSurface, prompt,
                        rect_fps, font, format_prompt, TEXT_COLOR)

            sign_img = pygame.image.load(TraitMap.get_sign_img(sign))
            sign_img = pygame.transform.scale(sign_img, (self.min_rect / 2, self.min_rect / 2))

            trait_img = pygame.image.load(TraitMap.get_random_trait_img(trait)).convert_alpha()
            trait_img = pygame.transform.scale(trait_img, (self.min_rect / 2, self.min_rect / 2))

            x_img = pygame.image.load('x_bad_button.png').convert_alpha()
            check_img = pygame.image.load('check_good_button.png').convert_alpha()

            if first_run:
                pygame.display.flip()
                pygame.time.delay(1000)

            self.windowSurface.blit(sign_img, (self.w / 4 - (self.min_rect / 4), self.h / 2 - (self.min_rect / 4)))

            if first_run:
                pygame.display.flip()
                pygame.time.delay(100)
                pygame.event.clear()

            self.windowSurface.blit(trait_img,
                                    (self.w / 4 - (self.min_rect / 4) + self.w / 2, self.h / 2 - (self.min_rect / 4)))
            pygame.display.flip()

            first_run = False

            event = pygame.event.wait(timeout=GAME_TIMEOUT)
            if Game.get_esc_event(event):
                return False
            elif Game.get_y_event(event):
                if press_y:
                    hit_time_taken = datetime.now() - start_time
                    run_record['hit_times'].append(hit_time_taken / timedelta(milliseconds=1))
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
                if not press_y:
                    hit_time_taken = datetime.now() - start_time
                    run_record['miss_times'].append(hit_time_taken / timedelta(milliseconds=1))
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




