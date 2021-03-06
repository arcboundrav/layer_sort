from object_config import *

gilded_light0 = GildedLight(controller=p0)
gilded_light1 = GildedLight(controller=p1)
gor_muldrak = GorMuldrakAmphinologist(controller=p0)
frogify = Frogify(controller=p0)

has_shroud_predicate = HasKeywordAbility(keyword_ability_type=KWAShroud)
has_protection_predicate = HasKeywordAbility(keyword_ability_type=KWAProtection)

snapshot()
display([gor_muldrak])
displayP([p0, p1])

# Outcome #
# Gor Muldrak has his static but does not yet confer to himself or to p0 the Protection keyword ability.
# By default, neither p0 nor p1 have any abilities.
assert p0.abilities == []
assert p1.abilities == []
assert not(has_protection_predicate.value_test(gor_muldrak))


# p0 resolves Gilded Light.
resolve_effects(gilded_light0)
snapshot()
displayP([p0, p1])

# Outcome #
# p0 gains the keyword ability Shroud.
assert has_shroud_predicate.value_test(p0)


# p1 resolves their own Gilded Light.
resolve_effects(gilded_light1)
snapshot()
displayP([p0, p1])

# Outcome #
# p1 gains the keyword ability Shroud as well.
assert has_shroud_predicate.value_test(p0)
assert has_shroud_predicate.value_test(p1)


# The end of turn causes these effects to expire.
EVENT_HANDLER.broadcast_event(UntilEndOfTurnEvent())
snapshot()
displayP([p0, p1])

# Outcome #
# Neither player has the keyword ability Shroud any longer.
assert p0.abilities == []
assert p1.abilities == []


# Gor Muldrak, Amphinologist is put onto the battlefield under p0's control.
ZH.zone_battlefield.add_object(gor_muldrak)
snapshot()
displayP([p0, p1])
display([gor_muldrak])

# Outcome #
# Gor Muldrak grants the protection keyword ability to p0 and to himself.
assert has_protection_predicate.value_test(p0)
assert not(has_protection_predicate.value_test(p1))
assert has_protection_predicate.value_test(gor_muldrak)


# Frogify is put onto the battlefield under p0's control, attached to Gor Muldrak, Amphinologist.
ZH.zone_battlefield.add_object(frogify)
frogify.enchanted_object = gor_muldrak
snapshot()
displayP([p0, p1])
display([gor_muldrak, frogify])

# Outcome #
# Gor Muldrak loses all abilities; therefore, it no longer grants itself protection and no longer
# grants p0 protection. It should also not grant protection to Frogify, which is a permanent
# controlled by p0, even though its static ability generates an effect which, according to timestamps,
# should be applied to Frogify before the effect generated by Frogify's ability is applied to Gor Muldrak.
# In other words, the existence of the component of the effect generated by Gor Muldrak's ability which
# is applied in layer 6 depends on the application of the component of Frogify's effect that is also applied
# in layer 6; Gor Muldrak's effect is therefore dependent on Frogify's effect and should wait until
# immediately after to apply; however, immediately after Frogify's effect is applied, it no longer exists,
# so it can't have any effect on any game object or player.
assert gor_muldrak.abilities == []
assert p0.abilities == []
assert p1.abilities == []
assert not(has_protection_predicate.value_test(frogify))


