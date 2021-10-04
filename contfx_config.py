from layers import *

# Support Testing Various Continuous Effects and their Generators #

##########################
# Effects via Resolution #
#######################################################################
class GildedLightSpellAbility(ResContFXGen):
    '''\
        You gain shroud until end of turn.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[],
                         phi_factories=[],
                         player_phi_factories=[
                             create_you_player_predicate
                         ],
                         components=[
                             FXC(layer="8",
                                 external_deltas=[
                                     AddKeywordAbilities(kwa_types_to_add=[KWAShroud])
                                 ])
                         ],
                         duration=UntilEndOfTurnDuration())
        self.debug_string = "gilded_light_spell_ability"


class OvercomeSpellAbility(ResContFXGen):
    '''\
        Creatures you control get +2/+2 gain trample until end of turn.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[
                             FIND.creature,
                             FIND.zone_battlefield
                         ],
                         phi_factories=[
                            create_same_controller_predicate
                         ],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="6",
                                 external_deltas=[
                                     AddKeywordAbilities(kwa_types_to_add=[KWATrample])
                             ]),
                             FXC(layer="7c",
                                 external_deltas=[
                                     PowerDelta(amount=2, gain=True),
                                     ToughnessDelta(amount=2, gain=True)
                             ])
                         ],
                         duration=UntilEndOfTurnDuration())
        self.debug_string = "overcome_spell_ability"


class InfuriateSpellAbility(ResContFXGen):
    '''\
        Target creature gets +3/+2 until end of turn.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[],
                         phi_factories=[create_target_data_predicate],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="7c",
                                 external_deltas=[
                                     PowerDelta(amount=3, gain=True),
                                     ToughnessDelta(amount=2, gain=True)
                             ])
                         ],
                         duration=UntilEndOfTurnDuration())
        self.debug_string = "infuriate_spell_ability"


class TruePolymorphSpellAbility(ResContFXGen):
    '''\
        Target artifact or creature becomes a copy of another target artifact or creature.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[],
                         phi_factories=[create_target_data_predicate],
                         player_phi_factories=[],
                         components=[
                             CopyEffectComponent()
                         ],
                         duration=None)
        self.debug_string = "true_polymorph_spell_ability"


class HeroicInterventionSpellAbility(ResContFXGen):
    '''\
        Permanents you control gain hexproof and indestructible until end of turn.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[FIND.zone_battlefield],
                         phi_factories=[create_same_controller_predicate],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="6",
                                 external_deltas=[
                                     AddKeywordAbilities(kwa_types_to_add=[
                                                             KWAHexproof,
                                                             KWAIndestructible
                                                         ])
                             ])
                         ],
                         duration=UntilEndOfTurnDuration())
        self.debug_string = "heroic_intervention_spell_ability"


##########################
# Morph Effect Generator #
##########################
class MorphEffectGenerator(ResContFXGen):
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[],
                         phi_factories=[create_host_object_predicate],
                         player_phi_factories=[],
                         components=[
                             FaceDownEffectComponent()
                         ],
                         duration=None)
        self.debug_string = "morph_effect_generator"



###################################################################################################
# EFFECTS #
###################################################################################################
# card1's power and toughness are equal to 2. #
###############################################
class pt7aStaticAbility(StaticAbility):
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[],
                         phi_factories=[create_host_object_predicate],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="7a",
                                 external_deltas=[SetFixedPT(constant_value=2)],
                                 delta_factories=[],
                                 is_cda=True)
                         ],
                         active_zone_types=[None])
        self.debug_string = "pt7a"


class MasterOfEtheriumCDA(StaticAbility):
    '''\
        ~'s power and toughness are each equal to the number of artifacts you control.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[],
                         phi_factories=[create_host_object_predicate],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="7a",
                                 external_deltas=[],
                                 delta_factories=[
                                     self.statistic
                                 ],
                                 is_cda=True)
                         ],
                         active_zone_types=[None])
        self.debug_string = "moe_cda"

    def statistic(self, effect_component):
        '''\
            Set power and toughness to the number of artifacts controlled by
            the controller of Master of Etherium.
        '''
        selection_to_use = Selection(CONJ(FIND.zone_battlefield,
                                          FIND.artifact,
                                          create_same_controller_predicate(effect_component)))
        return Delta(reference_attributes=['power', 'toughness'],
                     arbitrary_function=ObjectCounter(selection=selection_to_use))


