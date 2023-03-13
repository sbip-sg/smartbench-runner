#!/usr/bin/env python3

# Standard Library
import os
import shlex
import subprocess

from datetime import datetime
from subprocess import CompletedProcess
from typing import List

# Library
from smartbench import bug_annot, result, solc
from smartbench.debug import debug, warning
from smartbench.issue import Issue, IssueKind
from smartbench.bug_annot import BugAnnot
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


def check_detected_issue(annot: BugAnnot, issues: List[Issue]) -> bool:
    category = annot.bug_category.casefold()
    line = annot.start_line + 1
    for issue in issues:
        if issue.location != None:
            kind = issue.issue_kind
            location = issue.location.start_line
            if line <= location and location <= line + 5:
                if category == "arithmetic" and kind == IssueKind.INTEGER_OVERFLOW:
                    return True;
                if category == "arithmetic" and kind == IssueKind.INTEGER_UNDERFLOW:
                    return True;
                if category == "bad_randomness" and kind == IssueKind.BLOCK_DEPENDENCY:
                    return True;
                if category == "time_manipulation" and kind == IssueKind.BLOCK_DEPENDENCY:
                    return True;
                if category == "front_running" and kind == IssueKind.TOD:
                    return True;
                if category == "transaction_order_dependency" and kind == IssueKind.TOD:
                    return True;
                if category == "unchecked_ll_calls" and kind == IssueKind.UNHANDLED_EXCEPTION:
                    return True;
                if str(kind).casefold() == category:
                    return True;
    return False;


def analyze_test_file(
    tool: Tool, test_file: str, result_dir: str, validate=False
) -> (List[Issue], int, int):
    """Run the analysis on one test case.

    If `validate` is True, the detected issues will be validated with
    bug annotations in the testing files.
    """
    # Configure Solc compiler
    # TODO: check if tool doesn't need compiler, then don't configure
    solc.configure_solc_compiler(test_file)
    try:
        # Run the analysis
        print(f"{'-' * 45}\n")
        print(f"Analyzing: {test_file}\n")

        command = tool.make_analysis_command(test_file, result_dir)
        # print(f"Command: {command}\n")
        output = subprocess.run(
            shlex.split(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        record_execution_log(tool, test_file, command, output, result_dir)
    except ValueError:
        print("Failed to run command: " + str(command))
        return ([],0,0)

    # Process results
    issues = result.process_analysis_result(tool, result_dir)
    for issue in issues:
        print("- " + str(issue))

    total_bugs = 0
    validated_bugs = 0
    if validate:
        annots = bug_annot.parse_bug_annotations(test_file)
        total_bugs = len(annots)
        for annot in annots:
            if check_detected_issue(annot, issues):
                validated_bugs += 1

            print(annot.print_by_line())

    test_file_name = os.path.basename(test_file)
    result.print_summary(test_file_name, issues)

    print(f"validation: {validated_bugs}/{total_bugs}")
    return (issues, validated_bugs, total_bugs)


def run_analysis_tool(
    tool: Tool, test_files: List[str], result_dir: str, validate=False
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

    total_bugs = 0
    validated_bugs = 0
    for test_file in test_files:
        rel_path = os.path.relpath(test_file, start=parent_path)
        output_dir = os.path.join(result_dir, tool.id, rel_path)
        issues, validated, total = analyze_test_file(tool, test_file, output_dir, validate)
        all_issues += issues
        total_bugs += total
        validated_bugs += validated

    print(f"benchmark validation: {validated_bugs}/{total_bugs}")
    return all_issues


def perform_analysis(
    tools: List[Tool], test_files: List[str], validate=False
) -> List[Issue]:
    """Function to run all tools to analyze all test files.

    If `validate` is True, the detected issues will be validated with
    bug annotations in the testing files.
    """
    # Prepare output directory
    print("Start analyzing all test cases...\n")
    result_dir = os.path.join(
        ALL_RESULTS_DIR,
        datetime.now().strftime("%Y_%m_%d_%H_%M_%S"),
    )

    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    record_benchmarking_log(tools, test_files, result_dir)

    all_issues = []

    # Perform the analysis
    for tool in tools:
        issues = run_analysis_tool(tool, test_files, result_dir, validate)
        all_issues += issues

    print("Benchmarking completed!\n")
    print(f"Results are recorded at: {result_dir}")

    return all_issues
