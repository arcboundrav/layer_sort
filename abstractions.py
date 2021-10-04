from epochs import *


class SimpleAttributeReport(Computable):
    '''\
        Supply getattr(ref_obj, ref_attr) in response to compute() method call.
    '''
    def __init__(self, ref_obj, ref_attr):
        self._ref_obj = ref_obj
        self.ref_attr = ref_attr

    @dynamic
    def ref_obj(self):
        return self._ref_obj

    @ref_obj.setter
    def ref_obj(self, value):
        self._ref_obj = value

    def compute(self):
        return getattr(self.ref_obj, self.ref_attr)

SAR = SimpleAttributeReport


class LockedAttributeReport(SimpleAttributeReport):
    '''\
        Supply getattr(ref_obj, ref_attr) in response to compute() method call,
        but remember the first result, and refer back to that for all future calls.
    '''
    def __init__(self, **kwargs):
        self.locked_value = None
        super().__init__(**kwargs)

    def compute(self):
        if (self.locked_value is not None):
            self.locked_value = super().compute()
        return self.locked_value

LAR = LockedAttributeReport


class SimpleMethodReport(Computable):
    '''\
        See: SimpleAttributeReport, but permits calling a method with keyword arguments
             passed as a dictionary.
    '''
    def __init__(self, ref_obj, ref_method, method_kwargs=None):
        self._ref_obj = ref_obj
        self.ref_method = ref_method
        self.method_kwargs = method_kwargs

    @dynamic
    def ref_obj(self):
        return self._ref_obj

    @ref_obj.setter
    def ref_obj(self, value):
        self._ref_obj = value

    def compute(self):
        if (self.method_kwargs is not None):
            return self.ref_obj.ref_method(**self.method_kwargs)
        return self.ref_obj.ref_method()

SMR = SimpleMethodReport


class LockedMethodReport(Computable):
    '''\
        See: LockedAttributeReport, but permits calling a method with keyword arguments
             passed as a dictionary.
    '''
    def __init__(self, **kwargs):
        self.locked_value = None
        super().__init__(**kwargs)

    def compute(self):
        if (self.locked_value is None):
            if (self.method_kwargs is not None):
                self.locked_value = self.ref_obj.ref_method(**self.method_kwargs)
            else:
                self.locked_value = self.ref_obj.ref_method()
        return self.locked_value

LMR = LockedMethodReport


class ObjectCounter(Computable):
    '''\
        Tally the number of objects meeting a Selection criteria.
    '''
    def __init__(self, selection):
        self.selection = selection

    def compute(self):
        '''\
            Selection_ instances override __len__(self); they compute
            the set of objects they describe to before returning their size.
        '''
        return len(self.selection)


class ComputeWrapper(Computable):
    '''\
        Wrap arbitrary (possibly hard-coded special case) functions
        with this class to allow them to slot into places where
        a compute() method (returning a dependent value) is expected.
    '''
    def __init__(self, func, kwargdict=None):
        self.func = func
        self.kwargdict = kwargdict

    def compute(self):
        if (self.kwargdict is None):
            return self.func()
        return self.func(**self.kwargdict)



class ConcatReduction(Computable):
    '''\
        Support attribute value assignments which are concatenations of pre-existing lists
        with specified sequences.
    '''
    def __init__(self, ref_attr, seq_to_concat, ref_obj=None):
        self.ref_attr = ref_attr
        self.seq_to_concat = seq_to_concat
        self.ref_obj = ref_obj

    def compute(self):
        return reduce(concat, [list(getattr(self.ref_obj, self.ref_attr))], self.seq_to_concat)


class RulesTextAndCopiableEffectAbilityRemover(Computable):
    '''\
        Setting the land types of an object to a specific set of land types
        involves the removal of all abilities which originate from that object's
        rules text and copiable effects affecting that object, but not abilities
        granted to that object from other effects.
    '''
    def __init__(self, ref_obj=None):
        self.ref_obj = ref_obj

    def compute(self):
        new_value = []
        old_value = getattr(self.ref_obj, "abilities")
        for ability in old_value:
            if not(ability.origin in ["rules_text", "copiable_effect"]):
                new_value.append(ability)
        return new_value


