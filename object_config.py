from contfx_config import *


#######################################
# Setting Up Minimal Player Instances #
#######################################
p0 = ExpandedPlayerObject(player_idx=0)
p1 = ExpandedPlayerObject(player_idx=1)

p0.repr_string = "Player 0"
p1.repr_string = "Player 1"

GAME.list_of_player_objects = [p0, p1]
GAME.active_idx = 0
GAME.current_player = p0

GAME.list_of_game_objects = list([])
GAME.list_of_immaterial_objects = list([])

ZH.sync_zones_from_zh_to_players(p0, p1)


########################
# Testing Layer System #
########################
class ColossusHammer(Piece):
    def __init__(self, controller):
        super().__init__(impl_name="Colossus Hammer",
                         mana_cost="{1}",
                         color=set([]),
                         card_types=set(["artifact"]),
                         subtypes=set(["equipment"]),
                         abilities=[ColossusHammerStaticAbility(self)],
                         controller=controller)
        self.object_types = set(['card', 'permanent'])


class RuneOfFlight(Piece):
    # NOTE # Missing the triggered ability for the time being.
    def __init__(self, controller):
        super().__init__(impl_name="Rune of Flight",
                         mana_cost="{1}{U}",
                         color=set(["blue"]),
                         card_types=set(["enchantment"]),
                         subtypes=set(["aura", "rune"]),
                         abilities=[
                             RuneOfFlightPermanentIsCreatureStaticAbility(self),
                             RuneOfFlightPermanentIsEquipmentStaticAbility(self)
                         ],
                         controller=controller)
        self.object_types = set(["card", "permanent"])


class Opalescence(Piece):
    def __init__(self, controller):
        super().__init__(impl_name="Opalescence",
                         mana_cost="{2}{W}{W}",
                         color=set(["white"]),
                         card_types=set(["enchantment"]),
                         abilities=[OpalescenceStaticAbility(self)],
                         controller=controller)
        self.object_types = set(["card", "permanent"])


class Humility(Piece):
    def __init__(self, controller):
        super().__init__(impl_name="Humility",
                         mana_cost="{2}{W}{W}",
                         color=set(["white"]),
                         card_types=set(["enchantment"]),
                         abilities=[HumilityStaticAbility(self)],
                         controller=controller)
        self.object_types = set(["card", "permanent"])


class LostOrderOfJarkeld(Piece):
    def __init__(self, controller):
        super().__init__(impl_name="Lost Order of Jarkeld",
                         mana_cost="{2}{W}{W}",
                         color=set(["white"]),
                         card_types=set(["creature"]),
                         subtypes=set(["human", "knight"]),
                         abilities=[LostOrderOfJarkeldStaticAbility(self)],
                         power=1,
                         toughness=1,
                         controller=controller)
        self.object_types = set(["card", "permanent"])
        self.chosen_opponent = None


class QuicksilverGargantuan(Piece):
    def __init__(self, controller):
        super().__init__(impl_name="Quicksilver Gargantuan",
                         mana_cost="{5}{U}{U}",
                         color=set(["blue"]),
                         card_types=set(["creature"]),
                         subtypes=set(["shapeshifter"]),
                         abilities=[QuicksilverGargantuanStaticAbility(self)],
                         power=7,
                         toughness=7,
                         controller=controller)
        self.object_types = set(["card", "permanent"])
        self.copy_source_object = None


class MasterOfEtherium(Piece):
    def __init__(self, controller):
        super().__init__(impl_name="Master of Etherium",
                         mana_cost="{2}{U}",
                         color=set(["blue"]),
                         card_types=set(["artifact", "creature"]),
                         subtypes=set(["vedalken", "wizard"]),
                         abilities=[
                             MasterOfEtheriumCDA(self),
                             MasterOfEtheriumStaticAbility(self)
                         ],
                         power=0,
                         toughness=0,
                         controller=controller)
        self.object_types = set(["card", "permanent"])


class AlphaMyr(Piece):
    def __init__(self, controller):
        super().__init__(impl_name="Alpha Myr",
                         mana_cost="{2}",
                         color=set([]),
                         card_types=set(["artifact", "creature"]),
                         subtypes=set(["myr"]),
                         power=2,
                         toughness=1,
                         controller=controller)
        self.object_types = set(["card", "permanent"])


class Clone(Piece):
    def __init__(self, controller):
        super().__init__(impl_name="Clone",
                        mana_cost="{3}{U}",
                        color=set(["blue"]),
                        card_types=set(["creature"]),
                        subtypes=set(["shapeshifter"]),
                        abilities=[CloneStaticAbility(self)],
                        power=0,
                        toughness=0,
                        controller=controller)
        self.object_types = set(["card", "permanent"])
        self.copy_source_object = None


