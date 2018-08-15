from monkey import lexer, token

PROMPT = '>> '


def start():
    while True:
        line = input(PROMPT)
        if not line:
            return

        l = lexer.Lexer(line)

        while True:
            tok = l.next_token()
            if tok.type == token.EOF:
                break

            print(tok)
