from abstractions import *


########################################################
# Utility Functions For Filtering Iterables of Objects #
########################################################
# bool(obj.attr) == True
def pobj_(attr, objs):
    return list(filter(lambda obj: getattr(obj, attr), objs))

# bool(obj.attr) == False
def npobj_(attr, objs):
    return list(filterfalse(lambda obj: getattr(obj, attr), objs))

# obj.attr == val
def pobj(attr, val, objs):
    return list(filter(lambda obj: (getattr(obj, attr) == val), objs))

# obj.attr != val
def npobj(attr, val, objs):
    return list(filter(lambda obj: (getattr(obj, attr) != val), objs))

# val in obj.attr
def inpobj(attr, val, objs):
    return list(filter(lambda obj: (val in obj.attr), objs))

# val not in obj.attr
def ninpobj(attr, val, objs):
    return list(filter(lambda obj: not(val in obj.attr), objs))

# Split the items in iterable into two iterables in a tuple := t, where:
#   t[0] is the subset for which the predicate function holds; and,
#   t[1] is the subset for which the predicate function does not hold.
# Source: itertools documentation.
def partition(predicate, iterable):
    t1, t2 = tee(iterable)
    return filter(predicate, t1), filterfalse(predicate, t2)

# Same as partition except we return lists in the tuple instead of iterables
def partition_as_lists(predicate, iterable):
    t1, t2 = tee(iterable)
    return list(filter(predicate, t1)), list(filterfalse(predicate, t2))


###################################
# Classes For Encoding Predicates #
###################################
class P:
    '''\
        A predicate with a value_test(object) method that returns a boolean resulting from
        self.op(getattr(object, self.ref_attr), self.ref_val), where self.ref_val can be
        a dynamic value computed at test time.
    '''
    def __init__(self, ref_attr, op, ref_val):
        self.ref_attr = ref_attr
        self.op = op
        self._ref_val = ref_val

    @dynamic
    def ref_val(self):
        return self._ref_val

    def value_test(self, object):
        return self.op(getattr(object, self.ref_attr), self.ref_val)


class inP(P):
    '''\
        Test for the presence of a value in an iterable attribute of a reference object.
        Not to be confused with typeinP.
    '''
    def __init__(self, iterable_ref_attr, contained_ref_val):
        super().__init__(ref_attr=iterable_ref_attr, op=contains, ref_val=contained_ref_val)

    def value_test(self, object):
        # NOTE #
        # Over-rides P.value_test() to avoid the need for LHS argument in P (majority of Predicates).
        return self.op(getattr(object, self.ref_attr), self.ref_val)


class notinP(inP):
    '''\
        Test for the absence of a value in an iterable attribute of a reference object.
    '''
    def value_test(self, value):
        return not(super().value_test(value))


class typeinP(P):
    '''\
        Test for the presence of a value of a specified type in an iterable attribute of a reference object.
        Not to be confused with inP.
    '''
    def __init__(self, iterable_reference_attribute, reference_type):
        self.iterable_reference_attribute = iterable_reference_attribute
        self.reference_type = reference_type

    def value_test(self, object):
        return any(isinstance(value, self.reference_type) for value in getattr(object, self.iterable_reference_attribute))


class typenotinP(typeinP):
    '''\
        Test for the absence of a value of a specified type in an iterable attribute of a reference object.
        Not to be confused with notinP.
    '''
    def value_test(self, object):
        return not(super().value_test(object))


class idP(P):
    '''\
        Implement an identity predicate.
        value_test(self, object) ---> True, so long as object isn't None.
    '''
    def __init__(self):
        pass

    @property
    def ref_val(self):
        raise NotImplementedError("Identity predicates don't use the ref_val property.")

    def value_test(self, test_object):
        return not(test_object is None)


