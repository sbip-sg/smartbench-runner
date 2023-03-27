#!/usr/bin/env python3

"""
Module for command line configuration.
"""

# Standard Library
import argparse

from enum import Enum


class Command(Enum):
    """Class define sub-commands of Smartbench."""

    ANALYZE = "analyze"
    PARSE_RESULTS = "parse-results"
    PARSE_ANNOTS = "parse-annots"
    DEPLOY_CONTRACTS = "deploy-contracts"


def parse_cli_arguments():
    """Configure command arguments line."""
    arg_parser = argparse.ArgumentParser(
        description="Detect Solidity compiler version for a smart contract",
        add_help=True,
    )

    # Create sub-parser
    sub_parsers = arg_parser.add_subparsers(
        dest="sub_command",
        metavar=None,
        title="List of sub-commands",
        help=None,
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

    # Create a parser for the `analyze` sub-command
    analyze_parser = sub_parsers.add_parser(
        Command.ANALYZE.value,
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

    # Validate analysis result
    analyze_parser.add_argument(
        "--validate-results",
        action="store_true",
        help="Validate analysis results with bug annotations.",
    )

    # Additional arguments of Slither
    analyze_parser.add_argument(
        "--slither-args",
        metavar="ARGUMENTS",
        type=str,
        help="Additional arguments of Slither",
    )

    # Additional arguments of Confuzzius
    analyze_parser.add_argument(
        "--confuzzius-args",
        metavar="ARGUMENTS",
        type=str,
        help="Additional arguments of Confuzzius",
    )

    ################################
    # Parser for sub-command `parse-result`

    # Create a parser for the `parse-result` sub-command
    result_parser = sub_parsers.add_parser(
        Command.PARSE_RESULTS.value,
        parents=[parent_parser],
        add_help=False,
        help="Sub-command to parse existing analysis results.",
    )

    # Input result directories
    result_parser.add_argument(
        "result_directories",
        nargs="+",  # Accept multiple input files or directories
        type=str,
        help="Input result directories.",
    )

    # Validate analysis result
    result_parser.add_argument(
        "--validate-results",
        action="store_true",
        help="Validate analysis results with bug annotations.",
    )

    ################################
    # Parser for sub-command `parse-annotation`

    # Create a parser for the `parse-annotation` sub-command
    annotation_parser = sub_parsers.add_parser(
        Command.PARSE_ANNOTS.value,
        parents=[parent_parser],
        add_help=False,
        help="Sub-command to parse bug annotations in source code.",
    )

    # Input result directories
    annotation_parser.add_argument(
        "input_files_directories",
        nargs="+",  # Accept multiple input files or directories
        type=str,
        help="Input files or directories (accepts wildcard characters).",
    )

    ################################
    # Parser for sub-command `deploy-contracts`

    # Create a parser for the `parse-result` sub-command
    deploy_parser = sub_parsers.add_parser(
        Command.DEPLOY_CONTRACTS.value,
        parents=[parent_parser],
        add_help=False,
        help="Sub-command to deploy smart contracts for testing.",
    )

    # Input files
    deploy_parser.add_argument(
        "input_files_directories",
        nargs="+",  # Accept multiple input files or directories
        type=str,
        help="Input files or directories (accepts wildcard characters).",
    )

    # Analysis tool
    deploy_parser.add_argument(
        "-t",
        "--tools",
        nargs="+",  # Accept multiple tools.
        type=str,
        help="Analysis tools to be evaluated.",
    )

    ################################
    # Parse all arguments

    args = arg_parser.parse_args()

    return (arg_parser, args)