class CopyArtifact(Piece):
    def __init__(self, controller):
        super().__init__(impl_name="Copy Artifact",
                         mana_cost="{1}{U}",
                         color=set(["blue"]),
                         card_types=set(["enchantment"]),
                         abilities=[CopyArtifactStaticAbility(self)],
                         controller=controller)
        self.object_types = set(['card', 'permanent'])
        self.copy_source_object = None


class TestArtifact(Piece):
    def __init__(self, controller):
        super().__init__(impl_name="Test Artifact",
                         mana_cost="{1}",
                         color=set([]),
                         card_types=set(["artifact"]),
                         controller=controller)
        self.object_types = set(["card", "permanent"])


class TestCreature(Piece):
    '''\
        Vehicle for an example continuous effect generated by a static ability which
        modifies the type characteristic to test dependency solving in test1.py, with
        an ability which reads,
            All lands are artifacts in addition to their other types.
    '''
    def __init__(self, controller):
        super().__init__(impl_name="Test Creature",
                         mana_cost="{0}",
                         color=set([]),
                         card_types=set(["creature"]),
                         subtypes=set(["test"]),
                         abilities=[LandsAlsoArtifactsStaticAbility(self)],
                         power=10,
                         toughness=10,
                         controller=controller)
        self.object_types = set(["card", "permanent"])


class TestCreatureII(Piece):
    '''\
        Vehicle for an example continuous effect generated by a static ability which
        modifies the type characteristic to test dependency solving in test1.py, with
        an ability which reads,
            All artifacts are enchantments in addition to their other types.
    '''
    def __init__(self, controller):
        super().__init__(impl_name="Test Creature II",
                         mana_cost="{0}",
                         color=set([]),
                         card_types=set(["creature"]),
                         subtypes=set(["test"]),
                         abilities=[ArtifactsAlsoEnchantmentsStaticAbility(self)],
                         power=5,
                         toughness=5,
                         controller=controller)
        self.object_types = set(["card", "permanent"])


class TestLand(Piece):
    def __init__(self, controller):
        super().__init__(impl_name="Test Land",
                         mana_cost="",
                         color=set([]),
                         card_types=set(["land"]),
                         subtypes=set(["test"]),
                         supertypes=set(["basic"]),
                         controller=controller)
        self.object_types = set(["card", "permanent"])


class CardZero(Piece):
    def __init__(self, controller):
        super().__init__(impl_name="card0",
                         color=set(['red']),
                         card_types=set(['artifact', 'land']),
                         controller=controller)
        self.object_types = set(["permanent", "card"])


class CardOne(Piece):
    def __init__(self, controller):
        super().__init__(impl_name="card1",
                         color=set(['blue']),
                         card_types=set(['creature', 'artifact']),
                         power=1,
                         toughness=1,
                         controller=controller)
        self.object_types = set(["permanent", "card"])


class CardTwo(Piece):
    def __init__(self, controller):
        super().__init__(impl_name="card2",
                         color=set(['white']),
                         card_types=set(['artifact', 'planeswalker']),
                         supertypes=set(['legendary']),
                         loyalty=1,
                         controller=controller)
        self.object_types = set(["permanent", "card"])


class Alela(Piece):
    '''\
        Ignores triggered ability.
            Whenever you cast an artifact or enchantment spell:
                create a 1/1 blue Faerie creature token with flying.
    '''
    def __init__(self, controller):
        super().__init__(impl_name="Alela, Artful Provocateur",
                         mana_cost="{1}{W}{U}{B}",
                         color=set(['white', 'blue', 'black']),
                         card_types=set(['creature']),
                         subtypes=set(["faerie", "warlock"]),
                         supertypes=set(['legendary']),
                         abilities=[KWAFlying(self),
                                    KWADeathtouch(self),
                                    KWALifelink(self),
                                    AlelaStaticAbility(self)
                         ],
                         power=2,
                         toughness=3,
                         controller=controller)
        self.object_types = set(["permanent", "card"])


class Sephara(Piece):
    def __init__(self, controller):
        super().__init__(impl_name="Sephara, Sky's Blade",
                         mana_cost="{4}{W}{W}{W}",
                         color=set(["white"]),
                         card_types=set(["creature"]),
                         subtypes=set(["angel"]),
                         supertypes=set(["legendary"]),
                         abilities=[KWAFlying(self),
                                    KWALifelink(self),
                                    SepharaStaticAbility(self)
                         ],
                         power=7,
                         toughness=7,
                         controller=controller)
        self.object_types = set(["permanent", "card"])