class MasterOfEtheriumStaticAbility(StaticAbility):
    '''\
        Other artifact creatures you control get +1/+1.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[FIND.artifact, FIND.creature, FIND.zone_battlefield],
                         phi_factories=[
                             create_same_controller_predicate,
                             create_exclude_self_predicate
                         ],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="7c",
                                 external_deltas=[
                                     PowerDelta(amount=1, gain=True),
                                     ToughnessDelta(amount=1, gain=True)
                                 ])
                         ])
        self.debug_string = "moe_static"


# Base Power and/or Base Toughness Setting Effect (Sublayer 7B)
# Example of a Base Power Setting Effect
# " Artifact creatures have base power and toughness 3/5."
FIND @ ['artifact', 'creature']

class pt7bStaticAbility(StaticAbility):
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[FIND.artifact_creature, FIND.zone_battlefield],
                         phi_factories=[],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="7b",
                                 external_deltas=[
                                     SetFixedPower(constant_value=3),
                                     SetFixedToughness(constant_value=5)
                                 ])
                         ])
        self.debug_string = "pt7b"



# Effect with multiple parts in different layers, where the set of affected
# objects is determined at the time the first component is applied, and persists across
# application of the remaining parts in later layers---even when those objects no longer
# meet the original criteria.
# 
# 613.6 If an effect should be applied in different layers and/or sublayers, the parts of
# the effect each apply in their appropriate ones. If an effect starts to apply in one layer
# and/or sublayer, it will continue to be applied to the same set of objects in each other
# applicable layer and/or sublayer, even if the ability generating the effect is removed
# during this process.
#
# Example
# An effect that reads, "All noncreature artifacts become 2/2 artifact creatures until
# end of turn" is both a type-changing effect and a power-and-toughness-setting effect.
# The type-changing effect is applied to all noncreature artifacts in layer 4 and the
# power-and-toughness-setting effect is applied to those same permanents in layer 7b, 
# even though those permanents aren't noncreature artifacts by then.

# NOTE #
# The atomic attributes get sorted alphabetically to determine the conjunction attribute
# so it is useful to simply provide them in alphabetical order to keep things consistent
# while reading through the code.
FIND @ ['artifact', 'noncreature']

class example_613_6(ResContFXGen):
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[FIND.artifact_noncreature, FIND.zone_battlefield],
                         phi_factories=[],
                         player_phi_factories=[],
                         components=[
                             FXC(layer='4',
                                 external_deltas=[AddCreatureCardType()]),
                             FXC(layer='7b',
                                 external_deltas=[SetFixedPT(constant_value=2)])
                         ],
                         duration=UntilEndOfTurnDuration())
        self.debug_string = "example_613_6"


class MannichiActivatedAbilityEntailment(ResContFXGen):
    '''\
        Switch each creature's power and toughness until end of turn.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[FIND.creature, FIND.zone_battlefield],
                         phi_factories=[],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="7d",
                                 external_deltas=switch_power_and_toughness_delta_factory())
                         ],
                         duration=UntilEndOfTurnDuration())
        self.debug_string = "pt7d"


class LandsAlsoArtifactsStaticAbility(StaticAbility):
    '''\
        All lands are artifacts in addition to their other types.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[FIND.land, FIND.zone_battlefield],
                         phi_factories=[],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="4",
                                 external_deltas=[AddArtifactCardType()])
                         ])
        self.debug_string = "lands_also_artifacts"



class ArtifactsAlsoCreaturesStaticAbility(StaticAbility):
    '''\
        All artifacts are creatures in addition to their other types.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[FIND.artifact, FIND.zone_battlefield],
                         phi_factories=[],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="4",
                                 external_deltas=[AddCreatureCardType()])
                         ])
        self.debug_string = "artifacts_also_creatures"


class ArtifactsAlsoEnchantmentsStaticAbility(StaticAbility):
    '''\
        All artifacts are enchantments in addition to their other types.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[FIND.artifact, FIND.zone_battlefield],
                         phi_factories=[],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="4",
                                 external_deltas=[AddEnchantmentCardType()])
                         ])
        self.debug_string="artifacts_also_enchantments"


class GreenArtifactsStaticAbility(StaticAbility):
    '''\
        All artifacts are green.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[FIND.artifact, FIND.zone_battlefield],
                         phi_factories=[],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="5",
                                 external_deltas=[K(reference_attributes=['color'],
                                                    constant_value=set(['green']))])
                         ])
        self.debug_string = "green_artifacts"



