#!/usr/bin/env python3

"""
Module for command line configuration.
"""

# Standard Library
import argparse


def parse_cli_arguments():
    """Configure command arguments line."""
    arg_parser = argparse.ArgumentParser(
        description="Detect Solidity compiler version for a smart contract",
        add_help=True,
    )

    # Create sub-parser
    sub_parsers = arg_parser.add_subparsers(
        dest="sub_command",
        title="List of sub-commands",
        help="",
    )

    ################################
    # Parent parser for common arguments

    parent_parser = argparse.ArgumentParser(add_help=True)

    parent_parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Enable debugging mode.",
    )

    ################################
    # Parser for sub-command `analyze`

    # create the parser for the `analyze` sub-command
    analyze_parser = sub_parsers.add_parser(
        "analyze",
        parents=[parent_parser],
        add_help=False,
        help="Sub-command to analyze smart contracts",
    )

    # Input files
    analyze_parser.add_argument(
        "input_files_directories",
        nargs="+",  # Accept multiple input files or directories
        type=str,
        help="Input files or directories (accepts wildcard characters).",
    )

    # Analysis tool
    analyze_parser.add_argument(
        "-t",
        "--tools",
        nargs="+",  # Accept multiple tools.
        type=str,
        help="Analysis tools to be evaluated.",
    )

    analyze_parser.add_argument(
        "--slither-args",
        metavar="ARGUMENTS",
        type=str,
        help="Additional arguments of Slither",
    )

    analyze_parser.add_argument(
        "--confuzzius-args",
        metavar="ARGUMENTS",
        type=str,
        help="Additional arguments of Confuzzius",
    )

    ################################
    # Parser for sub-command `parse-result`

    # create the parser for the `analyze` sub-command
    result_parser = sub_parsers.add_parser(
        "result",
        parents=[parent_parser],
        add_help=False,
        help="Sub-command to read existing analysis results.",
    )

    # Parse results
    result_parser.add_argument(
        "-r",
        "--results",
        type=str,
        help="Directory containing results",
    )

    ################################
    # Parse all arguments

    args = arg_parser.parse_args()

    return args
