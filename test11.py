from object_config import *

# Testing conditional power and toughness static ability based on whose turn it is.
angry_mob = AngryMob(controller=p0)
swamp0 = Swamp(controller=p1)
swamp1 = Swamp(controller=p1)


# Scenario #
# It is p0's turn.
GAME.active_idx = p0.player_idx
snapshot()
display([angry_mob])

# Outcome #
# Off the battlefield, Angry Mob's power and toughness are each equal to 2, regardless of whose turn it is.
assert angry_mob.power == angry_mob.toughness == 2


# Angry Mob is put onto the battlefield under p0's control.
ZH.zone_battlefield.add_object(angry_mob)
snapshot()
display([angry_mob])

# Outcome #
# It is Angry Mob's controller's turn; its power and toughness are each equal to 2 + the number of
# swamps Angry Mob's controller's opponents control, which is zero.
assert angry_mob.controller.player_idx == GAME.active_idx
assert angry_mob.power == angry_mob.toughness == 2


# Two Swamps are put onto the battlefield under p1's control.
ZH.zone_battlefield.add_object(swamp0)
ZH.zone_battlefield.add_object(swamp1)
snapshot()
display([angry_mob])

# Outcome #
# It is Angry Mob's controller's turn; its power and toughness are each equal to 2 + 2 == 4.
assert angry_mob.controller.player_idx == GAME.active_idx
assert angry_mob.power == angry_mob.toughness == 4


# It becomes p1's turn.
GAME.active_idx = 1
snapshot()
display([angry_mob])

# Outcome #
# Although Angry Mob's controller's opponents control two Swamps, it isn't Angry Mob's controller's
# turn, so, power and toughness are each back to 2.
assert angry_mob.controller.player_idx != GAME.active_idx
assert angry_mob.power == angry_mob.toughness == 2


# Manually over-riding Angry Mob's controller to switch to p1.
angry_mob._controller = p1
snapshot()
display([angry_mob])

# Outcome #
# Same case as above where the turn is correct, but Angry Mob's controller's opponents control no Swamps.
assert angry_mob.controller == p1
assert angry_mob.controller.player_idx == GAME.active_idx
assert angry_mob.power == angry_mob.toughness == 2
