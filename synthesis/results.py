from z3 import ArithRef


def parse_synthesis_result(res):
    if isinstance(res, ArithRef):
        # if it's more than one element
        if str(res.arg(0)).startswith('Or('):  # UGLY
            elems = [c.arg(1) for c in res.arg(0).children()]
            value = res.arg(1)
            return elems, value.as_long()
        else:
            elem = res.arg(0).arg(1)
            value = res.arg(1)
            return [elem], value.as_long()
