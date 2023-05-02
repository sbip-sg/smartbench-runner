#!/usr/bin/env python3

"""Module for handling benchmarks of test cases"""


# Standard Library
import os
import pathlib
import sys
import traceback

from typing import Dict, List, Optional, Tuple

# Library
from smartbench.printer import error, error_traceback, safe_print
from smartbench.smartbench import printer


# TODO: rename to a better name
class TestConfig:
    """Class representing the configuration for an input test file."""

    def __init__(
        self, target_contracts: List[str], compiler_version: Optional[str]
    ):
        self.target_contracts: List[str] = target_contracts
        self.compiler_version: Optional[str] = compiler_version


def is_solidity_file(filename) -> bool:
    """Check whether the input file is an existing Solidity file."""
    return os.path.isfile(filename) and filename[-4:] in (".sol")


def find_test_files_in_directory(directory: str) -> List[str]:
    """
    Find all Solidity files in a directory.
    Return a list of absolute file names.
    """
    files = []
    path = pathlib.Path(directory)
    for file_path in path.rglob("*"):
        file_name = os.path.normpath(os.path.abspath(file_path))
        if is_solidity_file(file_name):
            files.append(file_name)
    return files


def collect_test_files(input_files_directories: List[str]) -> List[str]:
    """
    Collect test cases for the analysis.
    """
    printer.print_long_double_separator_line()
    safe_print("Collecting test cases...")
    test_files = []

    for input_path in input_files_directories:
        if os.path.isdir(input_path):
            test_files += find_test_files_in_directory(input_path)
        elif os.path.isfile(input_path):
            input_path = os.path.abspath(input_path)
            if is_solidity_file(input_path):
                test_files.append(input_path)

    if len(test_files) == 0:
        sys.exit("No input test file is found!")

    test_files = sorted(test_files)

    return test_files


def collect_test_configs(
    test_config_file: str,
) -> Dict[str, TestConfig]:
    test_config_dict: Dict[str, TestConfig] = {}
    try:
        with open(test_config_file, "r", encoding="utf-8") as file:
            while line := file.readline():
                configure_items = []

                # Parsing Smartbench format: each line contains a test file,
                # followed by a colon `:`, and then contract names, which are
                # separated by comma `,`.
                #
                # Example: `file_name: contract_name_1, contract_name_2`
                if (idx := line.find(":")) >= 0:
                    # Get test file base name
                    test_file = line[0:idx]
                    if test_file.endswith(".sol"):
                        test_file = test_file.removesuffix(".sol")

                    # Get contract names
                    configure_items = line[(idx + 1) :].split(",")
                    configure_items = [s.strip() for s in configure_items]

                # Parsing Smartian format: each line contains a test file name,
                # and contract names, all are separated by comma `,`.
                #
                # Example: `file_name, contract_name_1, contract_name_2`
                elif (idx := line.find(",")) >= 0:
                    # Get test file base name
                    test_file = line[0:idx]
                    if test_file.endswith(".sol"):
                        test_file = test_file.removesuffix(".sol")

                    # Get contract names
                    configure_items = line[(idx + 1) :].split(",")
                    configure_items = [s.strip() for s in configure_items]

                # Extract compiler version
                if "." in configure_items[-1]:
                    compiler_version = configure_items[-1]
                    target_contracts = configure_items[:-1]
                else:
                    compiler_version = None
                    target_contracts = configure_items

                test_config = TestConfig(target_contracts, compiler_version)
                test_config_dict[test_file] = test_config

            return test_config_dict

    except Exception:
        error_traceback(
            f"Failed to get target contracts and compiler version "
            f"from: {test_config_file}"
        )
        return test_config_dict
