#!/usr/bin/env python3


# Standard Library
import os

from typing import Union


class Location:
    """Class representing a source code location.

    When `start_line`, `start_colmum`, `end_line`, `end_column` are None,
    this bug location indicate to the whole file.
    """

    # Attribute of the location
    file_path: str
    start_line: Union[int, None]
    start_colmum: Union[int, None]
    end_line: Union[int, None]
    end_column: Union[int, None]

    def __init__(
        self,
        file_path,
        start_line=None,
        start_column=None,
        end_line=None,
        end_column=None,
    ):
        """Constructor"""
        self.file_path = file_path
        self.start_line = start_line
        self.start_column = start_column
        self.end_line = end_line
        self.end_column = end_column

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
