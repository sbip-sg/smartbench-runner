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
    PARSE_COVERAGE = "parse-coverage"
    PARSE_ANNOTS = "parse-annots"
    DEPLOY_CONTRACTS = "deploy-contracts"


def parse_cli_arguments():
    """Configure command arguments line."""
    arg_parser = argparse.ArgumentParser(
        description="Detect Solidity compiler version for a smart contract",
        add_help=True,
    )

    # Create sub-parser
    subcommand_parsers = arg_parser.add_subparsers(
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
    analyze_argparser = subcommand_parsers.add_parser(
        Command.ANALYZE.value,
        parents=[parent_parser],
        add_help=False,
        help="Sub-command to analyze smart contracts",
    )

    analyze_argparser.add_argument(
        "input_files_directories",
        nargs="*",  # Accept multiple input files or directories
        type=str,
        help="Input files or directories for testing.",
    )

    analyze_argparser.add_argument(
        "-f",
        dest="test_files_directories",
        nargs="*",  # Accept multiple input files or directories
        type=str,
        help="Test files or directories.",
    )

    analyze_argparser.add_argument(
        "--benchmark-dir",
        type=str,
        help="Configuration file specifying target contracts in test files. \
        Support both Smartbench and Smartian format.",
    )

    analyze_argparser.add_argument(
        "--test-config-file",
        type=str,
        help="Configuration file specifying target contracts in test files. \
        Support both Smartbench and Smartian format.",
    )

    analyze_argparser.add_argument(
        "--result-dir",
        type=str,
        help="Directory to store analysis resutls of all tools",
    )

    analyze_argparser.add_argument(
        "--solc-version",
        type=str,
        help="Version of the Solidity compiler.",
    )

    analyze_argparser.add_argument(
        "-t",
        "--tools",
        nargs="+",  # Accept multiple tools.
        type=str,
        help="Analysis tools to be evaluated.",
    )

    analyze_argparser.add_argument(
        "--timeout",
        type=int,
        help="Timeout for each test file. \
        This is the total timeout for all contracts in the same test file.",
    )

    analyze_argparser.add_argument(
        "--contract-timeout",
        type=int,
        help="Timeout for each contract in the test file. \
        One file may contain multiple contracts",
    )

    analyze_argparser.add_argument(
        "-j",
        "--jobs",
        type=int,
        help="Number of jobs to be run concurrently for each tool.",
    )

    analyze_argparser.add_argument(
        "--validate",
        action="store_true",
        help="Validate analysis results with bug annotations.",
    )

    analyze_argparser.add_argument(
        "--benchmarking",
        action="store_true",
        help="Validating analysis results for benchmarking.",
    )

    analyze_argparser.add_argument(
        "--annot-format",
        type=str,
        choices=["smartbugs", "smartbench", "solidifi"],
        help=("Type of bug annotation format."),
    )

    analyze_argparser.add_argument(
        "--install-smartbench-env",
        action="store_true",
        help="Install Smartbench environment before testing.",
    )

    analyze_argparser.add_argument(
        "--install-local-docker",
        action="store_true",
        help="Install Docker images of analysis tools locally.",
    )

    analyze_argparser.add_argument(
        "--install-remote-docker",
        action="store_true",
        help="Install Docker containers of analysis tools from remote.",
    )

    analyze_argparser.add_argument(
        "--only-create-containers",
        action="store_true",
        help="Automatically create Docker containers for analysis tools.",
    )

    analyze_argparser.add_argument(
        "--keep-docker-alive",
        action="store_true",
        help="Keep Docker containers alive after testing.",
    )

    ################################
    # Parser for sub-command `parse-results`

    # Create a parser for the `parse-result` sub-command
    result_argparser = subcommand_parsers.add_parser(
        Command.PARSE_RESULTS.value,
        parents=[parent_parser],
        add_help=False,
        help="Sub-command to parse existing analysis results.",
    )

    # Input result directories
    result_argparser.add_argument(
        "input_result_directories",
        nargs="*",  # Accept multiple result directories
        type=str,
        help="Input result directories.",
    )

    # Result directories
    result_argparser.add_argument(
        "-r",
        dest="result_directories",
        nargs="*",  # Accept multiple result directories
        type=str,
        help="Input result directories.",
    )

    # Result directories
    result_argparser.add_argument(
        "-b",
        dest="benchmark_names",
        nargs="*",  # Accept multiple benchmark names
        type=str,
        help="Benchmark names in the result directory.",
    )

    # Analysis tool
    result_argparser.add_argument(
        "-t",
        "--tools",
        nargs="+",  # Accept multiple tools.
        type=str,
        help="Analysis tools to be evaluated.",
    )

    # Validate analysis result
    result_argparser.add_argument(
        "--validate",
        action="store_true",
        help="Validate analysis results with bug annotations.",
    )

    # Validate analysis result
    result_argparser.add_argument(
        "--export-summary",
        action="store_true",
        help="Export analysis summaries to JSON or CSV files.",
    )

    # Print and exported summary in a more detailed format.
    result_argparser.add_argument(
        "--detailed-summary",
        action="store_true",
        help="Print and export summary in a more detailed format.",
    )

    # Specify benchmark name for special cases without standard annotation and
    # validation
    result_argparser.add_argument(
        "--annot-format",
        type=str,
        choices=["smartbugs", "smartbench", "solidifi"],
        help=("Type of bug annotation format."),
    )

    ################################
    # Parser for sub-command `parse-coverage`

    # Create a parser for the `parse-coverage` sub-command
    coverage_argparser = subcommand_parsers.add_parser(
        Command.PARSE_COVERAGE.value,
        parents=[parent_parser],
        add_help=False,
        help="Sub-command to parse instruction coverage in analysis results.",
    )

    # Input result directories
    coverage_argparser.add_argument(
        "result_directories",
        nargs="+",  # Accept multiple input files or directories
        type=str,
        help="Input result directories.",
    )

    ################################
    # Parser for sub-command `parse-annotation`

    # Create a parser for the `parse-annotation` sub-command
    annot_argparser = subcommand_parsers.add_parser(
        Command.PARSE_ANNOTS.value,
        parents=[parent_parser],
        add_help=False,
        help="Sub-command to parse bug annotations in source code.",
    )

    # Input result directories
    annot_argparser.add_argument(
        "input_files_directories",
        nargs="+",  # Accept multiple input files or directories
        type=str,
        help="Input files or directories (accepts wildcard characters).",
    )

    ################################
    # Parse all arguments

    args = arg_parser.parse_args()

    return (arg_parser, args)
