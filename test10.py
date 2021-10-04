from object_config import *

anger = Anger(controller=p0)
alpha_myr = AlphaMyr(controller=p0)
mountain = Mountain(controller=p0)

has_haste_predicate = HasKeywordAbility(keyword_ability_type=KWAHaste)

# Alpha Myr is put onto the battlefield under p0's control.
ZH.zone_battlefield.add_object(alpha_myr)
snapshot()
display([alpha_myr])

# Outcome #
# Alpha Myr's abilities characteristic is equal to the default value: an empty list.
assert alpha_myr.abilities == []


# Next, Anger is put onto the battlefield under p0's control.
ZH.zone_battlefield.add_object(anger)
snapshot()
display([alpha_myr, anger])

# Outcome #
# Anger has Haste, but Alpha Myr does not; Anger is not in the correct zone for its
# static ability to generate an effect, and the conditions for that effect to add
# Haste to Alpha Myr are not met (Anger is not in p0's graveyard and p0 does not control
# any Mountains).
assert alpha_myr.abilities == []
assert has_haste_predicate.value_test(anger)


# Anger leaves the battlefield and is put into p0's graveyard.
ZH.zone_battlefield.remove_specific_object_(anger)
ZH.p0_zone_graveyard.add_object(anger)
snapshot()
display([alpha_myr, anger])

# Outcome #
# Anger has Haste, but Alpha Myr does not; although Anger is now in the correct zone for
# its static ability to generate an effect and the first condition for its effect to add
# Haste to Alpha Myr is satisfied, p0 still does not control a Mountain.
assert alpha_myr.abilities == []
assert has_haste_predicate.value_test(anger)


# Mountain is put onto the battlefield under p0's control.
ZH.zone_battlefield.add_object(mountain)
snapshot()
display([mountain, alpha_myr, anger])

# Outcome #
# Both Anger and Alpha Myr have Haste; Anger is in the correct zone, and now that p0
# controls a Mountain, all of the conditions on Anger's static ability are satisfied.
has_haste_predicate.value_test(alpha_myr)
has_haste_predicate.value_test(anger)
