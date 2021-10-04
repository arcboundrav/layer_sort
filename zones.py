from modifiables import *


class Zone(list):
    '''\
        Attributes to consider:
            player <ExtendedPlayerObject>   Sole owner of a non-shared zone.
            shared          <bool>          Zone may be occupied by objects owned by either player.
            zid             <int>           unique int identifying this zone := id(self)
            nickname        <str>           shortcut for zone referencing

        A Zone is a subclass of list with additional properties supporting characterization,
        and additional methods for altering the data of elements added / removed.
    '''
    def __init__(self, **kwargs):
        self._player = None
        self.shared = False
        self.nickname = "Zone"
        for kwarg in kwargs:
            setattr(self, kwarg, kwargs[kwarg])

    def __repr__(self):
        return "{}".format(self.nickname)

    @property
    def player(self):
        return self._player

    @player.setter
    def player(self, value):
        self._player = value

    @property
    def is_empty(self):
        return not(bool(self.__len__()))

    def imprint_all(self):
        for object in self:
            self.imprint_object(object)

    def imprint_object(self, object_to_imprint):
        '''\
            Ensure that the object:
                has its prior zone recorded;
                has an updated current_zone attribute value;
                receives a new temporary id to make a distinction that prevents past effects
                that affected it from continuing to affect it; and,
                has a new timestamp.
        '''
        object_to_imprint.current_zone = self
        object_to_imprint.update_temp_id()
        object_to_imprint.timestamp = TIMESTAMP()


    def remove_imprint(self, object_to_clean):
        object_to_clean.prior_zone = object_to_clean.current_zone
        object_to_clean.current_zone = None


    def release_object(self, object):
        ''' Command objects leaving this Zone to call their case-based zone change routines. '''
        pass

    def accept_object(self, object):
        ''' Command objects entering this Zone to call their case-based zone change routines. '''
        pass

    def shuffle(self):
        np.random.shuffle(self)

    def add_object(self, object, top=False):
        if not(object in self):
            if not(top):
                self.append(object)
            else:
                self.reverse()
                self.append(object)
                self.reverse()
            self.imprint_object(object)
        else:
            raise ValueError("{} tried to add an object it already contained: {}".format(self.nickname, object))


    def remove_object(self, top=False):
        if not(top):
            removed_object = self.pop()
        else:
            self.reverse()
            removed_object = self.pop()
            self.reverse()
        self.remove_imprint(removed_object)
        return removed_object


    def remove_specific_object_(self, object):
        if (object in self):
            removed_object = self.pop(self.index(object))
            self.remove_imprint(removed_object)
            return removed_object
        raise ValueError("{} tried to remove an object it didn't contain: {}".format(self.nickname, object))


    def add_objects(self, list_of_objects, top=False):
        if not(top):
            for object in list_of_objects:
                self.add_object(object, top=False)
        else:
            for object in list_of_objects[::-1]:
                self.add_object(object, top=True)


    def remove_n_objects(self, n_objects, top=False):
        removed_objects = []
        n_objects = min(n_objects, self.__len__())

        if not(top):
            for i in range(n_objects):
                removed_object = self.remove_object(top=False)
                removed_objects.append(removed_object)

        else:
            for i in range(n_objects):
                removed_object = self.remove_object(top=True)
                removed_objects.append(removed_object)
            removed_objects = removed_objects[::-1]

        return list(removed_objects)


    def list_object_ids(self):
        return [id(object) for id in self]


    def list_n_ids(self, n_ids, top=False):
        ''' Return a list of the first n objects in the top or bottom of this Zone. '''
        n_ids = min(n_ids, self.__len__())
        result = []
        if n_ids:
            if not(top):
                result = [id(object) for object in self[n_ids:]]
            else:
                result = [id(object) for object in self[:n_ids]]

        return list(result)


class SharedZone(Zone):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._player = None
        self.shared = True

    @property
    def player(self):
        raise AttributeError("SharedZones do not have a player attribute.")


class ScryZone(Zone):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Battlefield(SharedZone):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def accept_object(self, object):
        ''' Command an object entering this Zone to run its case-based zone change routine. '''
        object.zone_arrival(self.name)

    def release_object(self, object):
        ''' Command an object leaving this Zone to run its case-base zone change routine. '''
        pass


