from __future__ import annotations

import argparse
import json
import sys

from . import ast
from .codegen import AssemblyProgram
from .diagnostics import Diagnostic, Phase
from .lexer import Token, TokenType, lex
from .optimizer import OptimizationResult
from .parser import parse
from .pipeline import compile_source
from .semantic import SemanticResult
from .tac import TACProgram, TACInstr, generate as generate_tac
from .codegen import generate as generate_asm
from .optimizer import optimize


def main() -> int:
    parser = argparse.ArgumentParser(prog="compiler-sim")
    sub = parser.add_subparsers(dest="command", required=True)

    for cmd in ["lex", "parse", "semantic", "tac", "codegen", "optimize", "all"]:
        cmd_parser = sub.add_parser(cmd)
        cmd_parser.add_argument("path", nargs="?", help="Path to source file")
        cmd_parser.add_argument("--stdin", action="store_true", help="Read from stdin")
        cmd_parser.add_argument(
            "--format", choices=["md", "json"], default="md", help="Output format"
        )

    args = parser.parse_args()
    source = _read_source(args.path, args.stdin)

    if args.command == "lex":
        tokens, diagnostics = lex(source)
        return _emit(args.format, render_lex(tokens, diagnostics, args.format))
    if args.command == "parse":
        tokens, _ = lex(source)
        program, diagnostics = parse(tokens)
        return _emit(args.format, render_parse(program, diagnostics, args.format))
    if args.command == "semantic":
        result = compile_source(source)
        return _emit(args.format, render_semantic(result.semantic, result.diagnostics, args.format))
    if args.command == "tac":
        tokens, _ = lex(source)
        program, _ = parse(tokens)
        tac = generate_tac(program)
        return _emit(args.format, render_tac(tac, args.format))
    if args.command == "codegen":
        tokens, _ = lex(source)
        program, _ = parse(tokens)
        tac = generate_tac(program)
        asm = generate_asm(tac)
        return _emit(args.format, render_codegen(asm, args.format))
    if args.command == "optimize":
        tokens, _ = lex(source)
        program, _ = parse(tokens)
        tac = generate_tac(program)
        optimized = optimize(tac)
        asm = generate_asm(optimized.program)
        return _emit(args.format, render_optimization(optimized, asm, args.format))
    if args.command == "all":
        result = compile_source(source)
        return _emit(args.format, render_all(result, args.format))

    return 1


def _read_source(path: str | None, use_stdin: bool) -> str:
    if use_stdin:
        return sys.stdin.read()
    if not path:
        raise SystemExit("Provide a source file path or use --stdin.")
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def _emit(fmt: str, payload: str | dict) -> int:
    if fmt == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(payload)
    return 0


def render_lex(tokens: list[Token], diagnostics: list[Diagnostic], fmt: str) -> str | dict:
    if fmt == "json":
        return {
            "tokens": [_token_dict(t) for t in tokens if t.type != TokenType.EOF],
            "diagnostics": [_diag_dict(d) for d in diagnostics],
        }
    return "\n".join(
        [
            "## Fase 1: Analisis Lexico",
            "",
            "### Tabla de tokens:",
            _tokens_table(tokens),
            "",
            _diagnostics_md(diagnostics),
        ]
    ).strip()


def render_parse(program: ast.Program, diagnostics: list[Diagnostic], fmt: str) -> str | dict:
    if fmt == "json":
        return {"ast": _ast_dict(program), "diagnostics": [_diag_dict(d) for d in diagnostics]}
    return "\n".join(
        [
            "## Fase 2: Analisis Sintactico (AST)",
            "",
            "### Arbol de sintaxis abstracta:",
            "",
            _ast_mermaid(program),
            "",
            _diagnostics_md(diagnostics),
        ]
    ).strip()


