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

GAME_TIMEOUT = 15000

class Game(object):

    def __init__(self, windowSurface, num_questions=10):
        self.num_questions = num_questions
        self.windowSurface = windowSurface
        self.w, self.h = pygame.display.get_surface().get_size()
        self.min_rect = min(self.w, self.h)
        self.client = MongoClient()
        self.db = self.client.kiosk_database
        self.runs = self.db.runs
        self.avg_target = 0.0
        self.avg_miss = 0.0


    @staticmethod
    def get_start_event(event):
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_s) or \
           (event.type == pygame.JOYBUTTONDOWN and event.button == pygame.CONTROLLER_BUTTON_B):
            print("Start!")
            return True
        return False

    @staticmethod
    def get_y_event(event):
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_y) or \
           (event.type == pygame.JOYBUTTONDOWN and event.button == pygame.CONTROLLER_BUTTON_Y):
            print("No!")
            return True
        return False

    @staticmethod
    def get_n_event(event):
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_n) or \
           (event.type == pygame.JOYBUTTONDOWN and event.button == pygame.CONTROLLER_BUTTON_A):
            print("Yes!")
            return True
        return False

    @staticmethod
    def get_esc_event(event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE or event.type == pygame.NOEVENT:
            print("ESC!")
            return True
        return False


    @staticmethod
    def get_run_template():
        return {
            'trait': '',
            'sign': '',
            'timestamp': '',
            'button_error_count': 0,
            'hit_times': [],
            'miss_times': []
        }

    def run_game(self):

        if choice([True, False]):
            completed, target_run_record = self.run_hit()
            if not completed:
                return False
            completed, miss_run_record = self.run_miss()
            if not completed:
                return False
        else:
            completed, miss_run_record = self.run_miss()
            if not completed:
                return False
            completed, target_run_record = self.run_hit()
            if not completed:
                return False

        run_avg_target = sum(target_run_record['hit_times']) / len(target_run_record['hit_times'])
        run_avg_miss = sum(miss_run_record['hit_times']) / len(miss_run_record['hit_times'])


        self.display_score(run_avg_target, run_avg_miss, target_run_record['trait'], target_run_record['sign'])

        return True

    def run_hit(self):
        print("Running On Target!")
        trait, sign = TraitMap.get_random_target_trait_sign_pair()
        run_record = self.get_run_template()
        run_record['trait'] = trait.name
        run_record['sign'] = sign.name
        run_record['timestamp'] = datetime.now()
        return self.do_run(trait, sign, run_record), run_record

    def run_miss(self):
        print("Running Off Target!")
        trait, sign = TraitMap.get_random_nontarget_trait_sign_pair()
        run_record = self.get_run_template()
        run_record['trait'] = trait.name
        run_record['sign'] = sign.name
        run_record['timestamp'] = datetime.now()
        return self.do_run(trait, sign, run_record), run_record

    def do_run(self, trait, sign, run_record):

        run_hits = ([False] * int(self.num_questions / 2))
        run_hits = run_hits + ([True] * int((self.num_questions + 1) / 2))
        shuffle(run_hits)
        if not self.display_prompt(trait, sign):
            return False
        for on_target in run_hits:
            self.display_prompt(trait, sign, timeout=500, wait_to_continue=False)
            if not self.run_instance_with_target(trait, sign, run_record, on_target):
                print("Aborted!")
                return False

        print("DONE!")
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

        grad_color_start = (0xAB, 0xA6, 0xBF, 0xFF)
        grad_color_end = (0x59, 0x57, 0x75, 0xFF)
        text_color = (0x5E, 0x00, 0x1F)

        font = pygame.font.Font('freesansbold.ttf', 32)

        format_prompt = StringFormat(ALIGNMENT_CENTER, ALIGNMENT_CENTER)
        rect_fps = Rect(0, 0, self.w - 4, self.h / 6)

        self.windowSurface.blit(gradients.vertical((self.w, self.h), grad_color_start, grad_color_end), (1, 1))

        draw_string(self.windowSurface, "Welcome to the astrological implicit bias test kiosk!",
                    rect_fps, font, format_prompt, text_color)

        rect_fps = Rect(0, 0, self.w - 4, self.h)
        draw_string(self.windowSurface, "Press the START button to begin...",
                    rect_fps, font, format_prompt, text_color)

        pygame.display.flip()

    def display_timeout(self):

        grad_color_start = (0xAB, 0xA6, 0xBF, 0xFF)
        grad_color_end = (0x59, 0x57, 0x75, 0xFF)
        text_color = (0x5E, 0x00, 0x1F)

        font = pygame.font.Font('freesansbold.ttf', 32)

        format_prompt = StringFormat(ALIGNMENT_CENTER, ALIGNMENT_CENTER)
        rect_fps = Rect(0, 0, self.w - 4, self.h / 6)

        self.windowSurface.blit(gradients.vertical((self.w, self.h), grad_color_start, grad_color_end), (1, 1))

        draw_string(self.windowSurface, "",
                    rect_fps, font, format_prompt, text_color)

        rect_fps = Rect(0, 0, self.w - 4, self.h)
        draw_string(self.windowSurface, "Student was too slow... test timed out... womp womp",
                    rect_fps, font, format_prompt, text_color)

        pygame.display.flip()

        while True:
            event = pygame.event.wait(timeout=3000)
            if Game.get_esc_event(event):
                return False
            if Game.get_start_event(event):
                return True

    def display_score(self, run_avg_target, run_avg_miss, trait, sign):

        grad_color_start = (0xAB, 0xA6, 0xBF, 0xFF)
        grad_color_end = (0x59, 0x57, 0x75, 0xFF)
        text_color = (0x5E, 0x00, 0x1F)

        font = pygame.font.Font('freesansbold.ttf', 32)

        format_prompt = StringFormat(ALIGNMENT_CENTER, ALIGNMENT_CENTER)
        rect_fps = Rect(0, 0, self.w - 4, self.h / 2)

        self.windowSurface.blit(gradients.vertical((self.w, self.h), grad_color_start, grad_color_end), (1, 1))

        score_string = "\n\nWe had you match the trait {} which is commonly associated with the astrological sign {}.\n\n" \
                       "You matched that trait on average {:.4f} seconds faster than our control question.\n\n" \
                       "This does {}indicate the presence of this association being present on a subconscious level.\n\n"\
                       "{}Have a nice day!"

        delta = (run_avg_miss - run_avg_target) / 1000.0
        bias = 'not ' if delta <= 0.0 else ''
        bias2 = '' if delta <= 0.0 else "You are biased! "

        score_string = score_string.format(trait, sign, delta, bias, bias2)

        draw_string(self.windowSurface, score_string,
                    rect_fps, font, format_prompt, text_color)

        rect_fps = Rect(0, 0, self.w - 4, self.h)
        draw_string(self.windowSurface, "Press the START button to continue...",
                    rect_fps, font, format_prompt, text_color)

        pygame.display.flip()

        while True:
            event = pygame.event.wait(timeout=GAME_TIMEOUT * 2)
            if Game.get_esc_event(event):
                return False
            elif Game.get_start_event(event):
                return True

    def display_prompt(self, target_trait, target_sign, timeout=GAME_TIMEOUT, wait_to_continue=True):

        trait_name = target_trait.name
        sign_name = target_sign.name

        grad_color_start = (0xAB, 0xA6, 0xBF, 0xFF)
        grad_color_end = (0x59, 0x57, 0x75, 0xFF)
        text_color = (0x5E, 0x00, 0x1F)

        font = pygame.font.Font('freesansbold.ttf', 32)

        format_prompt = StringFormat(ALIGNMENT_CENTER, ALIGNMENT_CENTER)
        rect_fps = Rect(0, 0, self.w - 4, self.h / 6)

        prompt_template = 'Press the GREEN button IF the screen shows BOTH a representation of the {}' \
                          ' symbol AND the word {}. \n\nOTHERWISE press the RED button.'

        prompt = prompt_template.format(sign_name.upper(), trait_name.upper())

        self.windowSurface.blit(gradients.vertical((self.w, self.h), grad_color_start, grad_color_end), (1, 1))

        draw_string(self.windowSurface, prompt,
                    rect_fps, font, format_prompt, text_color)

        if wait_to_continue:
            rect_fps = Rect(0, 0, self.w - 4, self.h)
            draw_string(self.windowSurface, "Press the START button to continue...",
                        rect_fps, font, format_prompt, text_color)

        pygame.display.flip()

        while True:
            event = pygame.event.wait(timeout=timeout)
            if Game.get_esc_event(event):
                return False
            elif Game.get_start_event(event) and wait_to_continue:
                return True

    def run_game_instance(self, target_trait, target_sign, trait: Enum, sign: Enum, press_y: bool, run_record):

        trait_name = target_trait.name
        sign_name = target_sign.name

        grad_color_start = (0xAB, 0xA6, 0xBF, 0xFF)
        grad_color_end = (0x59, 0x57, 0x75, 0xFF)
        text_color = (0x5E, 0x00, 0x1F)

        font = pygame.font.Font('freesansbold.ttf', 32)

        format_prompt = StringFormat(ALIGNMENT_CENTER, ALIGNMENT_CENTER)
        rect_fps = Rect(0, 0, self.w - 4, self.h / 6)

        prompt_template = 'Press the GREEN button IF the screen shows BOTH a representation of the {}' \
                          ' symbol AND a representation of {}. \n\nOTHERWISE press the RED button.'

        prompt = prompt_template.format(sign_name.upper(), trait_name.upper())

        self.windowSurface.blit(gradients.vertical((self.w, self.h), grad_color_start, grad_color_end), (1, 1))
        draw_string(self.windowSurface, prompt,
                    rect_fps, font, format_prompt, text_color)

        sign_img = pygame.image.load(TraitMap.get_sign_img(sign))
        sign_img = pygame.transform.scale(sign_img, (self.min_rect / 2, self.min_rect / 2))

        trait_img = pygame.image.load(TraitMap.get_random_trait_img(trait)).convert_alpha()
        trait_img = pygame.transform.scale(trait_img, (self.min_rect / 2, self.min_rect / 2))

        self.windowSurface.blit(sign_img, (self.w / 4 - (self.min_rect / 4), self.h / 2 - (self.min_rect / 4)))
        self.windowSurface.blit(trait_img,
                                (self.w / 4 - (self.min_rect / 4) + self.w / 2, self.h / 2 - (self.min_rect / 4)))
        pygame.display.flip()

        start_time = datetime.now()
        while True:
            event = pygame.event.wait(timeout=GAME_TIMEOUT)
            if Game.get_esc_event(event):
                return False
            elif Game.get_y_event(event):
                if press_y:
                    hit_time_taken = datetime.now() - start_time
                    print("Took:", hit_time_taken)
                    print("Took:", hit_time_taken / timedelta(milliseconds=1))
                    run_record['hit_times'].append(hit_time_taken / timedelta(milliseconds=1))
                    return True
                else:
                    print(start_time)
                    start_time -= timedelta(seconds=1)
                    run_record['button_error_count'] += 1
                    print(start_time)
            elif Game.get_n_event(event):
                if not press_y:
                    hit_time_taken = datetime.now() - start_time
                    print("Took:", hit_time_taken)
                    print("Took:", hit_time_taken / timedelta(milliseconds=1))
                    run_record['miss_times'].append(hit_time_taken / timedelta(milliseconds=1))
                    return True
                else:
                    print(start_time)
                    start_time -= timedelta(seconds=1)
                    run_record['button_error_count'] += 1
                    print(start_time)



