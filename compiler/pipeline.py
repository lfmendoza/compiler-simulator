from __future__ import annotations

from dataclasses import dataclass

from .ast import Program
from .codegen import AssemblyProgram, generate as generate_asm
from .diagnostics import Diagnostic
from .lexer import Token, lex
from .optimizer import OptimizationResult, optimize
from .parser import parse
from .semantic import SemanticResult, analyze
from .tac import TACProgram, generate as generate_tac


@dataclass(frozen=True)
class CompilationResult:
    tokens: list[Token]
    ast: Program
    semantic: SemanticResult
    tac: TACProgram
    assembly: AssemblyProgram
    optimized_tac: OptimizationResult
    optimized_assembly: AssemblyProgram
    diagnostics: list[Diagnostic]


def compile_source(source: str) -> CompilationResult:
    tokens, lex_diags = lex(source)
    program, parse_diags = parse(tokens)
    semantic = analyze(program)
    tac = generate_tac(program)
    assembly = generate_asm(tac)
    optimized_tac = optimize(tac)
    optimized_assembly = generate_asm(optimized_tac.program)

    diagnostics = lex_diags + parse_diags + semantic.diagnostics

    return CompilationResult(
        tokens=tokens,
        ast=program,
        semantic=semantic,
        tac=tac,
        assembly=assembly,
        optimized_tac=optimized_tac,
        optimized_assembly=optimized_assembly,
        diagnostics=diagnostics,
    )
