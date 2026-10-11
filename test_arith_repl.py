import unittest
from collections.abc import Iterator

from arith_repl import repl


class FakeInput:
    def __init__(self, lines: list[str]) -> None:
        self.lines: Iterator[str] = iter(lines)
        self.prompts: list[str] = []

    def __call__(self, prompt: str) -> str:
        self.prompts.append(prompt)
        try:
            return next(self.lines)
        except StopIteration:
            raise EOFError from None


class ArithmeticReplTest(unittest.TestCase):
    def test_evaluates_multiple_expressions(self) -> None:
        fake_input = FakeInput(["2 + 3 * 4", "20 / 5", ":quit"])
        output: list[str] = []

        repl(fake_input, output.append)

        self.assertEqual(output, ["14", "4.0"])

    def test_multiline_parentheses(self) -> None:
        fake_input = FakeInput(["(2 + 3", " * 4)", ":exit"])
        output: list[str] = []

        repl(fake_input, output.append)

        self.assertEqual(output, ["14"])
        self.assertEqual(fake_input.prompts[:2], ["math> ", "... "])

    def test_error_does_not_end_session(self) -> None:
        fake_input = FakeInput(["1 / 0", "8 - 3", ":quit"])
        output: list[str] = []

        repl(fake_input, output.append)

        self.assertTrue(output[0].startswith("error:"))
        self.assertEqual(output[1], "5")

    def test_eof_with_incomplete_expression(self) -> None:
        fake_input = FakeInput(["(1 + 2"])
        output: list[str] = []

        repl(fake_input, output.append)

        self.assertEqual(output, ["error: incomplete expression"])


if __name__ == "__main__":
    unittest.main()
