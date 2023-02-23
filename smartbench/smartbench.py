#!/usr/bin/env python3

# Standard Library
import os
import pathlib
import shlex
import signal
import subprocess
import sys

from datetime import datetime

# Third Party
import colored_traceback

# Library
from smartbench import buglabel, flags
from smartbench.cli import parse_cli_arguments
from smartbench.tools.tool import ALL_RESULTS_DIR, configure_analysis_tools


def collect_test_cases_from_file_patterns(patterns: str) -> [str]:
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


def collect_test_cases_in_directories(directories: str) -> [str]:
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


def collect_test_cases(args) -> [str]:
    """
    Collect test cases for the analysis.
    """
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


def perform_analysis(tools, test_files):
    # Prepare output directory
    output_dir = os.path.join(
        ALL_RESULTS_DIR,
        datetime.now().strftime("%Y_%m_%d_%H_%M_%S"),
    )
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Perform the analysis
    for tool in tools:
        print("Running tool:", tool.name)
        for test_file in test_files:
            print("Test file:", test_file)
            command = tool.make_analysis_command(test_file, output_dir)
            print("  Command: ", command)
            try:
                result = subprocess.run(
                    shlex.split(command),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                log_file = os.path.join(output_dir, tool.log_output)
                print("Log file:", log_file)
                # write result to file
                with open(log_file, "w") as f:
                    f.write("========== Output ============\n\n")
                    f.write(result.stdout.decode("utf-8"))
                    f.write("\n\n\n")
                    f.write("========== Errors ============\n\n")
                    f.write(result.stderr.decode("utf-8"))
            except:
                print("Failed to run command: " + str(command))


def signal_handler(sig, frame):
    print("Interuptted by Ctrl+C!")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def main():
    """Main function"""

    # Parse CLI
    args = parse_cli_arguments()
    flags.configure_global_flags(args)

    print("Debug mode: " + str(flags.DEBUG_MODE))

    # Configure tools
    tools = configure_analysis_tools(args)

    # Collect test files
    test_files = collect_test_cases(args)

    # Perform the analysis
    perform_analysis(tools, test_files)

    # Finish
    sys.exit(0)


if __name__ == "__main__":
    colored_traceback.add_hook()
    main()
