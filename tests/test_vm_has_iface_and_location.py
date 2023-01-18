import yaml
from z3 import *

from src.requirements import builtin_requirements
from src.results import save_results
from src.setup import init_data
from src.solver import solve
from src.types import State
from tests.requirements_bucket import req_all_vm_have_location

MM_FILE = './assets/metamodels/doml_meta_v2.0.yaml'
IM_FILE = './assets/doml/2.0/nginx-openstack_v2.0_wrong_vm_iface.yaml'

with open(MM_FILE, 'r') as mm_file:
    mm = yaml.safe_load(mm_file)
with open(IM_FILE, 'r') as im_file:
    im = yaml.safe_load(im_file)

#    <--> iface (ub)
# vm
#    <--> location (ub)


def test_vm_has_iface_and_location():
    state = State()
    state = init_data(state, mm, im)
    state = solve(state, requirements=[
                  builtin_requirements, req_all_vm_have_location])
    state = save_results(state)

    ub_elems = [v for v in state.data.Elems.values() if v.unbound]
    assert len(ub_elems) == 2

    model = state.solver.model()

    # Check the class of the unbound elements

    ub_iface = [ub for ub in ub_elems if model.eval(state.rels.ElemClass(
        ub.ref)) == state.data.Classes['infrastructure_NetworkInterface'].ref]

    ub_loc = [ub for ub in ub_elems if model.eval(state.rels.ElemClass(
        ub.ref)) == state.data.Classes['infrastructure_Location'].ref]

    assert len(ub_iface) == 1
    assert len(ub_loc) == 1

    ub_iface = ub_iface[0]
    ub_loc = ub_loc[0]

    vm = state.data.Elems['elem_139682454814288'].ref

    assert model.eval(state.rels.AssocRel(
        vm,
        state.data.Assocs['infrastructure_ComputingNode::ifaces'].ref,
        ub_iface.ref,  # iface
    ))
    assert model.eval(state.rels.AssocRel(
        vm,
        state.data.Assocs['infrastructure_ComputingNode::location'].ref,
        ub_loc.ref,  # iface
    ))
