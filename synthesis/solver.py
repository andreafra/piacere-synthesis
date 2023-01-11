# Here we define the Sorts of Elements and Associations as Enums
# (as they are finite), and the relationship between two elements
# as a Function `AssocRel :: ElemSort, AssocSort, ElemSort -> BoolSort`,
# which tells us if two items are in a relationship (returns true) or not.

from itertools import product
from z3 import *
from .types import Sort as DataSort


def Iff(a, b):
    return a == b


def init_solver(
    CLASSES,
    ELEMS,
    ASSOCS,
    ATTRS
):
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
    # (that till now have not been assigned any constraint) have a class
    # enforced onto them if they belong to a certain relationship
    elem_a = Const('elem_a', elem_sort)
    for assoc_k, assoc_v in ASSOCS.items():
        for _, ub_elem in ELEMS.items():
            if ub_elem.unbound:
                s.assert_and_track(
                    ForAll(
                        [elem_a],
                        Implies(
                            assoc_rel(elem_a,  assoc_v.ref, ub_elem.ref),
                            elem_class_fn(ub_elem.ref) == assoc_v.to_elem.ref
                        )
                    ),
                    f'AssocRel_EnforceClass {assoc_k}'
                )

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

    attr_int_value_rel = Function(
        'AttrIntValueRel', elem_sort, attr_sort, IntSort())

    for elem_k, elem_v in ELEMS.items():
        if not elem_v.unbound:
            for attr_k, attr_v in elem_v.attributes.items():
                # print(f'{elem_k}({elem_v.name}):\n\t{attr_k}({ATTRS[attr_k].type}, {ATTRS[attr_k].multiplicity}) = {attr_v[0]}')
                if ATTRS[attr_k].type == 'Integer' and len(attr_v) == 1:
                    s.assert_and_track((
                        attr_int_value_rel(
                            elem_v.ref, ATTRS[attr_k].ref) == attr_v[0]
                    ), f'AttrIntValueRel {elem_k} {attr_k}')

    return (
        s,
        DataSort(
            class_sort,
            elem_sort,
            assoc_sort,
            attr_sort),
        elem_class_fn,
        assoc_rel,
        attr_int_exist_rel,
        attr_int_exist_value_rel,
        attr_int_value_rel,
    )
