from typing import Any, List, NamedTuple

import pytest

from monkey import ast, lexer, parser


def test_let_statements():
    class Test(NamedTuple):
        input: str
        expected_identifier: str
        expected_value: Any

    tests = [
        Test('let x = 5;', 'x', 5),
        Test('let y = true;', 'y', True),
        Test('let foobar = y;', 'foobar', 'y')
    ]

    for tt in tests:
        l = lexer.Lexer(tt.input)
        p = parser.Parser(l)
        program = p.parse_program()
        check_parser_errors(p)

        assert len(program.statements) == 1, \
            'program.statements does not contain 1 statements. got={}'.format(len(program.statements))

        stmt = program.statements[0]
        if not _test_let_statement(stmt, tt.expected_identifier):
            return

        val = stmt.value
        if not _test_literal_expression(val, tt.expected_value):
            return


def test_return_statements():
    class Test(NamedTuple):
        input: str
        expected_value: Any

    tests = [
        Test('return 5;', 5),
        Test('return true;', True),
        Test('return foobar;', 'foobar'),
    ]

    for tt in tests:
        l = lexer.Lexer(tt.input)
        p = parser.Parser(l)
        program = p.parse_program()
        check_parser_errors(p)

        assert len(program.statements) == 1, \
            'program.statements does not contain 1 statements. got={}'.format(len(program.statements))

        return_stmt = program.statements[0]
        assert issubclass(return_stmt.__class__, ast.ReturnStatement), \
            'stmt not ast.ReturnStatement. got={}'.format(return_stmt.__class__.__name__)
        assert return_stmt.token_literal() == 'return', \
            "return_stmt.token_literal not 'return', got {}".format(return_stmt.token_literal())
        if _test_literal_expression(return_stmt.return_value, tt.expected_value):
            return


def test_identifier_expression():
    input = 'foobar;'

    l = lexer.Lexer(input)
    p = parser.Parser(l)
    program = p.parse_program()
    check_parser_errors(p)

    assert len(program.statements) == 1, \
        'program has not enough statements. got={}'.format(len(program.statements))

    stmt = program.statements[0]
    assert issubclass(stmt.__class__, ast.ExpressionStatement), \
        'program statements[0] is not ast.ExpressionStatement. got={}'.format(stmt.__class__.__name__)

    ident = stmt.expression
    assert ident.value == 'foobar', 'ident.value not {}. got={}'.format('foobar', ident.value)
    assert ident.token_literal() == 'foobar', \
        'ident.token_literal not {}. got={}'.format('foobar', ident.token_literal())


def test_integer_literal_expression():
    input = '5;'

    l = lexer.Lexer(input)
    p = parser.Parser(l)
    program = p.parse_program()
    check_parser_errors(p)

    assert len(program.statements) == 1, \
        'program has not enough statements. got={}'.format(len(program.statements))

    stmt = program.statements[0]
    assert issubclass(stmt.__class__, ast.ExpressionStatement), \
        'program statements[0] is not ast.ExpressionStatement. got={}'.format(stmt.__class__.__name__)

    literal = stmt.expression
    assert issubclass(literal.__class__, ast.IntegerLiteral), \
        'exp not ast.IntegerLiteral. got={}'.format(literal.__class__.__name__)
    assert literal.value == 5, 'literal.value not {}, got={}'.format(5, literal.value)
    assert literal.token_literal() == '5', 'literal.token_literal not {}. got={}'.format('5', literal.token_literal())


def test_parsing_prefix_expression():
    class PrefixTest(NamedTuple):
        input: str
        operator: str
        value: Any

    prefix_tests = [
        PrefixTest('!5;', '!', 5),
        PrefixTest('-15;', '-', 15),
        PrefixTest('!true', '!', True),
        PrefixTest('!false', '!', False),
    ]

    for tt in prefix_tests:
        l = lexer.Lexer(tt.input)
        p = parser.Parser(l)
        program = p.parse_program()
        check_parser_errors(p)

        assert len(program.statements) == 1, \
            'program.statements does not contain {} statements. got={}'.format(1, len(program.statements))

        stmt = program.statements[0]
        assert issubclass(stmt.__class__, ast.ExpressionStatement), \
            'program statements[0] is not ast.ExpressionStatement. got={}'.format(stmt.__class__.__name__)

        exp = stmt.expression
        assert issubclass(exp.__class__, ast.PrefixExpression), \
            'stmt is not ast.PrefixExpression. got={}'.format(stmt.expression.__class__.__name__)
        assert exp.operator == tt.operator, "exp.operator is not '{}'. got={}".format(tt.operator, exp.operator)
        assert _test_literal_expression(exp.right, tt.value)


