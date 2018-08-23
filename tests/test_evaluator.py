from typing import Any, NamedTuple

from monkey import evaluator, lexer, object, parser


class T(NamedTuple):
    input: str
    expected: Any


def test_eval_integer_expression():
    tests = [
        T('5', 5),
        T('10', 10),
        T('-5', -5),
        T('-10', -10),
        T('5 + 5 + 5 + 5 - 10', 10),
        T('2 * 2 * 2 * 2 * 2', 32),
        T('-50 + 100 + -50', 0),
        T('5 * 2 + 10', 20),
        T('5 + 2 * 10', 25),
        T('20 + 2 * -10', 0),
        T('50 / 2 * 2 + 10', 60),
        T('2 * (5 + 10)', 30),
        T('3 * 3 * 3 + 10', 37),
        T('3 * (3 * 3) + 10', 37),
        T('(5 + 10 * 2 + 15 / 3) * 2 + -10', 50),
    ]

    for tt in tests:
        evaluated = _test_eval(tt.input)
        _test_integer_object(evaluated, tt.expected)


def test_eval_boolean_expression():
    tests = [
        T('true', True),
        T('false', False),
        T('1 < 2', True),
        T('1 > 2', False),
        T('1 < 1', False),
        T('1 > 1', False),
        T('1 == 1', True),
        T('1 != 1', False),
        T('1 == 2', False),
        T('1 != 2', True),
        T('true == true', True),
        T('false == false', True),
        T('true == false', False),
        T('true != false', True),
        T('false != true', True),
        T('(1 < 2) == true', True),
        T('(1 < 2) == false', False),
        T('(1 > 2) == true', False),
        T('(1 > 2) == false', True),
    ]

    for tt in tests:
        evaluated = _test_eval(tt.input)
        _test_boolean_object(evaluated, tt.expected)


def test_bang_operator():
    tests = [
        T('!true', False),
        T('!false', True),
        T('!5', False),
        T('!!true', True),
        T('!!false', False),
        T('!!5', True),
    ]

    for tt in tests:
        evaluated = _test_eval(tt.input)
        _test_boolean_object(evaluated, tt.expected)


def test_if_else_expression():
    tests = [
        T('if (true) { 10 }', 10),
        T('if (false) { 10 }', None),
        T('if (1) { 10 }', 10),
        T('if (1 < 2) { 10 }', 10),
        T('if (1 > 2) { 10 }', None),
        T('if (1 > 2) { 10 } else { 20 }', 20),
        T('if (1 < 2) { 10 } else { 20 }', 10),
    ]

    for tt in tests:
        evaluated = _test_eval(tt.input)
        if issubclass(tt.expected.__class__, int):
            _test_integer_object(evaluated, tt.expected)
        else:
            _test_null_object(evaluated)


def test_return_statements():
    tests = [
        T('return 10;', 10),
        T('return 10; 9;', 10),
        T('return 2 * 5; 9;', 10),
        T('9; return 2 * 5; 9;', 10),
        T('if (10 > 1) { return 10; }', 10),
        T('''
        if (10 > 1) {
          if (10 > 1) {
            return 10;
          }
        
          return 1;
        }
        ''', 10),
        T('''
        let f = fn(x) {
          return x;
          x + 10;
        };
        f(10);
        ''', 10),
        T('''
        let f = fn(x) {
          let result = x + 10;
          return result;
          return 10;
        };
        f(10);
        ''', 20)
    ]

    for tt in tests:
        evaluated = _test_eval(tt.input)
        _test_integer_object(evaluated, tt.expected)


def test_error_handling():
    tests = [
        T(
            '5 + true;',
            'type mismatch: INTEGER + BOOLEAN',
        ),
        T(
            '5 + true; 5;',
            'type mismatch: INTEGER + BOOLEAN',
        ),
        T(
            '-true',
            'unknown operator: -BOOLEAN',
        ),
        T(
            'true + false;',
            'unknown operator: BOOLEAN + BOOLEAN',
        ),
        T(
            'true + false + true + false;',
            'unknown operator: BOOLEAN + BOOLEAN',
        ),
        T(
            '5; true + false; 5',
            'unknown operator: BOOLEAN + BOOLEAN',
        ),
        T(
            '"Hello" - "World";',
            'unknown operator: STRING - STRING',
        ),
        T(
            'if (10 > 1) { true + false; }',
            'unknown operator: BOOLEAN + BOOLEAN',
        ),
        T(
            '''
            if (10 > 1) {
              if (10 > 1) {
                return true + false;
              }
            
              return 1;
            }
            ''',
            'unknown operator: BOOLEAN + BOOLEAN'
        ),
        T(
            'foobar',
            'identifier not found: foobar'
        ),
        T(
            '{"name": "Monkey"}[fn(x) { x }];',
            'unusable as hash key: FUNCTION',
        ),
    ]

    for tt in tests:
        evaluated = _test_eval(tt.input)

        assert issubclass(evaluated.__class__, object.Error), \
            'no error object returned. got={} ({})'.format(evaluated.__class__.__name__, evaluated)
        assert evaluated.message == tt.expected, \
            'wrong error message. expected={}, got={}'.format(tt.expected, evaluated.message)


