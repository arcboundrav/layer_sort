from object_config import *

# Characteristic Defining Ability Setting Power and Toughness To a Statistic of the Game State
# "Master of Etherium's power and toughness are each equal to the number of artifacts you control."

# Static Ability Adding to Power and Toughness (Sublayer 7c) Excluding the Source Object
# "Other artifact creatures you control get +1/+1."

# Static Ability of an Aura Modifying the Controller of the Object it Enchants
# "You control enchanted permanent. Enchanted permanent is legendary."

master_of_etherium = MasterOfEtherium(controller=p0)

# Scenario 1a #
# Master of Etherium's owner does not control any artifacts.
display([master_of_etherium])

assert master_of_etherium.power == 0
assert master_of_etherium.toughness == 0
assert master_of_etherium.card_types == set(["creature", "artifact"])
assert master_of_etherium.supertypes == set([])

# Scenario 1b #
# Master of Etherium is alone on the battlefield. Its controller controls only one
# artifact; Master of Etherium itself.
# Master of Etherium's CDA sets its base power and toughness to 1.
# Master of Etherium's other static ability does not grant itself +1/+1.
ZH.zone_battlefield.add_object(master_of_etherium)

snapshot()
display([master_of_etherium])

assert master_of_etherium.power == 1
assert master_of_etherium.toughness == 1

# Scenario 1c #
# Alpha Myr, an artifact creature, is put onto the battlefield with the same controller
# as Master of Etherium. Alpha Myr is a 2/1 artifact creature by default.

alpha_myr = AlphaMyr(controller=p0)

assert "artifact" in alpha_myr.card_types
assert "creature" in alpha_myr.card_types
assert alpha_myr.power == 2
assert alpha_myr.toughness == 1
assert alpha_myr.controller == master_of_etherium.controller

ZH.zone_battlefield.add_object(alpha_myr)

snapshot()
display([master_of_etherium, alpha_myr])

assert master_of_etherium.power == 2
assert master_of_etherium.toughness == 2

assert alpha_myr.power == 3
assert alpha_myr.toughness == 2

# Scenario 1c Outcome #
# Master of Etherium's CDA sets its power and toughness to 2/2 because its controller
# controls two artifacts, and its other static ability does not give +1/+1 to itself.
# Alpha Myr's power and toughness becomes 3/2, because of Master of Etherium's non-CDA static
# ability.


# Scenario 2 #
# The opponent of the current controller of Master of Etherium enchants Master of Etherium
# with In Bolas's Clutches.
clutches = Clutches(controller=p1)

assert master_of_etherium.controller != clutches.controller

ZH.zone_battlefield.add_object(clutches)
clutches.enchanted_object = master_of_etherium


# Scenario 2 Outcome #
# Master of Etherium's controller becomes the controller of In Bolas's Clutches.
# Master of Etherium gains the legendary supertype.
# Master of Etherium's CDA sets its power and toughness to 1, since its new controller
# only controls 1 artifact creature (Master of Etherium itself).
# Alpha Myr's power and toughness return to their default values of 2/1, because Master of Etherium's
# non-CDA static ability no longer applies to it.

snapshot()
display([master_of_etherium, alpha_myr])

assert master_of_etherium.controller != alpha_myr.controller
assert master_of_etherium.controller == clutches.controller

assert master_of_etherium.supertypes == set(['legendary'])

assert master_of_etherium.power == master_of_etherium.toughness == 1

assert alpha_myr.power == 2
assert alpha_myr.toughness == 1

