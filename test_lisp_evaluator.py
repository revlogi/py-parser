import unittest

from lisp_evaluator import Environment, LispError, evaluate, parse_expression, standard_environment


class LispEvaluatorTest(unittest.TestCase):
    def test_parser(self) -> None:
        self.assertEqual(parse_expression(" (+ 1 (* 2 3)) "), ["+", 1, ["*", 2, 3]])
        self.assertEqual(parse_expression("'(1 2 3)"), ["quote", [1, 2, 3]])

    def test_arithmetic(self) -> None:
        self.assertEqual(evaluate("(+ 1 2 (* 3 4))"), 15)
        self.assertEqual(evaluate("(- 10 3 2)"), 5)
        self.assertEqual(evaluate("(/ 20 5 2)"), 2)

    def test_if_and_comparison(self) -> None:
        self.assertEqual(evaluate("(if (> 5 2) 10 20)"), 10)
        self.assertEqual(evaluate("(if #f 10 20)"), 20)

    def test_define_in_shared_environment(self) -> None:
        environment = standard_environment()
        self.assertEqual(evaluate("(define radius 3)", environment), 3)
        self.assertEqual(evaluate("(* radius radius)", environment), 9)

    def test_lambda_and_lexical_scope(self) -> None:
        program = "(begin (define x 10) ((lambda (x y) (+ x y)) 2 3))"
        self.assertEqual(evaluate(program), 5)

    def test_named_function(self) -> None:
        program = "(begin (define square (lambda (x) (* x x))) (square 7))"
        self.assertEqual(evaluate(program), 49)

    def test_list_operations_and_quote(self) -> None:
        self.assertEqual(evaluate("(car '(10 20 30))"), 10)
        self.assertEqual(evaluate("(cdr (list 10 20 30))"), [20, 30])
        self.assertEqual(evaluate("(cons 1 '(2 3))"), [1, 2, 3])

    def test_invalid_program(self) -> None:
        with self.assertRaises(ValueError):
            parse_expression("(+ 1 2")
        with self.assertRaises(LispError):
            evaluate("missing-name")


if __name__ == "__main__":
    unittest.main()
