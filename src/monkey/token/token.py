from typing import Dict, NewType

TokenType = NewType('TokenType', str)

ILLEGAL = 'ILLEGAL'  # add, foobar, x, y, ...
EOF = "EOF"  # 1343456

# Identifiers + literals
IDENT = 'IDENT'
INT = 'INT'
STRING = 'STRING'

# Operators
ASSIGN = '='
PLUS = '+'
MINUS = '-'
BANG = '!'
ASTERISK = '*'
SLASH = '/'

LT = '<'
GT = '>'

EQ = '=='
NOT_EQ = '!='

# Delimiters
COMMA = ','
SEMICOLON = ';'
COLON = ':'

LPAREN = '('
RPAREN = ')'
LBRACE = '{'
RBRACE = '}'
LBRACKET = '['
RBRACKET = ']'

# Keywords
FUNCTION = 'FUNCTION'
LET = 'LET'
TRUE = 'TRUE'
FALSE = 'FALSE'
IF = 'IF'
ELSE = 'ELSE'
RETURN = 'RETURN'


class Token:

    def __init__(self, type: TokenType, literal: str):
        self.type = type
        self.literal = literal

    def __str__(self):
        return '{{Type:{} Literal:{}}}'.format(self.type, self.literal)


keywords: Dict[str, TokenType] = {
    'fn': FUNCTION,
    'let': LET,
    'true': TRUE,
    'false': FALSE,
    'if': IF,
    'else': ELSE,
    'return': RETURN,
}


def lookup_ident(ident: str) -> TokenType:
    return keywords[ident] if ident in keywords else IDENT