class IdempotentManaAbilityGrant(Computable):
    '''\
        Used to confer intrinsic basic land type mana abilities.
        Assumes that mana ability instances do not require __init__ arguments.
        Will not add a duplicate instance of a mana ability.
    '''
    def __init__(self, mana_ability_types_to_grant):
        self.mana_ability_types_to_grant = mana_ability_types_to_grant
        self.ref_obj = None

    def compute(self):
        mana_abilities_to_grant = []
        extant_abilities = list(getattr(self.ref_obj, 'abilities'))
        for mana_ability_type in self.mana_ability_types_to_grant:
            mana_ability = mana_ability_type()
            if not(mana_ability in extant_abilities):
                mana_abilities_to_grant.append(mana_ability)
        return extant_abilities + mana_abilities_to_grant


#########################################################
# Support Effect Components Which Add Keyword Abilities #
#########################################################

class KeywordAbilityGrant(Computable):
    '''\
        Encodes the intention to grant one or more keyword abilities to a given object,
        in a manner which is sensitive to prohibitions against that object gaining
        certain keyword abilities. 
    '''
    def __init__(self, kwa_types_to_add):
        self.kwa_types_to_add = kwa_types_to_add
        self.ref_obj = None

    def derive_prohibited_kwa_types(self, existing_abilities):
        kwa_prohibitions = list(filter(lambda x: hasattr(x, 'prohibited_kwa_type'), existing_abilities))
        return [prohibition.prohibited_kwa_type for prohibition in kwa_prohibitions]

    def compute(self):
        new_abilities = []
        existing_abilities = list(getattr(self.ref_obj, 'abilities'))
        prohibited_kwa_types = self.derive_prohibited_kwa_types(existing_abilities)
        for kwa_type_to_add in self.kwa_types_to_add:
            if not(kwa_type_to_add in prohibited_kwa_types):
                kwa = kwa_type_to_add(host_object=self.ref_obj, origin='granted')
                new_abilities.append(kwa)
        return existing_abilities + new_abilities


class ProhibitKeywordAbility(Computable):
    '''\
        Represent prohibitions against objects gaining certain keyword abilities.
    '''
    def __init__(self, prohibition_to_add):
        self.prohibition_to_add = prohibition_to_add
        self.ref_obj = None

    def compute(self):
        new_abilities = [self.prohibition_to_add]
        existing_abilities = list(getattr(self.ref_obj, 'abilities'))
        return existing_abilities + new_abilities


class KeywordAbilityLoss(Computable):
    '''\
        Remove all instances of keyword abilities possessed by a given object
        that match each of the specified types.
    '''
    def __init__(self, kwa_types_to_lose):
        self.kwa_types_to_lose = kwa_types_to_lose
        self.ref_obj = None

    def should_lose(self, ability):
        for kwa_type_to_lose in self.kwa_types_to_lose:
            if isinstance(ability, kwa_type_to_lose):
                return True
        return False

    def compute(self):
        new_abilities = []
        existing_abilities = list(getattr(self.ref_obj, 'abilities'))
        for existing_ability in existing_abilities:
            if not(self.should_lose(existing_ability)):
                new_abilities.append(existing_ability)
        return new_abilities


class StaticAbilityGrant(Computable):
    '''\
        Confer a static ability to an object in a manner which ensures the
        static ability, as an effect generator, is synced to the object hosting it,
        while annotating the origin of the static ability.
    '''
    def __init__(self, static_ability_type_to_add):
        self.static_ability_type_to_add = static_ability_type_to_add
        self.ref_obj = None

    def compute(self):
        existing_abilities = list(getattr(self.ref_obj, 'abilities'))
        static_ability = self.static_ability_type_to_add(host_object=self.ref_obj)
        static_ability.origin = "granted"
        return existing_abilities + [static_ability]


class UnionReduction(ConcatReduction):
    '''\
        Support attribute value assignments which involve adding >= 1 elements to an
        underlying set.
    '''
    def compute(self):
        return reduce(set.union, [getattr(self.ref_obj, self.ref_attr), self.seq_to_concat])


class SetFiltration(ConcatReduction):
    '''\
        Support attribute value assignments which involve removing >= 1 elements from an
        underlying set.
    '''
    def compute(self):
        src_set = getattr(self.ref_obj, self.ref_attr)
        return src_set - self.seq_to_concat