def render_semantic(
    semantic: SemanticResult, diagnostics: list[Diagnostic], fmt: str
) -> str | dict:
    if fmt == "json":
        return {
            "symbols": [_symbol_dict(s) for s in semantic.symbols.all()],
            "diagnostics": [_diag_dict(d) for d in diagnostics if d.phase == Phase.SEMANTIC],
        }
    return "\n".join(
        [
            "## Fase 3: Analisis Semantico",
            "### Comprobaciones realizadas:",
            _symbol_table(semantic),
            "",
            _diagnostics_md([d for d in diagnostics if d.phase == Phase.SEMANTIC]),
        ]
    ).strip()


def render_tac(tac: TACProgram, fmt: str) -> str | dict:
    if fmt == "json":
        return {"tac": [_tac_dict(i) for i in tac.instructions]}
    return "\n".join(
        [
            "## Fase 4: Codigo Intermedio (TAC)",
            "```",
            *(_tac_lines(tac)),
            "```",
        ]
    ).strip()


def render_codegen(asm: AssemblyProgram, fmt: str) -> str | dict:
    if fmt == "json":
        return {"assembly": asm.instructions}
    return "\n".join(
        [
            "## Fase 5: Codigo Maquina",
            "```",
            *[f"- {line}" for line in asm.instructions],
            "```",
        ]
    ).strip()


def render_optimization(
    opt: OptimizationResult, asm: AssemblyProgram, fmt: str
) -> str | dict:
    if fmt == "json":
        return {
            "optimized_tac": [_tac_dict(i) for i in opt.program.instructions],
            "optimized_assembly": asm.instructions,
            "explanations": opt.explanations,
        }
    return "\n".join(
        [
            "## Fase 6: Optimizacion de Codigo",
            "### Codigo optimizado:",
            "```",
            *[f"- {line}" for line in asm.instructions],
            "```",
            "",
            "### Explicaciones:",
            *(f"- {e}" for e in (opt.explanations or ["Sin optimizaciones aplicables."])),
        ]
    ).strip()


def render_all(result, fmt: str) -> str | dict:
    if fmt == "json":
        return {
            "tokens": [_token_dict(t) for t in result.tokens if t.type != TokenType.EOF],
            "ast": _ast_dict(result.ast),
            "symbols": [_symbol_dict(s) for s in result.semantic.symbols.all()],
            "tac": [_tac_dict(i) for i in result.tac.instructions],
            "assembly": result.assembly.instructions,
            "optimized_tac": [_tac_dict(i) for i in result.optimized_tac.program.instructions],
            "optimized_assembly": result.optimized_assembly.instructions,
            "diagnostics": [_diag_dict(d) for d in result.diagnostics],
            "optimization_notes": result.optimized_tac.explanations,
        }
    sections = [
        render_lex(result.tokens, result.diagnostics, fmt),
        render_parse(result.ast, result.diagnostics, fmt),
        render_semantic(result.semantic, result.diagnostics, fmt),
        render_tac(result.tac, fmt),
        render_codegen(result.assembly, fmt),
        render_optimization(result.optimized_tac, result.optimized_assembly, fmt),
    ]
    return "\n\n".join(sections)


def _tokens_table(tokens: list[Token]) -> str:
    rows = [
        "| Lexema | Token | Atributo/Entrada |",
        "|---|---|---|",
    ]
    for token in tokens:
        if token.type == TokenType.EOF:
            continue
        attr = token.literal if token.literal is not None else "-"
        rows.append(f"| {token.lexeme} | {token.type.value} | {attr} |")
    return "\n".join(rows)


def _symbol_table(semantic: SemanticResult) -> str:
    rows = [
        "### Tabla de simbolos:",
        "| Entrada | Identificador | Tipo | Ambito |",
        "|---|---|---|---|",
    ]
    for idx, symbol in enumerate(semantic.symbols.all(), start=1):
        rows.append(f"| id#{idx} | {symbol.name} | {symbol.type_name.value} | {symbol.scope} |")
    return "\n".join(rows)


