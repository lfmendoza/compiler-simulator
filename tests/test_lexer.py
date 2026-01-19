from compiler.lexer import TokenType, lex


def test_lex_tokens():
    source = "int position = initial + velocity * 60;"
    tokens, diagnostics = lex(source)
    assert diagnostics == []
    types = [t.type for t in tokens if t.type != TokenType.EOF]
    assert types == [
        TokenType.KEYWORD_INT,
        TokenType.IDENTIFIER,
        TokenType.ASSIGN,
        TokenType.IDENTIFIER,
        TokenType.PLUS,
        TokenType.IDENTIFIER,
        TokenType.MULTIPLY,
        TokenType.INTEGER_LITERAL,
        TokenType.SEMICOLON,
    ]
