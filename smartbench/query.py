#!/usr/bin/env python3

"""
Module for querying information in smart contract test files.
"""

# Standard Library
from typing import List

from smartbench.solidity import solc
from smartbench.printer import debug, safe_print, warning


def query_solc_version(test_files: List[str]) -> None:
    print("Query Solc version...")
    for test_file in test_files:
        best_solc_versions = solc.detect_best_solc_versions(test_file)
        print(f"\nTest file: {test_file}")
        print(f"- Best solc versions: {best_solc_versions}")

    pass


def query_test_files(test_files: List[str], args) -> None:
    """Query information in test files"""
    if args.solc_version:
        query_solc_version(test_files)

    return None
