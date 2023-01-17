from z3 import *
from src.types import State


def req_all_vm_have_memory_mb(state: State):
    vm = Const("vm", state.sorts.Elem)

    # all VMs have a memory in mb = 2048
    memory_attr_ref = state.data.Attrs["infrastructure_ComputingNode::memory_mb"].ref
    req_vm_cpucount = ForAll(
        [vm],
        Implies(
            state.rels.ElemClass(
                vm) == state.data.Classes["infrastructure_VirtualMachine"].ref,
            And(
                state.rels.int.AttrExistRel(vm, memory_attr_ref),
                # state.rels.int.AttrExistValueRel(vm, memory_attr_ref),
                state.rels.int.AttrValueRel(vm, memory_attr_ref) == 2048,
                state.rels.int.AttrSynthRel(vm, memory_attr_ref) == True
            )
        )
    )
    state.solver.assert_and_track(req_vm_cpucount, "vm_memory_mb")
    return state


def req_all_vm_have_cpu_count(state: State):
    vm = Const('vm', state.sorts.Elem)

    # all VMs have a cpu_count >= 4
    cpu_attr_ref = state.data.Attrs["infrastructure_ComputingNode::cpu_count"].ref
    req_vm_cpucount = ForAll(
        [vm],
        Implies(
            state.rels.ElemClass(
                vm) == state.data.Classes["infrastructure_VirtualMachine"].ref,
            And(
                state.rels.int.AttrExistRel(vm, cpu_attr_ref),
                # state.rels.int.AttrExistValueRel(vm, cpu_attr_ref),
                state.rels.int.AttrValueRel(vm, cpu_attr_ref) >= 4,
                state.rels.int.AttrSynthRel(vm, cpu_attr_ref) == True
            )
        )
    )
    state.solver.assert_and_track(req_vm_cpucount, "vm_cpu_count")
    return state


def req_all_iface_have_valid_ip(state: State):
    iface = Const('iface', state.sorts.Elem)
    # all ifaces must have a valid IP
    endpoint_attr_ref = state.data.Attrs["infrastructure_NetworkInterface::endPoint"].ref
    req_iface_endpoint = ForAll(
        [iface],
        Implies(
            state.rels.ElemClass(
                iface) == state.data.Classes["infrastructure_NetworkInterface"].ref,
            And(
                state.rels.int.AttrExistRel(iface, endpoint_attr_ref),
                # state.rels.int.AttrExistValueRel(vm, cpu_attr_ref),
                state.rels.int.AttrValueRel(
                    iface, endpoint_attr_ref) >= 16777217,
                state.rels.int.AttrSynthRel(
                    iface, endpoint_attr_ref) == True
                # 16777217 ==toIP=> 1.0.0.1 first valid IP class-A ip address
            )
        )
    )
    state.solver.assert_and_track(req_iface_endpoint, "vm_iface_endpoint")
    return state


def req_exist_storage(state: State):
    # There must be at least 1 storage
    sto = Consts('sto', state.sorts.Elem)
    req_storage = Exists(
        [sto],
        state.rels.ElemClass(
            sto) == state.data.Classes["infrastructure_Storage"].ref
    )
    state.solver.assert_and_track(req_storage, "storage_iface")

    return state
