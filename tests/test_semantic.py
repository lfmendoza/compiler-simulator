from compiler.lexer import lex
from compiler.parser import parse
from compiler.semantic import analyze


def test_semantic_undeclared():
    source = "int position = initial + velocity * 60;"
    tokens, _ = lex(source)
    program, _ = parse(tokens)
    result = analyze(program)
    messages = [d.message for d in result.diagnostics]
    assert "initial" in messages[0] or "velocity" in messages[0]
    assert len(result.diagnostics) == 2


def test_semantic_declared_ok():
    source = (
        "int initial = 1;"
        "int velocity = 2;"
        "int position = initial + velocity * 60;"
    )
    tokens, _ = lex(source)
    program, _ = parse(tokens)
    result = analyze(program)
    assert result.diagnostics == []
