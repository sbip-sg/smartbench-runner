#!/usr/bin/env python3

"""Module handling log file generated during the analysis."""

# Standard Library
from typing import Optional


## REVIEW: consider moving this function to to other module
def get_input_test_file(log_file: str) -> Optional[str]:
    """Get input test file from a log file"""
    # Use "ISO-8859-1" codec instead of utf-8 to decode Chinese characters
    with open(log_file, "r", encoding="ISO-8859-1") as file:
        while line := file.readline():
            # Check both 2 headers for backward compatiblity
            if line.rstrip() in ["[input test file]", "[input contract]"]:
                try:
                    # Skip next 2 lines
                    file.readline()
                    file.readline()
                    # Read the input file
                    return file.readline().rstrip()
                except Exception:
                    return None
        return None
