
from dataclasses import dataclass
from typing import Optional
from z3 import SortRef, FuncDeclRef, DatatypeSortRef


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
class Sort:
    Class: DatatypeSortRef
    Elem: DatatypeSortRef
    Assoc: DatatypeSortRef
    Attr: DatatypeSortRef
