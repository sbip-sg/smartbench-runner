#!/usr/bin/env python3

"""
Module for command line configuration.
"""

import argparse


def configure_cli_arguments():
    """Configure command arguments line."""
    arg_parser = argparse.ArgumentParser(
        description="Detect Solidity compiler version for a smart contract",
        add_help=False,
    )

    # Help
    arg_parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help message and exit.",
    )

    # Input files
    arg_parser.add_argument(
        "-f",
        "--files",
        nargs="+",  # Accept multiple input files
        type=str,
        help="Patterns of input smart contracts.",
    )

    # Input directories
    arg_parser.add_argument(
        "-d",
        "--directories",
        help="Directory containing input smart contracts.",
    )

    # Parse CLI arguments
    args = arg_parser.parse_args()

    return args
