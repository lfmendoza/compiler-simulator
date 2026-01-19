from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .diagnostics import Diagnostic, Phase, Span, diag


class TokenType(str, Enum):
    KEYWORD_INT = "KEYWORD_INT"
    IDENTIFIER = "IDENTIFIER"
    INTEGER_LITERAL = "INTEGER_LITERAL"
    ASSIGN = "ASSIGN"
    PLUS = "PLUS"
    MULTIPLY = "MULTIPLY"
    SEMICOLON = "SEMICOLON"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    EOF = "EOF"


@dataclass(frozen=True)
class Token:
    type: TokenType
    lexeme: str
    span: Span
    literal: int | None = None


KEYWORDS = {"int": TokenType.KEYWORD_INT}


def lex(source: str) -> tuple[list[Token], list[Diagnostic]]:
    tokens: list[Token] = []
    diagnostics: list[Diagnostic] = []

    i = 0
    line = 1
    col = 1

    def current() -> str:
        return source[i] if i < len(source) else ""

    def advance() -> str:
        nonlocal i, line, col
        ch = source[i]
        i += 1
        if ch == "\n":
            line += 1
            col = 1
        else:
            col += 1
        return ch

    while i < len(source):
        ch = current()
        if ch.isspace():
            advance()
            continue

        start_span = Span(line, col)

        if ch.isalpha() or ch == "_":
            lexeme = advance()
            while i < len(source) and (current().isalnum() or current() == "_"):
                lexeme += advance()
            token_type = KEYWORDS.get(lexeme, TokenType.IDENTIFIER)
            tokens.append(Token(token_type, lexeme, start_span))
            continue

        if ch.isdigit():
            lexeme = advance()
            while i < len(source) and current().isdigit():
                lexeme += advance()
            tokens.append(
                Token(TokenType.INTEGER_LITERAL, lexeme, start_span, literal=int(lexeme))
            )
            continue

        if ch == "=":
            advance()
            tokens.append(Token(TokenType.ASSIGN, "=", start_span))
            continue

        if ch == "+":
            advance()
            tokens.append(Token(TokenType.PLUS, "+", start_span))
            continue

        if ch == "*":
            advance()
            tokens.append(Token(TokenType.MULTIPLY, "*", start_span))
            continue

        if ch == ";":
            advance()
            tokens.append(Token(TokenType.SEMICOLON, ";", start_span))
            continue

        if ch == "(":
            advance()
            tokens.append(Token(TokenType.LPAREN, "(", start_span))
            continue

        if ch == ")":
            advance()
            tokens.append(Token(TokenType.RPAREN, ")", start_span))
            continue

        diagnostics.append(
            diag(Phase.LEXER, "LEX001", f"Unexpected character '{ch}'", start_span)
        )
        advance()

    tokens.append(Token(TokenType.EOF, "", Span(line, col)))
    return tokens, diagnostics
