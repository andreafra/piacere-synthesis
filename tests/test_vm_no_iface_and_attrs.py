import yaml
from z3 import *

from doml_synthesis.requirements import builtin_requirements
from doml_synthesis.results import save_results
from doml_synthesis.data import init_data
from doml_synthesis.solver import solve
from doml_synthesis.types import State
from tests.requirements_bucket import req_all_vm_have_cpu_count, req_swcomponent_is_persistent, req_vm_has_size_description

MM_FILE = './assets/metamodels/doml_meta_v2.0.yaml'
IM_FILE = './assets/doml/2.0/nginx-openstack_v2.0_wrong_vm_iface.yaml'

with open(MM_FILE, 'r') as mm_file:
    mm = yaml.safe_load(mm_file)
with open(IM_FILE, 'r') as im_file:
    im = yaml.safe_load(im_file)

# vm <-->
#         iface (ub) --> Attrs
# sg <-->

# Attrs:
# infrastructure_ComputingNode::cpu_count (int) >= 4
# application_SoftwareComponent::isPersistent == True


def test_vm_missing_iface_and_cpu_count():
    state = State()
    state = init_data(state, mm, im)
    original = copy.deepcopy(state)
    state = solve(state,
                  requirements=[
                      builtin_requirements,
                      req_all_vm_have_cpu_count,
                      req_swcomponent_is_persistent,
                      req_vm_has_size_description
                  ],
                  strings=["TEST"])
    state = save_results(state)

    for ek, ev in original.data.Elems.items():
        for attrk, attrv in ev.attributes.items():
            assert len(attrv) == len(state.data.Elems[ek].attributes[attrk])
        for assock, assocv in ev.associations.items():
            assert len(assocv) == len(
                state.data.Elems[ek].associations[assock])

    ub_elems = [v for v in state.data.Elems.values() if v.unbound]
    assert len(ub_elems) == 1

    model = state.solver.model()
    ub_elem_class = str(model.eval(state.rels.ElemClass(ub_elems[0].ref)))
    assert ub_elem_class == 'infrastructure_NetworkInterface'
    assert is_true(model.eval(state.rels.AssocRel(
        state.data.Elems['elem_139682454814288'].ref,  # vm
        state.data.Assocs['infrastructure_ComputingNode::ifaces'].ref,
        ub_elems[0].ref,  # iface
    )))
    assert is_true(model.eval(state.rels.AssocRel(
        state.data.Elems['elem_139682454808208'].ref,  # security group
        state.data.Assocs['infrastructure_SecurityGroup::ifaces'].ref,
        ub_elems[0].ref,  # iface
    )))
    # Test Int
    assert model.eval(state.rels.int.AttrValueRel(
        state.data.Elems['elem_139682454814288'].ref,  # vm
        state.data.Attrs['infrastructure_ComputingNode::cpu_count'].ref)).as_long() >= 4
    # Test Bool
    assert is_true(model.eval(state.rels.bool.AttrValueRel(
        state.data.Elems['elem_139682454812560'].ref,  # sw component
        state.data.Attrs['application_SoftwareComponent::isPersistent'].ref)))
    # Test String
    assert (model.eval(state.rels.str.AttrValueRel(
        state.data.Elems['elem_139682454814288'].ref,  # sw component
        state.data.Attrs['infrastructure_VirtualMachine::sizeDescription'].ref))) == state.data.Strings["TEST"]
