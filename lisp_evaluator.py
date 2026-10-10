from __future__ import annotations

import argparse
import math
from collections.abc import Callable
from typing import Any, TypeAlias

from parser import (
    Parser,
    between,
    char,
    choice,
    fmap,
    lazy,
    many,
    many1,
    parse,
    satisfy,
    sequence,
    spaces,
    token,
)

Expr: TypeAlias = int | str | list["Expr"]
Value: TypeAlias = int | float | bool | list[Any] | Callable[..., Any]


class LispError(ValueError):
    """Raised for invalid Lisp programs."""


class Environment(dict[str, Value]):
    def __init__(
        self,
        values: dict[str, Value] | None = None,
        outer: Environment | None = None,
    ) -> None:
        super().__init__(values or {})
        self.outer = outer

    def find(self, name: str) -> Environment:
        if name in self:
            return self
        if self.outer is not None:
            return self.outer.find(name)
        raise LispError(f"undefined symbol: {name}")


def _symbol(value: str) -> Parser[str]:
    return token(char(value))


def _atom_value(chars: list[str]) -> Expr:
    text = "".join(chars)
    unsigned = text[1:] if text[:1] in {"+", "-"} else text
    if unsigned.isdigit():
        return int(text)
    return text


def _atom_parser() -> Parser[Expr]:
    atom_char = satisfy(lambda c: not c.isspace() and c not in "()'")
    return token(fmap(many1(atom_char), _atom_value))


def _expression_parser() -> Parser[Expr]:
    expression_list: Parser[Expr] = between(
        _symbol("("),
        fmap(many(lazy(_expression_parser)), lambda values: values),
        _symbol(")"),
    )
    quoted: Parser[Expr] = fmap(
        sequence(_symbol("'"), lazy(_expression_parser)),
        lambda result: ["quote", result[1]],
    )
    return choice(expression_list, choice(quoted, _atom_parser()))


def parse_expression(source: str) -> Expr:
    """Parse one Lisp expression into integers, symbols, and nested lists."""
    parser = fmap(sequence(spaces, _expression_parser()), lambda result: result[1])
    return parse(parser, source)


def _require_arguments(name: str, values: tuple[Any, ...]) -> None:
    if not values:
        raise LispError(f"{name} expects at least one argument")


def _subtract(first: Value, *rest: Value) -> Value:
    if not rest:
        return -first  # type: ignore[operator]
    result = first
    for value in rest:
        result = result - value  # type: ignore[operator]
    return result


def _divide(first: Value, *rest: Value) -> Value:
    if not rest:
        return 1 / first  # type: ignore[operator]
    result = first
    for value in rest:
        result = result / value  # type: ignore[operator]
    return result


def _multiply(*values: Value) -> Value:
    result: Value = 1
    for value in values:
        result = result * value  # type: ignore[operator]
    return result


def _compare(operation: Callable[[Any, Any], bool], *values: Value) -> bool:
    _require_arguments("comparison", values)
    return all(operation(left, right) for left, right in zip(values, values[1:]))


def standard_environment() -> Environment:
    """Create an environment containing arithmetic and small list primitives."""
    return Environment(
        {
            "+": lambda *values: sum(values),
            "-": _subtract,
            "*": _multiply,
            "/": _divide,
            "=": lambda *values: _compare(lambda a, b: a == b, *values),
            "<": lambda *values: _compare(lambda a, b: a < b, *values),
            "<=": lambda *values: _compare(lambda a, b: a <= b, *values),
            ">": lambda *values: _compare(lambda a, b: a > b, *values),
            ">=": lambda *values: _compare(lambda a, b: a >= b, *values),
            "list": lambda *values: list(values),
            "car": lambda value: value[0],
            "cdr": lambda value: value[1:],
            "cons": lambda first, rest: [first, *rest],
            "null?": lambda value: value == [],
            "not": lambda value: value is False,
            "abs": abs,
            "max": max,
            "min": min,
            "sqrt": math.sqrt,
            "#t": True,
            "#f": False,
        }
    )


def evaluate_expression(expression: Expr, environment: Environment) -> Value:
    if isinstance(expression, int):
        return expression

    if isinstance(expression, str):
        return environment.find(expression)[expression]

    if not expression:
        raise LispError("cannot evaluate an empty list")

    head = expression[0]

    if head == "quote":
        if len(expression) != 2:
            raise LispError("quote expects one argument")
        return expression[1]  # type: ignore[return-value]

    if head == "if":
        if len(expression) != 4:
            raise LispError("if expects a condition and two branches")
        condition = evaluate_expression(expression[1], environment)
        branch = expression[2] if condition is not False else expression[3]
        return evaluate_expression(branch, environment)

    if head == "define":
        if len(expression) != 3 or not isinstance(expression[1], str):
            raise LispError("define expects a symbol and a value")
        value = evaluate_expression(expression[2], environment)
        environment[expression[1]] = value
        return value

    if head == "lambda":
        if len(expression) < 3 or not isinstance(expression[1], list):
            raise LispError("lambda expects a parameter list and body")
        parameters = expression[1]
        if not all(isinstance(parameter, str) for parameter in parameters):
            raise LispError("lambda parameters must be symbols")
        body = expression[2:]

        def procedure(*arguments: Value) -> Value:
            if len(arguments) != len(parameters):
                raise LispError(
                    f"lambda expects {len(parameters)} arguments, got {len(arguments)}"
                )
            local = Environment(dict(zip(parameters, arguments)), environment)
            result: Value = False
            for item in body:
                result = evaluate_expression(item, local)
            return result

        return procedure

    if head == "begin":
        result: Value = False
        for item in expression[1:]:
            result = evaluate_expression(item, environment)
        return result

    procedure = evaluate_expression(head, environment)
    if not callable(procedure):
        raise LispError(f"{head!r} is not callable")
    arguments = [evaluate_expression(item, environment) for item in expression[1:]]
    return procedure(*arguments)


def evaluate(source: str, environment: Environment | None = None) -> Value:
    """Parse and evaluate one mini Lisp expression."""
    active_environment = environment if environment is not None else standard_environment()
    return evaluate_expression(parse_expression(source), active_environment)


def main() -> None:
    argument_parser = argparse.ArgumentParser(description="Evaluate a mini Lisp expression")
    argument_parser.add_argument("expression")
    args = argument_parser.parse_args()

    try:
        print(evaluate(args.expression))
    except (LispError, ValueError, TypeError, ZeroDivisionError, IndexError) as error:
        argument_parser.error(str(error))


if __name__ == "__main__":
    main()
