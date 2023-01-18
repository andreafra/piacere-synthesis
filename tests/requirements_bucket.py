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
    stmt = ForAll(
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
    state.solver.assert_and_track(stmt, "vm_iface_endpoint")
    return state


def req_all_iface_have_net(state: State):
    iface, net = Consts('iface net', state.sorts.Elem)
    # all ifaces must have an associated network
    # and for easy testing let's say that the Network must not the the one in the doml
    # net1 = elem_139682454813520
    stmt = ForAll(
        [iface],
        Implies(
            state.rels.ElemClass(
                iface) == state.data.Classes["infrastructure_NetworkInterface"].ref,
            Exists(
                [net],
                And(
                    state.rels.ElemClass(
                        net) == state.data.Classes["infrastructure_Network"].ref,  # we need this else the req fails to produce the correct output
                    state.rels.AssocRel(
                        iface, state.data.Assocs["infrastructure_NetworkInterface::belongsTo"].ref, net),
                    net != state.data.Elems['elem_139682454813520'].ref
                )
            )
        )
    )
    state.solver.assert_and_track(stmt, "vm_iface_network")
    return state


def req_all_vm_have_location(state: State):
    vm, loc = Consts('vm loc', state.sorts.Elem)
    # all ifaces must have an associated network
    # and for easy testing let's say that the Network must not the the one in the doml
    # net1 = elem_139682454813520
    stmt = ForAll(
        [vm],
        Implies(
            state.rels.ElemClass(
                vm) == state.data.Classes["infrastructure_VirtualMachine"].ref,
            Exists(
                [loc],
                And(
                    # state.rels.ElemClass(
                    #     loc) == state.data.Classes["infrastructure_Location"].ref, # uncommenting this make the solver VERY SLOW!
                    state.rels.AssocRel(
                        vm, state.data.Assocs["infrastructure_ComputingNode::location"].ref, loc),
                )
            )
        )
    )
    state.solver.assert_and_track(stmt, "vm_location")
    return state


def req_exist_storage(state: State):
    # There must be at least 1 storage
    sto = Const('sto', state.sorts.Elem)
    req_storage = Exists(
        [sto],
        state.rels.ElemClass(
            sto) == state.data.Classes["infrastructure_Storage"].ref,
    )
    state.solver.assert_and_track(req_storage, "req_storage")
    return state


def req_storage_has_iface(state: State):
    sto, sto_iface = Consts('sto sto_iface', state.sorts.Elem)
    req = ForAll(
        [sto],
        Implies(
            And(

                state.rels.ElemClass(
                    sto) == state.data.Classes["infrastructure_Storage"].ref,
            ),
            Exists(
                [sto_iface],
                And(
                    state.rels.ElemClass(
                        sto_iface) == state.data.Classes["infrastructure_NetworkInterface"].ref,
                    state.rels.AssocRel(
                        sto, state.data.Assocs["infrastructure_Storage::ifaces"].ref, sto_iface)
                )
            )
        )
    )
    state.solver.assert_and_track(req, "req_storage_iface")
    return state
