from __future__ import annotations

from dataclasses import dataclass

from . import ast
from .diagnostics import Diagnostic, Phase, Span, diag


@dataclass(frozen=True)
class Symbol:
    name: str
    type_name: ast.TypeName
    span: Span | None
    scope: str = "global"


class SymbolTable:
    def __init__(self) -> None:
        self._symbols: dict[str, Symbol] = {}

    def declare(self, symbol: Symbol) -> Diagnostic | None:
        if symbol.name in self._symbols:
            existing = self._symbols[symbol.name]
            return diag(
                Phase.SEMANTIC,
                "SEM001",
                f"Duplicate declaration of '{symbol.name}'",
                existing.span or symbol.span,
            )
        self._symbols[symbol.name] = symbol
        return None

    def lookup(self, name: str) -> Symbol | None:
        return self._symbols.get(name)

    def all(self) -> list[Symbol]:
        return list(self._symbols.values())


@dataclass(frozen=True)
class SemanticResult:
    symbols: SymbolTable
    diagnostics: list[Diagnostic]


def analyze(program: ast.Program) -> SemanticResult:
    diagnostics: list[Diagnostic] = []
    table = SymbolTable()

    for decl in program.statements:
        symbol = Symbol(name=decl.assignment.target.name, type_name=decl.type_name, span=decl.span)
        dup = table.declare(symbol)
        if dup:
            diagnostics.append(dup)
        diagnostics.extend(_check_expr(decl.assignment.value, table))

    return SemanticResult(symbols=table, diagnostics=diagnostics)


def _check_expr(expr: ast.Expr, table: SymbolTable) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    if isinstance(expr, ast.Identifier):
        if table.lookup(expr.name) is None:
            diagnostics.append(
                diag(
                    Phase.SEMANTIC,
                    "SEM002",
                    f"Use of undeclared identifier '{expr.name}'",
                    expr.span,
                )
            )
    elif isinstance(expr, ast.BinaryExpr):
        diagnostics.extend(_check_expr(expr.left, table))
        diagnostics.extend(_check_expr(expr.right, table))
    return diagnostics
