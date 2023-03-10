#!/usr/bin/env python3

"""Module for handling test cases"""


# Standard Library
import os
import pathlib
import sys

from typing import List

# Library
from smartbench import buglabel
from smartbench.buglabel import BugLabel
from smartbench.debug import debug


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


def parse_bug_labels(test_files: List[str]) -> List[BugLabel]:
    """Parsing bug labels from test files"""
    print("Parsing bug labels...\n")

    bug_labels = []

    for test_file in test_files:
        print("- Test case: " + test_file)
        labels = buglabel.parse_bug_labels(test_file)

        if len(labels) == 0:
            print("  No bug labels are found!")
            continue

        for lbl in labels:
            linum = str(lbl.start_line)
            if lbl.start_line != lbl.end_line:
                linum = linum + "-" + str(lbl.end_line)
                print("  Line " + str(linum) + ": " + lbl.bug_category)
            else:
                print("  Line " + str(linum) + ": " + lbl.bug_category)

        bug_labels += labels

        print("")

    return labels


def collect_test_cases(args) -> List[str]:
    """
    Collect test cases for the analysis.
    """
    print("Collecting test cases...\n")
    test_files = []

    for input_path in args.input_files_directories:
        if os.path.isdir(input_path):
            test_files += collect_test_cases_in_directory(input_path)
        elif os.path.isfile(input_path):
            input_path = os.path.abspath(input_path)
            if is_solidity_file(input_path):
                test_files.append(input_path)

    if len(test_files) == 0:
        sys.exit("No input smart contract is given!")

    parse_bug_labels(test_files)

    return test_files
