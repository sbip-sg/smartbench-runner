#!/usr/bin/env python3

"""Module for parsing results."""


# Standard Library
import os
import pathlib
import warnings

from typing import List

# Library
from smartbench.debug import warning
from smartbench.issue import Issue
from smartbench.tools.slither import slither
from smartbench.tools.tool import (
    Tool,
    configure_output_file,
    create_tool_configuration,
)


def process_analysis_result(tool: Tool, result_dir: str) -> List[Issue]:
    """Process analysis result of a tool."""
    process_result_fn = None

    if tool.is_slither():
        process_result_fn = slither.parse_slither_json_output

    if process_result_fn:
        output_file = configure_output_file(tool, result_dir)
        return process_result_fn(output_file)

    return []


def is_test_result_directory(tool: Tool, test_dir: str) -> bool:
    """Check whether `test_dir` containing analysis result of a tool for
    a test file."""

    test_dir = os.path.abspath(test_dir)
    output_file = os.path.join(test_dir, tool.output_file)
    return os.path.exists(output_file)


def parse_existing_analysis_result(tool: Tool, test_dir: str) -> List[Issue]:
    """Parse a test result.

    The input `test_result_dir` is the directory containing the
    immediate result of an analysis tool.
    """

    parse_result_fn = None

    if tool.is_slither():
        parse_result_fn = slither.parse_slither_json_output

    if parse_result_fn is None:
        warning(f"Does not support parsing result of tool: {tool.name}")
        return []

    test_dir = os.path.abspath(test_dir)
    output_file = os.path.join(test_dir, tool.output_file)
    return parse_result_fn(output_file)


def process_result_directory(result_dir: str) -> List[Issue]:
    """Function to process result directory of a tool.

    The input `result_dir` is the directory containing results of all
    tools.

    """

    print("Result dir: " + result_dir)
    path = pathlib.Path(result_dir)
    if not path.is_dir():
        warning(f"Directory does not exists: {result_dir}")
        return []

    all_issues: List[Issue] = []

    tool_dirs = list(os.listdir(result_dir))
    for tool_dir in tool_dirs:
        # Tool id is expected to be the same as tool_result_dir
        tool_id = tool_dir
        print(f"Create tool configuration for: {tool_id}")
        tool = create_tool_configuration(tool_id)
        tool_dir = os.path.join(result_dir, tool_dir)
        test_dirs = list(os.listdir(tool_dir))
        if tool is None:
            warning(f"Unable to reconstruct tool configuration: {tool_id}")
            continue
        print(f"  - {tool.id}")

        test_dirs = [p[0] for p in os.walk(tool_dir)]
        test_dirs = sorted(test_dirs)
        for test_dir in test_dirs:
            if not is_test_result_directory(tool, test_dir):
                continue

            print(f"=== Parsing results in test dir: {test_dir}\n")
            issues = parse_existing_analysis_result(tool, test_dir)
            for issue in issues:
                print(f"- {issue}")
            all_issues = all_issues + issues

    return all_issues
