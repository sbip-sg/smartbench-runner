#!/usr/bin/env python3

"""Module for handling test cases"""


# Standard Library
import os
import pathlib
import sys

from typing import List

# Library
from smartbench import buglabel


def collect_test_cases_from_file_patterns(patterns: str) -> List[str]:
    """
    Collect all Solidity files whose name satisfying a file name pattern.
    Return a list of absolute file names.
    """
    files = []
    for rel_fname in patterns:
        # print("Root:", root, "spec:", spec)
        abs_fname = os.path.abspath(rel_fname)
        if os.path.isfile(abs_fname) and abs_fname[-4:] in (".sol"):
            files.append(abs_fname)
    return files


def collect_test_cases_in_directories(directories: str) -> List[str]:
    """
    Collect all Solidity files in a directory.
    Return a list of absolute file names.
    """
    files = []
    for directory in directories:
        path = pathlib.Path(directory)
        for rel_fname in path.rglob("*"):
            rel_fname = os.path.normpath(rel_fname)
            abs_fname = os.path.abspath(rel_fname)
            abs_fname = os.path.normpath(abs_fname)
            if os.path.isfile(abs_fname) and abs_fname[-4:] in (".sol"):
                files.append(abs_fname)
    return files


def collect_test_cases(args) -> List[str]:
    """
    Collect test cases for the analysis.
    """
    test_files = []

    if args.directories is not None:
        test_files = collect_test_cases_in_directories(args.files)

    if args.files is not None:
        test_files += collect_test_cases_from_file_patterns(args.files)

    # Printing for debugging
    for test_file in test_files:
        print("\nTest case: " + test_file)
        labels = buglabel.parse_bug_labels(test_file, "auto")
        for lbl in labels:
            linum = str(lbl.start_line)
            if lbl.start_line != lbl.end_line:
                linum = linum + "-" + str(lbl.end_line)
                print("  Line " + str(linum) + ": " + lbl.bug_category)

    if len(test_files) == 0:
        sys.exit("No input smart contract is given!")

    return test_files
