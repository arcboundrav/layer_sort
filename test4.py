from object_config import *

# Testing Copy Effects #
# NOTE # Metamorphic Alteration would be another good example of auras

# Scenario #
alpha_myr = AlphaMyr(p0)
clone = Clone(p0)
copy_artifact = CopyArtifact(p0)

# Alpha Myr enters the battlefield under p0's control.

ZH.zone_battlefield.add_object(alpha_myr)
snapshot()
display([alpha_myr])

# Clone enters the battlefield and its controller chooses for it to enter as a copy
# of Alpha Myr.
clone.copy_source_object = alpha_myr
ZH.zone_battlefield.add_object(clone)

snapshot()
display([alpha_myr, clone])

# Outcome #
# Clone is characteristics-wise indistinguishable from Alpha Myr
for copiable_attribute in COPIABLE_ATTRIBUTES:
    print("copiable_attribute: {}".format(copiable_attribute))
    alpha_myr_attribute = getattr(alpha_myr, copiable_attribute)
    alpha_myr_attribute_type = type(alpha_myr_attribute)
    clone_attribute = getattr(clone, copiable_attribute)
    clone_attribute_type = type(clone_attribute)
    print("{} <{}> vs. {} <{}>".format(alpha_myr_attribute, alpha_myr_attribute_type, clone_attribute, clone_attribute_type))
    assert getattr(alpha_myr, copiable_attribute) == getattr(clone, copiable_attribute)


# Copy Artifact enters the battlefield and its controller chooses for it to enter as a copy
# of Clone, which appears to be a legal choice as it is copying Alpha Myr.
copy_artifact.copy_source_object = clone
ZH.zone_battlefield.add_object(copy_artifact)
snapshot()
display([alpha_myr, clone, copy_artifact])

for copiable_attribute in COPIABLE_ATTRIBUTES:
    if not(copiable_attribute == 'card_types'):
        assert getattr(alpha_myr, copiable_attribute) == getattr(clone, copiable_attribute) == getattr(copy_artifact, copiable_attribute)
    else:
        assert getattr(alpha_myr, copiable_attribute) == getattr(clone, copiable_attribute)
        assert getattr(copy_artifact, copiable_attribute) == set(['creature', 'artifact', 'enchantment'])


# The controller of Alpha Myr, Clone, and Copy Artifact resolves Infuriate, targeting Alpha Myr.
infuriate = Infuriate(p0)
add_target_to_object(alpha_myr, infuriate)
resolve_effects(infuriate)

snapshot()
display([alpha_myr, clone, copy_artifact])

# Outcome: Alpha Myr becomes 5/3. Neither Clone nor Copy Artifact have their power or toughness
# changed due to 707.2b and 707.2c.

assert alpha_myr.power == 5
assert alpha_myr.toughness == 3

assert clone.power == copy_artifact.power == 2
assert clone.toughness == copy_artifact.toughness == 1


