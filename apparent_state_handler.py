from combinatorics import *


def copy_sensitive(value):
    '''\
        Wrapper to ensure that references match distinct objects in memory during
        copying of attribute values so that comparisons work correctly.
    '''
    if (type(value) in [set, list, dict]):
        return deepcopy(value)
    return value


def compute_difference(op0, op1):
    '''\
        Polymorphic, dispatching on operand types. Assumes type(op0) == type(op1).
    '''
    op0_type = type(op0)
    op1_type = type(op1)

    assert op0_type is op1_type

    if op0_type==int:
        return op0 - op1
    elif op0_type==set:
        return (op0.difference(op1), op0.symmetric_difference(op1))
    else:
        return op0 == op1


def delta_dicts(avd, ravd):
    '''\
        The base attribute value of a Modifiable instance's attribute is recorded in
        ravd[id(instance)][attribute] the first time setattr(instance, attribute, new_value)
        is called; and, ANY TIME, setattr(instance, attribute, new_value) is called,
        avd[id(instance)][attribute] = new_value is executed as well.

        If we start with the base state X, then derive A(X) by enacting effect component A,
        the impact on X of A can be quantified by subtracting ravd from avd.

        This approach works since only A can be responsible for all of the data in avd and ravd.
        However, it can possibly break down when quantifying the impact on A(X) of a second
        effect component, B. Before enacting B, ravd is cleared but avd is set to the avd
        resulting from A(X), so that B can see A(X), in the event some of its impact is a function
        of attribute values of attributes of objects influenced by A.
        
        After deriving B(A(X)), quantifying the impact of B on A(X) cannot be done by
        directly subtracting ravd from avd, because it is possible that data contained in
        avd is the result of deriving A(X).

        For consistency regardless of which case this function is used for, always subtract ravd from
        avd, but, only consider in the final result data in avd for which B was at least partially
        responsible.
    '''
    impact = defaultdict(dict)
    relevant_object_keys = ravd.keys()
    for relevant_object_key in relevant_object_keys:
        relevant_attribute_keys = ravd[relevant_object_key].keys()
        for relevant_attribute_key in relevant_attribute_keys:
            avd_data = avd[relevant_object_key][relevant_attribute_key]
            ravd_data = ravd[relevant_object_key][relevant_attribute_key]
            impact[relevant_object_key][relevant_attribute_key] = compute_difference(avd_data, ravd_data)
    return impact


