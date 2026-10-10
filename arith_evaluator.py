from __future__ import annotations

import argparse
from collections.abc import Callable
from typing import TypeAlias

from parser import (
    Parser,
    between,
    char,
    chain_left,
    choice,
    fmap,
    integer,
    lazy,
    parse,
    sequence,
    spaces,
    token,
)

Number: TypeAlias = int | float
Operator: TypeAlias = Callable[[Number, Number], Number]


def symbol(value: str) -> Parser[str]:
    """Parse a symbol and any whitespace following it."""
    return token(char(value))


def _add_operator() -> Parser[Operator]:
    plus: Parser[Operator] = fmap(symbol("+"), lambda _: lambda a, b: a + b)
    minus: Parser[Operator] = fmap(symbol("-"), lambda _: lambda a, b: a - b)
    return choice(plus, minus)


def _multiply_operator() -> Parser[Operator]:
    multiply: Parser[Operator] = fmap(symbol("*"), lambda _: lambda a, b: a * b)
    divide: Parser[Operator] = fmap(symbol("/"), lambda _: lambda a, b: a / b)
    return choice(multiply, divide)


def _factor() -> Parser[Number]:
    number: Parser[Number] = token(integer)
    parenthesized = between(
        symbol("("), lazy(_expression), symbol(")")
    )
    negative = fmap(
        sequence(symbol("-"), lazy(_factor)),
        lambda result: -result[1],
    )
    positive = fmap(
        sequence(symbol("+"), lazy(_factor)),
        lambda result: result[1],
    )
    return choice(number, choice(parenthesized, choice(negative, positive)))


def _term() -> Parser[Number]:
    return chain_left(_factor(), _multiply_operator())


def _expression() -> Parser[Number]:
    return chain_left(_term(), _add_operator())


def _calculator() -> Parser[Number]:
    # Tokens consume trailing whitespace; this sequence handles leading whitespace.
    return fmap(sequence(spaces, _expression()), lambda result: result[1])


def evaluate(text: str) -> Number:
    """Evaluate an expression containing +, -, *, /, and parentheses."""
    return parse(_calculator(), text)


def main() -> None:
    argument_parser = argparse.ArgumentParser(description="Evaluate basic arithmetic")
    argument_parser.add_argument("expression", help="expression to evaluate")
    args = argument_parser.parse_args()

    try:
        print(evaluate(args.expression))
    except (ValueError, ZeroDivisionError) as error:
        argument_parser.error(str(error))


if __name__ == "__main__":
    main()
