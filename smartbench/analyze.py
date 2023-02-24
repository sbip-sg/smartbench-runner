#!/usr/bin/env python3

# Standard Library
import os
import shlex
import subprocess

from datetime import datetime
from typing import List

# Library
from smartbench.buginfo import BugInfo
from smartbench.tools.slither import slither
from smartbench.tools.tool import ALL_RESULTS_DIR, Tool
from smartbench.tools.util import get_output_directory


def record_analysis_log(log_data, log_file):
    with open(log_file, "w", encoding="utf-8") as file:
        file.write("========== Output ============\n\n")
        file.write(log_data.stdout.decode("utf-8"))
        file.write("\n\n\n")
        file.write("========== Errors ============\n\n")
        file.write(log_data.stderr.decode("utf-8"))


def parse_analysis_result(
    tool: Tool, test_file: str, result_dir
) -> List[BugInfo]:
    parse_result = None

    if tool.is_slither():
        parse_result = slither.parse_slither_json_output

    if parse_result:
        return parse_result(tool.id, test_file, result_dir, tool.output_file)

    return []


def analyze_test_file(
    tool: Tool, test_file: str, result_dir: str
) -> List[BugInfo]:
    "Run the analysis on one test case."
    command = tool.make_analysis_command(test_file, result_dir)
    print("  Command: ", command)
    try:
        output_log = subprocess.run(
            shlex.split(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        # Write output log
        output_dir = get_output_directory(tool.id, test_file, result_dir)
        log_file = os.path.join(output_dir, tool.log_file)
        print("  Log file:", log_file)
        record_analysis_log(output_log, log_file)
    except ValueError:
        print("Failed to run command: " + str(command))
        return []

    # Parse results
    return parse_analysis_result(tool, test_file, result_dir)


def run_analysis_tool(tool, test_files, result_dir):
    "Run one analysis tool."
    print("Running tool:", tool.name)
    for test_file in test_files:
        print("\nTest file:", test_file)
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
