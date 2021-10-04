from object_config import *

humility = Humility(p0)

# Scenario 1 #
# Humility is put onto the battlefield under p0's control.
# Humility has a static ability which reads:
# All creatures lose all abilities and have base power and toughness 1/1.
ZH.zone_battlefield.add_object(humility)
display([humility])

opalescence = Opalescence(p0)

# Opalescence is put onto the battlefield under p0's control.
# Opalescence has a static ability which reads:
# Each other non-Aura enchantment is a creature in addition to its other types and
# has base power and toughness each equal to its mana value.
ZH.zone_battlefield.add_object(opalescence)

snapshot()
display([humility, opalescence])

# Outcome #
# Opalescence makes Humility into an enchantment creature, and does not affect itself.
# This causes Humility to see itself as a creature and remove its own ability.
# Opalescence makes Humility have base power and toughness 4/4.
assert humility.card_types == set(["creature", "enchantment"])
assert humility.abilities == []
assert humility.power == humility.toughness == 4


ZH.zone_battlefield.remove_specific_object_(humility)
ZH.zone_battlefield.remove_specific_object_(opalescence)

# Scenario 2 #
# Opalescence is put onto the battlefield under p0's control.
ZH.zone_battlefield.add_object(opalescence)
snapshot()
display([opalescence])

# Next, Humility is put onto the battlefield under p1's control.
ZH.zone_battlefield.add_object(humility)
snapshot()
display([opalescence, humility])

# Outcome #
# Opalescence's ability generates an effect with a component that applies in layer 4,
# adding creature to Humility's card types.
# Humility's ability generates an effect with a component that applies in layer 6. It
# sees itself and removes its own ability. The other components of this effect will
# continue to apply to the same set of objects even though the ability was removed
# according to 616.3.
# The other component of Opalescence's effect applies in layer 7b and sets Humility's
# base power and toughness to 4. However, the other component of Humility's effect also
# applies in layer 7b and has a more recent timestamp. Humility's base power and toughness
# are therefore set to 1/1
