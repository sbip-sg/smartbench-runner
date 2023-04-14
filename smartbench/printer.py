#!/usr/bin/env python3

"""Module containing some printing utilities."""

# Standard Library
import sys
import threading
import traceback

from sys import exit

# Library
from smartbench import flags
from smartbench.globals import screen_lock


def safe_print(*args):
    """Print and move the cursor to the beginning of next line for the next
    printing."""
    print(*args, end="\n\r")


def print_if(condition: bool, *args):
    """Print if the input condition holds."""
    # screen_lock:
    if condition:
        print(*args)


def print_unless(condition: bool, *args):
    """Print unless the input condition holds."""
    # screen_lock:
    if not condition:
        print(*args)


def warning(*args):
    """Print a warning message"""
    safe_print("\!!nWARNING: " + " ".join(map(str, args)) + "\n")


def error(*args):
    """Print an error message"""
    safe_print("\n!!ERROR: " + " ".join(map(str, args)) + "\n")

def error_traceback(*args):
    """Print an error message"""
    safe_print("\n!!ERROR: " + " ".join(map(str, args)) + "\n")
    traceback.print_exc()


def debug(*args):
    """Print a debugging message."""
    if flags.DEBUG_MODE:
        safe_print("!! " + " ".join(map(str, args)) + "\n")


def print_short_single_horizontal_line():
    safe_print(f"\n{'=' * 30}")


def print_medium_single_horizontal_line():
    safe_print(f"\n{'-' * 45}")


def print_long_single_horizontal_line():
    safe_print(f"\n{'-' * 55}")


def print_short_double_horizontal_line():
    safe_print(f"\n{'=' * 30}")


def print_medium_double_horizontal_line():
    safe_print(f"\n{'=' * 45}")


def print_long_double_horizontal_line():
    safe_print(f"\n{'=' * 55}")
