#!/usr/bin/env python3

"""Module handling log file generated during the analysis."""

# Standard Library
from typing import Optional


## REVIEW: consider moving this function to to other module
def get_input_test_file(log_file: str) -> Optional[str]:
    """Get input test file from a log file"""
    with open(log_file, "r", encoding="utf-8") as file:
        while line := file.readline():
            if line.rstrip() == "[input contract]":
                try:
                    file.readline()  # skip next line
                    return file.readline().rstrip()
                except Exception:
                    return None
        return None
