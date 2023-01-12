from z3 import *
from .types import State


def init_requirements(state: State):
    CLASSES = state.data.Classes
    ELEMS = state.data.Elems
    ASSOCS = state.data.Assocs
    ATTRS = state.data.Attrs

    vm, iface = Consts("vm iface", state.sorts.Elem)

    req_vm_iface = ForAll(
        [vm],
        Implies(
            state.rels.ElemClass(
                vm) == CLASSES["infrastructure_VirtualMachine"].ref,
            Exists(
                [iface],
                And(
                    state.rels.AssocRel(
                        vm, ASSOCS["infrastructure_ComputingNode::ifaces"].ref, iface)
                )
            )
        )
    )
    state.solver.assert_and_track(req_vm_iface, "vm_iface")

    memory_attr_ref = ATTRS["infrastructure_ComputingNode::memory_mb"].ref
    req_vm_cpucount = ForAll(
        [vm],
        Implies(
            state.rels.ElemClass(
                vm) == CLASSES["infrastructure_VirtualMachine"].ref,
            And(
                state.rels.int.AttrExistRel(vm, memory_attr_ref),
                state.rels.int.AttrExistValueRel(vm, memory_attr_ref),
                state.rels.int.AttrValueRel(vm, memory_attr_ref) == 2048
            )
        )
    )
    state.solver.assert_and_track(req_vm_cpucount, "vm_memory_mb")

    cpu_attr_ref = ATTRS["infrastructure_ComputingNode::cpu_count"].ref
    req_vm_cpucount = ForAll(
        [vm],
        Implies(
            state.rels.ElemClass(
                vm) == CLASSES["infrastructure_VirtualMachine"].ref,
            And(
                state.rels.int.AttrExistRel(vm, cpu_attr_ref),
                # state.rels.int.AttrExistValueRel(vm, cpu_attr_ref),
                state.rels.int.AttrValueRel(vm, cpu_attr_ref) > 4
            )
        )
    )
    state.solver.assert_and_track(req_vm_cpucount, "vm_cpu_count")

    endpoint_attr_ref = ATTRS["infrastructure_NetworkInterface::endPoint"].ref
    req_iface_endpoint = ForAll(
        [iface],
        Implies(
            state.rels.ElemClass(
                iface) == CLASSES["infrastructure_NetworkInterface"].ref,
            And(
                state.rels.int.AttrExistRel(iface, endpoint_attr_ref),
                # state.rels.int.AttrExistValueRel(vm, cpu_attr_ref),
                state.rels.int.AttrValueRel(
                    iface, endpoint_attr_ref) >= 16777216
                # 16777216 ==toIP=> 1.0.0.0 first valid IP class-A ip address
            )
        )
    )
    state.solver.assert_and_track(req_iface_endpoint, "vm_iface_endpoint")

    sto, iface2 = Consts('sto iface2', state.sorts.Elem)
    req_storage = Exists(
        [sto],
        state.rels.ElemClass(sto) == CLASSES["infrastructure_Storage"].ref
    )
    state.solver.assert_and_track(req_storage, "storage_iface")

    return state
