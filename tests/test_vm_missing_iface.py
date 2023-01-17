import yaml
from z3 import *

from src.requirements import init_requirements
from src.results import save_results
from src.setup import init_data
from src.solver import solve
from src.types import State


def test_vm_missing_iface():

    MM_FILE = './assets/metamodels/doml_meta_v2.0.yaml'
    IM_FILE = './assets/doml/2.0/nginx-openstack_v2.0_wrong_vm_iface.yaml'

    with open(MM_FILE, 'r') as mm_file:
        mm = yaml.safe_load(mm_file)
    with open(IM_FILE, 'r') as im_file:
        im = yaml.safe_load(im_file)

    state = State()

    state = init_data(state, mm, im)
    original = copy.deepcopy(state)
    state = solve(state, requirements=init_requirements)
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
    assert model.eval(state.rels.AssocRel(
        state.data.Elems['elem_139682454814288'].ref,  # vm
        state.data.Assocs['infrastructure_ComputingNode::ifaces'].ref,
        ub_elems[0].ref,  # iface
    ))
    assert model.eval(state.rels.AssocRel(
        state.data.Elems['elem_139682454808208'].ref,  # security group
        state.data.Assocs['infrastructure_SecurityGroup::ifaces'].ref,
        ub_elems[0].ref,  # iface
    ))
