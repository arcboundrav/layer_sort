from object_config import *

rune_of_flight = RuneOfFlight(p0)
colossus_hammer = ColossusHammer(p0)
alela = Alela(p0)

has_flying_predicate = HasKeywordAbility(keyword_ability_type=KWAFlying)

# Scenario #
# Alela is put onto the battlefield under p0's control.
ZH.zone_battlefield.add_object(alela)
snapshot()
display([alela])

# Outcome #
# Alela is 2/3 and has flying by default
assert alela.power == 2
assert alela.toughness == 3
assert has_flying_predicate.value_test(alela)


# Colossus Hammer is put onto the battlefield under p0's control, then
# is equipped to Alela.
ZH.zone_battlefield.add_object(colossus_hammer)
colossus_hammer.equipped_object = alela
snapshot()
display([alela, colossus_hammer])

# Outcome #
# Alela becomes 12/13 and loses flying.
assert alela.power == 12
assert alela.toughness == 13
assert not(has_flying_predicate.value_test(alela))


# Rune of Flight is put onto the battlefield under p0's control, enchanting Colossus Hammer.
ZH.zone_battlefield.add_object(rune_of_flight)
rune_of_flight.enchanted_object = colossus_hammer
snapshot()
display([alela, colossus_hammer, rune_of_flight])

# Outcome #
# Rune of Flight gives Colossus Hammer a Static Ability which generates an effect, granting
# flying to Alela.
assert alela.power == 12
assert alela.toughness == 13
assert has_flying_predicate.value_test(alela)

assert colossus_hammer.abilities[0].debug_string == "colossus_hammer_static"
assert colossus_hammer.abilities[1].debug_string == "rune_of_flight_granted_equipment_static"


# Rune of Flight stops enchanting Colossus Hammer and enchants Alela directly instead.
rune_of_flight.enchanted_object = alela
snapshot()
display([alela, colossus_hammer, rune_of_flight])

# Outcome #
# Rune of Flight grants flying to Alela, still a 12/13; Colossus Hammer's extra static ability
# is no longer there.
assert alela.power == 12
assert alela.toughness == 13
assert has_flying_predicate.value_test(alela)

assert colossus_hammer.abilities[0].debug_string == "colossus_hammer_static"
assert len(colossus_hammer.abilities) == 1
