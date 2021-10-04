from object_config import *

# Testing Copy Effects with Morph Effects #

branchsnap_lorian = BranchsnapLorian(p0)
ainok_tracker = AinokTracker(p0)

display([branchsnap_lorian])

## Branchsnap Lorian's owner casts it facedown, which in part, generates a continuous effect
## modifying its characteristics to the default facedown characteristics.
ZH.zone_battlefield.add_object(branchsnap_lorian)
branchsnap_lorian.turn_facedown()
snapshot()
display([branchsnap_lorian])

## Branchsnap Lorian's controller casts Clone and chooses to copy Branchsnap Lorian.
clone = Clone(p0)
clone.copy_source_object = branchsnap_lorian
ZH.zone_battlefield.add_object(clone)

snapshot()
display([branchsnap_lorian, clone])

# Outcome: Clone has characteristics given by the default for facedown permanents.

# Branchsnap Lorian's controller casts Ainok Tracker faceup.
ZH.zone_battlefield.add_object(ainok_tracker)
snapshot()
display([branchsnap_lorian, clone, ainok_tracker])

# Branchsnap Lorian's controller casts True Polymorph, targeting Branchsnap Lorian to
# become a copy of Ainok Tracker.
true_polymorph = TruePolymorph(p0)
add_target_to_object(branchsnap_lorian, true_polymorph)
true_polymorph.copy_source_object = ainok_tracker
resolve_effects(true_polymorph)

snapshot()
display([branchsnap_lorian, clone, ainok_tracker])

# Outcome: Branchsnap Lorian still appears with the default facedown characteristics
# since they over-ride the copiable values granted through True Polymorph.

# Branchsnap Lorian is turned faceup by its controller using the Morph ability
# granted to it from Ainok Tracker.
branchsnap_lorian.turn_faceup()
snapshot()
display([branchsnap_lorian, clone, ainok_tracker])

# Outcome: Branchsnap Lorian's characteristics reveal that it has taken on the copiable values
# of Ainok Tracker now that it is no longer facedown---i.e., its characteristics are no longer
# modified by its facedown status.
