from random import random, choice
from enum import Enum, auto
from os import path, getcwd, listdir


class Signs(Enum):
    Aquarius = auto(),
    Aries = auto(),
    Virgo = auto(),
    Cancer = auto(),
    Capricorn = auto(),
    Gemini = auto(),
    Leo = auto(),
    Libra = auto()
    Pisces = auto(),
    Sagittarius = auto(),
    Scorpio = auto(),
    Taurus = auto()


class Traits(Enum):
    Jealousy = auto(),
    Manipulation = auto(),
    Arrogance = auto(),
    Suspicion = auto(),
    Selfishness = auto(),
    Narcissism = auto(),
    Impulsiveness = auto(),


hit_map = {
    Signs.Leo: [Traits.Arrogance],
    Signs.Scorpio: [Traits.Jealousy]
}

signs_dir = path.join(getcwd(), "astro_signs")

trait_dirs = {
    Traits.Jealousy: path.join(getcwd(), "traits", "jealous"),
    Traits.Manipulation: path.join(getcwd(), "traits", "manipulative"),
    Traits.Arrogance: path.join(getcwd(), "traits", "arrogant"),
    Traits.Suspicion: path.join(getcwd(), "traits", "suspicious"),
    Traits.Narcissism: path.join(getcwd(), "traits", "narcissistic"),
    Traits.Impulsiveness: path.join(getcwd(), "traits", "impulsive"),
    Traits.Selfishness: path.join(getcwd(), "traits", "selfish"),
}

sign_paths = {
    Signs.Aquarius: path.join(signs_dir, "Astrological_sign_Aquarius_at_the_Wisconsin_State_Capitol.jpeg"),
    Signs.Aries: path.join(signs_dir, "Astrological_sign_Aries_at_the_Wisconsin_State_Capitol.jpeg"),
    Signs.Virgo: path.join(signs_dir, "Astrological_sign_Virgo_at_the_Wisconsin_State_Capitol.jpeg"),
    Signs.Cancer: path.join(signs_dir, "Cancer_Astrological_Sign_at_the_Wisconsin_State_Capitol.jpeg"),
    Signs.Capricorn: path.join(signs_dir, "Capricornus_Astrological_Sign_at_the_Wisconsin_State_Capitol.jpeg"),
    Signs.Gemini: path.join(signs_dir, "Gemini_Astrological_Sign_at_the_Wisconsin_State_Capitol.jpeg"),
    Signs.Leo: path.join(signs_dir, "Leo_Astrological_Sign_at_the_Wisconsin_State_Capitol.jpeg"),
    Signs.Libra: path.join(signs_dir, "Libra_Astrological_Sign_at_the_Wisconsin_State_Capitol.jpeg"),
    Signs.Pisces: path.join(signs_dir, "Pisces_Astrological_Sign_at_the_Wisconsin_State_Capitol.jpeg"),
    Signs.Sagittarius: path.join(signs_dir, "Sagittarius_Astrological_Sign_at_the_Wisconsin_State_Capitol.jpeg"),
    Signs.Scorpio: path.join(signs_dir, "Scorpio_Astrological_Sign_at_the_Wisconsin_State_Capitol.jpeg"),
    Signs.Taurus: path.join(signs_dir, "Taurus_Astrological_Sign_at_the_Wisconsin_State_Capitol.jpeg")
}


class TraitMap(object):

    @staticmethod
    def get_random_target_trait_sign_pair():
        sign, trait = TraitMap.get_random_trait_sign_pair()
        while (not(sign in hit_map.keys())) or (not(trait in hit_map[sign])):
            sign, trait = TraitMap.get_random_trait_sign_pair()
        return trait, sign

    @staticmethod
    def get_random_nontarget_trait_sign_pair():
        sign, trait = TraitMap.get_random_trait_sign_pair()
        while (not(sign in hit_map.keys())) or trait in hit_map[sign]:
            sign, trait = TraitMap.get_random_trait_sign_pair()
        return trait, sign

    @staticmethod
    def get_random_trait_sign_pair():
        return TraitMap.get_random_sign(), TraitMap.get_random_trait()

    @staticmethod
    def get_random_trait():
        return choice(list(Traits))

    @staticmethod
    def get_random_sign():
        return choice(list(Signs))

    @staticmethod
    def get_sign_img(sign: Signs):
        return sign_paths[sign]

    @staticmethod
    def get_not_sign(sign: Signs):
        rand_sign = TraitMap.get_random_sign()

        while sign == rand_sign:
            rand_sign = TraitMap.get_random_sign()

        return rand_sign

    @staticmethod
    def get_random_trait_img(trait: Traits):
        return path.join(trait_dirs[trait], choice(listdir(trait_dirs[trait])))

    @staticmethod
    def get_not_trait(trait: Traits):
        rand_trait = TraitMap.get_random_trait()

        while trait == rand_trait:
            rand_trait = TraitMap.get_random_trait()

        return rand_trait

