#!/usr/bin/env python3

"""Module for running smart contract analyzers for testing contracts."""

# Standard Library
import json
import os
import shlex
import subprocess
import traceback

from datetime import datetime
from pathlib import Path
from subprocess import CompletedProcess
from typing import List, Optional

# Library
from smartbench import bug_annot, printer, result, solc, validator
from smartbench.issue import Issue
from smartbench.printer import debug
from smartbench.tools.config import RESULTS_DIR
from smartbench.tools.mythril import mythril
from smartbench.tools.mythril.mythril import Mythril
from smartbench.tools.smartfuzz import smartfuzz
from smartbench.tools.tool import Tool


def log_analysis_command(
    tool: Tool,
    input_file: str,
    command: str,
    result_dir: str,
) -> None:
    """Record execution log of an analysis tool in TOML format."""
    log_file = tool.configure_log_file(result_dir)
    with open(log_file, "w", encoding="utf-8") as file:
        file.write(f"# Execution log of {tool.name}:\n\n")

        # Log input
        file.write("-------------------------------------------------------\n")
        file.write("[input contract]\n")
        file.write("-------------------------------------------------------\n")
        file.write(f"{input_file}\n\n")

        file.write("-------------------------------------------------------\n")
        file.write("[command]\n")
        file.write("-------------------------------------------------------\n")
        file.write(f"{command}\n\n")


def log_analysis_output(
    tool: Tool,
    output: CompletedProcess,
    result_dir: str,
) -> None:
    """Record execution log of an analysis tool in TOML format."""
    log_file = tool.configure_log_file(result_dir)
    with open(log_file, "a", encoding="utf-8") as file:
        file.write("-------------------------------------------------------\n")
        file.write("[output]\n")
        file.write("-------------------------------------------------------\n")
        stdout = output.stdout.decode("utf-8")
        file.write(f"{stdout}\n\n")

        file.write("-------------------------------------------------------\n")
        file.write("[errors]\n")
        file.write("-------------------------------------------------------\n")
        stderr = output.stderr.decode("utf-8")
        file.write(f"{stderr}")


def log_analysis_info(
    tools: List[Tool], test_files: List[str], result_dir: str
):
    """Record analysis log of all tools."""
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
    test_output_dir: str,
    timeout=None,
    use_docker=True,
    validate=False,
) -> List[Issue]:
    """Analyze `test_file` using `tool` and write result to `test_output_dir`.

    If `validate` is True, the detected issues will be validated with
    bug annotations in the testing files."""

    # Reset issue index counter for the current test file
    Issue.index_counter = 1

    try:
        # Run the analysis
        print(f"{'-' * 45}\n")
        print(f"Analyzing: {test_file}\n")

        command = tool.make_analysis_command(
            test_file,
            test_output_dir,
            timeout,
            use_docker,
        )

        if command is None:
            print(f"Unable to make analysis command for tool: {tool.name}\n")
            return []

        log_analysis_command(tool, test_file, command, test_output_dir)

        debug(f"COMMAND: {command}")

        output = subprocess.run(
            shlex.split(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        log_analysis_output(tool, output, test_output_dir)
        if isinstance(tool, Mythril):
            # the results of `mythril` is in `stdout`
            tool.write_to_output_file(output, test_output_dir)

    except ValueError as err:
        print(f"Failed to run command: {command}\n")
        print(f"** Error: {err}")
        traceback.print_exc()
        return []

    # Process results
    issues = result.process_analysis_result(tool, test_output_dir)
    for issue in issues:
        print("- " + str(issue))

    bug_annots = None
    validation = None
    test_name = os.path.basename(test_file)
    if validate:
        print("Bug annotations:")
        bug_annots = bug_annot.parse_bug_annotations(test_file)
        for annot in bug_annots:
            print(f"- {annot.print_concise()}")
        print("")
        validation = validator.validate_issues(
            tool, test_file, issues, bug_annots
        )

    result.print_summary(tool, test_name, issues, bug_annots, validation)
    return issues


def run_analysis_tool(
    tool: Tool,
    test_files: List[str],
    tool_output_dir: str,
    timeout=None,
    use_docker=True,
    jobs=1,
    validate=False,
) -> List[Issue]:
    """Run one analysis tool for all `test_files` and write all results
    to `tool_output_dir`.

    If `validate` is True, the detected issues will be validated with
    bug annotations in the testing files.

    """
    printer.print_long_double_horizontal_line()
    print(f"Running analysis tool: {tool.name}\n")
    common_path = os.path.commonpath(test_files)
    parent_path = os.path.dirname(common_path)

    all_issues = []

    # if (tool.name.casefold() == smartfuzz.TOOL_NAME.casefold()):
    #     smartfuzz.install_virtual_env()

    for test_file in test_files:
        # Prepare output directory for one test file
        rel_path = os.path.relpath(test_file, start=parent_path)
        test_output_dir = os.path.join(tool_output_dir, rel_path)
        if not os.path.exists(test_output_dir):
            os.makedirs(test_output_dir)

        # Analyze the test file
        issues = analyze_test_file(
            tool,
            test_file,
            test_output_dir,
            timeout,
            use_docker,
            validate,
        )
        all_issues += issues

    return all_issues


def perform_analysis(
    tools: List[Tool],
    test_files: List[str],
    timeout=None,
    use_docker=True,
    jobs=1,
    validate=False,
) -> List[Issue]:
    """Function to run all tools to analyze all test files.

    If `validate` is True, the detected issues will be validated with
    bug annotations in the testing files.

    When `jobs` > 1, the analysis can be performed concurrently.
    """
    # Prepare output directory for all tests and all tools in this run
    print("Start analyzing all test cases...\n")
    results_dir = os.path.join(
        RESULTS_DIR,
        datetime.now().strftime("%Y_%m_%d_%H_%M_%S"),
    )
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    # Record the analysis details to a log file
    log_analysis_info(tools, test_files, results_dir)

    # Perform the analysis
    all_issues = []
    for tool in tools:
        tool_output_dir = os.path.join(results_dir, tool.id)
        issues = run_analysis_tool(
            tool,
            test_files,
            tool_output_dir,
            timeout,
            use_docker,
            jobs,
            validate,
        )
        all_issues += issues

    print("Benchmarking completed!\n")
    print(f"Results are recorded at: {results_dir}")

    return all_issues
