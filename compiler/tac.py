from __future__ import annotations

from dataclasses import dataclass

from . import ast


@dataclass(frozen=True)
class TACInstr:
    op: str
    arg1: str | int | None
    arg2: str | int | None
    result: str


@dataclass(frozen=True)
class TACProgram:
    instructions: list[TACInstr]


class TempFactory:
    def __init__(self) -> None:
        self._count = 0

    def next(self) -> str:
        self._count += 1
        return f"t{self._count}"


def generate(program: ast.Program) -> TACProgram:
    instructions: list[TACInstr] = []
    temps = TempFactory()

    for decl in program.statements:
        value = _emit_expr(decl.assignment.value, instructions, temps)
        instructions.append(TACInstr("ASSIGN", value, None, decl.assignment.target.name))

    return TACProgram(instructions=instructions)


def _emit_expr(expr: ast.Expr, instructions: list[TACInstr], temps: TempFactory) -> str | int:
    if isinstance(expr, ast.Literal):
        return expr.value
    if isinstance(expr, ast.Identifier):
        return expr.name
    if isinstance(expr, ast.BinaryExpr):
        left = _emit_expr(expr.left, instructions, temps)
        right = _emit_expr(expr.right, instructions, temps)
        temp = temps.next()
        op = expr.op.value
        instructions.append(TACInstr(op, left, right, temp))
        return temp
    raise TypeError(f"Unsupported expr type: {type(expr)}")
