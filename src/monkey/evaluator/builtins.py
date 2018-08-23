import copy
from typing import Dict, List

from monkey import evaluator, object


def _len(*args) -> object.Object:
    if len(args) != 1:
        return evaluator.new_error('wrong number of arguments. got={}, want=1'.format(len(args)))

    if type(args[0]) == object.Array:
        return object.Integer(len(args[0].elements))
    elif type(args[0]) == object.String:
        return object.Integer(len(args[0].value))
    else:
        return evaluator.new_error('argument to `len` not supported, got {}'.format(args[0].type()))


def puts(*args: List[object.Object]) -> object.Object:
    for arg in args:
        print(arg.inspect())

    return evaluator.NULL


def first(*args: List[object.Object]) -> object.Object:
    if len(args) != 1:
        return evaluator.new_error('wrong number of arguments. got={}, want=1', len(args))
    if args[0].type() != object.ARRAY_OBJ:
        return evaluator.new_error('argument to `first` must be ARRAY, got {}'.format(args[0].type()))

    arr = args[0]
    if len(arr.elements) > 0:
        return arr.elements[0]

    return evaluator.NULL


def last(*args: List[object.Object]) -> object.Object:
    if len(args) != 1:
        return evaluator.new_error('wrong number of arguments. got={}, want=1', len(args))
    if args[0].type() != object.ARRAY_OBJ:
        return evaluator.new_error('argument to `last` must be ARRAY, got {}'.format(args[0].type()))

    arr = args[0]
    length = len(arr.elements)
    if length > 0:
        return arr.elements[length-1]

    return evaluator.NULL


def rest(*args: List[object.Object]) -> object.Object:
    if len(args) != 1:
        return evaluator.new_error('wrong number of arguments. got={}, want=1', len(args))
    if args[0].type() != object.ARRAY_OBJ:
        return evaluator.new_error('argument to `rest` must be ARRAY, got {}'.format(args[0].type()))

    arr = args[0]
    length = len(arr.elements)
    if length > 0:
        new_elements = copy.deepcopy(arr.elements[1:length])
        return object.Array(new_elements)

    return evaluator.NULL


def push(*args: List[object.Object]) -> object.Object:
    if len(args) != 2:
        return evaluator.new_error('wrong number of arguments. got={}, want=2', len(args))
    if args[0].type() != object.ARRAY_OBJ:
        return evaluator.new_error('argument to `push` must be ARRAY, got {}'.format(args[0].type()))

    arr = args[0]

    new_elements = copy.deepcopy(arr.elements)
    new_elements.append(args[1])

    return object.Array(new_elements)


builtins: Dict[str, object.Builtin] = {
    'len': object.Builtin(
        _len
    ),
    'puts': object.Builtin(
        puts
    ),
    'first': object.Builtin(
        first
    ),
    'last': object.Builtin(
        last
    ),
    'rest': object.Builtin(
        rest
    ),
    'push': object.Builtin(
        push
    ),
}