class ApparentStateHandler:
    '''\
        Machinery for solving the interaction of continuous effects via the layer system,
        for producing the 'apparent state' in view of the base state and the correctly
        ordered application of modifications through the components of effects which modify
        either the characteristics, or controller, of game objects. Uses networkx to instantiate
        a digraph to facilitate detection and removal of dependency cycles, and thereafter, to
        facilitate linearization of the resultant directed acyclic graph---such that the order of
        vertices obeys the rules of MTG.

        As the place where the base state of game objects and continuous effects interact, the
        ApparentStateHandler also ties directly to the modifiable properties of each instance of a
        Modifiable. This facilitates restoring/loading/analyzing changes to attribute values of
        Modifiable objects in response to the application of components of effects, which is vital
        for solving the interaction of continuous effects. It also supports aggregation of changes
        to attribute values over time, while maintaining a dissociation with the base_state attribute
        values.
    '''
    def __init__(self):
        self.attr_val_dict = defaultdict(dict)
        self.ref_attr_val_dict = defaultdict(dict)
        self.snapshot = None

        # A dictionary with:
        #   keys        the object_id of effect components applied to the state; and,
        #   values      a 3-list, L, where:
        #               L[0] is a deepcopy of the reference attribute value dictionary
        #               L[1] is a deepcopy of the attribute value dictionary (representing the state after
        #                    applying the corresponding effect component).
        #               L[2] is the delta dict quantifying the difference between L[1] and L[0],
        #               in other words, the impact on the state of applying the associated effect component.
        self.first_order_component_data = defaultdict(list)

        # A dictionary with:
        #   keys        2-tuples T where:
        #               T[0] is the object_id of one effect component
        #               T[1] is the object_id of a distinct effect component
        #   values      a 4-list, L, where:
        #               L[0] is a deepcopy of the reference attribute value dictionary
        #               L[1] is a deepcopy of the attribute value dictionary
        #               L[2] is the delta dict quantifying the difference between L[1] and L[0],
        #               L[3] is a boolean flag that is True when enacting the effect component at T[0]
        #                    changed the state such that the generator of the effect component at T[1]
        #                    was removed and therefore T[1] no longer exists. This pattern, by definition,
        #                    implies that T[1] depends on T[0].
        #               For second order component data, we retrieve the previously computed impact on the state
        #               of applying the effect component with object_id T[0] before applying the effect component
        #               with object_id T[1]. L[2] therefore quantifies the impact on the state of applying the second
        #               effect component after applying the first effect component.
        self.second_order_component_data = defaultdict(list)

    def calibrate(self):
        self.attr_val_dict.clear()
        self.ref_attr_val_dict.clear()
        self.snapshot = None
        self.first_order_component_data.clear()
        self.second_order_component_data.clear()

    def refresh_attr_val_dict(self):
        self.attr_val_dict.clear()

    def refresh_ref_attr_val_dict(self):
        self.ref_attr_val_dict.clear()

    def ref_attr_val_check(self, obj, attribute):
        '''\
            Avoid needing a reference representation of the entire domain by recording
            only what is necessary---by taking a snapshot of a given attribute value of a given object
            the first time it is modified during application of a given component.
            Only this information is pertinent for quantifying the impact of applying an effect to
            the State and for comparing the impacts of applying different effects to the State.
        '''
        if not(attribute in self.ref_attr_val_dict[obj.object_id]):
            self.ref_attr_val_dict[obj.object_id][attribute] = copy_sensitive(getattr(obj, attribute))

    def modify_attribute_value(self, obj, attribute, new_value):
        '''\
            A Modifiable has attributes which are subject to modification by continuous effects.
            These attributes are properties with getter and setter methods which interact with
            this class.
            When the attribute value of one of these properties is set, this method is called.
            The reference value of the attribute is recorded in self.ref_attr_val_dict the
            first time there is an attempt to assign a new value to that attribute of that object.
            The assigned value is stored in self.attr_val_dict.
            When the attribute value of one of these properties is queried, if it has been modified
            then the value stored in self.attr_val_dict is returned, otherwise the underlying
            base value of the attribute stored in the object itself is returned.
        '''
        # Make sure that we have a reference value on record for the value of that attribute of that object
        self.ref_attr_val_check(obj, attribute)
        # Update the apparent value of that attribute of that object
        self.attr_val_dict[obj.object_id][attribute] = new_value

    def store_state(self):
        self.snapshot = deepcopy(self.attr_val_dict)

    def load_state(self, state_to_load):
        if (state_to_load is not None):
            self.attr_val_dict = deepcopy(state_to_load)

    def restore_state(self):
        self.load_state(self.snapshot)

    def return_ravd(self):
        return deepcopy(self.ref_attr_val_dict)

    def return_avd(self):
        return deepcopy(self.attr_val_dict)

    def refresh_components(self, components):
        '''\
            Clear the scope_cache of all of the superordinate effects of these components.
            The efficiency decreases as the number of components per effect increases.
            # NOTE #
            Components derived from counters which add keyword abilities or modify power and/or
            toughness do not have a reference effect.
        '''
        for component in components:
            if not(component.is_marker_effect_component):
                component.reference_effect.refresh_selectable_objects_cache()

    def first_order_data_(self, component):
        '''\
            Compute and store the impact on the attribute values of Modifiables affected
            by applying the given effect component.
        '''
        self.restore_state()
        self.refresh_ref_attr_val_dict()
        component.enact()
        ravd = self.return_ravd()
        avd = self.return_avd()
        delta_x = delta_dicts(avd, ravd)
        self.first_order_component_data[component.object_id] = [ravd, avd, delta_x]


    def first_order_data(self, list_of_components):
        '''\
            Record the summary of the changes to the state imposed by each component
            as applied to the original state.
        '''
        self.store_state()
        self.first_order_component_data.clear()
        self.refresh_components(list_of_components)

        for component in list_of_components:
            self.first_order_data_(component)
        self.restore_state()


    def second_order_data_(self, pair, state_to_load):
        '''\
            pair is a 2-tuple where:
                pair[0] is the effect component whose application to the base state gave rise to the
                attribute value dictionary passed to state_to_load; and,
                pair[1] is a distinct effect component waiting to be applied.
            This method computes and stores the impact on attribute values of Modifiables affected
            by applying the second effect component after having applied the first effect component,
            but instead of recomputing the impact of the first effect component's application, just
            retrieves the value cached when first order data was computed.
        '''
        self.load_state(state_to_load)
        self.refresh_ref_attr_val_dict()
        if pair[1].valid:
            pair_1_depends_on_pair_0 = False
        else:
            pair_1_depends_on_pair_0 = True

        # Ensure that pair[1]'s selectable object cache has been refreshed in the event it is unlockable.
        if not(pair[1].is_marker_effect_component):
            pair[1].reference_effect.refresh_selectable_objects_cache()

        pair[1].enact()
        ravd = self.return_ravd()
        avd = self.return_avd()
        delta_x = delta_dicts(avd, ravd)
        self.second_order_component_data[(pair[0].object_id, pair[1].object_id)] = [ravd, avd, delta_x, pair_1_depends_on_pair_0]



    def second_order_data(self, list_of_pairs):
        '''\
            Record the summary of the changes to the state imposed by the second component
            in each pair as applied to the state derived following application of the first
            component in each pair.
        '''
        self.second_order_component_data.clear()
        for pair in list_of_pairs:
            A = pair[0]
            id_A = A.object_id
            XA = self.first_order_component_data[id_A][1]
            self.second_order_data_(pair, state_to_load=XA)
        self.restore_state()


    def third_order_data(self):
        '''\
            Solve for pairwise dependency between components on the basis of:
                b(a(x)) == a(b(x))              |=>     No dependency
                d(XAB, XA) != d(XB, X)          |=>     B depends on A
                d(XBA, XB) != d(XA, X)          |=>     A depends on B

                b exists in X but not XA        |=>     B depends on A
                a exists in X but not XB        |=>     A depends on B

            This information is used to construct the digraph used for sorting
            the effect components.
        '''
        edge_set = set()
        used_key_pairs = set()

        for key in self.second_order_component_data:
            skey = tuple(sorted(key))

            if not(skey in used_key_pairs):
                used_key_pairs.add(skey)
                reversed_key = (key[1], key[0])

                a_on_b = False
                b_on_a = False

                # Detect dependency on the basis that one effect component's application alters the
                # game state such that the other effect ceases to exist.
                b_stops_existing_after_a = self.second_order_component_data[key][-1]
                a_stops_existing_after_b = self.second_order_component_data[reversed_key][-1]

                if b_stops_existing_after_a:
                    b_on_a = True

                if a_stops_existing_after_b:
                    a_on_b = True

                # Detect dependency on the basis that the impact of one effect component in terms of
                # what it affects or how it affects what it affects varies as a function of being applied
                # before or after a different effect component; in other words, A and B do not commute
                # when applied to X.
                id_A = key[0]
                id_B = key[1]

                XAB = self.second_order_component_data[key][1]
                XBA = self.second_order_component_data[reversed_key][1]

                if (XAB != XBA):
                    d_XAB_XA = self.second_order_component_data[key][2]
                    d_XB_X = self.first_order_component_data[key[1]][2]
                    d_XBA_XA = self.second_order_component_data[reversed_key][2]
                    d_XA_X = self.first_order_component_data[key[0]][2]

                    if (d_XAB_XA != d_XB_X):
                        # B's impact is dependent on the timing of A's impact; and,
                        # B does not cause A to stop existing.
                        if not(a_stops_existing_after_b):
                            b_on_a = True

                    if (d_XBA_XA != d_XA_X):
                        # A's impact is dependent on the timing of A's impact; and,
                        # A does not cause B to stop existing.
                        if not(b_stops_existing_after_a):
                            a_on_b = True

                    if a_on_b:
                        # If component A depends on component B, then, absent a dependency loop,
                        # it must wait for B to be applied before it can be applied; this constraint
                        # on application order is represented in the digraph by an edge from B to A.
                        edge_set.add(reversed_key)

                    if b_on_a:
                        # If component B depends on component A, then, absent a dependency loop,
                        # it must wait for A to be applied before it can be applied; this constraint
                        # on application order is represented in the digraph by an edge from A to B.
                        edge_set.add(key)

        return edge_set


    def determine_raw_edges(self, list_of_components):
        '''\
            Return a set of tuples where each tuple represents the source vertex and the target vertex of a
            directed edge in a directed graph which symbolizes the dependency of the target component on the
            source component.
        '''
        component_indices = [n for n in range(len(list_of_components))]

        # NOTE #
        # Edges are sorted so that they are added to the graph in the order implied by the presort.
        # This step avoids the need to check if successors of a given component are sorted before applying
        # them whenever more than one of a component's successors become independent immediately following
        # its application.
        edge_sort_dict = {}
        for i in range(len(list_of_components)):
            edge_sort_dict[list_of_components[i].object_id] = i

        pairs = pairs_to_consider(component_indices)

        true_pairs = []
        for pair in pairs:
            true_pair = (list_of_components[pair[0]], list_of_components[pair[1]])
            true_pairs.append(true_pair)

        self.first_order_data(list_of_components)
        self.refresh_components(list_of_components)
        self.second_order_data(true_pairs)
        self.refresh_components(list_of_components)
        set_of_edges = self.third_order_data()
        return sorted(set_of_edges, key=lambda x: (edge_sort_dict[x[0]], edge_sort_dict[x[1]]))


    def return_edges_to_remove(self, vertices):
        '''\
            Auxillary function assisting in the removal of simple cycles.
        '''
        result = []
        # Add the link from the final vertex to the first vertex
        result.append((vertices[-1], vertices[0]))
        n_vertices_ = len(vertices) - 1
        for i in range(n_vertices_):
            result.append((vertices[i], vertices[i+1]))
        return result


    def remove_simple_cycles(self, graph):
        '''\
            Dependency loops cancel out. Directed graphs must be acyclic to be
            topologically sorted. For consistency, detect all simple cycles before
            removing each of them to render the graph acyclic; otherwise, the end
            result could vary depending on the order that simple cycles were detected.
            # NOTE # networkx uses Johnson's algorithm for detecting simple cycles.
        '''
        removed_edges = set()
        simple_cycles = nx.simple_cycles(graph)
        if simple_cycles:
            for cycle in simple_cycles:
                edges_to_remove = self.return_edges_to_remove(cycle)
                for edge_to_remove in edges_to_remove:
                    if not(edge_to_remove in removed_edges):
                        removed_edges.add(edge_to_remove)
                        graph.remove_edge(*edge_to_remove)
        return graph


    def generate_dependency_graph(self, component_indices, edges_to_add):
        dependency_graph = nx.DiGraph()
        dependency_graph.add_nodes_from(component_indices)
        for edge_to_add in edges_to_add:
            dependency_graph.add_edge(*edge_to_add)
        return dependency_graph


    def presort(self, components):
        '''\
            Return components in the order they should be applied if dependency was
            irrelevant---i.e., according to timestamp, and, for components from
            the same effect, the order they appear in that effect's rules text relative
            to one another.
        '''
        return sorted(components, key=lambda x: (x.timestamp, x.relative_component_ordinal))


    def solve_sort(self, sublayer_of_components):
        # Case #
        # There is only one component; no need to sort.
        n_components = len(sublayer_of_components)
        if (n_components == 1):
            sublayer_of_components[0].enact(lock=True)

        # Case #
        # At least two components. Sort them according to timestamp and relative component ordinal.
        else:
            presorted_components = self.presort(sublayer_of_components)
            raw_dependencies = self.determine_raw_edges(presorted_components)

            # Case #
            # No dependencies detected; order of application given by presort.
            if not(raw_dependencies):
                for component in presorted_components:
                    component.enact(lock=True)

            # Case #
            # Preliminary dependencies detected. Generate the corresponding directed graph using the
            # ids of components as vertices.
            else:
                component_ids = [component.object_id for component in presorted_components]
                dependency_graph = self.generate_dependency_graph(component_ids, raw_dependencies)

                # Detect dependency loops in the dependency graph and remove them.
                dag = self.remove_simple_cycles(dependency_graph)

                # Case #
                # Rendering the graph acyclic removed all of the edges; no need for
                # topological sort, order of application is given by presort.
                if not(len(dag.edges)):
                    for component in presorted_components:
                        component.enact(lock=True)

                # Case #
                # Topological sort of dag required.
                else:
                    components_by_id = {component.object_id:component for component in presorted_components}
                    # Assumption: successors of any node will retain their relative
                    # order according to the presort, so that in cases where multiple
                    # dependent effects become independent following the removal of a shared
                    # predecessor, the rule that they apply in relative timestamp order is obeyed.
                    # Edges are sorted before adding them to the graph such that the successors of
                    # a given node are added in relative timestamp order according to the presort.
                    # This choice guarantees that the assumption will hold because dag.successors(...) returns
                    # successors in the order they were added to the graph.

                    # successor_data is a dictionary with keys == component_ids used as vertices in the graph,
                    # and each value == an iterator over the given component's successor component_ids (in presort order).
                    successor_data = {component_id:dag.successors(component_id) for component_id in component_ids}

                    # indegree_data is a dictionary with keys == component_ids used as vertices in the graph,
                    # and values == integers counting the indegree of the corresponding vertex.
                    indegree_data = dict(dag.in_degree(component_ids))

                    ids_to_sort = set(component_ids)

                    def get_next_independent_id():
                        # Despite being a set, indices_to_sort will maintain the
                        # relative order of its elements even after elements are
                        # removed. This order matches the initial presort.
                        for component_id in ids_to_sort:
                            if not(indegree_data[component_id]):
                                return component_id

                    def add_independent(independent_component):
                        # Remove the component from the remaining pool of components to sort.
                        # If it is valid, enact it; in either case, update successor indegrees.
                        # To obey 613.8b: immediately enact components which become independent upon the
                        # application of this component. If multiple components become independent
                        # in this way, enact them in relative presort order; and, react to dependent descendents
                        # becoming independent recursively, since they wait to apply until just after the last effect
                        # upon which they depend is applied. Any successor which becomes independent due to the
                        # removal of this component from the dag due to it being invalid waits its turn instead.
                        ids_to_sort.remove(independent_component.object_id)
                        ic_valid = independent_component.valid
                        if ic_valid:
                            independent_component.enact(lock=True)
                        successors = successor_data[independent_component.object_id]
                        for successor_id in successors:
                            indegree_data[successor_id] -= 1
                            if ic_valid:
                                if not(indegree_data[successor_id]):
                                    successor_component = components_by_id[successor_id]
                                    add_independent(successor_component)

                    while ids_to_sort:
                        next_independent_id = get_next_independent_id()
                        add_independent(components_by_id[next_independent_id])


APPARENT_X = ApparentStateHandler()