class Lambda(Computable):
    '''\
        Support arbitrary functions via composition of binary operations.
        l_operand and r_operand can be:
            Computable; or,
            a fixed a priori value.
    '''
    def __init__(self, operator, l_operand, r_operand):
        self.operator = operator
        self.l_operand = l_operand
        self.r_operand = r_operand
        self.computed_l_operand = None
        self.computed_r_operand = None
        self.ref_obj = None

    def compute_operand(self, operand):
        if isinstance(operand, Computable):
            # NOTE # Propagate reference object.
            operand.ref_obj = self.ref_obj
            return operand.compute()
        return operand

    def compute_operands(self):
        self.computed_l_operand = self.compute_operand(self.l_operand)
        self.computed_r_operand = self.compute_operand(self.r_operand)

    def compute(self):
        self.compute_operands()
        return self.operator(self.computed_l_operand, self.computed_r_operand)


class ConstantLambda(Lambda):
    def __init__(self, constant_value):
        # NOTE #
        # Ensure <Iterable> constant_values are copied before assignment.
        self.constant_value = copy_sensitive(constant_value)

    def compute(self):
        return self.constant_value


class Delta(Computable):
    '''\
        Encode the intention to assign the result of an arbitrary function to >=1 attributes
        of an eventual target object.
    '''
    def __init__(self, reference_attributes, arbitrary_function):
        self.reference_attributes = list(reference_attributes)
        self.arbitrary_function = arbitrary_function

    def compute(self, ref_obj):
        return self.arbitrary_function.compute()

D = Delta


class K(Delta):
    '''\
        Encode the intention to assign a pre-specified constant value to >=1 attributes
        of an eventual target object.
    '''
    def __init__(self, reference_attributes, constant_value):
        self.reference_attributes = reference_attributes
        self._constant_value = copy_sensitive(constant_value)

    @dynamic
    def constant_value(self):
        return self._constant_value

    def compute(self, ref_obj):
        return self.constant_value


class AbilitiesK(K):
    '''\
        CopyEffectComponent.generate_deltas() sets CopyEffectComponent.deltas to a list of
        Ks, one for each of the copiable values. This takes place before the copier object
        is necessarily known. It will, however, be known at the moment that the K meant
        to assign the copiable value of abilities is told to do so---when that copier object
        is passed as the ref_obj to K.compute(ref_obj).
        In this special case, we want to make sure the ability instances in the abilities list
        are cloned so that their references / dependencies are correct and don't act like
        the host_object of the abilities is the source object that is being copied by the copier
        object.
    '''
    def compute(self, ref_obj):
        abilities = []
        for ability in self.constant_value:
            # For placeholders
            if (type(ability) == str):
                abilities.append(ability)
            else:
                new_ability = ability.clone_for_new_host_object(new_host_object=ref_obj)
                new_ability.origin = "copiable_effect"
                abilities.append(new_ability)
        return abilities


class ReflexiveDelta(Delta):
    '''\
        Encodes the intention to assign the result of an arbitrary function to >= 1 attributes
        of an eventual target object... and said function depends, partially, or fully, on
        attribute values possessed by the object it targets in the first place.
        Example:
            Target player gains 5 life.
    '''
    def compute(self, ref_obj):
        # NOTE #
        # Unlike Delta instances, propagate ref_obj so that self.arbitrary_function
        # can take it into account when its compute() method is called.
        self.arbitrary_function.ref_obj = ref_obj
        return self.arbitrary_function.compute()

rD = ReflexiveDelta


class LoseRulesTextAndCopiableEffectAbilities(ReflexiveDelta):
    def __init__(self):
        super().__init__(reference_attributes=['abilities'],
                         arbitrary_function=RulesTextAndCopiableEffectRemover())


class AddKeywordAbilities(ReflexiveDelta):
    def __init__(self, kwa_types_to_add):
        super().__init__(reference_attributes=['abilities'],
                         arbitrary_function=KeywordAbilityGrant(kwa_types_to_add=kwa_types_to_add))