def test_parsing_infix_expressions():
    class InfixTest(NamedTuple):
        input: str
        left_value: int
        operator: str
        right_value: int

    infix_tests = [
        InfixTest('5 + 5;', 5, '+', 5),
        InfixTest('5 - 5;', 5, '-', 5),
        InfixTest('5 * 5;', 5, '*', 5),
        InfixTest('5 / 5;', 5, '/', 5),
        InfixTest('5 > 5;', 5, '>', 5),
        InfixTest('5 < 5;', 5, '<', 5),
        InfixTest('5 == 5;', 5, '==', 5),
        InfixTest('5 != 5;', 5, '!=', 5),
        InfixTest('true == true', True, '==', True),
        InfixTest('true != false', True, '!=', False),
        InfixTest('false == false', False, '==', False)
    ]

    for tt in infix_tests:
        l = lexer.Lexer(tt.input)
        p = parser.Parser(l)
        program = p.parse_program()
        check_parser_errors(p)

        assert len(program.statements) == 1, \
            'program.statements does not contain {} statements. got={}'.format(1, len(program.statements))

        stmt = program.statements[0]
        assert issubclass(stmt.__class__, ast.ExpressionStatement), \
            'program.statement[0] is not ast.ExpressionStatement. got={}'.format(stmt.__class__.__name__)

        assert _test_infix_expression(stmt.expression, tt.left_value, tt.operator, tt.right_value)


def test_operator_precedence_parsing():
    class Test(NamedTuple):
        input: str
        expected: str

    tests = [
        Test(
            '-a * b',
            '((-a) * b)',
        ),
        Test(
            '!-a',
            '(!(-a))',
        ),
        Test(
            'a + b + c',
            '((a + b) + c)',
        ),
        Test(
            'a + b - c',
            '((a + b) - c)',
        ),
        Test(
            'a * b * c',
            '((a * b) * c)',
        ),
        Test(
            'a * b / c',
            '((a * b) / c)',
        ),
        Test(
            'a + b / c',
            '(a + (b / c))',
        ),
        Test(
            'a + b * c + d / e - f',
            '(((a + (b * c)) + (d / e)) - f)',
        ),
        Test(
            '3 + 4; -5 * 5',
            '(3 + 4)((-5) * 5)',
        ),
        Test(
            '5 > 4 == 3 < 4',
            '((5 > 4) == (3 < 4))',
        ),
        Test(
            '5 < 4 != 3 > 4',
            '((5 < 4) != (3 > 4))',
        ),
        Test(
            '3 + 4 * 5 == 3 * 1 + 4 * 5',
            '((3 + (4 * 5)) == ((3 * 1) + (4 * 5)))',
        ),
        Test(
            'true',
            'true',
        ),
        Test(
            'false',
            'false',
        ),
        Test(
            '3 > 5 == false',
            '((3 > 5) == false)',
        ),
        Test(
            '3 < 5 == true',
            '((3 < 5) == true)',
        ),
        Test(
            '1 + (2 + 3) + 4',
            '((1 + (2 + 3)) + 4)',
        ),
        Test(
            '(5 + 5) * 2',
            '((5 + 5) * 2)',
        ),
        Test(
            '2 / (5 + 5)',
            '(2 / (5 + 5))',
        ),
        Test(
            '(5 + 5) * 2 * (5 + 5)',
            '(((5 + 5) * 2) * (5 + 5))',
        ),
        Test(
            '-(5 + 5)',
            '(-(5 + 5))',
        ),
        Test(
            '!(true == true)',
            '(!(true == true))',
        ),
        Test(
            'a + add(b * c) + d',
            '((a + add((b * c))) + d)',
        ),
        Test(
            'add(a, b, 1, 2 * 3, 4 + 5, add(6, 7 * 8))',
            'add(a, b, 1, (2 * 3), (4 + 5), add(6, (7 * 8)))',
        ),
        Test(
            'add(a + b + c * d / f + g)',
            'add((((a + b) + ((c * d) / f)) + g))',
        ),
        Test(
            'a * [1, 2, 3, 4][b * c] * d',
            '((a * ([1, 2, 3, 4][(b * c)])) * d)',
        ),
        Test(
            'add(a * b[2], b[1], 2 * [1, 2][1])',
            'add((a * (b[2])), (b[1]), (2 * ([1, 2][1])))',
        ),
    ]

    for tt in tests:
        l = lexer.Lexer(tt.input)
        p = parser.Parser(l)
        program = p.parse_program()
        check_parser_errors(p)

        actual = program.string()
        assert actual == tt.expected, "expected='{}', got='{}'".format(tt.expected, actual)


