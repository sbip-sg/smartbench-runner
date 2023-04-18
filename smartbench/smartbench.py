#!/usr/bin/env python3

# Standard Library
import argparse
import signal
import sys

from typing import List

# Library
from smartbench import (
    analyze,
    annotation,
    benchmark,
    deploy,
    docker,
    flags,
    result,
)
from smartbench.cli import Command, parse_cli_arguments
from smartbench.printer import error, safe_print
from smartbench.tools.config import configure_analysis_tools
from smartbench.tools.tool import Tool


def handle_signal_interupt(_sig, _frame) -> None:
    """Handling signal SIGINT."""
    print("\nInteruptted by Ctrl+C!")
    sys.exit(0)


def analyze_smart_contracts(args):
    """Run analyzers to analyze input smart contracts"""
    # Configure analysis tools
    tools: List[Tool] = configure_analysis_tools(args.tools)

    # Prepare docker environment
    jobs = 1 if args.jobs is None else args.jobs
    if args.install_docker:
        for tool in tools:
            safe_print(f"Install docker {jobs} container(s) for: {tool.id}")
            if not docker.install_docker_containers(tool.id, jobs):
                error("Failed to install docker container!")
                sys.exit(1)

    # Configure test files
    test_files = benchmark.collect_test_files(args.input_files_directories)
    test_contracts = (
        None
        if args.input_contracts is None
        else benchmark.collect_test_contracts(args.input_contracts)
    )

    # Perform the analysis
    analyze.perform_analysis(
        tools,
        test_files,
        test_contracts,
        args.solc_version,
        args.timeout,
        args.docker,
        jobs,
        args.validate,
        args.benchmarking,
    )


def parse_existing_results(args):
    """Parse existing results obtained from previous analyses."""
    for result_dir in args.result_directories:
        result.parse_result_directory(
            result_dir,
            args.validate,
            args.benchmarking,
            args.benchmark_name,
        )


def parse_instruction_coverage(args):
    """Parse instruction coverage from analysis results."""
    for result_dir in args.result_directories:
        result.parse_instruction_coverage(result_dir)


def parse_bug_annotations(args):
    """Parse bug annotation in smart contracts."""
    test_files = benchmark.collect_test_files(args.input_files_directories)
    annotation.collect_bug_annotations(test_files)


def deploy_smart_contracts(args):
    """Deploy smart contracts for testing."""
    # Prepare analysis tools and test files
    test_files = benchmark.collect_test_files(args.input_files_directories)
    tools = configure_analysis_tools(args.tools)
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
    signal.signal(signal.SIGINT, handle_signal_interupt)
    main()
