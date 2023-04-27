#!/usr/bin/env python3

# Standard Library
import argparse
import os
import shlex
import signal
import subprocess
import sys

from typing import List, Optional

# Library
from smartbench import (
    analyze,
    annotation,
    benchmark,
    cli,
    docker,
    flags,
    printer,
    result,
)
from smartbench.cli import Command
from smartbench.printer import error, error_traceback, safe_print
from smartbench.result import AnalysisResult
from smartbench.tools.config import configure_analysis_tools
from smartbench.tools.tool import Tool


# Init some paths
SMARTBENCH_ROOT = os.path.dirname(os.path.dirname(__file__))
SMARTBENCH_INSTALLER = "install-smartbench-env.sh"


def handle_sigint(_sig, _frame) -> None:
    """Handling signal SIGINT."""
    safe_print("\nInteruptted by Ctrl+C!")
    sys.exit(0)


def install_smartbench_environment() -> None:
    """Install Smartbench environment"""
    printer.print_medium_double_separator_line()
    safe_print("Installing Smartbench environment...\n")
    cmd = os.path.join(SMARTBENCH_ROOT, SMARTBENCH_INSTALLER)
    try:
        with subprocess.Popen(
            shlex.split(cmd),
            shell=False,
        ) as proc:
            proc.wait()
            (stdout, _) = proc.communicate()
    except Exception:
        error_traceback(f"Failed to install docker container: {cmd}")
        return None


def install_local_docker_containers(tools: List[Tool], jobs: int) -> None:
    """Build and install Docker images of analysis tools locally."""
    safe_print("Instralling Docker containers locally...\n")
    for tool in tools:
        safe_print(f"Install {jobs} Docker container(s) for: {tool.id}")
        if not docker.install_local_docker_containers(tool.id, jobs):
            error("Failed to install local docker containers!")
            sys.exit(1)


def install_remote_docker_containers(tools: List[Tool], jobs: int) -> None:
    """Pull and install Docker images of analysis tools from remote."""
    safe_print("Instralling Docker containers from remote...\n")
    for tool in tools:
        safe_print(f"Install {jobs} Docker container(s) for: {tool.id}")
        if not docker.install_remote_docker_containers(tool.id, jobs):
            error("Failed to install remote docker containers!")
            sys.exit(1)


def analyze_smart_contracts(args) -> None:
    """Run analyzers to analyze input smart contracts"""
    # Configure analysis tools and mode
    tools: List[Tool] = configure_analysis_tools(args.tools)
    jobs = 1 if args.jobs is None else args.jobs

    # Install Smartbench environment
    if args.install_smartbench_env:
        install_smartbench_environment()

    # Install Docker containers
    if args.install_local_docker:
        install_local_docker_containers(tools, jobs)
    if args.install_remote_docker:
        install_remote_docker_containers(tools, jobs)

    # Collect test files
    input_test_files = args.input_files_directories
    if args.test_files_directories:
        for file in args.test_files_directories:
            if file not in input_test_files:
                input_test_files.append(file)
    all_test_files = benchmark.collect_test_files(input_test_files)
    if args.target_contracts_file is None:
        test_contracts, compiler_versions = None, None
    else:
        test_contracts, compiler_versions = benchmark.collect_target_contracts(args.target_contracts_file)

    print (f"test_contracts: {test_contracts}")
    print (f"compiler_versions: {compiler_versions}")
    # Perform the analysis
    analyze.perform_analysis(
        tools,
        all_test_files,
        test_contracts,
        compiler_versions, # override the common compiler version
        args.solc_version,
        args.timeout,
        args.keep_docker_alive,
        jobs,
        args.validate,
        args.benchmarking,
    )


def parse_analysis_results(args) -> None:
    """Parse existing results obtained from previous analyses."""
    # Configure analysis tools and mode
    tools: Optional[List[Tool]] = None
    if args.tools:
        tools = configure_analysis_tools(args.tools)

    # Collect result directories
    result_directories = args.input_result_directories
    if args.result_directories is not None:
        result_directories.extend(args.result_directories)

    # Parsing analysis results
    for result_dir in result_directories:
        result.parse_result_directory(
            result_dir,
            tools,
            args.validate,
            args.benchmarking,
            args.benchmark_name,
        )


def parse_instruction_coverage(args) -> None:
    """Parse instruction coverage from analysis results."""
    for result_dir in args.result_directories:
        result.parse_instruction_coverage(result_dir)


def parse_bug_annotations(args) -> None:
    """Parse bug annotation in smart contracts."""
    test_files = benchmark.collect_test_files(args.input_files_directories)
    annotation.collect_bug_annotations(test_files)


def main():
    """Main function"""

    # Parse CLI
    (parser, args) = cli.parse_cli_arguments()

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
        parse_analysis_results(args)

    # Parse the instruction coverage in analysis results
    elif args.sub_command == Command.PARSE_COVERAGE.value:
        print("Smartbench: running mode parsing instruction coverage...\n")
        parse_instruction_coverage(args)

    # Parse bug annotations
    elif args.sub_command == Command.PARSE_ANNOTS.value:
        print("Smartbench: running mode parsing bug annotations...\n")
        parse_bug_annotations(args)

    else:
        print("Smartbench runner: no sub-command is specified!")

    # Finish
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_sigint)
    main()