def test_boolean_expression():
    class Test(NamedTuple):
        input: str
        expected_boolean: bool

    tests = [
        Test('true;', True),
        Test('false;', False),
    ]

    for tt in tests:
        l = lexer.Lexer(tt.input)
        p = parser.Parser(l)
        program = p.parse_program()
        check_parser_errors(p)

        assert len(program.statements) == 1, \
            'program has not enough statements. got={}'.format(len(program.statements))

        stmt = program.statements[0]
        assert issubclass(stmt.__class__, ast.ExpressionStatement), \
            'program.statements[0] is not ast.ExpressionStatement. got={}'.format(stmt.__class__.__name__)

        boolean = stmt.expression
        assert issubclass(boolean.__class__, ast.Boolean), \
            'exp not ast.Boolean. got={}'.format(boolean.__class__.__name__)
        assert boolean.value == tt.expected_boolean, \
            'boolean.value not {}. got={}'.format(tt.expected_boolean, boolean.value)


def test_if_expression():
    input = 'if (x < y) { x }'

    l = lexer.Lexer(input)
    p = parser.Parser(l)
    program = p.parse_program()
    check_parser_errors(p)

    assert len(program.statements) == 1, \
        'program.statements does not contain {} statements. got={}'.format(1, len(program.statements))

    stmt = program.statements[0]
    assert issubclass(stmt.__class__, ast.ExpressionStatement), \
        'program.statements[0] is not ast.ExpressionStatement. got={}'.format(stmt.__class__.__name__)

    exp = stmt.expression
    assert issubclass(exp.__class__, ast.IfExpression), \
        'stmt.expression is not ast.IfExpression. got={}'.format(exp.__class__.__name__)

    if not _test_infix_expression(exp.condition, 'x', '<', 'y'):
        return

    assert len(exp.consequence.statements) == 1, \
        'consequence is not 1 statements. got={}'.format(len(exp.consequence.statements))

    consequnce = exp.consequence.statements[0]
    assert issubclass(consequnce.__class__, ast.ExpressionStatement), \
        'statements[0] is not ast.ExpressionStatement. got={}'.format(consequnce.__class__.__name__)

    if not _test_identifier(consequnce.expression, 'x'):
        return

    assert exp.alternative is None, 'exp.alternative was not None. got={}'.format(exp.alternative)


def test_if_else_expression():
    input = 'if (x < y) { x } else { y }'

    l = lexer.Lexer(input)
    p = parser.Parser(l)
    program = p.parse_program()
    check_parser_errors(p)

    assert len(program.statements) == 1, \
        'program.statements does not contain {} statements. got={}'.format(1, len(program.statements))

    stmt = program.statements[0]
    assert issubclass(stmt.__class__, ast.ExpressionStatement), \
        'program.statements[0] is not ast.ExpressionStatement. got={}'.format(stmt.__class__.__name__)

    exp = stmt.expression
    assert issubclass(exp.__class__, ast.IfExpression), \
        'stmt.expression is not ast.IfExpression. got={}'.format(exp.__class__.__name__)

    if not _test_infix_expression(exp.condition, 'x', '<', 'y'):
        return

    assert len(exp.consequence.statements) == 1, \
        'consequence is not 1 statements. got={}'.format(len(exp.consequence.statements))

    consequnce = exp.consequence.statements[0]
    assert issubclass(consequnce.__class__, ast.ExpressionStatement), \
        'statements[0] is not ast.ExpressionStatement. got={}'.format(consequnce.__class__.__name__)

    if not _test_identifier(consequnce.expression, 'x'):
        return

    assert len(exp.alternative.statements) == 1, \
        'exp.alternative.statements does not contain 1 statements. got={}'.format(len(exp.alternative.statements))

    alternative = exp.alternative.statements[0]
    assert issubclass(alternative.__class__, ast.ExpressionStatement), \
        'statements[0] is not ast.ExpressionStatement. got={}'.format(alternative.__class__.__name__)

    if not _test_identifier(alternative.expression, 'y'):
        return


