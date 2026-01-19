from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Phase(str, Enum):
    LEXER = "lexer"
    PARSER = "parser"
    SEMANTIC = "semantic"
    TAC = "tac"
    CODEGEN = "codegen"
    OPTIMIZER = "optimizer"


@dataclass(frozen=True)
class Span:
    line: int
    col: int


@dataclass(frozen=True)
class Diagnostic:
    phase: Phase
    code: str
    message: str
    span: Span | None = None


def diag(phase: Phase, code: str, message: str, span: Span | None = None) -> Diagnostic:
    return Diagnostic(phase=phase, code=code, message=message, span=span)
