#!/usr/bin/env python3

"""Module providing debugging utilities."""

# Library
from smartbench import flags


def warning(*args):
    """Print a warning message"""
    print("WARNING: " + " ".join(map(str, args)) + "\n")


def error(*args):
    """Print an error message"""
    print("ERROR: " + " ".join(map(str, args)) + "\n")


def debug(*args):
    """Print a debugging message."""
    if flags.DEBUG_MODE:
        print("!! " + " ".join(map(str, args)))
