from __future__ import annotations

from collections.abc import Callable
from typing import TypeAlias, TypeVar

T = TypeVar("T")
U = TypeVar("U")

ParseResult: TypeAlias = tuple[T, int] | None
Parser: TypeAlias = Callable[[str, int], ParseResult[T]]


def satisfy(predicate: Callable[[str], bool]) -> Parser[str]:
    def parser(text: str, pos: int) -> ParseResult[str]:
        if 0 <= pos < len(text) and predicate(text[pos]):
            return text[pos], pos + 1
        return None

    return parser


def char(expected: str) -> Parser[str]:
    return satisfy(lambda c: c == expected)


def fmap(parser: Parser[T], f: Callable[[T], U]) -> Parser[U]:
    def new_parser(text: str, pos: int) -> ParseResult[U]:
        result = parser(text, pos)

        if result is None:
            return None

        value, new_pos = result
        return f(value), new_pos

    return new_parser


def sequence(p1: Parser[T], p2: Parser[U]) -> Parser[tuple[T, U]]:
    def parser(text: str, pos: int) -> ParseResult[tuple[T, U]]:
        result1 = p1(text, pos)
        if result1 is None:
            return None

        value1, next_pos = result1
        result2 = p2(text, next_pos)
        if result2 is None:
            return None

        value2, pos = result2

        return (value1, value2), pos

    return parser


def choice(p1: Parser[T], p2: Parser[T]) -> Parser[T]:
    def parser(text: str, pos: int) -> ParseResult[T]:
        result = p1(text, pos)
        if result is not None:
            return result

        return p2(text, pos)

    return parser


def many(parser: Parser[T]) -> Parser[list[T]]:
    def new_parser(text: str, pos: int) -> ParseResult[list[T]]:
        values: list[T] = []

        while True:
            result = parser(text, pos)
            if result is None:
                break

            value, new_pos = result
            if new_pos == pos:
                break

            values.append(value)
            pos = new_pos

        return values, pos

    return new_parser


def many1(parser: Parser[T]) -> Parser[list[T]]:
    def new_parser(text: str, pos: int) -> ParseResult[list[T]]:
        first = parser(text, pos)
        if first is None:
            return None

        value, pos = first
        rest_result = many(parser)(text, pos)

        assert rest_result is not None
        rest, pos = rest_result

        return [value, *rest], pos

    return new_parser


digit: Parser[str] = satisfy(str.isdigit)

integer: Parser[int] = fmap(many1(digit), lambda chars: int("".join(chars)))

spaces: Parser[list[str]] = many(satisfy(str.isspace))


def token(parser: Parser[T]) -> Parser[T]:
    return fmap(sequence(parser, spaces), lambda result: result[0])


L = TypeVar("L")
R = TypeVar("R")


def between(left: Parser[L], parser: Parser[T], right: Parser[R]) -> Parser[T]:
    combined = sequence(sequence(left, parser), right)
    return fmap(combined, lambda result: result[0][1])


def chain_left(
    value_parser: Parser[T], op_parser: Parser[Callable[[T, T], T]]
) -> Parser[T]:
    def parser(text: str, pos: int) -> ParseResult[T]:
        first = value_parser(text, pos)

        if first is None:
            return None

        value, pos = first

        while True:
            op_result = op_parser(text, pos)

            if op_result is None:
                break

            op, next_pos = op_result

            rhs_result = value_parser(text, next_pos)

            if rhs_result is None:
                return None

            rhs, new_pos = rhs_result
            if new_pos == pos:
                raise ValueError("chain_left parser consumed no input")

            pos = new_pos
            value = op(value, rhs)

        return value, pos

    return parser


def lazy(parser_factory: Callable[[], Parser[T]]) -> Parser[T]:
    def parser(text: str, pos: int) -> ParseResult[T]:
        return parser_factory()(text, pos)

    return parser


def parse(parser: Parser[T], text: str) -> T:
    result = parser(text, 0)

    if result is None:
        raise ValueError("parse failed")

    value, pos = result

    if pos != len(text):
        raise ValueError(f"unexpected input at {pos}: {text[pos:]!r}")

    return value
