#!/usr/bin/env python3

# Standard Library
import os
import pathlib
import sys

# Library
from smartbench import buglabel, cli, tools
from smartbench.tools.slither import slither
from smartbench.tools.tool import Tool


def collect_test_cases_from_file_patterns(patterns: str) -> [str]:
    """Collect all Solidity files whose name satisfying a file name pattern.
    Return a list of absolute file names.
    """
    files = []
    for rel_fname in patterns:
        # print("Root:", root, "spec:", spec)
        abs_fname = os.path.abspath(rel_fname)
        if os.path.isfile(abs_fname) and abs_fname[-4:] in (".sol"):
            files.append(abs_fname)
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
    test_files = []

    if args.directories is not None:
        test_files = collect_test_cases_in_directories(args.files)

    if args.files is not None:
        test_files += collect_test_cases_from_file_patterns(args.files)

    # Priting for debugging
    for test_file in test_files:
        print("\nTest case: " + test_file)
        labels = buglabel.parse_bug_labels(test_file, "auto")
        for lbl in labels:
            print("  Line " + str(lbl.line_number) + ": " + lbl.bug_category)

    if len(test_files) == 0:
        sys.exit("No input smart contract is given!")

    return test_files


# def run_slither(command, timeout):


def configure_one_tool(tool: str) -> Tool:
    """Configure one analysis tool."""
    if tool == "slither":
        return slither.read_slither_configuration()


def configure_analysis_tools(tools: [str]) -> [Tool]:
    """Configure all analysis tools."""
    if tools is None or len(tools) == 0:
        sys.exit("No analysis tool is selected!")

    configs = []
    for tool in tools:
        configs.append(configure_one_tool(tool))

    return configs


def main():
    """Main function"""

    # Parse CLI
    args = cli.configure_cli_arguments()

    # Configure tools
    tools1 = configure_analysis_tools(args.tools)

    # Collect test files
    test_files = collect_test_cases(args)

    # Perform the analysis
    for tool in tools1:
        print("Running tool:", tool.name)
        for test_file in test_files:
            print("Test file:", test_file)
            cmd = tool.make_analysis_command(test_file)
            print("  Command: ", cmd)

    # Quit
    sys.exit(0)


if __name__ == "__main__":
    main()
