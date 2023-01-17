from z3 import *
from src.types import State


def builtin_requirements(state: State):
    CLASSES = state.data.Classes
    ASSOCS = state.data.Assocs

    ELEMSORT = state.sorts.Elem

    def vm_iface() -> ExprRef:
        vm, iface = Consts("vm iface", ELEMSORT)
        return ForAll(
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

    def software_package_iface_net() -> ExprRef:
        asc_consumer, asc_exposer, siface, net, net_iface, cnode, cdeployment, enode, edeployment, vm, dc = Consts(
            "asc_consumer asc_exposer siface net net_iface cnode cdeployment enode edeployment vm dc", ELEMSORT)
        return ForAll(
            [asc_consumer, asc_exposer, siface],
            Implies(
                And(
                    state.rels.AssocRel(
                        asc_consumer, ASSOCS["application_SoftwareComponent::exposedInterfaces"].ref, siface),
                    state.rels.AssocRel(
                        asc_exposer, ASSOCS["application_SoftwareComponent::consumedInterfaces"].ref, siface),
                ),
                Exists(
                    [cdeployment, cnode, edeployment, enode, net],
                    And(
                        state.rels.AssocRel(
                            cdeployment, ASSOCS["commons_Deployment::component"].ref, asc_consumer),
                        state.rels.AssocRel(
                            cdeployment, ASSOCS["commons_Deployment::node"].ref, cnode),
                        Exists(
                            [vm, net_iface],
                            Or(
                                And(  # asc_consumer is deployed on a component with an interface in network n
                                    state.rels.AssocRel(
                                        cnode, ASSOCS["infrastructure_ComputingNode::ifaces"].ref, net_iface),
                                    state.rels.AssocRel(
                                        net_iface, ASSOCS["infrastructure_NetworkInterface::belongsTo"].ref, net),
                                ),
                                And(  # asc_consumer is deployed on a container hosted in a VM with an interface in network n
                                    state.rels.AssocRel(
                                        cnode, ASSOCS["infrastructure_Container::hosts"].ref, vm),
                                    state.rels.AssocRel(
                                        vm, ASSOCS["infrastructure_ComputingNode::ifaces"].ref, net_iface),
                                    state.rels.AssocRel(
                                        net_iface, ASSOCS["infrastructure_NetworkInterface::belongsTo"].ref, net),
                                ),
                                And(  # asc_consumer is deployed on a VM in an AutoScalingGroup with an interface in network n
                                    state.rels.AssocRel(
                                        cnode, ASSOCS["infrastructure_AutoScalingGroup::machineDefinition"].ref, vm),
                                    state.rels.AssocRel(
                                        vm, ASSOCS["infrastructure_ComputingNode::ifaces"].ref, net_iface),
                                    state.rels.AssocRel(
                                        net_iface, ASSOCS["infrastructure_NetworkInterface::belongsTo"].ref, net),
                                ),
                            )
                        ),
                        state.rels.AssocRel(
                            edeployment, ASSOCS["commons_Deployment::component"].ref, asc_exposer),
                        state.rels.AssocRel(
                            edeployment, ASSOCS["commons_Deployment::node"].ref, enode),
                        Exists(
                            [vm, net_iface],
                            Or(
                                And(  # asc_exposer is deployed on a component with an interface in network n
                                    state.rels.AssocRel(
                                        enode, ASSOCS["infrastructure_ComputingNode::ifaces"].ref, net_iface),
                                    state.rels.AssocRel(
                                        net_iface, ASSOCS["infrastructure_NetworkInterface::belongsTo"].ref, net),
                                ),
                                And(  # asc_exposer is deployed on a container hosted on a VM with an interface in network n
                                    state.rels.AssocRel(
                                        enode, ASSOCS["infrastructure_Container::hosts"].ref, vm),
                                    state.rels.AssocRel(
                                        vm, ASSOCS["infrastructure_ComputingNode::ifaces"].ref, net_iface),
                                    state.rels.AssocRel(
                                        net_iface, ASSOCS["infrastructure_NetworkInterface::belongsTo"].ref, net),
                                ),
                                And(  # asc_exposer is deployed on a VM in an AutoScalingGroup with an interface in network n
                                    state.rels.AssocRel(
                                        enode, ASSOCS["infrastructure_AutoScalingGroup::machineDefinition"].ref, vm),
                                    state.rels.AssocRel(
                                        vm, ASSOCS["infrastructure_ComputingNode::ifaces"].ref, net_iface),
                                    state.rels.AssocRel(
                                        net_iface, ASSOCS["infrastructure_NetworkInterface::belongsTo"].ref, net),
                                ),
                            )
                        )
                    )
                )
            )
        )

    # Is it correct?
    def iface_uniq() -> ExprRef:
        def any_iface(elem, iface):
            ifaces_assocs = [
                "infrastructure_ComputingNode::ifaces",
                "infrastructure_Storage::ifaces",
                "infrastructure_FunctionAsAService::ifaces"
            ]
            return Or(*(state.rels.AssocRel(elem, ASSOCS[assoc_name].ref, iface) for assoc_name in ifaces_assocs))

        e1, e2, ni = Consts("e1 e2 i", ELEMSORT)
        return ForAll(
            [e1, e2, ni],
            Implies(
                And(any_iface(e1, ni), any_iface(e2, ni)),
                e1 == e2
            )
        )

    def all_SoftwareComponents_deployed() -> ExprRef:
        sc, deployment, ielem = Consts("sc deployment ielem", ELEMSORT)
        return ForAll(
            [sc],
            Implies(
                state.rels.ElemClass(
                    sc) == CLASSES["application_SoftwareComponent"].ref,
                Exists(
                    [deployment, ielem],
                    And(
                        state.rels.AssocRel(
                            deployment, ASSOCS["commons_Deployment::component"].ref, sc),
                        state.rels.AssocRel(
                            deployment, ASSOCS["commons_Deployment::node"].ref, ielem),
                    )
                )
            )
        )

    def all_infrastructure_elements_deployed() -> ExprRef:
        def checkOneClass(ielem, concr, provider, celem, ielemClass, providerAssoc, celemAssoc):
            return Implies(
                state.rels.ElemClass(ielem) == CLASSES[ielemClass].ref,
                Exists(
                    [provider, celem],
                    And(
                        state.rels.AssocRel(
                            concr, ASSOCS["concrete_ConcreteInfrastructure::providers"].ref, provider),
                        state.rels.AssocRel(
                            provider, ASSOCS[providerAssoc].ref, celem),
                        state.rels.AssocRel(
                            celem, ASSOCS[celemAssoc].ref, ielem)
                    )
                )
            )

        ielem, concr, provider, celem = Consts(
            "ielem concr provider celem", ELEMSORT)
        return Exists(
            [concr],
            And(
                state.rels.ElemClass(
                    concr) == CLASSES["concrete_ConcreteInfrastructure"].ref,
                ForAll(
                    [ielem],
                    And(
                        checkOneClass(
                            ielem, concr, provider, celem,
                            "infrastructure_VirtualMachine",
                            "concrete_RuntimeProvider::vms",
                            "concrete_VirtualMachine::maps"
                        ),
                        checkOneClass(
                            ielem, concr, provider, celem,
                            "infrastructure_Network",
                            "concrete_RuntimeProvider::networks",
                            "concrete_Network::maps"
                        ),
                        checkOneClass(
                            ielem, concr, provider, celem,
                            "infrastructure_Storage",
                            "concrete_RuntimeProvider::storages",
                            "concrete_Storage::maps"
                        ),
                        checkOneClass(
                            ielem, concr, provider, celem,
                            "infrastructure_FunctionAsAService",
                            "concrete_RuntimeProvider::faas",
                            "concrete_FunctionAsAService::maps"
                        ),
                    )
                )
            )
        )

    def all_ifaces_have_sec_group() -> ExprRef:
        sg, iface = Consts("sg iface", ELEMSORT)

        return ForAll(
            [iface],
            Implies(
                state.rels.ElemClass(
                    iface) == CLASSES["infrastructure_NetworkInterface"].ref,
                Exists(
                    [sg],
                        state.rels.AssocRel(
                            iface, ASSOCS["infrastructure_NetworkInterface::associated"].ref, sg)

                )
            )
        )

    def all_secgroup_have_iface() -> ExprRef:
        sg, iface = Consts("sg iface", ELEMSORT)

        return ForAll(
            [sg],
            Implies(
                state.rels.ElemClass(
                    sg) == CLASSES["infrastructure_SecurityGroup"].ref,
                Exists(
                    [iface],
                        state.rels.AssocRel(
                            sg, ASSOCS["infrastructure_SecurityGroup::ifaces"].ref, iface)

                )
            )
        )

    REQS = [
        vm_iface,
        software_package_iface_net,
        iface_uniq,
        all_SoftwareComponents_deployed,
        all_infrastructure_elements_deployed,
        all_ifaces_have_sec_group,
        all_secgroup_have_iface
    ]

    for req in REQS:
        state.solver.assert_and_track(
            req(), f'Requirement {str(req.__name__)}')

    return state