def test_function_literal_parsing():
    input = 'fn(x, y) { x + y; }'

    l = lexer.Lexer(input)
    p = parser.Parser(l)
    program = p.parse_program()
    check_parser_errors(p)

    assert len(program.statements) == 1, \
        'program.statements does not contain {} statements. got={}'.format(1, len(program.statements))

    stmt = program.statements[0]
    assert issubclass(stmt.__class__, ast.ExpressionStatement), \
        'program.statements[0] is not ast.ExpressionStatement. got={}'.format(stmt.__class__.__name__)

    function = stmt.expression
    assert issubclass(function.__class__, ast.FunctionLiteral), \
        'stmt.expression is not ast.FunctionLiteral. got={}'.format(function.__class__.__name__)

    assert len(function.parameters) == 2, \
        'function literal parameters wrong. want 2, got={}'.format(len(function.parameters))

    _test_literal_expression(function.parameters[0], 'x')
    _test_literal_expression(function.parameters[1], 'y')

    assert len(function.body.statements) == 1, \
        'function.body.statements has not 1 statements. got={}'.format(len(function.body.statements))

    body_stmt = function.body.statements[0]
    assert issubclass(body_stmt.__class__, ast.ExpressionStatement), \
        'function body stmt is not ast.ExpressionStatement. got={}'.format(body_stmt.__class__.__name__)

    _test_infix_expression(body_stmt.expression, 'x', '+', 'y')


def test_function_parameter_parsing():
    class Test(NamedTuple):
        input: str
        expected_params: List[str]

    tests = [
        Test('fn() {};', []),
        Test('fn(x) {};', ['x']),
        Test('fn(x, y, z) {};', ['x', 'y', 'z']),
    ]

    for tt in tests:
        l = lexer.Lexer(tt.input)
        p = parser.Parser(l)
        program = p.parse_program()
        check_parser_errors(p)

        stmt = program.statements[0]
        function = stmt.expression

        assert len(function.parameters) == len(tt.expected_params), \
            'length parameters wrong. want {}, got={}'.format(len(tt.expected_params), len(function.parameters))

        for i, ident in enumerate(tt.expected_params):
            _test_literal_expression(function.parameters[i], ident)


def test_call_expression_parsing():
    input = 'add(1, 2 * 3, 4 + 5);'

    l = lexer.Lexer(input)
    p = parser.Parser(l)
    program = p.parse_program()
    check_parser_errors(p)

    assert len(program.statements) == 1, \
        'program.statements does not contain {} statements. got={}'.format(1, len(program.statements))

    stmt = program.statements[0]
    assert issubclass(stmt.__class__, ast.ExpressionStatement), \
        'program.statements[0] is not ast.ExpressionStatement. got={}'.format(stmt.__class__.__name__)

    exp = stmt.expression
    assert issubclass(exp.__class__, ast.CallExpression), \
        'stmt.expression is not ast.CallExpression. got={}'.format(exp.__class__.__name__)

    if not _test_identifier(exp.function, 'add'):
        return

    assert len(exp.arguments) == 3, 'wrong length of arguments. got={}'.format(len(exp.arguments))

    _test_literal_expression(exp.arguments[0], 1)
    _test_infix_expression(exp.arguments[1], 2, '*', 3)
    _test_infix_expression(exp.arguments[2], 4, '+', 5)


def test_string_literal_expression():
    input = '"hello world";'

    l = lexer.Lexer(input)
    p = parser.Parser(l)
    program = p.parse_program()
    check_parser_errors(p)

    stmt = program.statements[0]
    literal = stmt.expression
    assert issubclass(literal.__class__, ast.StringLiteral), \
        'exp not ast.StringLiteral. got={}'.format(stmt.expression.__class__.__name__)
    assert literal.value == 'hello world', \
        "literal.value not '{}'. got='{}'".format('hello world', literal.value)


def test_parsing_empty_array_literals():
    input = '[]'

    l = lexer.Lexer(input)
    p = parser.Parser(l)
    program = p.parse_program()
    check_parser_errors(p)

    stmt = program.statements[0]
    array = stmt.expression
    assert issubclass(array.__class__, ast.ArrayLiteral), \
        'exp not ast.ArrayLiteral. got={}'.format(array.__class__.__name__)

    assert len(array.elements) == 0, \
        'len(array.Elements) not 0. got={}'.format(len(array.elements))


