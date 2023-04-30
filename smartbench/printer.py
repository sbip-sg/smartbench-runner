#!/usr/bin/env python3

"""Module containing some printing utilities."""

# Standard Library
import traceback

# Library
from smartbench import flags


def safe_print(*args: str) -> None:
    """Print every single line and move the cursor to the beginning of next line
    for the next printing."""
    output = format(*args)
    output = output.replace("\n", "\n\r")
    print(output, end="\n\r")


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
    safe_print("\n!! WARNING: " + " ".join(map(str, args)) + "\n")


def error(*args: str) -> None:
    """Print an error message"""
    safe_print("\n!! ERROR: " + " ".join(map(str, args)) + "\n")


def error_traceback(*args: str) -> None:
    """Print an error message"""
    safe_print("\n!! ERROR: " + " ".join(map(str, args)) + "\n")
    exceptions = traceback.format_exc()
    safe_print("*** Backtrace ***\n")
    safe_print(f"{exceptions}")


def debug(*args: str) -> None:
    """Print a debugging message."""
    if flags.DEBUG_MODE:
        safe_print("!! " + " ".join(map(str, args)) + "\n")


def print_short_dashed_separator_line() -> None:
    """Print a short separator line: --------"""
    safe_print(f"\n{'-' * 30}")


def print_medium_dashed_separator_line() -> None:
    """Print a medium separator line: --------"""
    safe_print(f"\n{'-' * 45}")


def print_long_dashed_separator_line() -> None:
    """Print a long separator line: --------"""
    safe_print(f"\n{'-' * 55}")


def print_short_double_separator_line() -> None:
    """Print a short separator line: ========"""
    safe_print(f"\n{'=' * 30}")


def print_medium_double_separator_line() -> None:
    """Print a medium separator line: ========"""
    safe_print(f"\n{'=' * 45}")


def print_long_double_separator_line() -> None:
    """Print a long separator line: ========"""
    safe_print(f"\n{'=' * 55}")
