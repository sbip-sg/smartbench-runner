#!/usr/bin/env python3

"""Module handling analysis tools.

This is the shared interface for all tools.
"""


class Tool:
    """An analysis tool."""

    def __init__(self, name, analyzer_path, executable_file, timeout=15):
        self.name = name
        self.analyzer_executable = analyzer_path
        self.executable_file = executable_file
        self.timeout = timeout

