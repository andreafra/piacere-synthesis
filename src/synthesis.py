import yaml

from z3 import *

from src.requirements import builtin_requirements
from src.results import check_synth_results, save_results
from src.data import init_data
from src.solver import solve
from src.tests import run_tests
from src.types import State
from tests.requirements_bucket import (
    req_exist_storage,
    req_storage_has_iface,
    req_all_iface_have_net,
    req_swcomponent_is_persistent,
    req_vm_has_size_description)

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
        requirements=[builtin_requirements, req_vm_has_size_description],
        strings=["TEST"]
        # ).apply(
        #     run_tests
    ).apply(
        save_results
    ).apply(
        check_synth_results
    )
