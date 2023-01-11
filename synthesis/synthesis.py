from z3 import *

from synthesis.requirements import init_requirements
from synthesis.setup import setup
from synthesis.solver import init_solver
from synthesis.tests import run_tests
from synthesis.types import AssocRel, AttrRel, Elem, Class, Sort as DataSort

MM_FILE = './assets/metamodels/doml_meta_v2.0.yaml'

# IM_FILE = './assets/doml/2.0/nginx-openstack_v2.0.yaml'
# IM_FILE = './assets/doml/2.0/nginx-openstack_v2.0_double_vm.yaml'
IM_FILE = './assets/doml/2.0/nginx-openstack_v2.0_wrong_vm_iface.yaml'

UB_ELEMS = 0


def main():
    def solve(max_tries=8, _try=0, unbound_elems=0, on_solved=None):
        data = setup(
            metamodel_path=MM_FILE,
            doml_path=IM_FILE,
            unbound_elems=unbound_elems
        )

        s, *data_refs = init_solver(*data)

        run_tests(s, data, data_refs)
        # Congrats! You passed all the tests!

        # Real requirements!
        init_requirements(s, data, data_refs)

        if s.check() == sat:
            print(f'Solved with {unbound_elems} unbound elems')
            if on_solved:
                on_solved(s, data, data_refs)
        elif _try < 8:
            new_ub_elems = unbound_elems * 2 if unbound_elems > 0 else 1
            print(f'Solving again with {new_ub_elems} unbound elems')
            solve(unbound_elems=new_ub_elems,
                  max_tries=max_tries,
                  on_solved=on_solved,
                  _try=_try + 1,
                  )
        else:
            raise RuntimeError(
                'Max tries limit exceeded. Could not solve the model.\nTry increasing max_tries')

    solve(unbound_elems=UB_ELEMS, on_solved=check_synth_results)


def check_synth_results(
    s: Solver,
    data,
    data_refs
):
    CLASSES, ELEMS, ASSOCS, ATTRS = data
    (sort,
     elem_class_fn,
     assoc_rel,
     attr_int_exist_rel,
     attr_int_exist_value_rel,
     attr_int_value_rel) = data_refs

    # Verify some facts about the model
    model = s.model()

    vm = Const('vm', sort.Elem)

    def parse_synthesis_result(res):
        if isinstance(res, ArithRef):
            # if it's more than one element
            if str(res.arg(0)).startswith('Or('):  # UGLY
                elems = [c.arg(1) for c in res.arg(0).children()]
                value = res.arg(1)
                return elems, value.as_long()
            else:
                elem = res.arg(0).arg(1)
                value = res.arg(1)
                return [elem], value.as_long()

    print('Values of \'vm\' that have an associated value (cpu_count)')
    vm_cpu_count_elems, vm_cpu_count_value = parse_synthesis_result(
        model.eval(
            attr_int_value_rel(
                vm, ATTRS['infrastructure_ComputingNode::cpu_count'].ref)))
    print(vm_cpu_count_elems, vm_cpu_count_value)
    assert vm_cpu_count_value > 4

    # A value that is not assigned by anything is equal to 2???
    print('Values of \'vm\' that do not have an associated value (cost)')
    vm_cost_value = model.eval(attr_int_value_rel(
        vm, ATTRS['infrastructure_ComputingNode::cost'].ref))
    print(vm_cost_value)

    # Works only if we have unbound elems!
    elem_ub_0_class = model.eval(elem_class_fn(ELEMS['elem_ub_0'].ref))
    assert elem_ub_0_class == CLASSES['infrastructure_NetworkInterface'].ref

    # Is vm1.ifaces = [elem_ub_0]? Should be TRUE
    assert model.eval(assoc_rel(ELEMS['elem_139682454814288'].ref,
                                ASSOCS['infrastructure_ComputingNode::ifaces'].ref,
                                ELEMS['elem_ub_0'].ref))

    iface = Const('iface', sort.Elem)

    iface_endpoint_elems, iface_endpoint_value = parse_synthesis_result(model.eval(
        attr_int_value_rel(iface, ATTRS["infrastructure_NetworkInterface::endPoint"].ref)))
    print(iface_endpoint_elems, iface_endpoint_value)
    assert iface_endpoint_value >= 16777216
