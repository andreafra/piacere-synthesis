import yaml
from z3 import *

from src.requirements import builtin_requirements
from src.results import save_results
from src.data import init_data
from src.solver import solve
from src.types import State
from tests.requirements_bucket import req_all_iface_have_net

MM_FILE = './assets/metamodels/doml_meta_v2.0.yaml'
IM_FILE = './assets/doml/2.0/nginx-openstack_v2.0_wrong_vm_iface.yaml'

with open(MM_FILE, 'r') as mm_file:
    mm = yaml.safe_load(mm_file)
with open(IM_FILE, 'r') as im_file:
    im = yaml.safe_load(im_file)

# vm <-->
#         iface (ub) <--> net (ub)
# sg <-->


def test_vm_no_iface_and_net():
    state = State()
    state = init_data(state, mm, im)
    state = solve(state, requirements=[
                  builtin_requirements, req_all_iface_have_net])
    state = save_results(state)

    ub_elems = [v for v in state.data.Elems.values() if v.unbound]
    assert len(ub_elems) == 2

    model = state.solver.model()

    # Check the class of the unbound elements

    ub_iface = [ub for ub in ub_elems if model.eval(state.rels.ElemClass(
        ub.ref)) == state.data.Classes['infrastructure_NetworkInterface'].ref]

    ub_net = [ub for ub in ub_elems if model.eval(state.rels.ElemClass(
        ub.ref)) == state.data.Classes['infrastructure_Network'].ref]

    assert len(ub_iface) == 1
    assert len(ub_net) == 1

    ub_iface = ub_iface[0]
    ub_net = ub_net[0]

    assert model.eval(state.rels.AssocRel(
        state.data.Elems['elem_139682454814288'].ref,  # vm
        state.data.Assocs['infrastructure_ComputingNode::ifaces'].ref,
        ub_iface.ref,
    ))
    assert model.eval(state.rels.AssocRel(
        ub_iface.ref,
        state.data.Assocs['infrastructure_NetworkInterface::belongsTo'].ref,
        ub_net.ref,
    ))