def test_let_statement():
    tests = [
        T('let a = 5; a;', 5),
        T('let a = 5 * 5; a;', 25),
        T('let a = 5; let b = a; b;', 5),
        T('let a = 5; let b = a; let c = a + b + 5; c;', 15),
    ]

    for tt in tests:
        _test_integer_object(_test_eval(tt.input), tt.expected)


def test_function_object():
    input = 'fn(x) { x + 2; };'

    fn = _test_eval(input)
    assert issubclass(fn.__class__, object.Function), \
        'object is not Function. got={} ({})'.format(fn.__class__.__name__, fn)

    assert len(fn.parameters) == 1, \
        'function has wrong parameters. Parameters={}'.format(fn.parameters)

    assert fn.parameters[0].string() == 'x', \
        "parameter is not 'x'. got={}".format(fn.parameters[0])

    expected_body = '(x + 2)'

    assert fn.body.string() == expected_body, \
        'body is not {}. got={}'.format(expected_body, fn.body.string())


def test_function_application():
    tests = [
        T('let identity = fn(x) { x; }; identity(5);', 5),
        T('let identity = fn(x) { return x; }; identity(5);', 5),
        T('let double = fn(x) { x * 2; }; double(5);', 10),
        T('let add = fn(x, y) { x + y; }; add(5, 5);', 10),
        T('let add = fn(x, y) { x + y; }; add(5 + 5, add(5, 5));', 20),
        T('fn(x) { x; }(5)', 5),
    ]

    for tt in tests:
        _test_integer_object(_test_eval(tt.input), tt.expected)


def test_enclosing_environments():
    input = '''
    let first = 10;
    let second = 10;
    let third = 10;
    
    let ourFunction = fn(first) {
      let second = 20;
    
      first + second + third;
    };
    
    ourFunction(20) + first + second;
    '''

    _test_integer_object(_test_eval(input), 70)


def test_closures():
    input = '''
    let newAdder = fn(x) {
      fn(y) { x + y };
    };
    
    let addTwo = newAdder(2);
    addTwo(2);
    '''

    _test_integer_object(_test_eval(input), 4)


def test_string_literal():
    input = '"Hello World!"'

    evaluated = _test_eval(input)
    assert issubclass(evaluated.__class__, object.String), \
        'object is not String. got={} ({})'.format(evaluated.__class__.__name__, evaluated)

    assert evaluated.value == 'Hello World!', \
        'String has wrong value. got={}'.format(evaluated.value)


def test_string_concatenation():
    input = '"Hello" + " " + "World!"'

    evaluated = _test_eval(input)
    assert issubclass(evaluated.__class__, object.String), \
        'object is not String. got={} ({})'.format(evaluated.__class__.__name__, evaluated)

    assert evaluated.value == 'Hello World!', \
        'String has wrong value. got={}'.format(evaluated.value)


def test_builtin_functions():
    tests = [
        T('len("")', 0),
        T('len("four")', 4),
        T('len("hello world")', 11),
        T('len(1)', 'argument to `len` not supported, got INTEGER'),
        T('len("one", "two")', 'wrong number of arguments. got=2, want=1'),
        T('len([1, 2, 3])', 3),
        T('len([])', 0),
        T('puts("hello", "world!")', None),
        T('first([1, 2, 3])', 1),
        T('first([])', None),
        T('first(1)', "argument to `first` must be ARRAY, got INTEGER"),
        T('last([1, 2, 3])', 3),
        T('last([])', None),
        T('last(1)', "argument to `last` must be ARRAY, got INTEGER"),
        T('rest([1, 2, 3])', [2, 3]),
        T('rest([])', None),
        T('push([], 1)', [1]),
        T('push(1, 1)', "argument to `push` must be ARRAY, got INTEGER"),
    ]

    for tt in tests:
        evaluated = _test_eval(tt.input)

        if type(tt.expected) == int:
            _test_integer_object(evaluated, tt.expected)
        elif tt.expected is None:
            _test_null_object(evaluated)
        elif type(tt.expected) == str:
            assert issubclass(evaluated.__class__, object.Error), \
                'object is not Error. got={} ({})'.format(evaluated.__class__.__name__, evaluated)
            assert evaluated.message == tt.expected, \
                "wrong error message. expected='{}', got='{}'".format(tt.expected, evaluated.message)
        elif type(tt.expected) == list and all(type(e) == int for e in tt.expected):
            assert issubclass(evaluated.__class__, object.Array), \
                'obj not Array. got={} ({})'.format(evaluated.__class__.__name__, evaluated)
            assert len(evaluated.elements) == len(tt.expected), \
                'wrong num of elements. want={}, got={}'.format(len(tt.expected), len(evaluated.elements))
            for i, expected_elem in enumerate(tt.expected):
                _test_integer_object(evaluated.elements[i], expected_elem)


