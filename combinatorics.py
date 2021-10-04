from mana_value import *


def splits(tuple_to_split):
    '''\
        Return a list of sublists of tuples, where each sublist contains a distinct
        way of partitioning tuple_to_split into a left half and a right half.
        Example
        (0,1,2) -> [[(), (0,1,2)],
                    [(0,), (1,2)],
                    [(0,1), (2,)],
                    [(0,1,2), ()]] 
    '''
    if not(tuple_to_split):
        return []
    result = []
    n = len(tuple_to_split)
    n_breakpoints = n + 1
    for bp in range(n_breakpoints):
        result.append([tuple_to_split[:bp], tuple_to_split[bp:]])
    return result


def scry_splits(list_of_cards_to_scry):
    '''\
        Return a list of sublists of tuples representing the unique ways to
        scry given the list_of_cards_to_scry.
    '''
    n_cards_to_scry = len(list_of_cards_to_scry)
    if not(n_cards_to_scry):
        return None
    else:
        card_permutations = permutations(list_of_cards_to_scry)
        result = []
        for card_permutation in card_permutations:
            result.extend(splits(card_permutation))
        return result


def powerset(x):
    '''\
        Generate the powerset of x.
    '''
    if not(isinstance(x, list)):
        x = list(x)
    N = len(x)
    N_ = N + 1
    return chain.from_iterable(combinations(x, r) for r in range(N_))


def subpowerset(x, n=1, N=None):
    '''\
        Generate the subset of the powerset of x where the elements are subsets
        with cardinalities falling in the closed interval [n:N].
    '''
    if not(isinstance(x, list)):
        x = list(x)

    # Case: [None, None] means "each / all / every"
    if (n is None):
        # Case: n is never None unless N is also None
        if (N is not None):
            raise ValueError("n is None but N is not None, impossible.")
        n = N = len(x)

    # Case: [n, None] means "n <= size <= len(X)"
    elif (N is None):
        N = len(x)

    N_ = N + 1
    return chain.from_iterable(combinations(x, r) for r in range(n, N_))


def precon_subpowerset(x, set_of_cardinalities):
    '''\
        Generate the subset of the powerset of x where the elements are subsets with
        pre-specified cardinalities.
    '''
    if not(isinstance(x, list)):
        x = list(x)
    return chain.from_iterable(combinations(x, r) for r in set_of_cardinalities)


def constrained_range(n, N, banned):
    '''\
        Return the ascending closed interval of integers [n,N] with prohibited
        elements contained in banned <Iterable> removed. Can return an empty
        list.
    '''
    N_ = N + 1
    return list(filter(lambda i: not(i in banned), range(n, N_)))


def function_parameter_cartesian_product(list_of_parameter_ranges):
    '''\
        Return the cartesian product of the sublists of parameter ranges
        contained in list_of_parameter_ranges. Each element of the result
        represents a unique way of choosing a parameter for each of the
        parameters of a single function.
    '''
    return list(product(*list_of_parameter_ranges))


def multi_function_parameter_cartesian_product(list_of_sublist_of_parameter_ranges):
    '''\
        Each sublist of parameter ranges represents the choices of legal parameter values
        for each of the parameters of a function with multiple parameters.
        Each element of the result is a tuple of subtuples where each subtuple contains
        chosen parameters for each of the parameters of the corresponding function, and
        each tuple collectively represents a unique way of choosing a parameter for
        each of the parameters of each of the sublists (representing distinct functions)
        in list_of_sublist_of_parameter_ranges.
    '''
    return list(product(*[function_parameter_cartesian_product(list_of_parameter_ranges) for list_of_parameter_ranges in list_of_list_of_parameter_ranges]))

mfuncprod = multi_function_parameter_cartesian_product


def index_tuple_into_list_of_object_subset(index_tuple, list_of_objects):
    '''\
        Return the sublist of objects in list_of_objects defined by the indices
        in index_tuple.
    '''
    return [list_of_objects[i] for i in index_tuple]


def combinations_of_objects(size_of_combination, list_of_objects):
    '''\
        Take combinations of objects by labeling them with an index set,
        solving integer combinations of the index set, and then translating
        the index set combinations into combinations of objects.
    '''
    n_objects = len(list_of_objects)
    index_set = [i for i in range(n_objects)]
    index_combinations = combinations(index_set, size_of_combination)
    result = []
    for index_combination in index_combinations:
        result.append(index_tuple_into_list_of_object_subset(index_tuple=index_combination,
                                                             list_of_objects=list_of_objects))
    return result


def translate_list_of_sublist_of_objects_into_list_of_sublist_of_indices(list_of_sublist_of_objects):
    counter = 0
    result = []
    translation_dict = {}
    for sublist_of_objects in list_of_sublist_of_objects:
        derived_sublist = []
        for object in sublist_of_objects:
            derived_sublist.append(counter)
            translation_dict[counter] = object
            counter += 1
        result.append(derived_sublist)
    return result, translation_dict


def all_possible_ways_to_take_one_object_from_each_sublist_in_a_list_of_sublists_of_objects(list_of_sublist_of_objects):
    losloi, td = translate_list_of_sublist_of_objects_into_list_of_sublist_of_indices(list_of_sublist_of_objects)
    index_result = function_parameter_cartesian_product(losloi)
    result = []
    for tuple_of_indices in index_result:
        new_sublist = []
        for index in tuple_of_indices:
            new_sublist.append(td[index])
        result.append(new_sublist)
    return result

product_of_objects = all_possible_ways_to_take_one_object_from_each_sublist_in_a_list_of_sublists_of_objects


def pairs_to_consider(indices):
    '''\
        Return all pairs containing distinct indices given an iterable of indices,
        i.e., the cartesian product of the index set with itself, absent the diagonal.
    '''
    return filter(lambda pair: not(pair[0]==pair[1]), product(indices, indices))


def scry_permute(list_of_objects, sigma):
    '''\
        Sigma is a permutation of indices to be applied to list_of_objects
        to produce the indicated ordering.
    '''
    result = []
    n = list_of_objects
    for i in range(n):
        result.append(list_of_objects[sigma[i]])
    return list(result)
