from typing import List, Union

from monkey import ast, object

NULL = object.Null()
TRUE = object.Boolean(True)
FALSE = object.Boolean(False)


def eval(node: ast.Node, env: object.Environment) -> Union[object.Object, None]:

    # Statements

    if issubclass(node.__class__, ast.Program):
        return eval_program(node, env)

    elif issubclass(node.__class__, ast.BlockStatement):
        return eval_block_statement(node, env)

    elif issubclass(node.__class__, ast.ExpressionStatement):
        return eval(node.expression, env)

    elif issubclass(node.__class__, ast.ReturnStatement):
        val = eval(node.return_value, env)
        if is_error(val):
            return val
        return object.ReturnValue(val)

    elif issubclass(node.__class__, ast.LetStatement):
        val = eval(node.value, env)
        if is_error(val):
            return val
        env.set(node.name.value, val)

    # Expressions

    elif issubclass(node.__class__, ast.IntegerLiteral):
        return object.Integer(node.value)

    elif issubclass(node.__class__, ast.Boolean):
        return native_bool_to_boolean_object(node.value)

    elif issubclass(node.__class__, ast.PrefixExpression):
        right = eval(node.right, env)
        if is_error(right):
            return right
        return eval_prefix_expression(node.operator, right)

    elif issubclass(node.__class__, ast.InfixExpression):
        left = eval(node.left, env)
        if is_error(left):
            return left

        right = eval(node.right, env)
        if is_error(right):
            return right

        return eval_infix_expression(node.operator, left, right)

    elif issubclass(node.__class__, ast.IfExpression):
        return eval_if_expression(node, env)

    elif issubclass(node.__class__, ast.Identifier):
        return eval_identifier(node, env)

    elif issubclass(node.__class__, ast.FunctionLiteral):
        params = node.parameters
        body = node.body
        return object.Function(params, body, env)

    elif issubclass(node.__class__, ast.CallExpression):
        function = eval(node.function, env)
        if is_error(function):
            return function

        args = eval_expressions(node.arguments, env)
        if len(args) == 1 and is_error(args[0]):
            return args[0]

        return apply_function(function, args)

    return None


def eval_program(program: ast.Program, env: object.Environment) -> object.Object:
    result: object.Object = None

    for statement in program.statements:
        result = eval(statement, env)

        if issubclass(result.__class__, object.ReturnValue):
            return result.value
        elif issubclass(result.__class__, object.Error):
            return result

    return result


def eval_block_statement(block: ast.BlockStatement, env: object.Environment) -> object.Object:
    result: object.Object = None

    for statement in block.statements:
        result = eval(statement, env)

        if result is not None:
            rt = result.type()
            if rt == object.RETURN_VALUE_OBJ or rt == object.ERROR_OBJ:
                return result

    return result


def native_bool_to_boolean_object(input: bool) -> object.Boolean:
    return TRUE if input else FALSE


def eval_prefix_expression(operator: str, right: object.Object) -> Union[object.Object, None]:
    if operator == '!':
        return eval_bang_operator_expression(right)
    elif operator == '-':
        return eval_minus_prefix_expression(right)
    else:
        return new_error('unknown operator: {}{}', operator, right.type())


def eval_infix_expression(operator: str, left: object.Object, right: object.Object) -> Union[object.Object, None]:
    if left.type() == object.INTEGER_OBJ and right.type() == object.INTEGER_OBJ:
        return eval_integer_infix_expression(operator, left, right)
    elif operator == '==':
        return native_bool_to_boolean_object(left == right)
    elif operator == '!=':
        return native_bool_to_boolean_object(left != right)
    elif left.type() != right.type():
        return new_error('type mismatch: {} {} {}', left.type(), operator, right.type())
    else:
        return new_error('unknown operator: {} {} {}', left.type(), operator, right.type())


def eval_bang_operator_expression(right: object.Object) -> object.Object:
    if right == TRUE:
        return FALSE
    elif right == FALSE:
        return TRUE
    elif right == NULL:
        return TRUE
    else:
        return FALSE


def eval_minus_prefix_expression(right: object.Object) -> object.Object:
    if right.type() != object.INTEGER_OBJ:
        return new_error('unknown operator: -{}', right.type())

    value = right.value

    return object.Integer(-value)


def eval_integer_infix_expression(operator: str, left: object.Object, right: object.Object) -> Union[object.Object, None]:
    left_val = left.value
    right_val = right.value

    if operator == '+':
        return object.Integer(left_val + right_val)
    elif operator == '-':
        return object.Integer(left_val - right_val)
    elif operator == '*':
        return object.Integer(left_val * right_val)
    elif operator == '/':
        return object.Integer(left_val / right_val)
    elif operator == '<':
        return native_bool_to_boolean_object(left_val < right_val)
    elif operator == '>':
        return native_bool_to_boolean_object(left_val > right_val)
    elif operator == '==':
        return native_bool_to_boolean_object(left_val == right_val)
    elif operator == '!=':
        return native_bool_to_boolean_object(left_val != right_val)
    else:
        return new_error('unknown operator: {} {} {}', left.type(), operator, right.type())


def eval_if_expression(ie: ast.IfExpression, env: object.Environment) -> Union[object.Object, None]:
    condition = eval(ie.condition, env)

    if is_truthy(condition):
        return eval(ie.consequence, env)
    elif ie.alternative is not None:
        return eval(ie.alternative, env)
    else:
        return None


def eval_identifier(node: ast.Identifier, env: object.Environment) -> object.Object:
    val, ok = env.get(node.value)
    if not ok:
        return new_error('identifier not found: ' + node.value)

    return val


def is_truthy(obj: object.Object) -> bool:
    if obj == NULL:
        return False
    elif obj == TRUE:
        return True
    elif obj == FALSE:
        return False
    else:
        return True


def new_error(format: str, *a) -> object.Error:
    return object.Error(format.format(*a))


def is_error(obj: object.Object) -> bool:
    if obj is not None:
        return obj.type() == object.ERROR_OBJ
    return False


def eval_expressions(exps: List[ast.Expression], env: object.Environment) -> List[object.Object]:
    result: List[object.Object] = []

    for e in exps:
        evaluated = eval(e, env)
        if is_error(evaluated):
            return [evaluated]
        result.append(evaluated)

    return result


def apply_function(fn: object.Object, args: List[object.Object]) -> object.Object:
    if not issubclass(fn.__class__, object.Function):
        return new_error('not a function: {}'.format(fn.type()))

    extended_env = extend_function_env(fn, args)
    evaluated = eval(fn.body, extended_env)
    return unwrap_return_value(evaluated)


def extend_function_env(fn: object.Function, args: List[object.Object]) -> object.Environment:
    env = object.new_enclosed_environment(fn.env)

    for param_idx, param in enumerate(fn.parameters):
        env.set(param.value, args[param_idx])

    return env


def unwrap_return_value(obj: object.Object) -> object.Object:
    if issubclass(obj.__class__, object.ReturnValue):
        return obj.value

    return obj
