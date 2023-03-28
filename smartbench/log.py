#!/usr/bin/env python3

"""Module handling log file generated during the analysis."""

# Standard Library
from typing import Optional


def get_input_test_file(log_file: str) -> Optional[str]:
    """Get input test file from a log file"""
    with open(log_file, "r", encoding="utf-8") as file:
        try:
            while line := file.readline():
                if line.rstrip() == "[input contract]":
                    file.readline()  # skip next line
                    return file.readline().rstrip()
            return None
        except Exception:
            return None
