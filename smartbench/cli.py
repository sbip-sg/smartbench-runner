#!/usr/bin/env python3

"""
Module for command line configuration.
"""

# Standard Library
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

    ################################
    # Tool and input argument group

    main_args = arg_parser.add_argument_group("Tool and input arguments.")

    # Input files
    main_args.add_argument(
        "-f",
        "--files",
        nargs="+",  # Accept multiple input files
        type=str,
        help="Patterns of input smart contracts.",
    )

    # Input directories
    main_args.add_argument(
        "-d",
        "--directories",
        help="Directory containing input smart contracts.",
    )

    # Analysis tool
    main_args.add_argument(
        "-t",
        "--tools",
        nargs="+",  # Accept multiple tools.
        type=str,
        help="Analysis tools to be evaluated.",
    )

    ################################
    # Slither argument group

    slither_args = arg_parser.add_argument_group("Slither arguments")

    slither_args.add_argument(
        "--slither-additional-arguments",
        metavar="ARGUMENTS",
        type=str,
        help="Additional arguments of Slither",
    )

    ################################
    # Confuzzius argument group

    confuzzius_args = arg_parser.add_argument_group("Confuzzius arguments")

    confuzzius_args.add_argument(
        "--confuzzius-additional-arguments",
        metavar="ARGUMENTS",
        type=str,
        help="Additional arguments of Confuzzius",
    )

    ################################
    # Parse all arguments

    args = arg_parser.parse_args()

    return args
