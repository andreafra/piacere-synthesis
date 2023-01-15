
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Type
from z3 import SortRef, FuncDeclRef, DatatypeSortRef, Solver


@dataclass
class Class:
    name: str
    attributes: dict[str, dict]
    associations: dict[str, dict]
    ref: Optional[SortRef] = None


@dataclass
class Elem:
    id: str
    name: Optional[str]
    attributes: dict[str, dict]
    associations: dict[str, dict]
    eClass: Optional[Class] = None
    ref: Optional[SortRef] = None
    unbound: bool = False


@dataclass
class AssocRel:
    from_elem: Class
    to_elem: Class
    inverse_of: Optional[str]
    ref: Optional[FuncDeclRef] = None


@dataclass
class AttrRel:
    multiplicity: str
    type: str
    ref: Optional[FuncDeclRef] = None


@dataclass
class Sorts:
    Class: DatatypeSortRef = None
    Elem: DatatypeSortRef = None
    Assoc: DatatypeSortRef = None
    Attr: DatatypeSortRef = None


@dataclass
class Data:
    Classes: dict[str, Class] = field(default_factory=dict)
    Elems: dict[str, Elem] = field(default_factory=dict)
    Assocs: dict[str, AssocRel] = field(default_factory=dict)
    Attrs: dict[str, AttrRel] = field(default_factory=dict)


@dataclass
class IntRels:
    AttrExistRel: FuncDeclRef = None
    AttrExistValueRel: FuncDeclRef = None
    AttrValueRel: FuncDeclRef = None
    AttrSynthRel: FuncDeclRef = None


@dataclass
class BoolRels:
    pass


@dataclass
class StrRels:
    pass


@dataclass
class Rels:
    ElemClass: FuncDeclRef = None
    AssocRel: FuncDeclRef = None
    int: IntRels = field(default_factory=IntRels)
    bool: BoolRels = field(default_factory=BoolRels)
    str: StrRels = field(default_factory=StrRels)


@dataclass
class State:
    solver: Solver = field(default=None)
    data: Data = field(default_factory=Data)
    sorts: Sorts = field(default_factory=Sorts)
    rels: Rels = field(default_factory=Rels)

    def apply(self, func: Callable[['State'], 'State'], **kwargs) -> 'State':
        return func(
            self, **kwargs
        )