class BanKeywordAbility(ReflexiveDelta):
    def __init__(self, prohibition_to_add):
        super().__init__(reference_attributes=['abilities'],
                         arbitrary_function=ProhibitKeywordAbility(prohibition_to_add=prohibition_to_add))


class LoseKeywordAbilities(ReflexiveDelta):
    def __init__(self, kwa_types_to_lose):
        super().__init__(reference_attributes=['abilities'],
                         arbitrary_function=KeywordAbilityLoss(kwa_types_to_lose=kwa_types_to_lose))


class AddStaticAbility(ReflexiveDelta):
    def __init__(self, static_ability_type_to_add):
        super().__init__(reference_attributes=['abilities'],
                         arbitrary_function=StaticAbilityGrant(static_ability_type_to_add=static_ability_type_to_add))


########
# NOTE #
##################################################################################################
# The following subclasses are added as API shortcuts---common examples of intending to assign
# new values to >=1 attributes of an eventual target object which vary as a function of the
# current value of a reference attribute of that target object at the time of computation.
##################################################################################################
class BecomePermanentObjectType(ReflexiveDelta):
    def __init__(self):
        super().__init__(reference_attributes=['object_types'],
                         arbitrary_function=UnionReduction(ref_attr='object_types',
                                                           seq_to_concat=set(['permanent'])))

class BecomePermanentSpellObjectType(ReflexiveDelta):
    def __init__(self):
        super().__init__(reference_attributes=['object_types'],
                         arbitrary_function=UnionReduction(ref_attr='object_types',
                                                           seq_to_concat=set(['permanent spell'])))


class LosePermanentObjectType(ReflexiveDelta):
    def __init__(self):
        super().__init__(reference_attributes=['object_types'],
                         arbitrary_function=SetFiltration(ref_attr='object_types',
                                                          seq_to_concat=set(['permanent'])))


class LosePermanentSpellObjectType(ReflexiveDelta):
    def __init__(self):
        super().__init__(reference_attributes=['object_types'],
                         arbitrary_function=SetFiltration(ref_attr='object_types',
                                                          seq_to_concat=set(['permanent spell'])))


class BecomeCopyOfPermanentSpellType(ReflexiveDelta):
    def __init__(self):
        super().__init__(reference_attributes=['object_types'],
                         arbitrary_function=UnionReduction(ref_attr='object_types',
                                                           seq_to_concat=set(['kopy permanent spell'])))


class LosePermanentSpellObjectType(ReflexiveDelta):
    def __init__(self):
        super().__init__(reference_attributes=['object_types'],
                         arbitrary_function=SetFiltration(ref_attr='object_types',
                                                          seq_to_concat=set(['kopy permanent spell'])))


class BecomeTokenObjectType(ReflexiveDelta):
    def __init__(self):
        super().__init__(reference_attributes=['object_types'],
                         arbitrary_function=UnionReduction(ref_attr='object_types',
                                                           seq_to_concat=set(['token'])))
##################################################################################################

class RequestTimestamp(Computable):
    '''\
        Support Deltas that can assign timestamp values in real-time.
    '''
    def __init__(self):
        self.ref_obj = None

    def compute(self):
        return TIMESTAMP()

REQUEST_TIMESTAMP = RequestTimestamp()


class RequestUUID(Computable):
    '''\
        Support Deltas that can assign a unique id in real-time.
    '''
    def __init__(self):
        self.ref_obj = None

    def compute(self):
        return uuid.uuid4().hex

REQUEST_UUID = RequestUUID()



class UpdateTimestamp(Delta):
    def __init__(self):
        super().__init__(reference_attributes=['timestamp'], arbitrary_function=REQUEST_TIMESTAMP)


class IdentifierUpdate(Delta):
    def __init__(self):
        super().__init__(reference_attributes=['identified_uuid'], arbitrary_function=REQUEST_UUID)


