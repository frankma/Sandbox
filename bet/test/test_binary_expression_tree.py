from unittest import TestCase

from bet.binary_expression_tree import Plus, Minus, Times, Divide, Constant, Variable


class TestExpression(TestCase):
    def test_evaluate(self):
        env = {'x': 1, 'y': 2, 'z': 3}
        expression = Plus(Minus(Constant(1), Variable('z')), Times(Divide(Variable('x'), Constant(3)), Variable('y')))

        exp = expression.__str__()
        val = expression.evaluate(env)
        pass
