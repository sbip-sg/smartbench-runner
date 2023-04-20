#!/usr/bin/env python3

"""Module containing some global variables."""

# Flag for enable debugging mode.
DEBUG_MODE = False


def configure_global_flags(args) -> None:
    """Configure global flags from command-line arguments"""
    global DEBUG_MODE
    DEBUG_MODE = args.debug