class BranchsnapLorian(Piece):
    def __init__(self, controller):
        super().__init__(impl_name="Branchsnap Lorian",
                         mana_cost="{1}{G}{G}",
                         color=set(["green"]),
                         card_types=set(["creature"]),
                         subtypes=set(["beast"]),
                         abilities=[KWATrample(self),
                                    "Morph {G}"
                         ],
                         power=4,
                         toughness=1,
                         controller=controller)
        self.object_types = set(["card", "permanent"])


class AinokTracker(Piece):
    def __init__(self, controller):
        super().__init__(impl_name="Ainok Tracker",
                         mana_cost="{5}{R}",
                         color=set(["red"]),
                         card_types=set(["creature"]),
                         subtypes=set(["hound", "scout"]),
                         abilities=[KWAFirstStrike(self), "Morph {4}{R}"],
                         power=3,
                         toughness=3,
                         controller=controller)
        self.object_types = set(["card", "permanent"])


class Anger(Piece):
    def __init__(self, controller):
        super().__init__(impl_name="Anger",
                         mana_cost="{3}{R}",
                         color=set(["red"]),
                         card_types=set(["creature"]),
                         subtypes=set(["incarnation"]),
                         abilities=[
                             KWAHaste(self),
                             AngerStaticAbility(self)
                         ],
                         power=2,
                         toughness=2,
                         controller=controller)
        self.object_types = set(['card', 'permanent'])


class AngryMob(Piece):
    def __init__(self, controller):
        super().__init__(impl_name="Angry Mob",
                         mana_cost="{2}{W}{W}",
                         color=set(["white"]),
                         card_types=set(["creature"]),
                         subtypes=set(["human"]),
                         abilities=[
                             AngryMobStaticAbility(self)
                         ],
                         power=2,
                         toughness=2,
                         controller=controller)
        self.object_types = set(['card', 'permanent'])


class ArchetypeOfFinality(Piece):
    def __init__(self, controller):
        super().__init__(impl_name="Archetype of Finality",
                         mana_cost="{4}{B}{B}",
                         color=set(["black"]),
                         card_types=set(["enchantment", "creature"]),
                         subtypes=set(["gorgon"]),
                         abilities=[
                             ArchetypeOfFinalityStaticAbility(self),
                             ArchetypeOfFinalityProhibitionStaticAbility(self)
                         ],
                         power=2,
                         toughness=3,
                         controller=controller)
        self.object_types = set(["card", "permanent"])


class GorMuldrakAmphinologist(Piece):
    '''\
        # NOTE #
        # Missing a triggered ability.
    '''
    def __init__(self, controller):
        super().__init__(impl_name="Gor Muldrak, Amphinologist",
                         mana_cost="{1}{G}{U}",
                         color=set(["green", "blue"]),
                         card_types=set(["creature"]),
                         subtypes=set(["human", "scout"]),
                         supertypes=set(["legendary"]),
                         abilities=[
                             GorMuldrakAmphinologistAffectPermanentStaticAbility(self),
                             GorMuldrakAmphinologistAffectPlayerStaticAbility(self)
                         ],
                         power=3,
                         toughness=2,
                         controller=controller)
        self.object_types = set(["card", "permanent"])



#class Mountain(LandPiece):
#    def __init__(self, controller):
#        super().__init__(impl_name="Mountain",
#                         mana_cost="",
#                         color=set([]),
#                         card_types=set(["land"]),
#                         subtypes=set(["mountain"]),
#                         supertypes=set(["basic"]),
#                         abilities=[MountainManaAbility()],
#                         controller=controller)
#        self.object_types = set(['card', 'permanent'])


class Mountain(Piece):
    def __init__(self, controller):
        super().__init__(impl_name="Mountain",
                         mana_cost="",
                         color=set([]),
                         card_types=set(["land"]),
                         subtypes=set(["mountain"]),
                         supertypes=set(["basic"]),
                         abilities=[MountainManaAbility()],
                         controller=controller)
        self.object_types = set(['card', 'permanent'])


class Swamp(Piece):
    def __init__(self, controller):
        super().__init__(impl_name="Swamp",
                         mana_cost="",
                         color=set([]),
                         card_types=set(["land"]),
                         subtypes=set(["swamp"]),
                         supertypes=set(["basic"]),
                         abilities=[SwampManaAbility()],
                         controller=controller)
        self.object_types = set(['card', 'permanent'])