########
# Example of a Static Ability which generates a Continuous Effect with a Selection whose
# predicate contains a dynamically resolved reference to the host object of the ability itself.
#
# Example: Frogify
#          "Enchanted creature loses all abilities and is a blue Frog creature with
#           base power and toughness 1/1 (It loses all other card types and creature types).

class FrogifyStaticAbility(StaticAbility):
    '''\
        Enchanted creature loses all abilities and is a blue Frog creature with base power
        and toughness 1/1 (It loses all other card types and creature types).
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[FIND.zone_battlefield],
                         phi_factories=[create_object_enchanted_by_host_predicate],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="4",
                                 external_deltas=[
                                     LoseAllCardTypes(),
                                     LoseAllSubtypes(),
                                     AddCreatureCardType(),
                                     AddSubtypes(set_of_subtypes_to_add=set(['frog']))
                                 ]),
                             FXC(layer='5',
                                 external_deltas=[
                                     K(reference_attributes=['color'],
                                       constant_value=set(['blue']))
                                 ]),
                             FXC(layer='6',
                                 external_deltas=[
                                     LoseAllAbilities()
                                 ]),
                             FXC(layer='7b',
                                 external_deltas=[
                                     SetFixedPT(constant_value=1)
                                 ])
                         ])
        self.debug_string = "frogify_static"


######################
# Changeling Example #
######################
class ChangelingStaticAbility(StaticAbility):
    '''\
        702.73a
        Changeling is a characteristic-defining ability.
        "Changeling" means "This object is every creature type."
        This ability works everywhere, even outside the game.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[],
                         phi_factories=[create_host_object_predicate],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="4",
                                 external_deltas=[
                                     AddAllCreatureTypes()
                                 ],
                                 delta_factories=[],
                                 is_cda=True)
                         ],
                         active_zone_types=[None])
        self.debug_string = "changeling_static"


################
# Copy Effects #
#################################################
# Static Ability Generating Copy Effect Example #
#################################################
class CloneStaticAbility(StaticAbility):
    '''\
        You may have Clone enter the battlefield as a copy of any creature on the battlefield.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[],
                         phi_factories=[create_host_object_predicate],
                         player_phi_factories=[],
                         components=[
                            CopyEffectComponent()
                         ])
        self.debug_string = "clone_static"


#############################################################################################
# Static Ability Generating Copy Effect With Additional Characteristic Modification Example #
#############################################################################################
class CopyArtifactStaticAbility(StaticAbility):
    '''\
        You may have Copy Artifact enter the battlefield as a copy of any artifact on the
        battlefield, except it's an enchantment in addition to its other types.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[],
                         phi_factories=[create_host_object_predicate],
                         player_phi_factories=[],
                         components=[
                             CopyEffectComponent(modifications=[
                                                     AddEnchantmentCardType()
                                                 ])
                         ])
        self.debug_string = "copy_artifact_static"


#########################################################################################
# Static Ability Generating Copy Effect With Exception Retaining Original Value Example #
#########################################################################################
class QuicksilverGargantuanStaticAbility(StaticAbility):
    '''\
        You may have Quicksilver Gargantuan enter the battlefield as a copy of any creature
        on the battlefield, except it's 7/7.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[],
                         phi_factories=[create_host_object_predicate],
                         player_phi_factories=[],
                         components=[
                             CopyEffectComponent(modifications=[
                                                     SetFixedPT(constant_value=7)
                                                 ])
                         ])
        self.debug_string = "quicksilver_static"


######################################################################
# "As ... enters the battlefield" Generating Copiable Effect Example #
######################################################################
class LostOrderOfJarkeldStaticAbility(StaticAbility):
    '''\
        As Lost Order of Jarkeld enters the battlefield, choose an opponent.
        Lost Order of Jarkeld's power and toughness are each equal to 1 plus the number
        of creatures the chosen player controls.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[],
                         phi_factories=[create_host_object_predicate],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="1a",
                                 external_deltas=[],
                                 delta_factories=[
                                     self.statistic
                                 ])
                         ])
        self.debug_string = "looj_static"

    def statistic(self, effect_component):
        '''\
            Set power and toughness to 1 + the number of creatures controlled by the opponent chosen
            by the controller of Lost Order of Jarkeld as it entered the battlefield.
        '''
        controller_predicate = isP(ref_attr="controller",
                                   ref_val=link_to_host_object_attribute_value(effect_component,
                                                                               'chosen_opponent'))
        selection_to_use = Selection(CONJ(FIND.zone_battlefield,
                                          FIND.creature,
                                          controller_predicate))
        return Delta(reference_attributes=["power", "toughness"],
                     arbitrary_function=Lambda(ADD, 1, ObjectCounter(selection=selection_to_use)))



