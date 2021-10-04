import uuid
import re
import networkx as nx
import numpy as np
np.random.seed(112358)

from copy import deepcopy
from operator import add as ADD
from operator import sub as SUB
from operator import concat, eq, ne, iadd, isub, is_, contains, le, ge, itemgetter, xor
from time import time as TIMESTAMP
from itertools import chain, combinations, combinations_with_replacement, filterfalse
from itertools import groupby, permutations, product, tee
from collections import defaultdict
from collections import deque
from collections.abc import Iterable
from functools import partial, reduce


#####################
# Important Classes #
#####################
class Computable:
    '''\
        Subclasses are variations on getter methods for certain attributes using
        a compute() method. See also: class dynamic.
    '''
    pass


class dynamic(property):
    '''\
        Subclass of property which automatically handles resolving attribute values
        which are Computable and should have their compute() method called when accessed.
    '''
    def __get__(self, obj, objtype=None):
        result = super().__get__(obj, objtype)
        if isinstance(result, Computable):
            return result.compute()
        return result


#############
# Constants #
#############
GLOBAL_TIME = TIMESTAMP()


# NOTE #
# Layer 8 is used for continuous effects which modify players.
SUBLAYER_LIST = ['1a', '1b', '2', '3', '4', '5', '6', '7a', '7b', '7c', '7d', '8']
NO_CDA_SUBLAYERS = {'1a', '1b', '7a', '7b', '7c', '7d', '8'}

LAYER_SEVEN = set(['7a', '7b', '7c', '7d'])

COPIABLE_ATTRIBUTES = [
    'impl_name',
    'mana_cost',
    'card_types',
    'subtypes',
    'supertypes',
    'power',
    'toughness',
    'loyalty',
    'color',
    'abilities'
]


CHARX = COPIABLE_ATTRIBUTES + ['controller']


CARD_TYPES = [
    "artifact",
    "creature",
    "land",
    "planeswalker",
    "instant",
    "sorcery",
    "enchantment"
]
N_CARD_TYPES = len(CARD_TYPES)
NON_CARD_TYPES = [''.join(["non", string]) for string in CARD_TYPES]
N_NON_CARD_TYPES = len(NON_CARD_TYPES)


OBJECT_TYPES = [
    "token",
    "spell",
    "ability",
    "permanent",
    "card"
]
N_OBJECT_TYPES = len(OBJECT_TYPES)
NON_OBJECT_TYPES = [''.join(["non", string]) for string in OBJECT_TYPES]
N_NON_OBJECT_TYPES = len(NON_OBJECT_TYPES)


