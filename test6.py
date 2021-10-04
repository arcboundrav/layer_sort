from object_config import *


# Testing Copy Effects w.r.t. CDA #

master_of_etherium = MasterOfEtherium(p0)

# Scenario: Master of Etherium's owner puts it onto the battlefield.

display([master_of_etherium])
ZH.zone_battlefield.add_object(master_of_etherium)

snapshot()
display([master_of_etherium])

assert master_of_etherium.power == master_of_etherium.toughness == 1


# Master of Etherium's controller puts Clone onto the battlefield, choosing to have it enter
# as a copy of Master of Etherium.
clone = Clone(p0)
clone.copy_source_object = master_of_etherium
ZH.zone_battlefield.add_object(clone)

# Outcome # Both permanents should be 3/3, 2/2 from their CDAs and +1/+1 from the other
# static ability.
snapshot()
display([master_of_etherium, clone])

assert master_of_etherium.power == master_of_etherium.toughness == 3
assert clone.power == clone.toughness == 3


# Master of Etherium's controller puts Quicksilver Gargantuan onto the battlefield,
# choosing to have it enter as a copy of Master of Etherium.
quicksilver_gargantuan = QuicksilverGargantuan(p0)
quicksilver_gargantuan.copy_source_object = master_of_etherium
ZH.zone_battlefield.add_object(quicksilver_gargantuan)

snapshot()
display([master_of_etherium, clone, quicksilver_gargantuan])

assert master_of_etherium.power == master_of_etherium.toughness == 5
assert clone.power == clone.toughness == 5
assert quicksilver_gargantuan.power == quicksilver_gargantuan.toughness == 9

# Outcome:
# Master of Etherium's CDA makes it 3/3 because Clone, Quicksilver Gargantuan, and itself
# are all artifacts. The non-CDA static abilities of Clone and Quicksilver Garguantuan both add +1/+1
# since Master of Etherium is an artifact creature, rendering it a 5/5.
#
# Clone's CDA makes it 3/3 because Master of Etherium, Quicksilver Gargantuan, and itself are all
# artifacts. The non-CDA static abilities of Master of Etherium and Quicksilver Gargantuan both add
# +1/+1 since Clone is an artifact creature, rendering it a 5/5.
#
# Quicksilver Gargantuan's copy effect provides an exception which specifies the value for two
# characteristics, power and toughness. Therefore, it does not copy the static ability of Master
# of Etherium which is a CDA defining these characteristics. It does still copy the other static
# ability, however. It's base power and toughness are 7/7, and the non-CDA static abilities of
# Master of Etherium and Clone both add +1/+1 since it is an artifact creature, rendering it
# a 9/9.