class identifyP(idP):
    '''\
        value_test(self, object) returns True if (self.ref_val is object).
        Useful for filtering lists of objects to match a target object, e.g.,
        identifyP(ref_val=LINKS.active_player) in a Selection using LINKS.player_objects
        as its set will return the singleton list containing the PlayerObject instance
        who is the active_player at test time.
        # NOTE #
        Not to be confused with (object.ref_attr is ref_val), provided by isP.
    '''
    def __init__(self, ref_val):
        self._ref_val = ref_val

    @dynamic
    def ref_val(self):
        return self._ref_val

    def value_test(self, test_object):
        return (test_object is self.ref_val)


class excludeP(identifyP):
    '''\
        value_test(self, object) returns True if not(self.ref_val is object).
        Useful for filtering lists of objects to match everything that is not a target object,
        e.g., excludeP(ref_val=LINKS.active_player) in a Selection_ using LINKS.player_objects
        as its source_set will return the singleton list containing the PlayerObject instance
        who is the non_active_player at test time (assuming a game with 2 players).
    '''
    def value_test(self, test_object):
        return not(super().value_test(test_object))


class anyP(idP):
    '''\
        Let comparison_value := getattr(test_object, self.ref_attr), and
            self.ref_val := an iterable of objects to match against based on identity.

        Then,
            value_test(self, test_object) returns True if, for at least one object in self.ref_val,
            self.ref_val[i], comparison_value is self.ref_val[i]        
    '''
    def __init__(self, ref_attr, ref_val):
        # NOTE #
        # ref_val is an iterable of objects that test_object.ref_attr may or may not be identified
        # with.
        self.ref_attr = ref_attr
        self._ref_val = ref_val

    @dynamic
    def ref_val(self):
        return self._ref_val

    def value_test(self, test_object):
        comparison_value = getattr(test_object, self.ref_attr)
        for candidate in self.ref_val:
            if (comparison_value is candidate):
                return True
        return False


class notanyP(anyP):
    '''\
        Opposite of anyP.
    '''
    def value_test(self, test_object):
        return not(super().value_test(test_object))


class differentP(identifyP):
    '''\
        Negation of identifyP.
        # NOTE #
        Not to be confused with not(object.ref_attr is ref_val), provided by isnotP.
    '''
    def value_test(self, test_object):
        return not(super().value_test(test_object))


class eqP(P):
    ''' object.ref_attr == ref_val '''
    def __init__(self, ref_attr, ref_val, **kwargs):
        super().__init__(ref_attr, eq, ref_val, **kwargs)


class notP(eqP):
    ''' object.ref_attr != ref_val '''
    def value_test(self, value):
        return not(super().value_test(value))


class lteP(P):
    ''' object.ref_attr <= ref_val '''
    def __init__(self, ref_attr, ref_val, **kwargs):
        super().__init__(ref_attr, le, ref_val, **kwargs)


class gteP(P):
    ''' object.ref_attr >= ref_val '''
    def __init__(self, ref_attr, ref_val, **kwargs):
        super().__init__(ref_attr, ge, ref_val, **kwargs)


class lifetotalP(gteP):
    '''\
        Subclass of gteP used to find players with sufficiently high lifetotals to pay
        life costs.

        object.lifetotal >= ref_val
    '''
    def __init__(self, ref_val, **kwargs):
        super().__init__(ref_attr='lifetotal', ref_val=ref_val, **kwargs)


class isP(P):
    '''\
        object.ref_attr is ref_val
        # NOTE #
        Not to be confused with: object is ref_val, provided by identifyP.
    '''
    def __init__(self, ref_attr, ref_val, **kwargs):
        super().__init__(ref_attr, is_, ref_val, **kwargs)


class isnotP(isP):
    '''\
        not(object.ref_attr is ref_val)
        # NOTE #
        Not to be confused with: not(object is ref_val), provided by differentP.
    '''
    def value_test(self, value):
        return not(super().value_test(value))


class typeP:
    '''\
        isinstance(object, self.ref_type)
        # NOTE #
        Not to be confused with: isinstance(object.ref_attr, ref_val), provided by exactinstP.
    '''
    def __init__(self, ref_type):
        self.ref_type = ref_type

    def value_test(self, value):
        return isinstance(value, self.ref_type)


