from z3 import *
from .types import State


def run_tests(state: State):
    CLASSES = state.data.Classes
    ELEMS = state.data.Elems
    ASSOCS = state.data.Assocs
    ATTRS = state.data.Attrs

    s = state.solver

    # First of all, check that the model we got is actually satisfiable:
    assert s.check() == sat

    def z3_test_wrapper(expr: ExprRef, expectedResult: CheckSatResult):
        s.push()
        s.add(expr)
        assert s.check() == expectedResult
        s.pop()

    # TEST: VirtualMachine must have only its own attribute relationship, and not others.
    # VirtualMachine DOES NOT have Attribute infrastructure_Rule::cidr
    # so we're expecting it to be unsatisfiable
    vm = Const('vm', state.sorts.Elem)

    z3_test_wrapper(
        ForAll(
            [vm],
            Implies(
                state.rels.ElemClass(
                    vm) == CLASSES["infrastructure_VirtualMachine"].ref,
                state.rels.int.AttrExistRel(
                    vm, ATTRS["infrastructure_Rule::cidr"].ref)
            )
        ), unsat)

    # Same test, for another component, but this time it MUST have its own attribute.
    z3_test_wrapper(
        ForAll(
            [vm],
            Implies(
                state.rels.ElemClass(vm) == CLASSES["infrastructure_Rule"].ref,
                state.rels.int.AttrExistRel(
                    vm, ATTRS["infrastructure_Rule::fromPort"].ref)
            )
        ), sat)
    # If this fails, it means that you are assigning attribute relationship wrong!

    # TEST: VirtualMachine must have a value specified in the DOML
    # for attribute `infrastructure_ComputingNode::cpu_count`
    # MAKE SURE THAT in the test DOML/IM.yaml every VM DOES NOT have an attribute
    # `infrastructure_ComputingNode::cpu_count`
    z3_test_wrapper(
        ForAll(
            [vm],
            Implies(
                state.rels.ElemClass(
                    vm) == CLASSES["infrastructure_VirtualMachine"].ref,
                state.rels.int.AttrExistValueRel(
                    vm, ATTRS["infrastructure_ComputingNode::cpu_count"].ref)
            )
        ), unsat)

    # TEST: VirtualMachine must have a value specified in the DOML
    # for attribute `infrastructure_ComputingNode::memory_mb`
    # MAKE SURE THAT in the test DOML/IM.yaml every VM HAS an attribute
    # `infrastructure_ComputingNode::memory_mb`
    z3_test_wrapper(
        ForAll(
            [vm],
            Implies(
                state.rels.ElemClass(
                    vm) == CLASSES["infrastructure_VirtualMachine"].ref,
                state.rels.int.AttrExistValueRel(
                    vm, ATTRS["infrastructure_ComputingNode::memory_mb"].ref)
            )
        ), sat)

    # TEST: VirtualMachine must have a value specified in the DOML
    # for attribute `infrastructure_ComputingNode::memory_mb` and it has
    # to be equal to 2048.
    z3_test_wrapper(
        ForAll(
            [vm],
            Implies(
                state.rels.ElemClass(
                    vm) == CLASSES["infrastructure_VirtualMachine"].ref,
                state.rels.int.AttrValueRel(
                    vm, ATTRS["infrastructure_ComputingNode::memory_mb"].ref) == 2048
            )
        ), sat)

    # TEST: VirtualMachine must have a value specified in the DOML
    # for attribute `infrastructure_ComputingNode::memory_mb` and it has
    # to be equal to 2048, and so not equal to another value (i.e. 1024)
    z3_test_wrapper(
        ForAll(
            [vm],
            Implies(
                state.rels.ElemClass(
                    vm) == CLASSES["infrastructure_VirtualMachine"].ref,
                state.rels.int.AttrValueRel(
                    vm, ATTRS["infrastructure_ComputingNode::memory_mb"].ref) == 1024
            )
        ), unsat)

    return state
