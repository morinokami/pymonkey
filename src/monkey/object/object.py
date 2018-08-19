from abc import ABC, abstractmethod
from typing import List, NewType

from monkey import ast

ObjectType = NewType('ObjectType', str)

NULL_OBJ = 'NULL'
ERROR_OBJ = 'ERROR'

INTEGER_OBJ = 'INTEGER'
BOOLEAN_OBJ = 'BOOLEAN'

RETURN_VALUE_OBJ = 'RETURN_VALUE'

FUNCTION_OBJ = 'FUNCTION'


class Object(ABC):

    @abstractmethod
    def type(self) -> ObjectType:
        raise NotImplementedError

    @abstractmethod
    def inspect(self) -> str:
        raise NotImplementedError


class Integer(Object):

    def __init__(self, value: int):
        self.value = value

    def type(self) -> ObjectType:
        return INTEGER_OBJ

    def inspect(self) -> str:
        return str(self.value)


class Boolean(Object):

    def __init__(self, value: bool):
        self.value = value

    def type(self) -> ObjectType:
        return BOOLEAN_OBJ

    def inspect(self) -> str:
        return str(self.value).lower()


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
