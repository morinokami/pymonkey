from abc import ABC, abstractmethod
from typing import Callable, Dict, List, NewType

from monkey import ast

ObjectType = NewType('ObjectType', str)

NULL_OBJ = 'NULL'
ERROR_OBJ = 'ERROR'

INTEGER_OBJ = 'INTEGER'
BOOLEAN_OBJ = 'BOOLEAN'
STRING_OBJ = 'STRING'

RETURN_VALUE_OBJ = 'RETURN_VALUE'

FUNCTION_OBJ = 'FUNCTION'
BUILTIN_OBJ = 'BUILTIN'

ARRAY_OBJ = 'ARRAY'
HASH_OBJ = 'HASH'


class HashKey:

    def __init__(self, type: ObjectType, value: int):
        self.type = type
        self.value = value

    def __eq__(self, other):
        return type(self) == type(other) and self.type == other.type and self.value == other.value

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.value


class Hashable(ABC):

    @abstractmethod
    def hash_key(self) -> HashKey:
        raise NotImplementedError


class Object(ABC):

    @abstractmethod
    def type(self) -> ObjectType:
        raise NotImplementedError

    @abstractmethod
    def inspect(self) -> str:
        raise NotImplementedError


BuiltinFunction = NewType('BuiltinFunction', Callable[[List[Object]], Object])


class Integer(Object, Hashable):

    def __init__(self, value: int):
        self.value = value

    def type(self) -> ObjectType:
        return INTEGER_OBJ

    def inspect(self) -> str:
        return str(self.value)

    def hash_key(self) -> HashKey:
        return HashKey(self.type(), self.value)


class Boolean(Object, Hashable):

    def __init__(self, value: bool):
        self.value = value

    def type(self) -> ObjectType:
        return BOOLEAN_OBJ

    def inspect(self) -> str:
        return str(self.value).lower()

    def hash_key(self) -> HashKey:
        value = 1 if self.value else 0

        return HashKey(self.type(), value)


class Null(Object):

    def type(self) -> ObjectType:
        return NULL_OBJ

    def inspect(self) -> str:
        return 'null'


class ReturnValue(Object):

    def __init__(self, value: Object):
        self.value = value

    def type(self) -> ObjectType:
        return RETURN_VALUE_OBJ

    def inspect(self) -> str:
        return self.value.inspect()


class Error(Object):

    def __init__(self, message: str):
        self.message = message

    def type(self) -> ObjectType:
        return ERROR_OBJ

    def inspect(self) -> str:
        return 'ERROR: ' + self.message


class Function(Object):

    def __init__(self, parameters: List[ast.Identifier], body: ast.BlockStatement, env):
        self.parameters = parameters
        self.body = body
        self.env = env

    def type(self) -> ObjectType:
        return FUNCTION_OBJ

    def inspect(self) -> str:
        out = ''

        params: List[str] = []
        for p in self.parameters:
            params.append(p.string())

        out += 'fn'
        out += '('
        out += ', '.join(params)
        out += ') {\n'
        out += self.body.string()
        out += '\n}'

        return out


class String(Object, Hashable):

    def __init__(self, value: str):
        self.value = value

    def type(self):
            return STRING_OBJ

    def inspect(self):
        return self.value

    def hash_key(self) -> HashKey:
        return HashKey(self.type(), hash(self.value))


class Builtin(Object):

    def __init__(self, fn: BuiltinFunction):
        self.fn = fn

    def type(self):
        return BUILTIN_OBJ

    def inspect(self):
        return 'builtin function'


class Array(Object):

    def __init__(self, elements: List[Object]):
        self.elements = elements

    def type(self):
        return ARRAY_OBJ

    def inspect(self):
        out = ''

        elements: List[str] = []
        for e in self.elements:
            elements.append(e.inspect())

        out += '['
        out += ', '.join(elements)
        out += ']'

        return out


class HashPair:

    def __init__(self, key: Object, value: Object):
        self.key = key
        self.value = value


class Hash(Object):

    def __init__(self, pairs: Dict[HashKey, HashPair]):
        self.pairs = pairs

    def type(self):
        return HASH_OBJ

    def inspect(self):
        out = ''

        pairs: List[str] = []
        for pair in self.pairs.values():
            pairs.append('{}: {}'.format(pair.key.inspect(), pair.value.inspect()))

        out += '{'
        out += ', '.join(pairs)
        out += '}'

        return out
