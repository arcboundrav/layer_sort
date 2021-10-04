from object_config import *

archetype = ArchetypeOfFinality(controller=p0)
alela = Alela(controller=p1)
alpha_myr = AlphaMyr(controller=p1)
has_deathtouch_predicate = HasKeywordAbility(keyword_ability_type=KWADeathtouch)
has_trample_predicate = HasKeywordAbility(keyword_ability_type=KWATrample)

# Default Values #
snapshot()
display([archetype, alela, alpha_myr])

assert not(has_deathtouch_predicate.value_test(archetype))
assert has_deathtouch_predicate.value_test(alela)
assert alpha_myr.abilities == []


# Archetype of Finality is put onto the battlefield under p0's control.
ZH.zone_battlefield.add_object(archetype)
snapshot()
display([archetype, alela, alpha_myr])

# Outcome #
# Archetype of Finality grants itself deathtouch; Alela has deathtouch by default.
assert has_deathtouch_predicate.value_test(archetype)
assert has_deathtouch_predicate.value_test(alela)
assert alpha_myr.abilities == []


# Alela is put onto the battlefield under p1's control.
ZH.zone_battlefield.add_object(alela)
snapshot()
display([archetype, alela, alpha_myr])

# Outcome #
# Archetype of Finality continues to grant itself deathtouch; Alela loses deathtouch.
assert has_deathtouch_predicate.value_test(archetype)
assert not(has_deathtouch_predicate.value_test(alela))
assert alpha_myr.abilities == []


# Alpha Myr is put onto the battlefield under p1's control; then a deathtouch keyword
# counter and a trample keyword counter are put on both Alela and Alpha Myr.
ZH.zone_battlefield.add_object(alpha_myr)
alela.add_marker_by_type(KWADeathtouchMarker)
alela.add_marker_by_type(KWATrampleMarker)
alpha_myr.add_marker_by_type(KWADeathtouchMarker)
alpha_myr.add_marker_by_type(KWATrampleMarker)

snapshot()
display([archetype, alela, alpha_myr])

# Outcome #
# Archetype of Finality continues to grant itself deathtouch; Alela and Alpha Myr
# do not gain deathtouch from their keyword counters; Alela and Alpha Myr do, however,
# gain trample from their keyword counters, since they aren't banned from gaining that
# keyword ability by Archetype of Finality.
assert has_deathtouch_predicate.value_test(archetype)
assert not(has_deathtouch_predicate.value_test(alela))
assert not(has_deathtouch_predicate.value_test(alpha_myr))
assert has_trample_predicate.value_test(alela)
assert has_trample_predicate.value_test(alpha_myr)


# Archetype of Finality leaves the battlefield.
ZH.zone_battlefield.remove_specific_object_(archetype)
snapshot()
display([archetype, alela, alpha_myr])


# Outcome #
# Archetype of Finality no longer grants itself deathtouch and no longer prohibits Alela and Alpha Myr
# from having deathtouch, which they immediately gain from their keyword counters. Alela has two instances
# of deathtouch, which are redundant.
assert not(has_deathtouch_predicate.value_test(archetype))
assert has_deathtouch_predicate.value_test(alela)
assert has_deathtouch_predicate.value_test(alpha_myr)
assert has_trample_predicate.value_test(alela)
assert has_trample_predicate.value_test(alpha_myr)

assert alpha_myr.power == 2
assert alpha_myr.toughness == 1


# Three +1/+1 counters are put on Alpha Myr.
alpha_myr.add_marker_by_type(PlusOnePlusOneMarker)
alpha_myr.add_marker_by_type(PlusOnePlusOneMarker)
alpha_myr.add_marker_by_type(PlusOnePlusOneMarker)
snapshot()
display([alpha_myr])

# Outcome #
# Alpha Myr's power and toughness increase by 3.
assert alpha_myr.power == 5
assert alpha_myr.toughness == 4


# A -1/-1 counter is put on Alpha Myr.
alpha_myr.add_marker_by_type(MinusOneMinusOneMarker)
snapshot()
display([alpha_myr])

# Outcome #
# Alpha Myr's power and toughness are increased by 2.
assert alpha_myr.power == 4
assert alpha_myr.toughness == 3
