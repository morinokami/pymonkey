from .. import token


class Lexer:

    def __init__(self, input: str):
        self.input: str = input
        self.position: int = 0      # current position in input (points to current char)
        self.read_position: int = 0  # current reading position in input (after current char)
        self.ch: str = ''           # current char under examination

        self.read_char()

    def next_token(self) -> token.Token:
        tok = Lexer.new_token(token.ILLEGAL, self.ch)

        self.skip_whitespace()

        if self.ch == '=':
            if self.peek_char() == '=':
                ch = self.ch
                self.read_char()
                literal = ch + self.ch
                tok = Lexer.new_token(token.EQ, literal)
            else:
                tok = Lexer.new_token(token.ASSIGN, self.ch)
        elif self.ch == '+':
            tok = Lexer.new_token(token.PLUS, self.ch)
        elif self.ch == '-':
            tok = Lexer.new_token(token.MINUS, self.ch)
        elif self.ch == '!':
            if self.peek_char() == '=':
                ch = self.ch
                self.read_char()
                literal = ch + self.ch
                tok = Lexer.new_token(token.NOT_EQ, literal)
            else:
                tok = Lexer.new_token(token.BANG, self.ch)
        elif self.ch == '/':
            tok = Lexer.new_token(token.SLASH, self.ch)
        elif self.ch == '*':
            tok = Lexer.new_token(token.ASTERISK, self.ch)
        elif self.ch == '<':
            tok = Lexer.new_token(token.LT, self.ch)
        elif self.ch == '>':
            tok = Lexer.new_token(token.GT, self.ch)
        elif self.ch == ';':
            tok = Lexer.new_token(token.SEMICOLON, self.ch)
        elif self.ch == ':':
            tok = Lexer.new_token(token.COLON, self.ch)
        elif self.ch == '(':
            tok = Lexer.new_token(token.LPAREN, self.ch)
        elif self.ch == ')':
            tok = Lexer.new_token(token.RPAREN, self.ch)
        elif self.ch == ',':
            tok = Lexer.new_token(token.COMMA, self.ch)
        elif self.ch == '+':
            tok = Lexer.new_token(token.PLUS, self.ch)
        elif self.ch == '{':
            tok = Lexer.new_token(token.LBRACE, self.ch)
        elif self.ch == '}':
            tok = Lexer.new_token(token.RBRACE, self.ch)
        elif self.ch == '"':
            tok.type = token.STRING
            tok.literal = self.read_string()
        elif self.ch == '[':
            tok = Lexer.new_token(token.LBRACKET, self.ch)
        elif self.ch == ']':
            tok = Lexer.new_token(token.RBRACKET, self.ch)
        elif self.ch is chr(0):
            tok = Lexer.new_token(token.EOF, '')
        else:
            if Lexer.is_letter(self.ch):
                tok.literal = self.read_identifier()
                tok.type = token.lookup_ident(tok.literal)
                return tok
            elif Lexer.is_digit(self.ch):
                tok.type = token.INT
                tok.literal = self.read_number()
                return tok
            else:
                tok = Lexer.new_token(token.ILLEGAL, self.ch)

        self.read_char()

        return tok

    def skip_whitespace(self):
        while self.ch in [' ', '\t', '\n', '\r']:
            self.read_char()

    def read_char(self):
        if self.read_position >= len(self.input):
            self.ch = chr(0)
        else:
            self.ch = self.input[self.read_position]
        self.position = self.read_position
        self.read_position += 1

    def peek_char(self) -> str:
        if self.read_position >= len(self.input):
            return chr(0)
        else:
            return self.input[self.read_position]

    def read_identifier(self) -> str:
        position = self.position
        while Lexer.is_letter(self.ch):
            self.read_char()
        return self.input[position:self.position]

    def read_number(self):
        position = self.position
        while Lexer.is_digit(self.ch):
            self.read_char()
        return self.input[position:self.position]

    def read_string(self):
        position = self.position + 1
        while True:
            self.read_char()
            if self.ch == '"' or self.ch == chr(0):
                break
        return self.input[position:self.position]

    @classmethod
    def is_letter(cls, ch: str) -> bool:
        return 'a' <= ch <= 'z' or 'A' <= ch <= 'Z' or ch == '_'

    @classmethod
    def is_digit(cls, ch: str) -> bool:
        return '0' <= ch <= '9'

    @classmethod
    def new_token(cls, token_type: token.TokenType, ch: str) -> token.Token:
        return token.Token(token_type, ch)