class ArchetypeOfFinalityStaticAbility(StaticAbility):
    '''\
        Creatures you control have deathtouch.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[FIND.zone_battlefield, FIND.creature],
                         phi_factories=[create_same_controller_predicate],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="6",
                                 external_deltas=[
                                     AddKeywordAbilities(kwa_types_to_add=[KWADeathtouch])
                                 ])
                         ])
        self.debug_string = "archetype_of_finality_static"


class ArchetypeOfFinalityProhibitionStaticAbility(StaticAbility):
    '''\
        Creatures your opponents control lose deathtouch and can't have or gain deathtouch.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[FIND.zone_battlefield, FIND.creature],
                         phi_factories=[create_different_controller_predicate],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="6",
                                 external_deltas=[
                                     LoseKeywordAbilities(kwa_types_to_lose=[KWADeathtouch]),
                                     BanKeywordAbility(prohibition_to_add=KWAProhibition(prohibited_kwa_type=KWADeathtouch))
                                 ])
                         ])
        self.debug_string = "archetype_of_finality_prohibition_static"


class ClutchesStaticAbility(StaticAbility):
    '''\
        Enchant permanent.
        You control enchanted permanent.
        Enchanted permanent is legendary.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[],
                         phi_factories=[create_object_enchanted_by_host_predicate],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="2",
                                 external_deltas=[],
                                 delta_factories=[
                                     partial(create_host_object_imitation_delta,
                                             ['controller'],
                                             'controller')
                                 ]),
                             FXC(layer="4",
                                 external_deltas=[
                                     AddSupertypes(set_of_supertypes_to_add=set(['legendary']))
                                 ],
                                 delta_factories=[])
                         ])
        self.debug_string = "clutches_static"


class SepharaStaticAbility(StaticAbility):
    '''\
        Other creatures you control with flying gain indestructible.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[
                             FIND.creature,
                             HasKeywordAbility(keyword_ability_type=KWAFlying)
                         ],
                         phi_factories=[
                             create_same_controller_predicate,
                             create_exclude_self_predicate
                         ],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="6",
                                 external_deltas=[
                                     AddKeywordAbilities(kwa_types_to_add=[KWAIndestructible])
                                 ])
                         ])
        self.debug_string = "sephara_static"


class AlelaStaticAbility(StaticAbility):
    '''\
        Other creatures you control with flying get +1/+0.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[
                             FIND.creature,
                             HasKeywordAbility(keyword_ability_type=KWAFlying)
                         ],
                         phi_factories=[
                             create_same_controller_predicate,
                             create_exclude_self_predicate
                         ],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="7c",
                                 external_deltas=[
                                     PowerDelta(amount=1, gain=True),
                                     ToughnessDelta(amount=0, gain=True)
                                 ])
                         ])
        self.debug_string = "alela_static"


class HumilityStaticAbility(StaticAbility):
    '''\
        All creatures lose all abilities and have base power and toughness 1/1.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[FIND.zone_battlefield, FIND.creature],
                         phi_factories=[],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="6",
                                 external_deltas=[
                                     LoseAllAbilities()
                             ]),
                             FXC(layer="7b",
                                 external_deltas=[
                                     SetFixedPT(constant_value=1)
                             ])
                         ])
        self.debug_string = "humility_static"


class OpalescenceStaticAbility(StaticAbility):
    '''\
        Each other non-Aura enchantment is a creature in addition to its other types
        and has base power and base toughness each equal to its mana value.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[
                             FIND.zone_battlefield,
                             FIND.nonaura_enchantment
                         ],
                         phi_factories=[
                             create_exclude_self_predicate
                         ],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="4",
                                 external_deltas=[
                                     AddCreatureCardType()
                             ]),
                             FXC(layer="7b",
                                 external_deltas=[
                                     ReflexiveDelta(reference_attributes=['power', 'toughness'],
                                                    arbitrary_function=SAR(None, "mana_value"))
                             ])
                         ])
        self.debug_string = "opal_static"


class UrborgTombOfYawgmothStaticAbility(StaticAbility):
    '''\
        Each land is a Swamp in addition to its other types.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[
                             FIND.zone_battlefield,
                             FIND.land
                         ],
                         phi_factories=[],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="4",
                                 external_deltas=landtype_delta_factory(list_of_landtype_strings=["swamp"],
                                                                        in_addition=True))
                         ])
        self.debug_string = "urborg_static"


