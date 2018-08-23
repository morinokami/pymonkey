from typing import NamedTuple

from monkey import lexer, token


class Target(NamedTuple):
    expected_type: token.TokenType
    expected_literal: str


def test_next_token():
    input = '''let five = 5;
    let ten = 10;
    
    let add = fn(x, y) {
      x + y;
    };
    
    let result = add(five, ten);
    !-/*5;
    5 < 10 > 5;
    
    if (5 < 10) {
        return true;
    } else {
        return false;
    }

    10 == 10;
    10 != 9;
    "foobar"
    "foo bar"
    [1, 2];
    {"foo": "bar"}
    '''
    tests = [
        Target(token.LET, 'let'),
        Target(token.IDENT, 'five'),
        Target(token.ASSIGN, '='),
        Target(token.INT, '5'),
        Target(token.SEMICOLON, ';'),
        Target(token.LET, 'let'),
        Target(token.IDENT, 'ten'),
        Target(token.ASSIGN, '='),
        Target(token.INT, '10'),
        Target(token.SEMICOLON, ';'),
        Target(token.LET, 'let'),
        Target(token.IDENT, 'add'),
        Target(token.ASSIGN, '='),
        Target(token.FUNCTION, 'fn'),
        Target(token.LPAREN, '('),
        Target(token.IDENT, 'x'),
        Target(token.COMMA, ','),
        Target(token.IDENT, 'y'),
        Target(token.RPAREN, ')'),
        Target(token.LBRACE, '{'),
        Target(token.IDENT, 'x'),
        Target(token.PLUS, '+'),
        Target(token.IDENT, 'y'),
        Target(token.SEMICOLON, ';'),
        Target(token.RBRACE, '}'),
        Target(token.SEMICOLON, ';'),
        Target(token.LET, 'let'),
        Target(token.IDENT, 'result'),
        Target(token.ASSIGN, '='),
        Target(token.IDENT, 'add'),
        Target(token.LPAREN, '('),
        Target(token.IDENT, 'five'),
        Target(token.COMMA, ','),
        Target(token.IDENT, 'ten'),
        Target(token.RPAREN, ')'),
        Target(token.SEMICOLON, ';'),
        Target(token.BANG, '!'),
        Target(token.MINUS, '-'),
        Target(token.SLASH, '/'),
        Target(token.ASTERISK, '*'),
        Target(token.INT, '5'),
        Target(token.SEMICOLON, ';'),
        Target(token.INT, '5'),
        Target(token.LT, '<'),
        Target(token.INT, '10'),
        Target(token.GT, '>'),
        Target(token.INT, '5'),
        Target(token.SEMICOLON, ';'),
        Target(token.IF, 'if'),
        Target(token.LPAREN, '('),
        Target(token.INT, '5'),
        Target(token.LT, '<'),
        Target(token.INT, '10'),
        Target(token.RPAREN, ')'),
        Target(token.LBRACE, '{'),
        Target(token.RETURN, 'return'),
        Target(token.TRUE, 'true'),
        Target(token.SEMICOLON, ';'),
        Target(token.RBRACE, '}'),
        Target(token.ELSE, 'else'),
        Target(token.LBRACE, '{'),
        Target(token.RETURN, 'return'),
        Target(token.FALSE, 'false'),
        Target(token.SEMICOLON, ';'),
        Target(token.RBRACE, '}'),
        Target(token.INT, '10'),
        Target(token.EQ, '=='),
        Target(token.INT, '10'),
        Target(token.SEMICOLON, ';'),
        Target(token.INT, '10'),
        Target(token.NOT_EQ, '!='),
        Target(token.INT, '9'),
        Target(token.SEMICOLON, ';'),
        Target(token.STRING, 'foobar'),
        Target(token.STRING, 'foo bar'),
        Target(token.LBRACKET, '['),
        Target(token.INT, '1'),
        Target(token.COMMA, ','),
        Target(token.INT, '2'),
        Target(token.RBRACKET, ']'),
        Target(token.SEMICOLON, ';'),
        Target(token.LBRACE, '{'),
        Target(token.STRING, 'foo'),
        Target(token.COLON, ':'),
        Target(token.STRING, 'bar'),
        Target(token.RBRACE, '}'),
        Target(token.EOF, ''),
    ]

    l = lexer.Lexer(input)

    for i, tt in enumerate(tests):
        tok = l.next_token()
        assert tok.type == tt.expected_type
        assert tok.literal == tt.expected_literal
