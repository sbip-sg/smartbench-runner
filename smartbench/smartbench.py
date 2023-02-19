#!/usr/bin/env python3

# Standard Library
import os
import pathlib
import sys

# Library
from smartbench import buglabel, cli, tools
from smartbench.tools.slither import slither


def collect_test_cases_from_file_patterns(patterns: str) -> [str]:
    """Collect all Solidity files whose name satisfying a file name pattern.
    Return a list of absolute file names.
    """
    files = []
    for rel_fname in patterns:
        # print("Root:", root, "spec:", spec)
        abs_fname = os.path.abspath(rel_fname)
        if os.path.isfile(abs_fname) and abs_fname[-4:] in (".sol"):
            files.append((abs_fname, rel_fname))
    return files


def collect_test_cases_in_directories(directories: str) -> [str]:
    """Collect all Solidity files in a directory.
    Return a list of absolute file names."""
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


def collect_test_cases(args) -> [str]:
    "Collect test cases for the analysis."
    input_files = []

    if args.directories is not None:
        input_files = collect_test_cases_in_directories(args.files)

    if args.files is not None:
        input_files += collect_test_cases_from_file_patterns(args.files)

    # Priting for debugging
    for file_name, _ in input_files:
        print("\nTest case: " + file_name)
        labels = buglabel.parse_bug_labels(file_name, "auto")
        for lbl in labels:
            print("  Line " + str(lbl.line_number) + ": " + lbl.bug_category)

    return input_files


# def run_slither(command, timeout):


def configure_analysis_tool(tool: str):
    if tool == "slither":
        slither.read_slither_configuration()


def main():
    """Main function"""

    # Parse CLI
    args = cli.configure_cli_arguments()

    print("Analysis tools:", args.tools)
    for tool in args.tools:
        configure_analysis_tool(tool)

    # Collect test cases
    input_files = collect_test_cases(args)
    if input_files == []:
        sys.exit("No input smart contract is given!")

    sys.exit(0)


if __name__ == "__main__":
    main()
