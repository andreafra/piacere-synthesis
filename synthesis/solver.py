# Here we define the Sorts of Elements and Associations as Enums
# (as they are finite), and the relationship between two elements
# as a Function `AssocRel :: ElemSort, AssocSort, ElemSort -> BoolSort`,
# which tells us if two items are in a relationship (returns true) or not.

from itertools import product
from z3 import *

from synthesis.setup import update_unbound_elems
from synthesis.types import Sorts as DataSort, State, IntRels


def Iff(a, b):
    return a == b


def init_solver(
    state: State
):
    CLASSES = state.data.Classes
    ELEMS = state.data.Elems
    ASSOCS = state.data.Assocs
    ATTRS = state.data.Attrs

    # Init Z3 solver
    s = Solver()

    class_sort, classes = EnumSort('Class', list(CLASSES.keys()))
    # Add the Ref to each ELEM
    for c in classes:
        CLASSES[str(c)].ref = c

    elem_sort, elems = EnumSort('Elem', list(ELEMS.keys()))
    for elem in elems:
        ELEMS[str(elem)].ref = elem

    # Where assoc_sort is an EnumSort of all associations names...
    assoc_sort, assocs = EnumSort('Assoc', list(ASSOCS.keys()))
    # Add the Ref to each ASSOC
    for assoc in assocs:
        ASSOCS[str(assoc)].ref = assoc

    attr_sort, attrs = EnumSort('Attr', list(ATTRS.keys()))
    # Add the Ref to each ATTR
    for attr in attrs:
        ATTRS[str(attr)].ref = attr

    # ElemClass(Elem) -> Class
    elem_class_fn = Function('ElemClass', elem_sort, class_sort)

    for _, elem in ELEMS.items():
        if not elem.unbound:
            s.assert_and_track(
                elem_class_fn(elem.ref) == elem.eClass.ref,
                f'ElemClass {elem.id} {elem.eClass.name}'
            )

    # AssocRel(Elem, Assoc, Elem) -> Bool
    assoc_rel = Function('AssocRel', elem_sort,
                         assoc_sort, elem_sort, BoolSort())

    assoc_a = Const('assoc_a', assoc_sort)
    for (_, e1), (_, e2) in product(ELEMS.items(), ELEMS.items()):
        if (not e1.unbound and not e2.unbound):
            stmt = ForAll(
                [assoc_a],
                Iff(
                    assoc_rel(e1.ref, assoc_a, e2.ref),
                    Or(
                        *(
                            assoc_a == ASSOCS[e1_assoc_k].ref
                            for e1_assoc_k, e1_assoc_v in e1.associations.items()
                            if e2.id in e1_assoc_v
                        )
                    )
                )
            )
            s.assert_and_track(stmt, f'AssocRel {e1.id} {e2.id}')

    # The following assertions allow us to ensure that unbound elements
    # (that till now have not been assigned any constraint) have an
    # assigned class if they belong to a certain relationship
    elem_a = Const('elem_a', elem_sort)
    for assoc_k, assoc_v in ASSOCS.items():
        for ub_elem_k, ub_elem_v in ELEMS.items():
            if ub_elem_v.unbound:
                s.assert_and_track(
                    ForAll(
                        [elem_a],
                        Implies(
                            assoc_rel(elem_a,  assoc_v.ref, ub_elem_v.ref),
                            elem_class_fn(ub_elem_v.ref) == assoc_v.to_elem.ref
                        )
                    ),
                    f'AssocRel_EnforceClass {assoc_k} {ub_elem_k}'
                )

    # Attribute relationships

    # AttrIntExistRel(Elem, Attr) -> Bool
    # Tells us if an element has a certain attribute.
    attr_int_exist_rel = Function(
        'AttrIntExistRel', elem_sort, attr_sort, BoolSort())
    elem_a = Const('elem_a', elem_sort)
    attr_a = Const('attr_a', attr_sort)
    for class_k, class_v in CLASSES.items():
        s.assert_and_track((
            ForAll(
                [elem_a],
                Implies(
                    elem_class_fn(elem_a) == class_v.ref,
                    ForAll(
                        [attr_a],
                        Iff(
                            attr_int_exist_rel(elem_a, attr_a),
                            Or(
                                *(
                                    attr_a == ATTRS[i].ref
                                    for i in class_v.attributes.keys()
                                    if ATTRS[i].type == 'Integer'
                                )
                            )
                        )
                    )
                )
            )
        ), f'AttrIntExistRel {class_k}')

    # AttrIntExistValueRel(Elem, Attr) -> Bool
    # Tells us if an element attribute has been assigned a value in the DOML
    attr_int_exist_value_rel = Function(
        'AttrIntExistValueRel', elem_sort, attr_sort, BoolSort())
    attr_a = Const('attr_a', attr_sort)

    for elem_k, elem_v in ELEMS.items():
        if not elem_v.unbound:
            s.assert_and_track((
                ForAll(
                    [attr_a],
                    Iff(
                        attr_int_exist_value_rel(elem_v.ref, attr_a),
                        Or(
                            *(
                                attr_a == ATTRS[eAttr_k].ref
                                for eAttr_k, eAttr_v in elem_v.attributes.items()
                                if ATTRS[eAttr_k].type == 'Integer' and len(eAttr_v) == 1
                            )
                        )
                    )
                )
            ), f'AttrIntExistValueRel {elem_k}')

    # AttrIntValueRel(Elem, Attr) -> Int
    attr_int_value_rel = Function(
        'AttrIntValueRel', elem_sort, attr_sort, IntSort())

    for elem_k, elem_v in ELEMS.items():
        if not elem_v.unbound:
            for attr_k, attr_v in elem_v.attributes.items():
                if ATTRS[attr_k].type == 'Integer' and len(attr_v) == 1:
                    s.assert_and_track((
                        attr_int_value_rel(
                            elem_v.ref, ATTRS[attr_k].ref) == attr_v[0]
                    ), f'AttrIntValueRel {elem_k} {attr_k}')

    # AttrIntSynthRel(Elem, Attr) -> Bool
    # Tells us if the value was assigned during synthesis or not,
    # also, it should default to False
    attr_int_synth_rel = Function(
        'AttrIntSynthRel', elem_sort, attr_sort, BoolSort())

    for elem_k, elem_v in ELEMS.items():
        if not elem_v.unbound:
            for attr_k, attr_v in elem_v.attributes.items():
                if ATTRS[attr_k].type == 'Integer' and len(attr_v) == 1:
                    s.assert_and_track((
                        attr_int_synth_rel(
                            elem_v.ref, ATTRS[attr_k].ref) == True
                    ), f'AttrIntSynthRel {elem_k} {attr_k}')

    state.solver = s
    state.sorts = DataSort(
        class_sort,
        elem_sort,
        assoc_sort,
        attr_sort)

    state.rels.ElemClass = elem_class_fn
    state.rels.AssocRel = assoc_rel

    state.rels.int = IntRels(attr_int_exist_rel,
                             #  attr_int_exist_value_rel,
                             attr_int_value_rel,
                             attr_int_synth_rel)

    return state


def solve(state: State, requirements, max_tries=8):
    tries = 0
    ub_elems = 0

    def prepare_solver():
        return state.apply(
            update_unbound_elems,
            unbound_elems=ub_elems
        ).apply(
            init_solver
        ).apply(
            requirements
        )
    state = prepare_solver()
    while (
        state.solver.check() == unsat
    ):
        if tries >= max_tries:
            raise RuntimeError(
                'Max tries limit exceeded. Could not solve the model.\nTry increasing max_tries')

        tries += 1
        ub_elems = ub_elems * 2 if ub_elems > 0 else 1

        print(f'Solving again with {ub_elems} unbound elems')
        state = prepare_solver()
    print(f'Solved with {ub_elems} unbound elems in {tries} tries')
    return state
