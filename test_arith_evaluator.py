import unittest

from arith_evaluator import evaluate


class EvaluatorTest(unittest.TestCase):
    def test_integer(self) -> None:
        self.assertEqual(evaluate("42"), 42)

    def test_operator_precedence(self) -> None:
        self.assertEqual(evaluate("2 + 3 * 4"), 14)

    def test_parentheses(self) -> None:
        self.assertEqual(evaluate("(2 + 3) * 4"), 20)

    def test_left_associativity(self) -> None:
        self.assertEqual(evaluate("20 / 5 / 2"), 2)
        self.assertEqual(evaluate("10 - 3 - 2"), 5)

    def test_unary_operators(self) -> None:
        self.assertEqual(evaluate("-3 * -(2 + 1)"), 9)
        self.assertEqual(evaluate("+7"), 7)

    def test_whitespace(self) -> None:
        self.assertEqual(evaluate("  8 + 2  "), 10)

    def test_invalid_expression(self) -> None:
        with self.assertRaises(ValueError):
            evaluate("2 +")
        with self.assertRaises(ValueError):
            evaluate("2 3")

    def test_division_by_zero(self) -> None:
        with self.assertRaises(ZeroDivisionError):
            evaluate("1 / 0")


if __name__ == "__main__":
    unittest.main()
