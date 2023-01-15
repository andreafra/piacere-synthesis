from z3 import *

from synthesis.requirements import init_requirements
from termcolor import colored, cprint
from synthesis.setup import setup
from synthesis.solver import solve
from synthesis.tests import run_tests
from synthesis.types import State

MM_FILE = './assets/metamodels/doml_meta_v2.0.yaml'

# IM_FILE = './assets/doml/2.0/nginx-openstack_v2.0.yaml'
# IM_FILE = './assets/doml/2.0/nginx-openstack_v2.0_double_vm.yaml'
IM_FILE = './assets/doml/2.0/nginx-openstack_v2.0_wrong_vm_iface.yaml'


def main():

    state = State()

    state.apply(
        setup,
        metamodel_path=MM_FILE,
        doml_path=IM_FILE,
    ).apply(
        solve,
        requirements=init_requirements
    ).apply(
        run_tests
    ).apply(
        check_synth_results
    )


def check_synth_results(state: State):
    # Make sure we have a model!
    state.solver.check()
    model = state.solver.model()

    # Quick testing of synthetized values

    print('Values of \'vm1\' that have an associated value (cpu_count)')
    vm1 = state.data.Elems['elem_139682454814288']
    vm1_cpu_count = model.eval(
        state.rels.int.AttrValueRel(
            vm1.ref,
            state.data.Attrs['infrastructure_ComputingNode::cpu_count'].ref)).as_long()
    print(vm1.name, vm1_cpu_count)
    assert vm1_cpu_count > 4

    # A value that is not assigned by anything is equal to 2???
    print('Attribute of \'vm1\' that does not have an associated value (e.g. cost)')
    vm_cost_value = model.eval(state.rels.int.AttrValueRel(
        vm1.ref, state.data.Attrs['infrastructure_ComputingNode::cost'].ref))
    print(vm_cost_value)

    # Works only if we have unbound elems!

    # For each unbound variable, print the assigned values for each attribute (of type Integer)
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
                    elem_dest_k = colored(
                        elem_dest_k, on_color="on_yellow")
                _class, _assoc = assoc_k.split("::")
                _assoc = colored(_assoc, "blue")
                elem_dest_k = colored(elem_dest_k, "yellow")

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