###############################################
# Adding / subtracting relative amount deltas #
###############################################
class ReflexiveAdditionDelta(ReflexiveDelta):
    '''\
        # NOTE #
        This ReflexiveAdditionDelta's arbitrary_function attribute is a Lambda which has
        a pre-specified right operand: a SimpleAttributeReport (SAR) with ref_obj=None and
        ref_attr=a string passed during instantiation.

        As a ReflexiveDelta subclass, the compute(self, ref_obj) method actually does
        something with the value passed to its ref_obj argument: it assigns ref_obj
        to be the value of self.arbitrary_function's ref_obj attribute, prior to
        returning self.arbitrary_function.compute()

        As a Lambda, self.arbitrary_function's compute() method will try to compile its operands
        before returning its result. This process will notice that the right operand is a
        Computable, and so before calling the right operand's compute() method, it will
        assign self.ref_obj to be the value of its right operand's ref_obj attribute.

        In general, this technique ensures propagation of the original reference object
        passed to this ReflexiveDelta's compute() method to each node of the computation
        subtree represented by any of the Lambda's operands, while allowing a priori specification
        of the dependence of >=1 Lambda's operands on an object that it doesn't know about at
        instantiation time.

        In specific, it supports an assignment of a new value to the ref_obj's ref_attr attribute
        which is a function of the value of the ref_obj's ref_attr attribute at the time
        that modification is attempted.

        TL;DR: Encodes the intention to assign a new value to a reference object's reference
               attribute which will be computed using addition, amount, and the value of that
               reference object's reference attribute at the time immediately prior to modifying
               that reference object's reference attribute.

        # NOTE #
        Assumes:
            amount is always a non-negative integer representing the magnitude of the change; and,
            addition is the default change---substraction is accomplished by passing False to gain.
    '''
    def __init__(self, ref_attr, amount, gain=True):
        if not(gain):
            amount = -1 * amount
        super().__init__(reference_attributes=[ref_attr],
                         arbitrary_function=Lambda(ADD,
                                                   amount,
                                                   SAR(None, ref_attr)))


class LifetotalDelta(ReflexiveAdditionDelta):
    '''\
        Encodes the intention to assign a new value to a reference object's lifetotal
        attribute which will be computed using amount, and the current value of that
        reference object's lifetotal attribute at the time immediately prior to
        modifying that reference object's lifetotal attribute.
    '''
    def __init__(self, amount, gain=True):
        super().__init__(ref_attr="lifetotal",
                         amount=amount,
                         gain=gain)



class PowerDelta(ReflexiveAdditionDelta):
    '''\
        For use by Effect Components in Sublayer 7c which modify Power without
        defining it or setting it to a specific value. See also: ReflexiveAdditionDelta
        for an explanation of the arbitrary function.
    '''
    def __init__(self, amount, gain=True):
        super().__init__(ref_attr="power",
                         amount=amount,
                         gain=gain)


class ToughnessDelta(ReflexiveAdditionDelta):
    '''\
        For use by Effect Components in Sublayer 7c which modify Toughness without
        defining it or setting it to a specific value. See also: ReflexiveAdditionDelta
        for an explanation of the arbitrary function.
    '''
    def __init__(self, amount, gain=True):
        super().__init__(ref_attr="toughness",
                         amount=amount,
                         gain=gain)


class MarkerTotalDelta(ReflexiveAdditionDelta):
    '''\
        Encode the intention to add or subtract $amount markers of marker_type from
        a reference object, which requires taking into account the current number of
        markers of that type already possessed by that reference object at the time
        immediately prior to making the change.
    '''
    def __init__(self, amount, gain=True, marker_type='defaultmarkertype'):
        marker_ref_attr = 'marker_{}'.format(marker_type)
        super().__init__(ref_attr=marker_ref_attr,
                         amount=amount,
                         gain=gain)


