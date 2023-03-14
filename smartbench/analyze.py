#!/usr/bin/env python3

# Standard Library
import os
import shlex
import subprocess

from datetime import datetime
from subprocess import CompletedProcess
from typing import List

# Library
from smartbench import bug_annot, result, solc, validate
from smartbench.debug import debug, warning
from smartbench.issue import Issue
from smartbench.tools.slither import slither
from smartbench.tools.tool import (
    ALL_RESULTS_DIR,
    Tool,
    configure_log_file,
    configure_output_file,
)


def record_execution_log(
    tool: Tool,
    input_file: str,
    command: str,
    output: CompletedProcess,
    result_dir: str,
):
    """Record execution log of an analysis tool in TOML format."""
    log_file = configure_log_file(tool, result_dir)
    with open(log_file, "w", encoding="utf-8") as file:
        file.write(f"# Execution log of {tool.name}:\n\n")

        # Log input
        file.write("[input]\n")
        file.write(f'test_file = """{input_file}"""\n\n')
        file.write(f'command = """{command}"""\n\n')

        # Log output
        file.write("[output]\n")
        stdout = output.stdout.decode("utf-8")
        file.write(f'stdout = """{stdout}"""\n\n')
        stderr = output.stderr.decode("utf-8")
        file.write(f'stderr = """{stderr}"""')


def record_analysis_log(tools, test_files, result_dir: str):
    log_file = os.path.join(result_dir, "smartbench_log.toml")
    with open(log_file, "w", encoding="utf-8") as file:
        file.write("# Smartbench benchmarking log \n\n")

        # Log tools
        tools_info = ", ".join([f'"{tool.id}"' for tool in tools])
        file.write(f"tools = [{tools_info}]\n\n")

        # Log test files
        if test_files is None or len(test_files) == 0:
            file.write("test_files = []\n")
        else:
            tests_info = ",\n  ".join([f'"{test}"' for test in test_files])
            file.write(f"test_files = [\n  {tests_info}\n]\n")


def analyze_test_file(
    tool: Tool,
    test_file: str,
    benchmark_output_dir: str,
    validate_results=False,
) -> List[Issue]:
    """Run the analysis on one test case.

    If `validate` is True, the detected issues will be validated with
    bug annotations in the testing files.
    """
    # Configure Solc compiler
    solc_path = solc.configure_solc_compiler(test_file)
    try:
        # Run the analysis
        print(f"{'-' * 45}\n")
        print(f"Analyzing: {test_file}\n")

        command = tool.make_analysis_command(
            test_file, benchmark_output_dir, solc_path
        )
        output = subprocess.run(
            shlex.split(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        record_execution_log(
            tool, test_file, command, output, benchmark_output_dir
        )
    except ValueError:
        print("Failed to run command: " + str(command))
        return []

    # Process results
    issues = result.process_analysis_result(tool, benchmark_output_dir)
    for issue in issues:
        print("- " + str(issue))

    annots = None
    if validate_results:
        print("Bug annotations:")
        annots = bug_annot.parse_bug_annotations(test_file)
        for annot in annots:
            print(f"- {annot.print_by_line()}")
        print("")

    test_file_name = os.path.basename(test_file)

    validation = None
    if validate_results:
        validation = validate.validate_analysis_results(test_file, issues)

    result.print_summary(test_file_name, issues, annots, validation)

    return issues


def run_analysis_tool(
    tool: Tool,
    test_files: List[str],
    all_results_dir: str,
    validate_results=False,
) -> List[Issue]:
    """Run one analysis tool.

    The input `result_dir` is the directory containing results of all tools in
    the current run.

    If `validate` is True, the detected issues will be validated with
    bug annotations in the testing files.
    """
    print(f"{'=' * 55}\n")
    print(f"Running analysis tool: {tool.name}\n")
    common_path = os.path.commonpath(test_files)
    parent_path = os.path.dirname(common_path)

    all_issues = []

    for test_file in test_files:
        # Prepare output directory for one test file
        rel_path = os.path.relpath(test_file, start=parent_path)
        test_output_dir = os.path.join(all_results_dir, tool.id, rel_path)
        if not os.path.exists(test_output_dir):
            os.makedirs(test_output_dir)

        # Analyze the test file
        issues = analyze_test_file(
            tool, test_file, test_output_dir, validate_results
        )
        all_issues += issues

    return all_issues


def perform_analysis(
    tools: List[Tool], test_files: List[str], validate_results=False
) -> List[Issue]:
    """Function to run all tools to analyze all test files.

    If `validate` is True, the detected issues will be validated with
    bug annotations in the testing files.
    """
    # Prepare output directory for all tests and all tools in this run
    print("Start analyzing all test cases...\n")
    all_results_dir = os.path.join(
        ALL_RESULTS_DIR,
        datetime.now().strftime("%Y_%m_%d_%H_%M_%S"),
    )
    if not os.path.exists(all_results_dir):
        os.makedirs(all_results_dir)

    # Record the analysis details to a log file
    record_analysis_log(tools, test_files, all_results_dir)

    # Perform the analysis
    all_issues = []
    for tool in tools:
        issues = run_analysis_tool(
            tool, test_files, all_results_dir, validate_results
        )
        all_issues += issues

    print("Benchmarking completed!\n")
    print(f"Results are recorded at: {all_results_dir}")

    return all_issues
