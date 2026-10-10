import unittest
from collections.abc import Iterator

from lisp_repl import format_value, repl


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


class LispReplTest(unittest.TestCase):
    def test_persistent_environment(self) -> None:
        fake_input = FakeInput(["(define x 4)", "(+ x 3)", ":quit"])
        output: list[str] = []

        repl(fake_input, output.append)

        self.assertEqual(output, ["4", "7"])

    def test_multiline_expression(self) -> None:
        fake_input = FakeInput(["(+ 1", "   (* 2 3))", ":exit"])
        output: list[str] = []

        repl(fake_input, output.append)

        self.assertEqual(output, ["7"])
        self.assertEqual(fake_input.prompts[:2], ["lisp> ", "... "])

    def test_errors_do_not_stop_repl(self) -> None:
        fake_input = FakeInput(["unknown", "(+ 1 2)", ":quit"])
        output: list[str] = []

        repl(fake_input, output.append)

        self.assertTrue(output[0].startswith("error: undefined symbol"))
        self.assertEqual(output[1], "3")

    def test_value_formatting(self) -> None:
        self.assertEqual(format_value(True), "#t")
        self.assertEqual(format_value([1, [2, 3]]), "(1 (2 3))")


if __name__ == "__main__":
    unittest.main()
