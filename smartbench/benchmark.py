#!/usr/bin/env python3

"""Module for handling benchmarks of test cases"""


# Standard Library
import os
import pathlib
import sys
import traceback
from typing import Dict, List

from smartbench.printer import error
from smartbench.smartbench import printer


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
    print("Collecting test cases...")
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
    else:
        print(f"Found {len(test_files)} test files!")

    test_files = sorted(test_files)

    return test_files


def collect_target_contracts(test_contract_file: str) -> Dict[str, List[str]]:
    contract_dict = {}
    try:
        with open(test_contract_file, "r", encoding="utf-8") as file:
            while line := file.readline():
                # Parsing Smartbench format: each line contains a test file,
                # followed by a colon `:`, and then contract names, which are
                # separated by comma `,`.
                #
                # Example: `file_name: contract_name_1, contract_name_2`
                if (idx := line.find(":")) >= 0:
                    test_file = line[0:idx]
                    contract_names = line[(idx + 1) :].split(",")
                    contract_names = [s.strip() for s in contract_names]
                    contract_dict[test_file] = contract_names
                    continue

                # Parsing Smartian format: each line contains a test file name,
                # and contract names, all are separated by comma `,`.
                #
                # Example: `file_name, contract_name_1, contract_name_2`
                if (idx := line.find(",")) >= 0:
                    test_file = line[0:idx]
                    contract_names = line[(idx + 1) :].split(",")
                    contract_names = [s.strip() for s in contract_names]
                    contract_dict[test_file] = contract_names
                    continue

            return contract_dict

    except Exception:
        error(f"Failed to get contract list: {test_file}")
        traceback.print_exc()
        return contract_dict