class typenotP(typeP):
    '''\
        Negation of typeP.
        # NOTE #
        Not to be confusd with: not(isinstance(object.ref_attr, ref_val)), provided by notexactinstP.
    '''
    def value_test(self, value):
        return not(super().value_test(value))


class exactinstP(P):
    '''\
        isinstance(object.ref_attr, ref_val)
        # NOTE #
        Not to be confused with isinstance(object, ref_val), provided by typeP.
    '''
    def __init__(self, ref_attr, ref_val, **kwargs):
        super().__init__(ref_attr, isinstance, ref_val, **kwargs)


class notexactinstP(exactinstP):
    '''\
        not(isinstance(object.ref_attr, ref_val))
        # NOTE #
        Not to be confused with not(isinstance(object, ref_val)), provided by typenotP.
    '''
    def value_test(self, value):
        return not(super().value_test(value))


class anyinstP(P):
    '''\
        Returns true if isinstance(object.ref_attr, ref_val_i) for >= 1
        ref_val_i in self.ref_val <Iterable of Types>.
    '''
    def __init__(self, ref_attr, ref_val, **kwargs):
        super().__init__(ref_attr, isinstance, ref_val, **kwargs)

    def value_test(self, value):
        comparison_attribute_value = getattr(value, self.ref_attr)
        for acceptable_type in self.ref_val:
            if isinstance(comparison_attribute_value, acceptable_type):
                return True
        return False


class notanyinstP(anyinstP):
    '''\
        Returns true if object.ref_attr is not an instance of any of the ref_val_i types
        in self.ref_val <Iterable of Types>.
    '''
    def value_test(self, value):
        return not(super().value_test(value))


class Conjunction:
    '''\
        Support conjunctive composition of arbitrary predicates.
        Return True only if ALL of the constituent predicates return True.
    '''
    def __init__(self, *predicates):
        source_predicates = list(predicates)
        temp_predicates = []
        for predicate in source_predicates:
            if (predicate is None):
                raise ValueError("Tried to create a conjunction of predicates with at least one None.")
            else:
                temp_predicates.append(predicate)
        self.predicates = list(temp_predicates)

    def value_test(self, value):
        return all(predicate.value_test(value) for predicate in self.predicates)

CONJ = Conjunction


class Disjunction:
    '''\
        Support disjunctive composition of arbitrary predicates.
        Return True only if AT LEAST ONE of the constituent predicates returns True.
    '''
    def __init__(self, *predicates):
        source_predicates = list(predicates)
        temp_predicates = []
        for predicate in source_predicates:
            if (predicate is None):
                raise ValueError("Tried to creature a disjunction of predicates with at least one None.")
            else:
                temp_predicates.append(predicate)
        self.predicates = list(temp_predicates)

    def value_test(self, value):
        return any(predicate.value_test(value) for predicate in self.predicates)

DISJ = Disjunction


class Selection_:
    '''\
        Represent criteria which govern the task of making a selection.
        Support computation of all possible ways of making a selection that satisfies
        those criteria.

        source_set      The set of objects from which to select.

        predicate       Constrains selection on the basis of the properties of selected objects.

        sizes           Constrains the number of selected objects in a selection.
                        Note: Default value of sizes, [0, None], leads to considering the entire
                        set of selectable objects.
                        See also: subpowerset function in combinatorics.py
    '''
    def __init__(self, source_set, predicate, sizes=[0,None]):
        self._source_set = source_set
        self._predicate = predicate
        self.sizes = list(sizes)

    @dynamic
    def source_set(self):
        return self._source_set

    @dynamic
    def predicate(self):
        return self._predicate

    def selectable_objects(self, as_list=True):
        '''\
            Return the subset of the source set defined by the predicate---i.e., filter
            the source set to contain only objects with properties which satisfy the
            constraints on selected objects represented by the predicate.
        '''
        result = filter(lambda x: self.predicate.value_test(x), self.source_set)
        if as_list:
            return list(result)
        return result

    def selection_set(self, as_list=True):
        '''\
            Return the subset of the powerset of the set of selectable objects, which
            represents the set of legal selections according to the constraints on the:
                properties of selected objects; and,
                number of selected objects per selection.
            See also: the subpowerset function in combinatorics.py
        '''
        result = subpowerset(x=self.selectable_objects(), n=self.sizes[0], N=self.sizes[1])
        if as_list:
            return list(result)
        return result

    def __len__(self):
        return len(self.selectable_objects())

    def threshold(self, op, value):
        '''\
            Support queries concerning the number of objects in the source set which
            satisfy the predicate.
            Example:
                If you control 4 or more lands.
        '''
        return op(len(self), value)