class ReferenceLibrary:
    '''\
        An instance of ReferenceLibrary acts as a central reference point for accessing
        'global' variables. Since each of the attribute values of the ReferenceLibrary's
        attributes are SimpleAttributeReport (SAR) instances, querying an attribute value
        will return a value that is correct at the time of query, like a @property, while
        allowing specification of where to look for the value in advance.
        This design permits encoding references to 'global' variables as direct references
        to the attributes of a single object, without locking in the values to their value
        at time of instantiation.

        Example Use:
            Selections encode the intention to extract a subset from a default set of objects
            after filtering that set of objects with a predicate, for example a Selection which
            only ever pertains to Game Objects and never Players or Immaterials. However,
            the set of Game Objects might have elements added or removed during the course
            of a game. Instantiating a Selection with its default set assigned to a global variable
            called GAME_OBJECT_LIST, for example, causes it to fail to consider changes to that
            variable that occur after the Selection is instantiated. Assume we instantiate the
            ReferenceLibrary as an objects called LINKS. Instantiating a Selection with its
            default set assigned to LINKS.game_objects while making its default set attribute
            @dynamic avoids this problem. The default set will be returned dynamically and will
            reflect any changes to the underlying set over time, while maintaining the ease of
            encoding the reference to the 'global' variable. This layer of abstraction is
            also motivated by GAME taking on different game statedata during tree searches.
    '''
    def __init__(self):
        self.active_player = SAR(ref_obj=GAME, ref_attr="active_player")
        self.non_active_player = SAR(ref_obj=GAME, ref_attr="non_active_player")
        self.current_player = SAR(ref_obj=GAME, ref_attr="current_player")
        self.game_objects = SAR(ref_obj=GAME, ref_attr="list_of_game_objects")
        self.player_objects = SAR(ref_obj=GAME, ref_attr="list_of_player_objects")
        self.mutable_objects = SAR(ref_obj=GAME, ref_attr="list_of_mutable_objects")
        self.immaterial_objects = SAR(ref_obj=GAME, ref_attr="list_of_immaterial_objects")
        self.zones = SAR(ref_obj=ZH, ref_attr="zones")
        self.unshared_zones = SAR(ref_obj=ZH, ref_attr="unshared_zones")
        self.shared_zones = SAR(ref_obj=ZH, ref_attr="shared_zones")
        #####
        self.active_idx = SAR(ref_obj=GAME, ref_attr='active_idx')
        self.gameover = SAR(ref_obj=GAME, ref_attr='gameover')
        self.limbo = SAR(ref_obj=GAME, ref_attr='limbo')
        self.n_extra_turns = SAR(ref_obj=GAME, ref_attr='n_extra_turns')
        self.current_turn = SAR(ref_obj=GAME, ref_attr='current_turn')
        #####

LINKS = ReferenceLibrary()


###################################################
# Convenience Functions For Creating Abstractions #
###################################################
def link_to_host_object(instance):
    '''\
        Convenience function to make instantiations involving nested @dynamic
        Simple Attribute Reports for accessing attributes of a Static Ability's
        host_object easier to read.
    '''
    return SAR(ref_obj=instance, ref_attr="host_object")


def link_to_host_object_attribute_value(instance, ref_attr):
    '''\
        Convenience function to make instantiations involving nested @dynamic
        Simple Attribute Reports for accessing attribute of a Static Ability's
        host_object easier to read.
    '''
    return SAR(ref_obj=link_to_host_object(instance),
               ref_attr=ref_attr)


def create_host_object_imitation_delta(reference_attributes, external_attribute, fx_component):
    '''\
        A component needs to generate a constant delta that arrives at the value to assign
        to the given reference_attributes by dynamically querying the external_attribute
        of its host_object. A component's host_object is a property returned by asking
        its reference_effect for its reference_ability which has a host_object attribute.
        Example use case is a static ability possessed by an enchantment aura which sets
        the controller attribute of an enchanted permanent to be equal to the value of
        the static ability's host object (the enchantment)'s controller.
    '''
    return K(reference_attributes=reference_attributes,
             constant_value=SAR(ref_obj=SAR(ref_obj=fx_component,
                                            ref_attr="host_object"),
                                ref_attr=external_attribute))



##################################################
# Specific Deltas Used By Static Ability Effects #
##################################################
#######################
# Abstraction Aliases #
#######################
UnionR = UnionReduction
ConcatR = ConcatReduction


####################################
# Card Types, Subtypes, Supertypes #
####################################
class AddCardTypes(ReflexiveDelta):
    def __init__(self, set_of_card_types_to_add):
        super().__init__(reference_attributes=['card_types'],
                         arbitrary_function=UnionR(ref_attr='card_types',
                                                   seq_to_concat=set_of_card_types_to_add))

class AddAllCreatureTypes(ReflexiveDelta):
    def __init__(self):
        super().__init__(reference_attributes=['subtypes'],
                         arbitrary_function=UnionR(ref_attr='subtypes',
                                                   seq_to_concat=set(CREATURE_TYPES)))