def _ast_mermaid(program: ast.Program) -> str:
    lines = ["```mermaid", "graph TD"]
    node_id = 0

    def next_id() -> str:
        nonlocal node_id
        node_id += 1
        return f"N{node_id}"

    def walk(expr: ast.Expr) -> str:
        if isinstance(expr, ast.Identifier):
            nid = next_id()
            lines.append(f"  {nid}[\"Identifier: {expr.name}\"]")
            return nid
        if isinstance(expr, ast.Literal):
            nid = next_id()
            lines.append(f"  {nid}[\"Literal: {expr.value}\"]")
            return nid
        if isinstance(expr, ast.BinaryExpr):
            nid = next_id()
            lines.append(f"  {nid}[\"Expr({expr.op.value})\"]")
            left = walk(expr.left)
            right = walk(expr.right)
            lines.append(f"  {nid} --> {left}")
            lines.append(f"  {nid} --> {right}")
            return nid
        raise TypeError(f"Unknown expr {type(expr)}")

    root = next_id()
    lines.append(f"  {root}[Declaration]")
    for decl in program.statements:
        type_node = next_id()
        assign_node = next_id()
        lines.append(f"  {type_node}[\"Type: {decl.type_name.value}\"]")
        lines.append(f"  {assign_node}[Assign]")
        lines.append(f"  {root} --> {type_node}")
        lines.append(f"  {root} --> {assign_node}")
        target = next_id()
        lines.append(f"  {target}[\"Identifier: {decl.assignment.target.name}\"]")
        lines.append(f"  {assign_node} --> {target}")
        expr_id = walk(decl.assignment.value)
        lines.append(f"  {assign_node} --> {expr_id}")
    lines.append("```")
    return "\n".join(lines)


def _diagnostics_md(diagnostics: list[Diagnostic]) -> str:
    if not diagnostics:
        return "Sin errores."
    lines = ["### Diagnosticos:"]
    for diag in diagnostics:
        if diag.span:
            loc = f"(linea {diag.span.line}, col {diag.span.col})"
        else:
            loc = ""
        lines.append(f"- [{diag.phase}] {diag.code}: {diag.message} {loc}".strip())
    return "\n".join(lines)


def _tac_lines(tac: TACProgram) -> list[str]:
    lines: list[str] = []
    for instr in tac.instructions:
        if instr.op == "ASSIGN":
            lines.append(f"{instr.result} = {instr.arg1}")
        else:
            lines.append(f"{instr.result} = {instr.arg1} {instr.op} {instr.arg2}")
    return lines


def _token_dict(token: Token) -> dict:
    return {
        "type": token.type.value,
        "lexeme": token.lexeme,
        "line": token.span.line,
        "col": token.span.col,
        "literal": token.literal,
    }


def _symbol_dict(symbol) -> dict:
    return {
        "name": symbol.name,
        "type": symbol.type_name.value,
        "scope": symbol.scope,
        "line": symbol.span.line if symbol.span else None,
        "col": symbol.span.col if symbol.span else None,
    }


def _tac_dict(instr: TACInstr) -> dict:
    return {"op": instr.op, "arg1": instr.arg1, "arg2": instr.arg2, "result": instr.result}


def _diag_dict(diag: Diagnostic) -> dict:
    return {
        "phase": diag.phase.value,
        "code": diag.code,
        "message": diag.message,
        "line": diag.span.line if diag.span else None,
        "col": diag.span.col if diag.span else None,
    }


def _ast_dict(program: ast.Program) -> dict:
    return {"statements": [_node_dict(stmt) for stmt in program.statements]}


def _node_dict(node) -> dict:
    if isinstance(node, ast.Program):
        return {"statements": [_node_dict(s) for s in node.statements]}
    if isinstance(node, ast.Declaration):
        return {
            "type": node.type_name.value,
            "assignment": _node_dict(node.assignment),
        }
    if isinstance(node, ast.Assign):
        return {"target": _node_dict(node.target), "value": _node_dict(node.value)}
    if isinstance(node, ast.Identifier):
        return {"identifier": node.name}
    if isinstance(node, ast.Literal):
        return {"literal": node.value}
    if isinstance(node, ast.BinaryExpr):
        return {
            "op": node.op.value,
            "left": _node_dict(node.left),
            "right": _node_dict(node.right),
        }
    raise TypeError(f"Unsupported AST node: {type(node)}")


#