class LockedSelection_(Selection_):
    def __init__(self, source_set, predicate, sizes=[0, None]):
        self._source_set = source_set
        self._predicate = predicate
        self.sizes = sizes
        self.selectable_objects_cache = None

    def selectable_objects(self, as_list=True):
        if (self.selectable_objects_cache is None):
            self.selectable_objects_cache = list(filter(lambda x: self.predicate.value_test(x), self.source_set))
        return self.selectable_objects_cache


class Selection(Selection_):
    ''' Eligible elements of this selection must be game objects. '''
    def __init__(self, predicate, sizes=[0,None], **kwargs):
        super().__init__(source_set=LINKS.game_objects, predicate=predicate, sizes=sizes, **kwargs)


class EffectSelection(Selection_):
    ''' Eligible elements of this selection are either player objects or game objects. '''
    def __init__(self, predicate, sizes=[0,None], **kwargs):
        super().__init__(source_set=LINKS.mutable_objects, predicate=predicate, sizes=sizes, **kwargs)


class LockedSelection(LockedSelection_):
    ''' Eligible elements of this locked selection must be game objects. '''
    def __init__(self, predicate, sizes=[0,None], **kwargs):
        super().__init__(source_set=LINKS.game_objects, predicate=predicate, sizes=sizes, **kwargs)


class PlayerSelection(Selection_):
    ''' Eligible elements of this selection must be player objects. '''
    def __init__(self, predicate, sizes=[0,None], **kwargs):
        super().__init__(source_set=LINKS.player_objects, predicate=predicate, sizes=sizes, **kwargs)


class AnyPLife(PlayerSelection):
    '''\
        Which players have a lifetotal >= ref_val?
        Primary use case: finding players who can pay lifetotal costs.
    '''
    def __init__(self, ref_val, sizes=[1,2]):
        super().__init__(predicate=lifetotalP(ref_val=ref_val), sizes=sizes)


class APLife(PlayerSelection):
    def __init__(self, ref_val, sizes=[1,1]):
        super().__init__(predicate=CONJ(lifetotalP(ref_val=ref_val), identifyP(LINKS.active_player)), sizes=sizes)


class NAPLife(PlayerSelection):
    def __init__(self, ref_val, sizes=[1,1]):
        super().__init__(predicate=CONJ(lifetotalP(ref_val=ref_val), identifyP(LINKS.non_active_player)), sizes=sizes)


class CPLife(PlayerSelection):
    def __init__(self, ref_val, sizes=[1,1]):
        super().__init__(predicate=CONJ(lifetotalP(ref_val=ref_val), identifyP(LINKS.current_player)), sizes=sizes)


class ImmaterialSelection(Selection_):
    ''' Eligible elements of this selection must be immaterial objects---e.g., abilities. '''
    def __init__(self, predicate, sizes=[0,None], **kwargs):
        super().__init__(set=LINKS.immaterial_objects, predicate=predicate, sizes=sizes, **kwargs)


class ZoneSelection(Selection_):
    ''' Eligible elements of this selection must be zones. '''
    def __init__(self, predicate, sizes=[0,None], **kwargs):
        super().__init__(set=LINKS.zones, predicate=predicate, sizes=sizes, **kwargs)


class UnsharedZoneSelection(Selection_):
    ''' Eligible elements of this selection must be unshared zones---e.g., a specific player's hand. '''
    def __init__(self, predicate, sizes=[0,None], **kwargs):
        super().__init__(set=LINKS.unshared_zones, predicate=predicate, sizes=sizes, **kwargs)


