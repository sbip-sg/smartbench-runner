#!/usr/bin/env python3


# Standard Library
import math
import os

from typing import Dict, List, Optional, Tuple


class Location:
    """Class representing a source code location.

    When `start_line`, `start_colmum`, `end_line`, `end_column` are None,
    this bug location indicate to the whole file.
    """

    def __init__(
        self,
        file_path: Optional[str] = None,
        contract_name: Optional[str] = None,
        function_name: Optional[str] = None,
        start_line: Optional[int] = None,
        start_column: Optional[int] = None,
        end_line: Optional[int] = None,
        end_column: Optional[int] = None,
    ):
        """Constructor"""
        self.file_path = file_path
        self.contract_name = contract_name
        self.function_name = function_name
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

    def __eq__(self, other):
        return (
            self.file_path == other.file_path
            and self.contract_name == other.contract_name
            and self.function_name == other.function_name
            and self.start_line == other.start_line
            and self.start_column == other.start_column
            and self.end_line == other.end_line
            and self.end_column == other.end_column
        )

    def print_line_column(self) -> Optional[str]:
        """Print line and column info"""
        if self.start_line is None or self.end_line is None:
            return None

        start_line = f"{self.start_line}"
        if self.start_column is not None:
            start_line += f":{self.start_column}"

        end_line = f"{self.end_line}"
        if self.end_column is not None:
            end_line += f":{self.end_column}"

        return f"{start_line}-{end_line}"

    def print_concise(self) -> Optional[str]:
        """Print location in concise format."""
        location = os.path.basename(self.file_path)
        if location is None:
            return None

        if line_column := self.print_line_column():
            location += f":{line_column}"

        return location


class Localizer:
    """Class for getting line and column numbers from a character-based
    location in a file."""

    def __init__(self, file_path: str):
        self.file_path = file_path

        # A list containing the line number to its character-based
        # position in file. The element `self.line_positions[i]` store
        # the position of the line `i+1`.
        self.line_positions = []

        # Compute the line-position mapping for the input file.
        with open(file_path, "r", encoding="utf-8") as file:
            char_index = 0  # character index starts from 0
            self.line_positions.append(char_index)
            while c := file.read(1):
                char_index += 1
                if c == "\n":
                    self.line_positions.append(char_index)

            # Add a last element store the size of the whole file
            self.line_positions.append(char_index)

    def get_line_column_number(
        self, position: int
    ) -> Optional[Tuple[int, int]]:
        """Get line number and column number of a character-based
        position in the file."""

        start_line = 0
        end_line = len(self.line_positions) - 1

        # Check the position with the size of the whole file.
        if position < 0 or position > self.line_positions[end_line]:
            return None

        while True:
            if self.line_positions[start_line] > position:
                return None
            if start_line + 1 >= end_line:
                line_number = start_line + 1  # Adjust to 1-based indexing
                column_number = position - self.line_positions[start_line]
                return (line_number, column_number)

            middle_line = math.floor((start_line + end_line) / 2)
            if self.line_positions[middle_line] >= position:
                end_line = middle_line
            else:
                start_line = middle_line


def print_concise_locations(locs: List[Location]) -> str:
    # Group location by file path
    file_locs_dict: Dict[str, List[Location]] = {}

    for loc in locs:
        if loc.file_path in file_locs_dict:
            file_locs: List[Location] = file_locs_dict[loc.file_path]
            file_locs.append(loc)
        else:
            file_locs_dict[loc.file_path] = [loc]

    loc_strs = []
    for file_path in file_locs_dict:
        file_name = os.path.basename(file_path)
        file_locs = file_locs_dict[file_path]
        file_locs_strs = []
        for loc in file_locs:
            if loc_str := loc.print_line_column():
                file_locs_strs.append(loc_str)
        if file_locs_strs == []:
            loc_strs.append(f"{file_name}")
        else:
            loc_strs.append(f"{file_name}: {','.join(file_locs_strs)}")

    return "; ".join(loc_strs)


def check_same_locations(locs1: List[Location], locs2: List[Location]) -> bool:
    """Check if 2 location list are the same"""
    if len(locs1) != len(locs2):
        return False

    for loc1 in locs1:
        if all([loc1 != loc2 for loc2 in locs2]):
            return False

    return True
