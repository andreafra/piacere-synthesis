from z3 import *


def init_requirements(solver, data, data_refs):
    CLASSES, ELEMS, ASSOCS, ATTRS = data
    s = solver
    (sort, elem_class_fn,
     assoc_rel,
     attr_int_exist_rel,
     attr_int_exist_value_rel,
     attr_int_value_rel) = data_refs

    vm, iface = Consts("vm iface", sort.Elem)

    req_vm_iface = ForAll(
        [vm],
        Implies(
            elem_class_fn(vm) == CLASSES["infrastructure_VirtualMachine"].ref,
            Exists(
                [iface],
                And(
                    assoc_rel(
                        vm, ASSOCS["infrastructure_ComputingNode::ifaces"].ref, iface)
                )
            )
        )
    )
    s.assert_and_track(req_vm_iface, "vm_iface")

    memory_attr_ref = ATTRS["infrastructure_ComputingNode::memory_mb"].ref
    req_vm_cpucount = ForAll(
        [vm],
        Implies(
            elem_class_fn(vm) == CLASSES["infrastructure_VirtualMachine"].ref,
            And(
                attr_int_exist_rel(vm, memory_attr_ref),
                attr_int_exist_value_rel(vm, memory_attr_ref),
                attr_int_value_rel(vm, memory_attr_ref) == 2048
            )
        )
    )
    s.assert_and_track(req_vm_cpucount, "vm_memory_mb")

    cpu_attr_ref = ATTRS["infrastructure_ComputingNode::cpu_count"].ref
    req_vm_cpucount = ForAll(
        [vm],
        Implies(
            elem_class_fn(vm) == CLASSES["infrastructure_VirtualMachine"].ref,
            And(
                attr_int_exist_rel(vm, cpu_attr_ref),
                # attr_int_exist_value_rel(vm, cpu_attr_ref),
                attr_int_value_rel(vm, cpu_attr_ref) > 4
            )
        )
    )
    s.assert_and_track(req_vm_cpucount, "vm_cpu_count")

    endpoint_attr_ref = ATTRS["infrastructure_NetworkInterface::endPoint"].ref
    req_iface_endpoint = ForAll(
        [iface],
        Implies(
            elem_class_fn(
                iface) == CLASSES["infrastructure_NetworkInterface"].ref,
            And(
                attr_int_exist_rel(iface, endpoint_attr_ref),
                # attr_int_exist_value_rel(vm, cpu_attr_ref),
                attr_int_value_rel(iface, endpoint_attr_ref) >= 16777216
                # 16777216 ==toIP=> 1.0.0.0 first valid IP class-A ip address
            )
        )
    )
    s.assert_and_track(req_iface_endpoint, "vm_iface_endpoint")
