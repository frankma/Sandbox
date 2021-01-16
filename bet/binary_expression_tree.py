from typing import Dict


class Expression(object):
    def __str__(self):
        raise NotImplemented

    def evaluate(self, env: Dict):
        raise NotImplemented

    pass


class BinaryOperator(Expression):
    def __init__(self, left: Expression, right: Expression):
        self.left = left  # type: Expression
        self.right = right  # type: Expression
        pass


class Plus(BinaryOperator):
    def __str__(self):
        return self.left.__str__() + ' + ' + self.right.__str__()

    def evaluate(self, env: Dict):
        return self.left.evaluate(env) + self.right.evaluate(env)


class Minus(BinaryOperator):
    def __str__(self):
        return self.left.__str__() + ' - ' + self.right.__str__()

    def evaluate(self, env: Dict):
        return self.left.evaluate(env) - self.right.evaluate(env)


class Times(BinaryOperator):
    def __str__(self):
        left_str = '(' + self.left.__str__() + ')' if isinstance(self.left, BinaryOperator) else self.left.__str__()
        right_str = '(' + self.right.__str__() + ')' if isinstance(self.right, BinaryOperator) else self.right.__str__()
        return left_str + ' * ' + right_str

    def evaluate(self, env: Dict):
        return self.left.evaluate(env) * self.right.evaluate(env)


class Divide(BinaryOperator):
    def __str__(self):
        left_str = '(' + self.left.__str__() + ')' if isinstance(self.left, BinaryOperator) else self.left.__str__()
        right_str = '(' + self.right.__str__() + ')' if isinstance(self.right, BinaryOperator) else self.right.__str__()
        return left_str + ' / ' + right_str

    def evaluate(self, env: Dict):
        return self.left.evaluate(env) / self.right.evaluate(env)


class UnaryOperator(Expression):
    def __init__(self, value: Expression):
        self.value = value
        pass


class Operand(Expression):
    def __init__(self, value):
        self.value = value
        pass


class Constant(Operand):
    def __str__(self):
        return self.value.__str__()

    def evaluate(self, env: Dict):
        return self.value


class Variable(Operand):
    def __str__(self):
        return self.value.__str__()

    def evaluate(self, env: Dict):
        return env[self.value]