class BloodMoonStaticAbility(StaticAbility):
    '''\
        Nonbasic lands are Mountains.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[
                             FIND.zone_battlefield,
                             FIND.nonbasic_land
                         ],
                         phi_factories=[],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="4",
                                 external_deltas=landtype_delta_factory(list_of_landtype_strings=["mountain"],
                                                                        in_addition=False))
                         ])
        self.debug_string = "blood_moon_static"


class GorMuldrakAmphinologistAffectPlayerStaticAbility(StaticAbility):
    '''\
        You and permanents you control have protection from Salamanders
        |=> You have protection from Salamanders.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[],
                         phi_factories=[],
                         player_phi_factories=[
                             create_you_player_predicate
                         ],
                         components=[
                             FXC(layer="8",
                                 external_deltas=[
                                     AddKeywordAbilities(kwa_types_to_add=[KWAProtection])
                             ])
                         ])
        self.debug_string = "gor_muldrak_affect_player_static"


class GorMuldrakAmphinologistAffectPermanentStaticAbility(StaticAbility):
    '''\
        You and permanents you control have protection from Salamanders.
        |=> Permanents you control have protection from Salamanders.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[
                             FIND.zone_battlefield
                         ],
                         phi_factories=[
                             create_same_controller_predicate
                         ],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="6",
                                 external_deltas=[
                                     AddKeywordAbilities(kwa_types_to_add=[KWAProtection])
                             ])
                         ])
        self.debug_string = "gor_muldrak_affect_permanent_static"


###########
# TESTING #
###########
def add_target_to_object(target, object):
    '''\
        Convenience function for assigning a target the way it would be done
        during the process of putting a spell or ability on the Stack.
    '''
    if not(hasattr(object, 'target_data')):
        object.target_data = []
    target_temp_id = target.temp_id
    if not(target_temp_id in object.target_data):
        object.target_data.append(target_temp_id)


def snapshot():
    '''\
        Derive the apparent state by solving layer sort and applying the effect components
        in the correct order to the base state.
    '''
    FX_HANDLER.snapshot()


def set_to_string(set_of_strings):
    return " ".join(string.title() for string in set_of_strings)

def display(list_of_game_objects):
    print("___________")
    for go in list_of_game_objects:
        print(go.impl_name + "\t" + go.mana_cost)
        print("{} {} | {}".format(set_to_string(go.supertypes), set_to_string(go.card_types), set_to_string(go.subtypes)))
        print("{}\t{}".format(set_to_string(go.color), go.controller))
        print("{} / {}".format(go.power, go.toughness))
        print("{}\n".format(go.abilities))

def displayP(list_of_player_objects):
    print("___________")
    for po in list_of_player_objects:
        print("{}".format(po.__repr__()))
        print("{}".format(po.abilities))




###### Conditional Effects ######
class AdantoVanguardStaticAbility(StaticAbility):
    '''\
        As long as Adanto Vanguard is attacking, it gets +2/+0.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[],
                         phi_factories=[
                             create_host_object_predicate
                         ],
                         components=[
                             FXC(layer="7c",
                                 external_deltas=[
                                     PowerDelta(amount=2, gain=True),
                                     ToughnessDelta(amount=0, gain=True)
                             ])
                         ])
        self.debug_string = "adanto_vanguard_static"

    @property
    def antecedents_verified(self):
        return self.host_object.is_attacking


