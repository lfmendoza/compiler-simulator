from __future__ import annotations

from dataclasses import dataclass

from . import ast
from .diagnostics import Diagnostic, Phase, Span, diag
from .lexer import Token, TokenType


@dataclass
class ParserState:
    tokens: list[Token]
    index: int = 0
    diagnostics: list[Diagnostic] | None = None

    def current(self) -> Token:
        return self.tokens[self.index]

    def advance(self) -> Token:
        token = self.tokens[self.index]
        if self.index < len(self.tokens) - 1:
            self.index += 1
        return token

    def match(self, token_type: TokenType) -> Token | None:
        if self.current().type == token_type:
            return self.advance()
        return None

    def expect(self, token_type: TokenType, code: str, message: str) -> Token:
        token = self.current()
        if token.type == token_type:
            return self.advance()
        self.diagnostics.append(
            diag(Phase.PARSER, code, message, token.span)
        )
        return token

    def synchronize(self) -> None:
        while self.current().type not in (TokenType.SEMICOLON, TokenType.EOF):
            self.advance()
        if self.current().type == TokenType.SEMICOLON:
            self.advance()


def parse(tokens: list[Token]) -> tuple[ast.Program, list[Diagnostic]]:
    diagnostics: list[Diagnostic] = []
    state = ParserState(tokens=tokens, diagnostics=diagnostics)
    statements: list[ast.Declaration] = []

    while state.current().type != TokenType.EOF:
        decl = parse_declaration(state)
        if decl is not None:
            statements.append(decl)
        if state.current().type == TokenType.SEMICOLON:
            state.advance()
        elif state.current().type != TokenType.EOF:
            diagnostics.append(
                diag(Phase.PARSER, "PAR001", "Expected ';' after statement", state.current().span)
            )
            state.synchronize()

    return ast.Program(statements=statements), diagnostics


def parse_declaration(state: ParserState) -> ast.Declaration | None:
    token = state.current()
    if token.type != TokenType.KEYWORD_INT:
        state.diagnostics.append(
            diag(Phase.PARSER, "PAR002", "Expected type declaration", token.span)
        )
        state.synchronize()
        return None

    state.advance()
    ident = state.expect(TokenType.IDENTIFIER, "PAR003", "Expected identifier after type")
    target = ast.Identifier(name=ident.lexeme, span=ident.span)

    state.expect(TokenType.ASSIGN, "PAR004", "Expected '=' after identifier")
    value = parse_expr(state)
    assignment = ast.Assign(target=target, value=value, span=target.span)
    return ast.Declaration(type_name=ast.TypeName.INT, assignment=assignment, span=token.span)


def parse_expr(state: ParserState) -> ast.Expr:
    expr = parse_term(state)
    while state.current().type == TokenType.PLUS:
        op_token = state.advance()
        right = parse_term(state)
        expr = ast.BinaryExpr(
            op=ast.BinOp.ADD,
            left=expr,
            right=right,
            span=op_token.span,
        )
    return expr


def parse_term(state: ParserState) -> ast.Expr:
    expr = parse_factor(state)
    while state.current().type == TokenType.MULTIPLY:
        op_token = state.advance()
        right = parse_factor(state)
        expr = ast.BinaryExpr(
            op=ast.BinOp.MUL,
            left=expr,
            right=right,
            span=op_token.span,
        )
    return expr


def parse_factor(state: ParserState) -> ast.Expr:
    token = state.current()
    if token.type == TokenType.IDENTIFIER:
        state.advance()
        return ast.Identifier(name=token.lexeme, span=token.span)
    if token.type == TokenType.INTEGER_LITERAL:
        state.advance()
        return ast.Literal(value=token.literal or 0, span=token.span)
    if token.type == TokenType.LPAREN:
        state.advance()
        expr = parse_expr(state)
        state.expect(TokenType.RPAREN, "PAR005", "Expected ')' after expression")
        return expr

    state.diagnostics.append(
        diag(Phase.PARSER, "PAR006", "Expected expression", token.span)
    )
    state.advance()
    return ast.Literal(value=0, span=token.span)
