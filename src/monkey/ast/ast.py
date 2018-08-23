from abc import ABC, abstractmethod
from typing import Dict, List

from monkey import token


class Node(ABC):

    @abstractmethod
    def token_literal(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def string(self) -> str:
        raise NotImplementedError


class Statement(Node):

    @abstractmethod
    def statement_node(self):
        pass


class Expression(Node):

    @abstractmethod
    def expression_node(self):
        pass


class Program(Node):

    def __init__(self, statements: List[Statement] = None):
        if statements is None:
            statements = []
        self.statements = statements

    def token_literal(self) -> str:
        if len(self.statements) > 0:
            return self.statements[0].token_literal()
        else:
            return ''

    def string(self) -> str:
        out = ''

        for s in self.statements:
            out += s.string()

        return out


class Identifier(Expression):

    def __init__(self, token: token.Token, value: str = None):
        self.token = token
        self.value = value

    def expression_node(self):
        pass

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        return self.value


# Statements

class LetStatement(Statement):

    def __init__(self, token: token.Token, name: Identifier = None, value: Expression = None):
        self.token = token
        self.name = name
        self.value = value

    def statement_node(self):
        pass

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        out = self.token_literal() + ' '
        out += self.name.string()
        out += ' = '

        if self.value is not None:
            out += self.value.string()

        out += ';'

        return out


class ReturnStatement(Statement):

    def __init__(self, token: token.Token, return_value: Expression = None):
        self.token = token
        self.return_value = return_value

    def statement_node(self):
        pass

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        out = self.token_literal() + ' '

        if self.return_value is not None:
            out += self.return_value.string()

        out += ';'

        return out


class ExpressionStatement(Statement):

    def __init__(self, token: token.Token, expression: Expression = None):
        self.token = token
        self.expression = expression

    def statement_node(self):
        pass

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        return self.expression.string() if self.expression is not None else ''


class BlockStatement(Statement):

    def __init__(self, token: token.Token, statements: List[Statement] = None):
        self.token = token
        self.statements = statements

    def statement_node(self):
        pass

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        out = ''

        for s in self.statements:
            out += s.string()

        return out


# Expressions

class Boolean(Expression):

    def __init__(self, token: token.Token, value: bool = None):
        self.token = token
        self.value = value

    def expression_node(self):
        pass

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        return self.token.literal


class IntegerLiteral(Expression):

    def __init__(self, token: token.Token, value: int = None):
        self.token = token
        self.value = value

    def expression_node(self):
        pass

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        return self.token.literal


class PrefixExpression(Expression):

    def __init__(self, token: token.Token, operator: str = None, right: Expression = None):
        self.token = token
        self.operator = operator
        self.right = right

    def expression_node(self):
        pass

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        out = ''

        out += '('
        out += self.operator
        out += self.right.string()
        out += ')'

        return out


class InfixExpression(Expression):

    def __init__(self, token: token.Token, left: Expression = None, operator: str = None, right: Expression = None):
        self.token = token
        self.left = left
        self.operator = operator
        self.right = right

    def expression_node(self):
        pass

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        out = ''

        out += '('
        out += self.left.string()
        out += ' ' + self.operator + ' '
        out += self.right.string()
        out += ')'

        return out


class IfExpression(Expression):

    def __init__(self,
                 token: token.Token,
                 condition: Expression = None,
                 consequence: BlockStatement = None,
                 alternative: BlockStatement = None):
        self.token = token
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative

    def expression_node(self):
        pass

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        out = ''

        out += 'if'
        out += self.condition.string()
        out += ' '
        out += self.consequence.string()

        if self.alternative is not None:
            out += 'else '
            out += self.alternative.string()

        return out


class FunctionLiteral(Expression):

    def __init__(self, token: token.Token, parameters: List[Identifier] = None, body: BlockStatement = None):
        self.token = token
        self.parameters = parameters
        self.body = body

    def expression_node(self):
        pass

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        out = ''

        params: List[str] = []
        for p in self.parameters:
            params.append(p.string())

        out += self.token_literal()
        out += '('
        out += ', '.join(params)
        out += ') '
        out += self.body.string()

        return out


class CallExpression(Expression):

    def __init__(self, token: token.Token, function: Expression = None, arguments: List[Expression] = None):
        self.token = token
        self.function = function
        self.arguments = arguments

    def expression_node(self):
        pass

    def token_literal(self):
        return self.token.literal

    def string(self):
        out = ''

        args: List[str] = []
        for a in self.arguments:
            args.append(a.string())

        out += self.function.string()
        out += '('
        out += ', '.join(args)
        out += ')'

        return out


class StringLiteral(Expression):

    def __init__(self, token: token.Token, value: str = None):
        self.token = token
        self.value = value

    def expression_node(self):
        pass

    def token_literal(self):
        return self.token.literal

    def string(self):
        return self.token.literal


class ArrayLiteral(Expression):

    def __init__(self, token: token.Token, elements: List[Expression] = None):
        self.token = token
        self.elements = elements

    def expression_node(self):
        pass

    def token_literal(self):
        return self.token.literal

    def string(self):
        out = ''

        elements: List[str] = []
        for el in self.elements:
            elements.append(el.string())

        out += '['
        out += ', '.join(elements)
        out += ']'

        return out


class IndexExpression(Expression):

    def __init__(self, token: token.Token, left: Expression = None, index: Expression = None):
        self.token = token
        self.left = left
        self.index = index

    def expression_node(self):
        pass

    def token_literal(self):
        return self.token.literal

    def string(self):
        out = ''

        out += '('
        out += self.left.string()
        out += '['
        out += self.index.string()
        out += '])'

        return out


class HashLiteral(Expression):

    def __init__(self, token: token.Token, pairs: Dict[Expression, Expression] = None):
        self.token = token
        self.pairs = pairs

    def expression_node(self):
        pass

    def token_literal(self):
        return self.token.literal

    def string(self):
        out = ''

        pairs: List[str]
        for key, value in self.pairs.items():
            pairs.append(key.string() + ':' + value.string())

        out += '{'
        out += ', '.join(pairs)
        out += '}'

        return out
