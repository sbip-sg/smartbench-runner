#!/usr/bin/env python3

# Standard Library
import argparse
import signal
import sys

# Library
from smartbench import analyze, annotation, benchmark, deploy, flags, result
from smartbench.cli import Command, parse_cli_arguments
from smartbench.printer import error
from smartbench.tools.config import configure_analysis_tools


def signal_handler(_sig, _frame):
    print("\nInteruptted by Ctrl+C!")
    sys.exit(0)


def analyze_smart_contracts(args):
    """Run analyzers to analyze input smart contracts"""
    # Prepare analysis tools and test files
    tools = configure_analysis_tools(args)
    test_files = benchmark.collect_test_cases(args)

    # Prepare environment
    jobs = 1 if args.jobs is None else args.jobs

    if jobs > 1 and not args.docker:
        error("Do not support running multiple jobs in local mode!")

    # Perform the analysis
    analyze.perform_analysis(
        tools,
        test_files,
        args.timeout,
        args.docker,
        jobs,
        args.validate,
    )


def parse_existing_results(args):
    """Parse existing results obtained from previous analyses."""
    for result_dir in args.result_directories:
        result.parse_result_directory(
            result_dir, args.validate_results, args.benchmark_name
        )


def parse_instruction_coverage(args):
    """Parse instruction coverage from analysis results."""
    for result_dir in args.result_directories:
        result.parse_instruction_coverage(result_dir)


def parse_bug_annotations(args):
    """Parse bug annotation in smart contracts."""
    test_files = benchmark.collect_test_cases(args)
    annotation.collect_bug_annotations(test_files)


def deploy_smart_contracts(args):
    """Deploy smart contracts for testing."""
    # Prepare analysis tools and test files
    test_files = benchmark.collect_test_cases(args)
    tools = configure_analysis_tools(args)
    # Perform the deployment
    deploy.perform_deployment(tools, test_files)


def main():
    """Main function"""

    # Parse CLI
    (parser, args) = parse_cli_arguments()

    if args.sub_command is None:
        print("Error: no sub-command is specified!\n")
        print("Please try again!\n")
        parser.print_help()
        sys.exit(0)

    flags.configure_global_flags(args)

    # Run analysis tools
    if args.sub_command == Command.ANALYZE.value:
        print("Smartbench: running mode analyzing smart contracts...\n")
        analyze_smart_contracts(args)
    # Parse analysis results
    elif args.sub_command == Command.PARSE_RESULTS.value:
        print("Smartbench: running mode parsing benchmarking results...\n")
        parse_existing_results(args)
    # Parse the instruction coverage in analysis results
    elif args.sub_command == Command.PARSE_COVERAGE.value:
        print("Smartbench: running mode parsing instruction coverage...\n")
        parse_instruction_coverage(args)
    # Parse bug annotations
    elif args.sub_command == Command.PARSE_ANNOTS.value:
        print("Smartbench: running mode parsing bug annotations...\n")
        parse_bug_annotations(args)
    # Deploy contracts
    elif args.sub_command == Command.DEPLOY_CONTRACTS.value:
        print("Smartbench: running mode deploying contracts...\n")
        deploy_smart_contracts(args)
    else:
        print("Smartbench runner: no sub-command is specified!")

    # Finish
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main()