def test_parsing_array_literals():
    input = '[1, 2 * 2, 3 + 3]'

    l = lexer.Lexer(input)
    p = parser.Parser(l)
    program = p.parse_program()
    check_parser_errors(p)

    stmt = program.statements[0]
    array = stmt.expression
    assert issubclass(array.__class__, ast.ArrayLiteral), \
        'exp not ast.ArrayLiteral. got={}'.format(array.__class__.__name__)

    assert len(array.elements) == 3, \
        'len(array.Elements) not 3. got={}'.format(len(array.elements))

    _test_integer_literal(array.elements[0], 1)
    _test_infix_expression(array.elements[1], 2, '*', 2)
    _test_infix_expression(array.elements[2], 3, '+', 3)


def test_parsing_index_expressions():
    input = 'myArray[1 + 1]'

    l = lexer.Lexer(input)
    p = parser.Parser(l)
    program = p.parse_program()
    check_parser_errors(p)

    stmt = program.statements[0]
    index_exp = stmt.expression
    assert issubclass(index_exp.__class__, ast.IndexExpression), \
        'exp not ast.IndexExpression. got={}'.format(index_exp.__class__.__name__)

    assert _test_identifier(index_exp.left, 'myArray')

    assert _test_infix_expression(index_exp.index, 1, '+', 1)


def test_parsing_empty_hash_literal():
    input = '{}'

    l = lexer.Lexer(input)
    p = parser.Parser(l)
    program = p.parse_program()
    check_parser_errors(p)

    stmt = program.statements[0]
    hash = stmt.expression
    assert issubclass(hash.__class__, ast.HashLiteral), \
        'exp not ast.HashLiteral. got={}'.format(hash.__class__.__name__)

    assert len(hash.pairs) == 0, \
        'hash.Pairs has wrong length. got={}'.format(len(hash.pairs))


def test_parsing_hash_literals_string_keys():
    input = '{"one": 1, "two": 2, "three": 3}'

    l = lexer.Lexer(input)
    p = parser.Parser(l)
    program = p.parse_program()
    check_parser_errors(p)

    stmt = program.statements[0]
    hash = stmt.expression
    assert issubclass(hash.__class__, ast.HashLiteral), \
        'exp not ast.HashLiteral. got={}'.format(hash.__class__.__name__)

    expected = {
        'one': 1,
        'two': 2,
        'three': 3,
    }

    assert len(hash.pairs) == len(expected), \
        'hash.Pairs has wrong length. got={}'.format(len(hash.pairs))

    for key, value in hash.pairs.items():
        assert issubclass(key.__class__, ast.StringLiteral), \
            'key is not ast.StringLiteral. got={}'.format(key.__class__.__name__)

        assert key.string() in expected
        expected_value = expected[key.string()]

        _test_integer_literal(value, expected_value)


def test_parsing_hash_literals_boolean_keys():
    input = '{true: 1, false: 2}'

    l = lexer.Lexer(input)
    p = parser.Parser(l)
    program = p.parse_program()
    check_parser_errors(p)

    stmt = program.statements[0]
    hash = stmt.expression
    assert issubclass(hash.__class__, ast.HashLiteral), \
        'exp not ast.HashLiteral. got={}'.format(hash.__class__.__name__)

    expected = {
        'true': 1,
        'false': 2,
    }

    assert len(hash.pairs) == len(expected), \
        'hash.Pairs has wrong length. got={}'.format(len(hash.pairs))

    for key, value in hash.pairs.items():
        assert issubclass(key.__class__, ast.Boolean), \
            'key is not ast.Boolean. got={}'.format(key.__class__.__name__)

        assert key.string() in expected
        expected_value = expected[key.string()]
        _test_integer_literal(value, expected_value)


def test_parsing_hash_literals_integer_keys():
    input = '{1: 1, 2: 2, 3: 3}'

    l = lexer.Lexer(input)
    p = parser.Parser(l)
    program = p.parse_program()
    check_parser_errors(p)

    stmt = program.statements[0]
    hash = stmt.expression
    assert issubclass(hash.__class__, ast.HashLiteral), \
        'exp not ast.HashLiteral. got={}'.format(hash.__class__.__name__)

    expected = {
        '1': 1,
        '2': 2,
        '3': 3,
    }

    assert len(hash.pairs) == len(expected), \
        'hash.Pairs has wrong length. got={}'.format(len(hash.pairs))

    for key, value in hash.pairs.items():
        assert issubclass(key.__class__, ast.IntegerLiteral), \
            'key is not ast.IntegerLiteral. got={}'.format(key.__class__.__name__)

        assert key.string() in expected
        expected_value = expected[key.string()]
        _test_integer_literal(value, expected_value)


