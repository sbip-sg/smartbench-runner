#!/usr/bin/env python3


class Location:
    """Class representing a source code location."""

    # Attribute of the location
    file_path: str
    start_line: int
    start_colmum: int
    end_line: int
    end_column: int

    def __init__(
        self, file_path, start_line, start_column, end_line, end_column
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

    def get_line_column_info(self):
        """Print line and column info"""
        return (
            f"{self.start_line}:{self.start_column}"
            f"-{self.end_line}:{self.end_column}"
        )