class Graveyard(Zone):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Exile(SharedZone):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Stack(SharedZone):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Hand(Zone):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Library(Zone):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Command(Zone):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


def zone_handler_sync_attributes():
    zone_names_to_distribute = ("zone_hand", "zone_library", "zone_graveyard", "zone_command", "zone_scry")
    p0_template = "p0_"
    p1_template = "p1_"
    return {"p0":[(p0_template+zone_name, zone_name) for zone_name in zone_names_to_distribute],
            "p1":[(p1_template+zone_name, zone_name) for zone_name in zone_names_to_distribute]}

ZONE_HANDLER_SYNC_ATTRIBUTE_DICT = zone_handler_sync_attributes()


class ZoneHandler:
    '''\
        Centralize control over objects transitioning between zones, references
        to objects on the basis of their controllers/owners/current zones, and
        support resyncing of objects during game tree expansion.
    '''
    def __init__(self, **kwargs):
        self.zone_stack = Stack(player_id=None, nickname="the Stack")
        self.zone_battlefield = Battlefield(player_id=None, nickname="the Battlefield")
        self.zone_exile = Exile(player_id=None, nickname="Exile")
        self.p0_zone_hand = Hand(player_id=0, nickname="P0's Hand", player=None)
        self.p1_zone_hand = Hand(player_id=1, nickname="P1's Hand", player=None)
        self.p0_zone_library = Library(player_id=0, nickname="P0's Library", player=None)
        self.p1_zone_library = Library(player_id=1, nickname="P1's Library", player=None)
        self.p0_zone_graveyard = Graveyard(player_id=0, nickname="P0's Graveyard", player=None)
        self.p1_zone_graveyard = Graveyard(player_id=1, nickname="P1's Graveyard", player=None)
        self.p0_zone_command = Command(player_id=0, nickname="P0's CommandZone", player=None)
        self.p1_zone_command = Command(player_id=1, nickname="P1's CommandZone", player=None)
        self.p0_zone_scry = ScryZone(player_id=0, nickname="P0's ScryZone", player=None)
        self.p1_zone_scry = ScryZone(player_id=1, nickname="P1's ScryZone", player=None)
        self.zones = [self.zone_stack,
                      self.zone_battlefield,
                      self.zone_exile,
                      self.p0_zone_hand,
                      self.p1_zone_hand,
                      self.p0_zone_library,
                      self.p1_zone_library,
                      self.p0_zone_graveyard,
                      self.p1_zone_graveyard,
                      self.p0_zone_command,
                      self.p1_zone_command,
                      self.p0_zone_scry,
                      self.p1_zone_scry]

        self.shared_zones = list(filter(lambda zone: zone.shared, self.zones))
        self.unshared_zones = list(filter(lambda zone: not(zone.shared), self.zones))
        self.zone_types = [("scry",ScryZone), ("command",Command), ("graveyard",Graveyard), ("library",Library), ("hand",Hand), ("battlefield",Battlefield), ("exile",Exile), ("stack",Stack)]

        for kwarg in kwargs:
            setattr(self, kwarg, kwargs[kwarg])


    def sync_zones_to_objects(self):
        for zone in self.zones:
            for object in zone:
                setattr(object, 'current_zone', zone)


    def sync_shared_zones_to_player_(self, player):
        '''\
            Force player to have shared zone attribute values matching the current zone handler.
        '''
        setattr(player, "zone_battlefield", getattr(self, "zone_battlefield"))
        setattr(player, "zone_stack", getattr(self, "zone_stack"))
        setattr(player, "zone_exile", getattr(self, "zone_exile"))


    def sync_shared_zones_from_player_(self, player):
        '''\
            Force the current zone handler to match its shared zone attribute values to player's.
        '''
        setattr(self, "zone_battlefield", getattr(player, "zone_battlefield"))
        setattr(self, "zone_stack", getattr(player, "zone_stack"))
        setattr(self, "zone_exile", getattr(player, "zone_exile"))


    def sync_zones_from_zh_to_players(self, player0, player1):
        '''\
            Force player0 and player1 to have zone attribute values which
            match the current zone handler instance.
        '''
        for zone in self.zones:
            if (zone.player_id is not None):
                if zone.player_id:
                    zone.player = player1
                else:
                    zone.player = player0

        for item in ZONE_HANDLER_SYNC_ATTRIBUTE_DICT['p0']:
            setattr(player0, item[1], getattr(self, item[0]))
        self.sync_shared_zones_to_player_(player0)

        for item in ZONE_HANDLER_SYNC_ATTRIBUTE_DICT['p1']:
            setattr(player1, item[1], getattr(self, item[0]))
        self.sync_shared_zones_to_player_(player1)


    def sync_zones_from_players_to_zh(self, player0, player1):
        '''\
            Force the current zone handler to match its unshared zone attribute values to
            those of player0 and player 1 (and sync its shared zone attribute values to
            match those of player0, which should be identical to player1, but only needs
            to be done once in this direction).
        '''
        # NOTE #
        # Beware of a bug where player_i.zone_j.player != player_i somehow?
        # Unlikely, but check for it if things go strange in the future.
        self.sync_shared_zones_from_player_(player0)

        for item in ZONE_HANDLER_SYNC_ATTRIBUTE_DICT['p0']:
            setattr(self, item[0], getattr(player0, item[1]))
        for item in ZONE_HANDLER_SYNC_ATTRIBUTE_DICT['p1']:
            setattr(self, item[0], getattr(player1, item[1]))
        self.sync_zones_to_objects()



    def move_n(self, src_zone, src_top, dst_zone, dst_top, n_obj_to_move, sigma=None):
        n_obj_to_move = min(n_obj_to_move, src_zone.__len__())
        if n_obj_to_move:
            removed_objects = src_zone.remove_n_objects(n_objects=n_obj_to_move, top=src_top)
            if sigma:
                zone_0_perm_objects = []
                zone_1_perm_objects = []
                if sigma[0]:
                    for index in sigma[0]:
                        zone_0_perm_objects.append(removed_objects[index])
                    zone_0_perm_objects = zone_0_perm_objects[::-1]
                    for object in zone_0_perm_objects:
                        src_zone.add_object(object, top=True)

                if sigma[1]:
                    for index in sigma[1]:
                        zone_1_perm_objects.append(removed_objects[index])
                    if dst_top:
                        zone_1_perm_objects = zone_1_perm_objects[::-1]
                    for object in zone_1_perm_objects:
                        dst_zone.add_object(object, top=dst_top)

                src_zone.imprint()
                dst_zone.imprint()

            else:
                dst_zone.add_objects(list_of_objects=removed_objects, top=dst_top)
                dst_zone.imprint()


    def move_obj(self, src_zone, dst_zone, dst_top, obj_to_move):
        # NOTE # Exceptions are thrown by the remove_specific_object_ and
        #        add_object methods of each Zone, so no need to check here.
        removed_object = src_zone.remove_specific_object_(obj_to_move)
        dst_zone.add_object(removed_object, top=dst_top)


    def shuffle_objects_into_zone(self, list_of_objects, dst_zone):
        ''' For shuffling >=1 objects into a single Zone. '''
        if list_of_objects:
            dst_zone.add_objects(list_of_objects=source_objects, top=True)
            dst_zone.imprint()

        dst_zone.shuffle()


    def shuffle_zones_into_zone(self, src_zones, dst_zone):
        ''' For shuffling >=1 Zone into a single Zone. '''
        source_objects = []
        for zone in src_zones:
            zone_size = zone.__len__()
            if zone_size:
                removed_objects = zone.remove_n_objects(zone_size)
                source_objects.extend(removed_objects)
        self.shuffle_objects_into_zone(list_of_objects=source_objects, dst_zone=dst_zone)


    def add_object_by_zone_name_and_player_id(self, object, dst_zone_name, dst_zone_player_id):
        zone = self.filter_by_zone_names_and_player_ids([dst_zone_name], [dst_zone_player_id])
        zone = zone[0]
        zone.add_object(object)
        zone.imprint()


    def select_by_zone_name_and_subset_size(self, zone_name, size, top=True):
        result = []
        ref_zone = self.filter_by_zone_names([zone_name])[0]
        ref_zone_size = len(ref_zone)
        subset_size = min(ref_zone_size, size)

        if subset_size:
            subset_object_ids = ref_zone.list_n_ids(subset_size, top)
            result = subset_object_ids

        return result


ZH = ZoneHandler()
