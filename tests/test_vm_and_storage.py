import yaml
from z3 import *

from doml_synthesis.requirements import builtin_requirements
from doml_synthesis.results import save_results
from doml_synthesis.data import init_data
from doml_synthesis.solver import solve
from doml_synthesis.types import State
from tests.requirements_bucket import req_exist_storage, req_storage_has_iface

MM_FILE = './assets/metamodels/doml_meta_v2.0.yaml'
IM_FILE = './assets/doml/2.0/nginx-openstack_v2.0_wrong_vm_iface.yaml'

with open(MM_FILE, 'r') as mm_file:
    mm = yaml.safe_load(mm_file)
with open(IM_FILE, 'r') as im_file:
    im = yaml.safe_load(im_file)

# vm <-> iface (ub) <->
#                       (Something)
# sto (ub) <---------->
#          <----------> concrete_storage (ub)
#


def test_vm_and_storage():
    state = State()
    state = init_data(state, mm, im)
    state = solve(state, requirements=[
                  builtin_requirements,
                  req_exist_storage,
                  req_storage_has_iface])
    state = save_results(state)

    ub_elems = [v for v in state.data.Elems.values() if v.unbound]
    assert len(ub_elems) == 4

    model = state.solver.model()

    # Check the class of the unbound elements

    ub_ifaces = [ub for ub in ub_elems if model.eval(state.rels.ElemClass(
        ub.ref)) == state.data.Classes['infrastructure_NetworkInterface'].ref]

    ub_storage = [ub for ub in ub_elems if model.eval(state.rels.ElemClass(
        ub.ref)) == state.data.Classes['infrastructure_Storage'].ref]

    # Checking concrete storage is more like an unreliable side-effect. We care about the
    # two Network Interfaces, not the mapping, really.
    # ub_concrete_storage = [ub for ub in ub_elems if model.eval(state.rels.ElemClass(
    #     ub.ref)) == state.data.Classes['concrete_Storage'].ref]

    assert len(ub_ifaces) == 2
    assert len(ub_storage) == 1
    # assert len(ub_concrete_storage) == 1

    ub_storage = ub_storage[0]
    # ub_concrete_storage = ub_concrete_storage[0]

    # We're basically using a XOR to check whether vm has an iface in ub_ifaces[0 or 1]
    assert is_true(model.eval(state.rels.AssocRel(
        state.data.Elems['elem_139682454814288'].ref,  # vm
        state.data.Assocs['infrastructure_ComputingNode::ifaces'].ref,
        ub_ifaces[0].ref,
    ))) != is_true(model.eval(state.rels.AssocRel(
        state.data.Elems['elem_139682454814288'].ref,  # vm
        state.data.Assocs['infrastructure_ComputingNode::ifaces'].ref,
        ub_ifaces[1].ref,
    )))
    assert is_true(model.eval(state.rels.AssocRel(
        ub_storage.ref,
        state.data.Assocs['infrastructure_Storage::ifaces'].ref,
        ub_ifaces[0].ref,
    ))) != is_true(model.eval(state.rels.AssocRel(
        ub_storage.ref,
        state.data.Assocs['infrastructure_Storage::ifaces'].ref,
        ub_ifaces[1].ref,
    )))
    # assert is_true(model.eval(state.rels.AssocRel(
    #     ub_concrete_storage.ref,
    #     state.data.Assocs['concrete_Storage::maps'].ref,
    #     ub_storage.ref,
    # )))

    assert any(is_true(model.eval(state.rels.AssocRel(
        ub_ifaces[0].ref,
        state.data.Assocs['infrastructure_NetworkInterface::associated'].ref,
        elem.ref
    ))) == is_true(model.eval(state.rels.AssocRel(
        ub_ifaces[1].ref,
        state.data.Assocs['infrastructure_NetworkInterface::associated'].ref,
        elem.ref))) for elem in state.data.Elems.values())
