#!/usr/bin/env python3

"""Module containing some printing utilities."""

# Standard Library
import traceback

# Third Party
import pygments
import pygments.formatters
import pygments.lexers

# Library
from smartbench import flags


def safe_print(*args: str) -> None:
    """Print every single line and move the cursor to the beginning of next line
    for the next printing."""
    output = format(*args)
    output = output.replace("\n", "\n\r")
    print(output, end="\n\r")


def safe_print_underline(*args: str) -> None:
    """Print and underline text."""
    output = format(*args)
    output = output.replace("\n", "\n\r")
    print(output, end="\n\r")
    underline_length = min(75, len(output) + 1)
    print("-" * underline_length, end="\n\r\n\r")


def print_if(condition: bool, *args: str) -> None:
    """Print if the input condition holds."""
    # screen_lock:
    if condition:
        safe_print(*args)


def print_unless(condition: bool, *args: str) -> None:
    """Print unless the input condition holds."""
    # screen_lock:
    if not condition:
        safe_print(*args)


def warning(*args: str) -> None:
    """Print a warning message"""
    safe_print("\n!! WARNING: " + " ".join(map(str, args)))


def error(*args: str) -> None:
    """Print an error message"""
    safe_print("\n!! ERROR: " + " ".join(map(str, args)))


def error_traceback(*args: str) -> None:
    """Print an error message"""
    safe_print("\n!! ERROR: " + " ".join(map(str, args)) + "\n")
    traceback_info = traceback.format_exc()
    safe_print("************ Backtrace ************\n")
    lexer = pygments.lexers.get_lexer_by_name("pytb", stripall=True)
    formatter = pygments.formatters.get_formatter_by_name("terminal")
    traceback_info = pygments.highlight(traceback_info, lexer, formatter)
    safe_print(f"{traceback_info}")


def debug(*args: str) -> None:
    """Print a debugging message."""
    if flags.DEBUG_MODE:
        safe_print("!! " + " ".join(map(str, args)) + "\n")


def print_short_dashed_separator_line() -> None:
    """Print a short separator line: --------"""
    safe_print(f"\n{'-' * 30}\n")


def print_medium_dashed_separator_line() -> None:
    """Print a medium separator line: --------"""
    safe_print(f"\n{'-' * 45}\n")


def print_long_dashed_separator_line() -> None:
    """Print a long separator line: --------"""
    safe_print(f"\n{'-' * 55}\n")


def print_short_double_separator_line() -> None:
    """Print a short separator line: ========"""
    safe_print(f"\n{'=' * 30}\n")


def print_medium_double_separator_line() -> None:
    """Print a medium separator line: ========"""
    safe_print(f"\n{'=' * 45}\n")


def print_long_double_separator_line() -> None:
    """Print a long separator line: ========"""
    safe_print(f"\n{'=' * 55}\n")
