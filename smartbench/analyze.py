#!/usr/bin/env python3

# Standard Library
import os
import shlex
import subprocess

from datetime import datetime
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


def record_analysis_log(input_file: str, command: str, log_data, log_file):
    with open(log_file, "w", encoding="utf-8") as file:
        file.write("============== Input file ==============\n\n")
        file.write(f"{input_file}\n\n")
        file.write("=============== Command ================\n\n")
        file.write(f"{command}\n\n")
        file.write("============== Output Log ==============\n\n")
        file.write(f"{log_data.stdout.decode('utf-8')}\n\n")
        file.write("============== Errors Log ==============\n\n")
        file.write(f"{log_data.stderr.decode('utf-8')}")


def analyze_test_file(
    tool: Tool, test_file: str, result_dir: str
) -> List[Issue]:
    "Run the analysis on one test case."
    # Configure Solc compiler
    # TODO: check if tool doesn't need compiler, then don't configure
    solc.configure_solc_compiler(test_file)
    try:
        # Run the analysis
        command = tool.make_analysis_command(test_file, result_dir)
        debug("Command:", command)
        output_log = subprocess.run(
            shlex.split(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        # Write output log
        log_file = configure_log_file(tool, test_file, result_dir)
        debug("Log file:", log_file)
        record_analysis_log(test_file, command, output_log, log_file)
    except ValueError:
        print("Failed to run command: " + str(command))
        return []

    # Process results
    issues = result.process_analysis_result(tool, test_file, result_dir)
    print("Issues: ")
    for issue in issues:
        print("- " + str(issue))

    return issues


def run_analysis_tool(tool, test_files, result_dir):
    """Run one analysis tool.

    The input `result_dir` is the directory containing results of all tools in
    the current run.
    """
    debug("Running tool:", tool.name)
    for test_file in test_files:
        analyze_test_file(tool, test_file, result_dir)


def perform_analysis(tools, test_files):
    """Function to run all tools to analyze all test files."""
    # Prepare output directory
    result_dir = os.path.join(
        ALL_RESULTS_DIR,
        datetime.now().strftime("%Y_%m_%d_%H_%M_%S"),
    )
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    # Perform the analysis
    for tool in tools:
        run_analysis_tool(tool, test_files, result_dir)
