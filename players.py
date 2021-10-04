from apparent_state_handler import *


class ExpandedPlayerObject:
    '''\
        Minimal representation of Player instances for testing purposes.
    '''
    def __init__(self, player_idx=0):
        self.player_idx = player_idx
        self.lifetotal = 20
        self.starting_lifetotal = 20
        self.max_hand_size = 7
        self.has_priority = False
        self.object_id = id(self)
        self.temp_id = uuid.uuid4().hex
        self.temp_id_history = set([])
        self.environment = None
        self.n_lands_played_this_turn = 0
        self._abilities = list([])
        self.markers = list([])

    def __repr__(self):
        return "Player {}".format(self.player_idx)

    def __eq__(self, object):
        assert isinstance(object, ExpandedPlayerObject)
        return self.player_idx == object.player_idx

    @property
    def abilities(self):
        if (self.object_id in APPARENT_X.attr_val_dict):
            if ('abilities' in APPARENT_X.attr_val_dict[self.object_id]):
                return APPARENT_X.attr_val_dict[self.object_id]['abilities']
        return self._abilities

    @abilities.setter
    def abilities(self, value):
        APPARENT_X.modify_attribute_value(self, 'abilities', value)
