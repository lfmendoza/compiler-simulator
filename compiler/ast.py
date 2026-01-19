from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .diagnostics import Span


class TypeName(str, Enum):
    INT = "int"


class BinOp(str, Enum):
    ADD = "+"
    MUL = "*"


@dataclass(frozen=True, kw_only=True)
class Node:
    span: Span | None = None


@dataclass(frozen=True)
class Program(Node):
    statements: list[Declaration]


@dataclass(frozen=True)
class Declaration(Node):
    type_name: TypeName
    assignment: Assign


@dataclass(frozen=True)
class Assign(Node):
    target: Identifier
    value: Expr


class Expr(Node):
    pass


@dataclass(frozen=True)
class Identifier(Expr):
    name: str


@dataclass(frozen=True)
class Literal(Expr):
    value: int


@dataclass(frozen=True)
class BinaryExpr(Expr):
    op: BinOp
    left: Expr
    right: Expr
