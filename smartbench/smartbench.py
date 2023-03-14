#!/usr/bin/env python3

# Standard Library
import signal
import sys

# Library
from smartbench import analyze, bug_annot, flags, result, tests
from smartbench.cli import parse_cli_arguments
from smartbench.tools.tool import configure_analysis_tools


def signal_handler(_sig, _frame):
    print("\nInteruptted by Ctrl+C!")
    sys.exit(0)


def analyze_smart_contracts(args):
    """Run analyzers to analyze input smart contracts"""
    test_files = tests.collect_test_cases(args)

    # Configure tools
    tools = configure_analysis_tools(args)

    # Perform the analysis
    analyze.perform_analysis(tools, test_files, args.validate_results)


def parse_existing_results(args):
    """Parse existing results obtained from previous analyses."""
    for result_dir in args.result_directories:
        result.parse_result_directory(result_dir, args.validate_results)


def parse_bug_annotations(args):
    """Parse bug annotation in smart contracts."""
    test_files = tests.collect_test_cases(args)
    bug_annot.collect_bug_annotations(test_files)


def main():
    """Main function"""

    # Parse CLI
    args = parse_cli_arguments()
    flags.configure_global_flags(args)

    # Run analysis tools
    if args.sub_command == "analyze":
        print("Smartbench: running mode analyzing smart contracts...\n")
        analyze_smart_contracts(args)
    # Parse analysis results
    elif args.sub_command == "parse-result":
        print("Smartbench: running mode parsing benchmarking results...\n")
        parse_existing_results(args)
    # Parse bug annotations
    elif args.sub_command == "parse-annot":
        print("Smartbench: running mode parsing bug annotations...\n")
        parse_bug_annotations(args)
    else:
        print("Smartbench runner: no sub-command is specified!")

    # Finish
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main()
