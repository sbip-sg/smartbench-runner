#!/usr/bin/env python3

# Standard Library
import os
import shlex
import subprocess

from datetime import datetime
from subprocess import CompletedProcess
from typing import List

# Library
from smartbench import result, solc
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


def record_benchmarking_log(tools, test_files, result_dir: str):
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
    tool: Tool, test_file: str, result_dir: str
) -> List[Issue]:
    "Run the analysis on one test case."
    # Configure Solc compiler
    # TODO: check if tool doesn't need compiler, then don't configure
    solc.configure_solc_compiler(test_file)
    try:
        # Run the analysis
        print(f"Analyzing: {test_file}\n")

        command = tool.make_analysis_command(test_file, result_dir)
        output = subprocess.run(
            shlex.split(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        record_execution_log(tool, test_file, command, output, result_dir)
    except ValueError:
        print("Failed to run command: " + str(command))
        return []

    # Process results
    issues = result.process_analysis_result(tool, result_dir)
    for issue in issues:
        print("- " + str(issue))

    return issues


def run_analysis_tool(tool, test_files, result_dir):
    """Run one analysis tool.

    The input `result_dir` is the directory containing results of all tools in
    the current run.
    """
    debug("Running tool:", tool.name)
    common_path = os.path.commonpath(test_files)
    parent_path = os.path.dirname(common_path)

    for test_file in test_files:
        rel_path = os.path.relpath(test_file, start=parent_path)
        output_dir = os.path.join(result_dir, tool.id, rel_path)
        analyze_test_file(tool, test_file, output_dir)


def perform_analysis(tools, test_files):
    """Function to run all tools to analyze all test files."""
    # Prepare output directory
    print("Start analyzing all test cases...\n")
    result_dir = os.path.join(
        ALL_RESULTS_DIR,
        datetime.now().strftime("%Y_%m_%d_%H_%M_%S"),
    )

    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    record_benchmarking_log(tools, test_files, result_dir)

    # Perform the analysis
    for tool in tools:
        run_analysis_tool(tool, test_files, result_dir)

    print("Benchmarking completed!\n")
    print(f"Results are recorded at: {result_dir}")
