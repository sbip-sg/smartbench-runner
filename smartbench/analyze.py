#!/usr/bin/env python3

# Standard Library
import os
import shlex
import subprocess

from datetime import datetime

# Library
from smartbench.tools.tool import ALL_RESULTS_DIR


def analyze_one_file(tool, test_file, result_dir):
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
        log_file = os.path.join(result_dir, tool.log_output)
        print("  Log file:", log_file)
        # write result to file
        with open(log_file, "w", encoding="utf-8") as file:
            file.write("========== Output ============\n\n")
            file.write(output_log.stdout.decode("utf-8"))
            file.write("\n\n\n")
            file.write("========== Errors ============\n\n")
            file.write(output_log.stderr.decode("utf-8"))
    except ValueError:
        print("Failed to run command: " + str(command))


def run_analysis_tool(tool, test_files, result_dir):
    "Run one analysis tool."
    print("Running tool:", tool.name)
    for test_file in test_files:
        print("\nTest file:", test_file)
        analyze_one_file(tool, test_file, result_dir)


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
