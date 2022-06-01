from random import random, sample, choice
from enum import Enum, auto
from os import path, getcwd, listdir

GOOD_WORDS = [
    'Joyous',
    'Attractive',
    'Love',
    'Appealing',
    'Friend',
    'Glad',
    'Spectacular',
    'Fabulous',
    'Celebrate',
    'Cheerful',
    'Adore'
]

BAD_WORDS = [
    'Yucky',
    'Hate',
    'Bothersome',
    'Humiliate',
    'Nasty',
    'Angry',
    'Hurtful',
    'Disgust',
    'Pain',
    'Scorn',
    'Sadness',
    'Selfish',
    'Negative'
]

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
    Manipulative = auto(),
    Arrogant = auto(),
    Suspicious = auto(),
    Selfish = auto(),
    Narcissistic = auto(),
    Impulsive = auto(),


hit_map = {
    Signs.Leo: [Traits.Arrogant],
    Signs.Scorpio: [Traits.Jealousy]
}

signs_dir = path.join(getcwd(), "astro_signs")

trait_dirs = {
    Traits.Jealousy: path.join(getcwd(), "traits", "jealous"),
    Traits.Manipulative: path.join(getcwd(), "traits", "manipulative"),
    Traits.Arrogant: path.join(getcwd(), "traits", "arrogant"),
    Traits.Suspicious: path.join(getcwd(), "traits", "suspicious"),
    Traits.Narcissistic: path.join(getcwd(), "traits", "narcissistic"),
    Traits.Impulsive: path.join(getcwd(), "traits", "impulsive"),
    Traits.Selfish: path.join(getcwd(), "traits", "selfish"),
}

sign_paths_old = {
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

sign_paths = {
    Signs.Aquarius: path.join(signs_dir, "aquarius.png"),
    Signs.Aries: path.join(signs_dir, "aries.png"),
    Signs.Virgo: path.join(signs_dir, "virgo.png"),
    Signs.Cancer: path.join(signs_dir, "cancer.png"),
    Signs.Capricorn: path.join(signs_dir, "capricorn.png"),
    Signs.Gemini: path.join(signs_dir, "gemini.png"),
    Signs.Leo: path.join(signs_dir, "leo.png"),
    Signs.Libra: path.join(signs_dir, "libra.png"),
    Signs.Pisces: path.join(signs_dir, "pisces.png"),
    Signs.Sagittarius: path.join(signs_dir, "sagittarius.png"),
    Signs.Scorpio: path.join(signs_dir, "scorpio.png"),
    Signs.Taurus: path.join(signs_dir, "taurus.png")
}

sign_paths_new = {
    Signs.Aquarius: path.join(signs_dir, "aquarius.svg"),
    Signs.Aries: path.join(signs_dir, "aries.svg"),
    Signs.Virgo: path.join(signs_dir, "virgo.svg"),
    Signs.Cancer: path.join(signs_dir, "cancer.svg"),
    Signs.Capricorn: path.join(signs_dir, "capricorn.svg"),
    Signs.Gemini: path.join(signs_dir, "gemini.svg"),
    Signs.Leo: path.join(signs_dir, "leo.svg"),
    Signs.Libra: path.join(signs_dir, "libra.svg"),
    Signs.Pisces: path.join(signs_dir, "pisces.svg"),
    Signs.Sagittarius: path.join(signs_dir, "sagittarius.svg"),
    Signs.Scorpio: path.join(signs_dir, "scorpio.svg"),
    Signs.Taurus: path.join(signs_dir, "taurus.svg")
}


class TraitMap(object):

    @staticmethod
    def get_random_two_signs():
        r = sample(list(Signs), 2)
        return r[0], r[1]

    @staticmethod
    def get_random_bad_word():
        return choice(list(BAD_WORDS))

    @staticmethod
    def get_random_good_word():
        return choice(list(GOOD_WORDS))

    @staticmethod
    def get_random_target_trait_sign_pair():
        sign, trait = TraitMap.get_random_trait_sign_pair()
        while (not(sign in hit_map.keys())) or (not(trait in hit_map[sign])):
            sign, trait = TraitMap.get_random_trait_sign_pair()
        return trait, sign

    @staticmethod
    def get_random_nontarget_trait_sign_pair():
        sign, trait = TraitMap.get_random_trait_sign_pair()
        while (sign in hit_map.keys()) and trait in hit_map[sign]:
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

