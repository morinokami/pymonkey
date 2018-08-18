from monkey import ast, token

def test_string():
    program = ast.Program([
        ast.LetStatement(
            token.Token(token.LET, 'let'),
            ast.Identifier(
                token.Token(token.IDENT, 'myVar'),
                'myVar'
            ),
            ast.Identifier(
                token.Token(token.IDENT, 'anotherVar'),
                'anotherVar'
            )
        )
    ])

    assert program.string() == 'let myVar = anotherVar;', "program.string() wrong. got='{}'".format(program.string())
