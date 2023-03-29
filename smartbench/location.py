#!/usr/bin/env python3


# Standard Library
import os

from typing import Optional


class Location:
    """Class representing a source code location.

    When `start_line`, `start_colmum`, `end_line`, `end_column` are None,
    this bug location indicate to the whole file.
    """

    def __init__(
        self,
        file_path: str,
        start_line: Optional[int] = None,
        start_column: Optional[int] = None,
        end_line: Optional[int] = None,
        end_column: Optional[int] = None,
    ):
        """Constructor"""
        self.file_path: str = file_path
        self.start_line = int(start_line) if start_line else None
        self.start_column = int(start_column) if start_column else None
        self.end_line = int(end_line) if end_line else None
        self.end_column = int(end_column) if end_column else None

    def __str__(self):
        """Print to string"""
        return (
            f"{self.file_path}:{self.start_line}:{self.start_column}"
            f"-{self.end_line}:{self.end_column}"
        )

    def get_line_column(self):
        """Print line and column info"""
        return (
            f"{self.start_line}:{self.start_column}"
            f"-{self.end_line}:{self.end_column}"
        )

    def print_concise(self):
        """Print location in concise format."""
        file_name = os.path.basename(self.file_path)
        return f"{file_name}:{self.get_line_column()}"
