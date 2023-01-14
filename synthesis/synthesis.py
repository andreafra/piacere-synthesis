from z3 import *

from synthesis.requirements import init_requirements
from synthesis.results import parse_synthesis_result
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
    print("\nUnbound Elements")
    for ub_elem_k, ub_elem_v in [(k, v) for k, v in state.data.Elems.items() if v.unbound]:
        ub_elem_class = str(model.eval(state.rels.ElemClass(ub_elem_v.ref)))
        print(f'{ub_elem_k}\t{ub_elem_class}')
        for ub_elem_attr_k, ub_elem_attr_v in state.data.Classes[ub_elem_class].attributes.items():
            if ub_elem_attr_v['type'] == 'Integer':
                value = str(model.eval(state.rels.int.AttrValueRel(
                    ub_elem_v.ref, state.data.Attrs[ub_elem_attr_k].ref)))
                synthetized = str(model.eval(state.rels.int.AttrSynthRel(
                    ub_elem_v.ref, state.data.Attrs[ub_elem_attr_k].ref)))
                print(f'\t\t{ub_elem_attr_k}\t{value}\t{synthetized}')

    # For each unbound variable, print the assigned values for each attribute (of type Integer)
    print("\nExisting Elements for which an attribute has been synthetized")
    for elem_k, elem_v in [(k, v) for k, v in state.data.Elems.items() if not v.unbound]:
        elem_class = str(model.eval(state.rels.ElemClass(elem_v.ref)))
        print(f'{elem_k}\t{elem_class}')
        for elem_attr_k, elem_attr_v in state.data.Classes[elem_class].attributes.items():
            if elem_attr_v['type'] == 'Integer':
                value = str(model.eval(state.rels.int.AttrValueRel(
                    elem_v.ref, state.data.Attrs[elem_attr_k].ref)))
                synthetized = str(model.eval(state.rels.int.AttrSynthRel(
                    elem_v.ref, state.data.Attrs[elem_attr_k].ref)))
                print(f'\t\t{elem_attr_k}\t{value}\t{synthetized}')

    return state
