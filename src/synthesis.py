import yaml

from z3 import *

from src.requirements import init_requirements
from src.results import check_synth_results, save_results
from src.setup import init_data
from src.solver import solve
from src.tests import run_tests
from src.types import State

MM_FILE = './assets/metamodels/doml_meta_v2.0.yaml'

# IM_FILE = './assets/doml/2.0/nginx-openstack_v2.0.yaml'
# IM_FILE = './assets/doml/2.0/nginx-openstack_v2.0_double_vm.yaml'
IM_FILE = './assets/doml/2.0/nginx-openstack_v2.0_wrong_vm_iface.yaml'


def main():

    with open(MM_FILE, 'r') as mm_file:
        mm = yaml.safe_load(mm_file)
    with open(IM_FILE, 'r') as im_file:
        im = yaml.safe_load(im_file)

    state = State()

    state.apply(
        init_data,
        metamodel=mm,
        doml=im,
    ).apply(
        solve,
        requirements=init_requirements
    ).apply(
        run_tests
    ).apply(
        check_synth_results
    ).apply(
        save_results
    ).apply(
        lambda state: print(state.solver.statistics())
    )