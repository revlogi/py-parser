from __future__ import annotations

from collections.abc import Callable
from typing import Any

from arith_evaluator import evaluate

InputFunction = Callable[[str], str]
OutputFunction = Callable[[str], Any]


def _parenthesis_balance(source: str) -> int:
    return source.count("(") - source.count(")")


def repl(
    input_fn: InputFunction = input,
    output_fn: OutputFunction = print,
) -> None:
    """Run an interactive arithmetic read-evaluate-print loop."""
    lines: list[str] = []

    while True:
        prompt = "... " if lines else "math> "

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
            output_fn(str(evaluate(source)))
        except (ValueError, ZeroDivisionError) as error:
            output_fn(f"error: {error}")


def main() -> None:
    print("Arithmetic REPL. Use :quit or :exit to leave.")
    repl()


if __name__ == "__main__":
    main()