class SharedZoneSelection(Selection_):
    ''' Eligible elements of this selection must be shared zones---e.g., the battlefield. '''
    def __init__(self, predicate, sizes=[0,None], **kwargs):
        super().__init__(set=LINKS.shared_zones, predicate=predicate, sizes=sizes, **kwargs)


class ScrySelection(Selection_):
    '''\
        Special case of selection for returning objects from the top of a player's library
        for decisions related to scrying.

        # NOTE #
        Assumes that the number to scry is always a fixed number and there's never
        a 'scry up to X' or 'scry at least X but no more than Y' quantifiers.
        The selection_set that gets returned from this type of Selection contains
        2-tuples representing every possible way to partition self.source_set into two
        partitions, with at most one empty, where permutation of the elements matters.
    '''
    def __init__(self, sizes=[0,None]):
        self.sizes = sizes

    @property
    def n_to_scry(self):
        return self.sizes[0]

    @property
    def set(self):
        return GAME.current_player.zone_library[:self.n_to_scry]

    def selectable_objects(self, as_list):
        '''\
            This is only going to return the top n_to_scry objects from the
            current player's library. This shouldn't really ever be called.
        '''
        raise NotImplementedError("ScrySelections don't really have selectable_objects.")

    def selection_set(self, as_list=True):
        cards_to_scry = list(self.source_set)
        return scry_splits(cards_to_scry)


class IntegerSelection(Selection_):
    '''\
        Special case of selection for returning sets of integers which are
        eligible for numerical decisions.
    '''
    def __init__(self, min_value, max_value, sizes=[1,1]):
        self._min_value = min_value
        self._max_value = max_value + 1
        self.sizes = list(sizes)

    @dynamic
    def min_value(self):
        return self._min_value

    @dynamic
    def max_value(self):
        return self._max_value

    def selectable_objects(self, as_list=True):
        if as_list:
            return list(range(self.min_value, self.max_value))
        return range(self.min_value, self.max_value)

    # NOTE #
    # Can use the same selection_set() method as Selection_ since
    # the selection() method is over-written.


