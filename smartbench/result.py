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
    parse_tool_configuration,
)


def process_analysis_result(
    tool: Tool, test_file: str, result_dir: str
) -> List[Issue]:
    """Function to process analysis result of a tool."""
    parse_result = None

    if tool.is_slither():
        parse_result = slither.parse_slither_json_output

    if parse_result:
        output_file = configure_output_file(tool, test_file, result_dir)
        return parse_result(output_file)

    return []


def reconstruct_analysis_tools(tool_result_dirs: List[str]) -> List[Tool]:
    """Reconstruct tool configurations from the result directories.

    Each tool result directory is supposed to be the same as the tool name.
    """

    tools = []
    for tool_name in tool_result_dirs:
        tool = parse_tool_configuration(tool_name)
        if tool is None:
            warning(f"Unable to reconstruct tool configuration: {tool_name}")
        else:
            tools.append(tool)

    return tools


def process_result_directory(result_dir: str):
    """Function to process result directory of a tool.

    The input `result_dir` is the directory containing results of all tools.
    """

    print("Result dir: " + result_dir)
    path = pathlib.Path(result_dir)
    if not path.is_dir():
        warning(f"Directory does not exists: {result_dir}")
        return

    tool_result_dirs = list(os.listdir(result_dir))
    for tool_result_dir in tool_result_dirs:
        # Tool name is expected to be the same as tool_result_dir
        tool_name = tool_result_dir
        print(f"Reconstruct tool configuration for: {tool_name}")
        tool = parse_tool_configuration(tool_result_dir)
        tool_result_dir = os.path.join(result_dir, tool_result_dir)
        test_result_dirs = list(os.listdir(tool_result_dir))
        if tool is None:
            warning(f"Unable to reconstruct tool configuration: {tool_name}")
            continue

        print(f"  - {tool.id}")

        print("Test result dir:")
        for dir in test_result_dirs:
            print(f"  - {dir}")
