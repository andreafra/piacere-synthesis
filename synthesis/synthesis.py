from z3 import *

from synthesis.requirements import init_requirements
from synthesis.results import check_synth_results
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
