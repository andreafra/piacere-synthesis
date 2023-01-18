from termcolor import colored, cprint

from src.types import Elem, State
from z3 import Model


def check_synth_results(state: State):
    """Verifies some conditions and pretty prints the resulting synthesis."""
    # Make sure we have a model!
    model = state.solver.model()

    # Quick testing of synthetized values

    # print('Values of \'vm1\' that have an associated value (cpu_count)')
    # vm1 = state.data.Elems['elem_139682454814288']
    # vm1_cpu_count = model.eval(
    #     state.rels.int.AttrValueRel(
    #         vm1.ref,
    #         state.data.Attrs['infrastructure_ComputingNode::cpu_count'].ref)).as_long()
    # print(vm1.name, vm1_cpu_count)
    # assert vm1_cpu_count > 4

    # # A value that is not assigned by anything is equal to 2???
    # print('Attribute of \'vm1\' that does not have an associated value (e.g. cost)')
    # vm_cost_value = model.eval(state.rels.int.AttrValueRel(
    #     vm1.ref, state.data.Attrs['infrastructure_ComputingNode::cost'].ref))
    # print(vm_cost_value)

    # Works only if we have unbound elems!

    # For each element, print the assigned values for each attribute and associations
    print("\nSynthesis Results: synthetized results have a 'True' at the end of the line")
    for elem_k, elem_v in state.data.Elems.items():
        elem_class = str(model.eval(state.rels.ElemClass(elem_v.ref)))
        cprint(f'{elem_k}\t{elem_class}', "magenta")

        evaluate_associations(state, model, elem_v, elem_class)
        evaluate_attributes(state, model, elem_v, elem_class)

    return state


def evaluate_associations(state, model, elem_v, elem_class):
    for elem_dest_k, elem_dest_v in state.data.Elems.items():
        e1 = elem_v.ref
        e2 = elem_dest_v.ref
        for assoc_k, _ in state.data.Classes[elem_class].associations.items():
            assoc = state.data.Assocs[assoc_k].ref
            if model.eval(state.rels.AssocRel(e1, assoc, e2)):
                if elem_dest_v.unbound:
                    elem_dest_k = colored(elem_dest_k, on_color="on_yellow")
                else:
                    elem_dest_k = colored(elem_dest_k, "yellow")
                _class, _assoc = assoc_k.split("::")
                _assoc = colored(_assoc, "blue")

                print(f'\t\t\t{_class}::{_assoc}\t{elem_dest_k}')


def evaluate_attributes(state, model, elem_v, elem_class):
    for elem_attr_k, elem_attr_v in state.data.Classes[elem_class].attributes.items():
        if elem_attr_v['type'] == 'Integer':
            value = str(model.eval(state.rels.int.AttrValueRel(
                elem_v.ref, state.data.Attrs[elem_attr_k].ref)))
            synthetized = bool(str(model.eval(state.rels.int.AttrSynthRel(
                elem_v.ref, state.data.Attrs[elem_attr_k].ref))) == "True")
            synthetized = colored(
                synthetized, "green" if synthetized else "red")
            _class, _attr = elem_attr_k.split("::")
            _attr = colored(_attr, "cyan")
            value = colored(value, "yellow")
            print(f'\t\t\t{_class}::{_attr}\t{value}\t{synthetized}')


def save_results(state: State):
    """Returns a state with updated attribute and association fields for each element."""
    # Make sure we have a model!
    model = state.solver.model()

    # For each unbound variable, print the assigned values for each attribute (of type Integer)
    for elem_k, elem_v in state.data.Elems.items():
        elem_class = str(model.eval(state.rels.ElemClass(elem_v.ref)))
        if elem_v.unbound:
            elem_v.eClass = elem_class

        update_associations(state, model, elem_v, elem_class)
        update_attributes(state, model, elem_v, elem_class)

    return state


def update_associations(state: State, model: Model, elem_v: Elem, elem_class: str):
    for elem_dest_k, elem_dest_v in state.data.Elems.items():
        e1 = elem_v.ref
        e2 = elem_dest_v.ref
        for assoc_k, _ in state.data.Classes[elem_class].associations.items():
            assoc = state.data.Assocs[assoc_k].ref
            if model.eval(state.rels.AssocRel(e1, assoc, e2)):
                # Add the association into the element data
                if elem_dest_v.unbound:
                    elem_v.associations[assoc_k] = elem_v.associations.get(
                        assoc_k, set())
                    elem_v.associations[assoc_k].add(elem_dest_k)


def update_attributes(state: State, model: Model, elem_v: Elem, elem_class: str):
    for elem_attr_k, elem_attr_v in state.data.Classes[elem_class].attributes.items():
        if elem_attr_v['type'] == 'Integer':
            value = str(model.eval(state.rels.int.AttrValueRel(
                elem_v.ref, state.data.Attrs[elem_attr_k].ref)))
            synthetized = bool(str(model.eval(state.rels.int.AttrSynthRel(
                elem_v.ref, state.data.Attrs[elem_attr_k].ref))) == "True")
            if synthetized:
                elem_v.attributes[elem_attr_k] = [int(value)]
