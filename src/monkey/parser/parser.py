from enum import Enum
from typing import Callable, Dict, List, Union

from monkey import ast, lexer, token


class Precedence(Enum):
    LOWEST = 1
    EQUALS = 2       # ==
    LESSGREATER = 3  # > or <
    SUM = 4          # +
    PRODUCT = 5      # *
    PREFIX = 6       # -X or !X
    CALL = 7         # myFunction(X)
    INDEX = 8        # array[index]


precedences = {
    token.EQ: Precedence.EQUALS,
    token.NOT_EQ: Precedence.EQUALS,
    token.LT: Precedence.LESSGREATER,
    token.GT: Precedence.LESSGREATER,
    token.PLUS: Precedence.SUM,
    token.MINUS: Precedence.SUM,
    token.SLASH: Precedence.PRODUCT,
    token.ASTERISK: Precedence.PRODUCT,
    token.LPAREN: Precedence.CALL,
    token.LBRACKET: Precedence.INDEX,
}


prefix_parse_fn = Callable[[], ast.Expression]
infix_parse_fn = Callable[[ast.Expression], ast.Expression]


class Parser:

    def __init__(self, l: lexer.Lexer):
        self.l = l
        self.errors: List[str] = []

        self.cur_token: token.Token = None
        self.peek_token: token.Token = None

        self.prefix_parse_fns: Dict[token.TokenType, prefix_parse_fn] = {}
        self.infix_parse_fns: Dict[token.TokenType, infix_parse_fn] = {}

        self.register_prefix(token.IDENT, self.parse_identifier)
        self.register_prefix(token.INT, self.parse_integer_literal)
        self.register_prefix(token.STRING, self.parse_string_literal)
        self.register_prefix(token.BANG, self.parse_prefix_expression)
        self.register_prefix(token.MINUS, self.parse_prefix_expression)
        self.register_prefix(token.TRUE, self.parse_boolean)
        self.register_prefix(token.FALSE, self.parse_boolean)
        self.register_prefix(token.LPAREN, self.parse_grouped_expression)
        self.register_prefix(token.IF, self.parse_if_expression)
        self.register_prefix(token.FUNCTION, self.parse_function_literal)
        self.register_prefix(token.LBRACKET, self.parse_array_literal)
        self.register_prefix(token.LBRACE, self.parse_hash_literal)

        self.register_infix(token.PLUS, self.parse_infix_expression)
        self.register_infix(token.MINUS, self.parse_infix_expression)
        self.register_infix(token.SLASH, self.parse_infix_expression)
        self.register_infix(token.ASTERISK, self.parse_infix_expression)
        self.register_infix(token.EQ, self.parse_infix_expression)
        self.register_infix(token.NOT_EQ, self.parse_infix_expression)
        self.register_infix(token.LT, self.parse_infix_expression)
        self.register_infix(token.GT, self.parse_infix_expression)
        self.register_infix(token.LPAREN, self.parse_call_expression)
        self.register_infix(token.LBRACKET, self.parse_index_expression)

        # Read two tokens, so cur_token and peek_token are both set
        self.next_token()
        self.next_token()

    def next_token(self):
        self.cur_token = self.peek_token
        self.peek_token = self.l.next_token()

    def cur_token_is(self, t: token.TokenType) -> bool:
        return self.cur_token.type == t

    def peek_token_is(self, t: token.TokenType) -> bool:
        return self.peek_token.type == t

    def expect_peek(self, t: token.TokenType) -> bool:
        if self.peek_token_is(t):
            self.next_token()
            return True
        else:
            self.peek_error(t)
            return False

    def peek_error(self, t: token.TokenType):
        msg = 'expected next token to be {}, got {} instead'.format(t, self.peek_token.type)
        self.errors.append(msg)

    def no_prefix_parse_fn_error(self, t: token.TokenType):
        msg = 'no prefix parse function for {} found'.format(t)
        self.errors.append(msg)

    def parse_program(self) -> ast.Program:
        program = ast.Program()

        while self.cur_token.type != token.EOF:
            stmt = self.parse_statement()
            if stmt is not None:
                program.statements.append(stmt)
            self.next_token()

        return program

    def parse_statement(self) -> Union[ast.Statement, None]:
        if self.cur_token.type == token.LET:
            return self.parse_let_statement()
        elif self.cur_token.type == token.RETURN:
            return self.parse_return_statement()
        else:
            return self.parse_expression_statement()

    def parse_let_statement(self) -> Union[ast.LetStatement, None]:
        stmt = ast.LetStatement(self.cur_token)

        if not self.expect_peek(token.IDENT):
            return None

        stmt.name = ast.Identifier(self.cur_token, self.cur_token.literal)

        if not self.expect_peek(token.ASSIGN):
            return None

        self.next_token()

        stmt.value = self.parse_expression(Precedence.LOWEST)

        if self.peek_token_is(token.SEMICOLON):
            self.next_token()

        return stmt

    def parse_return_statement(self) -> ast.ReturnStatement:
        stmt = ast.ReturnStatement(self.cur_token)

        self.next_token()

        stmt.return_value = self.parse_expression(Precedence.LOWEST)

        if self.peek_token_is(token.SEMICOLON):
            self.next_token()

        return stmt

    def parse_expression_statement(self) -> ast.ExpressionStatement:
        stmt = ast.ExpressionStatement(self.cur_token)

        stmt.expression = self.parse_expression(Precedence.LOWEST)

        if self.peek_token_is(token.SEMICOLON):
            self.next_token()

        return stmt

    def parse_expression(self, precedence: Precedence) -> Union[ast.Expression, None]:
        if self.cur_token.type not in self.prefix_parse_fns:
            self.no_prefix_parse_fn_error(self.cur_token.type)
            return None
        prefix = self.prefix_parse_fns[self.cur_token.type]
        left_exp = prefix()

        # ここが山場だ！ 1 + 2 * 3
        while not self.peek_token_is(token.SEMICOLON) and precedence.value < self.peek_precedence().value:
            if self.peek_token.type not in self.infix_parse_fns:
                return left_exp
            infix = self.infix_parse_fns[self.peek_token.type]

            self.next_token()

            left_exp = infix(left_exp)

        return left_exp

    def peek_precedence(self) -> Precedence:
        if self.peek_token.type in precedences:
            return precedences[self.peek_token.type]

        return Precedence.LOWEST

    def cur_precedence(self) -> Precedence:
        if self.cur_token.type in precedences:
            return precedences[self.cur_token.type]

        return Precedence.LOWEST

    def parse_identifier(self) -> ast.Expression:
        return ast.Identifier(self.cur_token, self.cur_token.literal)

    def parse_integer_literal(self) -> Union[ast.Expression, None]:
        lit = ast.IntegerLiteral(self.cur_token)

        if not self.cur_token.literal.isdigit():
            msg = "could not parse '{}' as integer".format(self.cur_token.literal)
            self.errors.append(msg)
            return None

        lit.value = int(self.cur_token.literal)

        return lit

    def parse_string_literal(self) -> ast.Expression:
        return ast.StringLiteral(self.cur_token, self.cur_token.literal)

    def parse_prefix_expression(self) -> ast.Expression:
        expression = ast.PrefixExpression(self.cur_token, self.cur_token.literal)

        self.next_token()

        expression.right = self.parse_expression(Precedence.PREFIX)

        return expression

    def parse_infix_expression(self, left: ast.Expression) -> ast.Expression:
        expression = ast.InfixExpression(self.cur_token, left, self.cur_token.literal)

        precedence = self.cur_precedence()
        self.next_token()
        expression.right = self.parse_expression(precedence)

        return expression

    def parse_boolean(self) -> ast.Expression:
        return ast.Boolean(self.cur_token, self.cur_token_is(token.TRUE))

    def parse_if_expression(self) -> Union[ast.Expression, None]:
        expression = ast.IfExpression(self.cur_token)

        if not self.expect_peek(token.LPAREN):
            return None

        self.next_token()
        expression.condition = self.parse_expression(Precedence.LOWEST)

        if not self.expect_peek(token.RPAREN):
            return None

        if not self.expect_peek(token.LBRACE):
            return None

        expression.consequence = self.parse_block_statement()

        if self.peek_token_is(token.ELSE):
            self.next_token()

            if not self.expect_peek(token.LBRACE):
                return None

            expression.alternative = self.parse_block_statement()

        return expression

    def parse_block_statement(self) -> ast.BlockStatement:
        block = ast.BlockStatement(self.cur_token)
        block.statements = []

        self.next_token()

        while not self.cur_token_is(token.RBRACE) and not self.cur_token_is(token.EOF):
            stmt = self.parse_statement()
            if stmt is not None:
                block.statements.append(stmt)
            self.next_token()

        return block

    def parse_function_literal(self) -> Union[ast.Expression, None]:
        lit = ast.FunctionLiteral(self.cur_token)

        if not self.expect_peek(token.LPAREN):
            return None

        lit.parameters = self.parse_function_parameters()

        if not self.expect_peek(token.LBRACE):
            return None

        lit.body = self.parse_block_statement()

        return lit

    def parse_function_parameters(self) -> Union[List[ast.Identifier], None]:
        identifiers: List[ast.Identifier] = []

        if self.peek_token_is(token.RPAREN):
            self.next_token()
            return identifiers

        self.next_token()

        ident = ast.Identifier(self.cur_token, self.cur_token.literal)
        identifiers.append(ident)

        while self.peek_token_is(token.COMMA):
            self.next_token()
            self.next_token()
            ident = ast.Identifier(self.cur_token, self.cur_token.literal)
            identifiers.append(ident)

        if not self.expect_peek(token.RPAREN):
            return None

        return identifiers

    def parse_call_expression(self, function: ast.Expression) -> ast.Expression:
        exp = ast.CallExpression(self.cur_token, function)
        exp.arguments = self.parse_expression_list(token.RPAREN)
        return exp

    def parse_expression_list(self, end: token.TokenType) -> Union[List[ast.Expression], None]:
        list: List[ast.Expression] = []

        if self.peek_token_is(end):
            self.next_token()
            return list

        self.next_token()
        list.append(self.parse_expression(Precedence.LOWEST))

        while self.peek_token_is(token.COMMA):
            self.next_token()
            self.next_token()
            list.append(self.parse_expression(Precedence.LOWEST))

        if not self.expect_peek(end):
            return None

        return list

    def parse_array_literal(self) -> ast.Expression:
        array = ast.ArrayLiteral(self.cur_token)

        array.elements = self.parse_expression_list(token.RBRACKET)

        return array

    def parse_index_expression(self, left: ast.Expression) -> Union[ast.Expression, None]:
        exp = ast.IndexExpression(self.cur_token, left)

        self.next_token()
        exp.index = self.parse_expression(Precedence.LOWEST)

        if not self.expect_peek(token.RBRACKET):
            return None

        return exp

    def parse_grouped_expression(self) -> Union[ast.Expression, None]:
        self.next_token()

        exp = self.parse_expression(Precedence.LOWEST)

        if not self.expect_peek(token.RPAREN):
            return None

        return exp

    def parse_hash_literal(self) -> Union[ast.Expression, None]:
        hash = ast.HashLiteral(self.cur_token)
        hash.pairs = {}

        while not self.peek_token_is(token.RBRACE):
            self.next_token()
            key = self.parse_expression(Precedence.LOWEST)

            if not self.expect_peek(token.COLON):
                return None

            self.next_token()
            value = self.parse_expression(Precedence.LOWEST)

            hash.pairs[key] = value

            if not self.peek_token_is(token.RBRACE) and not self.expect_peek(token.COMMA):
                return None

        if not self.expect_peek(token.RBRACE):
            return None

        return hash

    def register_prefix(self, token_type: token.TokenType, fn: prefix_parse_fn):
        self.prefix_parse_fns[token_type] = fn

    def register_infix(self, token_type: token.TokenType, fn: infix_parse_fn):
        self.infix_parse_fns[token_type] = fn