class AngerStaticAbility(StaticAbility):
    '''\
        As long as Anger is in your graveyard and you control a Mountain,
        creatures you control have haste.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[
                             FIND.zone_battlefield,
                             FIND.creature
                         ],
                         phi_factories=[
                             create_same_controller_predicate
                         ],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="6",
                                 external_deltas=[
                                     AddKeywordAbilities(kwa_types_to_add=[KWAHaste])
                             ])
                         ],
                         active_zone_types=[
                             Graveyard
                         ])
        self.debug_string = "anger_static"

    @property
    def antecedents_verified(self):
        anger_is_in_your_graveyard = self.host_object.current_zone is self.host_object.controller.zone_graveyard
        n_mountain = len(Selection(CONJ(FIND.zone_battlefield,
                                        FIND.mountain,
                                        create_same_controller_predicate(self))))

        return (anger_is_in_your_graveyard and n_mountain)


class AngryMobStaticAbility(StaticAbility):
    '''\
        As long as it's your turn, Angry Mob's power and toughness
        are each equal to 2 plus the number of Swamps your opponents control.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[],
                         phi_factories=[
                             create_host_object_predicate
                         ],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="7b",
                                 external_deltas=[],
                                 delta_factories=[
                                     self.statistic
                                 ])
                         ])
        self.debug_string = "angry_mob_static"

    def statistic(self, effect_component):
        '''\
            Set power and toughness to 2 + the number of Swamps controlled by the opponent of
            the controller of Angry Mob.
        '''
        return Delta(reference_attributes=["power", "toughness"],
                     arbitrary_function=Lambda(ADD, 2, ObjectCounter(Selection(CONJ(FIND.zone_battlefield,
                                                                                    FIND.swamp,
                                                                                    create_different_controller_predicate(effect_component))))))

    @property
    def antecedents_verified(self):
        return self.host_object.controller.player_idx == GAME.active_idx


class EquippedCreatureHasFlyingStaticAbility(StaticAbility):
    '''\
        Equipped creature has flying.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[],
                         phi_factories=[create_object_equipped_by_host_predicate],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="6",
                                 external_deltas=[
                                     AddKeywordAbilities(kwa_types_to_add=[KWAFlying])
                                 ])
                         ])
        self.debug_string = "rune_of_flight_granted_equipment_static"


class RuneOfFlightPermanentIsCreatureStaticAbility(StaticAbility):
    '''\
        As long as enchanted permanent is a creature, it has flying.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[],
                         phi_factories=[create_object_enchanted_by_host_predicate],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="6",
                                 external_deltas=[
                                     AddKeywordAbilities(kwa_types_to_add=[KWAFlying])
                                 ])
                         ])
        self.debug_string = "rune_of_flight_enchanting_creature_static"

    @property
    def antecedents_verified(self):
        return ("creature" in self.host_object.enchanted_object.card_types)


class RuneOfFlightPermanentIsEquipmentStaticAbility(StaticAbility):
    '''\
        As long as enchanted permanent is an Equipment, it has,
        "Equipped creature has flying."
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[],
                         phi_factories=[create_object_enchanted_by_host_predicate],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="6",
                                 external_deltas=[
                                     AddStaticAbility(EquippedCreatureHasFlyingStaticAbility)
                             ])
                         ])
        self.debug_string = "rune_of_flight_enchanting_eq_static"

    @property
    def antecedents_verified(self):
        return ("equipment" in self.host_object.enchanted_object.subtypes)


class ColossusHammerStaticAbility(StaticAbility):
    '''\
        Equipped creature gets +10/+10 and loses flying.
    '''
    def __init__(self, host_object=None):
        super().__init__(host_object=host_object,
                         external_predicates=[],
                         phi_factories=[],
                         player_phi_factories=[],
                         components=[
                             FXC(layer="6",
                                 external_deltas=[
                                     LoseKeywordAbilities(kwa_types_to_lose=[KWAFlying])
                             ]),
                             FXC(layer="7c",
                                 external_deltas=[
                                     PowerDelta(amount=10, gain=True),
                                     ToughnessDelta(amount=10, gain=True)
                             ])
                         ])
        self.debug_string = "colossus_hammer_static"


######################
# Implementing Morph #
######################
class Morphable:
    '''\
        Mixin for use with Modifiable to handle Morph and the Sublayer 1b Continuous
        Effect that gets generated by the object being played face down.
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.morph_effect_generator = MorphEffectGenerator(self)
        self.morph_effect_generator.debug_string = "Morph Effect Generator of {}".format(self)

    def turn_facedown(self):
        self.is_facedown = True
        morph_effect = self.morph_effect_generator.generate_effect()
        self.morph_effect = morph_effect
        GAME.list_of_immaterial_objects.append(morph_effect)

    def turn_faceup(self):
        self.is_facedown = False
        self.morph_effect.expired = True
        self.morph_effect = None


class Piece(Morphable, Modifiable):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Automatically add ourselves to the state's list of game objects on
        # instantiation.
        GAME.list_of_game_objects.append(self)
        # Automatically provide ourselves with a reference to the GAME instance as our environment.
        self.environment = GAME
        self.owner = self._controller
