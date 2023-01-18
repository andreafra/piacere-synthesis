import yaml
from z3 import *

from src.requirements import builtin_requirements
from src.results import save_results
from src.setup import init_data
from src.solver import solve
from src.types import State

# Verifies that no unbound element is produced
# It simply tells us that the model is ok, and returns it


def test_no_synthesis():

    MM_FILE = './assets/metamodels/doml_meta_v2.0.yaml'
    IM_FILE = './assets/doml/2.0/nginx-openstack_v2.0.yaml'

    with open(MM_FILE, 'r') as mm_file:
        mm = yaml.safe_load(mm_file)
    with open(IM_FILE, 'r') as im_file:
        im = yaml.safe_load(im_file)

    state = State()

    state = init_data(state, mm, im)
    original = copy.deepcopy(state)
    state = solve(state, requirements=[builtin_requirements])
    state = save_results(state)

    for ek, ev in original.data.Elems.items():
        for attrk, attrv in ev.attributes.items():
            assert len(attrv) == len(state.data.Elems[ek].attributes[attrk])
        for assock, assocv in ev.associations.items():
            assert len(assocv) == len(
                state.data.Elems[ek].associations[assock])

    ub_elems = [v for v in state.data.Elems.values() if v.unbound]
    assert len(ub_elems) == 0
