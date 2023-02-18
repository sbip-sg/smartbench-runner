#!/usr/bin/env python3

# Standard Library
import os
import pathlib

# Library
from smartbench import buglabel, cli


# import .cli
# from . import cli


def collect_files_from_patterns(patterns):
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


def collect_files_from_directories(directories):
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


def main():
    print("Run Smartbench")
    args = cli.configure_cli_arguments()

    input_files = []

    if args.directories is not None:
        input_files = collect_files_from_directories(args.files)

    if args.files is not None:
        input_files += collect_files_from_patterns(args.files)

    for file_name, _ in input_files:
        print("Test case: " + file_name)


if __name__ == "__main__":
    main()