CREATURE_TYPES = [
    "Advisor", "Aetherborn", "Ally", "Angel", "Antelope", "Ape", "Archer", "Archon",
    "Army", "Artificer", "Assassin", "Assembly-Worker", "Atog", "Aurochs", "Avatar", "Azra", "Badger", "Barbarian",
    "Bard", "Basilisk", "Bat", "Bear", "Beast", "Beeble", "Beholder", "Berserker", "Bird", "Blinkmoth", "Boar", "Bringer",
    "Brushwagg", "Camarid", "Camel", "Caribou", "Carrier", "Cat", "Centaur", "Cephalid", "Chimera", "Citizen",
    "Cleric", "Cockatrice", "Construct", "Coward", "Crab", "Crocodile", "Cyclops", "Dauthi", "Demigod", "Demon",
    "Deserter", "Devil", "Dinosaur", "Djinn", "Dog", "Dragon", "Drake", "Dreadnought", "Drone", "Druid", "Dryad",
    "Dwarf", "Efreet", "Egg", "Elder", "Eldrazi", "Elemental", "Elephant", "Elf", "Elk", "Eye", "Faerie", "Ferret", "Fish",
    "Flagbearer", "Fox", "Fractal", "Frog", "Fungus", "Gargoyle", "Germ", "Giant", "Gnoll", "Gnome", "Goat", "Goblin",
    "God", "Golem", "Gorgon", "Graveborn", "Gremlin", "Griffin", "Hag", "Halfling", "Hamster", "Harpy", "Hellion",
    "Hippo", "Hippogriff", "Homarid", "Homunculus", "Horror", "Horse", "Human", "Hydra", "Hyena", "Illusion", "Imp",
    "Incarnation", "Inkling", "Insect", "Jackal", "Jellyfish", "Juggernaut", "Kavu", "Kirin", "Kithkin", "Knight", "Kobold",
    "Kor", "Kraken", "Lamia", "Lammasu", "Leech", "Leviathan", "Lhurgoyf", "Licid", "Lizard", "Manticore",
    "Masticore", "Mercenary", "Merfolk", "Metathran", "Minion", "Minotaur", "Mole", "Monger", "Mongoose",
    "Monk", "Monkey", "Moonfolk", "Mouse", "Mutant", "Myr", "Mystic", "Naga", "Nautilus", "Nephilim", "Nightmare",
    "Nightstalker", "Ninja", "Noble", "Noggle", "Nomad", "Nymph", "Octopus", "Ogre", "Ooze", "Orb", "Orc", "Orgg",
    "Otter", "Ouphe", "Ox", "Oyster", "Pangolin", "Peasant", "Pegasus", "Pentavite", "Pest", "Phelddagrif", "Phoenix",
    "Phyrexian", "Pilot", "Pincher", "Pirate", "Plant", "Praetor", "Prism", "Processor", "Rabbit", "Ranger", "Rat", "Rebel",
    "Reflection", "Rhino", "Rigger", "Rogue", "Sable", "Salamander", "Samurai", "Sand", "Saproling", "Satyr",
    "Scarecrow", "Scion", "Scorpion", "Scout", "Sculpture", "Serf", "Serpent", "Servo", "Shade", "Shaman",
    "Shapeshifter", "Shark", "Sheep", "Siren", "Skeleton", "Slith", "Sliver", "Slug", "Snake", "Soldier", "Soltari", "Spawn",
    "Specter", "Spellshaper", "Sphinx", "Spider", "Spike", "Spirit", "Splinter", "Sponge", "Squid", "Squirrel", "Starfish",
    "Surrakar", "Survivor", "Tentacle", "Tetravite", "Thalakos", "Thopter", "Thrull", "Tiefling", "Treefolk", "Trilobite",
    "Triskelavite", "Troll", "Turtle", "Unicorn", "Vampire", "Vedalken", "Viashino", "Volver", "Wall", "Warlock",
    "Warrior", "Weird", "Werewolf", "Whale", "Wizard", "Wolf", "Wolverine", "Wombat", "Worm", "Wraith", "Wurm",
    "Yeti", "Zombie", "Zubera"
]
CREATURE_TYPES = set([creature_type.lower() for creature_type in CREATURE_TYPES])


ARTIFACT_TYPES = set([
    "clue",
    "contraption",
    "equipment",
    "food",
    "fortification",
    "gold",
    "treasure",
    "vehicle"
])


ENCHANTMENT_TYPES = set([
    "aura",
    "cartouche",
    "class",
    "curse",
    "rune",
    "saga",
    "shard",
    "shrine"
])


BASIC_LAND_TYPES = set([
    "forest",
    "island",
    "mountain",
    "plains",
    "swamp"
])


OTHER_LAND_TYPES = set([
    "desert",
    "gate",
    "lair",
    "locus",
    "mine",
    "power-plant",
    "tower",
    "urza's"
])
LAND_TYPES = BASIC_LAND_TYPES | OTHER_LAND_TYPES


SPELL_TYPES = set([
    "adventure",
    "arcane",
    "lesson",
    "trap"
])


PLANESWALKER_TYPES = set([
    "Ajani", "Aminatou", "Angrath", "Arlinn", "Ashiok", "Bahamut", "Basri", "Bolas",
    "Calix", "Chandra", "Dack", "Dakkon", "Daretti", "Davriel", "Dihada", "Domri",
    "Dovin", "Ellywick", "Elspeth", "Estrid", "Freyalise", "Garruk", "Gideon", "Grist",
    "Huatli", "Jace", "Jaya", "Jeska", "Karn", "Kasmina", "Kaya", "Kiora", "Koth", "Liliana",
    "Lolth", "Lukka", "Mordenkainen", "Nahiri", "Narset", "Niko", "Nissa", "Nixilis", "Oko",
    "Ral", "Rowan", "Saheeli", "Samut", "Sarkhan", "Serra", "Sorin", "Szat", "Tamiyo", "Teferi",
    "Teyo", "Tezzeret", "Tibalt", "Tyvar", "Ugin", "Venser", "Vivien", "Vraska", "Will",
    "Windgrace", "Wrenn", "Xenagos", "Yanggu", "Yanling", "Zariel"
])