# NOTE # Namespace for centralizing / standardizing representation of frequently used predicates.
class PhiLibrary:
    def __init__(self):
        self.player_shortforms = [('ap', LINKS.active_player), ('nap', LINKS.non_active_player), ('curr', LINKS.current_player)]
        self.active_player = identifyP(ref_val=LINKS.active_player)
        self.active_player_opponents = differentP(ref_val=LINKS.active_player)
        self.non_active_player = identifyP(ref_val=LINKS.non_active_player)
        self.non_active_player_opponents = differentP(ref_val=LINKS.non_active_player)
        self.current_player = identifyP(ref_val=LINKS.current_player)
        self.current_player_opponents = differentP(ref_val=LINKS.current_player)
        self.player_object_identity = typeP(ExpandedPlayerObject)
        self.game_object_identity = typeP(Modifiable)
        self.zone_object_identity = typeP(Zone)
        self.zone_shared = eqP('shared',True)
        self.zone_unshared = notP('shared',True)
        self.player_kontrol_predicate_attributes = []
        self.player_zone_predicate_attributes = []
        self.object_zone_predicate_attributes = []
        self.relevant_object_zone_by_kontrol_predicate_attributes = []
        self.zone_identity_predicates = []
        self.generate_player_kontrol_predicates()
        self.generate_player_zone_predicates()
        self.generate_object_zone_predicates()
        self.generate_relevant_object_zone_by_kontrol_predicates()
        self.generate_zone_predicates()
        self.generate_charx_predicates()


    def _init_from_player_data(self, shared_ref_attr, true_class, negated_class, players_to_include=['ap', 'nap', 'curr']):
        '''\
            Generate predicates which inspect ownership in relation to active player, non active player,
            and current player status.
            Examples:
                owner_ap, controwner_not_curr, controller_nap
        '''
        for shortform in self.player_shortforms:
            if (shortform[0] in players_to_include):
                true_attribute = "{}_{}".format(shared_ref_attr, shortform[0])
                negated_attribute = "{}_not_{}".format(shared_ref_attr, shortform[0])
                setattr(self, true_attribute, true_class(shared_ref_attr, shortform[1]))
                setattr(self, negated_attribute, negated_class(shared_ref_attr, shortform[1]))
                self.player_kontrol_predicate_attributes.append(true_attribute)
                self.player_kontrol_predicate_attributes.append(negated_attribute)


    def _init_from_data(self, shared_ref_attr, true_list, true_class, negated_list, negated_class):
        n_true_list = len(true_list)
        n_negated_list = len(negated_list)
        for i in range(n_true_list):
            setattr(self, true_list[i], true_class(shared_ref_attr, true_list[i]))
        for i in range(n_negated_list):
            setattr(self, negated_list[i], negated_class(shared_ref_attr, negated_list[i]))

    def _init_from_data2(self, shared_ref_attr, true_list, true_class, negated_list, negated_class):
        n_true_list = len(true_list)
        for i in range(n_true_list):
            setattr(self, true_list[i], true_class(shared_ref_attr, true_list[i]))
            setattr(self, negated_list[i], negated_class(shared_ref_attr, true_list[i]))


    def generate_player_owner_predicates(self):
        self._init_from_player_data(shared_ref_attr="owner", true_class=isP, negated_class=notP)

    def generate_player_controller_predicates(self):
        self._init_from_player_data(shared_ref_attr="controller", true_class=isP, negated_class=notP)

    def generate_player_controwner_predicates(self):
        self._init_from_player_data(shared_ref_attr="controwner", true_class=isP, negated_class=notP)

    def generate_player_kontrol_predicates(self):
        self.generate_player_owner_predicates()
        self.generate_player_controller_predicates()
        self.generate_player_controwner_predicates()

    def generate_player_zone_predicates(self):
        for player_shortform in self.player_shortforms:
            true_attribute_name = "zones_{}".format(player_shortform[0])
            negated_attribute_name = "zones_not_{}".format(player_shortform[0])
            setattr(self, true_attribute_name, DISJ(self.zone_shared, isP("player", player_shortform[1])))
            setattr(self, negated_attribute_name, CONJ(self.zone_unshared, isnotP("player", player_shortform[1])))
            self.player_zone_predicate_attributes.extend([true_attribute_name,negated_attribute_name])

    def generate_zone_predicates(self):
        for zone_type in ZH.zone_types:
            zone_name = zone_type[0]
            zone_class = zone_type[1]
            true_attribute_name = "zone_is_{}".format(zone_name)
            negated_attribute_name = "zone_is_not_{}".format(zone_name)
            setattr(self, true_attribute_name, typeP(zone_class))
            setattr(self, negated_attribute_name, typenotP(zone_class))
            self.zone_identity_predicates.extend([true_attribute_name, negated_attribute_name])

    def generate_object_zone_predicates(self):
        for zone_type in ZH.zone_types:
            zone_name = zone_type[0]
            zone_class = zone_type[1]
            true_attribute_name = "zone_{}".format(zone_name)
            negated_attribute_name = "zone_not_{}".format(zone_name)
            setattr(self, true_attribute_name, exactinstP("current_zone", zone_class))
            setattr(self, negated_attribute_name, notexactinstP("current_zone", zone_class))
            self.object_zone_predicate_attributes.extend([true_attribute_name, negated_attribute_name])

    def generate_relevant_object_zone_by_kontrol_predicates(self):
        # NOTE # This can be extended as use cases arise.
        #        Currently only working with affirmative single zone checks.
        relevant_zone_predicate_attributes = ["zone_battlefield", "zone_graveyard", "zone_exile", "zone_library", "zone_hand"]
        relevant_kontrol_predicate_attributes = ['controwner_ap', 'controwner_not_ap', 'controwner_nap', 'controwner_not_nap', 'controwner_curr', 'controwner_not_curr']
        for relevant_zone_predicate_attribute in relevant_zone_predicate_attributes:
            for relevant_kontrol_predicate_attribute in relevant_kontrol_predicate_attributes:
                self @ [relevant_zone_predicate_attribute, relevant_kontrol_predicate_attribute]
                self.relevant_object_zone_by_kontrol_predicate_attributes.append(relevant_kontrol_predicate_attribute+"_"+relevant_zone_predicate_attribute)



    def single_card_types(self):
        self._init_from_data2(shared_ref_attr="card_types",
                              true_list=CARD_TYPES, true_class=inP,
                              negated_list=NON_CARD_TYPES, negated_class=notinP)


    def single_object_types(self):
        self._init_from_data(shared_ref_attr="object_types",
                             true_list=OBJECT_TYPES, true_class=inP,
                             negated_list=NON_OBJECT_TYPES, negated_class=notinP)


    def generate_charx_predicates(self):
        self.single_card_types()
        self.single_object_types()


    def _process_list_of_atoms(self, list_of_atoms):
        # Assumes that list_of_atoms is a non empty set of strings
        sorted_list_of_atoms = sorted(list_of_atoms)
        sorted_string_of_atoms = '_'.join(sorted_list_of_atoms)
        return sorted_list_of_atoms, sorted_string_of_atoms

    def __matmul__(self, list_of_atoms):
        '''\
            Override @ operator so that it can be used to ask for arbitrary compositions
            of atomic predicates which are then cached for the rest of the session.
            Example:
                FIND = PhiLibrary()
                APSelection = PlayerSelection(predicate=FIND@['active_player'], sizes=[1,1])
                creatures_nonartifact doesn't exist by default in FIND, but it will after:
                phi_creature_nonartifact = FIND @ ['nonartifact', 'creature']; AND,
                will be available afterwards with the reference FIND.creature_nonartifact
        '''
        sorted_list_of_atoms, sorted_string_of_atoms = self._process_list_of_atoms(list_of_atoms)
        if not(sorted_string_of_atoms in self.__dict__):
            individual_predicates = [getattr(self, atom) for atom in sorted_list_of_atoms]
            composition_of_predicates = CONJ(*individual_predicates)
            setattr(self, sorted_string_of_atoms, composition_of_predicates)
            return composition_of_predicates
        return getattr(self, sorted_string_of_atoms)



