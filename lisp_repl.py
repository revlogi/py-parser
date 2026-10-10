from __future__ import annotations

from collections.abc import Callable
from typing import Any

from lisp_evaluator import LispError, evaluate, standard_environment

InputFunction = Callable[[str], str]
OutputFunction = Callable[[str], Any]


def format_value(value: Any) -> str:
    """Format Python values using a small amount of Lisp notation."""
    if value is True:
        return "#t"
    if value is False:
        return "#f"
    if isinstance(value, list):
        return "(" + " ".join(format_value(item) for item in value) + ")"
    if callable(value):
        return "<procedure>"
    return str(value)


def _parenthesis_balance(source: str) -> int:
    # The mini Lisp has no string literals, so counting parentheses is enough.
    return source.count("(") - source.count(")")


def repl(
    input_fn: InputFunction = input,
    output_fn: OutputFunction = print,
) -> None:
    """Run a read-evaluate-print loop with one persistent environment."""
    environment = standard_environment()
    lines: list[str] = []

    while True:
        prompt = "... " if lines else "lisp> "

        try:
            line = input_fn(prompt)
        except EOFError:
            if lines:
                output_fn("error: incomplete expression")
            return
        except KeyboardInterrupt:
            lines.clear()
            output_fn("^C")
            continue

        stripped = line.strip()
        if not lines and stripped in {":quit", ":exit"}:
            return
        if not lines and not stripped:
            continue

        lines.append(line)
        source = "\n".join(lines)
        balance = _parenthesis_balance(source)

        if balance > 0:
            continue

        lines.clear()
        if balance < 0:
            output_fn("error: unexpected ')'")
            continue

        try:
            output_fn(format_value(evaluate(source, environment)))
        except (LispError, ValueError, TypeError, ZeroDivisionError, IndexError) as error:
            output_fn(f"error: {error}")


def main() -> None:
    print("Mini Lisp REPL. Use :quit or :exit to leave.")
    repl()


if __name__ == "__main__":
    main()
