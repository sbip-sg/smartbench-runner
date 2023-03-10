#!/usr/bin/env python3

# Library
from smartbench import flags


def info(*args):
    """Wrapper function to print information."""
    print("\n> " + " ".join(map(str, args)) + "\n")


def warning(*args):
    """Print a warning message"""
    print("\n>> " + " ".join(map(str, args)) + "\n")


def debug(*args):
    """Wrapper function to print information."""
    if flags.DEBUG_MODE:
        print("\n!! " + " ".join(map(str, args)) + "\n")
