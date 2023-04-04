#!/usr/bin/env python3

"""Module containing some printing utilities."""

# Standard Library
from sys import exit

# Library
from smartbench import flags


def warning(*args):
    """Print a warning message"""
    print("\nWARNING: " + " ".join(map(str, args)) + "\n")


def error(*args):
    """Print an error message"""
    print("\nERROR: " + " ".join(map(str, args)) + "\n")
    print("Smartbench exiting...")
    exit(1)


def debug(*args):
    """Print a debugging message."""
    if flags.DEBUG_MODE:
        print("!! " + " ".join(map(str, args)) + "\n")


def print_short_single_horizontal_line():
    print(f"{'=' * 30}")


def print_medium_single_horizontal_line():
    print(f"{'=' * 45}")


def print_long_single_horizontal_line():
    print(f"{'=' * 55}")


def print_short_double_horizontal_line():
    print(f"{'=' * 30}")


def print_medium_double_horizontal_line():
    print(f"{'=' * 45}")


def print_long_double_horizontal_line():
    print(f"{'=' * 55}")
