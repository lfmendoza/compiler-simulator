from compiler import ast
from compiler.lexer import lex
from compiler.parser import parse


def test_parse_declaration_ast():
    source = "int position = initial + velocity * 60;"
    tokens, _ = lex(source)
    program, diagnostics = parse(tokens)
    assert diagnostics == []
    assert len(program.statements) == 1
    decl = program.statements[0]
    assert isinstance(decl, ast.Declaration)
    assert decl.type_name == ast.TypeName.INT
    assign = decl.assignment
    assert assign.target.name == "position"
    assert isinstance(assign.value, ast.BinaryExpr)
    assert assign.value.op == ast.BinOp.ADD