class LoseAllCreatureTypes(ReflexiveDelta):
    def __init__(self):
        super().__init__(reference_attributes=['subtypes'],
                         arbitrary_function=SetFiltration(ref_attr='subtypes',
                                                          seq_to_concat=set(CREATURE_TYPES)))

class AddSubtypes(ReflexiveDelta):
    def __init__(self, set_of_subtypes_to_add):
        super().__init__(reference_attributes=['subtypes'],
                         arbitrary_function=UnionR(ref_attr='subtypes',
                                                   seq_to_concat=set_of_subtypes_to_add))

class AddSupertypes(ReflexiveDelta):
    def __init__(self, set_of_supertypes_to_add):
        super().__init__(reference_attributes=['supertypes'],
                         arbitrary_function=UnionR(ref_attr='supertypes',
                                                   seq_to_concat=set_of_supertypes_to_add))


class AddPlaneswalkerCardType(AddCardTypes):
    def __init__(self):
        super().__init__(set_of_card_types_to_add=set(['planeswalker']))

class AddArtifactCardType(AddCardTypes):
    def __init__(self):
        super().__init__(set_of_card_types_to_add=set(['artifact']))

class AddCreatureCardType(AddCardTypes):
    def __init__(self):
        super().__init__(set_of_card_types_to_add=set(['creature']))

class AddEnchantmentCardType(AddCardTypes):
    def __init__(self):
        super().__init__(set_of_card_types_to_add=set(['enchantment']))


class LoseAllLandTypes(ReflexiveDelta):
    def __init__(self):
        super().__init__(reference_attributes=['subtypes'],
                         arbitrary_function=SetFiltration(ref_attr="subtypes",
                                                          seq_to_concat=LAND_TYPES))

class AddLandTypePlains(AddSubtypes):
    def __init__(self):
        super().__init__(set_of_subtypes_to_add=set(['plains']))

class AddLandTypeIsland(AddSubtypes):
    def __init__(self):
        super().__init__(set_of_subtypes_to_add=set(['island']))

class AddLandTypeSwamp(AddSubtypes):
    def __init__(self):
        super().__init__(set_of_subtypes_to_add=set(['swamp']))

class AddLandTypeMountain(AddSubtypes):
    def __init__(self):
        super().__init__(set_of_subtypes_to_add=set(['mountain']))

class AddLandTypeForest(AddSubtypes):
    def __init__(self):
        super().__init__(set_of_subtypes_to_add=set(['forest']))



class SetFixedController(K):
    '''\
        For use by Sublayer 2 Effect Components which set the controller of
        game objects to a fixed value.
    '''
    def __init__(self, constant_value):
        super().__init__(reference_attributes=['controller'],
                         constant_value=constant_value)


class SetFixedPT(K):
    '''\
        For use by Sublayer 7a Effect Components which define power and toughness
        to the same fixed apriori value; or, Sublayer 7b Effect Components which
        set base power and base toughness to the same fixed apriori value.
    '''
    def __init__(self, constant_value):
        super().__init__(reference_attributes=['power', 'toughness'],
                         constant_value=constant_value)

class SetFixedPower(K):
    '''\
        For use by Sublayer 7a Effect Components which define power to a fixed apriori value; or,
        Sublayer 7b Effect Components which set base power to a fixed apriori value.
    '''
    def __init__(self, constant_value):
        super().__init__(reference_attributes=['power'], constant_value=constant_value)


class SetFixedToughness(K):
    '''\
        For use by Sublayer 7a Effect Components which define toughness to a fixed apriori value; or,
        Sublayer 7b Effect Components which set base toughness to a fixed apriori value.
    '''
    def __init__(self, constant_value):
        super().__init__(reference_attributes=['toughness'], constant_value=constant_value)


########################################
# Switching power and toughness deltas #
########################################
class AssignSwitchedPowerDelta(ReflexiveDelta):
    '''\
        As a ReflexiveDelta, self.compute(ref_obj) will assign ref_obj
        to be the attribute value of self.arbitrary_function.ref_obj
        before returning the compute() method of self.arbitrary_function.
        With an arbitrary_function that is a SimpleAttributeReport,
        this means that self.compute(ref_obj) is essentially synonymous
        with: getattr(ref_obj, SAR.ref_attr).
        In this way, AssignSwitchedPowerDelta.compute(ref_obj) will end
        up doing:
            ref_obj.switched_power = getattr(ref_obj, 'toughness')

    '''
    def __init__(self):
        super().__init__(reference_attributes=['switched_power'],
                         arbitrary_function=SAR(None, 'toughness'))