def test_parsing_hash_literals_integer_keys():
    input = '{"one": 0 + 1, "two": 10 - 8, "three": 15 / 5}'

    l = lexer.Lexer(input)
    p = parser.Parser(l)
    program = p.parse_program()
    check_parser_errors(p)

    stmt = program.statements[0]
    hash = stmt.expression
    assert issubclass(hash.__class__, ast.HashLiteral), \
        'exp not ast.HashLiteral. got={}'.format(hash.__class__.__name__)

    assert len(hash.pairs) == 3, \
        'hash.Pairs has wrong length. got={}'.format(len(hash.pairs))

    tests = {
        'one': lambda e: _test_infix_expression(e, 0, '+', 1),
        'two': lambda e: _test_infix_expression(e, 10, '-', 8),
        'three': lambda e: _test_infix_expression(e, 15, '/', 5),
    }

    for key, value in hash.pairs.items():
        assert issubclass(key.__class__, ast.StringLiteral), \
            'key is not ast.StringLiteral. got={}'.format(key.__class__.__name__)

        assert key.string() in tests, \
            "No test function for key '{}' found".format(key.string())
        test_func = tests[key.string()]

        test_func(value)


def _test_let_statement(s: ast.Statement, name: str):
    assert s.token_literal() == 'let', "s.token_literal not 'let'. got='{}'".format(s.token_literal())
    assert issubclass(s.__class__, ast.LetStatement), 's not ast.LetStatement. got={}'.format(s.__class__.__name__)
    assert s.name.value == name, "letStmt.name.value not '{}'. got={}".format(name, s.name.value)
    assert s.name.token_literal() == name, \
        "letStmt.name.token_literal() not '{}'. got={}".format(name, s.name.token_literal())


def _test_infix_expression(exp: ast.Expression, left: Any, operator: str, right: Any) -> bool:
    op_exp = exp
    assert issubclass(op_exp.__class__, ast.InfixExpression), \
        'exp is not ast.InfixExpression. got={}({})'.format(exp.__class__.__name__, exp)

    if not _test_literal_expression(op_exp.left, left):
        return False

    if op_exp.operator != operator:
        pytest.exit("exp.operator is not '{}'".format(operator, op_exp.operator))

    if not _test_literal_expression(op_exp.right, right):
        return False

    return True


def _test_literal_expression(exp: ast.Expression, expected: Any) -> bool:
    if type(expected) == int:
        return _test_integer_literal(exp, expected)
    elif type(expected) == str:
        return _test_identifier(exp, expected)
    elif type(expected) == bool:
        return _test_boolean_literal(exp, expected)

    pytest.exit('type of exp not handled. got={}'.format(exp.__class__.__name__))

    return False


def _test_integer_literal(il: ast.Expression, value: int) -> bool:
    integ = il
    assert issubclass(integ.__class__, ast.IntegerLiteral), \
        'il not ast.IntegerLiteral. got={}'.format(il.__class__.__name__)

    assert integ.value == value, 'integ.value not {}. got={}'.format(value, integ.value)

    assert integ.token_literal() == '{}'.format(value), \
        'integ.token_literal not {}. got={}'.format(value, integ.token_literal())

    return True


def _test_identifier(exp: ast.Expression, value: str) -> bool:
    ident = exp
    assert issubclass(ident.__class__, ast.Identifier), \
        'exp not ast.Identifier. got={}'.format(ident.__class__.__name__)

    assert ident.value == value, 'ident.value not {}. got={}'.format(value, ident.value)

    assert ident.token_literal() == value, 'ident.token_literal not {}. got={}'.format(value, ident.token_literal())

    return True


def _test_boolean_literal(exp: ast.Expression, value: bool):
    bo = exp
    assert issubclass(bo.__class__, ast.Boolean), 'exp not ast.Boolean. got={}'.format(bo.__class__.__name__)

    assert bo.value == value, 'bo.value not {}. got={}'.format(value, bo.value)

    assert bo.token_literal() == str(value).lower(), 'bo.token_literal not {}. got={}'.format(value, bo.token_literal())

    return True


def check_parser_errors(p: parser.Parser):
    errors = p.errors
    if len(errors) == 0:
        return

    messages = ['parser has {} errors'.format(len(errors))]
    for msg in errors:
        messages.append("parser error: '{}'".format(msg))

    pytest.exit('\n'.join(messages))