def test_array_literals():
    input = '[1, 2 * 2, 3 + 3]'

    evaluated = _test_eval(input)
    assert issubclass(evaluated.__class__, object.Array), \
        'object is not Array. got={} ({})'.format(evaluated.__class__.__name__, evaluated)

    assert len(evaluated.elements) == 3, \
        'array has wrong num of elements. got={}'.format(len(evaluated.elements))

    _test_integer_object(evaluated.elements[0], 1)
    _test_integer_object(evaluated.elements[1], 4)
    _test_integer_object(evaluated.elements[2], 6)


def test_array_index_expressions():
    tests = [
        T(
            '[1, 2, 3][0]',
            1,
        ),
        T(
            '[1, 2, 3][1]',
            2,
        ),
        T(
            '[1, 2, 3][2]',
            3,
        ),
        T(
            'let i = 0; [1][i];',
            1,
        ),
        T(
            '[1, 2, 3][1 + 1];',
            3,
        ),
        T(
            'let myArray = [1, 2, 3]; myArray[2];',
            3,
        ),
        T(
            'let myArray = [1, 2, 3]; myArray[0] + myArray[1] + myArray[2];',
            6,
        ),
        T(
            'let myArray = [1, 2, 3]; let i = myArray[0]; myArray[i]',
            2,
        ),
        T(
            '[1, 2, 3][3]',
            None,
        ),
        T(
            '[1, 2, 3][-1]',
            None,
        ),
    ]

    for tt in tests:
        evaluated = _test_eval(tt.input)
        if type(tt.expected) == int:
            _test_integer_object(evaluated, tt.expected)
        else:
            _test_null_object(evaluated)


def test_hash_literals():
    input = '''
    let two = "two";
    {
        "one": 10 - 9,
        two: 1 + 1,
        "thr" + "ee": 6 / 2,
        4: 4,
        true: 5,
        false: 6
    }
    '''

    evaluated = _test_eval(input)
    assert issubclass(evaluated.__class__, object.Hash), \
        "Eval didn't return Hash. got={} ({})".format(evaluated.__class__.__name__, evaluated)

    expected = {
        object.String('one').hash_key(): 1,
        object.String('two').hash_key(): 2,
        object.String('three').hash_key(): 3,
        object.Integer(4).hash_key(): 4,
        evaluator.TRUE.hash_key(): 5,
        evaluator.FALSE.hash_key(): 6,
    }

    assert len(evaluated.pairs) == len(expected), \
        'Hash has wrong num of pairs. got={}'.format(len(evaluated.pairs))

    for expected_key, expected_value in expected.items():
        assert expected_key in evaluated.pairs, \
            'no pair for given key in pairs: ' + str(expected_key)
        pair = evaluated.pairs[expected_key]

        _test_integer_object(pair.value, expected_value)


def test_hash_index_expressions():
    tests = [
        T(
            '{"foo": 5}["foo"]',
            5,
        ),
        T(
            '{"foo": 5}["bar"]',
            None,
        ),
        T(
            'let key = "foo"; {"foo": 5}[key]',
            5,
        ),
        T(
            '{}["foo"]',
            None,
        ),
        T(
            '{5: 5}[5]',
            5,
        ),
        T(
            '{true: 5}[true]',
            5,
        ),
        T(
            '{false: 5}[false]',
            5,
        ),
    ]

    for tt in tests:
        evaluated = _test_eval(tt.input)
        if type(tt.expected) == int:
            _test_integer_object(evaluated, tt.expected)
        else:
            _test_null_object(evaluated)


def _test_eval(input: str) -> object.Object:
    l = lexer.Lexer(input)
    p = parser.Parser(l)
    program = p.parse_program()
    env = object.Environment()

    return evaluator.eval(program, env)


def _test_integer_object(obj: object.Object, expected: int):
    result = obj
    assert issubclass(result.__class__, object.Integer), \
        'object is not Integer. got={} ({})'.format(obj.__class__.__name__, obj.inspect())
    assert result.value == expected, \
        'object has wrong value. got={}, want={}'.format(result.value, expected)


def _test_boolean_object(obj: object.Object, expected: bool):
    result = obj
    assert issubclass(result.__class__, object.Boolean), \
        'object is not Boolean. got={} ({})'.format(obj.__class__.__name__, obj)
    assert result.value == expected, \
        'object has wrong value. got={}, want={}'.format(result.value, expected)


def _test_null_object(obj: object.Object):
    assert obj is evaluator.NULL, \
        'object is not NULL. got={} ({})'.format(obj.__class__.__name__, obj)