class UrborgTombOfYawgmoth(Piece):
    def __init__(self, controller):
        super().__init__(impl_name="Urborg, Tomb of Yawgmoth",
                         mana_cost="",
                         color=set([]),
                         card_types=set(["land"]),
                         supertypes=set(["legendary"]),
                         abilities=[UrborgTombOfYawgmothStaticAbility(self)],
                         controller=controller)
        self.object_types = set(["card", "permanent"])


class BloodMoon(Piece):
    def __init__(self, controller):
        super().__init__(impl_name="Blood Moon",
                         mana_cost="{2}{R}",
                         color=set(["red"]),
                         card_types=set(["enchantment"]),
                         abilities=[BloodMoonStaticAbility(self)],
                         controller=controller)
        self.object_types = set(["card", "permanent"])


class Frogify(Piece):
    def __init__(self, controller):
        super().__init__(impl_name="Frogify",
                         mana_cost="{1}{U}",
                         color=set(["blue"]),
                         card_types=set(["enchantment"]),
                         subtypes=set(["aura"]),
                         abilities=[FrogifyStaticAbility(self)],
                         controller=controller)
        self.object_types = set(["permanent", "card"])


class Clutches(Piece):
    '''\
        a.k.a. In Bolas's Clutches
    '''
    def __init__(self, controller):
        super().__init__(impl_name="In Bolas's Clutches",
                         mana_cost="{4}{U}{U}",
                         color=set(["blue"]),
                         card_types=set(["enchantment"]),
                         subtypes=set(["aura"]),
                         abilities=[ClutchesStaticAbility(self)],
                         controller=controller)
        self.object_types = set(["permanent", "card"])


class TruePolymorph(Piece):
    def __init__(self, controller):
        super().__init__(impl_name="True Polymorph",
                         mana_cost="{4}{U}{U}",
                         color=set(["blue"]),
                         card_types=set(["instant"]),
                         abilities=[TruePolymorphSpellAbility(self)],
                         controller=controller)
        self.object_types = set(["spell", "card"])
        self.copy_source_object = None


class Infuriate(Piece):
    def __init__(self, controller):
        super().__init__(impl_name="Infuriate",
                         mana_cost="{R}",
                         color=set(['red']),
                         card_types=set(['instant']),
                         abilities=[InfuriateSpellAbility(self)],
                         controller=controller)
        self.object_types = set(['spell', 'card'])
        self.target_data = list([])


class Overcome(Piece):
    def __init__(self, controller):
        super().__init__(impl_name="Overcome",
                         mana_cost="{3}{G}{G}",
                         color=set(["green"]),
                         card_types=set(["sorcery"]),
                         abilities=[OvercomeSpellAbility(self)],
                         controller=controller)
        self.object_types = set(["spell", "card"])


class HeroicIntervention(Piece):
    def __init__(self, controller):
        super().__init__(impl_name="Heroic Intervention",
                         mana_cost="{1}{G}",
                         color=set(["green"]),
                         card_types=set(["instant"]),
                         abilities=[HeroicInterventionSpellAbility(self)],
                         controller=controller)
        self.object_types = set(['spell', 'card'])


class TestInstant(Piece):
    '''\
        Vehicle for the continuous effect generated by the resolution of a
        spell or ability given as an example after Rule 613.6, which reads:
        "All noncreature artifacts become 2/2 artifact creatures until end of turn."
    '''
    def __init__(self, controller):
        super().__init__(impl_name="Test Instant",
                         mana_cost="{0}",
                         color=set([]),
                         card_types=set(["instant"]),
                         abilities=[example_613_6(self)],
                         controller=controller)
        self.object_types = set(["spell", "card"])


class GildedLight(Piece):
    '''\
        # NOTE #
        # Missing Cycling {2} activated ability.
    '''
    def __init__(self, controller):
        super().__init__(impl_name="Gilded Light",
                         mana_cost="{1}{W}",
                         color=set(["white"]),
                         card_types=set(["instant"]),
                         abilities=[GildedLightSpellAbility(self)],
                         controller=controller)
        self.object_types = set(["spell", "card"])


###################################
# Auxillary Functions For Testing #
###################################
def resolve_effects(object):
    '''\
        Simulate the generation of continuous effects due to following instructions
        during the resolution of spells or abilities on the Stack.
    '''
    if isinstance(object, Modifiable):
        if ("spell" in object.object_types):
            if (object.card_types < set(["instant", "sorcery"])):
                for ability in object.abilities:
                    if isinstance(ability, ResolutionContinuousEffectGenerator):
                        effect = ability.generate_effect()
                        GAME.list_of_immaterial_objects.append(effect)
