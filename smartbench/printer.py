#!/usr/bin/env python3

"""Module containing some printing utilities."""

# Standard Library
from sys import exit

# Library
from smartbench import flags


def warning(*args):
    """Print a warning message"""
    print("WARNING: " + " ".join(map(str, args)) + "\n")


def error(*args):
    """Print an error message"""
    print("ERROR: " + " ".join(map(str, args)) + "\n")
    print("Smartbench exiting...")
    exit(1)


def debug(*args):
    """Print a debugging message."""
    if flags.DEBUG_MODE:
        print("!! " + " ".join(map(str, args)) + "\n")


def print_short_single_horizontal_line():
    print(f"{'=' * 30}\n")


def print_medium_single_horizontal_line():
    print(f"{'=' * 45}\n")


def print_long_single_horizontal_line():
    print(f"{'=' * 55}\n")


def print_short_double_horizontal_line():
    print(f"{'=' * 30}\n")


def print_medium_double_horizontal_line():
    print(f"{'=' * 45}\n")


def print_long_double_horizontal_line():
    print(f"{'=' * 55}\n")
