#!/usr/bin/env python3

"""Module containing utilities handling processes"""

# Standard Library
import os
import signal

from smartbench.printer import safe_print


def ignore_sigint() -> None:
    """Ignore SIGINT signal"""
    print("== IGNORE SIGINT")
    signal.signal(signal.SIGINT, signal.SIG_IGN)
