from zones import *


class EventHandler:
    '''\
        Centralize control over event listeners, e.g., triggered abilities,
        durations which expire, replacement effects, etc.
    '''
    def __init__(self):
        self.listeners = set([])
        self.listeners_to_remove = set([])

    def broadcast_event(self, event):
        for listener in self.listeners:
            listener.react(event)

        # Remove all of the listeners which deregistered themselves as part of their reaction.
        if self.listeners_to_remove:
            for listener in self.listeners_to_remove:
                self.listeners.remove(listener)
            self.listeners_to_remove = set([])

    def register(self, listener):
        self.listeners.add(listener)

    def deregister(self, listener):
        if listener in self.listeners:
            self.listeners_to_remove.add(listener)

EVENT_HANDLER = EventHandler()


class BoundaryEvent:
    '''\
        Data-structure describing epoch boundary events matched against by
        event-based durations of continuous effects.
    '''
    def __init__(self, start, epoch_type, active_player):
        self.start = start
        self.epoch_type = epoch_type
        self.active_player = active_player


class UntilEndOfTurnSignal:
    '''\
        Special type for the end step turn-based action to use to cause
        until end of turn effects to expire.
    '''
    pass


class UntilEndOfTurnEvent(BoundaryEvent):
    '''\
        Special class for the end step turn-based action to use to cause
        until end of turn effects to expire.
    '''
    def __init__(self):
        super().__init__(start=False,
                         epoch_type=UntilEndOfTurnSignal,
                         active_player=None)



class BoundaryEventListener:
    def __init__(self, start, epoch_type, n_to_match=1):
        self.start = start
        self.epoch_type = epoch_type
        self.reference_effect = None
        self.active_player = None
        self.n_matches = 0
        self.n_to_match = n_to_match

    def solve_active_player(self):
        self.active_player = self.reference_effect.reference_ability.host_object.controller

    def match_active_player(self, event):
        raise NotImplementedError("BoundaryEventListener subclasses must over-ride match_active_player().")

    def update_reference_effect(self, reference_effect):
        self.reference_effect = reference_effect
        self.solve_active_player()
        # Now that references are synced, register with the event handler.
        EVENT_HANDLER.register(self)

    def match(self, event):
        if (self.start == event.start):
            if (self.epoch_type is event.epoch_type):
                if self.match_active_player(event):
                    return True
        return False

    def react(self, event):
        if self.match(event):
            self.n_matches += 1
            if (self.n_matches == self.n_to_match):
                self.expire()

    def expire(self):
        # Mark the effect for which we are the duration as expired
        setattr(self.reference_effect, 'expired', True)
        # Deregister ourselves from the event handler
        EVENT_HANDLER.deregister(self)

    def clone(self, clone_type):
        return clone_type(start=self.start, epoch_type=self.epoch_type, n_to_match=self.n_to_match)


class UntilEndOfTurnDuration(BoundaryEventListener):
    '''\
        Special duration for the common case of 'until end of turn' which isn't
        tied to a boundary event, as it is technically a turn-based action.
        Will match against instances of the special class at the top of the file,
        UntilEndOfTurnEvent, which use the special epoch_type UntilEndOfTurnSignal.
        The eventual implementation of this turn-based action can simply broadcast
        an instance of the UntilEndOfTurnEvent through the EVENT_HANDLER and it will
        cause UntilEndOfTurnDurations to match and cause their reference effects to
        expire and cause the durations to deregister from the EVENT_HANDLER.
    '''
    def __init__(self, start=False, epoch_type=UntilEndOfTurnSignal, n_to_match=1):
        super().__init__(start=start,
                         epoch_type=epoch_type,
                         n_to_match=n_to_match)

    def match_active_player(self, event):
        return True

    def clone(self):
        return super().clone(clone_type=UntilEndOfTurnDuration)


class SameAPDuration(BoundaryEventListener):
    def match_active_player(self, event):
        return self.active_player is event.active_player

    def clone(self):
        return super().clone(clone_type=SameAPDuration)


class OtherAPDuration(BoundaryEventListener):
    def match_active_player(self, event):
        return not(self.active_player is event.active_player)

    def clone(self):
        return super().clone(clone_type=OtherAPDuration)


class AnyAPDuration(BoundaryEventListener):
    def match_active_player(self, event):
        return True

    def clone(self):
        return super().clone(clone_type=AnyAPDuration)