FIND = PhiLibrary()


# NOTE #
# Example extensions to PhiLibrary.
FIND.physical_status_tapped = eqP("physical_status_tapped", True)
FIND.physical_status_untapped = eqP("physical_status_tapped", False)
FIND.has_summoning_sickness = eqP("has_summoning_sickness", True)
FIND.not_has_summoning_sickness = eqP("has_summoning_sickness", False)
FIND.is_not_summoning_sick = DISJ(FIND.noncreature, FIND.not_has_summoning_sickness)

FIND.can_become_tapped = CONJ(FIND.is_not_summoning_sick, FIND.physical_status_untapped)
FIND.can_become_untapped = FIND.physical_status_tapped

FIND.can_be_permanent = CONJ(FIND.noninstant, FIND.nonsorcery)

FIND.nonaura_enchantment = CONJ(FIND.enchantment, notinP("subtypes", "aura"))
FIND.nonbasic_land = CONJ(FIND.land, notinP("supertypes", "basic"))

FIND.plains = CONJ(FIND.land, inP("subtypes", "plains"))
FIND.island = CONJ(FIND.land, inP("subtypes", "island"))
FIND.swamp = CONJ(FIND.land, inP("subtypes", "swamp"))
FIND.mountain = CONJ(FIND.land, inP("subtypes", "mountain"))
FIND.forest = CONJ(FIND.land, inP("subtypes", "forest"))

# Alias #
FIND.GOBJ = FIND.game_object_identity
FIND.POBJ = FIND.player_object_identity


#################################################
# Convenience Functions For Creating Predicates #
###############################################################################
# NOTE # These 'factories' support instances of ContinuousEffectGenerators    #
######## (or EffectComponents) which have Selections (or Deltas) which depend #
#        at least partially on properties of the associated host object.      #
###############################################################################
def create_object_equipped_by_host_predicate(instance):
    '''\
        Assumes that a static ability generating a continuous effect will use
        this function as a phi_factory, and that the host_object of the static ability
        instance will have an equipped_object attribute with value the equipped game
        object instance.
    '''
    return identifyP(ref_val=link_to_host_object_attribute_value(instance, 'equipped_object'))


