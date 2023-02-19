#!/usr/bin/env python3

"""Module handling analysis tools.

This is the shared interface for all tools.
"""

class ToolConfiguration:
    """A configuration of analysis tool.
    """

    def __init__(self, analyzer_path, executable_file, timeout=15):
        self.analyzer_executable = analyzer_path
        self.executable_file = executable_file
        self.timeout = timeout
