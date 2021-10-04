from top import *


def extract_particles(mana_cost):
    '''\
        Takes a string representing a mana cost and returns a list containing
        the components. Mana cost representation follows the standard described
        at: https://scryfall.com/docs/api/colors

        Examples:
            extract_particles("{2}{W}") -> ["2", "W"]
            extract_particles("{0}") -> ["0"]
            extract_particles("") -> []
    '''
    if mana_cost:
        mana_cost_ = mana_cost[1:-1]
        if ("}{" in mana_cost_):
            mana_cost_ = mana_cost_.split("}{")
        else:
            mana_cost_ = [mana_cost_]
        return mana_cost_
    return []


def is_hybrid_particle(particle):
    return "/" in particle


def is_phyrexian_particle(particle):
    return "P" in particle


def mana_value_of_hybrid_particle(hybrid_particle):
    '''\
        202.3f
        When calculating the mana value of an object with a hybrid mana symbol in
        its mana cost, use the largest component of each hybrid symbol.
    '''
    components = hybrid_particle.split("/")
    max_value = 0
    for component in components:
        if component.isdigit():
            component_int = int(component)
        else:
            component_int = 1
        if (component_int > max_value):
            max_value = component_int
    return max_value


def mana_value_given_particles(particles, X):
    result = 0
    for particle in particles:
        if is_phyrexian_particle(particle):
            result += 1
        elif is_hybrid_particle(particle):
            result += mana_value_of_hybrid_particle(particle)
        elif particle == "X":
            result += X
        elif particle.isdigit():
            result += int(particle)
        else:
            result += 1
    return result


def solve_mana_value(mana_cost, X):
    '''\
        Used by Pieces to compute their mana value, with X passed when relevant,
        i.e., when the object is on the Stack.
    '''
    return mana_value_given_particles(extract_particles(mana_cost), X)
