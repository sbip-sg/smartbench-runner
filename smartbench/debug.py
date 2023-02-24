#!/usr/bin/env python3


def info(*args):
    """Wrapper function to print information."""
    print("> " + " ".join(map(str, args)))


def warning(*args):
    """Print a warning message"""
    print("[Warning]" + " ".join(map(str, args)))


def debug(*args):
    """Wrapper function to print information."""
    print("[dbg]" + " ".join(map(str, args)))
