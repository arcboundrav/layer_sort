from durations import *


class Game:
    '''\
        # NOTE #
        Abbreviated form of the proof-of-concept engine supporting the game loop
        in the engine repository.
    '''
    def __init__(self):
        self.current_player = None
        self.list_of_game_objects = list([])
        self.list_of_player_objects = list([])
        self.list_of_immaterial_objects = list([])
        self.gameover = False
        self.current_turn = None
        self.active_idx = 1
        self.n_extra_turns = 0
        self.limbo = list([])

    def registration(self):
        for player in self.players:
            player.environment = self
        for game_object in self.game_objects:
            game_object.environment = self
        for immaterial_object in self.immaterial_objects:
            immaterial_object.environment = self

    @property
    def list_of_mutable_objects(self):
        return self.list_of_player_objects + self.list_of_game_objects

    @property
    def active_player(self):
        return self.list_of_player_objects[self.active_idx]

    @property
    def non_active_idx(self):
        return xor(1, self.active_idx)

    @property
    def non_active_player(self):
        return self.list_of_player_objects[self.non_active_idx]

    #@property
    #def current_epoch(self):
    #    return self.current_turn.current_epoch

    def swap_active_player(self):
        self.active_idx = self.non_active_idx

    def broadcast_event(self, event):
        EVENT_HANDLER.broadcast_event(event)

GAME = Game()
