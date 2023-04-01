#!/usr/bin/env python3

"""Module for handling test cases"""


# Standard Library
import os
import pathlib
import sys

from typing import List

# Library
from smartbench import bug_annot
from smartbench.bug_annot import BugAnnot


def is_solidity_file(filename) -> bool:
    """Check whether the input file is an existing Solidity file."""
    return os.path.isfile(filename) and filename[-4:] in (".sol")


def collect_test_cases_in_directory(directory: str) -> List[str]:
    """
    Collect all Solidity files in a directory.
    Return a list of absolute file names.
    """
    files = []
    path = pathlib.Path(directory)
    for file_path in path.rglob("*"):
        file_name = os.path.normpath(os.path.abspath(file_path))
        if is_solidity_file(file_name):
            files.append(file_name)
    return files


def collect_test_cases(args) -> List[str]:
    """
    Collect test cases for the analysis.
    """
    print("Collecting test cases...")
    test_files = []

    for input_path in args.input_files_directories:
        if os.path.isdir(input_path):
            test_files += collect_test_cases_in_directory(input_path)
        elif os.path.isfile(input_path):
            input_path = os.path.abspath(input_path)
            if is_solidity_file(input_path):
                test_files.append(input_path)

    if len(test_files) == 0:
        sys.exit("No input smart contract is found!")
    else:
        print(f"Found {len(test_files)} test files!")

    test_files = sorted(test_files)

    return test_files
