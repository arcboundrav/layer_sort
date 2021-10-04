from abilities import *


class EffectManager:
    '''\
        Determine which static abilities should generate continuous effects,
        cause them to generate those effects, and aggregate them. Determine
        which extant continuous effects generated via the resolution of spells or abilities,
        (or due to the face-down physical status of cards) have not yet expired.
        Decompose these effects into their components and provide them to the ApparentStateHandler
        to solve the order in which they should be applied.
        Apply them according to this order, deriving the apparent state.
        
        Note: Only continuous effects which modify the characteristics or controller of
              game objects, or which modify the abilities of players, are currently supported.
        Note: Mutate / merging with permanents is not currently supported.
        
    '''
    def __init__(self):
        self.effects = list([])
        self.static_ids = set([])
        self.marker_effect_components = list([])
        self.used_components = list([])
        self.game_objects = list([])
        self.immaterial_objects = list([])
        self.solved_copiable_values = False

    def calibrate(self):
        self.static_ids = set([])
        self.effects.clear()
        self.marker_effect_components.clear()
        self.used_components.clear()
        self.game_objects = LINKS.game_objects.compute()
        self.immaterial_objects = LINKS.immaterial_objects.compute()
        self.solved_copiable_values = False

    @property
    def unused_marker_effect_components(self):
        return list(filter(lambda marker_fxc: not(marker_fxc in self.used_components), self.marker_effect_components))

    def gather_effects(self):
        self.gather_resolution_generated_effects()
        self.gather_static_ability_generated_effects()

    def novel_active_static_abilities(self, game_object):
        return (ability for ability in game_object.abilities if ((isinstance(ability, StaticAbility) and (ability.is_active)) and not(ability.object_id in self.static_ids)))

    def gather_static_ability_generated_effects(self):
        for game_object in self.game_objects:
            for novel_active_static_ability in self.novel_active_static_abilities(game_object):
                self.static_ids.add(novel_active_static_ability.object_id)
                self.effects.append(novel_active_static_ability.generate_effect())

    def gather_resolution_generated_effects(self):
        for immaterial_object in self.immaterial_objects:
            if isinstance(immaterial_object, ContinuousEffectViaResolution):
                if immaterial_object.is_valid:
                    self.effects.append(immaterial_object)

    def gather_marker_effect_components(self):
        for game_object in self.game_objects:
            for marker in game_object.markers:
                marker_effect_component = marker.effect_component
                if (marker_effect_component is not None):
                    self.marker_effect_components.append(marker_effect_component)

    def gather_components(self):
        self.gather_marker_effect_components()
        components = self.unused_marker_effect_components
        self.gather_effects()
        for effect in self.effects:
            for component in effect.components:
                components.append(component)
        return components

    def regather_components(self):
        components = self.unused_marker_effect_components
        self.gather_static_ability_generated_effects()
        for effect in self.effects:
            for component in effect.components:
                if not(component in self.used_components):
                    components.append(component)
        return components

    def component_sort(self, sublayer):
        return sorted(sublayer, key=lambda item: (item.relative_component_ordinal, item.timestamp))

    def partition_by_is_cda(self, sublayer_of_components):
        return partition(lambda obj: (obj.is_cda), sublayer_of_components)

    def filter_by_layer(self, target_layer, list_of_components):
        return pobj('layer', target_layer, list_of_components)

    def partition_by_sublayer(self, all_components):
        sublayer_dict = defaultdict(list)
        for sublayer_string in SUBLAYER_LIST:
            sublayer_dict[sublayer_string] = self.component_sort(self.filter_by_layer(sublayer_string, all_components))
        return sublayer_dict

    def solve_copiable_values(self):
        for game_object in self.game_objects:
            game_object.solve_copiable_values()
        self.solved_copiable_values = True

    def solve_sublayer(self, components):
        result = APPARENT_X.solve_sort(components)
        return result[0]

    def solve_layer(self, components):
        yes, no = self.partition_by_is_cda(components)
        yes = list(yes)
        if yes:
            return APPARENT_X.solve_sort(yes)[0]
        return APPARENT_X.solve_sort(list(no))[0]

    def next_effect_to_apply(self, initial=True):
        components = self.gather_components() if initial else self.regather_components()
        sublayers = self.partition_by_sublayer(components)
        for sublayer_key in SUBLAYER_LIST:
            if sublayers[sublayer_key]:
                if (sublayer_key in NO_CDA_SUBLAYERS):
                    return self.solve_sublayer(components=sublayers[sublayer_key])
                else:
                    return self.solve_layer(components=sublayers[sublayer_key])
            if (sublayer_key == '1b'):
                if not(self.solved_copiable_values):
                    self.solve_copiable_values()
        return None

    def old_snapshot(self):
        APPARENT_X.calibrate()
        self.calibrate()
        to_apply = self.next_effect_to_apply(initial=True)
        while (to_apply is not None):
            if not(to_apply.valid):
                for component in to_apply.reference_effect.components:
                    self.used_components.append(component)
            else:
                to_apply.enact(lock=True)
                self.used_components.append(to_apply)

            to_apply = self.next_effect_to_apply(initial=False)

    def layer_sort(self, components):
        valid_components = [c for c in components if (c.valid)]
        APPARENT_X.solve_sort(valid_components)
        self.used_components.extend(components)

    def snapshot(self):
        APPARENT_X.calibrate()
        self.calibrate()
        components = self.gather_components()
        sublayers = self.partition_by_sublayer(components)

        for sublayer in ['1a', '1b']:
            if sublayers[sublayer]:
                self.layer_sort(sublayers[sublayer])

        self.solve_copiable_values()

        components = self.regather_components()
        sublayers = self.partition_by_sublayer(components)

        for sublayer in ['2', '3', '4', '5', '6']:
            if sublayers[sublayer]:
                self.layer_sort(sublayers[sublayer])

        components = self.regather_components()
        sublayers = self.partition_by_sublayer(components)

        for sublayer in ['6', '7a', '7b', '7c', '7d', '8']:
            if sublayers[sublayer]:
                self.layer_sort(sublayers[sublayer])




FX_HANDLER = EffectManager()