def create_object_enchanted_by_host_predicate(instance):
    '''\
        Assumes that a Static Ability generating a Continuous Effect
        will use this function as a phi_factory, and that the host_object
        of the Static Ability instance will have an enchanted_object
        attribute with value the enchanted game object instance.
        Example:
            Enchanted permanent ...
    '''
    return identifyP(ref_val=link_to_host_object_attribute_value(instance, 'enchanted_object'))


def create_player_enchanted_by_host_predicate(instance):
    '''\
        Assumes that a Static Ability generating a Continuous Effect
        will use this function as a phi_factory, and that the host_object
        of the Static Ability instance will have an enchanted_player
        attribute with value the enchanted player object instance.
        Example:
            Enchanted player ...
    '''
    return identifyP(ref_val=link_to_host_object_attribute_value(instance, 'enchanted_player'))


def create_single_target_by_host_predicate(instance):
    '''\
        Assumes that a Resolution Continuous Effect Generator will use this function
        as a phi_factory, and that the host_object of the ResContFXGen will have a
        single_target_choice attribute with value equal to the object that is targeted.
    '''
    return identifyP(ref_val=link_to_host_object_attribute_value(instance, 'single_target_choice'))


def create_target_data_predicate(instance):
    '''\
        Assumes that a Resolution Continuous Effect Generator will use this function
        as a phi_factory, and that the host_object of the ResContFXGen will have a
        target_data attribute which is a list of temp_ids for each of the targets.
    '''
    return anyP(ref_attr="temp_id", ref_val=link_to_host_object_attribute_value(instance, 'target_data'))


def create_same_controller_predicate(instance):
    '''\
        Find objects with the same controller as the host_object
        of a ContinuousEffectGenerator or EffectComponent.
        Example:
            X you control ...
    '''
    return isP(ref_attr='controller',
               ref_val=link_to_host_object_attribute_value(instance, 'controller'))


def create_different_controller_predicate(instance):
    '''\
        Find objects with a different controller than the host_object
        of a ContinuousEffectGenerator or EffectComponent.
        Example:
            X your opponents control ...
    '''
    return isnotP(ref_attr='controller',
                  ref_val=link_to_host_object_attribute_value(instance, 'controller'))


def create_exclude_self_predicate(instance):
    '''\
        Find objects which are distinct from the host_object of a
        ContinuousEffectGenerator or EffectComponent.
        Example:
            Other X ...        
    '''
    return differentP(link_to_host_object(instance))


def create_host_object_predicate(instance):
    '''\
        Find the host_object of a ContinuousEffectGenerator or EffectComponent.
        Example:
            CARDNAME is ...
    '''
    return identifyP(link_to_host_object(instance))


################################
# Player Phi Factory Functions #
################################
def create_you_player_predicate(instance):
    '''\
        Find the PlayerObject who is the controller of the host_object of a
        ContinuousEffectGenerator or EffectComponent.
    '''
    return identifyP(link_to_host_object_attribute_value(instance, 'controller'))

def create_opponent_player_predicate(instance):
    '''\
        Find the PlayerObject who is the opponent of the controller of the host_object
        of a ContinuousEffectGenerator or EffectComponent.
    '''
    return excludeP(link_to_host_object_attribute_value(instance, 'controller'))

def create_all_player_predicate(instance):
    '''\
        Return a predicate that will be composed with FIND.player_object_identity
        to create a disjunction term which should match all PlayerObjects in LINKS.mutable_objects.
    '''
    return idP()


###################################
# Specific Examples of Predicates #
###################################
class HasKeywordAbility(typeinP):
    def __init__(self, keyword_ability_type):
        super().__init__(iterable_reference_attribute='abilities',
                         reference_type=keyword_ability_type)


class MissingKeywordAbility(typenotinP):
    def __init__(self, keyword_ability_type):
        super().__init__(iterable_reference_attribute='abilities',
                         reference_type=keyword_ability_type)
