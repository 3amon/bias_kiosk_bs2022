from random import random, choice
from enum import Enum, auto
from os import path, getcwd


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
    Jealous = auto(),
    Manipulative = auto(),
    Arrogant = auto(),
    Suspicious = auto(),
    Selfish = auto(),
    Narcissistic = auto(),
    Impulsive = auto(),


hit_map = {
    Signs.Leo: [Traits.Arrogant],
    Signs.Scorpio: [Traits.Jealous]
}

trait_dirs = {
    Traits.Jealous: path.join(getcwd(), "traits", "jealous"),
    Traits.Manipulative: path.join(getcwd(), "traits", "manipulative"),
    Traits.Arrogant: path.join(getcwd(), "traits", "arrogant"),
    Traits.Suspicious: path.join(getcwd(), "traits", "suspicious"),
    Traits.Narcissistic: path.join(getcwd(), "traits", "narcissistic"),
    Traits.Impulsive: path.join(getcwd(), "traits", "impulsive"),
}


class TraitMap(object):

    @staticmethod
    def get_random_hit_trait():
        sign, trait = TraitMap.get_random_trait()
        while not(trait in hit_map[sign]):
            sign, trait = TraitMap.get_random_trait()
        return trait, sign

    @staticmethod
    def get_random_miss_trait():
        sign, trait = TraitMap.get_random_trait()
        while trait in hit_map[sign]:
            sign, trait = TraitMap.get_random_trait()
        return trait, sign

    @staticmethod
    def get_random_trait():
        return choice(list(Signs)), choice((list(Traits)))
