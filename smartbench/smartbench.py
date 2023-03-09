#!/usr/bin/env python3

# Standard Library
import os
import pathlib
import signal
import sys

# Library
from smartbench import analyze, buglabel, flags, result, tests
from smartbench.cli import parse_cli_arguments
from smartbench.tools.tool import configure_analysis_tools


def signal_handler(sig, frame):
    print("\nInteruptted by Ctrl+C!")
    sys.exit(0)


def analyze_smart_contracts(args):
    """Run analyzers to analyze input smart contracts"""
    test_files = tests.collect_test_cases(args)

    # Configure tools
    tools = configure_analysis_tools(args)

    # Perform the analysis
    analyze.perform_analysis(tools, test_files)


def parse_existing_results(args):
    """Parse existing results obtained from previous analyses."""
    # Configure tools
    for result_dir in args.result_directories:
        result.process_result_directory(result_dir)


def main():
    """Main function"""

    # Parse CLI
    args = parse_cli_arguments()
    flags.configure_global_flags(args)

    # Run analysis mode
    if args.sub_command == "analyze":
        print("Smartbench runner: run analysis mode...")
        analyze_smart_contracts(args)
    # Run result parsing mode
    elif args.sub_command == "parse-result":
        print("Smartbench runner: parse existing results...")
        parse_existing_results(args)
    else:
        print("Smartbench runner: no sub-command is specified!")

    # Finish
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main()