class AssignSwitchedToughnessDelta(ReflexiveDelta):
    '''\
        Given a reference_object, accomplish the following:
            ref_obj.switched_toughness = getattr(reference_object, 'power')
    '''
    def __init__(self):
        super().__init__(reference_attributes=['switched_toughness'],
                         arbitrary_function=SAR(None, 'power'))

class SwitchPower(ReflexiveDelta):
    '''\
        Requires that the EffectComponent containing an instance of this
        Delta must also have an instance of AssignSwitchedPowerDelta earlier
        in its list of Deltas to do the work of figuring out what the correct value is.

        Given a reference_object, accomplish the following:
            ref_obj.power = ref_obj.switched_power
    '''
    def __init__(self):
        super().__init__(reference_attributes=['power'],
                         arbitrary_function=SAR(None, 'switched_power'))


class SwitchToughness(ReflexiveDelta):
    '''\
        Requires that the EffectComponent containing an instance of this Delta
        must also have an instance of AssignSwitchedToughnessDelta earlier in
        its list of Deltas to do the work of figuring out what the correct value is.

        Given a reference_object, accomplish the following:
            ref_obj.toughness = ref_obj.switched_toughness
    '''
    def __init__(self):
        super().__init__(reference_attributes=['toughness'],
                         arbitrary_function=SAR(None, 'switched_toughness'))


def switch_power_and_toughness_delta_factory():
    '''\
        Auxillary function ensuring that the sequential logic of these deltas
        is respected.
    '''
    return [AssignSwitchedPowerDelta(),
            AssignSwitchedToughnessDelta(),
            SwitchPower(),
            SwitchToughness()
    ]


####### Losing All Abilities ############
class LoseAllAbilities(K):
    '''\
        type(Modifiable.abilities) == list
        Losing all abilities is equivalent to assigning an empty list
        to the attribute value of the abilities attribute.
        This is a fixed apriori constant value; therefore, this is a subclass
        of K (aka a constant delta).
    '''
    def __init__(self):
        super().__init__(reference_attributes=['abilities'],
                         constant_value=list([]))


class LoseNonGrantedAbilities(ReflexiveDelta):
    '''\
        For use by effects components which set the land types of an object to a specified
        set, and therefore cause the object to lose all of the abilities generated from its
        rules-text, including intrinsic mana abilities, and abilities granted by copiable effects,
        but NOT abilities granted by non-copiable effects.
    '''
    def __init__(self):
        super().__init__(reference_attributes=['abilities'],
                         arbitrary_function=RulesTextAndCopiableEffectAbilityRemover())



####### Losing All Card Types ##########
class LoseAllCardTypes(K):
    '''\
        type(Modifiable.card_types) == set
        Losing all card_types is equivalent to assigning an empty set to the attribute
        value of the card_types attribute. This is a fixed apriori constant value; therefore,
        this is a subclass of K (aka a constant delta).
    '''
    def __init__(self):
        super().__init__(reference_attributes=['card_types'],
                         constant_value=set([]))



####### Losing All Creature Types ######
class LoseAllSubtypes(K):
    '''\
        type(Modifiable.subtypes) == set
        Losing all subtypes is equivalent to assigning an empty set to the attribute value of
        the subtypes attribute. This is a fixed apriori constant value; therefore, this is a
        subclass of K (aka a constant delta).
        # NOTE #
        This might need to be extended to allow differentiating between the subsets of subtypes
        which belong to one card_type and not to another.
    '''
    def __init__(self):
        super().__init__(reference_attributes=['subtypes'],
                         constant_value=set([]))

####### Losing All Colors #######
class LoseAllColors(K):
    '''\
        type(Modifiable.color) == set
        See above.
    '''
    def __init__(self):
        super().__init__(reference_attributes=['color'], constant_value=set([]))
