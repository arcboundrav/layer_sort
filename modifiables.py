from players import *


class Modifiable:
    def __init__(self, **kwargs):
        #########################
        # Layer Sort Attributes #
        #########################
        self._impl_name = ""
        self._mana_cost = ""
        self._color = set([])
        self._card_types = set([])
        self._subtypes = set([])
        self._supertypes = set([])
        self._abilities = list([])
        self._power = 0
        self._toughness = 0
        self._loyalty = 0
        self._controller = ""

        ############################
        # Miscellaneous Attributes #
        ############################
        self.object_id = id(self)
        self.temp_id = uuid.uuid4().hex
        self.temp_id_history = set([])
        self.prior_zone = None
        self.current_zone = None
        self.environment = None

        #####################
        # Marker Attributes #
        #####################
        self.markers = list([])
        self.can_have_markers = True
        self.prohibited_marker_types = list([])

        ##################################
        # Information Concerning Choices #
        ##################################
        self.enchanted_object = None
        self.enchanted_player = None
        self.equipped_object = None
        self.target_data = list([])
        self.copy_source_object = None
        self.chosen_opponent = None
        self.chosen_X = None
        self.object_types = set([])
        self.copiable_values = {}
        self.timestamp = 0

        ###################
        # Physical Status #
        ###################
        self.is_tapped = False
        self.is_facedown = False
        self.is_flipped = False
        self.is_phased_out = False

        ##########
        # Combat #
        ##########
        self.is_attacking = False
        self.is_blocking = False


        for kwarg in kwargs:
            if kwarg in CHARX:
                under_kwarg = '_' + kwarg
                setattr(self, under_kwarg, kwargs[kwarg])
            else:
                setattr(self, kwarg, kwargs[kwarg])

        self.solve_copiable_values()


    def update_temp_id(self):
        self.temp_id_history.add(self.temp_id)
        self.temp_id = uuid.uuid4().hex


    def query_(self, attribute_name):
        '''\
            Links to the apparent state handler which records the apparent value
            of certain attributes in the event they've been modified; otherwise,
            return the base attribute value.
        '''
        if (self.object_id in APPARENT_X.attr_val_dict):
            if (attribute_name in APPARENT_X.attr_val_dict[self.object_id]):
                return APPARENT_X.attr_val_dict[self.object_id][attribute_name]
        return getattr(self, "_{}".format(attribute_name))


    @property
    def impl_name(self):
        return self.query_('impl_name')

    @impl_name.setter
    def impl_name(self, value):
        APPARENT_X.modify_attribute_value(self, 'impl_name', value)

    @property
    def mana_cost(self):
        return self.query_('mana_cost')

    @mana_cost.setter
    def mana_cost(self, value):
        APPARENT_X.modify_attribute_value(self, 'mana_cost', value)

    @property
    def color(self):
        return self.query_('color')

    @color.setter
    def color(self, value):
        APPARENT_X.modify_attribute_value(self, 'color', value)

    @property
    def card_types(self):
        return self.query_('card_types')

    @card_types.setter
    def card_types(self, value):
        APPARENT_X.modify_attribute_value(self, 'card_types', value)

    @property
    def subtypes(self):
        return self.query_('subtypes')

    @subtypes.setter
    def subtypes(self, value):
        APPARENT_X.modify_attribute_value(self, 'subtypes', value)

    @property
    def supertypes(self):
        return self.query_('supertypes')

    @supertypes.setter
    def supertypes(self, value):
        APPARENT_X.modify_attribute_value(self, 'supertypes', value)

    @property
    def abilities(self):
        return self.query_('abilities')

    @abilities.setter
    def abilities(self, value):
        APPARENT_X.modify_attribute_value(self, 'abilities', value)

    @property
    def power(self):
        return self.query_('power')

    @power.setter
    def power(self, value):
        APPARENT_X.modify_attribute_value(self, 'power', value)

    @property
    def toughness(self):
        return self.query_('toughness')

    @toughness.setter
    def toughness(self, value):
        APPARENT_X.modify_attribute_value(self, 'toughness', value)

    @property
    def loyalty(self):
        return self.query_('loyalty')

    @loyalty.setter
    def loyalty(self, value):
        APPARENT_X.modify_attribute_value(self, 'loyalty', value)

    @property
    def controller(self):
        return self.query_('controller')

    @controller.setter
    def controller(self, value):
        APPARENT_X.modify_attribute_value(self, 'controller', value)

    @property
    def mana_value_X(self):
        '''\
            202.3e
            When calculating the mana value of an object with an {X} in its mana cost,
            X is treated as 0 while the object is not on the stack, and X is treated
            as the number chosen for it while the object is on the stack. 
        '''
        if (self.chosen_X is not None):
            if (self.current_zone is not None):
                if (self.current_zone.nickname == "the Stack"):
                    return self.chosen_X
        return 0

    @property
    def mana_value(self):
        '''\
            # NOTE #
            Currently does not support transforming double-faced cards, melded cards,
            flipped cards, or split cards.
        '''
        return solve_mana_value(self.mana_cost, self.mana_value_X)

    @property
    def is_monocolored(self):
        return len(self.color) == 1

    @property
    def is_multicolored(self):
        return len(self.color) > 1

    def solve_copiable_values(self):
        '''\
            Lock in the subset of Modifiable characteristics which are determined
            after Layer Sort is finished with Sublayer 1b.
        '''
        self.copiable_values = {}
        for attribute in COPIABLE_ATTRIBUTES:
            self.copiable_values[attribute] = getattr(self, attribute)

    ##################
    # Marker Methods #
    ##################
    def update_marker_timestamps_by_type(self, marker_type, new_timestamp):
        '''\
            613.7c Each counter receives a timestamp as it’s put on an object or player.
            If that object or player already has a counter of that kind on it, each counter
            of that kind receives a new timestamp identical to that of the new counter.
        '''
        for marker in self.markers:
            if isinstance(marker, marker_type):
                marker.timestamp = new_timestamp

    def add_marker_by_type(self, marker_type_to_add):
        if self.can_have_markers:
            if not(marker_type_to_add in self.prohibited_marker_types):
                new_marker = marker_type_to_add(host_object=self)
                self.update_marker_timestamps_by_type(marker_type=marker_type_to_add,
                                                      new_timestamp=new_marker.timestamp)
                self.markers.append(new_marker)

    def count_markers_by_type(self, marker_type):
        return sum(1 for marker in self.markers if isinstance(marker, marker_type))

    def __repr__(self):
        return "| {} | {} |".format(self.object_id, self.impl_name)
